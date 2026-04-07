"""
Database models for user and patient management
"""
import sqlite3
import os
from datetime import datetime
import uuid

DB_PATH = os.path.join(os.path.dirname(__file__), '../../data/app.db')

def ensure_db():
    """Create database and tables if they don't exist"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Patients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            phone TEXT,
            email TEXT,
            medical_history TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Analysis results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            result_id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            analysis_type TEXT NOT NULL,
            file_name TEXT,
            audio_features TEXT,
            predictions TEXT,
            facial_expressions TEXT,
            combined_analysis TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        )
    ''')
    
    # Reports table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            report_id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            result_id TEXT NOT NULL,
            analysis_type TEXT NOT NULL,
            report_title TEXT NOT NULL,
            report_summary TEXT,
            emotion_detected TEXT,
            confidence_score REAL,
            audio_features_json TEXT,
            video_features_json TEXT,
            recommendations TEXT,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
            FOREIGN KEY (result_id) REFERENCES analysis_results(result_id)
        )
    ''')
    
    conn.commit()
    conn.close()

class User:
    """User model"""
    
    @staticmethod
    def create(email, password, full_name):
        """Create a new user"""
        ensure_db()
        user_id = str(uuid.uuid4())
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (id, email, password, full_name)
                VALUES (?, ?, ?, ?)
            ''', (user_id, email, password, full_name))
            conn.commit()
            conn.close()
            return {'id': user_id, 'email': email, 'full_name': full_name}
        except sqlite3.IntegrityError:
            return None
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        ensure_db()
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        ensure_db()
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

class Patient:
    """Patient model"""
    
    @staticmethod
    def create(user_id, name, age=None, gender=None, phone=None, email=None, medical_history=None):
        """Create a new patient record"""
        ensure_db()
        patient_id = f"PAT-{str(uuid.uuid4())[:8].upper()}"
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO patients 
                (patient_id, user_id, name, age, gender, phone, email, medical_history)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (patient_id, user_id, name, age, gender, phone, email, medical_history))
            conn.commit()
            conn.close()
            return {
                'patient_id': patient_id,
                'user_id': user_id,
                'name': name,
                'age': age,
                'gender': gender,
                'phone': phone,
                'email': email
            }
        except Exception as e:
            return None
    
    @staticmethod
    def get_by_id(patient_id):
        """Get patient by ID"""
        ensure_db()
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM patients WHERE patient_id = ?', (patient_id,))
        patient = cursor.fetchone()
        conn.close()
        return dict(patient) if patient else None
    
    @staticmethod
    def get_by_user(user_id):
        """Get all patients for a user"""
        ensure_db()
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM patients WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        patients = cursor.fetchall()
        conn.close()
        return [dict(p) for p in patients]
    
    @staticmethod
    def update(patient_id, **kwargs):
        """Update patient information"""
        ensure_db()
        allowed_fields = ['name', 'age', 'gender', 'phone', 'email', 'medical_history']
        
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False
        
        set_clause = ', '.join([f'{k} = ?' for k in updates.keys()])
        values = list(updates.values()) + [patient_id]
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(f'UPDATE patients SET {set_clause} WHERE patient_id = ?', values)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            return False

class AnalysisResult:
    """Analysis result model"""
    
    @staticmethod
    def create(patient_id, analysis_type, file_name=None, **kwargs):
        """Create a new analysis result"""
        ensure_db()
        result_id = f"RES-{str(uuid.uuid4())[:8].upper()}"
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO analysis_results
                (result_id, patient_id, analysis_type, file_name, audio_features, predictions, 
                 facial_expressions, combined_analysis, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result_id,
                patient_id,
                analysis_type,
                file_name,
                kwargs.get('audio_features'),
                kwargs.get('predictions'),
                kwargs.get('facial_expressions'),
                kwargs.get('combined_analysis'),
                kwargs.get('notes')
            ))
            conn.commit()
            conn.close()
            return {'result_id': result_id, 'patient_id': patient_id}
        except Exception as e:
            return None
    
    @staticmethod
    def get_by_patient(patient_id):
        """Get all analysis results for a patient"""
        ensure_db()
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM analysis_results 
            WHERE patient_id = ? 
            ORDER BY created_at DESC
        ''', (patient_id,))
        results = cursor.fetchall()
        conn.close()
        return [dict(r) for r in results]
    
    @staticmethod
    def get_by_id(result_id):
        """Get analysis result by ID"""
        ensure_db()
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM analysis_results WHERE result_id = ?', (result_id,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None
    
    @staticmethod
    def get_latest_by_patient(patient_id, limit=10):
        """Get latest analysis results for a patient"""
        ensure_db()
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM analysis_results 
            WHERE patient_id = ? 
            ORDER BY created_at DESC
            LIMIT ?
        ''', (patient_id, limit))
        results = cursor.fetchall()
        conn.close()
        return [dict(r) for r in results]

class Report:
    """Report model for detailed analysis reports"""
    
    @staticmethod
    def create(patient_id, result_id, analysis_type, report_title, emotion_detected, 
               confidence_score, audio_features=None, video_features=None, recommendations=None):
        """Create a new analysis report"""
        ensure_db()
        report_id = f"RPT-{str(uuid.uuid4())[:12].upper()}"
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO reports
                (report_id, patient_id, result_id, analysis_type, report_title, 
                 emotion_detected, confidence_score, audio_features_json, 
                 video_features_json, recommendations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                report_id,
                patient_id,
                result_id,
                analysis_type,
                report_title,
                emotion_detected,
                confidence_score,
                audio_features,
                video_features,
                recommendations
            ))
            conn.commit()
            conn.close()
            return {
                'report_id': report_id,
                'patient_id': patient_id,
                'result_id': result_id,
                'created_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error creating report: {e}")
            return None
    
    @staticmethod
    def get_by_patient(patient_id):
        """Get all reports for a patient"""
        ensure_db()
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM reports 
            WHERE patient_id = ?
            ORDER BY generated_at DESC
        ''', (patient_id,))
        reports = cursor.fetchall()
        conn.close()
        return [dict(r) for r in reports]
    
    @staticmethod
    def get_by_result(result_id):
        """Get report for a specific analysis result"""
        ensure_db()
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reports WHERE result_id = ?', (result_id,))
        report = cursor.fetchone()
        conn.close()
        return dict(report) if report else None
    
    @staticmethod
    def get_by_id(report_id):
        """Get report by ID"""
        ensure_db()
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reports WHERE report_id = ?', (report_id,))
        report = cursor.fetchone()
        conn.close()
        return dict(report) if report else None
