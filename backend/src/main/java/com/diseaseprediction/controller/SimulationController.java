package com.diseaseprediction.controller;

import com.diseaseprediction.dto.ApiResponse;
import com.diseaseprediction.dto.SimulationRequestDto;
import com.diseaseprediction.dto.SimulationResponseDto;
import com.diseaseprediction.service.WhatIfSimulationService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/simulations")
@RequiredArgsConstructor
public class SimulationController {

    private final WhatIfSimulationService simulationService;

    @PostMapping
    public ResponseEntity<ApiResponse<SimulationResponseDto>> simulate(@Valid @RequestBody SimulationRequestDto request) {
        SimulationResponseDto response = simulationService.simulateAndSave(request);
        return ResponseEntity.ok(ApiResponse.ok("Counterfactual simulation completed", response));
    }

    @PostMapping("/public")
    public ResponseEntity<ApiResponse<SimulationResponseDto>> simulatePublic(@Valid @RequestBody SimulationRequestDto request) {
        SimulationResponseDto response = simulationService.simulateAndSave(request);
        return ResponseEntity.ok(ApiResponse.ok("Public counterfactual simulation completed", response));
    }

    @GetMapping("/history/{patientId}")
    public ResponseEntity<ApiResponse<List<SimulationResponseDto>>> getHistory(@PathVariable Long patientId) {
        return ResponseEntity.ok(ApiResponse.ok(simulationService.getHistoryByPatientId(patientId)));
    }
}
