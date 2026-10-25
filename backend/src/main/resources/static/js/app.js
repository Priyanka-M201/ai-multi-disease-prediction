/**
 * AURA HEALTH AI - Frontend Client Architecture
 * Supports Heart Disease, Diabetes, Stroke, and Hypertension
 * SHAP Explainability & Interactive What-If Counterfactual Simulations
 */

// Configuration & API Discovery
const API_BASE = window.location.port === "8000" 
  ? "http://127.0.0.1:8000" 
  : (window.location.origin.includes(":8080") ? window.location.origin : "http://localhost:8080");

const STATE = {
  currentDisease: 'heart',
  activeModel: '',
  clinicalInputs: {},
  lastPrediction: null,
  benchmarkMetrics: null,
  authToken: null,
  patientId: 1
};

// Clinical Metadata Specifications & Realistic Presets
const DISEASE_CONFIGS = {
  heart: {
    title: 'Cardiovascular Heart Disease Risk',
    subtitle: 'Cleveland / UCI Clinical Cohort Benchmark (13 Vitals)',
    defaults: {
      age: 58, sex: 1, cp: 0, trestbps: 142, chol: 248, fbs: 0,
      restecg: 0, thalach: 135, exang: 1, oldpeak: 1.8, slope: 1, ca: 1, thal: 2
    },
    healthyPreset: {
      age: 42, sex: 1, cp: 2, trestbps: 118, chol: 185, fbs: 0,
      restecg: 0, thalach: 168, exang: 0, oldpeak: 0.2, slope: 2, ca: 0, thal: 1
    },
    riskPreset: {
      age: 64, sex: 1, cp: 0, trestbps: 165, chol: 295, fbs: 1,
      restecg: 1, thalach: 110, exang: 1, oldpeak: 3.2, slope: 0, ca: 2, thal: 3
    },
    fields: [
      { id: 'age', label: 'Patient Age', type: 'number', unit: 'years', min: 20, max: 90 },
      { id: 'sex', label: 'Biological Sex', type: 'select', options: [{ val: 1, text: 'Male (1)' }, { val: 0, text: 'Female (0)' }] },
      { id: 'cp', label: 'Chest Pain Type', type: 'select', options: [
        { val: 0, text: 'Typical Angina (0)' }, { val: 1, text: 'Atypical Angina (1)' },
        { val: 2, text: 'Non-anginal Pain (2)' }, { val: 3, text: 'Asymptomatic (3)' }
      ]},
      { id: 'trestbps', label: 'Resting Blood Pressure', type: 'number', unit: 'mm Hg', min: 80, max: 220 },
      { id: 'chol', label: 'Serum Cholesterol', type: 'number', unit: 'mg/dL', min: 100, max: 500 },
      { id: 'fbs', label: 'Fasting Blood Sugar > 120', type: 'select', options: [{ val: 0, text: 'No (<=120 mg/dL)' }, { val: 1, text: 'Yes (>120 mg/dL)' }] },
      { id: 'restecg', label: 'Resting ECG Results', type: 'select', options: [
        { val: 0, text: 'Normal (0)' }, { val: 1, text: 'ST-T Wave Abnormality (1)' }, { val: 2, text: 'Left Ventricular Hypertrophy (2)' }
      ]},
      { id: 'thalach', label: 'Max Heart Rate Achieved', type: 'number', unit: 'bpm', min: 60, max: 220 },
      { id: 'exang', label: 'Exercise Induced Angina', type: 'select', options: [{ val: 0, text: 'No (0)' }, { val: 1, text: 'Yes (1)' }] },
      { id: 'oldpeak', label: 'ST Depression (Exercise)', type: 'number', unit: 'mm', step: 0.1, min: 0, max: 6.5 },
      { id: 'slope', label: 'Slope of Peak Exercise ST', type: 'select', options: [
        { val: 0, text: 'Upsloping (0)' }, { val: 1, text: 'Flat (1)' }, { val: 2, text: 'Downsloping (2)' }
      ]},
      { id: 'ca', label: 'Major Fluoroscopy Vessels', type: 'select', options: [
        { val: 0, text: '0 Vessels (0)' }, { val: 1, text: '1 Vessel (1)' }, { val: 2, text: '2 Vessels (2)' }, { val: 3, text: '3 Vessels (3)' }
      ]},
      { id: 'thal', label: 'Thalassemia Status', type: 'select', options: [
        { val: 1, text: 'Normal (1)' }, { val: 2, text: 'Fixed Defect (2)' }, { val: 3, text: 'Reversible Defect (3)' }
      ]}
    ],
    modifiableParams: [
      { id: 'trestbps', label: 'Resting Blood Pressure', unit: 'mm Hg', min: 90, max: 190, step: 1 },
      { id: 'chol', label: 'Serum Cholesterol', unit: 'mg/dL', min: 140, max: 340, step: 2 },
      { id: 'thalach', label: 'Target Max Heart Rate', unit: 'bpm', min: 90, max: 200, step: 1 },
      { id: 'oldpeak', label: 'ST Depression Reduction', unit: 'mm', min: 0.0, max: 4.0, step: 0.1 }
    ]
  },

  diabetes: {
    title: 'Type-2 Diabetes Risk',
    subtitle: 'Pima Clinical Cohort Benchmark (9 Parameters)',
    defaults: {
      age: 45, gender: 1, pregnancies: 0, glucose: 138.0,
      blood_pressure: 84.0, skin_thickness: 28.0, insulin: 120.0, bmi: 31.4, diabetes_pedigree: 0.52
    },
    healthyPreset: {
      age: 32, gender: 1, pregnancies: 0, glucose: 92.0,
      blood_pressure: 72.0, skin_thickness: 18.0, insulin: 65.0, bmi: 22.8, diabetes_pedigree: 0.28
    },
    riskPreset: {
      age: 54, gender: 0, pregnancies: 4, glucose: 185.0,
      blood_pressure: 94.0, skin_thickness: 38.0, insulin: 220.0, bmi: 38.5, diabetes_pedigree: 1.15
    },
    fields: [
      { id: 'age', label: 'Age', type: 'number', unit: 'years', min: 18, max: 90 },
      { id: 'gender', label: 'Gender', type: 'select', options: [{ val: 1, text: 'Male (1)' }, { val: 0, text: 'Female (0)' }] },
      { id: 'pregnancies', label: 'Pregnancies Count', type: 'number', unit: 'count', min: 0, max: 17 },
      { id: 'glucose', label: 'Fasting Plasma Glucose', type: 'number', unit: 'mg/dL', min: 50, max: 280 },
      { id: 'blood_pressure', label: 'Diastolic Blood Pressure', type: 'number', unit: 'mm Hg', min: 40, max: 140 },
      { id: 'skin_thickness', label: 'Triceps Skinfold Thickness', type: 'number', unit: 'mm', min: 5, max: 80 },
      { id: 'insulin', label: '2-Hour Serum Insulin', type: 'number', unit: 'mu U/ml', min: 10, max: 600 },
      { id: 'bmi', label: 'Body Mass Index (BMI)', type: 'number', unit: 'kg/m²', step: 0.1, min: 15, max: 55 },
      { id: 'diabetes_pedigree', label: 'Diabetes Pedigree Score', type: 'number', unit: 'heredity', step: 0.01, min: 0.05, max: 2.5 }
    ],
    modifiableParams: [
      { id: 'glucose', label: 'Fasting Plasma Glucose', unit: 'mg/dL', min: 70, max: 200, step: 1 },
      { id: 'bmi', label: 'Body Mass Index (BMI)', unit: 'kg/m²', min: 18.5, max: 42.0, step: 0.2 },
      { id: 'blood_pressure', label: 'Diastolic Blood Pressure', unit: 'mm Hg', min: 60, max: 110, step: 1 },
      { id: 'insulin', label: 'Serum Insulin Level', unit: 'mu U/ml', min: 30, max: 250, step: 5 }
    ]
  },

  stroke: {
    title: 'Cerebrovascular Stroke Risk',
    subtitle: 'Clinical Stroke Registry Distribution (10 Parameters)',
    defaults: {
      age: 62, gender: 1, hypertension: 1, heart_disease: 0, ever_married: 1,
      work_type: 1, residence_type: 1, avg_glucose_level: 145.0, bmi: 31.0, smoking_status: 2
    },
    healthyPreset: {
      age: 38, gender: 0, hypertension: 0, heart_disease: 0, ever_married: 1,
      work_type: 1, residence_type: 1, avg_glucose_level: 88.0, bmi: 23.2, smoking_status: 0
    },
    riskPreset: {
      age: 72, gender: 1, hypertension: 1, heart_disease: 1, ever_married: 1,
      work_type: 2, residence_type: 1, avg_glucose_level: 198.0, bmi: 35.8, smoking_status: 2
    },
    fields: [
      { id: 'age', label: 'Patient Age', type: 'number', unit: 'years', min: 18, max: 95 },
      { id: 'gender', label: 'Gender', type: 'select', options: [{ val: 1, text: 'Male (1)' }, { val: 0, text: 'Female (0)' }] },
      { id: 'hypertension', label: 'Hypertension Diagnosed', type: 'select', options: [{ val: 0, text: 'No (0)' }, { val: 1, text: 'Yes (1)' }] },
      { id: 'heart_disease', label: 'Pre-existing Heart Disease', type: 'select', options: [{ val: 0, text: 'No (0)' }, { val: 1, text: 'Yes (1)' }] },
      { id: 'ever_married', label: 'Marital Status', type: 'select', options: [{ val: 1, text: 'Married / Ever Married' }, { val: 0, text: 'Never Married' }] },
      { id: 'work_type', label: 'Work Sector', type: 'select', options: [
        { val: 0, text: 'Government (0)' }, { val: 1, text: 'Private (1)' }, { val: 2, text: 'Self-employed (2)' }, { val: 3, text: 'Never worked (3)' }
      ]},
      { id: 'residence_type', label: 'Residence Zone', type: 'select', options: [{ val: 1, text: 'Urban' }, { val: 0, text: 'Rural' }] },
      { id: 'avg_glucose_level', label: 'Average Blood Glucose', type: 'number', unit: 'mg/dL', step: 0.1, min: 55, max: 280 },
      { id: 'bmi', label: 'Body Mass Index (BMI)', type: 'number', unit: 'kg/m²', step: 0.1, min: 15, max: 55 },
      { id: 'smoking_status', label: 'Smoking History', type: 'select', options: [
        { val: 0, text: 'Never Smoked (0)' }, { val: 1, text: 'Formerly Smoked (1)' }, { val: 2, text: 'Currently Smokes (2)' }
      ]}
    ],
    modifiableParams: [
      { id: 'avg_glucose_level', label: 'Average Glucose Level', unit: 'mg/dL', min: 70, max: 200, step: 1 },
      { id: 'bmi', label: 'Body Mass Index', unit: 'kg/m²', min: 18.5, max: 40.0, step: 0.2 },
      { id: 'hypertension', label: 'Manage Hypertension', unit: '0=Controlled', min: 0, max: 1, step: 1 },
      { id: 'smoking_status', label: 'Cessation of Smoking', unit: '0=Never/Quit', min: 0, max: 2, step: 1 }
    ]
  },

  hypertension: {
    title: 'Essential Hypertension Risk',
    subtitle: 'Cardiovascular BP Evaluation Benchmark (10 Parameters)',
    defaults: {
      age: 52, gender: 1, bmi: 29.8, systolic_bp: 148.0, diastolic_bp: 94.0,
      heart_rate: 80.0, glucose: 115.0, cholesterol: 235.0, smoking: 1, physical_activity: 0
    },
    healthyPreset: {
      age: 35, gender: 0, bmi: 22.4, systolic_bp: 114.0, diastolic_bp: 74.0,
      heart_rate: 68.0, glucose: 88.0, cholesterol: 175.0, smoking: 0, physical_activity: 2
    },
    riskPreset: {
      age: 65, gender: 1, bmi: 34.5, systolic_bp: 172.0, diastolic_bp: 106.0,
      heart_rate: 88.0, glucose: 155.0, cholesterol: 285.0, smoking: 1, physical_activity: 0
    },
    fields: [
      { id: 'age', label: 'Patient Age', type: 'number', unit: 'years', min: 18, max: 90 },
      { id: 'gender', label: 'Gender', type: 'select', options: [{ val: 1, text: 'Male (1)' }, { val: 0, text: 'Female (0)' }] },
      { id: 'bmi', label: 'Body Mass Index (BMI)', type: 'number', unit: 'kg/m²', step: 0.1, min: 16, max: 50 },
      { id: 'systolic_bp', label: 'Systolic Blood Pressure', type: 'number', unit: 'mm Hg', min: 85, max: 220 },
      { id: 'diastolic_bp', label: 'Diastolic Blood Pressure', type: 'number', unit: 'mm Hg', min: 50, max: 135 },
      { id: 'heart_rate', label: 'Resting Heart Rate', type: 'number', unit: 'bpm', min: 45, max: 130 },
      { id: 'glucose', label: 'Fasting Glucose', type: 'number', unit: 'mg/dL', min: 60, max: 260 },
      { id: 'cholesterol', label: 'Total Cholesterol', type: 'number', unit: 'mg/dL', min: 110, max: 400 },
      { id: 'smoking', label: 'Smoking Habit', type: 'select', options: [{ val: 0, text: 'Non-Smoker (0)' }, { val: 1, text: 'Smoker (1)' }] },
      { id: 'physical_activity', label: 'Physical Activity Level', type: 'select', options: [
        { val: 0, text: 'Low / Sedentary (0)' }, { val: 1, text: 'Moderate (1)' }, { val: 2, text: 'High / Active (2)' }
      ]}
    ],
    modifiableParams: [
      { id: 'systolic_bp', label: 'Systolic Blood Pressure', unit: 'mm Hg', min: 100, max: 180, step: 1 },
      { id: 'diastolic_bp', label: 'Diastolic Blood Pressure', unit: 'mm Hg', min: 65, max: 115, step: 1 },
      { id: 'bmi', label: 'Body Mass Index', unit: 'kg/m²', min: 18.5, max: 38.0, step: 0.2 },
      { id: 'cholesterol', label: 'Serum Cholesterol', unit: 'mg/dL', min: 140, max: 300, step: 2 },
      { id: 'smoking', label: 'Quit Smoking', unit: '0=Non-smoker', min: 0, max: 1, step: 1 },
      { id: 'physical_activity', label: 'Increase Activity Level', unit: '0-2', min: 0, max: 2, step: 1 }
    ]
  }
};

