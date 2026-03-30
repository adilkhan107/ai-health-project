"""
AI Medical Advisor - OpenAI Integration
Provides intelligent medical advice, medicine recommendations, and doctor suggestions
using OpenAI's GPT models with patient history learning
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import streamlit as st # type: ignore
from openai import OpenAI # type: ignore

class AIMedicalAdvisor:
    """AI-powered medical advisor using OpenAI"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI client"""
        # Try to load API key from config file if not provided
        if not api_key:
            try:
                from config.openai_config import OPENAI_API_KEY
                api_key = OPENAI_API_KEY
            except ImportError:
                api_key = None

        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            st.warning("⚠️ OpenAI API key not found. Please configure OPENAI_API_KEY in config/openai_config.py or provide it directly.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)

        # Medical knowledge base for context
        self.medical_context = """
        You are an AI Medical Assistant for rural healthcare in India. You provide preliminary medical advice,
        medicine suggestions, and doctor recommendations based on patient symptoms and history.

        IMPORTANT GUIDELINES:
        1. Always emphasize that you're not a replacement for professional medical care
        2. Suggest consulting doctors for serious conditions
        3. Provide general medicine suggestions based on common practices
        4. Consider Indian healthcare context and availability of medicines
        5. Be culturally sensitive and use simple language
        6. Learn from patient history to provide personalized recommendations

        COMMON INDIAN MEDICINES AND PRACTICES:
        - Paracetamol for fever/pain
        - ORS for dehydration
        - Antibiotics like Amoxicillin for bacterial infections
        - Antacids for stomach issues
        - Ayurvedic options when appropriate
        - Consider affordability and availability in rural areas
        """

    def analyze_patient_data(self, patient_data: Dict, medical_history: List[Dict] = None) -> Dict:
        """
        Analyze patient data and provide comprehensive medical advice

        Args:
            patient_data: Current patient information
            medical_history: Previous medical records

        Returns:
            Dict containing diagnosis, medicine advice, and doctor recommendations
        """
        if not self.client:
            return {
                "error": "OpenAI API key not configured",
                "diagnosis": "Unable to analyze - API key missing",
                "medicine_advice": "Please configure OpenAI API key",
                "doctor_suggestion": "General Practitioner",
                "urgency_level": "Unknown"
            }

        try:
            # Build comprehensive patient profile
            patient_profile = self._build_patient_profile(patient_data, medical_history)

            # Get AI analysis
            analysis = self._get_ai_analysis(patient_profile)

            return analysis

        except Exception as e:
            return {
                "error": f"Analysis failed: {str(e)}",
                "diagnosis": "Analysis error",
                "medicine_advice": "Consult a doctor",
                "doctor_suggestion": "General Practitioner",
                "urgency_level": "High"
            }

    def _build_patient_profile(self, patient_data: Dict, medical_history: List[Dict] = None) -> str:
        """Build comprehensive patient profile for AI analysis"""
        profile = f"""
        CURRENT PATIENT INFORMATION:
        - Name: {patient_data.get('name', 'Unknown')}
        - Age: {patient_data.get('age', 'Unknown')}
        - Gender: {patient_data.get('gender', 'Unknown')}
        - Temperature: {patient_data.get('temperature', 'Unknown')}°C
        - Heart Rate: {patient_data.get('heart_rate', 'Unknown')} bpm
        - Blood Pressure: {patient_data.get('blood_pressure', 'Unknown')}
        - Symptoms: {patient_data.get('symptoms', 'Unknown')}
        - Location: {patient_data.get('location', 'Rural India')}

        """

        if medical_history:
            profile += "\nMEDICAL HISTORY:\n"
            for record in medical_history[-5:]:  # Last 5 records
                profile += f"""
                - Date: {record.get('date', 'Unknown')}
                - Symptoms: {record.get('symptoms', 'Unknown')}
                - Diagnosis: {record.get('diagnosis', 'Unknown')}
                - Medicine: {record.get('medicine_prescribed', 'Unknown')}
                - Notes: {record.get('doctor_notes', 'None')}
                """

        return profile

    def _get_ai_analysis(self, patient_profile: str) -> Dict:
        """Get AI-powered medical analysis"""

        prompt = f"""
        {self.medical_context}

        PATIENT PROFILE:
        {patient_profile}

        Based on the above patient information, please provide:

        1. **PRELIMINARY DIAGNOSIS**: What could be the likely condition?
        2. **MEDICINE RECOMMENDATIONS**: Suggest appropriate medicines/treatments (consider Indian market availability)
        3. **URGENCY LEVEL**: How urgent is medical attention needed? (Low/Medium/High/Critical)
        4. **DOCTOR SPECIALTY**: Which type of doctor should they consult?
        5. **ADDITIONAL ADVICE**: Any lifestyle/dietary recommendations or precautions
        6. **FOLLOW-UP**: When should they seek follow-up care?

        Format your response as a JSON object with keys: diagnosis, medicine_advice, urgency_level, doctor_suggestion, additional_advice, follow_up
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a medical AI assistant. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )

            # Parse JSON response
            result_text = response.choices[0].message.content.strip()

            # Clean up response if it has markdown formatting
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]

            result = json.loads(result_text.strip())

            return {
                "diagnosis": result.get("diagnosis", "Unable to determine"),
                "medicine_advice": result.get("medicine_advice", "Consult a doctor"),
                "urgency_level": result.get("urgency_level", "Medium"),
                "doctor_suggestion": result.get("doctor_suggestion", "General Practitioner"),
                "additional_advice": result.get("additional_advice", "Rest and monitor symptoms"),
                "follow_up": result.get("follow_up", "Within 1-2 days if symptoms persist")
            }

        except Exception as e:
            return {
                "diagnosis": "Analysis failed",
                "medicine_advice": "Please consult a healthcare professional",
                "urgency_level": "Medium",
                "doctor_suggestion": "General Practitioner",
                "additional_advice": f"Error in analysis: {str(e)}",
                "follow_up": "Seek medical attention promptly"
            }

    def get_medicine_suggestions(self, diagnosis: str, patient_age: int, patient_location: str = "Rural India") -> List[str]:
        """Get medicine suggestions based on diagnosis and patient factors"""
        if not self.client:
            return ["Consult a doctor for personalized medicine recommendations"]

        prompt = f"""
        Suggest appropriate medicines for: {diagnosis}
        Patient age: {patient_age}
        Location: {patient_location} (consider medicine availability)

        Provide 3-5 medicine options with dosages, considering:
        - Age-appropriate dosing
        - Common availability in Indian pharmacies
        - Affordability for rural patients
        - Both allopathic and ayurvedic options if suitable

        Format as a list of medicine recommendations.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.2
            )

            suggestions = response.choices[0].message.content.strip().split('\n')
            return [s.strip('- •').strip() for s in suggestions if s.strip()]

        except Exception:
            return ["Paracetamol 500mg (as needed for fever/pain)",
                   "Consult local pharmacist for appropriate medicines"]

    def suggest_doctor_specialty(self, symptoms: str, diagnosis: str = None) -> Dict:
        """Suggest appropriate doctor specialty based on symptoms"""
        if not self.client:
            return {"specialty": "General Practitioner", "reason": "Default recommendation"}

        prompt = f"""
        For symptoms: {symptoms}
        Preliminary diagnosis: {diagnosis or 'Unknown'}

        Suggest the most appropriate doctor specialty and explain why.
        Consider specialties available in rural Indian healthcare settings.

        Format as JSON: {{"specialty": "Specialty Name", "reason": "Explanation"}}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.2
            )

            result_text = response.choices[0].message.content.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]

            return json.loads(result_text.strip())

        except Exception:
            return {"specialty": "General Practitioner", "reason": "General healthcare needs"}

    def predict_diagnosis(self, patient_data: Dict, medical_history: List[Dict] = None) -> Dict:
        """
        Use OpenAI to predict diagnosis directly (alternative to ML model)

        Args:
            patient_data: Current patient information
            medical_history: Previous medical records

        Returns:
            Dict containing diagnosis prediction and confidence
        """
        if not self.client:
            return {
                "diagnosis": "AI Prediction Unavailable",
                "confidence": 0.0,
                "reasoning": "OpenAI API key not configured",
                "alternative_suggestions": ["Consult ML model prediction", "See a doctor"]
            }

        try:
            # Build patient profile
            patient_profile = self._build_patient_profile(patient_data, medical_history)

            prompt = f"""
            {self.medical_context}

            PATIENT PROFILE:
            {patient_profile}

            Based on the patient information above, predict the most likely diagnosis.

            Consider these common conditions in rural Indian healthcare:
            - Common Cold
            - Viral Fever
            - Pneumonia
            - Flu
            - Food Poisoning
            - Dengue (Mild)
            - Bronchitis
            - Fatigue
            - Throat Infection
            - Other conditions as appropriate

            Provide your response in this exact JSON format:
            {{
                "diagnosis": "Your predicted diagnosis",
                "confidence": 0.0 to 1.0 (your confidence level),
                "reasoning": "Brief explanation of your diagnosis",
                "differential_diagnoses": ["Alternative diagnosis 1", "Alternative diagnosis 2"]
            }}
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a medical AI specializing in diagnosis prediction. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.2  # Lower temperature for more consistent predictions
            )

            result_text = response.choices[0].message.content.strip()

            # Clean up response
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]

            result = json.loads(result_text.strip())

            return {
                "diagnosis": result.get("diagnosis", "Unable to determine"),
                "confidence": float(result.get("confidence", 0.5)),
                "reasoning": result.get("reasoning", "AI analysis completed"),
                "differential_diagnoses": result.get("differential_diagnoses", [])
            }

        except Exception as e:
            return {
                "diagnosis": "Prediction Error",
                "confidence": 0.0,
                "reasoning": f"Error in AI prediction: {str(e)}",
                "differential_diagnoses": ["Consult healthcare professional"]
            }

    def learn_from_feedback(self, patient_data: Dict, ai_advice: Dict, actual_outcome: str):
        """Learn from feedback to improve future recommendations"""
        # This could be extended to store learning data for future model fine-tuning
        # For now, we'll just log the feedback
        feedback_data = {
            "timestamp": datetime.now().isoformat(),
            "patient_data": patient_data,
            "ai_advice": ai_advice,
            "actual_outcome": actual_outcome,
            "learned": True
        }

        # In a production system, this would be stored in a database
        # For now, we'll just return the feedback data
        return feedback_data