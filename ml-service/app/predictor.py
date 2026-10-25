import os
import json
import numpy as np
import pandas as pd
import joblib
from typing import Dict, Any, Tuple

MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))


class PredictorEngine:
    """Manages loading of trained models, feature scalers, and running risk inferences."""

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_specs = {}
        self.evaluation_meta = {}
        self.load_artifacts()

    def load_artifacts(self):
        eval_path = os.path.join(MODELS_DIR, "models_evaluation.json")
        if os.path.exists(eval_path):
            with open(eval_path, "r") as f:
                self.evaluation_meta = json.load(f)

        for disease in ["heart", "diabetes", "stroke", "hypertension"]:
            # Load feature specs
            spec_path = os.path.join(MODELS_DIR, f"{disease}_features.json")
            if os.path.exists(spec_path):
                with open(spec_path, "r") as f:
                    self.feature_specs[disease] = json.load(f)["features"]

            # Load scaler
            scaler_path = os.path.join(MODELS_DIR, f"{disease}_scaler.joblib")
            if os.path.exists(scaler_path):
                self.scalers[disease] = joblib.load(scaler_path)

            # Load models
            for model_key in ["logistic_regression", "random_forest", "xgboost", "catboost", "ann"]:
                model_path = os.path.join(MODELS_DIR, f"{disease}_{model_key}.joblib")
                if os.path.exists(model_path):
                    self.models[f"{disease}_{model_key}"] = joblib.load(model_path)

    def get_best_model_key(self, disease: str) -> str:
        if disease in self.evaluation_meta and "best_model_key" in self.evaluation_meta[disease]:
            return self.evaluation_meta[disease]["best_model_key"]
        return "random_forest"

    def get_model_display_name(self, disease: str, model_key: str) -> str:
        if (
            disease in self.evaluation_meta
            and "models" in self.evaluation_meta[disease]
            and model_key in self.evaluation_meta[disease]["models"]
        ):
            return self.evaluation_meta[disease]["models"][model_key]["model_name"]
        return model_key.replace("_", " ").title()

    def prepare_input_vector(self, disease: str, raw_inputs: Dict[str, Any]) -> pd.DataFrame:
        feature_names = self.feature_specs.get(disease, [])
        if not feature_names:
            raise ValueError(f"Feature specifications not found for disease '{disease}'")

        vector_data = {}
        for feat in feature_names:
            if feat in raw_inputs:
                vector_data[feat] = [float(raw_inputs[feat])]
            else:
                vector_data[feat] = [0.0]

        return pd.DataFrame(vector_data)

    def predict(self, disease: str, raw_inputs: Dict[str, Any], requested_model: str = None) -> Dict[str, Any]:
        if not self.feature_specs:
            self.load_artifacts()

        disease = disease.lower()
        if disease not in self.feature_specs:
            raise ValueError(f"Unknown disease '{disease}'. Supported: heart, diabetes, stroke, hypertension")

        best_key = self.get_best_model_key(disease)
        model_key = (requested_model or best_key).lower()
        full_key = f"{disease}_{model_key}"

        if full_key not in self.models:
            raise ValueError(f"Model '{model_key}' not found for disease '{disease}'")

        model = self.models[full_key]
        df_vector = self.prepare_input_vector(disease, raw_inputs)

        # Scale if required by linear / ANN models
        if model_key in ["logistic_regression", "ann"]:
            scaler = self.scalers.get(disease)
            if scaler:
                input_data = scaler.transform(df_vector)
            else:
                input_data = df_vector
        else:
            input_data = df_vector

        # Predict probabilities
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(input_data)[0]
            prob = float(probs[1]) if len(probs) > 1 else float(probs[0])
        else:
            pred = model.predict(input_data)[0]
            prob = float(pred)

        risk_percent = round(prob * 100.0, 1)

        # Clinically calibrated risk categorization
        if risk_percent < 30.0:
            prediction_label = "Low Risk"
        elif risk_percent < 65.0:
            prediction_label = "Moderate Risk"
        else:
            prediction_label = "High Risk"

        confidence = round(abs(prob - 0.5) * 2.0, 3)

        return {
            "disease": disease.capitalize(),
            "risk_probability": round(prob, 4),
            "risk_percentage": risk_percent,
            "prediction": prediction_label,
            "model_key": model_key,
            "model_name": self.get_model_display_name(disease, model_key),
            "is_best_model": (model_key == best_key),
            "confidence_score": confidence,
            "features_used": raw_inputs
        }


predictor = PredictorEngine()
