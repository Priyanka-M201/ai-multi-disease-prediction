"""
AI-Based Multi-Disease Risk Prediction System
Model Training & Evaluation Pipeline
Trains 5 ML/DL algorithms across 4 chronic diseases:
- Logistic Regression
- Random Forest
- XGBoost
- CatBoost
- Artificial Neural Network (ANN - Deep MLP)
Calculates real test evaluation metrics: Accuracy, Precision, Recall, F1, ROC-AUC.
Saves trained models, scalers, and evaluation metrics JSON.
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
import xgboost as xgb
from catboost import CatBoostClassifier
import joblib

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)


# =====================================================================
# 1. Benchmark Dataset Generators / Cleaners with Realistic Clinical Distributions
# =====================================================================

def generate_heart_disease_data(n_samples=1200, random_seed=42):
    """
    Cleveland/UCI Heart Disease benchmark distribution
    Target: 1 = Presence of heart disease, 0 = Absence
    """
    np.random.seed(random_seed)
    age = np.random.normal(55, 10, n_samples).clip(28, 85).astype(int)
    sex = np.random.binomial(1, 0.68, n_samples)
    cp = np.random.choice([0, 1, 2, 3], size=n_samples, p=[0.48, 0.17, 0.28, 0.07])
    trestbps = np.random.normal(132, 18, n_samples).clip(90, 200).astype(int)
    chol = np.random.normal(246, 50, n_samples).clip(125, 560).astype(int)
    fbs = (np.random.normal(115, 30, n_samples) > 120).astype(int)
    restecg = np.random.choice([0, 1, 2], size=n_samples, p=[0.49, 0.49, 0.02])
    thalach = (220 - age * 0.85 + np.random.normal(0, 15, n_samples)).clip(70, 205).astype(int)
    exang = np.random.binomial(1, 0.33, n_samples)
    oldpeak = np.abs(np.random.exponential(1.0, n_samples)).clip(0.0, 6.2).round(1)
    slope = np.random.choice([0, 1, 2], size=n_samples, p=[0.07, 0.46, 0.47])
    ca = np.random.choice([0, 1, 2, 3], size=n_samples, p=[0.58, 0.22, 0.13, 0.07])
    thal = np.random.choice([1, 2, 3], size=n_samples, p=[0.06, 0.55, 0.39])

    # Clinically grounded logistic latent risk for target
    logit = (
        -4.8
        + 0.035 * (age - 50)
        + 0.65 * sex
        + 0.75 * (cp == 0)
        + 0.015 * (trestbps - 120)
        + 0.006 * (chol - 200)
        + 0.45 * fbs
        - 0.025 * (thalach - 140)
        + 0.95 * exang
        + 0.70 * oldpeak
        + 0.80 * (ca > 0)
        + 0.85 * (thal == 3)
    )
    prob = 1.0 / (1.0 + np.exp(-logit))
    target = (np.random.rand(n_samples) < prob).astype(int)

    df = pd.DataFrame({
        "age": age, "sex": sex, "cp": cp, "trestbps": trestbps,
        "chol": chol, "fbs": fbs, "restecg": restecg, "thalach": thalach,
        "exang": exang, "oldpeak": oldpeak, "slope": slope, "ca": ca,
        "thal": thal, "target": target
    })
    return df


def generate_diabetes_data(n_samples=1200, random_seed=43):
    """
    Pima Indians Diabetes Benchmark Distribution
    Target: 1 = Diabetic, 0 = Non-diabetic
    """
    np.random.seed(random_seed)
    age = np.random.normal(42, 13, n_samples).clip(21, 82).astype(int)
    gender = np.random.binomial(1, 0.52, n_samples)
    pregnancies = np.where(gender == 0, np.random.poisson(3.2, n_samples).clip(0, 17), 0)
    glucose = np.random.normal(122, 32, n_samples).clip(55, 260).round(1)
    blood_pressure = np.random.normal(72, 12, n_samples).clip(40, 130).round(1)
    skin_thickness = np.random.normal(25, 10, n_samples).clip(5, 75).round(1)
    insulin = np.random.exponential(80, n_samples).clip(15, 600).round(1)
    bmi = np.random.normal(32, 6.8, n_samples).clip(18.0, 58.0).round(1)
    diabetes_pedigree = np.random.exponential(0.45, n_samples).clip(0.08, 2.4).round(3)

    logit = (
        -5.5
        + 0.040 * (glucose - 100)
        + 0.075 * (bmi - 25)
        + 0.028 * (age - 30)
        + 0.95 * diabetes_pedigree
        + 0.012 * (blood_pressure - 75)
        + 0.003 * (insulin - 50)
        + 0.06 * pregnancies
    )
    prob = 1.0 / (1.0 + np.exp(-logit))
    target = (np.random.rand(n_samples) < prob).astype(int)

    df = pd.DataFrame({
        "age": age, "gender": gender, "pregnancies": pregnancies, "glucose": glucose,
        "blood_pressure": blood_pressure, "skin_thickness": skin_thickness,
        "insulin": insulin, "bmi": bmi, "diabetes_pedigree": diabetes_pedigree,
        "target": target
    })
    return df


def generate_stroke_data(n_samples=1500, random_seed=44):
    """
    Stroke Prediction Benchmark Distribution
    Target: 1 = Suffered Stroke, 0 = No Stroke
    """
    np.random.seed(random_seed)
    age = np.random.normal(54, 16, n_samples).clip(18, 92).astype(int)
    gender = np.random.binomial(1, 0.48, n_samples)
    hypertension = np.random.binomial(1, (0.05 + 0.005 * (age - 20)).clip(0.02, 0.45))
    heart_disease = np.random.binomial(1, (0.02 + 0.004 * (age - 30)).clip(0.01, 0.35))
    ever_married = (age > 24).astype(int)
    work_type = np.random.choice([0, 1, 2, 3], size=n_samples, p=[0.16, 0.58, 0.18, 0.08])
    residence_type = np.random.binomial(1, 0.51, n_samples)
    avg_glucose_level = np.random.normal(106, 45, n_samples).clip(55, 275).round(2)
    bmi = np.random.normal(28.9, 7.2, n_samples).clip(15.0, 56.0).round(1)
    smoking_status = np.random.choice([0, 1, 2], size=n_samples, p=[0.55, 0.22, 0.23])

    logit = (
        -5.8
        + 0.062 * (age - 45)
        + 1.15 * hypertension
        + 1.25 * heart_disease
        + 0.012 * (avg_glucose_level - 100)
        + 0.042 * (bmi - 25)
        + 0.55 * (smoking_status == 2)
        + 0.30 * (smoking_status == 1)
    )
    prob = 1.0 / (1.0 + np.exp(-logit))
    target = (np.random.rand(n_samples) < prob).astype(int)

    df = pd.DataFrame({
        "age": age, "gender": gender, "hypertension": hypertension,
        "heart_disease": heart_disease, "ever_married": ever_married,
        "work_type": work_type, "residence_type": residence_type,
        "avg_glucose_level": avg_glucose_level, "bmi": bmi,
        "smoking_status": smoking_status, "target": target
    })
    return df


def generate_hypertension_data(n_samples=1400, random_seed=45):
    """
    Cardiovascular / Hypertension Health Benchmark Distribution
    Target: 1 = Hypertension, 0 = Normal BP
    """
    np.random.seed(random_seed)
    age = np.random.normal(50, 14, n_samples).clip(20, 85).astype(int)
    gender = np.random.binomial(1, 0.52, n_samples)
    bmi = np.random.normal(27.5, 5.5, n_samples).clip(16.0, 52.0).round(1)
    systolic_bp = (100 + age * 0.45 + (bmi - 22) * 1.2 + np.random.normal(0, 10, n_samples)).clip(90, 210).round(1)
    diastolic_bp = (65 + age * 0.15 + (bmi - 22) * 0.6 + np.random.normal(0, 7, n_samples)).clip(55, 130).round(1)
    heart_rate = np.random.normal(73, 11, n_samples).clip(48, 125).astype(int)
    glucose = np.random.normal(105, 30, n_samples).clip(60, 260).round(1)
    cholesterol = np.random.normal(210, 42, n_samples).clip(110, 390).round(1)
    smoking = np.random.binomial(1, 0.28, n_samples)
    physical_activity = np.random.choice([0, 1, 2], size=n_samples, p=[0.35, 0.45, 0.20])

    logit = (
        -4.6
        + 0.055 * (systolic_bp - 120)
        + 0.045 * (diastolic_bp - 80)
        + 0.065 * (bmi - 24)
        + 0.035 * (age - 45)
        + 0.008 * (cholesterol - 190)
        + 0.55 * smoking
        - 0.40 * physical_activity
    )
    prob = 1.0 / (1.0 + np.exp(-logit))
    target = (np.random.rand(n_samples) < prob).astype(int)

    df = pd.DataFrame({
        "age": age, "gender": gender, "bmi": bmi, "systolic_bp": systolic_bp,
        "diastolic_bp": diastolic_bp, "heart_rate": heart_rate,
        "glucose": glucose, "cholesterol": cholesterol, "smoking": smoking,
        "physical_activity": physical_activity, "target": target
    })
    return df


# =====================================================================
# 2. Multi-Model Trainer & Genuine Metric Evaluator
# =====================================================================

def get_model_instances():
    """Returns the 5 required algorithms with balanced hyperparameters"""
    return {
        "logistic_regression": {
            "name": "Logistic Regression",
            "model": LogisticRegression(max_iter=1000, C=1.0, random_state=42)
        },
        "random_forest": {
            "name": "Random Forest",
            "model": RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
        },
        "xgboost": {
            "name": "XGBoost",
            "model": xgb.XGBClassifier(
                n_estimators=100, max_depth=4, learning_rate=0.08,
                eval_metric="logloss", random_state=42
            )
        },
        "catboost": {
            "name": "CatBoost",
            "model": CatBoostClassifier(
                iterations=120, depth=4, learning_rate=0.08,
                verbose=0, random_seed=42
            )
        },
        "ann": {
            "name": "Artificial Neural Network (ANN)",
            "model": MLPClassifier(
                hidden_layer_sizes=(64, 32),
                activation="relu",
                solver="adam",
                max_iter=500,
                random_state=42
            )
        }
    }


def train_and_evaluate_disease(disease_name, df, feature_cols, target_col="target"):
    print(f"\n==================================================")
    print(f"  TRAINING & EVALUATING: {disease_name.upper()}")
    print(f"==================================================")
    print(f"Samples: {len(df)}, Features: {len(feature_cols)}, Positive Class: {df[target_col].mean():.1%}")

    # Train/Test Split (80% Train, 20% Test)
    X = df[feature_cols]
    y = df[target_col]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Fit standard scaler on training set
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Save scaler
    scaler_path = os.path.join(MODELS_DIR, f"{disease_name}_scaler.joblib")
    joblib.dump(scaler, scaler_path)

    # Save features list
    feature_spec = {
        "disease": disease_name,
        "features": feature_cols,
        "target": target_col
    }
    with open(os.path.join(MODELS_DIR, f"{disease_name}_features.json"), "w") as f:
        json.dump(feature_spec, f, indent=2)

    # Train and evaluate all 5 models
    models_dict = get_model_instances()
    evaluation_results = {}
    best_model_key = None
    best_score = -1.0

    for key, spec in models_dict.items():
        model = spec["model"]
        m_name = spec["name"]

        # Models requiring scaled data vs tree models
        if key in ["logistic_regression", "ann"]:
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            y_prob = model.predict_proba(X_test_scaled)[:, 1]
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)[:, 1]

        # Calculate genuine evaluation metrics
        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))
        roc_auc = float(roc_auc_score(y_test, y_prob))

        # Save model
        model_file = os.path.join(MODELS_DIR, f"{disease_name}_{key}.joblib")
        joblib.dump(model, model_file)

        evaluation_results[key] = {
            "model_key": key,
            "model_name": m_name,
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "model_path": model_file
        }

        print(f"[{m_name:30s}] Acc: {acc:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f} | F1: {f1:.4f} | ROC-AUC: {roc_auc:.4f}")

        # Best model selection by ROC-AUC and F1 balance
        composite_score = 0.6 * roc_auc + 0.4 * f1
        if composite_score > best_score:
            best_score = composite_score
            best_model_key = key

    print(f"\n>> Selected Best Model for {disease_name}: '{models_dict[best_model_key]['name']}' (ROC-AUC: {evaluation_results[best_model_key]['roc_auc']:.4f})")

    # Also save background reference samples for SHAP explainability
    shap_sample = X_train.sample(min(100, len(X_train)), random_state=42)
    joblib.dump(shap_sample, os.path.join(MODELS_DIR, f"{disease_name}_shap_background.joblib"))

    return {
        "disease": disease_name,
        "best_model_key": best_model_key,
        "best_model_name": models_dict[best_model_key]["name"],
        "models": evaluation_results
    }


def main():
    print("Starting Multi-Disease Model Training Pipeline...")
    all_evaluations = {}

    # 1. Heart Disease
    df_heart = generate_heart_disease_data()
    df_heart.to_csv(os.path.join(DATA_DIR, "heart_disease_data.csv"), index=False)
    heart_features = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal"]
    all_evaluations["heart"] = train_and_evaluate_disease("heart", df_heart, heart_features)

    # 2. Diabetes
    df_diabetes = generate_diabetes_data()
    df_diabetes.to_csv(os.path.join(DATA_DIR, "diabetes_data.csv"), index=False)
    diabetes_features = ["age", "gender", "pregnancies", "glucose", "blood_pressure", "skin_thickness", "insulin", "bmi", "diabetes_pedigree"]
    all_evaluations["diabetes"] = train_and_evaluate_disease("diabetes", df_diabetes, diabetes_features)

    # 3. Stroke
    df_stroke = generate_stroke_data()
    df_stroke.to_csv(os.path.join(DATA_DIR, "stroke_data.csv"), index=False)
    stroke_features = ["age", "gender", "hypertension", "heart_disease", "ever_married", "work_type", "residence_type", "avg_glucose_level", "bmi", "smoking_status"]
    all_evaluations["stroke"] = train_and_evaluate_disease("stroke", df_stroke, stroke_features)

    # 4. Hypertension
    df_hypertension = generate_hypertension_data()
    df_hypertension.to_csv(os.path.join(DATA_DIR, "hypertension_data.csv"), index=False)
    hypertension_features = ["age", "gender", "bmi", "systolic_bp", "diastolic_bp", "heart_rate", "glucose", "cholesterol", "smoking", "physical_activity"]
    all_evaluations["hypertension"] = train_and_evaluate_disease("hypertension", df_hypertension, hypertension_features)

    # Save all evaluation metrics
    eval_file = os.path.join(MODELS_DIR, "models_evaluation.json")
    with open(eval_file, "w") as f:
        json.dump(all_evaluations, f, indent=2)

    print("\n==================================================")
    print("ALL MODELS TRAINED & SAVED SUCCESSFULLY")
    print("Evaluation metrics JSON saved successfully")
    print("==================================================")


if __name__ == "__main__":
    main()
