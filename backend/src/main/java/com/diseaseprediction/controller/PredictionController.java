package com.diseaseprediction.controller;

import com.diseaseprediction.dto.ApiResponse;
import com.diseaseprediction.dto.PredictionRequestDto;
import com.diseaseprediction.dto.PredictionResponseDto;
import com.diseaseprediction.service.PredictionService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/predictions")
@RequiredArgsConstructor
public class PredictionController {

    private final PredictionService predictionService;

    @PostMapping
    public ResponseEntity<ApiResponse<PredictionResponseDto>> predict(@Valid @RequestBody PredictionRequestDto request) {
        PredictionResponseDto response = predictionService.predictAndSave(request);
        return ResponseEntity.ok(ApiResponse.ok("Risk prediction completed", response));
    }

    @PostMapping("/public")
    public ResponseEntity<ApiResponse<PredictionResponseDto>> predictPublic(@Valid @RequestBody PredictionRequestDto request) {
        PredictionResponseDto response = predictionService.predictAndSave(request);
        return ResponseEntity.ok(ApiResponse.ok("Public risk prediction completed", response));
    }

    @GetMapping("/history/{patientId}")
    public ResponseEntity<ApiResponse<List<PredictionResponseDto>>> getHistory(@PathVariable Long patientId) {
        return ResponseEntity.ok(ApiResponse.ok(predictionService.getHistoryByPatientId(patientId)));
    }
}