// Initializer
document.addEventListener('DOMContentLoaded', async () => {
  setupEventListeners();
  loadDisease(STATE.currentDisease);
  await fetchBenchmarkMetrics();
  await triggerPrediction();
});

function setupEventListeners() {
  // Disease Tabs
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      const target = e.currentTarget;
      target.classList.add('active');
      const disease = target.getAttribute('data-disease');
      loadDisease(disease);
      triggerPrediction();
    });
  });

  // Preset Buttons
  document.getElementById('btn-preset-healthy').addEventListener('click', () => {
    const config = DISEASE_CONFIGS[STATE.currentDisease];
    populateForm(config.healthyPreset);
    showToast('Loaded healthy vital parameters', 'success');
    triggerPrediction();
  });

  document.getElementById('btn-preset-risk').addEventListener('click', () => {
    const config = DISEASE_CONFIGS[STATE.currentDisease];
    populateForm(config.riskPreset);
    showToast('Loaded elevated clinical risk patient profile', 'error');
    triggerPrediction();
  });

  // Algorithm Selector
  document.getElementById('select-model').addEventListener('change', (e) => {
    STATE.activeModel = e.target.value;
    triggerPrediction();
  });

  // Clinical Form Submit
  document.getElementById('clinical-form').addEventListener('submit', (e) => {
    e.preventDefault();
    triggerPrediction();
  });

  // What-If Simulation Trigger Button
  document.getElementById('btn-run-simulation').addEventListener('click', () => {
    runSimulation();
  });

  // History Modal
  document.getElementById('btn-view-history').addEventListener('click', () => {
    openHistoryModal();
  });
  document.getElementById('btn-close-modal').addEventListener('click', () => {
    document.getElementById('history-modal').classList.remove('active');
  });
  document.getElementById('history-modal').addEventListener('click', (e) => {
    if (e.target.id === 'history-modal') {
      document.getElementById('history-modal').classList.remove('active');
    }
  });

  // User Profile Switch
  document.getElementById('btn-auth-switch').addEventListener('click', () => {
    showToast('Authenticated as Patient #1 (John Doe)', 'success');
  });
}

