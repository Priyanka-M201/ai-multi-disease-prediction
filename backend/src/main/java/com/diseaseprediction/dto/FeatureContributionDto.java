package com.diseaseprediction.dto;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class FeatureContributionDto {
    private String feature;
    private String rawFeatureName;
    private Object value;
    private Double shapValue;
    private Double contributionPercent;
    private String direction;
    private String description;
}
