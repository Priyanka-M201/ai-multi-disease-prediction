package com.diseaseprediction.controller;

import com.diseaseprediction.dto.ApiResponse;
import com.diseaseprediction.dto.HealthRecordDto;
import com.diseaseprediction.service.HealthRecordService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/health-records")
@RequiredArgsConstructor
public class HealthRecordController {

    private final HealthRecordService healthRecordService;

    @GetMapping("/patient/{patientId}")
    public ResponseEntity<ApiResponse<List<HealthRecordDto>>> getRecordsByPatientId(@PathVariable Long patientId) {
        return ResponseEntity.ok(ApiResponse.ok(healthRecordService.getRecordsByPatientId(patientId)));
    }

    @PostMapping
    public ResponseEntity<ApiResponse<HealthRecordDto>> addRecord(@Valid @RequestBody HealthRecordDto dto) {
        return ResponseEntity.ok(ApiResponse.ok("Health record added successfully", healthRecordService.addRecord(dto)));
    }
}
