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
from features.ai_advisor import AIMedicalAdvisor
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
    page_title="🏥 Rural Healthcare Predictor",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/hospital.png", width=80)
    st.title("🏥 Rural Healthcare")
    st.markdown("---")
    st.markdown("**Navigation:**")
    st.markdown("- 💊 Single Prediction (ML + AI)")
    st.markdown("- 📊 Batch Prediction")
    st.markdown("- 🎤 Voice Input")
    st.markdown("- 📋 Health History")
    st.markdown("- 🤖 AI Advisor")
    st.markdown("- 📈 Model Insights")
    st.markdown("- 🗺️ Find Doctors")
    st.markdown("- 💉 Medicine Guide")
    st.markdown("---")
    st.markdown("**About:**")
    st.markdown("AI-powered healthcare diagnosis for rural areas. Get predictions, medicine suggestions, and locate nearby doctors.")
    st.markdown("**⚠️ Disclaimer:** For educational use only. Consult professionals for real medical advice.")

import json

# Load the trained model
@st.cache_resource
def load_model():
    try:
        return joblib.load('model/final_pipeline.joblib')
    except Exception as e:
        st.error(f"Failed to load model: {e}")
        return None

# Load training metadata (feature order, raw columns, etc.)
@st.cache_resource
def load_training_info():
    try:
        with open('model/training_artifacts_info.json', 'r', encoding='utf-8') as f:
            return json.load(f)
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
    {"name": "Rural Clinic", "type": "Health Center", "lat": 28.5355, "lon": 77.3910, "phone": "+91-9876543214", "address": "202 Village Road, Ghaziabad"},
    {"name": "Dr. Neha Gupta", "type": "Gynecologist", "lat": 28.7589, "lon": 77.0266, "phone": "+91-9876543215", "address": "303 Women's Health Clinic, Gurgaon"},
]

st.title("🏥 Rural Healthcare Diagnosis Predictor")
st.markdown('<div class="card"><p style="text-align: center; font-size: 18px; color: #666;">🌟 <strong>Empowering Rural Healthcare with AI</strong> 🌟</p></div>', unsafe_allow_html=True)
st.markdown("**⚠️ Disclaimer:** This is a demo app for educational purposes. Consult a healthcare professional for real medical advice.")

# Load the pipeline
pipeline = load_model()

if pipeline is None:
    st.error("Could not load the model. Please ensure the model has been trained.")
    st.stop()

# Set feature columns from the actual trained pipeline
FEATURE_COLUMNS = pipeline.get('feature_columns', TRAIN_INFO.get('feature_columns', []))

# Initialize patient history database
db = PatientHistoryDB()

# Initialize voice input module
voice = VoiceInput()

# Initialize AI Medical Advisor
ai_advisor = AIMedicalAdvisor()

# Tabs with creative icons
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "💊 Single Prediction",
    "📊 Batch Prediction",
    "🎤 Voice Input",
    "📋 Health History",
    "🤖 AI Advisor",
    "📈 Model Insights",
    "🗺️ Find Doctors",
    "💉 Medicine Guide"
])