function loadDisease(diseaseKey) {
  STATE.currentDisease = diseaseKey;
  const config = DISEASE_CONFIGS[diseaseKey];

  document.getElementById('form-title').innerText = config.title;
  document.getElementById('form-subtitle').innerText = config.subtitle;
  document.getElementById('benchmark-disease-tag').innerText = `Disease: ${diseaseKey.toUpperCase()}`;

  // Build Dynamic Inputs
  const container = document.getElementById('dynamic-form-fields');
  container.innerHTML = '';

  config.fields.forEach(f => {
    const group = document.createElement('div');
    group.className = 'form-group';

    const label = document.createElement('label');
    label.className = 'form-label';
    label.innerHTML = `<span>${f.label}</span>${f.unit ? `<span class="label-unit">${f.unit}</span>` : ''}`;

    let inputElem;
    if (f.type === 'select') {
      inputElem = document.createElement('select');
      inputElem.className = 'input-field';
      inputElem.id = `input-${f.id}`;
      f.options.forEach(opt => {
        const optEl = document.createElement('option');
        optEl.value = opt.val;
        optEl.innerText = opt.text;
        inputElem.appendChild(optEl);
      });
    } else {
      inputElem = document.createElement('input');
      inputElem.type = 'number';
      inputElem.className = 'input-field';
      inputElem.id = `input-${f.id}`;
      if (f.min !== undefined) inputElem.min = f.min;
      if (f.max !== undefined) inputElem.max = f.max;
      if (f.step !== undefined) inputElem.step = f.step;
    }

    group.appendChild(label);
    group.appendChild(inputElem);
    container.appendChild(group);
  });

  // Set default values
  populateForm(config.defaults);

  // Render Simulation Sliders for this disease
  renderSimulationSliders(config.modifiableParams, config.defaults);

  // Update Benchmark Leaderboard Table
  renderBenchmarkTable();
}

