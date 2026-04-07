# 🏥 HealthPredict AI — Early Disease Prediction System

> *"No patient should die because they couldn't reach a doctor."*

An AI-powered rural healthcare web app that predicts diseases, guides medicine use, tracks patient history, and locates nearby doctors — all in one place, supporting **Hindi & English**.

Built for **Hackathon 2026 | Rural Healthcare Track**

---

## 🌟 Features

| Feature | Description |
|---|---|
| 💊 Disease Prediction | Enter vitals & symptoms → AI predicts disease + medicine + dosage |
| 🎤 Voice Input | Speak symptoms in Hindi or English → instant diagnosis + voice output |
| 📋 Patient History | Store & retrieve patient records in local SQLite database |
| 📈 Model Insights | AI accuracy, confidence chart, feature importance visualization |
| 🗺️ Find Doctors | Real-time nearby hospitals/clinics via OpenStreetMap (no API key needed) |
| 💉 Medicine Guide | Searchable medicine reference with dosage, duration & precautions |

---

## 🤖 How the AI Works

- **Model:** Random Forest Classifier (500 trees) + SMOTE oversampling
- **Features:** Age, Gender, Temperature, Heart Rate, Blood Pressure + 40 symptom binary flags
- **Diseases:** 9 common rural diseases (Common Cold, Viral Fever, Pneumonia, Flu, Food Poisoning, Dengue, Bronchitis, Fatigue, Throat Infection)
- **Accuracy:** 95% on test set
- **Dataset:** 100 patient records (`server/dataset/health_dataset.csv`)

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Clone the repo
git clone https://github.com/your-username/healthpredict-ai.git
cd healthpredict-ai

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r server/requirements.txt
```

### Run the App

```bash
streamlit run app.py
```

Open browser at **http://localhost:8501**

---

## 🧠 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend/Backend** | Streamlit (Python) |
| **ML Model** | Scikit-learn — Random Forest |
| **Oversampling** | imbalanced-learn (SMOTE) |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Plotly, Matplotlib, Folium |
| **Database** | SQLite (local, no server needed) |
| **Voice Input** | SpeechRecognition + Google Speech API |
| **Voice Output** | gTTS (Google Text-to-Speech) |
| **Maps** | OpenStreetMap + Overpass API (free) |
| **Location** | streamlit-geolocation |

> ✅ **100% Free & Open Source** — No paid APIs, no cloud cost, ₹0 deployment

---

## 📁 Project Structure

```
├── app.py                          # Main Streamlit app (UI + logic)
├── server/
│   ├── model/
│   │   ├── final_pipeline.joblib   # Trained ML model
│   │   ├── model_train.py          # Model training script
│   │   ├── metrics.json            # Model accuracy & report
│   │   └── training_artifacts_info.json
│   ├── dataset/
│   │   └── health_dataset.csv      # Training dataset (100 rows, 9 diseases)
│   ├── database/
│   │   ├── patient_history.py      # SQLite patient history manager
│   │   └── patient_history.db      # Local database file
│   ├── features/
│   │   ├── voice_input.py          # Voice recording & TTS
│   │   └── doctor_finder.py        # Specialty matcher
│   └── requirements.txt
└── README.md
```

---

## 🩺 Supported Diseases

| Disease | Severity | Specialist |
|---|---|---|
| Common Cold | 🟢 Low | General Practitioner |
| Viral Fever | 🟡 Medium | General Practitioner |
| Flu | 🟡 Medium | General Practitioner |
| Bronchitis | 🟡 Medium | Pulmonologist |
| Food Poisoning | 🟡 Medium | Gastroenterologist |
| Dengue (Mild) | 🔴 High | Infectious Disease |
| Pneumonia | 🔴 High | Pulmonologist |
| Fatigue | 🟢 Low | General Practitioner |
| Throat Infection | 🟢 Low | ENT Specialist |

---

## 🗺️ Doctor Finder — How it Works

1. Browser detects your GPS location
2. App sends 3 split queries to Overpass API (OpenStreetMap)
3. Results shown on live Folium map with color-coded markers
4. Category-wise list: Hospitals, Clinics, Doctors, Pharmacies, Dentists
5. Auto-expands radius if no results found
6. Fallback data shown if API times out (504 handled)

---

## 🔮 Future Scope

- Add Malaria, TB, Diabetes, Hypertension detection
- Offline mode for no-internet villages
- WhatsApp Bot for feature phones
- Ayushman Bharat / ABHA health ID integration
- Android / iOS mobile app
- Real-time disease outbreak alert system
- Wearable device (BP monitor, pulse oximeter) integration
- Multi-language support (Tamil, Telugu, Bengali, Marathi)

---

## 📊 Why This Project is Different

| Feature | Other Apps | HealthPredict AI |
|---|---|---|
| Hindi Voice Diagnosis | ❌ | ✅ |
| Offline ML Prediction | ❌ | ✅ |
| Patient History Tracking | ❌ | ✅ |
| Real-time Doctor Finder | ❌ | ✅ |
| Zero Cost Deployment | ❌ | ✅ |
| All-in-One Platform | ❌ | ✅ |

---

## ⚠️ Disclaimer

This application is for **educational and demonstration purposes only**. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional.

---

## 📚 References

- WHO Rural Health Report 2023 — [who.int](https://who.int)
- NITI Aayog Health Index 2022 — [niti.gov.in](https://niti.gov.in)
- National Health Mission — [nhm.gov.in](https://nhm.gov.in)
- OpenStreetMap / Overpass API — [overpass-api.de](https://overpass-api.de)
- Scikit-learn — [scikit-learn.org](https://scikit-learn.org)
- Inspired by: PM-JAY, eSanjeevani, WHO SDG Goal 3
