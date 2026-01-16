"""
Database models and initialization for Resume Screening System.
Handles SQLite database setup and CRUD operations.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import config


class Database:
    """Database manager for resume screening system."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path or config.DATABASE_PATH
        self.ensure_database_exists()
        self.init_tables()
    
    def ensure_database_exists(self):
        """Create database directory if it doesn't exist."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_tables(self):
        """Initialize database tables."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Job Descriptions Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                required_skills TEXT,
                clean_text TEXT,
                embedding BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Resumes Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id TEXT UNIQUE NOT NULL,
                candidate_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                content TEXT NOT NULL,
                extracted_skills TEXT,
                clean_text TEXT,
                embedding BLOB,
                experience_years REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Screening Results Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS screening_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                resume_id TEXT NOT NULL,
                skill_match_score REAL,
                semantic_similarity_score REAL,
                experience_score REAL,
                overall_score REAL,
                rank INTEGER,
                matched_skills TEXT,
                screened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES job_descriptions(job_id),
                FOREIGN KEY (resume_id) REFERENCES resumes(resume_id)
            )
        ''')
        
        # Create indexes for better query performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_job_id 
            ON screening_results(job_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_resume_id 
            ON screening_results(resume_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_overall_score 
            ON screening_results(overall_score DESC)
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_job_description(self, job_data: Dict) -> int:
        """
        Insert a job description into the database.
        
        Args:
            job_data: Dictionary containing job information
            
        Returns:
            ID of inserted job
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO job_descriptions 
            (job_id, title, description, required_skills, clean_text, embedding)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            job_data.get('job_id'),
            job_data.get('title'),
            job_data.get('description'),
            json.dumps(job_data.get('required_skills', [])),
            job_data.get('clean_text'),
            job_data.get('embedding')
        ))
        
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return job_id
    
    def insert_resume(self, resume_data: Dict) -> int:
        """
        Insert a resume into the database.
        
        Args:
            resume_data: Dictionary containing resume information
            
        Returns:
            ID of inserted resume
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO resumes 
            (resume_id, candidate_name, email, phone, content, 
             extracted_skills, clean_text, embedding, experience_years)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            resume_data.get('resume_id'),
            resume_data.get('candidate_name'),
            resume_data.get('email'),
            resume_data.get('phone'),
            resume_data.get('content'),
            json.dumps(resume_data.get('extracted_skills', [])),
            resume_data.get('clean_text'),
            resume_data.get('embedding'),
            resume_data.get('experience_years', 0.0)
        ))
        
        resume_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return resume_id
    
    def insert_screening_result(self, result_data: Dict) -> int:
        """
        Insert screening result into the database.
        
        Args:
            result_data: Dictionary containing screening results
            
        Returns:
            ID of inserted result
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO screening_results 
            (job_id, resume_id, skill_match_score, semantic_similarity_score,
             experience_score, overall_score, rank, matched_skills)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            result_data.get('job_id'),
            result_data.get('resume_id'),
            result_data.get('skill_match_score'),
            result_data.get('semantic_similarity_score'),
            result_data.get('experience_score'),
            result_data.get('overall_score'),
            result_data.get('rank'),
            json.dumps(result_data.get('matched_skills', []))
        ))
        
        result_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return result_id
    
    def get_job_description(self, job_id: str) -> Optional[Dict]:
        """
        Retrieve job description by ID.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job description data or None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM job_descriptions WHERE job_id = ?
        ''', (job_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_resume(self, resume_id: str) -> Optional[Dict]:
        """
        Retrieve resume by ID.
        
        Args:
            resume_id: Resume identifier
            
        Returns:
            Resume data or None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM resumes WHERE resume_id = ?
        ''', (resume_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_resumes(self) -> List[Dict]:
        """
        Retrieve all resumes from database.
        
        Returns:
            List of resume dictionaries
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM resumes')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_all_jobs(self) -> List[Dict]:
        """
        Retrieve all job descriptions from database.
        
        Returns:
            List of job description dictionaries
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM job_descriptions ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_screening_results(self, job_id: str) -> List[Dict]:
        """
        Get screening results for a job, ordered by rank.
        
        Args:
            job_id: Job identifier
            
        Returns:
            List of screening results with candidate details
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                sr.*,
                r.candidate_name,
                r.email,
                r.phone,
                r.experience_years
            FROM screening_results sr
            JOIN resumes r ON sr.resume_id = r.resume_id
            WHERE sr.job_id = ?
            ORDER BY sr.overall_score DESC, sr.rank ASC
        ''', (job_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def clear_screening_results(self, job_id: str):
        """
        Clear previous screening results for a job.
        
        Args:
            job_id: Job identifier
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM screening_results WHERE job_id = ?
        ''', (job_id,))
        
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict:
        """
        Get database statistics.
        
        Returns:
            Dictionary with database statistics
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM job_descriptions')
        job_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM resumes')
        resume_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM screening_results')
        screening_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_jobs': job_count,
            'total_resumes': resume_count,
            'total_screenings': screening_count
        }
