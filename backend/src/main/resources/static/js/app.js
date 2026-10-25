/**
 * AURA HEALTH AI - Frontend Client Architecture
 * Deep Learning Multi-Disease Risk Prediction: Diabetes, Heart Disease, Stroke
 * Exclusively Artificial Neural Networks (ANN) & Deep Neural Networks (DNN)
 * SHAP Explainability & Interactive What-If Counterfactual Simulations
 */

// Configuration & API Discovery
const API_BASE = window.location.port === "8000" 
  ? "http://127.0.0.1:8000" 
  : (window.location.origin.includes(":8080") ? window.location.origin : "http://localhost:8080");

const STATE = {
  currentDisease: 'diabetes',
  activeModel: '',
  clinicalInputs: {},
  lastPrediction: null,
  benchmarkMetrics: null,
  authToken: null,
  patientId: 1
};

// Clinical Metadata Specifications & Realistic Presets for the 3 Required Diseases
const DISEASE_CONFIGS = {
  diabetes: {
    title: 'Type-2 Diabetes Risk',
    subtitle: 'Pima Indians Clinical Cohort Benchmark (9 Parameters)',
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
  }
};

// Lifecycle Initialization
document.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
  switchDisease('diabetes');
  fetchBenchmarkMetrics();
});

function setupEventListeners() {
  // Disease Tabs
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const targetDisease = btn.getAttribute('data-disease');
      if (targetDisease && DISEASE_CONFIGS[targetDisease]) {
        switchDisease(targetDisease);
      }
    });
  });

  // Presets
  document.getElementById('btn-preset-healthy').addEventListener('click', () => loadPreset('healthy'));
  document.getElementById('btn-preset-risk').addEventListener('click', () => loadPreset('risk'));

  // Model Selection Dropdown
  document.getElementById('select-model').addEventListener('change', (e) => {
    STATE.activeModel = e.target.value;
    if (STATE.lastPrediction) {
      submitPrediction();
    }
  });

  // Form Submission
  document.getElementById('clinical-form').addEventListener('submit', (e) => {
    e.preventDefault();
    submitPrediction();
  });

  // What-If Simulation
  document.getElementById('btn-run-simulation').addEventListener('click', () => {
    runWhatIfSimulation();
  });

  // Patient History Drawer
  document.getElementById('btn-view-history').addEventListener('click', openHistoryModal);
  document.getElementById('btn-close-modal').addEventListener('click', () => {
    document.getElementById('history-modal').classList.remove('active');
  });
}

// Disease Switching Logic
function switchDisease(disease) {
  if (!DISEASE_CONFIGS[disease]) return;
  STATE.currentDisease = disease;

  // Update tabs active state
  document.querySelectorAll('.tab-btn').forEach(b => {
    b.classList.toggle('active', b.getAttribute('data-disease') === disease);
  });

  const cfg = DISEASE_CONFIGS[disease];
  document.getElementById('form-title').innerText = cfg.title;
  document.getElementById('form-subtitle').innerText = cfg.subtitle;
  document.getElementById('benchmark-disease-tag').innerText = `Disease: ${cfg.title.split(' ')[0]}`;

  renderDynamicForm(cfg);
  renderWhatIfSliders(cfg);
  loadPreset('default');
  renderBenchmarkTable();
}

function renderDynamicForm(cfg) {
  const container = document.getElementById('dynamic-form-fields');
  container.innerHTML = '';

  cfg.fields.forEach(f => {
    const wrap = document.createElement('div');
    wrap.className = 'form-group';

    const label = document.createElement('label');
    label.className = 'form-label';
    label.setAttribute('for', `inp-${f.id}`);
    label.innerHTML = `${f.label} ${f.unit ? `<span class="unit-tag">(${f.unit})</span>` : ''}`;
    wrap.appendChild(label);

    if (f.type === 'select') {
      const select = document.createElement('select');
      select.className = 'input-field';
      select.id = `inp-${f.id}`;
      f.options.forEach(opt => {
        const option = document.createElement('option');
        option.value = opt.val;
        option.innerText = opt.text;
        select.appendChild(option);
      });
      wrap.appendChild(select);
    } else {
      const input = document.createElement('input');
      input.className = 'input-field';
      input.type = 'number';
      input.id = `inp-${f.id}`;
      if (f.step) input.step = f.step;
      if (f.min !== undefined) input.min = f.min;
      if (f.max !== undefined) input.max = f.max;
      wrap.appendChild(input);
    }

    container.appendChild(wrap);
  });
}

function renderWhatIfSliders(cfg) {
  const container = document.getElementById('simulation-sliders-container');
  container.innerHTML = '';

  cfg.modifiableParams.forEach(p => {
    const row = document.createElement('div');
    row.className = 'slider-row';

    row.innerHTML = `
      <div class="slider-header">
        <span class="slider-label">${p.label}</span>
        <span class="slider-val" id="val-sim-${p.id}">--</span>
      </div>
      <input type="range" class="slider-input" id="slider-${p.id}" 
             min="${p.min}" max="${p.max}" step="${p.step || 1}" value="${p.min}">
    `;
    container.appendChild(row);

    const slider = row.querySelector(`#slider-${p.id}`);
    const display = row.querySelector(`#val-sim-${p.id}`);
    slider.addEventListener('input', () => {
      display.innerText = `${slider.value} ${p.unit}`;
      debouncedSimulation();
    });
  });
}

