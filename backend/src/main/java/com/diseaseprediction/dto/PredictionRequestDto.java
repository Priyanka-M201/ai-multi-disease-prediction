package com.diseaseprediction.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.*;

import java.util.Map;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PredictionRequestDto {

    private Long patientId;

    @NotBlank(message = "Disease must be specified (diabetes, heart, stroke)")
    private String disease;

    private String modelName;

    @NotNull(message = "Clinical inputs map is required")
    private Map<String, Object> inputs;
}
