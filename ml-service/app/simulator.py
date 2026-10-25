from typing import Dict, Any, List
from .predictor import predictor


class WhatIfSimulatorEngine:
    """Executes What-If clinical counterfactual simulations without mutating original patient records."""

    def simulate(
        self, disease: str, original_inputs: Dict[str, Any], simulated_inputs: Dict[str, Any], model_name: str = None
    ) -> Dict[str, Any]:
        disease = disease.lower()

        # Run original prediction
        orig_res = predictor.predict(disease, original_inputs, model_name)
        # Run simulated prediction
        sim_res = predictor.predict(disease, simulated_inputs, model_name)

        orig_risk = orig_res["risk_percentage"]
        sim_risk = sim_res["risk_percentage"]
        risk_diff = round(sim_risk - orig_risk, 2)

        # Relative risk reduction calculation
        if orig_risk > 0:
            rel_reduction = round(((sim_risk - orig_risk) / orig_risk) * 100.0, 1)
        else:
            rel_reduction = 0.0

        # Identify key modifications and clinically explain their impacts
        key_improvements: List[str] = []
        labels = {
            "bmi": "Body Mass Index (BMI)", "glucose": "Plasma Glucose",
            "trestbps": "Blood Pressure", "systolic_bp": "Systolic Blood Pressure",
            "diastolic_bp": "Diastolic Blood Pressure", "chol": "Cholesterol",
            "cholesterol": "Total Cholesterol", "smoking": "Smoking Habit",
            "smoking_status": "Smoking History", "thalach": "Max Heart Rate",
            "physical_activity": "Physical Activity Level"
        }

        for k, v_sim in simulated_inputs.items():
            if k in original_inputs:
                v_orig = original_inputs[k]
                if v_sim != v_orig:
                    param_name = labels.get(k, k.replace("_", " ").title())
                    if isinstance(v_orig, (int, float)) and isinstance(v_sim, (int, float)):
                        delta_param = v_sim - v_orig
                        direction = "reduced" if delta_param < 0 else "increased"
                        key_improvements.append(
                            f"{param_name} {direction} from {v_orig} to {v_sim} (delta: {delta_param:+.1f})."
                        )
                    else:
                        key_improvements.append(f"{param_name} modified from '{v_orig}' to '{v_sim}'.")

        if not key_improvements:
            key_improvements.append("No parameters were modified in this simulation.")

        return {
            "disease": disease.capitalize(),
            "model_name": orig_res["model_name"],
            "original_risk_probability": orig_res["risk_probability"],
            "original_risk_percentage": orig_risk,
            "simulated_risk_probability": sim_res["risk_probability"],
            "simulated_risk_percentage": sim_risk,
            "risk_difference": risk_diff,
            "relative_reduction_percent": rel_reduction,
            "original_prediction": orig_res["prediction"],
            "simulated_prediction": sim_res["prediction"],
            "key_improvements": key_improvements,
            "disclaimer": (
                "Notice: What-If simulation demonstrates algorithmic sensitivity to input modifications. "
                "It is designed for exploratory scenario comparison, not as a clinical prescription."
            )
        }


simulator = WhatIfSimulatorEngine()
