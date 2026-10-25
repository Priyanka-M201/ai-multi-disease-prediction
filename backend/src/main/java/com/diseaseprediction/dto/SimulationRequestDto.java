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
public class SimulationRequestDto {

    private Long patientId;
    private Long predictionId;

    @NotBlank(message = "Disease must be specified")
    private String disease;

    private String modelName;

    @NotNull(message = "Original inputs are required")
    private Map<String, Object> originalInputs;

    @NotNull(message = "Simulated inputs are required")
    private Map<String, Object> simulatedInputs;
}
