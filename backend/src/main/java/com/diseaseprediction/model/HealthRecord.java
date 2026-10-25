package com.diseaseprediction.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "health_records")
public class HealthRecord {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "patient_id", nullable = false)
    private Patient patient;

    @Column(nullable = false)
    private Integer age;

    @Column(nullable = false, length = 20)
    private String gender;

    @Column(name = "systolic_bp")
    private Double systolicBp;

    @Column(name = "diastolic_bp")
    private Double diastolicBp;

    private Double bmi;
    private Double glucose;
    private Double cholesterol;

    @Column(name = "heart_rate")
    private Double heartRate;

    @Column(name = "smoking_status", length = 30)
    private String smokingStatus;

    @Lob
    @Column(name = "additional_features_json", columnDefinition = "TEXT")
    private String additionalFeaturesJson;

    @Column(name = "recorded_at", updatable = false)
    private LocalDateTime recordedAt;

    public HealthRecord() {}

    public HealthRecord(Long id, Patient patient, Integer age, String gender, Double systolicBp, Double diastolicBp,
                        Double bmi, Double glucose, Double cholesterol, Double heartRate, String smokingStatus,
                        String additionalFeaturesJson) {
        this.id = id;
        this.patient = patient;
        this.age = age;
        this.gender = gender;
        this.systolicBp = systolicBp;
        this.diastolicBp = diastolicBp;
        this.bmi = bmi;
        this.glucose = glucose;
        this.cholesterol = cholesterol;
        this.heartRate = heartRate;
        this.smokingStatus = smokingStatus;
        this.additionalFeaturesJson = additionalFeaturesJson;
    }

    public static HealthRecordBuilder builder() {
        return new HealthRecordBuilder();
    }

    public static class HealthRecordBuilder {
        private Long id;
        private Patient patient;
        private Integer age;
        private String gender;
        private Double systolicBp;
        private Double diastolicBp;
        private Double bmi;
        private Double glucose;
        private Double cholesterol;
        private Double heartRate;
        private String smokingStatus;
        private String additionalFeaturesJson;

        public HealthRecordBuilder id(Long id) { this.id = id; return this; }
        public HealthRecordBuilder patient(Patient patient) { this.patient = patient; return this; }
        public HealthRecordBuilder age(Integer age) { this.age = age; return this; }
        public HealthRecordBuilder gender(String gender) { this.gender = gender; return this; }
        public HealthRecordBuilder systolicBp(Double systolicBp) { this.systolicBp = systolicBp; return this; }
        public HealthRecordBuilder diastolicBp(Double diastolicBp) { this.diastolicBp = diastolicBp; return this; }
        public HealthRecordBuilder bmi(Double bmi) { this.bmi = bmi; return this; }
        public HealthRecordBuilder glucose(Double glucose) { this.glucose = glucose; return this; }
        public HealthRecordBuilder cholesterol(Double cholesterol) { this.cholesterol = cholesterol; return this; }
        public HealthRecordBuilder heartRate(Double heartRate) { this.heartRate = heartRate; return this; }
        public HealthRecordBuilder smokingStatus(String smokingStatus) { this.smokingStatus = smokingStatus; return this; }
        public HealthRecordBuilder additionalFeaturesJson(String additionalFeaturesJson) { this.additionalFeaturesJson = additionalFeaturesJson; return this; }

        public HealthRecord build() {
            return new HealthRecord(id, patient, age, gender, systolicBp, diastolicBp, bmi, glucose, cholesterol, heartRate, smokingStatus, additionalFeaturesJson);
        }
    }

    @PrePersist
    protected void onCreate() {
        this.recordedAt = LocalDateTime.now();
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Patient getPatient() { return patient; }
    public void setPatient(Patient patient) { this.patient = patient; }

    public Integer getAge() { return age; }
    public void setAge(Integer age) { this.age = age; }

    public String getGender() { return gender; }
    public void setGender(String gender) { this.gender = gender; }

    public Double getSystolicBp() { return systolicBp; }
    public void setSystolicBp(Double systolicBp) { this.systolicBp = systolicBp; }

    public Double getDiastolicBp() { return diastolicBp; }
    public void setDiastolicBp(Double diastolicBp) { this.diastolicBp = diastolicBp; }

    public Double getBmi() { return bmi; }
    public void setBmi(Double bmi) { this.bmi = bmi; }

    public Double getGlucose() { return glucose; }
    public void setGlucose(Double glucose) { this.glucose = glucose; }

    public Double getCholesterol() { return cholesterol; }
    public void setCholesterol(Double cholesterol) { this.cholesterol = cholesterol; }

    public Double getHeartRate() { return heartRate; }
    public void setHeartRate(Double heartRate) { this.heartRate = heartRate; }

    public String getSmokingStatus() { return smokingStatus; }
    public void setSmokingStatus(String smokingStatus) { this.smokingStatus = smokingStatus; }

    public String getAdditionalFeaturesJson() { return additionalFeaturesJson; }
    public void setAdditionalFeaturesJson(String additionalFeaturesJson) { this.additionalFeaturesJson = additionalFeaturesJson; }

    public LocalDateTime getRecordedAt() { return recordedAt; }
    public void setRecordedAt(LocalDateTime recordedAt) { this.recordedAt = recordedAt; }
}
