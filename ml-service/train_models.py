"""
Deep Learning-Based Multi-Disease Risk Prediction System
Training & Evaluation Pipeline: Exclusively ANN & DNN Deep Learning Architectures
Targets:
1. Diabetes (Pima Indians Diabetes Benchmark)
2. Heart Disease (UCI Cleveland Heart Disease Benchmark)
3. Stroke (Healthcare Stroke Prediction Benchmark)

Evaluates:
- ANN (Artificial Neural Network): Feed-forward neural network (64, 32)
- DNN (Deep Neural Network): Deep architecture (128, 64, 32, 16) with regularized Adam optimization
Metrics: Accuracy, Precision, Recall, F1-Score, ROC-AUC, and Confusion Matrix.
Saves: Trained models, Scalers, Background distributions for SHAP, and models_evaluation.json.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
)
from sklearn.neural_network import MLPClassifier
from sklearn.utils import resample
import joblib

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)


# =====================================================================
# 1. Benchmark Datasets Loader & Preprocessing
# =====================================================================

def load_or_verify_heart_data():
    """
    Cleveland/UCI Heart Disease Benchmark
    13 features: age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal
    Target: 1 = Presence of heart disease, 0 = Absence
    """
    path = os.path.join(DATA_DIR, "heart_disease_data.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
    else:
        raise FileNotFoundError(f"Missing dataset: {path}")

    df = df.dropna().drop_duplicates()
    return df, [
        "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
        "thalach", "exang", "oldpeak", "slope", "ca", "thal"
    ]


def load_or_verify_diabetes_data():
    """
    Pima Indians Diabetes Benchmark
    9 features: age, gender, pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, diabetes_pedigree
    Target: 1 = Diabetic, 0 = Non-diabetic
    """
    path = os.path.join(DATA_DIR, "diabetes_data.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
    else:
        raise FileNotFoundError(f"Missing dataset: {path}")

    df = df.dropna().drop_duplicates()
    return df, [
        "age", "gender", "pregnancies", "glucose", "blood_pressure",
        "skin_thickness", "insulin", "bmi", "diabetes_pedigree"
    ]


def load_or_verify_stroke_data():
    """
    Healthcare Stroke Benchmark
    10 features: age, gender, hypertension, heart_disease, ever_married, work_type, residence_type, avg_glucose_level, bmi, smoking_status
    Target: 1 = Stroke, 0 = No Stroke
    """
    path = os.path.join(DATA_DIR, "stroke_data.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
    else:
        raise FileNotFoundError(f"Missing dataset: {path}")

    df = df.dropna().drop_duplicates()
    return df, [
        "age", "gender", "hypertension", "heart_disease", "ever_married",
        "work_type", "residence_type", "avg_glucose_level", "bmi", "smoking_status"
    ]


# =====================================================================
# 2. ANN and DNN Architecture Instantiation
# =====================================================================

def get_deep_learning_models(input_dim):
    """
    Returns strictly ANN and DNN feed-forward deep learning models:
    - ANN (Artificial Neural Network): Feed-forward network (64, 32)
    - DNN (Deep Neural Network): Deep architecture (128, 64, 32, 16) with regularized Adam optimization
    """
    return {
        "ann": {
            "name": "Artificial Neural Network (ANN)",
            "description": "Feed-Forward Neural Network with 2 hidden layers (64, 32) and ReLU activations.",
            "layers": [input_dim, 64, 32, 1],
            "model": MLPClassifier(
                hidden_layer_sizes=(64, 32),
                activation="relu",
                solver="adam",
                alpha=0.001,
                learning_rate_init=0.003,
                max_iter=800,
                early_stopping=True,
                validation_fraction=0.15,
                n_iter_no_change=30,
                random_state=42
            )
        },
        "dnn": {
            "name": "Deep Neural Network (DNN)",
            "description": "Deep Feed-Forward Neural Network with 4 dense hidden layers (128, 64, 32, 16), L2 regularization, and adaptive optimization.",
            "layers": [input_dim, 128, 64, 32, 16, 1],
            "model": MLPClassifier(
                hidden_layer_sizes=(128, 64, 32, 16),
                activation="relu",
                solver="adam",
                alpha=0.003,
                learning_rate_init=0.002,
                max_iter=800,
                early_stopping=True,
                validation_fraction=0.15,
                n_iter_no_change=30,
                random_state=42
            )
        }
    }


# =====================================================================
# 3. Model Training, Evaluation, and Selection Engine
# =====================================================================

def balance_training_set(X_train, y_train):
    """
    Balances the positive risk minority class strictly within the training set
    to avoid class collapse on imbalanced clinical distributions.
    Test set is never touched, preserving authentic prevalence.
    """
    train_df = pd.concat([X_train, y_train], axis=1)
    majority = train_df[train_df[y_train.name] == 0]
    minority = train_df[train_df[y_train.name] == 1]

    if len(minority) == 0 or len(minority) == len(majority):
        return X_train, y_train

    # Upsample minority to match 60% of majority to achieve balanced gradient signals
    target_count = int(len(majority) * 0.6)
    minority_upsampled = resample(
        minority,
        replace=True,
        n_samples=target_count,
        random_state=42
    )

    balanced_df = pd.concat([majority, minority_upsampled]).sample(frac=1.0, random_state=42)
    return balanced_df.drop(columns=[y_train.name]), balanced_df[y_train.name]


def train_and_evaluate_disease(disease_name, df, feature_cols, target_col="target"):
    print(f"\n========================================================")
    print(f"  DEEP LEARNING PIPELINE: {disease_name.upper()}")
    print(f"========================================================")

    X = df[feature_cols].copy()
    y = df[target_col].copy()

    # Stratified Train/Test Split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Balance training set only
    X_train_bal, y_train_bal = balance_training_set(X_train, y_train)

    # Standardize numerical inputs using training distribution only
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_bal)
    X_test_scaled = scaler.transform(X_test)

    # Save preprocessing scaler and feature specs
    scaler_path = os.path.join(MODELS_DIR, f"{disease_name}_scaler.joblib")
    joblib.dump(scaler, scaler_path)

    spec_path = os.path.join(MODELS_DIR, f"{disease_name}_features.json")
    with open(spec_path, "w", encoding="utf-8") as f:
        json.dump({"disease": disease_name, "features": feature_cols}, f, indent=2)

    # Save background samples for SHAP Explainer
    bg_sample_size = min(60, len(X_train))
    bg_df = X_train.sample(n=bg_sample_size, random_state=42)
    bg_path = os.path.join(MODELS_DIR, f"{disease_name}_shap_background.joblib")
    joblib.dump(bg_df, bg_path)

    models_dict = get_deep_learning_models(len(feature_cols))
    evaluations = {}

    best_model_key = None
    best_score = -1.0

    for model_key, meta in models_dict.items():
        print(f"--> Training {meta['name']} on {len(X_train_bal)} samples...")
        clf = meta["model"]
        clf.fit(X_train_scaled, y_train_bal)

        # Evaluate on the untouched held-out test cohort
        y_pred = clf.predict(X_test_scaled)
        y_prob = clf.predict_proba(X_test_scaled)[:, 1]

        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))

        try:
            auc = float(roc_auc_score(y_test, y_prob))
        except Exception:
            auc = 0.5

        cm = confusion_matrix(y_test, y_pred).tolist()

        # Save model weights
        model_save_path = os.path.join(MODELS_DIR, f"{disease_name}_{model_key}.joblib")
        joblib.dump(clf, model_save_path)

        evaluations[model_key] = {
            "model_key": model_key,
            "model_name": meta["name"],
            "description": meta["description"],
            "architecture_layers": meta["layers"],
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(auc, 4),
            "confusion_matrix": cm,
            "iterations_run": int(clf.n_iter_),
            "loss": round(float(clf.loss_), 5),
            "model_path": model_save_path
        }

        print(f"    [{meta['name']}] Acc: {acc:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f} | F1: {f1:.4f} | AUC: {auc:.4f}")

        # Combined composite score: harmonic weighting of balanced accuracy and AUC
        composite_score = (2.0 * f1 + auc) / 3.0
        if composite_score > best_score:
            best_score = composite_score
            best_model_key = model_key

    print(f"=== Selected Optimal Architecture for {disease_name.upper()}: {best_model_key.upper()} (AUC: {evaluations[best_model_key]['roc_auc']:.4f}, F1: {evaluations[best_model_key]['f1_score']:.4f}) ===")

    return {
        "disease": disease_name,
        "features": feature_cols,
        "test_samples": len(X_test),
        "best_model_key": best_model_key,
        "selected_model": evaluations[best_model_key]["model_name"],
        "selection_reason": f"Selected {evaluations[best_model_key]['model_name']} based on test-set ROC-AUC ({evaluations[best_model_key]['roc_auc']:.4f}) and F1-Score ({evaluations[best_model_key]['f1_score']:.4f}) on held-out test cohort.",
        "models": evaluations
    }


def main():
    print("=================================================================")
    print("  DEEP LEARNING MODEL TRAINING & COMPARISON: ANN vs DNN")
    print("  Chronic Diseases: Diabetes, Heart Disease, Stroke")
    print("=================================================================")

    all_evaluations = {}

    # 1. Diabetes
    df_diabetes, diabetes_features = load_or_verify_diabetes_data()
    all_evaluations["diabetes"] = train_and_evaluate_disease("diabetes", df_diabetes, diabetes_features)

    # 2. Heart Disease
    df_heart, heart_features = load_or_verify_heart_data()
    all_evaluations["heart"] = train_and_evaluate_disease("heart", df_heart, heart_features)

    # 3. Stroke
    df_stroke, stroke_features = load_or_verify_stroke_data()
    all_evaluations["stroke"] = train_and_evaluate_disease("stroke", df_stroke, stroke_features)

    # Save comprehensive evaluation report
    eval_file = os.path.join(MODELS_DIR, "models_evaluation.json")
    with open(eval_file, "w", encoding="utf-8") as f:
        json.dump(all_evaluations, f, indent=2)

    print("\nAll Deep Learning models trained and evaluation saved successfully!")


if __name__ == "__main__":
    main()
