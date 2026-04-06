"""
Enhanced Rural Healthcare App - New Feature Implementations
Add these tab implementations to the main app.py
"""

# ===== TAB 3: Voice Input =====
def voice_input_tab(voice, symptom_extractor, db, medicine_mapping, pipeline, FEATURE_COLUMNS, RAW_FEATURE_COLUMNS):
    """Voice input capability for patient symptoms"""
    st.header("🎤 Voice Input Diagnosis")
    st.markdown('<div class="card">Speak your symptoms in Hindi or English for instant diagnosis.</div>', unsafe_allow_html=True)
    
    # Language selection
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("🗣️ Language")
        language = st.radio("Choose language:", ["हिन्दी (Hindi)", "English"], key="voice_language")
        lang_code = "hi-IN" if "Hindi" in language else "en-IN"
    
    with col2:
        st.subheader("🎙️ Voice Recording")
        if st.button("🔴 Start Recording", key="start_voice_record"):
            st.info("Listening... Speak your symptoms clearly")
            try:
                transcript = voice.record_audio(language=lang_code, timeout=10)
                if transcript:
                    st.success(f"✅ Recorded: {transcript}")
                    
                    # Extract symptoms from speech
                    extracted_symptom = symptom_extractor.extract(transcript)
                    st.write(f"**Detected Symptom:** {extracted_symptom if extracted_symptom else 'Could not detect symptom'}")
                    
                    # Store in database
                    patient_name = st.text_input("Patient Name", key="voice_patient_name")
                    patient_age = st.number_input("Patient Age", min_value=1, max_value=120, key="voice_patient_age")
                    
                    if st.button("Save to History & Analyze", key="save_voice_record"):
                        # Add to database
                        patient_id = db.add_patient(patient_name, patient_age, "Not specified")
                        st.success(f"✅ Patient #{patient_id} added to history")
                        
                        # Perform diagnosis if all symptoms are available
                        st.info("💡 Voice input saved. Use Single Prediction tab for detailed diagnosis.")
            except Exception as e:
                st.error(f"Error during voice recording: {e}")
                st.info("💡 Make sure your microphone is connected and permission is granted")


