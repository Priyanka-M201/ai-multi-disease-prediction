package com.diseaseprediction.service;

import com.diseaseprediction.dto.SimulationRequestDto;
import com.diseaseprediction.dto.SimulationResponseDto;
import com.diseaseprediction.model.Patient;
import com.diseaseprediction.model.Prediction;
import com.diseaseprediction.model.WhatIfSimulation;
import com.diseaseprediction.repository.PatientRepository;
import com.diseaseprediction.repository.PredictionRepository;
import com.diseaseprediction.repository.WhatIfSimulationRepository;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class WhatIfSimulationService {

    private final MlServiceClient mlServiceClient;
    private final WhatIfSimulationRepository simulationRepository;
    private final PatientRepository patientRepository;
    private final PredictionRepository predictionRepository;
    private final ObjectMapper objectMapper;

    @Transactional
    public SimulationResponseDto simulateAndSave(SimulationRequestDto request) {
        String disease = request.getDisease().toLowerCase().trim();

        // 1. Call ML Service for Counterfactual What-If analysis
        Map<String, Object> simResult = mlServiceClient.simulate(
                disease, request.getOriginalInputs(), request.getSimulatedInputs(), request.getModelName()
        );

        Double origProb = ((Number) simResult.get("original_risk_probability")).doubleValue();
        Double origPercent = ((Number) simResult.get("original_risk_percentage")).doubleValue();
        Double simProb = ((Number) simResult.get("simulated_risk_probability")).doubleValue();
        Double simPercent = ((Number) simResult.get("simulated_risk_percentage")).doubleValue();
        Double riskDiff = ((Number) simResult.get("risk_difference")).doubleValue();
        Double relReduction = ((Number) simResult.get("relative_reduction_percent")).doubleValue();
        String origPred = (String) simResult.get("original_prediction");
        String simPred = (String) simResult.get("simulated_prediction");
        String modelName = (String) simResult.get("model_name");
        String disclaimer = (String) simResult.get("disclaimer");

        @SuppressWarnings("unchecked")
        List<String> keyImprovements = simResult.containsKey("key_improvements")
                ? (List<String>) simResult.get("key_improvements")
                : Collections.emptyList();

        Long savedSimulationId = null;
        Patient patient = null;
        Prediction prediction = null;

        if (request.getPatientId() != null) {
            patient = patientRepository.findById(request.getPatientId()).orElse(null);
        }
        if (request.getPredictionId() != null) {
            prediction = predictionRepository.findById(request.getPredictionId()).orElse(null);
        }

        if (patient != null) {
            try {
                String modifiedJson = objectMapper.writeValueAsString(request.getSimulatedInputs());
                WhatIfSimulation entity = WhatIfSimulation.builder()
                        .patient(patient)
                        .prediction(prediction)
                        .disease(disease.toUpperCase())
                        .originalRisk(origPercent)
                        .simulatedRisk(simPercent)
                        .riskDifference(riskDiff)
                        .modifiedFeaturesJson(modifiedJson)
                        .build();

                WhatIfSimulation saved = simulationRepository.save(entity);
                savedSimulationId = saved.getId();
            } catch (Exception ex) {
                log.error("Failed to save simulation record: {}", ex.getMessage());
            }
        }

        return SimulationResponseDto.builder()
                .id(savedSimulationId)
                .patientId(patient != null ? patient.getId() : null)
                .predictionId(prediction != null ? prediction.getId() : null)
                .disease(disease)
                .modelName(modelName)
                .originalRiskProbability(origProb)
                .originalRiskPercentage(origPercent)
                .simulatedRiskProbability(simProb)
                .simulatedRiskPercentage(simPercent)
                .riskDifference(riskDiff)
                .relativeReductionPercent(relReduction)
                .originalPrediction(origPred)
                .simulatedPrediction(simPred)
                .keyImprovements(keyImprovements)
                .disclaimer(disclaimer)
                .build();
    }

    public List<SimulationResponseDto> getHistoryByPatientId(Long patientId) {
        return simulationRepository.findByPatientIdOrderByCreatedAtDesc(patientId).stream()
                .map(this::mapEntityToDto)
                .collect(Collectors.toList());
    }

    private SimulationResponseDto mapEntityToDto(WhatIfSimulation s) {
        return SimulationResponseDto.builder()
                .id(s.getId())
                .patientId(s.getPatient() != null ? s.getPatient().getId() : null)
                .predictionId(s.getPrediction() != null ? s.getPrediction().getId() : null)
                .disease(s.getDisease())
                .originalRiskPercentage(s.getOriginalRisk())
                .simulatedRiskPercentage(s.getSimulatedRisk())
                .riskDifference(s.getRiskDifference())
                .createdAt(s.getCreatedAt())
                .build();
    }
}
