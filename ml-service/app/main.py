import os
import json
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import (
    HeartDiseaseInput, DiabetesInput, StrokeInput,
    PredictionResponse, ExplanationResponse, SimulationRequest, SimulationResponse
)
from .predictor import predictor, MODELS_DIR, SUPPORTED_DISEASES
from .explainer import shap_engine
from .simulator import simulator

app = FastAPI(
    title="Deep Learning-Based Multi-Disease Risk Prediction & Explainability ML Service",
    description="FastAPI service hosting ANN & DNN Deep Learning models across Diabetes, Heart Disease, and Stroke with SHAP Explainable AI and What-If counterfactual simulation.",
    version="2.0.0"
)

# Enable CORS for Spring Boot backend and local web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "UP",
        "service": "Deep Learning Multi-Disease ML Service",
        "diseases_supported": SUPPORTED_DISEASES,
        "architectures_supported": ["ann", "dnn"],
        "algorithms_loaded": list(predictor.models.keys()),
        "total_models": len(predictor.models)
    }


@app.get("/models/metrics")
def get_model_metrics():
    """Returns genuine evaluation metrics (Accuracy, Precision, Recall, F1, ROC-AUC) across ANN and DNN models for all 3 supported diseases."""
    eval_file = os.path.join(MODELS_DIR, "models_evaluation.json")
    if not os.path.exists(eval_file):
        raise HTTPException(status_code=404, detail="Model evaluation metrics file not found. Please train models first.")
    with open(eval_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


# Dedicated Disease Prediction Endpoints

@app.post("/predict/diabetes", response_model=PredictionResponse)
def predict_diabetes(inputs: DiabetesInput):
    try:
        raw = inputs.model_dump()
        m_name = raw.pop("model_name", None)
        return predictor.predict("diabetes", raw, m_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/predict/heart", response_model=PredictionResponse)
def predict_heart(inputs: HeartDiseaseInput):
    try:
        raw = inputs.model_dump()
        m_name = raw.pop("model_name", None)
        return predictor.predict("heart", raw, m_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/predict/stroke", response_model=PredictionResponse)
def predict_stroke(inputs: StrokeInput):
    try:
        raw = inputs.model_dump()
        m_name = raw.pop("model_name", None)
        return predictor.predict("stroke", raw, m_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/predict/{disease}", response_model=PredictionResponse)
def predict_generic(disease: str, inputs: Dict[str, Any]):
    try:
        inputs_copy = dict(inputs)
        m_name = inputs_copy.pop("model_name", None)
        return predictor.predict(disease, inputs_copy, m_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Explainable AI (SHAP) Endpoint

@app.post("/explain/{disease}", response_model=ExplanationResponse)
def explain_prediction(disease: str, inputs: Dict[str, Any]):
    try:
        inputs_copy = dict(inputs)
        m_name = inputs_copy.pop("model_name", None)
        return shap_engine.explain(disease, inputs_copy, m_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# What-If Counterfactual Simulation Endpoint

@app.post("/simulate", response_model=SimulationResponse)
def simulate_counterfactual(payload: SimulationRequest):
    try:
        return simulator.simulate(
            disease=payload.disease,
            original_inputs=payload.original_inputs,
            simulated_inputs=payload.simulated_inputs,
            model_name=payload.model_name
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/what-if", response_model=SimulationResponse)
def what_if_alias(payload: SimulationRequest):
    return simulate_counterfactual(payload)
