"""
End-to-End Automated Test Suite for Deep Learning Multi-Disease System
Tests:
1. Model loading & metrics (ANN & DNN only for Diabetes, Heart Disease, Stroke)
2. Diabetes risk prediction & SHAP attribution
3. Heart Disease risk prediction & SHAP attribution
4. Stroke risk prediction & SHAP attribution
5. Counterfactual What-If simulation recalculations
6. Strict rejection of unsupported diseases (Hypertension) and legacy ML models
"""

import urllib.request
import urllib.error
import json
import sys


def assert_true(cond, msg):
    if not cond:
        print(f"FAILED: {msg}")
        sys.exit(1)
    else:
        print(f"PASSED: {msg}")


def test_api():
    print("\n--- TEST 1: Model Loading & Metrics API ---")
    metrics_url = "http://localhost:8080/api/models/metrics"
    req = urllib.request.Request(metrics_url)
    res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    data = res.get("data", res)

    diseases = list(data.keys())
    assert_true("hypertension" not in diseases, "Hypertension removed from benchmark metrics")
    assert_true(set(diseases) == {"diabetes", "heart", "stroke"}, f"Strictly 3 diseases supported: {diseases}")

    for d in diseases:
        models = data[d]["models"]
        assert_true(set(models.keys()) == {"ann", "dnn"}, f"{d} has strictly ANN and DNN: {list(models.keys())}")
        best = data[d]["best_model_key"]
        assert_true(best in ["ann", "dnn"], f"{d} best model is deep learning: {best}")
        print(f"   * {d.upper()}: Best architecture is {best.upper()} (ROC-AUC: {models[best]['roc_auc']}, F1: {models[best]['f1_score']})")

    print("\n--- TEST 2: Diabetes Prediction & SHAP (Pima Benchmark) ---")
    pred_url = "http://localhost:8080/api/predictions/public"
    diabetes_payload = {
        "disease": "diabetes",
        "modelName": "ann",
        "inputs": {
            "age": 48, "gender": 1, "pregnancies": 0, "glucose": 172.0,
            "blood_pressure": 88.0, "skin_thickness": 32.0, "insulin": 180.0,
            "bmi": 34.5, "diabetes_pedigree": 0.85
        }
    }
    req = urllib.request.Request(pred_url, data=json.dumps(diabetes_payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))["data"]
    assert_true(res["prediction"] in ["Low Risk", "Moderate Risk", "High Risk"], f"Valid risk label: {res['prediction']}")
    assert_true(len(res["contributions"]) == 9, f"SHAP evaluated all 9 features: {len(res['contributions'])}")
    print(f"   * Diabetes risk: {res['riskPercentage']}% ({res['prediction']}) via {res['modelName']}")
    print(f"   * Top SHAP driver: {res['contributions'][0]['feature']} ({res['contributions'][0]['description']})")

    print("\n--- TEST 3: Heart Disease Prediction & SHAP (UCI Cleveland) ---")
    heart_payload = {
        "disease": "heart",
        "modelName": "dnn",
        "inputs": {
            "age": 62, "sex": 1, "cp": 0, "trestbps": 155.0, "chol": 270.0, "fbs": 1,
            "restecg": 1, "thalach": 120.0, "exang": 1, "oldpeak": 2.6, "slope": 1,
            "ca": 2, "thal": 3
        }
    }
    req = urllib.request.Request(pred_url, data=json.dumps(heart_payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))["data"]
    assert_true(res["prediction"] in ["Low Risk", "Moderate Risk", "High Risk"], f"Valid heart risk label: {res['prediction']}")
    assert_true(len(res["contributions"]) == 13, f"SHAP evaluated all 13 features: {len(res['contributions'])}")
    print(f"   * Heart risk: {res['riskPercentage']}% ({res['prediction']}) via {res['modelName']}")
    print(f"   * Top SHAP driver: {res['contributions'][0]['feature']}")

    print("\n--- TEST 4: Stroke Prediction & SHAP (Healthcare Stroke) ---")
    stroke_payload = {
        "disease": "stroke",
        "modelName": "dnn",
        "inputs": {
            "age": 70, "gender": 1, "hypertension": 1, "heart_disease": 1, "ever_married": 1,
            "work_type": 1, "residence_type": 1, "avg_glucose_level": 185.0, "bmi": 33.2,
            "smoking_status": 2
        }
    }
    req = urllib.request.Request(pred_url, data=json.dumps(stroke_payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))["data"]
    assert_true(res["prediction"] in ["Low Risk", "Moderate Risk", "High Risk"], f"Valid stroke risk label: {res['prediction']}")
    assert_true(len(res["contributions"]) == 10, f"SHAP evaluated all 10 features: {len(res['contributions'])}")
    print(f"   * Stroke risk: {res['riskPercentage']}% ({res['prediction']}) via {res['modelName']}")

    print("\n--- TEST 5: Counterfactual What-If Simulation ---")
    sim_url = "http://localhost:8080/api/simulations/public"
    sim_payload = {
        "disease": "diabetes",
        "modelName": "ann",
        "originalInputs": diabetes_payload["inputs"],
        "simulatedInputs": {
            "age": 48, "gender": 1, "pregnancies": 0, "glucose": 105.0,
            "blood_pressure": 75.0, "skin_thickness": 22.0, "insulin": 75.0,
            "bmi": 24.5, "diabetes_pedigree": 0.85
        }
    }
    req = urllib.request.Request(sim_url, data=json.dumps(sim_payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))["data"]
    assert_true(res["simulatedRiskPercentage"] < res["originalRiskPercentage"], "What-If lifestyle changes reduced simulated risk")
    assert_true(len(res["keyImprovements"]) > 0, "Key improvements listed")
    print(f"   * Original Risk: {res['originalRiskPercentage']}% -> Simulated Risk: {res['simulatedRiskPercentage']}% (Delta: {res['riskDifference']}%)")

    print("\n--- TEST 6: Validation Rejections ---")
    # Test rejection of hypertension
    try:
        bad_req = urllib.request.Request(
            pred_url,
            data=json.dumps({"disease": "hypertension", "inputs": {}}).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(bad_req)
        assert_true(False, "Hypertension should have been rejected")
    except urllib.error.HTTPError as e:
        assert_true(e.code == 400, f"Hypertension properly rejected with 400 Bad Request (HTTP {e.code})")

    # Test rejection of unsupported machine learning algorithm
    try:
        bad_model_req = urllib.request.Request(
            pred_url,
            data=json.dumps({"disease": "diabetes", "modelName": "xgboost", "inputs": diabetes_payload["inputs"]}).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(bad_model_req)
        assert_true(False, "Legacy ML model should have been rejected")
    except urllib.error.HTTPError as e:
        assert_true(e.code == 400, f"Legacy ML model rejected with 400 Bad Request (HTTP {e.code})")

    print("\n=======================================================")
    print("  ALL 6 END-TO-END VALIDATION TESTS PASSED SUCCESSFULLY!")
    print("=======================================================")


if __name__ == "__main__":
    test_api()
