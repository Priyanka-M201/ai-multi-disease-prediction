from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


# Feature Inputs for Each Disease (Strictly Diabetes, Heart Disease, Stroke)

class HeartDiseaseInput(BaseModel):
    age: int = Field(55, description="Patient age in years")
    sex: int = Field(1, description="Gender (1 = male, 0 = female)")
    cp: int = Field(0, description="Chest pain type (0: typical angina, 1: atypical, 2: non-anginal, 3: asymptomatic)")
    trestbps: float = Field(130.0, description="Resting blood pressure in mm Hg")
    chol: float = Field(240.0, description="Serum cholesterol in mg/dl")
    fbs: int = Field(0, description="Fasting blood sugar > 120 mg/dl (1 = true, 0 = false)")
    restecg: int = Field(0, description="Resting ECG results (0, 1, 2)")
    thalach: float = Field(150.0, description="Maximum heart rate achieved")
    exang: int = Field(0, description="Exercise induced angina (1 = yes, 0 = no)")
    oldpeak: float = Field(1.0, description="ST depression induced by exercise relative to rest")
    slope: int = Field(1, description="Slope of peak exercise ST segment (0, 1, 2)")
    ca: int = Field(0, description="Number of major vessels colored by fluoroscopy (0-3)")
    thal: int = Field(2, description="Thalassemia (1 = normal, 2 = fixed defect, 3 = reversible defect)")
    model_name: Optional[str] = Field(None, description="Optional architecture key ('ann' or 'dnn')")


class DiabetesInput(BaseModel):
    age: int = Field(45, description="Patient age in years")
    gender: int = Field(1, description="Gender (1 = male, 0 = female)")
    pregnancies: int = Field(0, description="Number of pregnancies")
    glucose: float = Field(120.0, description="Fasting plasma glucose (mg/dL)")
    blood_pressure: float = Field(75.0, description="Diastolic blood pressure (mm Hg)")
    skin_thickness: float = Field(25.0, description="Triceps skinfold thickness (mm)")
    insulin: float = Field(85.0, description="2-hour serum insulin (mu U/ml)")
    bmi: float = Field(28.5, description="Body mass index (kg/m²)")
    diabetes_pedigree: float = Field(0.45, description="Diabetes pedigree function score")
    model_name: Optional[str] = Field(None, description="Optional architecture key ('ann' or 'dnn')")


class StrokeInput(BaseModel):
    age: int = Field(56, description="Patient age in years")
    gender: int = Field(1, description="Gender (1 = male, 0 = female)")
    hypertension: int = Field(0, description="Hypertension diagnosed (1 = yes, 0 = no)")
    heart_disease: int = Field(0, description="Heart disease diagnosed (1 = yes, 0 = no)")
    ever_married: int = Field(1, description="Ever married (1 = yes, 0 = no)")
    work_type: int = Field(1, description="Work type (0: Govt, 1: Private, 2: Self-employed, 3: Children)")
    residence_type: int = Field(1, description="Residence (1 = Urban, 0 = Rural)")
    avg_glucose_level: float = Field(105.0, description="Average blood glucose level (mg/dL)")
    bmi: float = Field(29.0, description="Body mass index (kg/m²)")
    smoking_status: int = Field(0, description="Smoking status (0: never, 1: formerly, 2: smokes)")
    model_name: Optional[str] = Field(None, description="Optional architecture key ('ann' or 'dnn')")


# Response Schemas

class PredictionResponse(BaseModel):
    disease: str
    risk_probability: float
    risk_percentage: float
    prediction: str  # "Low Risk", "Moderate Risk", "High Risk"
    model_key: str
    model_name: str
    is_best_model: bool
    confidence_score: float
    features_used: Dict[str, Any]


class FeatureContribution(BaseModel):
    feature: str
    raw_feature_name: Optional[str] = None
    value: Any
    shap_value: float
    contribution_percent: float
    direction: str  # "INCREASES_RISK" or "REDUCES_RISK"
    description: str


class ExplanationResponse(BaseModel):
    disease: str
    model_name: str
    base_risk_probability: float
    predicted_risk_probability: float
    contributions: List[FeatureContribution]
    summary_text: str
    disclaimer: str


class SimulationRequest(BaseModel):
    disease: str
    original_inputs: Dict[str, Any]
    simulated_inputs: Dict[str, Any]
    model_name: Optional[str] = None


class SimulationResponse(BaseModel):
    disease: str
    model_name: str
    original_risk_probability: float
    original_risk_percentage: float
    simulated_risk_probability: float
    simulated_risk_percentage: float
    risk_difference: float
    relative_reduction_percent: float
    original_prediction: str
    simulated_prediction: str
    key_improvements: List[str]
    disclaimer: str