# ===== TAB 1: Single Prediction =====
with tab1:
    st.header("💊 Predict Diagnosis for a Single Patient")
    st.markdown('<div class="card">Enter patient details below to get a diagnosis prediction and medicine recommendation.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 Patient Information")
        age = st.number_input("Age", min_value=0, max_value=120, value=30)
        gender = st.selectbox("Gender", ["Male", "Female"])
        temperature = st.number_input("🌡️ Temperature (°C)", min_value=30.0, max_value=45.0, value=36.5, step=0.1)
        heart_rate = st.number_input("❤️ Heart Rate (bpm)", min_value=40, max_value=200, value=70)
    
    with col2:
        st.subheader("📋 Medical Details")
        blood_pressure = st.selectbox("🩸 Blood Pressure", ["Normal", "High", "Low"])
        symptoms = st.selectbox("🤒 Symptoms", ["Cough", "Fever", "Fatigue", "Headache", "Nausea", "Other"])  
        # Medicine_Advice is not passed to the model because it was not used during training.
    if st.button("🔍 Predict Diagnosis", key="predict_btn"):
        with st.spinner("🔄 Analyzing patient data..."):
            try:
                input_data = pd.DataFrame({
                    'Patient_ID': [0],
                    'Age': [age],
                    'Gender': [gender],
                    'Temperature': [temperature],
                    'Heart_Rate': [heart_rate],
                    'Blood_Pressure': [blood_pressure],
                    'Symptoms': [symptoms]
                })

                # Ensure the raw features are in the same order as training
                if RAW_FEATURE_COLUMNS:
                    # Build the expected feature columns including Patient_ID
                    expected_features = ['Patient_ID'] + [c for c in RAW_FEATURE_COLUMNS if c != 'Patient_ID']
                    missing = [c for c in expected_features if c not in input_data.columns]
                    if missing:
                        raise ValueError(f"Missing features required by model: {missing}")
                    input_data = input_data[expected_features]

                # Ensure Patient_ID is numeric
                input_data['Patient_ID'] = pd.to_numeric(input_data['Patient_ID'], errors='coerce').fillna(0).astype(int)

                # Apply label encoders (from training) to categorical columns ONLY
                cat_encoders = pipeline.get('cat_encoders', {}) or {}
                for col, le in cat_encoders.items():
                    if col in input_data.columns:
                        vals = input_data[col].astype(str).fillna("nan_missing")
                        mapping = {c: i for i, c in enumerate(le.classes_)}
                        input_data[col] = vals.map(mapping).fillna(mapping.get("nan_missing", -1)).astype(int)

                # Apply preprocessing from training (scaling, imputation)
                preprocessor = pipeline.get('preprocessor')
                if preprocessor is None:
                    raise ValueError("Model preprocessor not found in saved pipeline.")

                processed = preprocessor.transform(input_data)
                processed_df = pd.DataFrame(processed, columns=FEATURE_COLUMNS)

                prediction = pipeline['pipeline'].predict(processed_df)[0]

                st.success(f"✅ **ML Predicted Diagnosis: {prediction}**")

                # Show medicine advice
                advice = medicine_mapping.get(prediction, "Consult a doctor for personalized advice.")
                st.info(f"💊 **Suggested Medicine/Advice:** {advice}")

                # ===== OPENAI PREDICTION OPTION =====
                st.markdown("---")
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("🤖 Get OpenAI Prediction", key="openai_predict_btn"):
                        # Prepare patient data for OpenAI
                        patient_data = {
                            'name': 'Anonymous Patient',
                            'age': age,
                            'gender': gender,
                            'temperature': temperature,
                            'heart_rate': heart_rate,
                            'blood_pressure': blood_pressure,
                            'symptoms': symptoms,
                            'location': 'Rural India'
                        }

                        with st.spinner("🤖 OpenAI analyzing patient data..."):
                            ai_prediction = ai_advisor.predict_diagnosis(patient_data)

                        if ai_prediction['confidence'] > 0:
                            st.success(f"🤖 **AI Predicted Diagnosis: {ai_prediction['diagnosis']}**")
                            st.info(f"🎯 **AI Confidence: {ai_prediction['confidence']*100:.1f}%**")

                            # Show AI reasoning
                            with st.expander("📋 AI Reasoning"):
                                st.write(ai_prediction['reasoning'])

                            # Show differential diagnoses
                            if ai_prediction.get('differential_diagnoses'):
                                st.subheader("🔍 Alternative Possibilities:")
                                for alt_diag in ai_prediction['differential_diagnoses'][:3]:
                                    st.write(f"• {alt_diag}")
                        else:
                            st.error(f"❌ AI Prediction failed: {ai_prediction['reasoning']}")

                with col2:
                    # AI-Enhanced Advice Option
                    if st.button("🧠 Get AI-Enhanced Advice", key="ai_enhance_btn"):
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.subheader("🤖 AI-Enhanced Analysis")

                        # Prepare patient data for AI analysis
                        patient_data = {
                            'name': 'Anonymous Patient',
                            'age': age,
                            'gender': gender,
                            'temperature': temperature,
                            'heart_rate': heart_rate,
                            'blood_pressure': blood_pressure,
                            'symptoms': symptoms,
                            'location': 'Rural India'
                        }

                        # Get AI analysis
                        with st.spinner("🤖 AI analyzing patient data..."):
                            ai_analysis = ai_advisor.analyze_patient_data(patient_data)

                        if 'error' not in ai_analysis:
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("AI Diagnosis", ai_analysis['diagnosis'])
                                st.metric("Urgency", ai_analysis['urgency_level'])

                            with col2:
                                st.metric("Doctor Specialty", ai_analysis['doctor_suggestion'])

                            st.subheader("💊 AI Medicine Recommendations")
                            st.info(ai_analysis['medicine_advice'])

                            st.subheader("📋 AI Additional Advice")
                            st.write(ai_analysis['additional_advice'])

                            st.subheader("📅 AI Follow-up Recommendation")
                            st.write(ai_analysis['follow_up'])
                        else:
                            st.warning(f"⚠️ AI Analysis unavailable: {ai_analysis.get('error', 'Unknown error')}")

                        st.markdown('</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Prediction failed: {e}")

# ===== TAB 2: Batch Prediction =====
with tab2:
    st.header("📊 Batch Prediction")
    st.markdown('<div class="card">Upload a CSV file with patient data for multiple predictions at once.</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("📁 Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📋 Uploaded Data Preview")
        st.dataframe(df.head(), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("🚀 Run Batch Prediction", key="batch_predict_btn"):
            with st.spinner("🔄 Processing batch predictions..."):
                try:
                    required_cols = ['Age', 'Gender', 'Temperature', 'Heart_Rate', 'Blood_Pressure', 'Symptoms']
                    # Patient_ID is optional for batch prediction but will be included if present
                    missing_cols = [col for col in required_cols if col not in df.columns]

                    if missing_cols:
                        st.error(f"❌ Missing columns: {', '.join(missing_cols)}")
                    else:
                        # Add Patient_ID if not present (for compatibility with model)
                        if 'Patient_ID' not in df.columns:
                            df['Patient_ID'] = range(1, len(df) + 1)
                        
                        # Ensure Patient_ID is numeric
                        df['Patient_ID'] = pd.to_numeric(df['Patient_ID'], errors='coerce').fillna(range(1, len(df) + 1)).astype(int)
                        
                        # Ensure correct feature order if available
                        # Ensure raw features match what the preprocessor expects
                        if RAW_FEATURE_COLUMNS:
                            # Build the expected feature columns including Patient_ID
                            expected_features = ['Patient_ID'] + [c for c in RAW_FEATURE_COLUMNS if c != 'Patient_ID']
                            missing = [c for c in expected_features if c not in df.columns]
                            if missing:
                                st.error(f"❌ Missing features required by model: {', '.join(missing)}")
                                st.stop()
                            # Include Patient_ID for preprocessing 
                            df_raw = df[expected_features].copy()
                        else:
                            df_raw = df[required_cols].copy()

                        # Apply label encoders (from training) to categorical columns ONLY
                        cat_encoders = pipeline.get('cat_encoders', {}) or {}
                        for col, le in cat_encoders.items():
                            if col in df_raw.columns:
                                vals = df_raw[col].astype(str).fillna("nan_missing")
                                mapping = {c: i for i, c in enumerate(le.classes_)}
                                df_raw[col] = vals.map(mapping).fillna(mapping.get("nan_missing", -1)).astype(int)

                        preprocessor = pipeline.get('preprocessor')
                        if preprocessor is None:
                            st.error("Model preprocessor not found in saved pipeline.")
                            st.stop()

                        processed = preprocessor.transform(df_raw)
                        # Use all feature columns from the preprocessor output
                        df_processed = pd.DataFrame(processed, columns=FEATURE_COLUMNS)

                        predictions = pipeline['pipeline'].predict(df_processed)
                        df['Predicted_Diagnosis'] = predictions
                        df['Suggested_Medicine'] = df['Predicted_Diagnosis'].map(medicine_mapping).fillna("Consult a doctor")

                        st.success("✅ Predictions completed!")
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.subheader("📊 Prediction Results")
                        st.dataframe(df[['Patient_ID', 'Age', 'Predicted_Diagnosis', 'Suggested_Medicine']], use_container_width=True)
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
    st.markdown('<div class="card">Get intelligent medical advice powered by AI that learns from patient history and provides personalized recommendations.</div>', unsafe_allow_html=True)

    # OpenAI API Key Configuration
    st.subheader("🔑 OpenAI Configuration")

    # Check if API key is already configured
    try:
        from config.openai_config import OPENAI_API_KEY
        api_key_configured = OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here"
    except ImportError:
        api_key_configured = False

    if api_key_configured:
        st.success("✅ OpenAI API key is configured in config/openai_config.py")
        use_config_key = st.checkbox("Use configured API key", value=True, key="use_config_key")
        if not use_config_key:
            api_key = st.text_input("Or enter a different OpenAI API Key:", type="password")
        else:
            api_key = OPENAI_API_KEY
    else:
        st.warning("⚠️ OpenAI API key not configured. Please enter your API key below or configure it in config/openai_config.py")
        api_key = st.text_input("Enter your OpenAI API Key:", type="password", help="Get your API key from https://platform.openai.com/api-keys")

    if api_key and api_key != "your_openai_api_key_here":
        # Initialize AI advisor with the provided key
        ai_advisor_temp = AIMedicalAdvisor(api_key=api_key)

        st.success("✅ AI Advisor configured successfully!")

        # Patient Analysis Section
        st.divider()
        st.subheader("🔍 AI-Powered Patient Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("👤 Patient Information")

            # Patient selection or new entry
            analysis_type = st.radio("Analysis Type:", ["New Patient", "Existing Patient"], key="ai_analysis_type")

            if analysis_type == "Existing Patient":
                patient_id = st.number_input("Patient ID:", min_value=1, key="ai_patient_id")
                if st.button("Load Patient Data", key="load_patient_ai"):
                    patient_data = db.get_patient(patient_id)
                    if patient_data:
                        st.session_state['ai_patient_data'] = patient_data
                        st.success(f"✅ Loaded data for {patient_data['name']}")
                    else:
                        st.error("Patient not found")
            else:
                # New patient form
                pat_name = st.text_input("Patient Name:", key="ai_patient_name")
                pat_age = st.number_input("Age:", min_value=1, max_value=120, key="ai_patient_age")
                pat_gender = st.selectbox("Gender:", ["Male", "Female", "Other"], key="ai_patient_gender")
                pat_location = st.text_input("Location:", key="ai_patient_location")

                if st.button("Set Patient Info", key="set_patient_ai"):
                    st.session_state['ai_patient_data'] = {
                        'name': pat_name,
                        'age': pat_age,
                        'gender': pat_gender,
                        'location': pat_location
                    }
                    st.success("✅ Patient information set")

            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📋 Current Symptoms")

            temperature = st.number_input("🌡️ Temperature (°C):", min_value=30.0, max_value=45.0, value=36.5, step=0.1, key="ai_temp")
            heart_rate = st.number_input("❤️ Heart Rate (bpm):", min_value=40, max_value=200, value=70, key="ai_hr")
            blood_pressure = st.selectbox("🩸 Blood Pressure:", ["Normal", "High", "Low"], key="ai_bp")
            symptoms = st.text_area("🤒 Symptoms Description:", height=100, key="ai_symptoms",
                                  placeholder="Describe the symptoms in detail...")

            if st.button("🔍 Get AI Analysis", key="ai_analyze_btn"):
                if 'ai_patient_data' in st.session_state:
                    # Prepare patient data for analysis
                    patient_data = st.session_state['ai_patient_data'].copy()
                    patient_data.update({
                        'temperature': temperature,
                        'heart_rate': heart_rate,
                        'blood_pressure': blood_pressure,
                        'symptoms': symptoms
                    })

                    # Get medical history if existing patient
                    medical_history = None
                    if analysis_type == "Existing Patient" and 'patient_id' in locals():
                        medical_history = db.get_patient_history(patient_id)

                    with st.spinner("🤖 AI is analyzing patient data..."):
                        analysis = ai_advisor_temp.analyze_patient_data(patient_data, medical_history)

                    if 'error' not in analysis:
                        # Display results
                        st.success("✅ AI Analysis Complete!")

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            urgency_colors = {"Low": "🟢", "Medium": "🟡", "High": "🔴", "Critical": "🔴💀"}
                            st.metric("Urgency Level", f"{urgency_colors.get(analysis['urgency_level'], '🟡')} {analysis['urgency_level']}")

                        with col2:
                            st.metric("Suggested Doctor", analysis['doctor_suggestion'])

                        with col3:
                            st.metric("Diagnosis", analysis['diagnosis'])

                        st.divider()

                        # Detailed recommendations
                        st.subheader("💊 Medicine Recommendations")
                        st.info(f"**{analysis['medicine_advice']}**")

                        st.subheader("🏥 Doctor Consultation")
                        st.write(f"**Recommended Specialty:** {analysis['doctor_suggestion']}")

                        st.subheader("📋 Additional Advice")
                        st.write(analysis['additional_advice'])

                        st.subheader("📅 Follow-up Care")
                        st.write(analysis['follow_up'])

                        # Save analysis to patient history if existing patient
                        if analysis_type == "Existing Patient" and 'patient_id' in locals():
                            if st.button("💾 Save Analysis to History", key="save_ai_analysis"):
                                db.add_medical_record(
                                    patient_id=patient_id,
                                    symptoms=symptoms,
                                    diagnosis=analysis['diagnosis'],
                                    temperature=temperature,
                                    heart_rate=heart_rate,
                                    blood_pressure=blood_pressure,
                                    medicine_prescribed=analysis['medicine_advice'],
                                    doctor_notes=f"AI Analysis: {analysis['additional_advice']}"
                                )
                                st.success("✅ Analysis saved to patient history!")

                    else:
                        st.error(f"❌ {analysis['error']}")

                else:
                    st.warning("⚠️ Please set patient information first")

            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.warning("⚠️ Please enter your OpenAI API key to use the AI Medical Advisor")
        st.markdown("""
        **How to get an OpenAI API key:**
        1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
        2. Sign in to your OpenAI account
        3. Click 'Create new secret key'
        4. Copy the key and paste it above
        """)

# ===== TAB 6: Model Insights =====
with tab5:
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
with tab6:
    st.header("🗺️ Find Nearby Doctors & Hospitals")
    st.markdown('<div class="card">Use this interactive tool to find healthcare professionals and hospitals near your location.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📍 Location Input")
        st.write("**Enter your location (latitude & longitude) or use default:**")
        
        default_user_lat = 28.7041
        default_user_lon = 77.1025
        
        user_lat = st.number_input("Your Latitude", value=default_user_lat, format="%.4f")
        user_lon = st.number_input("Your Longitude", value=default_user_lon, format="%.4f")
        
        max_distance = st.slider("🔍 Search within (km)", min_value=1, max_value=50, value=15, step=1)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🏥 Doctor Type Filter")
        doctor_types = ["All"] + list(set([d["type"] for d in doctors_data]))
        selected_type = st.selectbox("Filter by type", doctor_types)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Calculate distances
    doctors_df = pd.DataFrame(doctors_data)
    doctors_df["distance_km"] = doctors_df.apply(
        lambda row: geodesic((user_lat, user_lon), (row["lat"], row["lon"])).km,
        axis=1
    )
    
    # Filter by distance
    filtered_doctors = doctors_df[doctors_df["distance_km"] <= max_distance].copy()
    
    # Filter by type
    if selected_type != "All":
        filtered_doctors = filtered_doctors[filtered_doctors["type"] == selected_type]
    
    filtered_doctors = filtered_doctors.sort_values("distance_km")
    
    # Create interactive map
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📍 Interactive Map")
    
    map_center = [user_lat, user_lon]
    m = folium.Map(location=map_center, zoom_start=12, tiles="OpenStreetMap")
    
    # Add user location marker
    folium.Marker(
        location=[user_lat, user_lon],
        popup="📌 Your Location",
        icon=folium.Icon(color="blue", icon="location-dot", prefix="fa"),
        tooltip="Your Current Location"
    ).add_to(m)
    
    # Add doctor/hospital markers
    colors = {"General Practitioner": "green", "Hospital": "red", "Health Center": "orange", 
              "Pediatrician": "lightblue", "Cardiologist": "darkred", "Gynecologist": "pink"}
    
    for idx, doctor in filtered_doctors.iterrows():
        color = colors.get(doctor["type"], "gray")
        folium.Marker(
            location=[doctor["lat"], doctor["lon"]],
            popup=f"<b>{doctor['name']}</b><br>{doctor['type']}<br>Distance: {doctor['distance_km']:.2f} km<br>Phone: {doctor['phone']}",
            icon=folium.Icon(color=color, icon="hospital", prefix="fa"),
            tooltip=f"{doctor['name']} ({doctor['distance_km']:.2f} km)"
        ).add_to(m)
    
    st_folium(m, width=1200, height=500)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Display nearby doctors in table format
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(f"👨‍⚕️ Nearby Healthcare Providers ({len(filtered_doctors)} found)")
    
    if len(filtered_doctors) > 0:
        display_df = filtered_doctors[["name", "type", "distance_km", "phone", "address"]].copy()
        display_df["distance_km"] = display_df["distance_km"].round(2)
        display_df.columns = ["Name", "Type", "Distance (km)", "Phone", "Address"]
        
        st.dataframe(display_df, use_container_width=True)
        
        # Recommend doctor based on diagnosis
        st.divider()
        st.subheader("💡 Doctor Recommendation Based on Diagnosis")
        
        diagnosis_to_specialist = {
            "Common Cold": "General Practitioner",
            "Viral Fever": "General Practitioner",
            "Pneumonia": "General Practitioner",
            "Flu": "General Practitioner",
            "Food Poisoning": "General Practitioner",
            "Dengue (Mild)": "General Practitioner",
            "Bronchitis": "General Practitioner",
            "Fatigue": "General Practitioner",
            "Throat Infection": "General Practitioner"
        }
        
        selected_diagnosis = st.selectbox("Select your diagnosis", list(diagnosis_to_specialist.keys()))
        specialist_type = diagnosis_to_specialist[selected_diagnosis]
        
        specialist_doctors = filtered_doctors[filtered_doctors["type"] == specialist_type].sort_values("distance_km")
        
        if len(specialist_doctors) > 0:
            st.success(f"✅ **Recommended Specialists for {selected_diagnosis}:**")
            for idx, doctor in specialist_doctors.head(3).iterrows():
                st.info(f"""
                **{doctor['name']}**
                - Type: {doctor['type']}
                - Distance: {doctor['distance_km']:.2f} km away
                - Phone: {doctor['phone']}
                - Address: {doctor['address']}
                """)
        else:
            st.warning(f"⚠️ No {specialist_type} found within {max_distance} km. Try increasing the search distance.")
    else:
        st.warning(f"⚠️ No healthcare providers found within {max_distance} km. Try increasing the search distance.")
    st.markdown('</div>', unsafe_allow_html=True)

# ===== TAB 8: Medicine Guide =====
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