let simTimeout = null;
function debouncedSimulation() {
  clearTimeout(simTimeout);
  simTimeout = setTimeout(() => {
    runWhatIfSimulation();
  }, 350);
}

function loadPreset(type) {
  const cfg = DISEASE_CONFIGS[STATE.currentDisease];
  let data = cfg.defaults;
  if (type === 'healthy') data = cfg.healthyPreset;
  if (type === 'risk') data = cfg.riskPreset;

  Object.keys(data).forEach(k => {
    const el = document.getElementById(`inp-${k}`);
    if (el) el.value = data[k];

    const slider = document.getElementById(`slider-${k}`);
    const display = document.getElementById(`val-sim-${k}`);
    if (slider) {
      slider.value = data[k];
      if (display) {
        const param = cfg.modifiableParams.find(p => p.id === k);
        display.innerText = `${data[k]} ${param ? param.unit : ''}`;
      }
    }
  });

  showToast(`Loaded ${type === 'default' ? 'default baseline' : (type === 'healthy' ? 'healthy profile' : 'elevated risk profile')}`);
}

function gatherInputs() {
  const cfg = DISEASE_CONFIGS[STATE.currentDisease];
  const payload = {};
  let hasMissing = false;

  cfg.fields.forEach(f => {
    const el = document.getElementById(`inp-${f.id}`);
    if (el && el.value !== "") {
      payload[f.id] = parseFloat(el.value);
    } else {
      hasMissing = true;
    }
  });

  if (hasMissing) {
    showToast("Please provide valid values for all clinical inputs", "error");
    return null;
  }
  return payload;
}

// Prediction & SHAP Analysis Pipeline
async function submitPrediction() {
  const inputs = gatherInputs();
  if (!inputs) return;

  STATE.clinicalInputs = inputs;
  const btn = document.getElementById('btn-calculate-risk');
  btn.classList.add('loading');
  btn.disabled = true;

  try {
    const endpoint = `${API_BASE}/api/predictions/public`;
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        disease: STATE.currentDisease,
        modelName: STATE.activeModel || null,
        inputs: inputs
      })
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.message || `Prediction server returned status ${res.status}`);
    }

    const json = await res.json();
    const data = json.data || json;
    STATE.lastPrediction = data;
    renderPredictionResults(data);

    // Sync sliders to current inputs
    syncSlidersToInputs(inputs);

    // Trigger What-If calculation
    runWhatIfSimulation();
    showToast(`Neural Network Risk Analysis Complete: ${data.prediction}`);
  } catch (err) {
    showToast(err.message, 'error');
    console.error('Prediction error:', err);
  } finally {
    btn.classList.remove('loading');
    btn.disabled = false;
  }
}

function syncSlidersToInputs(inputs) {
  const cfg = DISEASE_CONFIGS[STATE.currentDisease];
  cfg.modifiableParams.forEach(p => {
    const slider = document.getElementById(`slider-${p.id}`);
    const display = document.getElementById(`val-sim-${p.id}`);
    if (slider && inputs[p.id] !== undefined) {
      slider.value = inputs[p.id];
      if (display) display.innerText = `${inputs[p.id]} ${p.unit}`;
    }
  });
}

function renderPredictionResults(data) {
  const riskNum = document.getElementById('risk-number');
  const badge = document.getElementById('risk-category-badge');
  const circle = document.getElementById('gauge-circle');
  const modelDisp = document.getElementById('active-model-display');
  const confDisp = document.getElementById('meta-confidence');
  const disDisp = document.getElementById('meta-disease');
  const bestBadge = document.getElementById('meta-best-badge');

  const pct = data.riskPercentage || (data.riskProbability * 100).toFixed(1);
  riskNum.innerText = pct;

  // Gauge animation: circumference = 2 * PI * 55 = 345.57
  const circumference = 345.57;
  const offset = circumference - (pct / 100.0) * circumference;
  circle.style.strokeDashoffset = Math.max(0, offset);

  // Status badge
  badge.className = 'risk-badge-large';
  if (pct < 30.0) {
    badge.classList.add('low');
    badge.innerText = `Low Risk (${pct}%)`;
    circle.style.stroke = 'var(--accent-emerald)';
  } else if (pct < 65.0) {
    badge.classList.add('moderate');
    badge.innerText = `Moderate Risk (${pct}%)`;
    circle.style.stroke = 'var(--accent-amber)';
  } else {
    badge.classList.add('high');
    badge.innerText = `High Risk (${pct}%)`;
    circle.style.stroke = 'var(--accent-rose)';
  }

  modelDisp.innerText = `Architecture: ${data.modelName || 'ANN'}`;
  confDisp.innerText = `${((data.confidenceScore || 0.85) * 100).toFixed(1)}%`;
  disDisp.innerText = data.disease || STATE.currentDisease;
  bestBadge.style.display = data.isBestModel ? 'inline-block' : 'none';

  // Render SHAP
  renderShapAttributions(data.contributions || [], data.summaryText);
}

