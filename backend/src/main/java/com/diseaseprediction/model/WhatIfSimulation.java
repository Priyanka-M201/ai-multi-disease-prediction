package com.diseaseprediction.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "what_if_simulations")
public class WhatIfSimulation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "patient_id", nullable = false)
    private Patient patient;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "prediction_id")
    private Prediction prediction;

    @Column(nullable = false, length = 60)
    private String disease;

    @Column(name = "original_risk", nullable = false)
    private Double originalRisk;

    @Column(name = "simulated_risk", nullable = false)
    private Double simulatedRisk;

    @Column(name = "risk_difference", nullable = false)
    private Double riskDifference;

    @Lob
    @Column(name = "modified_features_json", nullable = false, columnDefinition = "TEXT")
    private String modifiedFeaturesJson;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    public WhatIfSimulation() {}

    public WhatIfSimulation(Long id, Patient patient, Prediction prediction, String disease, Double originalRisk,
                            Double simulatedRisk, Double riskDifference, String modifiedFeaturesJson) {
        this.id = id;
        this.patient = patient;
        this.prediction = prediction;
        this.disease = disease;
        this.originalRisk = originalRisk;
        this.simulatedRisk = simulatedRisk;
        this.riskDifference = riskDifference;
        this.modifiedFeaturesJson = modifiedFeaturesJson;
    }

    public static WhatIfSimulationBuilder builder() {
        return new WhatIfSimulationBuilder();
    }

    public static class WhatIfSimulationBuilder {
        private Long id;
        private Patient patient;
        private Prediction prediction;
        private String disease;
        private Double originalRisk;
        private Double simulatedRisk;
        private Double riskDifference;
        private String modifiedFeaturesJson;

        public WhatIfSimulationBuilder id(Long id) { this.id = id; return this; }
        public WhatIfSimulationBuilder patient(Patient patient) { this.patient = patient; return this; }
        public WhatIfSimulationBuilder prediction(Prediction prediction) { this.prediction = prediction; return this; }
        public WhatIfSimulationBuilder disease(String disease) { this.disease = disease; return this; }
        public WhatIfSimulationBuilder originalRisk(Double originalRisk) { this.originalRisk = originalRisk; return this; }
        public WhatIfSimulationBuilder simulatedRisk(Double simulatedRisk) { this.simulatedRisk = simulatedRisk; return this; }
        public WhatIfSimulationBuilder riskDifference(Double riskDifference) { this.riskDifference = riskDifference; return this; }
        public WhatIfSimulationBuilder modifiedFeaturesJson(String modifiedFeaturesJson) { this.modifiedFeaturesJson = modifiedFeaturesJson; return this; }

        public WhatIfSimulation build() {
            return new WhatIfSimulation(id, patient, prediction, disease, originalRisk, simulatedRisk, riskDifference, modifiedFeaturesJson);
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

    public Prediction getPrediction() { return prediction; }
    public void setPrediction(Prediction prediction) { this.prediction = prediction; }

    public String getDisease() { return disease; }
    public void setDisease(String disease) { this.disease = disease; }

    public Double getOriginalRisk() { return originalRisk; }
    public void setOriginalRisk(Double originalRisk) { this.originalRisk = originalRisk; }

    public Double getSimulatedRisk() { return simulatedRisk; }
    public void setSimulatedRisk(Double simulatedRisk) { this.simulatedRisk = simulatedRisk; }

    public Double getRiskDifference() { return riskDifference; }
    public void setRiskDifference(Double riskDifference) { this.riskDifference = riskDifference; }

    public String getModifiedFeaturesJson() { return modifiedFeaturesJson; }
    public void setModifiedFeaturesJson(String modifiedFeaturesJson) { this.modifiedFeaturesJson = modifiedFeaturesJson; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
