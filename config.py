"""
Configuration module for Resume Screening System.
Loads environment variables and provides configuration constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Database Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/resume_screener.db')
DATABASE_PATH = BASE_DIR / DATABASE_PATH

# Model Configuration
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.5'))

# NLP Configuration
SPACY_MODEL = 'en_core_web_sm'

# Skills Database - Common technical and professional skills
SKILL_KEYWORDS = {
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust',
    'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'html', 'css',
    
    # Frameworks & Libraries
    'react', 'angular', 'vue', 'django', 'flask', 'spring', 'nodejs', 'express',
    'tensorflow', 'pytorch', 'keras', 'pandas', 'numpy', 'scikit-learn',
    
    # Databases
    'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 'oracle', 'sqlite',
    'dynamodb', 'elasticsearch',
    
    # Cloud & DevOps
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'ci/cd', 'terraform',
    'ansible', 'git', 'github', 'gitlab',
    
    # Data Science & ML
    'machine learning', 'deep learning', 'nlp', 'computer vision', 'data analysis',
    'data science', 'statistics', 'data visualization', 'tableau', 'power bi',
    
    # Soft Skills
    'leadership', 'communication', 'teamwork', 'problem solving', 'critical thinking',
    'project management', 'agile', 'scrum', 'collaboration',
    
    # Other Technical
    'api', 'rest', 'graphql', 'microservices', 'testing', 'debugging',
    'linux', 'unix', 'shell scripting', 'networking', 'security'
}

# Flask API Configuration
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# File Upload Configuration
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# Scoring Weights
WEIGHTS = {
    'skill_match': 0.4,
    'semantic_similarity': 0.4,
    'experience': 0.2
}