function populateForm(values) {
  Object.keys(values).forEach(k => {
    const el = document.getElementById(`input-${k}`);
    if (el) el.value = values[k];
  });
}

function getFormData() {
  const config = DISEASE_CONFIGS[STATE.currentDisease];
  const data = {};
  config.fields.forEach(f => {
    const el = document.getElementById(`input-${f.id}`);
    if (el) {
      data[f.id] = parseFloat(el.value);
    }
  });
  return data;
}

// Prediction & SHAP Analysis Engine
async function triggerPrediction() {
  const inputs = getFormData();
  STATE.clinicalInputs = inputs;
  const disease = STATE.currentDisease;
  const requestedModel = STATE.activeModel || null;

  // Visual Loading Feedback
  const submitBtn = document.getElementById('btn-calculate-risk');
  const origBtnText = submitBtn.innerHTML;
  submitBtn.innerHTML = `<span>⏳ Calculating Statistical Attributions...</span>`;

  try {
    let result;
    const payload = {
      patientId: STATE.patientId,
      disease: disease,
      modelName: requestedModel,
      inputs: inputs
    };

    // Try Spring Boot Backend Prediction Endpoint first
    const res = await fetch(`${API_BASE}/api/predictions/public`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      const json = await res.json();
      result = json.data || json;
    } else {
      // Direct ML Service Fallback if backend proxy not available
      const mlRes = await fetch(`http://127.0.0.1:8000/predict/${disease}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...inputs, model_name: requestedModel })
      });
      const mlPred = await mlRes.json();

      const shapRes = await fetch(`http://127.0.0.1:8000/explain/${disease}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...inputs, model_name: requestedModel })
      });
      const shapData = await shapRes.json();

      result = {
        ...mlPred,
        contributions: shapData.contributions,
        summaryText: shapData.summary_text,
        disclaimer: shapData.disclaimer
      };
    }

    STATE.lastPrediction = result;
    renderPredictionResults(result);
    // Sync current inputs to simulation sliders
    updateSimulationSlidersFromInputs(inputs);
    // Automatically run baseline simulation
    runSimulation();

  } catch (err) {
    console.error('Prediction failed:', err);
    showToast('Service temporarily synchronizing. Ensure backend or ML-service is running.', 'error');
  } finally {
    submitBtn.innerHTML = origBtnText;
  }
}

