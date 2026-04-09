import os
import streamlit as st
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic

# Import new feature modules
from features.voice_input import VoiceInput, SymptomExtractor
from features.doctor_finder import DoctorFinder, SpecialtyMatcher
from database.patient_history import PatientHistoryDB

# Main app content (only shown if logged in)
def main_app():
    # Custom CSS for strong healthcare theme
    st.markdown("""
<style>
    /* Overall theme */
    .main {
        background-color: #f0f8ff;
        color: #2c3e50;
    }
    
    /* Header styling */
    .stTitle {
        color: #1e3a8a;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        text-align: center;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #e3f2fd;
        border-radius: 8px;
        padding: 10px 20px;
        color: #1565c0;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1976d2;
        color: white;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #1976d2;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1565c0;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Success, info, warning messages */
    .stSuccess {
        background-color: #e8f5e8;
        border-left: 5px solid #4caf50;
        padding: 10px;
        border-radius: 5px;
    }
    .stInfo {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
        padding: 10px;
        border-radius: 5px;
    }
    .stWarning {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
        padding: 10px;
        border-radius: 5px;
    }
    .stError {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
        padding: 10px;
        border-radius: 5px;
    }
    
    /* Input fields */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>select {
        border-radius: 8px;
        border: 2px solid #e3f2fd;
        padding: 8px;
    }
    .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus, .stSelectbox>div>div>select:focus {
        border-color: #1976d2;
        box-shadow: 0 0 5px rgba(25, 118, 210, 0.3);
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: #ffffff;
        border-right: 3px solid #1976d2;
    /* Overall theme */
    .main {
        background-color: #f0f8ff;
        color: #2c3e50;
    }
    
    /* Header styling */
    .stTitle {
        color: #1e3a8a;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        text-align: center;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #e3f2fd;
        border-radius: 8px;
        padding: 10px 20px;
        color: #1565c0;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1976d2;
        color: white;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #1976d2;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1565c0;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Success, info, warning messages */
    .stSuccess {
        background-color: #e8f5e8;
        border-left: 5px solid #4caf50;
        padding: 10px;
        border-radius: 5px;
    }
    .stInfo {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
        padding: 10px;
        border-radius: 5px;
    }
    .stWarning {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
        padding: 10px;
        border-radius: 5px;
    }
    .stError {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
        padding: 10px;
        border-radius: 5px;
    }
    
    /* Input fields */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>select {
        border-radius: 8px;
        border: 2px solid #e3f2fd;
        padding: 8px;
    }
    .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus, .stSelectbox>div>div>select:focus {
        border-color: #1976d2;
        box-shadow: 0 0 5px rgba(25, 118, 210, 0.3);
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: #ffffff;
        border-right: 3px solid #1976d2;
    }
    
    /* Cards for sections */
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #1976d2;
    }
    
    /* Animation for loading */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    .loading {
        animation: pulse 1.5s infinite;
    }
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="🏥 Early Diagnosis Predictor",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/hospital.png", width=80)
    st.title("🏥Early Diagnosis Predictor ")
    st.markdown("---")
    st.markdown("**Navigation:**")
    st.markdown("- 💊 Single Prediction (ML)")
    st.markdown("- 📊 Batch Prediction")
    st.markdown("- 🎤 Voice Input")
    st.markdown("- 📋 Health History")
    st.markdown("- 📈 Model Insights")
    st.markdown("- 🗺️ Find Doctors")
    st.markdown("- 💉 Medicine Guide")
    st.markdown("---")
    st.markdown("**About:**")
    st.markdown("AI-powered healthcare diagnosis for early disease detection. Get predictions, medicine suggestions, and locate nearby doctors.")
    st.markdown("**⚠️ Disclaimer:** For educational use only. Consult professionals for real medical advice.")

import json

BASE_DIR = os.path.dirname(__file__)

# Load the trained model
@st.cache_resource
def load_model():
    model_path = os.path.join(BASE_DIR, 'model', 'final_pipeline.joblib')
    try:
        return joblib.load(model_path)
    except FileNotFoundError:
        st.warning(f"Model file not found at {model_path}. Prediction features will be disabled.")
        return None
    except Exception as e:
        st.error(f"Failed to load model: {e}")
        return None

# Load training metadata (feature order, raw columns, etc.)
@st.cache_resource
def load_training_info():
    info_path = os.path.join(BASE_DIR, 'model', 'training_artifacts_info.json')
    try:
        with open(info_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.warning(f"Training info file not found at {info_path}. Using fallback feature configuration.")
        return {}
    except Exception:
        return {}

TRAIN_INFO = load_training_info()
# Feature columns will be set after pipeline is loaded
FEATURE_COLUMNS = []
RAW_FEATURE_COLUMNS = TRAIN_INFO.get('numeric_cols', []) + TRAIN_INFO.get('categorical_cols', [])

# Medicine advice mapping based on diagnosis
medicine_mapping = {
    "Common Cold": "Rest, hydration, paracetamol",
    "Viral Fever": "Paracetamol, fluids, rest",
    "Pneumonia": "Antibiotics, steam inhalation",
    "Flu": "Rest, warm fluids, vitamin C",
    "Food Poisoning": "ORS, antibiotics, avoid oily food",
    "Dengue (Mild)": "Hydration, paracetamol, rest",
    "Bronchitis": "Antibiotics, inhaler, warm fluids",
    "Fatigue": "Rest, iron-rich food",
    "Throat Infection": "Salt water gargle, rest"
}

# Sample doctors and hospitals data (with coordinates)
doctors_data = [
    {"name": "Dr. Raj Kumar", "type": "General Practitioner", "lat": 28.7041, "lon": 77.1025, "phone": "+91-9876543210", "address": "123 Hospital Street, Delhi"},
    {"name": "Dr. Priya Singh", "type": "Pediatrician", "lat": 28.5244, "lon": 77.1855, "phone": "+91-9876543211", "address": "456 Medical Road, Noida"},
    {"name": "City Hospital", "type": "Hospital", "lat": 28.6139, "lon": 77.2090, "phone": "+91-9876543212", "address": "789 Health Ave, Greater Noida"},
    {"name": "Dr. Amit Patel", "type": "Cardiologist", "lat": 28.4595, "lon": 77.0266, "phone": "+91-9876543213", "address": "101 Heart Care Lane, Gurgaon"},
    {"name": "Community Health Center", "type": "Health Center", "lat": 28.5355, "lon": 77.3910, "phone": "+91-9876543214", "address": "202 Village Road, Ghaziabad"},
    {"name": "Dr. Neha Gupta", "type": "Gynecologist", "lat": 28.7589, "lon": 77.0266, "phone": "+91-9876543215", "address": "303 Women's Health Clinic, Gurgaon"},
]

st.title("🏥 Early Diagnosis Predictor")
st.markdown('<div class="card"><p style="text-align: center; font-size: 18px; color: #666;">🌟 <strong>Empowering Rural Healthcare with AI</strong> 🌟</p></div>', unsafe_allow_html=True)
st.markdown("**⚠️ Disclaimer:** This is a demo app for educational purposes. Consult a healthcare professional for real medical advice.")

# Load the pipeline
pipeline = load_model()
MODEL_AVAILABLE = pipeline is not None

if not MODEL_AVAILABLE:
    st.warning("⚠️ The trained model is not available. Prediction and model insight features are disabled.")

# Set feature columns from the actual trained pipeline
FEATURE_COLUMNS = pipeline.get('feature_columns', TRAIN_INFO.get('feature_columns', [])) if MODEL_AVAILABLE else TRAIN_INFO.get('feature_columns', [])

# Initialize patient history database
db = PatientHistoryDB()

# Initialize voice input module
voice = VoiceInput()

# Tabs with creative icons
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "💊 Single Prediction",
    "📊 Batch Prediction",
    "🎤 Voice Input",
    "📋 Health History",
    "📈 Model Insights",
    "🗺️ Find Doctors",
    "💉 Medicine Guide"
])

# ===== TAB 1: Single Prediction =====
with tab1:
    st.header("💊 Patient Diagnosis & Medicine Predictor")
    st.markdown('<div class="card">Enter patient details to get diagnosis, medicines, dosage, precautions and care plan.</div>', unsafe_allow_html=True)

    # detailed medicine database
    medicine_detail_db = {
        "Common Cold":      {"medicine": "Paracetamol, Cetirizine, Nasal drops",  "dosage": "Paracetamol 500mg every 6-8 hrs",  "duration": "3-7 days",  "precaution": "Stay hydrated, avoid cold air, rest",          "severity": "Low",    "specialist": "General Practitioner"},
        "Viral Fever":      {"medicine": "Paracetamol, Vitamin C, ORS",           "dosage": "Paracetamol 500mg every 6 hrs",    "duration": "5-7 days",  "precaution": "Complete bed rest, warm fluids",               "severity": "Medium", "specialist": "General Practitioner"},
        "Pneumonia":        {"medicine": "Antibiotics (Amoxicillin), Steam",       "dosage": "As prescribed by doctor",          "duration": "10-14 days","precaution": "Complete antibiotic course, chest physio",     "severity": "High",   "specialist": "Pulmonologist"},
        "Flu":              {"medicine": "Oseltamivir, Paracetamol, Vitamin C",    "dosage": "Oseltamivir 75mg twice daily",     "duration": "7-10 days", "precaution": "Isolation, vaccination recommended",           "severity": "Medium", "specialist": "General Practitioner"},
        "Food Poisoning":   {"medicine": "ORS, Metronidazole, Bland diet",         "dosage": "ORS every 30-60 mins",             "duration": "2-4 days",  "precaution": "Hydration essential, avoid oily food",         "severity": "Medium", "specialist": "Gastroenterologist"},
        "Dengue (Mild)":    {"medicine": "Paracetamol, ORS, Rest",                 "dosage": "Paracetamol 500mg every 6 hrs",    "duration": "5-7 days",  "precaution": "Avoid NSAIDs, maintain platelet count",        "severity": "High",   "specialist": "Infectious Disease"},
        "Bronchitis":       {"medicine": "Amoxicillin, Salbutamol inhaler, Steam", "dosage": "Amoxicillin 500mg 3x daily",       "duration": "7-14 days", "precaution": "Avoid smoke, use humidifier",                  "severity": "Medium", "specialist": "Pulmonologist"},
        "Fatigue":          {"medicine": "Iron supplements, Vitamin B12, Rest",    "dosage": "Iron 65mg daily with Vitamin C",   "duration": "2-4 weeks", "precaution": "Adequate sleep, balanced diet",                "severity": "Low",    "specialist": "General Practitioner"},
        "Throat Infection": {"medicine": "Amoxicillin, Throat lozenges, Gargle",   "dosage": "Amoxicillin 250mg 3x daily",       "duration": "5-7 days",  "precaution": "Avoid spicy food, warm liquids",               "severity": "Low",    "specialist": "ENT Specialist"},
    }

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("👤 Patient Information")
        p_name      = st.text_input("Patient Name", value="", placeholder="Optional")
        age         = st.number_input("Age", min_value=0, max_value=120, value=30)
        gender      = st.selectbox("Gender", ["Male", "Female"])
        temperature = st.number_input("🌡️ Temperature (°C)", min_value=30.0, max_value=45.0, value=36.5, step=0.1)
        heart_rate  = st.number_input("❤️ Heart Rate (bpm)", min_value=40, max_value=200, value=70)

    with col2:
        st.subheader("📋 Medical Details")
        blood_pressure = st.selectbox("🩸 Blood Pressure", ["Normal", "High", "Low"])
        symptoms       = st.selectbox("🤒 Primary Symptom", ["Cough", "Fever", "Fatigue", "Headache", "Nausea", "Other"])
        weight         = st.number_input("⚖️ Weight (kg)", min_value=1, max_value=200, value=60)
        allergies      = st.text_input("⚠️ Known Allergies", placeholder="e.g. Penicillin, Aspirin")
    if not MODEL_AVAILABLE:
        st.warning("Single prediction is disabled because the model file is unavailable.")
    elif st.button("🔍 Predict Diagnosis & Medicine", key="predict_btn"):
        with st.spinner("🔄 Analyzing patient data..."):
            try:
                numeric_cols_t = TRAIN_INFO.get('numeric_cols', ['Age', 'Temperature', 'Heart_Rate'])
                cat_cols_t     = TRAIN_INFO.get('categorical_cols', ['Gender', 'Blood_Pressure', 'Symptoms'])
                feature_order  = TRAIN_INFO.get('feature_columns', numeric_cols_t + cat_cols_t)

                raw = {'Patient_ID': 0, 'Age': age, 'Temperature': temperature, 'Heart_Rate': heart_rate,
                       'Gender': gender, 'Blood_Pressure': blood_pressure, 'Symptoms': symptoms}
                # use all columns the preprocessor knows about
                all_prep_cols = ['Patient_ID', 'Age', 'Temperature', 'Heart_Rate', 'Gender', 'Blood_Pressure', 'Symptoms']
                input_data = pd.DataFrame([raw])[all_prep_cols]

                cat_encoders = pipeline.get('cat_encoders', {}) or {}
                for col, le in cat_encoders.items():
                    if col in input_data.columns:
                        val = str(input_data.at[0, col])
                        mapping = {c: i for i, c in enumerate(le.classes_)}
                        input_data[col] = mapping.get(val, -1)

                preprocessor = pipeline.get('preprocessor')
                if preprocessor is None:
                    raise ValueError("Model preprocessor not found.")

                processed    = preprocessor.transform(input_data)
                proc_cols    = FEATURE_COLUMNS if FEATURE_COLUMNS else feature_order
                processed_df = pd.DataFrame(processed, columns=proc_cols)

                raw_pred = pipeline['pipeline'].predict(processed_df)[0]

                # decode numeric label → disease name
                target_enc = pipeline.get('target_encoder')
                if target_enc is not None and not isinstance(raw_pred, str):
                    prediction = target_enc.inverse_transform([int(raw_pred)])[0]
                else:
                    prediction = str(raw_pred)

                # confidence probabilities
                proba = None
                if hasattr(pipeline['pipeline'], 'predict_proba'):
                    try:
                        proba = pipeline['pipeline'].predict_proba(processed_df)[0]
                    except Exception:
                        proba = None

                # ── display results ──────────────────────────────────────
                st.divider()
                details = medicine_detail_db.get(prediction, {})
                severity_icon = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(details.get("severity", "Low"), "🟡")
                st.success(f"✅ Predicted Diagnosis: **{prediction}** {severity_icon}")

                if p_name:
                    st.markdown(f"**Patient:** {p_name} | Age: {age} | Gender: {gender}")

                # vitals
                c1, c2, c3 = st.columns(3)
                temp_status = "🔴 High" if temperature > 37.5 else ("🟢 Normal" if temperature >= 36.0 else "🔵 Low")
                hr_status   = "🔴 High" if heart_rate > 100 else ("🟢 Normal" if heart_rate >= 60 else "🔵 Low")
                bp_status   = {"Normal": "🟢 Normal", "High": "🔴 High", "Low": "🔵 Low"}.get(blood_pressure, blood_pressure)
                c1.metric("🌡️ Temperature", f"{temperature}°C", temp_status)
                c2.metric("❤️ Heart Rate",  f"{heart_rate} bpm", hr_status)
                c3.metric("🩸 Blood Pressure", blood_pressure, bp_status)

                # confidence chart — use pipeline's own classes to avoid length mismatch
                if proba is not None and target_enc is not None:
                    try:
                        pipe_classes = pipeline['pipeline'].classes_
                        chart_labels = target_enc.inverse_transform([int(c) for c in pipe_classes])
                        conf_df = pd.DataFrame({"Diagnosis": chart_labels, "Confidence": proba}).sort_values("Confidence", ascending=False).head(5)
                        fig = px.bar(conf_df, x="Confidence", y="Diagnosis", orientation="h",
                                     color="Confidence", color_continuous_scale="Blues",
                                     title="Top Diagnosis Probabilities")
                        fig.update_layout(height=260, margin=dict(t=30, b=0))
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        pass  # chart is optional, skip silently

                # medicine details
                st.divider()
                if details:
                    st.subheader("💊 Medicine & Treatment Plan")
                    m1, m2 = st.columns(2)
                    with m1:
                        st.markdown(f"**💊 Medicines:** {details['medicine']}")
                        st.markdown(f"**⏰ Dosage:** {details['dosage']}")
                        st.markdown(f"**� Duration:** {details['duration']}")
                    with m2:
                        st.markdown(f"**⚠️ Precautions:** {details['precaution']}")
                        st.markdown(f"**👨‍⚕️ See a:** {details['specialist']}")
                        if allergies:
                            st.warning(f"⚠️ Patient allergic to **{allergies}** — verify medicines with doctor.")
                    paracetamol_dose = min(round(weight * 15), 1000)
                    st.info(f"💉 Weight-based Paracetamol dose for {weight}kg: **{paracetamol_dose}mg** per dose (max 4g/day)")
                else:
                    st.info(f"💊 {medicine_mapping.get(prediction, 'Consult a doctor for personalized advice.')}")

                # care instructions
                st.divider()
                st.subheader("📋 Patient Care Instructions")
                urgency = details.get("severity", "Low")
                if urgency == "High":
                    st.error("🚨 HIGH SEVERITY — Visit a hospital immediately.")
                elif urgency == "Medium":
                    st.warning("⚠️ MEDIUM SEVERITY — Consult a doctor within 24 hours.")
                else:
                    st.success("✅ LOW SEVERITY — Home care with rest and medicines should help.")

                st.markdown("""
- 🛏️ Rest adequately, avoid strenuous activity
- 💧 Stay well hydrated (8-10 glasses of water/day)
- 🌡️ Monitor temperature every 4-6 hours
- 📞 Call emergency if symptoms worsen suddenly
- 🔁 Follow up with doctor after completing medicine course
                """)

                st.session_state['last_prediction'] = prediction
                st.session_state['last_patient'] = {
                    'name': p_name, 'age': age, 'gender': gender,
                    'temperature': temperature, 'heart_rate': heart_rate,
                    'blood_pressure': blood_pressure, 'symptoms': symptoms
                }

            except Exception as e:
                st.error(f"❌ Prediction failed: {e}")
                import traceback
                st.code(traceback.format_exc())

# ===== TAB 2: Batch Prediction =====
with tab2:
    st.header("📊 Batch Prediction")
    st.markdown('<div class="card">Upload a CSV file with patient data for multiple predictions at once.</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("📁 Choose a CSV file", type="csv")
    
    if not MODEL_AVAILABLE:
        st.warning("Batch prediction is disabled because the model file is unavailable.")
    elif uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📋 Uploaded Data Preview")
        st.dataframe(df.head(), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("🚀 Run Batch Prediction", key="batch_predict_btn"):
            with st.spinner("🔄 Processing batch predictions..."):
                try:
                    required_cols = ['Age', 'Gender', 'Temperature', 'Heart_Rate', 'Blood_Pressure', 'Symptoms']
                    missing_cols = [col for col in required_cols if col not in df.columns]

                    if missing_cols:
                        st.error(f"❌ Missing columns: {', '.join(missing_cols)}")
                    else:
                        # Preprocessor needs Patient_ID — add it if missing
                        if 'Patient_ID' not in df.columns:
                            df['Patient_ID'] = range(1, len(df) + 1)
                        df['Patient_ID'] = pd.to_numeric(df['Patient_ID'], errors='coerce').fillna(0).astype(int)

                        all_prep_cols = ['Patient_ID', 'Age', 'Temperature', 'Heart_Rate', 'Gender', 'Blood_Pressure', 'Symptoms']
                        df_raw = df[[c for c in all_prep_cols if c in df.columns]].copy()

                        # Apply label encoders to categorical columns
                        cat_encoders = pipeline.get('cat_encoders', {}) or {}
                        for col, le in cat_encoders.items():
                            if col in df_raw.columns:
                                vals = df_raw[col].astype(str)
                                mapping = {c: i for i, c in enumerate(le.classes_)}
                                df_raw[col] = vals.map(mapping).fillna(-1).astype(int)

                        preprocessor = pipeline.get('preprocessor')
                        if preprocessor is None:
                            st.error("Model preprocessor not found in saved pipeline.")
                            st.stop()

                        processed = preprocessor.transform(df_raw)
                        proc_cols = FEATURE_COLUMNS if FEATURE_COLUMNS else all_prep_cols
                        df_processed = pd.DataFrame(processed, columns=proc_cols)

                        raw_preds = pipeline['pipeline'].predict(df_processed)

                        # decode numeric labels → disease names
                        target_enc = pipeline.get('target_encoder')
                        if target_enc is not None and not isinstance(raw_preds[0], str):
                            predictions = target_enc.inverse_transform([int(p) for p in raw_preds])
                        else:
                            predictions = raw_preds

                        df['Predicted_Diagnosis'] = predictions
                        df['Suggested_Medicine'] = df['Predicted_Diagnosis'].map(medicine_mapping).fillna("Consult a doctor")

                        st.success("✅ Predictions completed!")
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.subheader("📊 Prediction Results")
                        show_cols = [c for c in ['Patient_ID', 'Age', 'Predicted_Diagnosis', 'Suggested_Medicine'] if c in df.columns]
                        st.dataframe(df[show_cols], use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        # Download results
                        csv = df.to_csv(index=False)
                        st.download_button("📥 Download Predictions CSV", csv, "predictions.csv", "text/csv", key="download_btn")
                except Exception as e:
                    st.error(f"❌ Batch prediction failed: {e}")

# ===== TAB 3: Voice Input =====
with tab3:
    st.header("🎤 Voice Input Diagnosis")
    st.markdown('<div class="card">Speak your symptoms in Hindi or English for instant diagnosis.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("🗣️ Language")
        voice_language = st.radio("Choose language:", ["हिन्दी (Hindi)", "English"], key="voice_language")
        lang_code = "hi-IN" if "Hindi" in voice_language else "en-IN"
    
    with col2:
        st.subheader("🎙️ Voice Recording")
        if st.button("🔴 Start Recording", key="start_voice_record"):
            st.info("🎤 Listening... Speak your symptoms clearly (up to 10 seconds)")
            try:
                transcript = voice.record_audio(language=lang_code, timeout=10)
                if transcript:
                    st.success(f"✅ Recorded: {transcript}")
                    st.session_state.voice_transcript = transcript
                    
                    # Store in session for further use
                    st.info("💡 Transcript saved. You can use this in Single Prediction tab for detailed diagnosis.")
            except Exception as e:
                st.error(f"Error during voice recording: {e}")
                st.info("💡 Make sure your microphone is connected and working properly.")

# ===== TAB 4: Health History =====
with tab4:
    st.header("📋 Health History & Patient Records")
    st.markdown('<div class="card">View and manage patient medical history for informed diagnosis.</div>', unsafe_allow_html=True)
    
    history_tab1, history_tab2, history_tab3 = st.tabs(["👁️ View History", "➕ Add Patient", "📥 Export"])
    
    with history_tab1:
        st.subheader("🔍 Search Patient Records")
        
        search_type = st.radio("Search by:", ["Patient ID", "Phone Number"], key="history_search_type", horizontal=True)
        
        if search_type == "Patient ID":
            patient_id = st.number_input("Enter Patient ID:", min_value=1, key="search_patient_id")
            if st.button("Search", key="search_btn_id"):
                patient = db.get_patient(patient_id)
                if patient:
                    st.success(f"✅ Patient Found: {patient['name']}")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Age", f"{patient['age']} years")
                    with col2:
                        st.metric("Gender", patient['gender'])
                    with col3:
                        st.metric("Contact", patient['phone'] if patient['phone'] else "N/A")
                    
                    st.divider()
                    st.subheader("📊 Medical History")
                    history = db.get_patient_history(patient_id)
                    
                    if history:
                        for record in history:
                            with st.expander(f"🏥 Visit: {record['visit_date']}" ):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Symptoms:** {record['symptoms']}")
                                    st.write(f"**Diagnosis:** {record['diagnosis']}")
                                with col2:
                                    st.write(f"**Temperature:** {record['temperature']}°C")
                                    st.write(f"**Heart Rate:** {record['heart_rate']} bpm")
                                st.write(f"**BP:** {record['blood_pressure']}")
                    else:
                        st.info("No medical history records found for this patient.")
                else:
                    st.warning(f"❌ Patient #{patient_id} not found in records.")
        
        else:  # Phone search
            phone = st.text_input("Enter Phone Number:", key="search_phone")
            if st.button("Search", key="search_btn_phone"):
                patient_id = db.search_patient_by_phone(phone)
                if patient_id:
                    st.success(f"✅ Found Patient ID: {patient_id}")
                    if st.button("View Details", key="view_details_btn"):
                        patientdet = db.get_patient(patient_id)
                        st.write(f"**Name:** {patientdet['name']}")
                        st.write(f"**Age:** {patientdet['age']}")
                        st.write(f"**Location:** {patientdet['location']}")
                else:
                    st.warning(f"❌ No patient found with phone: {phone}")
    
    with history_tab2:
        st.subheader("➕ Register New Patient")
        
        col1, col2 = st.columns(2)
        with col1:
            pat_name = st.text_input("Full Name:", key="new_patient_name")
            pat_age = st.number_input("Age:", min_value=1, max_value=120, key="new_patient_age")
            pat_gender = st.selectbox("Gender:", ["Male", "Female", "Other"], key="new_patient_gender")
        
        with col2:
            pat_phone = st.text_input("Phone Number:", key="new_patient_phone")
            pat_email = st.text_input("Email (Optional):", key="new_patient_email")
            pat_location = st.text_input("Location:", key="new_patient_location")
        
        if st.button("✅ Register Patient", key="register_btn"):
            if pat_name and pat_age:
                patient_id = db.add_patient(pat_name, pat_age, pat_gender, pat_phone, pat_email, pat_location)
                st.success(f"✅ Patient registered! Patient ID: **{patient_id}**")
                st.balloons()
            else:
                st.error("Please fill in Name and Age fields.")
    
    with history_tab3:
        st.subheader("📥 Export Patient History")
        
        exp_patient_id = st.number_input("Enter Patient ID to Export:", min_value=1, key="export_patient_id")
        
        if st.button("📥 Export as CSV", key="export_btn"):
            try:
                filename = db.export_patient_history_csv(exp_patient_id)
                if "No history" not in filename:
                    st.success(f"✅ History exported successfully!")
                    with open(filename, 'rb') as f:
                        st.download_button(
                            label="📥 Download CSV File",
                            data=f.read(),
                            file_name=filename,
                            mime="text/csv"
                        )
                else:
                    st.warning(f"No medical history found for Patient #{exp_patient_id}")
            except Exception as e:
                st.error(f"Error exporting history: {e}")

# ===== TAB 5: AI Medical Advisor =====
with tab5:
    st.header("🤖 AI Medical Advisor")
    st.info("This feature has been removed from the application.")


# ===== TAB 6: Model Insights =====
with tab6:
    st.header("📈 Model Insights")
    st.markdown('<div class="card">Explore model information, feature importance, and available diagnoses.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🤖 Model Information")
        st.write("• **Model Type:** Random Forest Classifier with Stacking")
        st.write("• **Target:** Diagnosis Prediction")
        st.write("• **Features:** Age, Gender, Temperature, Heart Rate, Blood Pressure, Symptoms")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🏥 Available Diagnoses")
        diagnoses = list(medicine_mapping.keys())
        for diagnosis in diagnoses:
            st.write(f"• {diagnosis}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Feature importance
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 Feature Importance")
    if not MODEL_AVAILABLE:
        st.info("Model insights are unavailable because the trained model is missing.")
    else:
        try:
            # Try to get the stacking classifier
            if hasattr(pipeline['pipeline'], 'named_steps'):
                stack = pipeline['pipeline'].named_steps.get('stack', None)
                if stack and hasattr(stack, 'final_estimator_'):
                    model = stack.final_estimator_
                    if hasattr(model, 'feature_importances_'):
                        importances = model.feature_importances_
                        feature_names = ['Patient_ID', 'Age', 'Gender', 'Temperature', 'Heart_Rate', 'Blood_Pressure', 'Symptoms']
                        
                        importance_df = pd.DataFrame({
                            'Feature': feature_names,
                            'Importance': importances
                        }).sort_values('Importance', ascending=True)
                        
                        fig = px.barh(importance_df, x='Importance', y='Feature', title="Feature Importances", 
                                     color='Importance', color_continuous_scale='Blues')
                        st.plotly_chart(fig, width='stretch')
                    else:
                        st.info("Feature importances not available for this model configuration.")
                else:
                    st.info("Could not extract feature importances from the pipeline.")
            else:
                st.info("Model structure is not compatible with importance visualization.")
        except Exception as e:
            st.warning(f"Could not display feature importance: {e}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("💊 Medicine Mapping")
    st.write("**Auto-suggested medicines based on diagnosed condition:**")
    for diagnosis, medicine in medicine_mapping.items():
        st.write(f"• **{diagnosis}:** {medicine}")
    st.markdown('</div>', unsafe_allow_html=True)

# ===== TAB 7: Find Nearby Doctors =====
with tab7:
    import requests as _requests
    from streamlit_geolocation import streamlit_geolocation

    st.header("🗺️ Find Nearby Doctors & Hospitals")
    st.markdown('<div class="card">Find real doctors and hospitals near your actual location using live map data.</div>', unsafe_allow_html=True)

    # ── helper: query Overpass API for real healthcare places ──────────────
    @st.cache_data(ttl=300, show_spinner=False)
    def fetch_real_doctors(lat, lon, radius_m=5000):
        """Fetch real hospitals/clinics/doctors from OpenStreetMap via Overpass API."""
        overpass_url = "https://overpass-api.de/api/interpreter"
        query = f"""
        [out:json][timeout:25];
        (
          node["amenity"~"hospital|clinic|doctors|pharmacy|health_centre"](around:{radius_m},{lat},{lon});
          way["amenity"~"hospital|clinic|doctors|pharmacy|health_centre"](around:{radius_m},{lat},{lon});
        );
        out center tags;
        """
        try:
            resp = _requests.post(overpass_url, data={"data": query}, timeout=30)
            resp.raise_for_status()
            elements = resp.json().get("elements", [])
            results = []
            for el in elements:
                tags = el.get("tags", {})
                name = tags.get("name") or tags.get("name:en") or tags.get("operator")
                if not name:
                    continue
                if el["type"] == "node":
                    elat, elon = el["lat"], el["lon"]
                else:
                    elat = el.get("center", {}).get("lat")
                    elon = el.get("center", {}).get("lon")
                if not elat or not elon:
                    continue
                amenity = tags.get("amenity", "clinic").replace("_", " ").title()
                phone = tags.get("phone") or tags.get("contact:phone") or "N/A"
                address_parts = [
                    tags.get("addr:housenumber", ""),
                    tags.get("addr:street", ""),
                    tags.get("addr:city", ""),
                ]
                address = ", ".join(p for p in address_parts if p) or tags.get("addr:full", "N/A")
                dist = round(geodesic((lat, lon), (elat, elon)).km, 2)
                results.append({
                    "name": name,
                    "type": amenity,
                    "lat": elat,
                    "lon": elon,
                    "phone": phone,
                    "address": address,
                    "distance_km": dist,
                    "opening_hours": tags.get("opening_hours", "N/A"),
                    "website": tags.get("website") or tags.get("contact:website", "N/A"),
                })
            return sorted(results, key=lambda x: x["distance_km"])
        except Exception as e:
            return []

    # ── GPS via streamlit-geolocation (works on http too) ─────────────────
    st.subheader("📍 Detect Your Real Location")
    st.caption("Click the button below — your browser will ask for location permission.")
    location = streamlit_geolocation()

    gps_lat = location.get("latitude") if location else None
    gps_lon = location.get("longitude") if location else None

    if gps_lat and gps_lon:
        st.success(f"✅ Real location detected: {gps_lat:.5f}, {gps_lon:.5f}")
        # show live location map immediately
        st.subheader("📍 Your Current Location")
        live_map = folium.Map(location=[gps_lat, gps_lon], zoom_start=15, tiles="OpenStreetMap")
        folium.Marker(
            location=[gps_lat, gps_lon],
            popup="📌 You are here",
            icon=folium.Icon(color="blue", icon="home"),
            tooltip="Your Real Location"
        ).add_to(live_map)
        folium.Circle(
            location=[gps_lat, gps_lon],
            radius=500,
            color="#1976d2",
            fill=True,
            fill_opacity=0.15,
            tooltip="~500m radius"
        ).add_to(live_map)
        st_folium(live_map, width=1200, height=350)

    # ── Manual input (fallback) ────────────────────────────────────────────
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📍 Your Location")
        default_lat = gps_lat if gps_lat else 28.7041
        default_lon = gps_lon if gps_lon else 77.1025
        user_lat = st.number_input("Latitude", value=default_lat, format="%.6f", key="doc_lat")
        user_lon = st.number_input("Longitude", value=default_lon, format="%.6f", key="doc_lon")
        st.caption("💡 Click 'Detect My Real Location' above to auto-fill, or enter manually.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🔍 Search Settings")
        max_distance_km = st.slider("Radius (km)", min_value=1, max_value=20, value=5, step=1, key="doc_radius")
        facility_filter = st.selectbox("Facility Type", ["All", "Hospital", "Clinic", "Doctors", "Pharmacy", "Health Centre"], key="doc_filter")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Fetch real data ────────────────────────────────────────────────────
    if st.button("🔍 Search Nearby Doctors & Hospitals", key="search_real_doctors"):
        st.session_state["real_doctors_result"] = fetch_real_doctors(user_lat, user_lon, radius_m=max_distance_km * 1000)
        st.session_state["real_doctors_lat"] = user_lat
        st.session_state["real_doctors_lon"] = user_lon

    real_doctors = st.session_state.get("real_doctors_result", [])
    search_lat = st.session_state.get("real_doctors_lat", user_lat)
    search_lon = st.session_state.get("real_doctors_lon", user_lon)

    # Apply facility filter
    if facility_filter != "All" and real_doctors:
        real_doctors = [d for d in real_doctors if facility_filter.lower() in d["type"].lower()]

    # ── Map ────────────────────────────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🗺️ Live Map")
    m = folium.Map(location=[search_lat, search_lon], zoom_start=14, tiles="OpenStreetMap")

    # User marker
    folium.Marker(
        location=[search_lat, search_lon],
        popup="📌 Your Location",
        icon=folium.Icon(color="blue", icon="home"),
        tooltip="Your Location"
    ).add_to(m)

    # Doctor/hospital markers
    type_colors = {
        "hospital": "red", "clinic": "green", "doctors": "darkgreen",
        "pharmacy": "orange", "health centre": "purple"
    }
    for doc in real_doctors:
        color = type_colors.get(doc["type"].lower(), "gray")
        popup_html = f"""
        <b>{doc['name']}</b><br>
        🏥 {doc['type']}<br>
        📞 {doc['phone']}<br>
        📍 {doc['address']}<br>
        🕐 {doc['opening_hours']}<br>
        <b>📏 {doc['distance_km']} km away</b>
        """
        folium.Marker(
            location=[doc["lat"], doc["lon"]],
            popup=folium.Popup(popup_html, max_width=280),
            icon=folium.Icon(color=color, icon="plus-sign"),
            tooltip=f"{doc['name']} ({doc['distance_km']} km)"
        ).add_to(m)

    st_folium(m, width=1200, height=500)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Results table ──────────────────────────────────────────────────────
    st.divider()
    if real_doctors:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader(f"👨‍⚕️ Found {len(real_doctors)} Healthcare Providers (sorted by distance)")

        # Nearest one highlighted
        nearest = real_doctors[0]
        st.success(f"🏆 Nearest: **{nearest['name']}** — {nearest['type']} — {nearest['distance_km']} km away | 📞 {nearest['phone']}")

        display_df = pd.DataFrame(real_doctors)[["name", "type", "distance_km", "phone", "address", "opening_hours"]]
        display_df.columns = ["Name", "Type", "Distance (km)", "Phone", "Address", "Opening Hours"]
        st.dataframe(display_df, use_container_width=True)

        # Diagnosis-based recommendation using SpecialtyMatcher
        st.divider()
        st.subheader("💡 Recommend by Diagnosis")
        selected_diagnosis = st.selectbox("Select your diagnosis", list(medicine_mapping.keys()), key="diag_recommend")
        recommended_specialties = SpecialtyMatcher.get_matching_specialties(selected_diagnosis)
        st.info(f"Recommended specialties for **{selected_diagnosis}**: {', '.join(recommended_specialties)}")
        st.markdown('</div>', unsafe_allow_html=True)

    elif "real_doctors_result" in st.session_state:
        st.warning("⚠️ No healthcare providers found in this area. Try increasing the radius.")

# ===== TAB 7: Medicine Guide =====
with tab7:
    st.header("💉 Medicine & Treatment Guide")
    st.markdown('<div class="card">Complete reference guide for medicines suggested by the AI model.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        medicine_search = st.text_input("🔍 Search medicine or condition:", placeholder="e.g., Pneumonia, Paracetamol", key="med_search")
    
    with col2:
        med_sort = st.selectbox("Sort by:", ["Alphabetical", "Severity"], key="med_sort")
    
    st.divider()
    
    # Medicine database
    medicine_db = {
        "Common Cold": {
            "medicine": "Rest, Hydration, Paracetamol",
            "dosage": "500mg every 6-8 hours",
            "duration": "3-7 days",
            "precaution": "Stay hydrated, avoid cold air",
            "severity": "Low"
        },
        "Viral Fever": {
            "medicine": "Paracetamol, Fluids, Rest, Vitamin C",
            "dosage": "500mg every 6-8 hours",
            "duration": "5-7 days",
            "precaution": "Complete rest, drink warm fluids",
            "severity": "Medium"
        },
        "Pneumonia": {
            "medicine": "Antibiotics, Steam Inhalation",
            "dosage": "As prescribed by doctor",
            "duration": "10-14 days",
            "precaution": "Complete antibiotic course, chest physiotherapy",
            "severity": "High"
        },
        "Flu": {
            "medicine": "Rest, Warm Fluids, Vitamin C, Antiviral",
            "dosage": "As per symptoms",
            "duration": "7-10 days",
            "precaution": "Vaccination recommended, isolation if needed",
            "severity": "Medium"
        },
        "Food Poisoning": {
            "medicine": "ORS, Antibiotics, Bland Diet",
            "dosage": "ORS every 30-60 minutes",
            "duration": "2-4 days",
            "precaution": "Hydration essential, avoid oily food",
            "severity": "Medium"
        },
        "Dengue (Mild)": {
            "medicine": "Hydration, Paracetamol, Rest",
            "dosage": "500mg every 6-8 hours",
            "duration": "5-7 days",
            "precaution": "Avoid NSAIDs, maintain hydration",
            "severity": "Medium"
        },
        "Bronchitis": {
            "medicine": "Antibiotics, Inhaler, Warm Fluids",
            "dosage": "As prescribed",
            "duration": "7-14 days",
            "precaution": "Avoid smoke, use humidifier",
            "severity": "Medium"
        },
        "Fatigue": {
            "medicine": "Rest, Iron-rich Food, Supplements",
            "dosage": "Iron supplement daily",
            "duration": "2-4 weeks",
            "precaution": "Adequate sleep, balanced diet",
            "severity": "Low"
        },
        "Throat Infection": {
            "medicine": "Salt Water Gargle, Throat Lozenges, Antibiotics",
            "dosage": "Gargle 3-4 times daily",
            "duration": "5-7 days",
            "precaution": "Avoid spicy food, warm liquids",
            "severity": "Low"
        }
    }
    
    # Filter based on search
    if medicine_search:
        filtered_meds = {k: v for k, v in medicine_db.items() 
                        if medicine_search.lower() in k.lower() or medicine_search.lower() in v['medicine'].lower()}
    else:
        filtered_meds = medicine_db
    
    # Sort
    if med_sort == "Severity":
        severity_order = {"High": 0, "Medium": 1, "Low": 2}
        filtered_meds = dict(sorted(filtered_meds.items(), key=lambda x: severity_order.get(x[1]['severity'], 3)))
    else:
        filtered_meds = dict(sorted(filtered_meds.items()))
    
    # Display medicine guide
    if filtered_meds:
        for condition, details in filtered_meds.items():
            severity_color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
            
            with st.expander(f"{severity_color[details['severity']]} {condition}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**💊 Medicine:** {details['medicine']}")
                    st.write(f"**⏰ Dosage:** {details['dosage']}")
                    st.write(f"**📅 Duration:** {details['duration']}")
                
                with col2:
                    st.write(f"**⚠️ Precautions:** {details['precaution']}")
                    st.write(f"**Severity Level:** {details['severity']}")
                
                st.write("*⚕️ Always consult a healthcare professional before starting any medicine.*")
    else:
        st.info(f"No matches found for '{medicine_search}'. Try searching with different keywords.")
    
    st.divider()
    
    st.warning("""
    **⚠️ IMPORTANT DISCLAIMER:**
    ⚕️ This medicine guide is for **informational purposes only**
    ⚕️ Always consult a **qualified healthcare professional** before taking medicines
    ⚕️ Follow the **prescription and dosage** given by your doctor
    ⚕️ Report any **side effects immediately**
    ⚕️ Keep medicines away from **children and pets**
    """)

# Main execution logic
if __name__ == "__main__":
    main_app()