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
from server.features.voice_input import VoiceInput, SymptomExtractor
from server.features.doctor_finder import DoctorFinder, SpecialtyMatcher
from server.database.patient_history import PatientHistoryDB

# Main app content (only shown if logged in)
def main_app():
    # Hackathon Dark Theme — CSS only
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700;800&display=swap');

    /* ═══════════════════════════════════════════
       BASE — deep dark background
    ═══════════════════════════════════════════ */
    html, body, [class*="css"] {
        font-family: 'Inter', 'Space Grotesk', sans-serif !important;
    }
    .main .block-container {
        padding: 2rem 2.5rem 3rem !important;
        max-width: 1400px;
    }
    .main {
        background: #050d1a !important;
    }
    /* Dark background for entire app */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #050d1a 0%, #0a1628 50%, #060e1c 100%) !important;
    }
    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* ═══════════════════════════════════════════
       SIDEBAR — darker with cyan glow
    ═══════════════════════════════════════════ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020810 0%, #060f1e 50%, #040c18 100%) !important;
        border-right: 1px solid rgba(0,255,200,0.12) !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }
    [data-testid="stSidebar"] * {
        color: #94a3b8 !important;
    }
    [data-testid="stSidebar"] h1 {
        color: #e2e8f0 !important;
        font-size: 1.1rem !important;
        font-weight: 800 !important;
    }
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #00ffc8 !important;
        font-weight: 700 !important;
        font-size: 0.7rem !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] li {
        color: #64748b !important;
        font-size: 0.83rem !important;
        line-height: 1.7;
    }
    [data-testid="stSidebar"] strong {
        color: #cbd5e1 !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(0,255,200,0.1) !important;
        margin: 1rem 0 !important;
    }

    /* ═══════════════════════════════════════════
       HERO BANNER — neon gradient
    ═══════════════════════════════════════════ */
    .hero-banner {
        background: linear-gradient(135deg, #0a0f1e 0%, #0d1f3c 40%, #0a2040 100%);
        border-radius: 20px;
        padding: 2.4rem 2.8rem;
        margin-bottom: 1.8rem;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(0,255,200,0.2);
        box-shadow: 0 0 40px rgba(0,255,200,0.08), 0 0 80px rgba(0,150,255,0.06), inset 0 1px 0 rgba(255,255,255,0.05);
    }
    .hero-banner::before {
        content: '';
        position: absolute;
        top: -60px; right: -60px;
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(0,255,200,0.08) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-banner::after {
        content: '';
        position: absolute;
        bottom: -80px; left: 20%;
        width: 250px; height: 250px;
        background: radial-gradient(circle, rgba(0,150,255,0.07) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-title {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 2.1rem !important;
        font-weight: 800 !important;
        background: linear-gradient(90deg, #00ffc8, #00b4ff, #7c3aed) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        margin: 0 0 0.5rem 0 !important;
        letter-spacing: -0.5px;
        line-height: 1.2;
    }
    .hero-subtitle {
        font-size: 0.92rem !important;
        color: #64748b !important;
        margin: 0 !important;
        font-weight: 400;
        line-height: 1.6;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(0,255,200,0.08);
        border: 1px solid rgba(0,255,200,0.3);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.75rem;
        font-weight: 700;
        color: #00ffc8 !important;
        margin-bottom: 1rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .disclaimer-bar {
        background: rgba(245,158,11,0.08);
        border: 1px solid rgba(245,158,11,0.25);
        border-radius: 10px;
        padding: 10px 16px;
        font-size: 0.82rem;
        color: #fbbf24 !important;
        margin-bottom: 1.5rem;
    }

    /* ═══════════════════════════════════════════
       TABS
    ═══════════════════════════════════════════ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(255,255,255,0.03);
        border-radius: 14px;
        padding: 5px;
        border: 1px solid rgba(255,255,255,0.07);
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 10px !important;
        padding: 9px 20px !important;
        color: #475569 !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        transition: all 0.18s ease !important;
        border: none !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(0,255,200,0.06) !important;
        color: #00ffc8 !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0,255,200,0.15), rgba(0,180,255,0.15)) !important;
        color: #00ffc8 !important;
        border: 1px solid rgba(0,255,200,0.3) !important;
        box-shadow: 0 0 16px rgba(0,255,200,0.12) !important;
    }

    /* ═══════════════════════════════════════════
       HEADINGS
    ═══════════════════════════════════════════ */
    h1 { color: #e2e8f0 !important; font-weight: 800 !important; }
    h2 { color: #cbd5e1 !important; font-weight: 700 !important; font-size: 1.25rem !important; }
    h3 { color: #94a3b8 !important; font-weight: 600 !important; font-size: 1rem !important; }
    p, li, span { color: #94a3b8; }

    /* ═══════════════════════════════════════════
       CARDS
    ═══════════════════════════════════════════ */
    .card {
        background: rgba(255,255,255,0.03);
        border-radius: 14px;
        padding: 20px 24px;
        margin: 10px 0;
        border: 1px solid rgba(255,255,255,0.07);
        border-top: 2px solid #00ffc8;
        box-shadow: 0 4px 24px rgba(0,0,0,0.3), 0 0 0 1px rgba(0,255,200,0.04);
        transition: border-color 0.2s, box-shadow 0.2s;
        backdrop-filter: blur(10px);
    }
    .card:hover {
        border-top-color: #00b4ff;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 20px rgba(0,255,200,0.06);
    }

    /* ═══════════════════════════════════════════
       BUTTONS — neon glow
    ═══════════════════════════════════════════ */
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 11px 28px !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        letter-spacing: 0.3px !important;
        transition: all 0.22s ease !important;
        box-shadow: 0 0 20px rgba(124,58,237,0.4), 0 4px 14px rgba(0,0,0,0.4) !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 0 35px rgba(124,58,237,0.6), 0 8px 24px rgba(0,0,0,0.5) !important;
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* ═══════════════════════════════════════════
       INPUTS
    ═══════════════════════════════════════════ */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 9px !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        background: #0d1f38 !important;
        color: #f1f5f9 !important;
        caret-color: #00ffc8 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.92rem !important;
        transition: border-color 0.18s, box-shadow 0.18s !important;
    }
    .stTextInput > div > div > input::placeholder,
    .stNumberInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #475569 !important;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #00ffc8 !important;
        box-shadow: 0 0 0 3px rgba(0,255,200,0.1), 0 0 12px rgba(0,255,200,0.08) !important;
        outline: none !important;
        background: #0f2540 !important;
    }
    .stSelectbox > div > div {
        border-radius: 9px !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        background: #0d1f38 !important;
        color: #f1f5f9 !important;
    }
    /* Selectbox dropdown text */
    .stSelectbox > div > div > div {
        color: #f1f5f9 !important;
    }
    /* Number input buttons */
    .stNumberInput > div > div > div > button {
        background: rgba(255,255,255,0.06) !important;
        color: #94a3b8 !important;
        border-color: rgba(255,255,255,0.1) !important;
    }
    .stTextInput label, .stNumberInput label,
    .stSelectbox label, .stTextArea label,
    .stSlider label, .stRadio label {
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        color: #64748b !important;
        text-transform: uppercase !important;
        letter-spacing: 0.6px !important;
    }

    /* ═══════════════════════════════════════════
       METRICS
    ═══════════════════════════════════════════ */
    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.03) !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        border: 1px solid rgba(255,255,255,0.07) !important;
        border-bottom: 2px solid #00ffc8 !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3) !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.7rem !important;
        font-weight: 700 !important;
        color: #475569 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.55rem !important;
        font-weight: 800 !important;
        color: #e2e8f0 !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }

    /* ═══════════════════════════════════════════
       ALERTS
    ═══════════════════════════════════════════ */
    .stSuccess > div {
        background: rgba(0,200,100,0.08) !important;
        border-left: 3px solid #00c864 !important;
        border-radius: 10px !important;
        color: #4ade80 !important;
    }
    .stInfo > div {
        background: rgba(0,180,255,0.08) !important;
        border-left: 3px solid #00b4ff !important;
        border-radius: 10px !important;
        color: #7dd3fc !important;
    }
    .stWarning > div {
        background: rgba(245,158,11,0.08) !important;
        border-left: 3px solid #f59e0b !important;
        border-radius: 10px !important;
        color: #fbbf24 !important;
    }
    .stError > div {
        background: rgba(239,68,68,0.08) !important;
        border-left: 3px solid #ef4444 !important;
        border-radius: 10px !important;
        color: #f87171 !important;
    }

    /* ═══════════════════════════════════════════
       EXPANDERS
    ═══════════════════════════════════════════ */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.03) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        color: #94a3b8 !important;
        border: 1px solid rgba(255,255,255,0.07) !important;
        transition: all 0.18s !important;
    }
    .streamlit-expanderHeader:hover {
        background: rgba(0,255,200,0.04) !important;
        color: #00ffc8 !important;
        border-color: rgba(0,255,200,0.2) !important;
    }
    .streamlit-expanderContent {
        background: rgba(255,255,255,0.02) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
    }

    /* ═══════════════════════════════════════════
       DATAFRAME
    ═══════════════════════════════════════════ */
    [data-testid="stDataFrame"] {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid rgba(255,255,255,0.07) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
    }

    /* ═══════════════════════════════════════════
       DIVIDER
    ═══════════════════════════════════════════ */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(0,255,200,0.2) 30%, rgba(0,180,255,0.2) 70%, transparent) !important;
        margin: 1.5rem 0 !important;
    }

    /* ═══════════════════════════════════════════
       RADIO
    ═══════════════════════════════════════════ */
    .stRadio > div > label {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-size: 0.85rem !important;
        color: #64748b !important;
        transition: all 0.18s !important;
    }
    .stRadio > div > label:hover {
        border-color: rgba(0,255,200,0.3) !important;
        color: #00ffc8 !important;
        background: rgba(0,255,200,0.05) !important;
    }

    /* ═══════════════════════════════════════════
       SLIDER
    ═══════════════════════════════════════════ */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #00ffc8, #00b4ff) !important;
    }

    /* ═══════════════════════════════════════════
       ANIMATIONS
    ═══════════════════════════════════════════ */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 10px rgba(0,255,200,0.2); }
        50% { box-shadow: 0 0 25px rgba(0,255,200,0.5); }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(12px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .loading { animation: pulse 1.5s infinite; }
    .glow    { animation: glow 2s infinite; }
    .fade-in { animation: fadeInUp 0.4s ease forwards; }

    /* ═══════════════════════════════════════════
       SEVERITY BADGES
    ═══════════════════════════════════════════ */
    .badge {
        display: inline-flex; align-items: center; gap: 5px;
        padding: 3px 10px; border-radius: 20px;
        font-size: 0.72rem; font-weight: 700; letter-spacing: 0.3px;
    }
    .badge-low    { background: rgba(0,200,100,0.12); color: #4ade80; border: 1px solid rgba(0,200,100,0.25); }
    .badge-medium { background: rgba(245,158,11,0.12); color: #fbbf24; border: 1px solid rgba(245,158,11,0.25); }
    .badge-high   { background: rgba(239,68,68,0.12); color: #f87171; border: 1px solid rgba(239,68,68,0.25); }

    /* ═══════════════════════════════════════════
       SCROLLBAR
    ═══════════════════════════════════════════ */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #0a1628; border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: rgba(0,255,200,0.25); border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #00ffc8; }

    /* ═══════════════════════════════════════════
       MISC
    ═══════════════════════════════════════════ */
    .block-container { padding-top: 1.5rem !important; }
    .stDownloadButton > button {
        background: linear-gradient(135deg, #00c896, #00e0a8) !important;
        color: #050d1a !important;
    }
    /* Plotly dark background */
    .js-plotly-plot .plotly { background: transparent !important; }
</style>
""", unsafe_allow_html=True)


st.set_page_config(
    page_title="🏥 Early Disease Prediction",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
with st.sidebar:
    st.markdown("""
<div style="text-align:center; padding: 0.5rem 0 1.2rem;">
    <div style="font-size:2.8rem; margin-bottom:0.3rem;">🏥</div>
    <div style="font-size:1.05rem; font-weight:800; color:#f0f9ff; letter-spacing:-0.3px; line-height:1.3;">
        HealthPredict AI
    </div>
    <div style="font-size:0.72rem; color:#7dd3fc; font-weight:500; letter-spacing:1px; text-transform:uppercase; margin-top:4px;">
        Rural Healthcare System
    </div>
</div>
""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
<div style="font-size:0.7rem; font-weight:700; color:#7dd3fc; text-transform:uppercase; letter-spacing:1.2px; margin-bottom:10px;">
    Navigation
</div>
<div style="display:flex; flex-direction:column; gap:4px;">
    <div style="padding:8px 12px; border-radius:8px; background:rgba(56,189,248,0.08); border:1px solid rgba(56,189,248,0.12); font-size:0.85rem; color:#e2e8f0;">💊 Single Prediction</div>
    <div style="padding:8px 12px; border-radius:8px; font-size:0.85rem; color:#94a3b8;">🎤 Voice Input</div>
    <div style="padding:8px 12px; border-radius:8px; font-size:0.85rem; color:#94a3b8;">📋 Health History</div>
    <div style="padding:8px 12px; border-radius:8px; font-size:0.85rem; color:#94a3b8;">📈 Model Insights</div>
    <div style="padding:8px 12px; border-radius:8px; font-size:0.85rem; color:#94a3b8;">🗺️ Find Doctors</div>
    <div style="padding:8px 12px; border-radius:8px; font-size:0.85rem; color:#94a3b8;">💉 Medicine Guide</div>
</div>
""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
<div style="font-size:0.7rem; font-weight:700; color:#7dd3fc; text-transform:uppercase; letter-spacing:1.2px; margin-bottom:8px;">
    About
</div>
<div style="font-size:0.82rem; color:#94a3b8; line-height:1.65;">
    AI-powered early disease detection for rural healthcare. Get instant predictions, medicine guidance, and locate nearby doctors.
</div>
<div style="margin-top:14px; padding:10px 12px; background:rgba(245,158,11,0.1); border:1px solid rgba(245,158,11,0.25); border-radius:8px; font-size:0.75rem; color:#fbbf24; line-height:1.5;">
    ⚠️ For educational use only. Always consult a qualified healthcare professional.
</div>
""", unsafe_allow_html=True)

import json

BASE_DIR = os.path.dirname(__file__)

# Load the trained model
@st.cache_resource
def load_model():
    model_path = os.path.join(BASE_DIR, 'server', 'model', 'final_pipeline.joblib')
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
    info_path = os.path.join(BASE_DIR, 'server', 'model', 'training_artifacts_info.json')
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

st.markdown("""
<div class="hero-banner">
    <div class="hero-badge">⚡ Hackathon 2026 &nbsp;|&nbsp; AI Healthcare</div>
    <div class="hero-title">Early Disease Prediction System</div>
    <div class="hero-subtitle">AI-powered diagnosis · Medicine guidance · Real-time doctor discovery · Built for rural healthcare access</div>
</div>
""", unsafe_allow_html=True)
st.markdown("""
<div class="disclaimer-bar">
    ⚠️ <strong>Disclaimer:</strong> For educational and demonstration purposes only. Always consult a qualified healthcare professional.
</div>
""", unsafe_allow_html=True)


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
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💊 Single Prediction",
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
        p_name      = st.text_input("Patient Name *", value="", placeholder="Required - e.g. John Doe")
        age         = st.number_input("Age", min_value=0, max_value=120, value=30)
        gender      = st.selectbox("Gender", ["Male", "Female"])
        temperature = st.number_input("🌡️ Temperature (°C)", min_value=30.0, max_value=45.0, value=36.5, step=0.1)
        heart_rate  = st.number_input("❤️ Heart Rate (bpm)", min_value=40, max_value=200, value=70)

    with col2:
        st.subheader("📋 Medical Details")
        blood_pressure = st.selectbox("🩸 Blood Pressure", ["Normal", "High", "Low"])
        symptoms       = st.text_area(
            "🤒 Symptoms (describe all symptoms)",
            placeholder="e.g. fever cough headache tiredness\nOr: chest pain breathlessness wheezing\nOr: nausea vomiting stomach pain diarrhea",
            height=110,
            help="Write all symptoms separated by spaces or commas. More symptoms = better prediction accuracy."
        )
        weight         = st.number_input("⚖️ Weight (kg)", min_value=1, max_value=200, value=60)
        allergies      = st.text_input("⚠️ Known Allergies", placeholder="e.g. Penicillin, Aspirin")
    # Symptom hint chips
    st.markdown("""
<div style="margin: -8px 0 12px; display:flex; flex-wrap:wrap; gap:6px;">
    <span style="font-size:0.75rem; color:#64748b; padding-top:4px;">Quick add:</span>
    <code style="background:rgba(0,255,200,0.08);border:1px solid rgba(0,255,200,0.2);border-radius:6px;padding:2px 8px;font-size:0.75rem;color:#00ffc8;cursor:pointer;">fever</code>
    <code style="background:rgba(0,255,200,0.08);border:1px solid rgba(0,255,200,0.2);border-radius:6px;padding:2px 8px;font-size:0.75rem;color:#00ffc8;">cough</code>
    <code style="background:rgba(0,255,200,0.08);border:1px solid rgba(0,255,200,0.2);border-radius:6px;padding:2px 8px;font-size:0.75rem;color:#00ffc8;">headache</code>
    <code style="background:rgba(0,255,200,0.08);border:1px solid rgba(0,255,200,0.2);border-radius:6px;padding:2px 8px;font-size:0.75rem;color:#00ffc8;">fatigue</code>
    <code style="background:rgba(0,255,200,0.08);border:1px solid rgba(0,255,200,0.2);border-radius:6px;padding:2px 8px;font-size:0.75rem;color:#00ffc8;">breathlessness</code>
    <code style="background:rgba(0,255,200,0.08);border:1px solid rgba(0,255,200,0.2);border-radius:6px;padding:2px 8px;font-size:0.75rem;color:#00ffc8;">nausea</code>
    <code style="background:rgba(0,255,200,0.08);border:1px solid rgba(0,255,200,0.2);border-radius:6px;padding:2px 8px;font-size:0.75rem;color:#00ffc8;">throat</code>
    <code style="background:rgba(0,255,200,0.08);border:1px solid rgba(0,255,200,0.2);border-radius:6px;padding:2px 8px;font-size:0.75rem;color:#00ffc8;">wheezing</code>
    <code style="background:rgba(0,255,200,0.08);border:1px solid rgba(0,255,200,0.2);border-radius:6px;padding:2px 8px;font-size:0.75rem;color:#00ffc8;">diarrhea</code>
    <code style="background:rgba(0,255,200,0.08);border:1px solid rgba(0,255,200,0.2);border-radius:6px;padding:2px 8px;font-size:0.75rem;color:#00ffc8;">rash</code>
    <code style="background:rgba(0,255,200,0.08);border:1px solid rgba(0,255,200,0.2);border-radius:6px;padding:2px 8px;font-size:0.75rem;color:#00ffc8;">joint pain</code>
    <code style="background:rgba(0,255,200,0.08);border:1px solid rgba(0,255,200,0.2);border-radius:6px;padding:2px 8px;font-size:0.75rem;color:#00ffc8;">chest pain</code>
</div>
""", unsafe_allow_html=True)
    if not MODEL_AVAILABLE:
        st.warning("Single prediction is disabled because the model file is unavailable.")
    elif st.button("🔍 Predict Diagnosis & Medicine", key="predict_btn"):
        if not p_name.strip():
            st.error("⚠️ Patient Name is compulsory. Please enter a valid name before predicting.")
            st.stop()
        if not symptoms.strip():
            st.error("⚠️ Symptoms are compulsory. Please enter at least one symptom before predicting.")
            st.stop()
            
        with st.spinner("🔄 Analyzing patient data..."):
            try:
                feature_order    = pipeline.get('feature_columns', TRAIN_INFO.get('feature_columns', []))
                symptom_keywords = pipeline.get('symptom_keywords', TRAIN_INFO.get('symptom_keywords', {}))
                symptom_flags    = pipeline.get('symptom_flags', TRAIN_INFO.get('symptom_flags', []))
                bp_mapping       = pipeline.get('bp_map', {'Low': 0, 'Normal': 1, 'High': 2})

                symptoms_lower = symptoms.lower().replace(',', ' ')

                # Symptom_Score
                symptom_score = sum(v for k, v in symptom_keywords.items() if k in symptoms_lower)
                if symptoms_lower.strip() and symptom_score == 0:
                    symptom_score = 1

                gender_encoded = 0 if gender == 'Male' else 1
                bp_encoded     = bp_mapping.get(blood_pressure, 1)

                # Build input row with all features
                raw = {
                    'Age':          float(age),
                    'Gender_enc':   float(gender_encoded),
                    'Temperature':  float(temperature),
                    'Heart_Rate':   float(heart_rate),
                    'BP_enc':       float(bp_encoded),
                    'Symptom_Score': float(symptom_score),
                }
                # Add individual symptom binary flags
                for flag in symptom_flags:
                    raw[f'sym_{flag}'] = 1 if flag in symptoms_lower else 0

                input_data = pd.DataFrame([raw])[feature_order]

                # Apply preprocessor if present
                preprocessor = pipeline.get('preprocessor')
                if preprocessor is not None:
                    try:
                        processed = preprocessor.transform(input_data)
                        if hasattr(processed, 'toarray'):
                            processed = processed.toarray()
                        processed_df = pd.DataFrame(processed, columns=feature_order)
                    except Exception as e:
                        st.warning(f"Preprocessing failed, using raw data: {e}")
                        processed_df = input_data
                else:
                    processed_df = input_data

                # Make prediction using the pipeline
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

                # ── Auto-save to medical history if patient name provided ──
                if p_name.strip():
                    try:
                        medicine_prescribed = details.get('medicine', medicine_mapping.get(prediction, ''))
                        # Check if patient already exists by name+age, else create
                        all_patients = db.get_all_patients()
                        existing = all_patients[
                            (all_patients['name'].str.lower() == p_name.strip().lower()) &
                            (all_patients['age'] == age)
                        ] if not all_patients.empty else pd.DataFrame()

                        if not existing.empty:
                            pid = int(existing.iloc[0]['patient_id'])
                        else:
                            pid = db.add_patient(p_name.strip(), age, gender)

                        db.add_diagnosis(
                            patient_id=pid,
                            symptoms=symptoms,
                            diagnosis=prediction,
                            temperature=temperature,
                            heart_rate=heart_rate,
                            blood_pressure=blood_pressure,
                            medicine=medicine_prescribed
                        )
                        st.success(f"📋 Visit saved to medical history for **{p_name}** (Patient ID: {pid})")
                    except Exception as db_err:
                        st.warning(f"Could not save to history: {db_err}")

            except Exception as e:
                st.error(f"❌ Prediction failed: {e}")
                import traceback
                st.code(traceback.format_exc())

# ===== TAB 2: Voice Input (Full Pipeline) =====
with tab2:
    st.header("🎤 Voice-to-Diagnosis Pipeline")
    st.markdown("""
<div class="card">
    <strong>🔊 Complete Voice Diagnosis</strong> — Speak your symptoms in Hindi or English.<br>
    The AI will <em>extract symptoms → run diagnosis → recommend medicine → speak the result</em> back to you.
</div>
""", unsafe_allow_html=True)

    # ── Patient info row ──────────────────────────────────────────────────
    st.subheader("👤 Patient Details")
    v_col1, v_col2, v_col3, v_col4 = st.columns(4)
    with v_col1:
        v_name = st.text_input("Name *", value="", placeholder="Required", key="voice_p_name")
    with v_col2:
        v_age = st.number_input("Age", min_value=0, max_value=120, value=30, key="voice_p_age")
    with v_col3:
        v_gender = st.selectbox("Gender", ["Male", "Female"], key="voice_p_gender")
    with v_col4:
        v_temp = st.number_input("Temperature (°C)", min_value=30.0, max_value=45.0, value=36.5, step=0.1, key="voice_p_temp")

    v_col5, v_col6 = st.columns(2)
    with v_col5:
        v_hr = st.number_input("Heart Rate (bpm)", min_value=40, max_value=200, value=70, key="voice_p_hr")
    with v_col6:
        v_bp = st.selectbox("Blood Pressure", ["Normal", "High", "Low"], key="voice_p_bp")

    st.divider()

    # ── Language + Recording ──────────────────────────────────────────────
    rec_col1, rec_col2 = st.columns([1, 2])
    with rec_col1:
        st.subheader("🗣️ Language")
        voice_language = st.radio("Choose language:", ["हिन्दी (Hindi)", "English"], key="voice_language")
        lang_code = "hi-IN" if "Hindi" in voice_language else "en-IN"
        speak_result = st.checkbox("🔊 Speak diagnosis aloud", value=True, key="voice_speak_result")

    with rec_col2:
        st.subheader("🎙️ Voice Recording")
        if st.button("🔴 Start Recording", key="start_voice_record"):
            st.info("🎤 Listening… Speak your symptoms clearly (up to 10 seconds)")
            try:
                transcript = voice.record_audio(language=lang_code, timeout=10)
                if transcript:
                    st.session_state.voice_transcript = transcript
                    st.session_state.voice_diagnosed = False
                else:
                    st.warning("Could not capture audio. Please try again.")
            except Exception as e:
                st.error(f"Error during voice recording: {e}")
                st.info("💡 Make sure your microphone is connected and working properly.")

        # Also allow typed input as fallback
        typed_symptoms = st.text_area(
            "Or type your symptoms here:",
            value=st.session_state.get("voice_transcript", ""),
            placeholder="e.g. I have fever and cough since 2 days",
            height=80,
            key="voice_typed_symptoms"
        )
        if typed_symptoms and typed_symptoms != st.session_state.get("voice_transcript", ""):
            st.session_state.voice_transcript = typed_symptoms

    # ── Process: Extract → Diagnose → Speak ───────────────────────────────
    transcript_text = st.session_state.get("voice_transcript", "")

    if transcript_text:
        st.divider()
        st.markdown(f"""
<div class="card">
    <strong>📝 Captured Input:</strong> <em>"{transcript_text}"</em>
</div>
""", unsafe_allow_html=True)

        # Step 1 — Symptom extraction
        detected_keywords = SymptomExtractor.extract_all(transcript_text)
        display_names = SymptomExtractor.display_symptoms(transcript_text)
        symptom_string = SymptomExtractor.symptom_text(transcript_text)

        if display_names:
            chips_html = " ".join(
                f'<code style="background:rgba(0,255,200,0.08);border:1px solid rgba(0,255,200,0.2);'
                f'border-radius:6px;padding:3px 10px;font-size:0.82rem;color:#00ffc8;margin:2px;">{s}</code>'
                for s in display_names
            )
            st.markdown(f"""
<div style="margin:8px 0 16px;">
    <span style="font-size:0.8rem;color:#64748b;font-weight:600;">DETECTED SYMPTOMS:</span><br>
    {chips_html}
</div>
""", unsafe_allow_html=True)
        else:
            st.info("ℹ️ No specific symptoms detected from keywords — the full text will be used for analysis.")

        # Step 2 — Run ML diagnosis
        if st.button("⚡ Diagnose from Voice Input", key="voice_diagnose_btn", type="primary"):
            if not v_name.strip():
                st.error("⚠️ Patient Name is compulsory. Please enter a valid name before diagnosing.")
            elif not symptom_string.strip() and not transcript_text.strip():
                st.error("⚠️ Symptoms are compulsory. Please provide voice input or type your symptoms.")
            elif not MODEL_AVAILABLE:
                st.error("⚠️ Trained model is not available. Please check the model file.")
            else:
                with st.spinner("🔄 Analyzing symptoms and running diagnosis…"):
                    try:
                        feature_order    = pipeline.get('feature_columns', TRAIN_INFO.get('feature_columns', []))
                        symptom_keywords = pipeline.get('symptom_keywords', TRAIN_INFO.get('symptom_keywords', {}))
                        symptom_flags    = pipeline.get('symptom_flags', TRAIN_INFO.get('symptom_flags', []))
                        bp_mapping       = pipeline.get('bp_map', {'Low': 0, 'Normal': 1, 'High': 2})

                        symptoms_lower = symptom_string.lower().replace(',', ' ')

                        # Symptom_Score
                        symptom_score = sum(v for k, v in symptom_keywords.items() if k in symptoms_lower)
                        if symptoms_lower.strip() and symptom_score == 0:
                            symptom_score = 1

                        gender_encoded = 0 if v_gender == 'Male' else 1
                        bp_encoded     = bp_mapping.get(v_bp, 1)

                        raw = {
                            'Age':           float(v_age),
                            'Gender_enc':    float(gender_encoded),
                            'Temperature':   float(v_temp),
                            'Heart_Rate':    float(v_hr),
                            'BP_enc':        float(bp_encoded),
                            'Symptom_Score': float(symptom_score),
                        }
                        for flag in symptom_flags:
                            raw[f'sym_{flag}'] = 1 if flag in symptoms_lower else 0

                        input_data = pd.DataFrame([raw])[feature_order]

                        # Preprocessor
                        preprocessor = pipeline.get('preprocessor')
                        if preprocessor is not None:
                            try:
                                processed = preprocessor.transform(input_data)
                                if hasattr(processed, 'toarray'):
                                    processed = processed.toarray()
                                processed_df = pd.DataFrame(processed, columns=feature_order)
                            except Exception:
                                processed_df = input_data
                        else:
                            processed_df = input_data

                        # Predict
                        raw_pred = pipeline['pipeline'].predict(processed_df)[0]

                        target_enc = pipeline.get('target_encoder')
                        if target_enc is not None and not isinstance(raw_pred, str):
                            prediction = target_enc.inverse_transform([int(raw_pred)])[0]
                        else:
                            prediction = str(raw_pred)

                        # Confidence
                        proba = None
                        if hasattr(pipeline['pipeline'], 'predict_proba'):
                            try:
                                proba = pipeline['pipeline'].predict_proba(processed_df)[0]
                            except Exception:
                                proba = None

                        # ── Display Results ─────────────────────────────────
                        st.divider()

                        # Medicine detail lookup
                        medicine_detail_db_voice = {
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

                        details = medicine_detail_db_voice.get(prediction, {})
                        severity = details.get("severity", "Low")
                        severity_icon = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(severity, "🟡")
                        badge_class = {"Low": "badge-low", "Medium": "badge-medium", "High": "badge-high"}.get(severity, "badge-medium")

                        st.markdown(f"""
<div class="card" style="border-top-color: {'#4ade80' if severity == 'Low' else '#fbbf24' if severity == 'Medium' else '#f87171'};">
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
        <span style="font-size:2rem;">{severity_icon}</span>
        <div>
            <div style="font-size:1.3rem;font-weight:800;color:#e2e8f0;">Diagnosis: {prediction}</div>
            <span class="badge {badge_class}">{severity} Severity</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

                        if v_name:
                            st.markdown(f"**Patient:** {v_name} | Age: {v_age} | Gender: {v_gender}")

                        # Vitals
                        vc1, vc2, vc3 = st.columns(3)
                        temp_status = "🔴 High" if v_temp > 37.5 else ("🟢 Normal" if v_temp >= 36.0 else "🔵 Low")
                        hr_status   = "🔴 High" if v_hr > 100 else ("🟢 Normal" if v_hr >= 60 else "🔵 Low")
                        bp_label    = {"Normal": "🟢 Normal", "High": "🔴 High", "Low": "🔵 Low"}.get(v_bp, v_bp)
                        vc1.metric("🌡️ Temperature", f"{v_temp}°C", temp_status)
                        vc2.metric("❤️ Heart Rate",  f"{v_hr} bpm", hr_status)
                        vc3.metric("🩸 Blood Pressure", v_bp, bp_label)

                        # Confidence chart
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
                                pass

                        # Medicine plan
                        st.divider()
                        if details:
                            st.subheader("💊 Medicine & Treatment Plan")
                            m1, m2 = st.columns(2)
                            with m1:
                                st.markdown(f"**💊 Medicines:** {details['medicine']}")
                                st.markdown(f"**⏰ Dosage:** {details['dosage']}")
                                st.markdown(f"**📅 Duration:** {details['duration']}")
                            with m2:
                                st.markdown(f"**⚠️ Precautions:** {details['precaution']}")
                                st.markdown(f"**👨‍⚕️ See a:** {details['specialist']}")
                        else:
                            st.info(f"💊 {medicine_mapping.get(prediction, 'Consult a doctor for personalized advice.')}")

                        # Severity-based care
                        st.divider()
                        if severity == "High":
                            st.error("🚨 HIGH SEVERITY — Visit a hospital immediately.")
                        elif severity == "Medium":
                            st.warning("⚠️ MEDIUM SEVERITY — Consult a doctor within 24 hours.")
                        else:
                            st.success("✅ LOW SEVERITY — Home care with rest and medicines should help.")

                        # ── Step 3: Voice Output ────────────────────────────
                        if speak_result:
                            tts_lang = "hi" if "Hindi" in voice_language else "en"
                            if tts_lang == "en":
                                speech_text = (
                                    f"Diagnosis: {prediction}. "
                                    f"Severity: {severity}. "
                                    f"Recommended medicine: {details.get('medicine', medicine_mapping.get(prediction, 'consult a doctor'))}. "
                                    f"Duration: {details.get('duration', 'as advised')}. "
                                    f"Precaution: {details.get('precaution', 'rest and stay hydrated')}."
                                )
                            else:
                                speech_text = (
                                    f"निदान: {prediction}. "
                                    f"गंभीरता: {severity}. "
                                    f"दवाई: {details.get('medicine', medicine_mapping.get(prediction, 'डॉक्टर से सलाह लें'))}."
                                )
                            try:
                                voice.text_to_speech(speech_text, language=tts_lang)
                            except Exception as tts_err:
                                st.warning(f"🔇 Could not play voice output: {tts_err}")

                        # ── Auto-save to history ────────────────────────────
                        if v_name.strip():
                            try:
                                medicine_prescribed = details.get('medicine', medicine_mapping.get(prediction, ''))
                                all_patients = db.get_all_patients()
                                existing = all_patients[
                                    (all_patients['name'].str.lower() == v_name.strip().lower()) &
                                    (all_patients['age'] == v_age)
                                ] if not all_patients.empty else pd.DataFrame()

                                if not existing.empty:
                                    pid = int(existing.iloc[0]['patient_id'])
                                else:
                                    pid = db.add_patient(v_name.strip(), v_age, v_gender)

                                db.add_diagnosis(
                                    patient_id=pid,
                                    symptoms=symptom_string,
                                    diagnosis=prediction,
                                    temperature=v_temp,
                                    heart_rate=v_hr,
                                    blood_pressure=v_bp,
                                    medicine=medicine_prescribed
                                )
                                st.success(f"📋 Visit saved to medical history for **{v_name}** (Patient ID: {pid})")
                            except Exception as db_err:
                                st.warning(f"Could not save to history: {db_err}")

                        st.session_state.voice_diagnosed = True

                    except Exception as e:
                        st.error(f"❌ Diagnosis failed: {e}")
                        import traceback
                        st.code(traceback.format_exc())

# ===== TAB 3: Health History =====
with tab3:
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
        
        with st.form("register_patient_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                pat_name = st.text_input("Full Name:", key="new_patient_name")
                pat_age = st.number_input("Age:", min_value=1, max_value=120, key="new_patient_age", value=1)
                pat_gender = st.selectbox("Gender:", ["Male", "Female", "Other"], key="new_patient_gender")
            
            with col2:
                pat_phone = st.text_input("Phone Number:", key="new_patient_phone")
                pat_email = st.text_input("Email (Optional):", key="new_patient_email")
                pat_location = st.text_input("Location:", key="new_patient_location")
            
            submitted = st.form_submit_button("✅ Register Patient")
            
        if submitted:
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

# ===== TAB 4: Model Insights =====
with tab4:
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

# ===== TAB 5: Find Nearby Doctors =====
with tab5:
    import requests as _requests
    import math
    from streamlit_geolocation import streamlit_geolocation

    st.header("🗺️ Find Nearby Doctors & Hospitals")
    st.markdown('<div class="card">Find real doctors, hospitals, clinics and pharmacies near your location using live OpenStreetMap data.</div>', unsafe_allow_html=True)

    def _haversine(lat1, lon1, lat2, lon2):
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2)**2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(R * c, 2)

    @st.cache_data(ttl=300, show_spinner=False)
    def fetch_doctors_osm(lat, lon, radius_m=5000):
        import math as _m
        def _hav(la1, lo1, la2, lo2):
            R = 6371.0
            dlat = _m.radians(la2-la1); dlon = _m.radians(lo2-lo1)
            a = _m.sin(dlat/2)**2 + _m.cos(_m.radians(la1))*_m.cos(_m.radians(la2))*_m.sin(dlon/2)**2
            return round(R*2*_m.atan2(_m.sqrt(a), _m.sqrt(1-a)), 2)

        overpass_url = "https://overpass-api.de/api/interpreter"

        def run_query(r):
            q = f"""
[out:json][timeout:30];
(
  node["amenity"="doctors"](around:{r},{lat},{lon});
  node["amenity"="hospital"](around:{r},{lat},{lon});
  node["amenity"="clinic"](around:{r},{lat},{lon});
  node["amenity"="pharmacy"](around:{r},{lat},{lon});
  node["amenity"="health_centre"](around:{r},{lat},{lon});
  node["amenity"="dentist"](around:{r},{lat},{lon});
  node["healthcare"="doctor"](around:{r},{lat},{lon});
  node["healthcare"="hospital"](around:{r},{lat},{lon});
  node["healthcare"="clinic"](around:{r},{lat},{lon});
  way["amenity"="hospital"](around:{r},{lat},{lon});
  way["amenity"="clinic"](around:{r},{lat},{lon});
  way["amenity"="health_centre"](around:{r},{lat},{lon});
  way["healthcare"="hospital"](around:{r},{lat},{lon});
);
out center tags;
"""
            resp = _requests.post(overpass_url, data={"data": q}, timeout=35)
            resp.raise_for_status()
            return resp.json().get("elements", [])

        tried_radii = [radius_m]
        if radius_m < 10000: tried_radii.append(10000)
        if radius_m < 20000: tried_radii.append(20000)

        elements = []; used_radius = radius_m; api_error = None
        for r in tried_radii:
            try:
                elements = run_query(r); used_radius = r
                if elements: break
            except _requests.exceptions.Timeout:
                api_error = "⏱️ Overpass API timed out. Try again."; break
            except _requests.exceptions.ConnectionError:
                api_error = "❌ No internet connection."; break
            except Exception as e:
                api_error = f"❌ API Error: {e}"; break

        if api_error:
            return [], api_error, used_radius

        results = []; seen = set()
        for el in elements:
            tags = el.get("tags", {})
            name = (tags.get("name") or tags.get("name:en") or
                    tags.get("operator") or tags.get("brand") or "Unknown Facility")
            if el["type"] == "node":
                elat, elon = el.get("lat"), el.get("lon")
            else:
                center = el.get("center", {})
                elat, elon = center.get("lat"), center.get("lon")
            if elat is None or elon is None: continue
            try: elat, elon = float(elat), float(elon)
            except (TypeError, ValueError): continue
            coord_key = (round(elat,5), round(elon,5))
            if coord_key in seen: continue
            seen.add(coord_key)
            amenity = tags.get("amenity") or tags.get("healthcare") or "clinic"
            phone = tags.get("phone") or tags.get("contact:phone") or tags.get("mobile") or "N/A"
            addr_parts = [tags.get("addr:housenumber",""), tags.get("addr:street",""), tags.get("addr:city","")]
            address = ", ".join(p for p in addr_parts if p) or tags.get("addr:full","N/A")
            dist = _hav(lat, lon, elat, elon)
            results.append({
                "name": name, "type": amenity.replace("_"," ").title(),
                "amenity_raw": amenity.lower(), "lat": elat, "lon": elon,
                "phone": phone, "address": address, "distance_km": dist,
                "opening_hours": tags.get("opening_hours","N/A"),
                "website": tags.get("website") or tags.get("contact:website","N/A"),
            })
        results.sort(key=lambda x: x["distance_km"])
        return results, None, used_radius

    # ── GPS Location ───────────────────────────────────────────────────────
    st.subheader("📍 Detect Your Location")
    st.caption("Allow browser location access to auto-detect your position.")
    location = streamlit_geolocation()
    gps_lat = location.get("latitude")  if location else None
    gps_lon = location.get("longitude") if location else None

    if not gps_lat or not gps_lon:
        st.warning("⚠️ Location not detected. Allow location access in your browser, or enter coordinates manually below.")
        mc1, mc2 = st.columns(2)
        with mc1:
            gps_lat = st.number_input("Latitude (manual)", value=28.7041, format="%.6f", key="manual_lat")
        with mc2:
            gps_lon = st.number_input("Longitude (manual)", value=77.1025, format="%.6f", key="manual_lon")
    else:
        st.success(f"✅ Location detected: **{gps_lat:.5f}, {gps_lon:.5f}**")

    st.divider()

    # ── Filters ────────────────────────────────────────────────────────────
    f1, f2, f3 = st.columns([1, 1, 1])
    with f1:
        max_distance_km = st.slider("Search Radius (km)", min_value=1, max_value=25, value=5, step=1)
    with f2:
        facility_filter = st.selectbox("Facility Type", ["All","Hospital","Clinic","Doctors","Pharmacy","Health Centre","Dentist"])
    with f3:
        show_test_data = st.checkbox("🧪 Test Mode (dummy markers)", value=False,
                                     help="Adds 3 dummy markers near you to verify map rendering.")

    if st.button("🔍 Search Nearby Healthcare", key="search_doctors_btn", type="primary"):
        with st.spinner(f"🔍 Searching OSM within {max_distance_km} km..."):
            results, api_err, used_r = fetch_doctors_osm(gps_lat, gps_lon, radius_m=max_distance_km*1000)
        st.session_state["doctor_results"] = results
        st.session_state["doctor_api_err"] = api_err
        st.session_state["doctor_used_r"]  = used_r
        st.session_state["doctor_lat"]     = gps_lat
        st.session_state["doctor_lon"]     = gps_lon

    if "doctor_results" in st.session_state:
        raw_results = st.session_state.get("doctor_results", [])
        api_err     = st.session_state.get("doctor_api_err")
        used_r      = st.session_state.get("doctor_used_r", max_distance_km*1000)
        s_lat       = st.session_state.get("doctor_lat", gps_lat)
        s_lon       = st.session_state.get("doctor_lon", gps_lon)

        if show_test_data:
            dummy = [
                {"name":"🧪 Test Hospital",  "type":"Hospital",  "amenity_raw":"hospital",
                 "lat":s_lat+0.010,"lon":s_lon+0.010,"phone":"N/A","address":"Near You",
                 "distance_km":_haversine(s_lat,s_lon,s_lat+0.010,s_lon+0.010),"opening_hours":"24/7","website":"N/A"},
                {"name":"🧪 Test Clinic",    "type":"Clinic",    "amenity_raw":"clinic",
                 "lat":s_lat-0.008,"lon":s_lon+0.005,"phone":"N/A","address":"Near You",
                 "distance_km":_haversine(s_lat,s_lon,s_lat-0.008,s_lon+0.005),"opening_hours":"9am-6pm","website":"N/A"},
                {"name":"🧪 Test Pharmacy",  "type":"Pharmacy",  "amenity_raw":"pharmacy",
                 "lat":s_lat+0.005,"lon":s_lon-0.010,"phone":"N/A","address":"Near You",
                 "distance_km":_haversine(s_lat,s_lon,s_lat+0.005,s_lon-0.010),"opening_hours":"8am-10pm","website":"N/A"},
            ]
            raw_results = dummy + raw_results

        if facility_filter != "All":
            kw = facility_filter.lower()
            filtered = [d for d in raw_results if kw in d["type"].lower() or kw in d["amenity_raw"]]
        else:
            filtered = list(raw_results)
        filtered.sort(key=lambda x: x["distance_km"])

        # ── Debug ──────────────────────────────────────────────────────────
        with st.expander("🛠️ Debug Info", expanded=(len(filtered)==0 and not show_test_data)):
            st.write(f"📍 Searched at: `{s_lat:.6f}, {s_lon:.6f}`")
            st.write(f"📏 Radius used: `{used_r/1000:.1f} km`")
            st.write(f"📦 Raw OSM results: `{len(raw_results)}`")
            st.write(f"🔎 After filter ({facility_filter}): `{len(filtered)}`")
            if api_err:
                st.error(api_err)
            elif len(raw_results) == 0:
                st.warning("OSM returned 0 results. Sparse map data in this area. Enable Test Mode to verify map works.")
            else:
                st.success(f"✅ OSM API OK — {len(raw_results)} facilities fetched.")
            if used_r > max_distance_km*1000:
                st.info(f"ℹ️ Radius auto-expanded to {used_r/1000:.0f} km (original had no results).")

        # ── Map + Category List ────────────────────────────────────────────
        map_col, list_col = st.columns([2, 1])

        with map_col:
            st.markdown("**🗺️ Live Map**")
            m = folium.Map(location=[s_lat, s_lon], zoom_start=14,
                           tiles="CartoDB positron", control_scale=True)
            folium.Marker(
                location=[s_lat, s_lon],
                popup=folium.Popup("<b>📌 You are here</b>", max_width=150),
                icon=folium.Icon(color="red", icon="home", prefix="fa"),
                tooltip="📌 Your Location"
            ).add_to(m)
            folium.Circle(
                location=[s_lat, s_lon], radius=used_r,
                color="#00ffc8", fill=True, fill_opacity=0.05,
                tooltip=f"Search radius: {used_r/1000:.1f} km"
            ).add_to(m)
            type_colors = {
                "hospital":"darkred","clinic":"cadetblue","doctors":"blue",
                "doctor":"blue","pharmacy":"orange","health centre":"purple","dentist":"green",
            }
            for doc in filtered:
                color = type_colors.get(doc["amenity_raw"], "darkblue")
                popup_html = f"""
<div style="font-family:Arial,sans-serif;min-width:200px;padding:4px;">
  <b style="font-size:14px;color:#0d47a1;">{doc['name']}</b><br>
  🏥 <b>Type:</b> {doc['type']}<br>
  📞 <b>Phone:</b> {doc['phone']}<br>
  📍 <b>Address:</b> {doc['address']}<br>
  🕐 <b>Hours:</b> {doc['opening_hours']}<br>
  <hr style="margin:5px 0;">
  <b style="color:#c62828;">📏 {doc['distance_km']} km away</b>
</div>"""
                folium.Marker(
                    location=[doc["lat"], doc["lon"]],
                    popup=folium.Popup(popup_html, max_width=300),
                    icon=folium.Icon(color=color, icon="plus-sign"),
                    tooltip=f"🏥 {doc['name']} ({doc['distance_km']} km)"
                ).add_to(m)
            st_folium(m, width="100%", height=500, key="doctor_map_v3")

        with list_col:
            st.markdown("**📋 Results by Category**")
            if not filtered:
                st.warning("No nearby doctors found.")
                st.info("💡 Try:\n- Increasing the radius\n- Enabling Test Mode\n- Checking internet connection")
            else:
                categories = {
                    "🏥 Hospitals":      ["hospital"],
                    "🩺 Doctors":        ["doctors","doctor"],
                    "🏨 Clinics":        ["clinic"],
                    "💊 Pharmacies":     ["pharmacy"],
                    "🦷 Dentists":       ["dentist"],
                    "🏪 Health Centres": ["health centre","health_centre"],
                }
                shown = set()
                for cat_label, cat_keys in categories.items():
                    cat_items = [d for d in filtered
                                 if any(k in d["amenity_raw"] or k in d["type"].lower() for k in cat_keys)]
                    if not cat_items: continue
                    st.markdown(f"""
<div style="background:rgba(0,255,200,0.06);border:1px solid rgba(0,255,200,0.2);
border-radius:10px;padding:10px 14px;margin:8px 0;">
<div style="font-size:0.85rem;font-weight:700;color:#00ffc8;margin-bottom:8px;">{cat_label} ({len(cat_items)})</div>
""", unsafe_allow_html=True)
                    for d in cat_items[:8]:
                        shown.add(d["name"])
                        ph = f"📞 {d['phone']}" if d['phone'] != 'N/A' else ""
                        st.markdown(f"""
<div style="padding:8px 10px;margin:4px 0;background:rgba(255,255,255,0.03);
border-radius:8px;border-left:3px solid rgba(0,255,200,0.3);">
<div style="font-size:0.85rem;font-weight:600;color:#e2e8f0;">{d['name']}</div>
<div style="font-size:0.75rem;color:#64748b;">📏 {d['distance_km']} km &nbsp;{ph}</div>
</div>""", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                others = [d for d in filtered if d["name"] not in shown]
                if others:
                    st.markdown("""
<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);
border-radius:10px;padding:10px 14px;margin:8px 0;">
<div style="font-size:0.85rem;font-weight:700;color:#94a3b8;margin-bottom:8px;">🏪 Other</div>
""", unsafe_allow_html=True)
                    for d in others[:5]:
                        st.markdown(f"""
<div style="padding:8px 10px;margin:4px 0;background:rgba(255,255,255,0.02);border-radius:8px;">
<div style="font-size:0.85rem;font-weight:600;color:#e2e8f0;">{d['name']}</div>
<div style="font-size:0.75rem;color:#64748b;">📏 {d['distance_km']} km | {d['type']}</div>
</div>""", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

        # ── Full table ─────────────────────────────────────────────────────
        if filtered:
            st.divider()
            st.subheader(f"📊 All {len(filtered)} Results — Sorted by Distance")
            nearest = filtered[0]
            st.success(f"🏆 Nearest: **{nearest['name']}** ({nearest['type']}) — {nearest['distance_km']} km | 📞 {nearest['phone']}")
            df_show = pd.DataFrame(filtered)[["name","type","distance_km","phone","address","opening_hours"]]
            df_show.columns = ["Name","Type","Distance (km)","Phone","Address","Opening Hours"]
            st.dataframe(df_show, use_container_width=True)

            st.divider()
            st.subheader("💡 Specialist Recommendation by Diagnosis")
            sel_diag = st.selectbox("Select diagnosis", list(medicine_mapping.keys()), key="diag_recommend")
            rec_spec = SpecialtyMatcher.get_matching_specialties(sel_diag)
            st.info(f"Recommended specialties for **{sel_diag}**: {', '.join(rec_spec)}")

# ===== TAB 6: Medicine Guide =====
with tab6:
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