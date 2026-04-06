# 🏥 Early Disease Prediction System

An AI-powered healthcare diagnosis system for early disease detection and prediction. It combines machine learning, OpenAI GPT, and interactive maps to help predict diseases and locate nearby doctors.

---

## 🌟 Features

| Feature | Description |
|---|---|
| 💊 Single Prediction | ML-based diagnosis from patient vitals |
| 📊 Batch Prediction | Upload CSV for multiple patient predictions |
| 🎤 Voice Input | Speak symptoms in Hindi or English |
| 📋 Health History | SQLite-backed patient record management |
| 🤖 AI Advisor | OpenAI GPT-3.5 powered medical advice |
| 📈 Model Insights | Feature importance & diagnosis mapping |
| 🗺️ Find Doctors | Interactive map to locate nearby doctors |
| 💉 Medicine Guide | Searchable medicine & treatment reference |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Clone the repo
git clone https://github.com/adilkhan1234556/ai-health-project.git
cd ai-health-project

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Configuration (Optional — for AI Advisor)

Edit `config/openai_config.py` and replace the placeholder with your OpenAI API key:

```python
OPENAI_API_KEY = "sk-your-actual-openai-api-key-here"
```

> ⚠️ Never commit a real API key. The config file is kept as a template only.

### Run the App

```bash
streamlit run app.py
```

---

## 🤖 Tech Stack

- **Framework:** Streamlit
- **ML:** scikit-learn, XGBoost, joblib
- **AI:** OpenAI GPT-3.5-turbo
- **Data:** Pandas, NumPy
- **Visualization:** Plotly, Matplotlib, Folium
- **Database:** SQLite

---

## 📁 Project Structure

```
├── app.py                  # Main Streamlit app
├── app_features_new.py     # Supplemental feature implementations
├── config/
│   └── openai_config.py    # OpenAI API key template
├── database/
│   └── patient_history.py  # SQLite patient history manager
├── features/
│   ├── ai_advisor.py       # OpenAI medical advisor
│   ├── doctor_finder.py    # Location-based doctor finder
│   └── voice_input.py      # Voice/speech recognition
├── model/
│   ├── final_pipeline.joblib  # Trained ML pipeline
│   └── training_artifacts_info.json
├── dataset/
│   └── health_dataset.csv  # Training dataset
└── requirements.txt
```

---

## ⚠️ Disclaimer

This application is for **educational and demonstration purposes only**. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional.
