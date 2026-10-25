-- AI-Based Multi-Disease Risk Prediction System
-- Database Schema (MySQL Compatible)

CREATE DATABASE IF NOT EXISTS disease_prediction_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE disease_prediction_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(30) NOT NULL DEFAULT 'ROLE_PATIENT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. Patients Table
CREATE TABLE IF NOT EXISTS patients (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(20) NOT NULL,
    phone VARCHAR(30),
    blood_group VARCHAR(10),
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_patients_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Health Records Table
CREATE TABLE IF NOT EXISTS health_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    patient_id BIGINT NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(20) NOT NULL,
    systolic_bp DOUBLE,
    diastolic_bp DOUBLE,
    bmi DOUBLE,
    glucose DOUBLE,
    cholesterol DOUBLE,
    heart_rate DOUBLE,
    smoking_status VARCHAR(30),
    additional_features_json TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_health_records_patient FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- 4. Prediction Records Table
CREATE TABLE IF NOT EXISTS predictions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    patient_id BIGINT NOT NULL,
    disease VARCHAR(60) NOT NULL,
    risk_percentage DOUBLE NOT NULL,
    risk_probability DOUBLE NOT NULL,
    prediction_result VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    shap_summary_json LONGTEXT,
    input_features_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_predictions_patient FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- 5. What-If Simulation History Table
CREATE TABLE IF NOT EXISTS what_if_simulations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    patient_id BIGINT NOT NULL,
    prediction_id BIGINT,
    disease VARCHAR(60) NOT NULL,
    original_risk DOUBLE NOT NULL,
    simulated_risk DOUBLE NOT NULL,
    risk_difference DOUBLE NOT NULL,
    modified_features_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_simulations_patient FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    CONSTRAINT fk_simulations_prediction FOREIGN KEY (prediction_id) REFERENCES predictions(id) ON DELETE SET NULL
);

-- Indexes for optimal querying
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_patients_user ON patients(user_id);
CREATE INDEX idx_predictions_patient ON predictions(patient_id);
CREATE INDEX idx_predictions_disease ON predictions(disease);
CREATE INDEX idx_simulations_patient ON what_if_simulations(patient_id);