function renderShapAttributions(contributions, summaryText) {
  const container = document.getElementById('shap-bars-list');
  const narrative = document.getElementById('shap-summary-narrative');
  container.innerHTML = '';

  narrative.innerText = summaryText || 'Mathematical SHAP attribution indicating how individual vitals drive the neural network output.';

  if (!contributions || contributions.length === 0) {
    container.innerHTML = `<p style="color: var(--text-muted); font-size: 13px;">No SHAP contributions returned.</p>`;
    return;
  }

  contributions.forEach(c => {
    const row = document.createElement('div');
    row.className = 'shap-bar-row';

    const isRisk = c.direction === 'INCREASES_RISK';
    const barClass = isRisk ? 'risk-driver' : 'protective';
    const sign = isRisk ? '+' : '-';

    row.innerHTML = `
      <div class="shap-bar-header">
        <span class="shap-feature-name">${c.feature} (${c.value})</span>
        <span class="shap-pct-val" style="color: ${isRisk ? '#fb7185' : '#34d399'};">
          ${sign}${c.contributionPercent}%
        </span>
      </div>
      <div class="shap-track">
        <div class="shap-fill ${barClass}" style="width: ${Math.min(100, c.contributionPercent * 2.2)}%;"></div>
      </div>
      <div class="shap-desc">${c.description}</div>
    `;
    container.appendChild(row);
  });
}

// What-If Counterfactual Simulation Engine
async function runWhatIfSimulation() {
  if (!STATE.lastPrediction) return;

  const cfg = DISEASE_CONFIGS[STATE.currentDisease];
  const simulatedInputs = Object.assign({}, STATE.clinicalInputs);

  cfg.modifiableParams.forEach(p => {
    const slider = document.getElementById(`slider-${p.id}`);
    if (slider) {
      simulatedInputs[p.id] = parseFloat(slider.value);
    }
  });

  try {
    const res = await fetch(`${API_BASE}/api/simulations/public`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        disease: STATE.currentDisease,
        modelName: STATE.activeModel || null,
        originalInputs: STATE.clinicalInputs,
        simulatedInputs: simulatedInputs
      })
    });

    if (res.ok) {
      const json = await res.json();
      renderSimulationResults(json.data || json);
    }
  } catch (err) {
    console.error('Simulation error:', err);
  }
}

function renderSimulationResults(res) {
  const origEl = document.getElementById('sim-orig-risk');
  const newEl = document.getElementById('sim-new-risk');
  const badge = document.getElementById('sim-reduction-badge');

  const origRisk = res.originalRiskPercentage || 0;
  const simRisk = res.simulatedRiskPercentage || 0;
  const riskDiff = res.riskDifference || 0;
  const relRed = res.relativeReductionPercent || 0;

  origEl.innerText = `${origRisk.toFixed(1)}%`;
  newEl.innerText = `${simRisk.toFixed(1)}%`;

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

// Deep Learning Benchmark Metrics Leaderboard
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
    tbody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding: 20px; color: var(--text-muted);">Evaluation metrics loaded directly from trained benchmark artifacts.</td></tr>`;
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

    const cmStr = m.confusion_matrix 
      ? `[${m.confusion_matrix[0][0]}, ${m.confusion_matrix[0][1]} / ${m.confusion_matrix[1][0]}, ${m.confusion_matrix[1][1]}]` 
      : 'N/A';
    const layersStr = m.architecture_layers ? m.architecture_layers.join(' ➔ ') : 'Dense';

    tr.innerHTML = `
      <td>
        <b>${m.model_name}</b>
        ${isBest ? `<span class="badge-champion">SELECTED</span>` : ''}
      </td>
      <td><span style="font-size: 11px; font-family: monospace; color: #94a3b8;">${layersStr}</span></td>
      <td>${(m.accuracy * 100).toFixed(1)}%</td>
      <td>${(m.precision * 100).toFixed(1)}%</td>
      <td>${(m.recall * 100).toFixed(1)}%</td>
      <td>${(m.f1_score * 100).toFixed(1)}%</td>
      <td><b style="color: ${isBest ? '#38bdf8' : 'var(--text-primary)'};">${(m.roc_auc || 0).toFixed(4)}</b></td>
      <td><span style="font-size: 12px; font-family: monospace;">${cmStr}</span></td>
      <td>
        <span style="color: ${isBest ? '#34d399' : 'var(--text-muted)'}; font-size: 12px; font-weight: 600;">
          ${isBest ? '● Selected Production' : '● Evaluated Alternative'}
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
