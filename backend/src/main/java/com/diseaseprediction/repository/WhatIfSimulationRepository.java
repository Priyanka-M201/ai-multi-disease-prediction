package com.diseaseprediction.repository;

import com.diseaseprediction.model.Patient;
import com.diseaseprediction.model.WhatIfSimulation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface WhatIfSimulationRepository extends JpaRepository<WhatIfSimulation, Long> {
    List<WhatIfSimulation> findByPatientOrderByCreatedAtDesc(Patient patient);
    List<WhatIfSimulation> findByPatientIdOrderByCreatedAtDesc(Long patientId);
}