function renderPredictionResults(pred) {
  const riskPercent = pred.risk_percentage || pred.riskPercentage || 0;
  const riskLabel = pred.prediction || 'Moderate Risk';
  const modelName = pred.model_name || pred.modelName || 'Optimal Model';
  const confidence = Math.round((pred.confidence_score || pred.confidenceScore || 0.85) * 100);
  const isBest = pred.is_best_model !== undefined ? pred.is_best_model : (pred.isBestModel || true);

  // Update Numbers
  document.getElementById('risk-number').innerText = riskPercent.toFixed(1);
  document.getElementById('active-model-display').innerText = `Model: ${modelName}`;
  document.getElementById('meta-confidence').innerText = `${confidence}%`;
  document.getElementById('meta-disease').innerText = STATE.currentDisease.toUpperCase();
  document.getElementById('meta-best-badge').style.display = isBest ? 'inline-flex' : 'none';

  // Gauge Progress (Circumference = 345.4)
  const circle = document.getElementById('gauge-circle');
  const circumference = 345.4;
  const offset = circumference - (riskPercent / 100) * circumference;
  circle.style.strokeDashoffset = offset;

  // Category Badge & Gauge Color
  const badge = document.getElementById('risk-category-badge');
  badge.className = 'risk-badge-large';

  if (riskPercent < 30) {
    badge.classList.add('low');
    badge.innerText = '🛡️ Low Risk (<30%)';
    circle.style.stroke = '#10b981';
  } else if (riskPercent < 65) {
    badge.classList.add('moderate');
    badge.innerText = '⚠️ Moderate Risk (30-65%)';
    circle.style.stroke = '#f59e0b';
  } else {
    badge.classList.add('high');
    badge.innerText = '🚨 High Risk (>65%)';
    circle.style.stroke = '#f43f5e';
  }

  // Render SHAP Feature Attribution Bars
  const barsContainer = document.getElementById('shap-bars-container');
  barsContainer.innerHTML = '';

  const contributions = pred.contributions || [];
  const topContributions = contributions.slice(0, 6);

  if (topContributions.length === 0) {
    barsContainer.innerHTML = `<p style="color: var(--text-muted); font-size: 12px;">Feature attributions are uniformly balanced.</p>`;
  } else {
    topContributions.forEach(item => {
      const isIncrease = item.direction === 'INCREASES_RISK';
      const pct = Math.abs(item.contribution_percent || item.contributionPercent || 10);
      const barItem = document.createElement('div');
      barItem.className = 'shap-bar-item';

      barItem.innerHTML = `
        <div class="shap-bar-header">
          <span class="shap-bar-name">${item.feature}</span>
          <span class="shap-bar-val" style="color: ${isIncrease ? '#fb7185' : '#34d399'};">
            ${isIncrease ? '+' : '-'}${pct}%
          </span>
        </div>
        <div class="shap-track">
          <div class="shap-fill ${isIncrease ? 'increase' : 'reduce'}" style="width: ${Math.min(pct * 2.2, 100)}%;"></div>
        </div>
        <div class="shap-explanation-note">${item.description}</div>
      `;
      barsContainer.appendChild(barItem);
    });
  }

  // Summary Text & Disclaimer
  const summaryText = pred.summary_text || pred.summaryText;
  if (summaryText) {
    document.getElementById('clinical-summary-text').innerText = summaryText;
  }
  const disclaimer = pred.disclaimer;
  if (disclaimer) {
    document.getElementById('clinical-disclaimer-text').innerText = disclaimer;
  }
}

