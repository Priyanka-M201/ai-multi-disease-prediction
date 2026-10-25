package com.diseaseprediction.repository;

import com.diseaseprediction.model.Patient;
import com.diseaseprediction.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface PatientRepository extends JpaRepository<Patient, Long> {
    List<Patient> findByUser(User user);
    Optional<Patient> findFirstByUserId(Long userId);
}
