"""backend.models.database

Database models for user and patient management.

- Local development: SQLite file at data/app.db
- Production (e.g. Vercel): Postgres via DATABASE_URL (or Vercel POSTGRES_URL)
"""

from __future__ import annotations

import os
import sqlite3
import uuid
from datetime import datetime
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


def _get_database_url() -> str | None:
    # Vercel Postgres integration commonly provides POSTGRES_URL.
    url = (
        os.getenv("DATABASE_URL")
        or os.getenv("POSTGRES_URL")
        or os.getenv("POSTGRES_PRISMA_URL")
    )
    if not url:
        return None

    # Some providers use postgres:// which psycopg2 can be picky about.
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]

    # Encourage SSL in hosted environments if the URL doesn't specify.
    parsed = urlparse(url)
    if parsed.scheme.startswith("postgres"):
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        if "sslmode" not in query:
            query["sslmode"] = "require"
            parsed = parsed._replace(query=urlencode(query))
            url = urlunparse(parsed)
    return url


DATABASE_URL = _get_database_url()
IS_PRODUCTION = bool(DATABASE_URL)

IS_VERCEL = os.getenv("VERCEL") == "1" or os.getenv("VERCEL_ENV") is not None

if IS_PRODUCTION:
    # Not used in production mode, but keep defined.
    DB_PATH = ""
else:
    # Vercel allows writes only to /tmp. This fallback keeps the app running even
    # if the user hasn't configured DATABASE_URL yet (data will not persist).
    DB_PATH = (
        "/tmp/app.db"
        if IS_VERCEL
        else os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "data", "app.db")
        )
    )


def _placeholder() -> str:
    return "%s" if IS_PRODUCTION else "?"


