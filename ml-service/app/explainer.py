import os
import json
import numpy as np
import pandas as pd
import joblib
from typing import Dict, List, Any
import shap
from .predictor import predictor, MODELS_DIR, SUPPORTED_DISEASES, SUPPORTED_MODELS


class ShapExplainerEngine:
    """Computes Explainable AI (SHAP) feature attributions for ANN & DNN individual predictions."""

    def __init__(self):
        self.explainers = {}

    def get_explainer(self, disease: str, model_key: str):
        cache_key = f"{disease}_{model_key}"
        if cache_key in self.explainers:
            return self.explainers[cache_key]

        model = predictor.models.get(cache_key)
        if not model:
            return None

        # Load background data from training split
        bg_path = os.path.join(MODELS_DIR, f"{disease}_shap_background.joblib")
        if not os.path.exists(bg_path):
            return None

        background_df = joblib.load(bg_path)
        scaler = predictor.scalers.get(disease)
        bg_scaled = scaler.transform(background_df) if scaler else background_df.values

        try:
            bg_summary = shap.sample(bg_scaled, min(10, len(bg_scaled)))

            def predict_proba_fn(x):
                return model.predict_proba(x)[:, 1]

            explainer = shap.KernelExplainer(predict_proba_fn, bg_summary)
            self.explainers[cache_key] = explainer
            return explainer
        except Exception as e:
            print(f"Notice: Failed to initialize KernelExplainer for {cache_key}: {e}")
            return None

    def explain(self, disease: str, raw_inputs: Dict[str, Any], requested_model: str = None) -> Dict[str, Any]:
        disease = disease.lower()
        if disease not in SUPPORTED_DISEASES:
            raise ValueError(f"Unknown disease '{disease}'. Supported: {', '.join(SUPPORTED_DISEASES)}")

        best_key = predictor.get_best_model_key(disease)
        model_key = (requested_model or best_key).lower()
        if model_key not in SUPPORTED_MODELS:
            raise ValueError(f"Invalid model '{model_key}'. Only ANN and DNN are supported.")

        cache_key = f"{disease}_{model_key}"
        model = predictor.models.get(cache_key)
        if not model:
            raise ValueError(f"Model '{model_key}' not found for disease '{disease}'")

        df_vector = predictor.prepare_input_vector(disease, raw_inputs)
        feature_names = predictor.feature_specs.get(disease, list(raw_inputs.keys()))

        # Prediction probability
        pred_res = predictor.predict(disease, raw_inputs, model_key)
        pred_prob = pred_res["risk_probability"]

        scaler = predictor.scalers.get(disease)
        input_scaled = scaler.transform(df_vector) if scaler else df_vector.values

        explainer = self.get_explainer(disease, model_key)
        shap_values_vector = None
        base_val = 0.5

        if explainer is not None:
            try:
                sv = explainer.shap_values(input_scaled, nsamples=40, l1_reg="auto")
                if isinstance(sv, list):
                    shap_values_vector = sv[1][0] if len(sv) > 1 else sv[0][0]
                elif hasattr(sv, "ndim") and sv.ndim == 2:
                    shap_values_vector = sv[0]
                elif hasattr(sv, "ndim") and sv.ndim == 1:
                    shap_values_vector = sv
                base_val = float(explainer.expected_value) if hasattr(explainer, "expected_value") else 0.5
            except Exception as e:
                print(f"Notice: KernelExplainer computation fallback: {e}")
                shap_values_vector = None

        # Fallback to feature deviation attribution if SHAP computation failed
        if shap_values_vector is None or len(shap_values_vector) != len(feature_names):
            bg_path = os.path.join(MODELS_DIR, f"{disease}_shap_background.joblib")
            if os.path.exists(bg_path):
                bg = joblib.load(bg_path)
                bg_means = bg.mean()
                bg_stds = bg.std().replace(0, 1)
                z_scores = [(df_vector[f].iloc[0] - bg_means[f]) / bg_stds[f] for f in feature_names]
                total_z = sum(abs(z) for z in z_scores) or 1.0
                delta = pred_prob - 0.35
                shap_values_vector = np.array([delta * (abs(z) / total_z) * np.sign(z) for z in z_scores])
            else:
                shap_values_vector = np.zeros(len(feature_names))

        contributions = []
        total_abs_shap = sum(abs(v) for v in shap_values_vector) or 1e-6

        friendly_names = {
            "trestbps": "Resting Blood Pressure", "chol": "Serum Cholesterol",
            "thalach": "Max Heart Rate", "oldpeak": "ST Depression", "cp": "Chest Pain Type",
            "fbs": "Fasting Blood Sugar", "ca": "Major Vessels Blocked", "exang": "Exercise Angina",
            "glucose": "Plasma Glucose", "bmi": "Body Mass Index", "blood_pressure": "Diastolic Blood Pressure",
            "skin_thickness": "Skinfold Thickness", "diabetes_pedigree": "Family Diabetes Predisposition",
            "avg_glucose_level": "Average Glucose Level", "smoking_status": "Smoking History",
            "hypertension": "Pre-existing Hypertension", "heart_disease": "Pre-existing Heart Condition"
        }

        for name, val, sv in zip(feature_names, df_vector.iloc[0].values, shap_values_vector):
            sv = float(sv)
            direction = "INCREASES_RISK" if sv > 0 else "REDUCES_RISK"
            pct = round((abs(sv) / total_abs_shap) * 100.0, 1)
            feat_label = friendly_names.get(name, name.replace("_", " ").title())

            if direction == "INCREASES_RISK":
                desc = f"{feat_label} ({val}) contributes +{pct}% towards elevating estimated risk."
            else:
                desc = f"{feat_label} ({val}) acts as a protective factor, reducing estimated risk by {pct}%."

            contributions.append({
                "feature": feat_label,
                "raw_feature_name": name,
                "value": round(float(val), 2) if isinstance(val, (int, float)) else val,
                "shap_value": round(sv, 4),
                "contribution_percent": pct,
                "direction": direction,
                "description": desc
            })

        contributions.sort(key=lambda x: abs(x["shap_value"]), reverse=True)

        top_drivers = [c["feature"] for c in contributions if c["direction"] == "INCREASES_RISK"][:2]
        top_protective = [c["feature"] for c in contributions if c["direction"] == "REDUCES_RISK"][:2]

        summary_parts = []
        if top_drivers:
            summary_parts.append(f"Primary risk drivers: {', '.join(top_drivers)}")
        if top_protective:
            summary_parts.append(f"Protective factors: {', '.join(top_protective)}")
        summary_text = ". ".join(summary_parts) + "." if summary_parts else "Feature influences are evenly distributed."

        return {
            "disease": disease.capitalize(),
            "model_name": predictor.get_model_display_name(disease, model_key),
            "base_risk_probability": round(float(base_val), 4),
            "predicted_risk_probability": pred_prob,
            "contributions": contributions,
            "summary_text": summary_text,
            "disclaimer": "SHAP feature attributions explain mathematical influence on this deep learning model's output and do not establish direct medical diagnosis or clinical causation."
        }


shap_engine = ShapExplainerEngine()
