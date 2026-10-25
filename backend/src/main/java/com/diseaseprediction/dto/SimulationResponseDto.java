package com.diseaseprediction.dto;

import lombok.*;

import java.time.LocalDateTime;
import java.util.List;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SimulationResponseDto {

    private Long id;
    private Long patientId;
    private Long predictionId;
    private String disease;
    private String modelName;
    private Double originalRiskProbability;
    private Double originalRiskPercentage;
    private Double simulatedRiskProbability;
    private Double simulatedRiskPercentage;
    private Double riskDifference;
    private Double relativeReductionPercent;
    private String originalPrediction;
    private String simulatedPrediction;
    private List<String> keyImprovements;
    private String disclaimer;
    private LocalDateTime createdAt;
}
