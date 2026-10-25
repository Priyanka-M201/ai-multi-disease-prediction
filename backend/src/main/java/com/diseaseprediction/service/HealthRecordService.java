package com.diseaseprediction.service;

import com.diseaseprediction.dto.HealthRecordDto;
import com.diseaseprediction.exception.ResourceNotFoundException;
import com.diseaseprediction.model.HealthRecord;
import com.diseaseprediction.model.Patient;
import com.diseaseprediction.repository.HealthRecordRepository;
import com.diseaseprediction.repository.PatientRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class HealthRecordService {

    private final HealthRecordRepository healthRecordRepository;
    private final PatientRepository patientRepository;

    public List<HealthRecordDto> getRecordsByPatientId(Long patientId) {
        return healthRecordRepository.findByPatientIdOrderByRecordedAtDesc(patientId).stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    @Transactional
    public HealthRecordDto addRecord(HealthRecordDto dto) {
        Patient patient = patientRepository.findById(dto.getPatientId())
                .orElseThrow(() -> new ResourceNotFoundException("Patient not found with id: " + dto.getPatientId()));

        HealthRecord record = HealthRecord.builder()
                .patient(patient)
                .age(dto.getAge() != null ? dto.getAge() : patient.getAge())
                .gender(dto.getGender() != null ? dto.getGender() : patient.getGender())
                .systolicBp(dto.getSystolicBp())
                .diastolicBp(dto.getDiastolicBp())
                .bmi(dto.getBmi())
                .glucose(dto.getGlucose())
                .cholesterol(dto.getCholesterol())
                .heartRate(dto.getHeartRate())
                .smokingStatus(dto.getSmokingStatus())
                .additionalFeaturesJson(dto.getAdditionalFeaturesJson())
                .build();

        return mapToDto(healthRecordRepository.save(record));
    }

    private HealthRecordDto mapToDto(HealthRecord record) {
        return HealthRecordDto.builder()
                .id(record.getId())
                .patientId(record.getPatient().getId())
                .age(record.getAge())
                .gender(record.getGender())
                .systolicBp(record.getSystolicBp())
                .diastolicBp(record.getDiastolicBp())
                .bmi(record.getBmi())
                .glucose(record.getGlucose())
                .cholesterol(record.getCholesterol())
                .heartRate(record.getHeartRate())
                .smokingStatus(record.getSmokingStatus())
                .additionalFeaturesJson(record.getAdditionalFeaturesJson())
                .recordedAt(record.getRecordedAt())
                .build();
    }
}