# ===== TAB 4: Health History =====
def health_history_tab(db):
    """Patient health history tracking"""
    st.header("📋 Health History & Patient Records")
    st.markdown('<div class="card">View and manage patient medical history for informed diagnosis.</div>', unsafe_allow_html=True)
    
    tab_view, tab_add, tab_export = st.tabs(["👁️ View History", "➕ Add Patient", "📥 Export History"])
    
    with tab_view:
        st.subheader("Search Patient Records")
        
        search_type = st.radio("Search by:", ["Patient ID", "Phone Number"], key="history_search_type")
        
        if search_type == "Patient ID":
            patient_id = st.number_input("Enter Patient ID:", min_value=1, key="search_patient_id")
            if st.button("Search", key="search_btn_id"):
                patient = db.get_patient(patient_id)
                if patient:
                    st.success(f"✅ Patient Found: {patient['name']}")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Age", patient['age'])
                    with col2:
                        st.metric("Gender", patient['gender'])
                    with col3:
                        st.metric("Contact", patient['phone'])
                    
                    st.divider()
                    st.subheader("📊 Medical History")
                    history = db.get_patient_history(patient_id)
                    
                    if history:
                        for record in history:
                            with st.expander(f"🏥 Visit on {record['visit_date']}"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Symptoms:** {record['symptoms']}")
                                    st.write(f"**Diagnosis:** {record['diagnosis']}")
                                with col2:
                                    st.write(f"**Temperature:** {record['temperature']}°C")
                                    st.write(f"**Heart Rate:** {record['heart_rate']} bpm")
                                st.write(f"**BP:** {record['blood_pressure']}")
                                st.write(f"**Medicine:** {record['medicine']}")
                    else:
                        st.info("No medical history records found for this patient.")
                else:
                    st.warning(f"Patient #{patient_id} not found in records.")
        
        else:  # Phone search
            phone = st.text_input("Enter Phone Number:", key="search_phone")
            if st.button("Search", key="search_btn_phone"):
                patient_id = db.search_patient_by_phone(phone)
                if patient_id:
                    st.info(f"Found Patient ID: {patient_id}")
                    st.rerun()
                else:
                    st.warning(f"No patient found with phone: {phone}")
    
    with tab_add:
        st.subheader("Register New Patient")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name:", key="new_patient_name")
            age = st.number_input("Age:", min_value=1, max_value=120, key="new_patient_age")
            gender = st.selectbox("Gender:", ["Male", "Female", "Other"], key="new_patient_gender")
        
        with col2:
            phone = st.text_input("Phone Number:", key="new_patient_phone")
            email = st.text_input("Email (Optional):", key="new_patient_email")
            location = st.text_input("Location:", key="new_patient_location")
        
        if st.button("✅ Register Patient", key="register_btn"):
            patient_id = db.add_patient(name, age, gender, phone, email, location)
            st.success(f"✅ Patient registered successfully! Patient ID: {patient_id}")
            st.balloons()
    
    with tab_export:
        st.subheader("Export Patient History")
        
        patient_id = st.number_input("Enter Patient ID to Export:", min_value=1, key="export_patient_id")
        
        if st.button("📥 Export as CSV", key="export_btn"):
            try:
                filename = db.export_patient_history_csv(patient_id)
                st.success(f"✅ History exported to {filename}")
                
                with open(filename, 'rb') as f:
                    st.download_button(
                        label="Download CSV File",
                        data=f.read(),
                        file_name=filename,
                        mime="text/csv"
                    )
            except Exception as e:
                st.error(f"Error exporting history: {e}")


# ===== TAB 7: Medicine Guide =====
def medicine_guide_tab(medicine_mapping):
    """Comprehensive medicine recommendation guide"""
    st.header("💉 Medicine & Treatment Guide")
    st.markdown('<div class="card">Complete reference guide for medicines suggested by the AI model.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search medicine or condition:", placeholder="e.g., Pneumonia, Aspirin")
    
    with col2:
        sort_by = st.selectbox("Sort by:", ["Alphabetical", "Most Common", "Severity"])
    
    st.divider()
    
    # Create medicine database
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
            "precaution": "Complete antibiotics course, chest physiotherapy",
            "severity": "High"
        },
        "Flu": {
            "medicine": "Rest, Warm Fluids, Vitamin C, Antiviral",
            "dosage": "As per symptoms",
            "duration": "7-10 days",
            "precaution": "Vaccination recommended, isolation recommended",
            "severity": "Medium"
        },
        "Food Poisoning": {
            "medicine": "ORS, Antibiotics, Avoid Oily Food",
            "dosage": "ORS every 30-60 minutes",
            "duration": "2-4 days",
            "precaution": "Hydration essential, bland diet",
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
            "medicine": "Salt Water Gargle, Throat Lozenges, Antibiotics if Bacterial",
            "dosage": "Gargle 3-4 times daily",
            "duration": "5-7 days",
            "precaution": "Avoid spicy food, take warm liquids",
            "severity": "Low"
        }
    }
    
    # Filter based on search
    if search_term:
        filtered_meds = {k: v for k, v in medicine_db.items() 
                        if search_term.lower() in k.lower() or search_term.lower() in v['medicine'].lower()}
    else:
        filtered_meds = medicine_db
    
    # Display medicine guide
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
                st.write(f"**🔴 Severity:** {details['severity']}")
            
            st.write("**Note:** Always consult a healthcare professional before starting any medicine.")
    
    st.divider()
    
    st.info("""
    **⚕️ Important Disclaimer:**
    - This medicine guide is for informational purposes only
    - Always consult a qualified healthcare professional before taking medicines
    - Follow the prescription and dosage given by your doctor
    - Report any side effects immediately
    - Keep medicines away from children
    """)

