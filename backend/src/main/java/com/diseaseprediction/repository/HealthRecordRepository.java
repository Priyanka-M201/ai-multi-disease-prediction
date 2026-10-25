package com.diseaseprediction.repository;

import com.diseaseprediction.model.HealthRecord;
import com.diseaseprediction.model.Patient;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface HealthRecordRepository extends JpaRepository<HealthRecord, Long> {
    List<HealthRecord> findByPatientOrderByRecordedAtDesc(Patient patient);
    List<HealthRecord> findByPatientIdOrderByRecordedAtDesc(Long patientId);
}
