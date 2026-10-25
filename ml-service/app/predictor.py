import os
import json
import numpy as np
import pandas as pd
import joblib
from typing import Dict, Any, Tuple

MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))
SUPPORTED_DISEASES = ["diabetes", "heart", "stroke"]
SUPPORTED_MODELS = ["ann", "dnn"]


class PredictorEngine:
    """Manages loading of trained ANN and DNN models, scalers, and clinical risk inferences."""

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_specs = {}
        self.evaluation_meta = {}
        self.load_artifacts()

    def load_artifacts(self):
        eval_path = os.path.join(MODELS_DIR, "models_evaluation.json")
        if os.path.exists(eval_path):
            with open(eval_path, "r", encoding="utf-8") as f:
                self.evaluation_meta = json.load(f)

        for disease in SUPPORTED_DISEASES:
            # Load feature specs
            spec_path = os.path.join(MODELS_DIR, f"{disease}_features.json")
            if os.path.exists(spec_path):
                with open(spec_path, "r", encoding="utf-8") as f:
                    self.feature_specs[disease] = json.load(f)["features"]

            # Load scaler
            scaler_path = os.path.join(MODELS_DIR, f"{disease}_scaler.joblib")
            if os.path.exists(scaler_path):
                self.scalers[disease] = joblib.load(scaler_path)

            # Load only ANN and DNN deep learning architectures
            for model_key in SUPPORTED_MODELS:
                model_path = os.path.join(MODELS_DIR, f"{disease}_{model_key}.joblib")
                if os.path.exists(model_path):
                    self.models[f"{disease}_{model_key}"] = joblib.load(model_path)

    def get_best_model_key(self, disease: str) -> str:
        if disease in self.evaluation_meta and "best_model_key" in self.evaluation_meta[disease]:
            return self.evaluation_meta[disease]["best_model_key"]
        return "ann"

    def get_model_display_name(self, disease: str, model_key: str) -> str:
        if (
            disease in self.evaluation_meta
            and "models" in self.evaluation_meta[disease]
            and model_key in self.evaluation_meta[disease]["models"]
        ):
            return self.evaluation_meta[disease]["models"][model_key]["model_name"]
        return "Artificial Neural Network (ANN)" if model_key == "ann" else "Deep Neural Network (DNN)"

    def prepare_input_vector(self, disease: str, raw_inputs: Dict[str, Any]) -> pd.DataFrame:
        feature_names = self.feature_specs.get(disease, [])
        if not feature_names:
            raise ValueError(f"Feature specifications not found for disease '{disease}'")

        vector_data = {}
        for feat in feature_names:
            if feat not in raw_inputs:
                raise ValueError(f"Missing required clinical parameter: '{feat}' for {disease}")
            try:
                vector_data[feat] = [float(raw_inputs[feat])]
            except (ValueError, TypeError):
                raise ValueError(f"Invalid numeric value for parameter '{feat}': {raw_inputs[feat]}")

        return pd.DataFrame(vector_data)

    def predict(self, disease: str, raw_inputs: Dict[str, Any], requested_model: str = None) -> Dict[str, Any]:
        if not self.feature_specs or not self.models:
            self.load_artifacts()

        disease = disease.lower()
        if disease not in SUPPORTED_DISEASES:
            raise ValueError(f"Unknown disease '{disease}'. Supported: {', '.join(SUPPORTED_DISEASES)}")

        best_key = self.get_best_model_key(disease)
        model_key = (requested_model or best_key).lower()
        if model_key not in SUPPORTED_MODELS:
            raise ValueError(f"Invalid architecture '{model_key}'. Only ANN and DNN are supported.")

        full_key = f"{disease}_{model_key}"
        if full_key not in self.models:
            raise ValueError(f"Model '{model_key}' not found for disease '{disease}'. Please verify models exist.")

        model = self.models[full_key]
        df_vector = self.prepare_input_vector(disease, raw_inputs)

        # Apply standardized scaling (both ANN and DNN use standardized inputs)
        scaler = self.scalers.get(disease)
        if scaler:
            input_data = scaler.transform(df_vector)
        else:
            input_data = df_vector.values

        # Predict genuine probability from neural network output layer
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(input_data)[0]
            prob = float(probs[1]) if len(probs) > 1 else float(probs[0])
        else:
            pred = model.predict(input_data)[0]
            prob = float(pred)

        risk_percent = round(prob * 100.0, 1)

        # Documented risk categorization thresholds:
        # < 30.0%: Low Risk, 30.0% - 65.0%: Moderate Risk, >= 65.0%: High Risk
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
