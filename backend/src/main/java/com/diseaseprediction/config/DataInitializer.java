package com.diseaseprediction.config;

import com.diseaseprediction.model.*;
import com.diseaseprediction.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class DataInitializer implements CommandLineRunner {

    private final UserRepository userRepository;
    private final PatientRepository patientRepository;
    private final HealthRecordRepository healthRecordRepository;
    private final PredictionRepository predictionRepository;
    private final PasswordEncoder passwordEncoder;

    @Override
    public void run(String... args) {
        if (userRepository.count() == 0) {
            log.info("Seeding initial demo data for AI Disease Prediction system...");

            // 1. Doctor account
            User doctor = User.builder()
                    .name("Dr. Sarah Jenkins, MD")
                    .email("doctor@hospital.org")
                    .password(passwordEncoder.encode("doctor123"))
                    .role(Role.ROLE_DOCTOR)
                    .build();
            userRepository.save(doctor);

            // 2. Patient account
            User patientUser = User.builder()
                    .name("John Doe")
                    .email("patient@example.com")
                    .password(passwordEncoder.encode("patient123"))
                    .role(Role.ROLE_PATIENT)
                    .build();
            userRepository.save(patientUser);

            // 3. Patient profile
            Patient patient = Patient.builder()
                    .user(patientUser)
                    .age(58)
                    .gender("Male")
                    .phone("+1 (555) 234-5678")
                    .bloodGroup("B+")
                    .address("742 Evergreen Terrace, Springfield")
                    .build();
            patientRepository.save(patient);

            // 4. Baseline Health Record
            HealthRecord record = HealthRecord.builder()
                    .patient(patient)
                    .age(58)
                    .gender("Male")
                    .systolicBp(142.0)
                    .diastolicBp(92.0)
                    .bmi(29.4)
                    .glucose(135.0)
                    .cholesterol(245.0)
                    .heartRate(78.0)
                    .smokingStatus("Smoker")
                    .build();
            healthRecordRepository.save(record);

            // 5. Initial Sample Prediction Record
            Prediction prediction = Prediction.builder()
                    .patient(patient)
                    .disease("HEART")
                    .riskPercentage(62.5)
                    .riskProbability(0.625)
                    .predictionResult("Moderate Risk")
                    .modelName("CatBoost Classifier")
                    .inputFeaturesJson("{\"age\":58,\"trestbps\":142,\"chol\":245}")
                    .shapSummaryJson("{\"summary_text\":\"Primary risk drivers: Resting Blood Pressure, Serum Cholesterol.\"}")
                    .build();
            predictionRepository.save(prediction);

            log.info("Demo users seeded successfully: doctor@hospital.org / doctor123 and patient@example.com / patient123");
        }
    }
}
