package com.diseaseprediction.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "predictions")
public class Prediction {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "patient_id", nullable = false)
    private Patient patient;

    @Column(nullable = false, length = 60)
    private String disease;

    @Column(name = "risk_percentage", nullable = false)
    private Double riskPercentage;

    @Column(name = "risk_probability", nullable = false)
    private Double riskProbability;

    @Column(name = "prediction_result", nullable = false, length = 50)
    private String predictionResult;

    @Column(name = "model_name", nullable = false, length = 100)
    private String modelName;

    @Lob
    @Column(name = "shap_summary_json", columnDefinition = "LONGTEXT")
    private String shapSummaryJson;

    @Lob
    @Column(name = "input_features_json", columnDefinition = "TEXT")
    private String inputFeaturesJson;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    public Prediction() {}

    public Prediction(Long id, Patient patient, String disease, Double riskPercentage, Double riskProbability,
                      String predictionResult, String modelName, String shapSummaryJson, String inputFeaturesJson) {
        this.id = id;
        this.patient = patient;
        this.disease = disease;
        this.riskPercentage = riskPercentage;
        this.riskProbability = riskProbability;
        this.predictionResult = predictionResult;
        this.modelName = modelName;
        this.shapSummaryJson = shapSummaryJson;
        this.inputFeaturesJson = inputFeaturesJson;
    }

    public static PredictionBuilder builder() {
        return new PredictionBuilder();
    }

    public static class PredictionBuilder {
        private Long id;
        private Patient patient;
        private String disease;
        private Double riskPercentage;
        private Double riskProbability;
        private String predictionResult;
        private String modelName;
        private String shapSummaryJson;
        private String inputFeaturesJson;

        public PredictionBuilder id(Long id) { this.id = id; return this; }
        public PredictionBuilder patient(Patient patient) { this.patient = patient; return this; }
        public PredictionBuilder disease(String disease) { this.disease = disease; return this; }
        public PredictionBuilder riskPercentage(Double riskPercentage) { this.riskPercentage = riskPercentage; return this; }
        public PredictionBuilder riskProbability(Double riskProbability) { this.riskProbability = riskProbability; return this; }
        public PredictionBuilder predictionResult(String predictionResult) { this.predictionResult = predictionResult; return this; }
        public PredictionBuilder modelName(String modelName) { this.modelName = modelName; return this; }
        public PredictionBuilder shapSummaryJson(String shapSummaryJson) { this.shapSummaryJson = shapSummaryJson; return this; }
        public PredictionBuilder inputFeaturesJson(String inputFeaturesJson) { this.inputFeaturesJson = inputFeaturesJson; return this; }

        public Prediction build() {
            return new Prediction(id, patient, disease, riskPercentage, riskProbability, predictionResult, modelName, shapSummaryJson, inputFeaturesJson);
        }
    }

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Patient getPatient() { return patient; }
    public void setPatient(Patient patient) { this.patient = patient; }

    public String getDisease() { return disease; }
    public void setDisease(String disease) { this.disease = disease; }

    public Double getRiskPercentage() { return riskPercentage; }
    public void setRiskPercentage(Double riskPercentage) { this.riskPercentage = riskPercentage; }

    public Double getRiskProbability() { return riskProbability; }
    public void setRiskProbability(Double riskProbability) { this.riskProbability = riskProbability; }

    public String getPredictionResult() { return predictionResult; }
    public void setPredictionResult(String predictionResult) { this.predictionResult = predictionResult; }

    public String getModelName() { return modelName; }
    public void setModelName(String modelName) { this.modelName = modelName; }

    public String getShapSummaryJson() { return shapSummaryJson; }
    public void setShapSummaryJson(String shapSummaryJson) { this.shapSummaryJson = shapSummaryJson; }

    public String getInputFeaturesJson() { return inputFeaturesJson; }
    public void setInputFeaturesJson(String inputFeaturesJson) { this.inputFeaturesJson = inputFeaturesJson; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
