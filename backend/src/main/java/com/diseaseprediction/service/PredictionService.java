package com.diseaseprediction.service;

import com.diseaseprediction.dto.FeatureContributionDto;
import com.diseaseprediction.dto.PredictionRequestDto;
import com.diseaseprediction.dto.PredictionResponseDto;
import com.diseaseprediction.model.Patient;
import com.diseaseprediction.model.Prediction;
import com.diseaseprediction.repository.PatientRepository;
import com.diseaseprediction.repository.PredictionRepository;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class PredictionService {

    private final MlServiceClient mlServiceClient;
    private final PredictionRepository predictionRepository;
    private final PatientRepository patientRepository;
    private final ObjectMapper objectMapper;

    @Transactional
    public PredictionResponseDto predictAndSave(PredictionRequestDto request) {
        String disease = request.getDisease().toLowerCase().trim();

        // 1. ML Prediction
        Map<String, Object> predResult = mlServiceClient.predict(disease, request.getInputs(), request.getModelName());

        // 2. SHAP Explanation
        Map<String, Object> expResult = mlServiceClient.explain(disease, request.getInputs(), request.getModelName());

        Double riskProb = ((Number) predResult.get("risk_probability")).doubleValue();
        Double riskPercent = ((Number) predResult.get("risk_percentage")).doubleValue();
        String label = (String) predResult.get("prediction");
        String modelKey = (String) predResult.get("model_key");
        String modelName = (String) predResult.get("model_name");
        Boolean isBestModel = (Boolean) predResult.get("is_best_model");
        Double confidence = ((Number) predResult.get("confidence_score")).doubleValue();

        // Parse contributions
        List<FeatureContributionDto> contributions = new ArrayList<>();
        if (expResult.containsKey("contributions") && expResult.get("contributions") instanceof List<?> list) {
            for (Object item : list) {
                if (item instanceof Map<?, ?> m) {
                    contributions.add(FeatureContributionDto.builder()
                            .feature((String) m.get("feature"))
                            .rawFeatureName((String) m.get("raw_feature_name"))
                            .value(m.get("value"))
                            .shapValue(m.get("shap_value") != null ? ((Number) m.get("shap_value")).doubleValue() : 0.0)
                            .contributionPercent(m.get("contribution_percent") != null ? ((Number) m.get("contribution_percent")).doubleValue() : 0.0)
                            .direction((String) m.get("direction"))
                            .description((String) m.get("description"))
                            .build());
                }
            }
        }

        String summaryText = (String) expResult.getOrDefault("summary_text", "");
        String disclaimer = (String) expResult.getOrDefault("disclaimer", "");

        Long savedPredictionId = null;
        Patient patient = null;

        if (request.getPatientId() != null) {
            patient = patientRepository.findById(request.getPatientId()).orElse(null);
        }

        if (patient != null) {
            try {
                String inputJson = objectMapper.writeValueAsString(request.getInputs());
                String expJson = objectMapper.writeValueAsString(expResult);

                Prediction entity = Prediction.builder()
                        .patient(patient)
                        .disease(disease.toUpperCase())
                        .riskPercentage(riskPercent)
                        .riskProbability(riskProb)
                        .predictionResult(label)
                        .modelName(modelName)
                        .shapSummaryJson(expJson)
                        .inputFeaturesJson(inputJson)
                        .build();

                Prediction saved = predictionRepository.save(entity);
                savedPredictionId = saved.getId();
            } catch (Exception ex) {
                log.error("Failed to save prediction record: {}", ex.getMessage());
            }
        }

        return PredictionResponseDto.builder()
                .id(savedPredictionId)
                .patientId(patient != null ? patient.getId() : null)
                .disease(disease)
                .riskProbability(riskProb)
                .riskPercentage(riskPercent)
                .prediction(label)
                .modelKey(modelKey)
                .modelName(modelName)
                .isBestModel(isBestModel)
                .confidenceScore(confidence)
                .featuresUsed(request.getInputs())
                .contributions(contributions)
                .summaryText(summaryText)
                .disclaimer(disclaimer)
                .build();
    }

    public List<PredictionResponseDto> getHistoryByPatientId(Long patientId) {
        return predictionRepository.findByPatientIdOrderByCreatedAtDesc(patientId).stream()
                .map(this::mapEntityToDto)
                .collect(Collectors.toList());
    }

    private PredictionResponseDto mapEntityToDto(Prediction p) {
        Map<String, Object> features = null;
        List<FeatureContributionDto> contributions = new ArrayList<>();
        String summary = null;
        String disclaimer = null;

        try {
            if (p.getInputFeaturesJson() != null) {
                features = objectMapper.readValue(p.getInputFeaturesJson(), new TypeReference<>() {});
            }
            if (p.getShapSummaryJson() != null) {
                Map<String, Object> exp = objectMapper.readValue(p.getShapSummaryJson(), new TypeReference<>() {});
                summary = (String) exp.get("summary_text");
                disclaimer = (String) exp.get("disclaimer");
                if (exp.containsKey("contributions") && exp.get("contributions") instanceof List<?> list) {
                    for (Object item : list) {
                        if (item instanceof Map<?, ?> m) {
                            contributions.add(FeatureContributionDto.builder()
                                    .feature((String) m.get("feature"))
                                    .rawFeatureName((String) m.get("raw_feature_name"))
                                    .value(m.get("value"))
                                    .shapValue(m.get("shap_value") != null ? ((Number) m.get("shap_value")).doubleValue() : 0.0)
                                    .contributionPercent(m.get("contribution_percent") != null ? ((Number) m.get("contribution_percent")).doubleValue() : 0.0)
                                    .direction((String) m.get("direction"))
                                    .description((String) m.get("description"))
                                    .build());
                        }
                    }
                }
            }
        } catch (Exception ex) {
            log.warn("Error parsing saved JSON for prediction {}: {}", p.getId(), ex.getMessage());
        }

        return PredictionResponseDto.builder()
                .id(p.getId())
                .patientId(p.getPatient() != null ? p.getPatient().getId() : null)
                .disease(p.getDisease())
                .riskProbability(p.getRiskProbability())
                .riskPercentage(p.getRiskPercentage())
                .prediction(p.getPredictionResult())
                .modelName(p.getModelName())
                .featuresUsed(features)
                .contributions(contributions)
                .summaryText(summary)
                .disclaimer(disclaimer)
                .createdAt(p.getCreatedAt())
                .build();
    }
}