def get_connection():
    """Get a DB-API connection for SQLite or Postgres."""

    if IS_PRODUCTION:
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
        except Exception as e:  # pragma: no cover
            raise RuntimeError(
                "Postgres DATABASE_URL is set but psycopg2 is not installed"
            ) from e

        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_db():
    """Create database and tables if they don't exist."""

    ddl_statements = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
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
        """,
        """
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
        """,
        """
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
        """,
    ]

    conn = get_connection()
    try:
        cursor = conn.cursor()
        for ddl in ddl_statements:
            cursor.execute(ddl)
        conn.commit()
    finally:
        try:
            conn.close()
        except Exception:
            pass

class User:
    """User model"""
    
    @staticmethod
    def create(email, password, full_name):
        """Create a new user"""
        ensure_db()
        user_id = str(uuid.uuid4())

        conn = get_connection()
        try:
            cursor = conn.cursor()
            ph = _placeholder()
            cursor.execute(
                f"INSERT INTO users (id, email, password, full_name) VALUES ({ph}, {ph}, {ph}, {ph})",
                (user_id, email, password, full_name),
            )
            conn.commit()
            return {"id": user_id, "email": email, "full_name": full_name}
        except Exception:
            return None
        finally:
            try:
                conn.close()
            except Exception:
                pass
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        ensure_db()
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM users WHERE email = {_placeholder()}", (email,))
            user = cursor.fetchone()
            return dict(user) if user else None
        finally:
            try:
                conn.close()
            except Exception:
                pass
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        ensure_db()
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM users WHERE id = {_placeholder()}", (user_id,))
            user = cursor.fetchone()
            return dict(user) if user else None
        finally:
            try:
                conn.close()
            except Exception:
                pass

class Patient:
    """Patient model"""
    
    @staticmethod
    def create(user_id, name, age=None, gender=None, phone=None, email=None, medical_history=None):
        """Create a new patient record"""
        ensure_db()
        patient_id = f"PAT-{str(uuid.uuid4())[:8].upper()}"
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            ph = _placeholder()
            cursor.execute(
                "INSERT INTO patients (patient_id, user_id, name, age, gender, phone, email, medical_history) "
                f"VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})",
                (patient_id, user_id, name, age, gender, phone, email, medical_history),
            )
            conn.commit()
            return {
                "patient_id": patient_id,
                "user_id": user_id,
                "name": name,
                "age": age,
                "gender": gender,
                "phone": phone,
                "email": email,
            }
        except Exception:
            return None
        finally:
            try:
                conn.close()
            except Exception:
                pass
    
    @staticmethod
    def get_by_id(patient_id):
        """Get patient by ID"""
        ensure_db()
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM patients WHERE patient_id = {_placeholder()}",
                (patient_id,),
            )
            patient = cursor.fetchone()
            return dict(patient) if patient else None
        finally:
            try:
                conn.close()
            except Exception:
                pass
    
    @staticmethod
    def get_by_user(user_id):
        """Get all patients for a user"""
        ensure_db()
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM patients WHERE user_id = {_placeholder()} ORDER BY created_at DESC",
                (user_id,),
            )
            patients = cursor.fetchall()
            return [dict(p) for p in patients]
        finally:
            try:
                conn.close()
            except Exception:
                pass
    
    @staticmethod
    def update(patient_id, **kwargs):
        """Update patient information"""
        ensure_db()
        allowed_fields = ['name', 'age', 'gender', 'phone', 'email', 'medical_history']
        
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False
        
        ph = _placeholder()
        set_clause = ', '.join([f'{k} = {ph}' for k in updates.keys()])
        values = list(updates.values()) + [patient_id]

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE patients SET {set_clause} WHERE patient_id = {ph}",
                values,
            )
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            try:
                conn.close()
            except Exception:
                pass

class AnalysisResult:
    """Analysis result model"""
    
    @staticmethod
    def create(patient_id, analysis_type, file_name=None, **kwargs):
        """Create a new analysis result"""
        ensure_db()
        result_id = f"RES-{str(uuid.uuid4())[:8].upper()}"
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            ph = _placeholder()
            cursor.execute(
                "INSERT INTO analysis_results (result_id, patient_id, analysis_type, file_name, audio_features, predictions, facial_expressions, combined_analysis, notes) "
                f"VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})",
                (
                    result_id,
                    patient_id,
                    analysis_type,
                    file_name,
                    kwargs.get("audio_features"),
                    kwargs.get("predictions"),
                    kwargs.get("facial_expressions"),
                    kwargs.get("combined_analysis"),
                    kwargs.get("notes"),
                ),
            )
            conn.commit()
            return {"result_id": result_id, "patient_id": patient_id}
        except Exception:
            return None
        finally:
            try:
                conn.close()
            except Exception:
                pass
    
    @staticmethod
    def get_by_patient(patient_id):
        """Get all analysis results for a patient"""
        ensure_db()
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM analysis_results WHERE patient_id = "
                f"{_placeholder()} ORDER BY created_at DESC",
                (patient_id,),
            )
            results = cursor.fetchall()
            return [dict(r) for r in results]
        finally:
            try:
                conn.close()
            except Exception:
                pass
    
    @staticmethod
    def get_by_id(result_id):
        """Get analysis result by ID"""
        ensure_db()
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM analysis_results WHERE result_id = {_placeholder()}",
                (result_id,),
            )
            result = cursor.fetchone()
            return dict(result) if result else None
        finally:
            try:
                conn.close()
            except Exception:
                pass
    
    @staticmethod
    def get_latest_by_patient(patient_id, limit=10):
        """Get latest analysis results for a patient"""
        ensure_db()
        conn = get_connection()
        try:
            cursor = conn.cursor()
            ph = _placeholder()
            cursor.execute(
                f"SELECT * FROM analysis_results WHERE patient_id = {ph} ORDER BY created_at DESC LIMIT {ph}",
                (patient_id, limit),
            )
            results = cursor.fetchall()
            return [dict(r) for r in results]
        finally:
            try:
                conn.close()
            except Exception:
                pass

class Report:
    """Report model for detailed analysis reports"""
    
    @staticmethod
    def create(
        patient_id,
        result_id,
        analysis_type,
        report_title,
        emotion_detected,
        confidence_score,
        report_summary=None,
        audio_features_json=None,
        video_features_json=None,
        recommendations=None,
    ):
        """Create a new analysis report"""
        ensure_db()
        report_id = f"RPT-{str(uuid.uuid4())[:12].upper()}"

        conn = get_connection()
        try:
            cursor = conn.cursor()
            ph = _placeholder()
            cursor.execute(
                "INSERT INTO reports (report_id, patient_id, result_id, analysis_type, report_title, report_summary, emotion_detected, confidence_score, audio_features_json, video_features_json, recommendations) "
                f"VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})",
                (
                    report_id,
                    patient_id,
                    result_id,
                    analysis_type,
                    report_title,
                    report_summary,
                    emotion_detected,
                    confidence_score,
                    audio_features_json,
                    video_features_json,
                    recommendations,
                ),
            )
            conn.commit()
            return {
                "report_id": report_id,
                "patient_id": patient_id,
                "result_id": result_id,
                "created_at": datetime.now().isoformat(),
            }
        except Exception as e:
            print(f"Error creating report: {e}")
            return None
        finally:
            try:
                conn.close()
            except Exception:
                pass
    
    @staticmethod
    def get_by_patient(patient_id):
        """Get all reports for a patient"""
        ensure_db()
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM reports WHERE patient_id = {_placeholder()} ORDER BY generated_at DESC",
                (patient_id,),
            )
            reports = cursor.fetchall()
            return [dict(r) for r in reports]
        finally:
            try:
                conn.close()
            except Exception:
                pass
    
    @staticmethod
    def get_by_result(result_id):
        """Get report for a specific analysis result"""
        ensure_db()
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM reports WHERE result_id = {_placeholder()}",
                (result_id,),
            )
            report = cursor.fetchone()
            return dict(report) if report else None
        finally:
            try:
                conn.close()
            except Exception:
                pass
    
    @staticmethod
    def get_by_id(report_id):
        """Get report by ID"""
        ensure_db()
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM reports WHERE report_id = {_placeholder()}",
                (report_id,),
            )
            report = cursor.fetchone()
            return dict(report) if report else None
        finally:
            try:
                conn.close()
            except Exception:
                pass
