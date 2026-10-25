package com.diseaseprediction.service;

import com.diseaseprediction.dto.PatientDto;
import com.diseaseprediction.exception.ResourceNotFoundException;
import com.diseaseprediction.model.Patient;
import com.diseaseprediction.model.User;
import com.diseaseprediction.repository.PatientRepository;
import com.diseaseprediction.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class PatientService {

    private final PatientRepository patientRepository;
    private final UserRepository userRepository;

    public List<PatientDto> getAllPatients() {
        return patientRepository.findAll().stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    public PatientDto getPatientById(Long id) {
        Patient patient = patientRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Patient not found with id: " + id));
        return mapToDto(patient);
    }

    public PatientDto getPatientByUserId(Long userId) {
        Patient patient = patientRepository.findFirstByUserId(userId)
                .orElseThrow(() -> new ResourceNotFoundException("No patient profile found for user id: " + userId));
        return mapToDto(patient);
    }

    @Transactional
    public PatientDto createPatient(PatientDto dto) {
        User user = userRepository.findById(dto.getUserId())
                .orElseThrow(() -> new ResourceNotFoundException("User not found with id: " + dto.getUserId()));

        Patient patient = Patient.builder()
                .user(user)
                .age(dto.getAge())
                .gender(dto.getGender())
                .phone(dto.getPhone())
                .bloodGroup(dto.getBloodGroup())
                .address(dto.getAddress())
                .build();

        return mapToDto(patientRepository.save(patient));
    }

    @Transactional
    public PatientDto updatePatient(Long id, PatientDto dto) {
        Patient patient = patientRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Patient not found with id: " + id));

        patient.setAge(dto.getAge());
        patient.setGender(dto.getGender());
        patient.setPhone(dto.getPhone());
        patient.setBloodGroup(dto.getBloodGroup());
        patient.setAddress(dto.getAddress());

        return mapToDto(patientRepository.save(patient));
    }

    public Patient getPatientEntity(Long id) {
        return patientRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Patient not found with id: " + id));
    }

    public PatientDto mapToDto(Patient patient) {
        return PatientDto.builder()
                .id(patient.getId())
                .userId(patient.getUser() != null ? patient.getUser().getId() : null)
                .userName(patient.getUser() != null ? patient.getUser().getName() : null)
                .age(patient.getAge())
                .gender(patient.getGender())
                .phone(patient.getPhone())
                .bloodGroup(patient.getBloodGroup())
                .address(patient.getAddress())
                .createdAt(patient.getCreatedAt())
                .build();
    }
}
