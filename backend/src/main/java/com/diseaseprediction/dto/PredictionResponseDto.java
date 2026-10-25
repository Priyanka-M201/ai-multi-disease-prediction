package com.diseaseprediction.dto;

import lombok.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PredictionResponseDto {

    private Long id;
    private Long patientId;
    private String disease;
    private Double riskProbability;
    private Double riskPercentage;
    private String prediction;
    private String modelKey;
    private String modelName;
    private Boolean isBestModel;
    private Double confidenceScore;
    private Map<String, Object> featuresUsed;
    private List<FeatureContributionDto> contributions;
    private String summaryText;
    private String disclaimer;
    private LocalDateTime createdAt;
}
