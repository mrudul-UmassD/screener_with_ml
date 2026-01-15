# API Documentation

## Base URL
```
http://localhost:5000/api
```

## Endpoints

### Health Check
**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-15T10:30:00",
  "version": "1.0.0"
}
```

---

### Get Statistics
**GET** `/stats`

Get database statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_jobs": 5,
    "total_resumes": 50,
    "total_screenings": 250
  }
}
```

---

### Upload Resume
**POST** `/upload/resume`

Upload a single resume.

**Request Body:**
```json
{
  "resume_id": "optional_custom_id",
  "candidate_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1-555-1234",
  "content": "Full resume text content here..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "resume_id": "abc123",
    "candidate_name": "John Doe",
    "skills_extracted": 12,
    "experience_years": 5.0,
    "skills": ["python", "javascript", "react", "...]
  }
}
```

---

### Upload Multiple Resumes
**POST** `/upload/resumes/batch`

Upload multiple resumes at once.

**Request Body:**
```json
{
  "resumes": [
    {
      "candidate_name": "John Doe",
      "content": "..."
    },
    {
      "candidate_name": "Jane Smith",
      "content": "..."
    }
  ]
}
```

---

### Upload Job Description
**POST** `/upload/job`

Upload a job description.

**Request Body:**
```json
{
  "job_id": "optional_custom_id",
  "title": "Senior Python Developer",
  "description": "Full job description text..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "job_id": "job123",
    "title": "Senior Python Developer",
    "skills_required": 10,
    "skills": ["python", "django", "postgresql", "...]
  }
}
```

---

### Screen Candidates
**POST** `/screen`

Screen resumes against a job description.

**Request Body:**
```json
{
  "job_id": "job123",
  "resume_ids": ["resume1", "resume2"]  // Optional - screen all if omitted
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "job_id": "job123",
    "candidates_screened": 2,
    "results": [
      {
        "resume_id": "resume1",
        "rank": 1,
        "overall_score": 0.85,
        "skill_match_score": 0.90,
        "semantic_similarity_score": 0.80,
        "experience_score": 0.85,
        "matched_skills": ["python", "django", "postgresql"]
      }
    ]
  }
}
```

---

### Get Screening Results
**GET** `/results/<job_id>`

Get ranked candidates for a specific job.

**Response:**
```json
{
  "success": true,
  "data": {
    "job_id": "job123",
    "total_candidates": 10,
    "results": [...]
  }
}
```

---

### Get Resume Details
**GET** `/resume/<resume_id>`

Get details of a specific resume.

**Response:**
```json
{
  "success": true,
  "data": {
    "resume_id": "resume1",
    "candidate_name": "John Doe",
    "email": "john@example.com",
    "extracted_skills": ["python", "javascript"],
    "experience_years": 5.0,
    "created_at": "2026-01-15T10:00:00"
  }
}
```

---

### Get Job Details
**GET** `/job/<job_id>`

Get details of a specific job.

**Response:**
```json
{
  "success": true,
  "data": {
    "job_id": "job123",
    "title": "Senior Python Developer",
    "required_skills": ["python", "django"],
    "created_at": "2026-01-15T10:00:00"
  }
}
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "success": false,
  "error": "Error message here"
}
```

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request (invalid input)
- `404` - Not Found
- `500` - Internal Server Error

---

## Example Usage (Python)

```python
import requests

BASE_URL = "http://localhost:5000/api"

# Upload a resume
resume_data = {
    "candidate_name": "John Doe",
    "email": "john@example.com",
    "content": "Resume text here..."
}
response = requests.post(f"{BASE_URL}/upload/resume", json=resume_data)
resume_id = response.json()['data']['resume_id']

# Upload a job
job_data = {
    "title": "Python Developer",
    "description": "Job description here..."
}
response = requests.post(f"{BASE_URL}/upload/job", json=job_data)
job_id = response.json()['data']['job_id']

# Screen candidates
screen_data = {"job_id": job_id}
response = requests.post(f"{BASE_URL}/screen", json=screen_data)
results = response.json()['data']['results']

# Get results
response = requests.get(f"{BASE_URL}/results/{job_id}")
ranked_candidates = response.json()['data']['results']
```