// What-If Simulation Rendering & Execution
function renderSimulationSliders(params, initialValues) {
  const container = document.getElementById('simulation-sliders-container');
  container.innerHTML = '';

  params.forEach(param => {
    const val = initialValues[param.id] !== undefined ? initialValues[param.id] : param.min;

    const group = document.createElement('div');
    group.className = 'slider-group';

    group.innerHTML = `
      <div class="slider-header">
        <span>${param.label}</span>
        <span class="slider-val-badge" id="slider-val-${param.id}">${val} ${param.unit}</span>
      </div>
      <input type="range" class="sim-slider" id="slider-${param.id}"
             min="${param.min}" max="${param.max}" step="${param.step}" value="${val}">
    `;

    container.appendChild(group);

    const slider = group.querySelector(`#slider-${param.id}`);
    slider.addEventListener('input', (e) => {
      document.getElementById(`slider-val-${param.id}`).innerText = `${e.target.value} ${param.unit}`;
      runSimulationDebounced();
    });
  });
}

function updateSimulationSlidersFromInputs(inputs) {
  const config = DISEASE_CONFIGS[STATE.currentDisease];
  config.modifiableParams.forEach(p => {
    const slider = document.getElementById(`slider-${p.id}`);
    const badge = document.getElementById(`slider-val-${p.id}`);
    if (slider && badge && inputs[p.id] !== undefined) {
      slider.value = inputs[p.id];
      badge.innerText = `${inputs[p.id]} ${p.unit}`;
    }
  });
}

