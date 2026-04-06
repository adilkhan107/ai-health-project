"""
Voice Input Module - Hindi & English Speech Recognition
Supports voice input for patient symptoms and diagnosis queries
Uses gTTS (Google Text-to-Speech) for clear Hindi & English voice output
"""

import speech_recognition as sr
import io
from typing import Optional, Tuple
import streamlit as st

class VoiceInput:
    """Handle voice input and text-to-speech conversion using gTTS"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()

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
        Convert text to speech using gTTS and auto-play in Streamlit.
        
        Args:
            text: Text to convert to speech
            language: Language code ('hi' for Hindi, 'en' for English)
        """
        try:
            from gtts import gTTS
            
            lang_label = "Hindi" if language == "hi" else "English"
            st.info(f"🔊 Playing result in {lang_label}...")
            
            # Generate speech audio in memory
            tts = gTTS(text=text, lang=language, slow=False)
            audio_bytes = io.BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            
            # Auto-play in Streamlit
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)
            
        except ImportError:
            st.error("❌ gTTS is not installed. Run: `pip install gtts`")
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
        "खांसी": "cough",
        "बुखार": "fever",
        "थकान": "fatigue",
        "सिरदर्द": "headache",
        "जी मचलना": "nausea",
        "गला खराब": "throat",
        "उल्टी": "nausea",
        "दस्त": "diarrhea",
        "सांस": "breathlessness",
        "छाती में दर्द": "chest pain",
        "जोड़ों में दर्द": "joint pain",
        "चकत्ते": "rash",
        "पेट दर्द": "stomach pain",
        
        # English
        "cough": "cough",
        "coughing": "cough",
        "fever": "fever",
        "temperature": "fever",
        "fatigue": "fatigue",
        "tiredness": "fatigue",
        "tired": "fatigue",
        "headache": "headache",
        "head pain": "headache",
        "nausea": "nausea",
        "vomiting": "nausea",
        "throat": "throat",
        "sore throat": "throat",
        "cold": "cough",
        "sick": "fever",
        "breathlessness": "breathlessness",
        "breathing": "breathlessness",
        "shortness of breath": "breathlessness",
        "wheezing": "wheezing",
        "diarrhea": "diarrhea",
        "loose motion": "diarrhea",
        "rash": "rash",
        "skin rash": "rash",
        "joint pain": "joint pain",
        "body pain": "joint pain",
        "chest pain": "chest pain",
        "stomach pain": "stomach pain",
        "stomach ache": "stomach pain",
    }

    # Friendly display names for detected symptom keywords
    DISPLAY_NAMES = {
        "cough": "Cough",
        "fever": "Fever",
        "fatigue": "Fatigue",
        "headache": "Headache",
        "nausea": "Nausea",
        "throat": "Throat Infection",
        "breathlessness": "Breathlessness",
        "wheezing": "Wheezing",
        "diarrhea": "Diarrhea",
        "rash": "Rash",
        "joint pain": "Joint Pain",
        "chest pain": "Chest Pain",
        "stomach pain": "Stomach Pain",
    }
    
    @classmethod
    def extract(cls, text: str) -> Optional[str]:
        """Extract first matching symptom from text (legacy)"""
        text_lower = text.lower()
        
        for symptom_text, symptom_label in cls.SYMPTOMS_MAPPING.items():
            if symptom_text.lower() in text_lower:
                return cls.DISPLAY_NAMES.get(symptom_label, symptom_label)
        
        return None

    @classmethod
    def extract_all(cls, text: str) -> list:
        """Extract ALL matching symptoms from text, returning unique keyword labels"""
        text_lower = text.lower()
        found = set()
        
        for symptom_text, symptom_keyword in cls.SYMPTOMS_MAPPING.items():
            if symptom_text.lower() in text_lower:
                found.add(symptom_keyword)
        
        return list(found)

    @classmethod
    def symptom_text(cls, text: str) -> str:
        """Return a space-separated string of all detected symptom keywords (for ML pipeline)"""
        keywords = cls.extract_all(text)
        return " ".join(keywords) if keywords else text

    @classmethod
    def display_symptoms(cls, text: str) -> list:
        """Return a list of human-readable symptom names detected in text"""
        keywords = cls.extract_all(text)
        return [cls.DISPLAY_NAMES.get(k, k.title()) for k in keywords]
