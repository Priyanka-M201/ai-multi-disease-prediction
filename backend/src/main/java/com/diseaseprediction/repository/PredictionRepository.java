package com.diseaseprediction.repository;

import com.diseaseprediction.model.Patient;
import com.diseaseprediction.model.Prediction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PredictionRepository extends JpaRepository<Prediction, Long> {
    List<Prediction> findByPatientOrderByCreatedAtDesc(Patient patient);
    List<Prediction> findByPatientIdOrderByCreatedAtDesc(Long patientId);
    List<Prediction> findByPatientIdAndDiseaseOrderByCreatedAtDesc(Long patientId, String disease);
}