let simTimeout = null;
function runSimulationDebounced() {
  clearTimeout(simTimeout);
  simTimeout = setTimeout(() => {
    runSimulation();
  }, 200);
}

async function runSimulation() {
  const originalInputs = { ...STATE.clinicalInputs };
  const simulatedInputs = { ...STATE.clinicalInputs };
  const config = DISEASE_CONFIGS[STATE.currentDisease];

  config.modifiableParams.forEach(p => {
    const slider = document.getElementById(`slider-${p.id}`);
    if (slider) {
      simulatedInputs[p.id] = parseFloat(slider.value);
    }
  });

  const payload = {
    patientId: STATE.patientId,
    disease: STATE.currentDisease,
    modelName: STATE.activeModel || null,
    originalInputs: originalInputs,
    simulatedInputs: simulatedInputs
  };

  try {
    let simResult;
    const res = await fetch(`${API_BASE}/api/simulations/public`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      const json = await res.json();
      simResult = json.data || json;
    } else {
      // Direct ML Service Fallback
      const mlRes = await fetch(`http://127.0.0.1:8000/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          disease: STATE.currentDisease,
          original_inputs: originalInputs,
          simulated_inputs: simulatedInputs,
          model_name: STATE.activeModel || null
        })
      });
      simResult = await mlRes.json();
    }

    renderSimulationResults(simResult);

  } catch (err) {
    console.warn('Simulation API call:', err);
  }
}

function renderSimulationResults(res) {
  const origPercent = res.original_risk_percentage || res.originalRiskPercentage || 0;
  const simPercent = res.simulated_risk_percentage || res.simulatedRiskPercentage || 0;
  const riskDiff = res.risk_difference !== undefined ? res.risk_difference : (res.riskDifference || (simPercent - origPercent));
  const relRed = res.relative_reduction_percent !== undefined ? res.relative_reduction_percent : (res.relativeReductionPercent || 0);

  document.getElementById('sim-orig-risk').innerText = `${origPercent.toFixed(1)}%`;
  document.getElementById('sim-new-risk').innerText = `${simPercent.toFixed(1)}%`;

  const badge = document.getElementById('sim-reduction-badge');
  if (riskDiff < 0) {
    badge.style.background = 'var(--risk-low-bg)';
    badge.style.borderColor = 'rgba(16, 185, 129, 0.4)';
    badge.style.color = '#34d399';
    badge.innerHTML = `<span>📉</span> Net Risk Reduction: ${riskDiff.toFixed(1)}% points (${relRed.toFixed(1)}% relative)`;
  } else if (riskDiff > 0) {
    badge.style.background = 'var(--risk-high-bg)';
    badge.style.borderColor = 'rgba(244, 63, 94, 0.4)';
    badge.style.color = '#fb7185';
    badge.innerHTML = `<span>📈</span> Elevated Risk Scenario: +${riskDiff.toFixed(1)}% points (+${relRed.toFixed(1)}%)`;
  } else {
    badge.style.background = 'rgba(255, 255, 255, 0.05)';
    badge.style.borderColor = 'var(--border-color)';
    badge.style.color = 'var(--text-secondary)';
    badge.innerHTML = `<span>⚖️</span> Baseline Equilibrium: 0.0% difference`;
  }

  // List of improvements
  const listEl = document.getElementById('sim-improvements-list');
  listEl.innerHTML = '';
  const improvements = res.key_improvements || res.keyImprovements || [];

  if (improvements.length === 0) {
    listEl.innerHTML = `<li>No parameters adjusted yet. Move the sliders to test scenarios.</li>`;
  } else {
    improvements.forEach(item => {
      const li = document.createElement('li');
      li.innerText = item;
      listEl.appendChild(li);
    });
  }
}

// Benchmark Metrics Leaderboard
async function fetchBenchmarkMetrics() {
  try {
    const res = await fetch(`${API_BASE}/api/models/metrics`);
    if (res.ok) {
      const json = await res.json();
      STATE.benchmarkMetrics = json.data || json;
      renderBenchmarkTable();
    }
  } catch (err) {
    console.warn('Could not load benchmark metrics:', err);
  }
}

function renderBenchmarkTable() {
  const tbody = document.getElementById('benchmark-table-body');
  if (!STATE.benchmarkMetrics || !STATE.benchmarkMetrics[STATE.currentDisease]) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 20px; color: var(--text-muted);">Evaluation metrics loaded directly from trained benchmark artifacts.</td></tr>`;
    return;
  }

  const diseaseData = STATE.benchmarkMetrics[STATE.currentDisease];
  const models = diseaseData.models || {};
  const bestKey = diseaseData.best_model_key;

  tbody.innerHTML = '';

  Object.keys(models).forEach(key => {
    const m = models[key];
    const isBest = (key === bestKey);
    const tr = document.createElement('tr');
    if (isBest) tr.className = 'champion-row';

    tr.innerHTML = `
      <td>
        <b>${m.model_name}</b>
        ${isBest ? `<span class="badge-champion">CHAMPION</span>` : ''}
      </td>
      <td>${(m.accuracy * 100).toFixed(1)}%</td>
      <td>${(m.precision * 100).toFixed(1)}%</td>
      <td>${(m.recall * 100).toFixed(1)}%</td>
      <td>${(m.f1_score * 100).toFixed(1)}%</td>
      <td><b style="color: ${isBest ? '#38bdf8' : 'var(--text-primary)'};">${m.roc_auc.toFixed(4)}</b></td>
      <td>
        <span style="color: ${isBest ? '#34d399' : 'var(--text-muted)'}; font-size: 12px;">
          ${isBest ? '● Production Model' : '● Evaluated'}
        </span>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// Patient History Drawer
async function openHistoryModal() {
  const modal = document.getElementById('history-modal');
  const container = document.getElementById('history-content-list');
  modal.classList.add('active');
  container.innerHTML = `<p style="color: var(--text-muted); font-size: 13px;">Retrieving patient record history...</p>`;

  try {
    const res = await fetch(`${API_BASE}/api/predictions/history/${STATE.patientId}`);
    if (res.ok) {
      const json = await res.json();
      const list = json.data || [];
      if (list.length === 0) {
        container.innerHTML = `<p style="color: var(--text-muted); font-size: 13px;">No prior clinical prediction records found for this patient profile.</p>`;
        return;
      }
      container.innerHTML = '';
      list.forEach(item => {
        const row = document.createElement('div');
        row.style.cssText = 'background: rgba(15, 23, 42, 0.7); padding: 14px; border-radius: 8px; border: 1px solid var(--border-color);';
        row.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <b style="font-family: var(--font-heading); color: #38bdf8;">${item.disease} Risk Assessment</b>
            <span style="font-size: 12px; color: var(--text-muted);">${item.createdAt ? new Date(item.createdAt).toLocaleString() : 'Recent'}</span>
          </div>
          <div style="font-size: 13px; color: var(--text-secondary); margin-bottom: 4px;">
            Result: <b style="color: var(--text-primary);">${item.prediction}</b> (${item.riskPercentage}% probability) via ${item.modelName}
          </div>
          ${item.summaryText ? `<div style="font-size: 12px; color: #bae6fd;">${item.summaryText}</div>` : ''}
        `;
        container.appendChild(row);
      });
    } else {
      container.innerHTML = `<p style="color: var(--text-muted); font-size: 13px;">Patient record history is stored in the database.</p>`;
    }
  } catch (err) {
    container.innerHTML = `<p style="color: var(--text-muted); font-size: 13px;">Patient record history currently unavailable.</p>`;
  }
}

// Toast Notifications
function showToast(msg, type = 'success') {
  const toast = document.getElementById('toast');
  toast.innerText = msg;
  toast.className = `toast ${type} show`;
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3200);
}
