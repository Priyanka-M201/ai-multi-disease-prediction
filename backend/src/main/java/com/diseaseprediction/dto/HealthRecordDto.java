package com.diseaseprediction.dto;

import jakarta.validation.constraints.NotNull;
import lombok.*;

import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class HealthRecordDto {

    private Long id;

    @NotNull(message = "Patient ID is required")
    private Long patientId;

    private Integer age;
    private String gender;
    private Double systolicBp;
    private Double diastolicBp;
    private Double bmi;
    private Double glucose;
    private Double cholesterol;
    private Double heartRate;
    private String smokingStatus;
    private String additionalFeaturesJson;
    private LocalDateTime recordedAt;
}
