# Resume Screening ML System

An end-to-end machine learning system for automated resume screening and candidate ranking.

## Features

- **Text Preprocessing**: Advanced cleaning and normalization of resume and job description text
- **Skill Extraction**: NLP-based entity recognition and keyword matching for skill identification
- **Semantic Matching**: Sentence transformer embeddings for semantic similarity
- **Candidate Ranking**: Automated scoring and ranking of candidates per job posting
- **REST API**: Flask-based API for easy integration
- **Data Persistence**: SQLite database for storing results

## Tech Stack

- Python 3.8+
- scikit-learn
- spaCy / NLTK
- sentence-transformers
- Flask
- SQLite

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download required NLP models:
   ```bash
   python -m spacy download en_core_web_sm
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
   ```

5. Copy `.env.example` to `.env` and configure as needed

## Usage

### Running the API Server

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### API Endpoints

- `POST /api/upload/resume` - Upload resume data
- `POST /api/upload/job` - Upload job description
- `POST /api/screen` - Screen resumes against job descriptions
- `GET /api/results/<job_id>` - Get ranked candidates for a job
- `GET /api/health` - Health check

## Project Structure

```
resume-screener/
├── src/
│   ├── preprocessing/
│   ├── skill_extraction/
│   ├── embeddings/
│   ├── scoring/
│   └── api/
├── data/
├── models/
├── tests/
├── app.py
└── requirements.txt
```

## License

MIT
