"""
Doctor Location Finder - Location-based doctor suggestions
Real-time doctor discovery based on patient location
"""

import folium
from geopy.distance import geodesic
from typing import List, Dict, Tuple, Optional
import pandas as pd
import streamlit as st

class SpecialtyMatcher:
    """Map medical diagnoses to required doctor specialties"""
    
    SPECIALTY_MAPPING = {
        "Common Cold": ["General Practitioner"],
        "Viral Fever": ["General Practitioner"],
        "Pneumonia": ["Respiratory Specialist", "General Practitioner"],
        "Flu": ["General Practitioner"],
        "Food Poisoning": ["Internal Medicine"],
        "Dengue (Mild)": ["Internal Medicine", "Infectious Disease"],
        "Bronchitis": ["Respiratory Specialist"],
        "Fatigue": ["General Practitioner"],
        "Throat Infection": ["Internal Medicine"],
    }
    
    @classmethod
    def get_matching_specialties(cls, diagnosis: str) -> list:
        """Get recommended specialties for a diagnosis"""
        return cls.SPECIALTY_MAPPING.get(diagnosis, ["General Practitioner"])


class DoctorFinder:
    """Find doctors near patient location"""
    
    # Sample doctor database (in production, use real API/database)
    DOCTORS_DATABASE = [
        {
            "id": 1,
            "name": "Dr. Raj Kumar",
            "specialty": "General Practitioner",
            "lat": 28.7041, "lon": 77.1025,
            "phone": "+91-9876543210",
            "address": "123 Hospital Street, Delhi",
            "experience": "15 years",
            "rating": 4.8
        },
        {
            "id": 2,
            "name": "Dr. Priya Singh",
            "specialty": "Internal Medicine",
            "lat": 28.6139, "lon": 77.2090,
            "phone": "+91-9876543211",
            "address": "456 Medical Plaza, Delhi",
            "experience": "12 years",
            "rating": 4.9
        },
        {
            "id": 3,
            "name": "Dr. Amit Patel",
            "specialty": "Respiratory Specialist",
            "lat": 28.5244, "lon": 77.1855,
            "phone": "+91-9876543212",
            "address": "789 Health Center, Gurgaon",
            "experience": "10 years",
            "rating": 4.7
        },
        {
            "id": 4,
            "name": "Dr. Neha Sharma",
            "specialty": "Pediatrician",
            "lat": 28.6332, "lon": 77.2197,
            "phone": "+91-9876543213",
            "address": "321 Child Care Clinic, Delhi",
            "experience": "8 years",
            "rating": 4.9
        },
        {
            "id": 5,
            "name": "Dr. Vikram Verma",
            "specialty": "Infectious Disease",
            "lat": 28.5355, "lon": 77.3910,
            "phone": "+91-9876543214",
            "address": "654 Infection Care, Noida",
            "experience": "14 years",
            "rating": 4.8
        }
    ]
    
    @classmethod
    def find_nearby_doctors(cls, patient_lat: float, patient_lon: float, 
                           radius_km: float = 5.0) -> List[Dict]:
        """Find doctors within specified radius"""
        nearby = []
        patient_location = (patient_lat, patient_lon)
        
        for doctor in cls.DOCTORS_DATABASE:
            doctor_location = (doctor['lat'], doctor['lon'])
            distance = geodesic(patient_location, doctor_location).kilometers
            
            if distance <= radius_km:
                doctor_copy = doctor.copy()
                doctor_copy['distance_km'] = round(distance, 2)
                nearby.append(doctor_copy)
        
        # Sort by distance
        return sorted(nearby, key=lambda x: x['distance_km'])
    
    @classmethod
    def find_by_specialty(cls, specialty: str, patient_lat: float = None, 
                         patient_lon: float = None, radius_km: float = 10.0) -> List[Dict]:
        """Find doctors by specialty"""
        specialists = [d.copy() for d in cls.DOCTORS_DATABASE 
                      if specialty.lower() in d['specialty'].lower()]
        
        if patient_lat and patient_lon:
            patient_location = (patient_lat, patient_lon)
            for doc in specialists:
                doc_location = (doc['lat'], doc['lon'])
                distance = geodesic(patient_location, doc_location).kilometers
                doc['distance_km'] = round(distance, 2)
            
            return sorted(specialists, key=lambda x: x['distance_km'])
        
        return sorted(specialists, key=lambda x: x.get('rating', 0), reverse=True)
    
    @classmethod
    def get_recommended_specialty(cls, diagnosis: str) -> str:
        """Get recommended doctor specialty based on diagnosis"""
        diagnosis_specialty_map = {
            "Common Cold": "General Practitioner",
            "Viral Fever": "General Practitioner",
            "Pneumonia": "Respiratory Specialist",
            "Flu": "General Practitioner",
            "Food Poisoning": "Internal Medicine",
            "Dengue (Mild)": "Internal Medicine",
            "Bronchitis": "Respiratory Specialist",
            "Fatigue": "General Practitioner",
            "Throat Infection": "Internal Medicine",
        }
        return diagnosis_specialty_map.get(diagnosis, "General Practitioner")
    
    @classmethod
    def create_map(cls, patient_lat: float, patient_lon: float, 
                   doctors: List[Dict], zoom: int = 13) -> folium.Map:
        """Create interactive map showing patient location and nearby doctors"""
        
        map_obj = folium.Map(
            location=[patient_lat, patient_lon],
            zoom_start=zoom,
            tiles="OpenStreetMap"
        )
        
        # Add patient location (blue marker)
        folium.Marker(
            location=[patient_lat, patient_lon],
            popup="Your Location",
            icon=folium.Icon(color="blue", icon="home"),
            tooltip="Your Current Location"
        ).add_to(map_obj)
        
        # Add doctor locations (red markers)
        for i, doctor in enumerate(doctors, 1):
            popup_text = f"""
            <b>{doctor['name']}</b><br>
            {doctor['specialty']}<br>
            📞 {doctor['phone']}<br>
            📍 {doctor['address']}<br>
            ⭐ {doctor['rating']} ({doctor['experience']})<br>
            <b>Distance: {doctor.get('distance_km', 'N/A')} km</b>
            """
            
            folium.Marker(
                location=[doctor['lat'], doctor['lon']],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color="red", icon="stethoscope"),
                tooltip=doctor['name']
            ).add_to(map_obj)
        
        return map_obj


class SpecialtyMatcher:
    """Match diagnosis to doctor specialties"""
    
    DIAGNOSIS_SPECIALTY = {
        "Common Cold": ["General Practitioner", "Internal Medicine"],
        "Viral Fever": ["Internal Medicine", "Infectious Disease"],
        "Pneumonia": ["Respiratory Specialist", "Internal Medicine"],
        "Flu": ["General Practitioner", "Internal Medicine"],
        "Food Poisoning": ["Internal Medicine", "Gastroenterologist"],
        "Dengue (Mild)": ["Infectious Disease", "Internal Medicine"],
        "Bronchitis": ["Respiratory Specialist", "Internal Medicine"],
        "Fatigue": ["General Practitioner", "Internal Medicine"],
        "Throat Infection": ["Internal Medicine", "ENT Specialist"],
    }
    
    @classmethod
    def get_matching_specialties(cls, diagnosis: str) -> List[str]:
        """Get recommended specialties for diagnosis"""
        return cls.DIAGNOSIS_SPECIALTY.get(diagnosis, ["General Practitioner"])
