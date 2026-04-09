"""
Patient Health History Tracking - SQLite Database
Store and retrieve patient medical history for better diagnosis
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd
from pathlib import Path

class PatientHistoryDB:
    """Manage patient health history using SQLite"""
    
    def __init__(self, db_path: str = "database/patient_history.db"):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Patients table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS patients (
                    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER,
                    gender TEXT,
                    phone TEXT,
                    email TEXT,
                    location TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Medical history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS medical_history (
                    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    symptoms TEXT,
                    diagnosis TEXT,
                    temperature REAL,
                    heart_rate INTEGER,
                    blood_pressure TEXT,
                    medicine_prescribed TEXT,
                    doctor_notes TEXT,
                    visit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(patient_id) REFERENCES patients(patient_id)
                )
            ''')
            
            conn.commit()
    
    def add_patient(self, name: str, age: int, gender: str, 
                   phone: str = "", email: str = "", location: str = "") -> int:
        """Add new patient"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO patients (name, age, gender, phone, email, location)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, age, gender, phone, email, location))
            conn.commit()
            return cursor.lastrowid
    
    def get_patient(self, patient_id: int) -> Optional[Dict]:
        """Get patient details"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM patients WHERE patient_id = ?', 
                (patient_id,)
            )
            row = cursor.fetchone()
            if row:
                return {
                    'patient_id': row[0], 'name': row[1], 'age': row[2],
                    'gender': row[3], 'phone': row[4], 'email': row[5],
                    'location': row[6], 'created_at': row[7]
                }
        return None
    
    def add_diagnosis(self, patient_id: int, symptoms: str, diagnosis: str,
                     temperature: float, heart_rate: int, blood_pressure: str,
                     medicine: str = "", notes: str = "") -> int:
        """Add diagnosis entry"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO medical_history 
                (patient_id, symptoms, diagnosis, temperature, heart_rate, 
                 blood_pressure, medicine_prescribed, doctor_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (patient_id, symptoms, diagnosis, temperature, heart_rate,
                  blood_pressure, medicine, notes))
            conn.commit()
            return cursor.lastrowid
            return cursor.lastrowid
    
    def get_patient_history(self, patient_id: int) -> List[Dict]:
        """Get complete medical history of patient"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM medical_history 
                WHERE patient_id = ? 
                ORDER BY visit_date DESC
            ''', (patient_id,))
            
            rows = cursor.fetchall()
            history = []
            for row in rows:
                history.append({
                    'history_id': row[0], 'patient_id': row[1],
                    'symptoms': row[2], 'diagnosis': row[3],
                    'temperature': row[4], 'heart_rate': row[5],
                    'blood_pressure': row[6], 'medicine': row[7],
                    'notes': row[8], 'visit_date': row[9]
                })
            return history
    
    def search_patient_by_phone(self, phone: str) -> Optional[int]:
        """Find patient by phone number"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT patient_id FROM patients WHERE phone = ?', (phone,))
            row = cursor.fetchone()
            return row[0] if row else None
    
    def get_all_patients(self) -> pd.DataFrame:
        """Get all patients as DataFrame"""
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query('SELECT * FROM patients', conn)
    
    def export_patient_history_csv(self, patient_id: int, filename: str = None) -> str:
        """Export patient history to CSV"""
        history = self.get_patient_history(patient_id)
        patient = self.get_patient(patient_id)
        
        if not history:
            return "No history found"
        
        df = pd.DataFrame(history)
        
        if filename is None:
            filename = f"patient_{patient_id}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        df.to_csv(filename, index=False)
        return filename
