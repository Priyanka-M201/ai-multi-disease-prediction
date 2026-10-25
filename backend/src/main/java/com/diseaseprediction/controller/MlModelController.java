package com.diseaseprediction.controller;

import com.diseaseprediction.dto.ApiResponse;
import com.diseaseprediction.service.MlServiceClient;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/models")
@RequiredArgsConstructor
public class MlModelController {

    private final MlServiceClient mlServiceClient;

    @GetMapping("/metrics")
    public ResponseEntity<ApiResponse<Map<String, Object>>> getModelMetrics() {
        return ResponseEntity.ok(ApiResponse.ok("Model benchmark evaluation metrics", mlServiceClient.getModelMetrics()));
    }

    @GetMapping("/supported")
    public ResponseEntity<ApiResponse<Object>> getSupportedDiseasesAndAlgorithms() {
        Map<String, Object> data = Map.of(
                "diseases", List.of("diabetes", "heart", "stroke"),
                "algorithms", List.of(
                        Map.of("key", "ann", "name", "Artificial Neural Network (ANN)", "description", "Feed-Forward Neural Network (2 hidden layers: 64, 32)"),
                        Map.of("key", "dnn", "name", "Deep Neural Network (DNN)", "description", "Deep Feed-Forward Network (4 hidden layers: 128, 64, 32, 16)")
                )
        );
        return ResponseEntity.ok(ApiResponse.ok(data));
    }
}
