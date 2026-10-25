package com.diseaseprediction.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class MlServiceClient {

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    @Value("${app.ml-service.url:http://127.0.0.1:8000}")
    private String mlServiceUrl;

    public Map<String, Object> predict(String disease, Map<String, Object> inputs, String modelName) {
        String url = mlServiceUrl + "/predict/" + disease.toLowerCase();
        Map<String, Object> payload = new HashMap<>(inputs);
        if (modelName != null && !modelName.isBlank()) {
            payload.put("model_name", modelName);
        }

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(payload, headers);

        try {
            ResponseEntity<String> response = restTemplate.postForEntity(url, entity, String.class);
            return objectMapper.readValue(response.getBody(), new TypeReference<>() {});
        } catch (Exception ex) {
            log.error("Error calling ML service predict endpoint [{}]: {}", url, ex.getMessage());
            throw new RuntimeException("ML service prediction failed: " + ex.getMessage(), ex);
        }
    }

    public Map<String, Object> explain(String disease, Map<String, Object> inputs, String modelName) {
        String url = mlServiceUrl + "/explain/" + disease.toLowerCase();
        Map<String, Object> payload = new HashMap<>(inputs);
        if (modelName != null && !modelName.isBlank()) {
            payload.put("model_name", modelName);
        }

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(payload, headers);

        try {
            ResponseEntity<String> response = restTemplate.postForEntity(url, entity, String.class);
            return objectMapper.readValue(response.getBody(), new TypeReference<>() {});
        } catch (Exception ex) {
            log.warn("Error calling ML service explain endpoint [{}]: {}", url, ex.getMessage());
            return Map.of(
                    "disease", disease,
                    "model_name", modelName != null ? modelName : "Standard Model",
                    "base_risk_probability", 0.5,
                    "contributions", java.util.List.of(),
                    "summary_text", "Explanation details unavailable.",
                    "disclaimer", "Attribution calculation skipped."
            );
        }
    }

    public Map<String, Object> simulate(String disease, Map<String, Object> originalInputs, Map<String, Object> simulatedInputs, String modelName) {
        String url = mlServiceUrl + "/simulate";
        Map<String, Object> payload = new HashMap<>();
        payload.put("disease", disease.toLowerCase());
        payload.put("original_inputs", originalInputs);
        payload.put("simulated_inputs", simulatedInputs);
        if (modelName != null && !modelName.isBlank()) {
            payload.put("model_name", modelName);
        }

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(payload, headers);

        try {
            ResponseEntity<String> response = restTemplate.postForEntity(url, entity, String.class);
            return objectMapper.readValue(response.getBody(), new TypeReference<>() {});
        } catch (Exception ex) {
            log.error("Error calling ML service simulate endpoint: {}", ex.getMessage());
            throw new RuntimeException("ML service counterfactual simulation failed: " + ex.getMessage(), ex);
        }
    }

    public Map<String, Object> getModelMetrics() {
        String url = mlServiceUrl + "/models/metrics";
        try {
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            return objectMapper.readValue(response.getBody(), new TypeReference<>() {});
        } catch (Exception ex) {
            log.warn("Could not retrieve model metrics from ML service: {}", ex.getMessage());
            return Map.of("status", "unavailable", "message", ex.getMessage());
        }
    }
}
