"""
Voice Input Module - Hindi & English Speech Recognition
Supports voice input for patient symptoms and diagnosis queries
"""

import speech_recognition as sr
import pyttsx3
from typing import Optional, Tuple
import streamlit as st

class VoiceInput:
    """Handle voice input and text-to-speech conversion"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speech rate

        # Microphone dependency: PyAudio is optional in environments without mic support
        try:
            import pyaudio  # noqa: F401
            self.pyaudio_available = True
        except Exception:
            self.pyaudio_available = False
    
    def record_audio(self, language: str = "hi-IN", timeout: int = 10) -> Optional[str]:
        """
        Record audio from microphone and convert to text
        
        Args:
            language: 'hi-IN' for Hindi, 'en-IN' for English
            timeout: Maximum seconds to wait for input
            
        Returns:
            Transcribed text or None if failed
        """
        if not getattr(self, 'pyaudio_available', False):
            st.error(
                "❌ PyAudio is not installed or not available. Please install PyAudio and restart the app. "
                "On Windows: `pip install pipwin` then `pipwin install pyaudio`, or download wheel from "
                "https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio`")
            return None

        try:
            with sr.Microphone() as source:
                st.info(f"🎤 Listening in {('Hindi' if 'hi' in language else 'English')}... (say something within {timeout}s)")
                audio = self.recognizer.listen(source, timeout=timeout)
            
            # Use Google Speech Recognition
            text = self.recognizer.recognize_google(audio, language=language)
            return text
            
        except sr.UnknownValueError:
            st.error("❌ Sorry, could not understand the audio. Please try again.")
            return None
        except sr.RequestError as e:
            st.error(f"❌ Error with speech recognition service: {e}")
            return None
        except Exception as e:
            st.error(f"❌ Error recording audio: {e}")
            return None
    
    def text_to_speech(self, text: str, language: str = "hi") -> None:
        """
        Convert text to speech
        
        Args:
            text: Text to convert to speech
            language: Language code ('hi' or 'en')
        """
        try:
            # For Hindi, we use a simple TTS (pyttsx3 has limited Hindi support)
            if language == "hi":
                st.info(f"🔊 Playing result in Hindi...")
            else:
                st.info(f"🔊 Playing result in English...")
            
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            st.error(f"Error in text-to-speech: {e}")
    
    def record_symptoms(self) -> Optional[str]:
        """Record patient symptoms via voice"""
        st.write("### 🎤 Describe Your Symptoms (Voice Input)")
        
        col1, col2 = st.columns(2)
        with col1:
            language = st.radio("Select language:", ["🇮🇳 हिन्दी (Hindi)", "🇬🇧 English"], key="voice_lang")
            lang_code = "hi-IN" if "Hindi" in language else "en-IN"
        
        with col2:
            if st.button("🎙️ Start Recording", key="voice_record_btn"):
                transcript = self.record_audio(language=lang_code)
                if transcript:
                    st.success(f"✅ Recorded: {transcript}")
                    return transcript
        
        return None


class SymptomExtractor:
    """Extract symptoms from text (Hindi/English)"""
    
    SYMPTOMS_MAPPING = {
        # Hindi
        "खांसी": "Cough",
        "बुखार": "Fever",
        "थकान": "Fatigue",
        "सिरदर्द": "Headache",
        "जी मचलना": "Nausea",
        "गला खराब": "Throat Infection",
        
        # English
        "cough": "Cough",
        "fever": "Fever",
        "fatigue": "Fatigue",
        "headache": "Headache",
        "nausea": "Nausea",
        "throat": "Throat Infection",
        "cold": "Cough",
        "sick": "Fever"
    }
    
    @classmethod
    def extract(cls, text: str) -> Optional[str]:
        """Extract symptoms from text"""
        text_lower = text.lower()
        
        for symptom_text, symptom_label in cls.SYMPTOMS_MAPPING.items():
            if symptom_text.lower() in text_lower:
                return symptom_label
        
        return None
