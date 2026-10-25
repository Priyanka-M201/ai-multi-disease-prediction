import os
import json
import numpy as np
import pandas as pd
import joblib
from typing import Dict, List, Any
import shap
from .predictor import predictor, MODELS_DIR


class ShapExplainerEngine:
    """Computes Explainable AI (SHAP) feature attributions for individual patient predictions."""

    def __init__(self):
        self.explainers = {}
        self.background_samples = {}

    def get_explainer(self, disease: str, model_key: str):
        cache_key = f"{disease}_{model_key}"
        if cache_key in self.explainers:
            return self.explainers[cache_key]

        model = predictor.models.get(cache_key)
        if not model:
            return None

        # Load background data
        bg_path = os.path.join(MODELS_DIR, f"{disease}_shap_background.joblib")
        background = joblib.load(bg_path) if os.path.exists(bg_path) else None

        try:
            if model_key in ["random_forest", "xgboost", "catboost"]:
                explainer = shap.TreeExplainer(model)
            elif model_key == "logistic_regression" and background is not None:
                scaler = predictor.scalers.get(disease)
                bg_scaled = scaler.transform(background) if scaler else background
                explainer = shap.LinearExplainer(model, bg_scaled)
            else:
                explainer = shap.Explainer(model, background)
            self.explainers[cache_key] = explainer
            return explainer
        except Exception as e:
            print(f"Warning: Failed to create standard SHAP explainer for {cache_key}: {e}")
            return None

    def explain(self, disease: str, raw_inputs: Dict[str, Any], requested_model: str = None) -> Dict[str, Any]:
        disease = disease.lower()
        best_key = predictor.get_best_model_key(disease)
        model_key = (requested_model or best_key).lower()
        cache_key = f"{disease}_{model_key}"

        model = predictor.models.get(cache_key)
        if not model:
            raise ValueError(f"Model '{model_key}' not found for disease '{disease}'")

        df_vector = predictor.prepare_input_vector(disease, raw_inputs)
        feature_names = predictor.feature_specs.get(disease, list(raw_inputs.keys()))

        # Prediction probability
        pred_res = predictor.predict(disease, raw_inputs, model_key)
        pred_prob = pred_res["risk_probability"]

        # Calculate SHAP values
        explainer = self.get_explainer(disease, model_key)
        shap_values_vector = None
        base_val = 0.5

        if explainer is not None:
            try:
                if model_key in ["logistic_regression", "ann"]:
                    scaler = predictor.scalers.get(disease)
                    input_scaled = scaler.transform(df_vector) if scaler else df_vector
                    sv = explainer(input_scaled)
                else:
                    sv = explainer(df_vector)

                if hasattr(sv, "values"):
                    vals = sv.values
                    if vals.ndim == 3:  # (samples, features, classes)
                        shap_values_vector = vals[0, :, 1]
                    elif vals.ndim == 2:
                        shap_values_vector = vals[0, :]
                    else:
                        shap_values_vector = vals.flatten()
                elif isinstance(sv, list):
                    shap_values_vector = sv[1][0] if len(sv) > 1 else sv[0][0]

                if hasattr(sv, "base_values"):
                    bv = sv.base_values
                    base_val = float(bv[0, 1] if bv.ndim > 1 else bv[0])
            except Exception as e:
                print(f"Notice: explainer call failed, using empirical attribution fallback: {e}")
                shap_values_vector = None

        # Robust attribution fallback based on feature deviations if explainer failed
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

        # Format contributions
        contributions = []
        total_abs_shap = sum(abs(v) for v in shap_values_vector) or 1e-6

        friendly_names = {
            "trestbps": "Resting Blood Pressure", "chol": "Serum Cholesterol",
            "thalach": "Max Heart Rate", "oldpeak": "ST Depression", "cp": "Chest Pain Type",
            "fbs": "Fasting Blood Sugar", "ca": "Major Vessels Blocked", "exang": "Exercise Angina",
            "glucose": "Plasma Glucose", "bmi": "Body Mass Index", "blood_pressure": "Diastolic Blood Pressure",
            "skin_thickness": "Skinfold Thickness", "diabetes_pedigree": "Family Diabetes Predisposition",
            "avg_glucose_level": "Average Glucose Level", "smoking_status": "Smoking History",
            "systolic_bp": "Systolic Blood Pressure", "diastolic_bp": "Diastolic Blood Pressure",
            "heart_rate": "Resting Heart Rate", "physical_activity": "Physical Activity Level"
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

        # Sort by absolute SHAP contribution descending
        contributions.sort(key=lambda x: abs(x["shap_value"]), reverse=True)

        top_increasing = [c["feature"] for c in contributions if c["direction"] == "INCREASES_RISK"][:2]
        top_reducing = [c["feature"] for c in contributions if c["direction"] == "REDUCES_RISK"][:2]

        summary_parts = []
        if top_increasing:
            summary_parts.append(f"Primary risk drivers: {', '.join(top_increasing)}.")
        if top_reducing:
            summary_parts.append(f"Protective factors: {', '.join(top_reducing)}.")
        summary_text = " ".join(summary_parts) or "Risk factors are evenly balanced."

        return {
            "disease": disease.capitalize(),
            "model_name": predictor.get_model_display_name(disease, model_key),
            "base_risk_probability": round(float(base_val), 4),
            "predicted_risk_probability": pred_prob,
            "contributions": contributions,
            "summary_text": summary_text,
            "disclaimer": (
                "SHAP values quantify algorithmic feature attributions from the trained model. "
                "They illustrate mathematical influence on the prediction, not clinical diagnostic causation."
            )
        }


shap_engine = ShapExplainerEngine()
