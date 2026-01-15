# Sample Datasets Directory

Place your resume and job description datasets here.

## Supported Formats
- `.txt` - Plain text files
- `.pdf` - PDF documents
- `.docx` - Microsoft Word documents

## Directory Structure

```
data/
├── resumes/
│   ├── resume1.txt
│   ├── resume2.pdf
│   └── ...
├── jobs/
│   ├── job1.txt
│   └── ...
└── resume_screener.db (auto-generated)
```

## Loading Data

Use the API endpoints or create custom scripts to load your data:

```python
import requests

# Upload resume
with open('data/resumes/resume1.txt', 'r') as f:
    content = f.read()
    
response = requests.post('http://localhost:5000/api/upload/resume', json={
    'candidate_name': 'John Doe',
    'content': content
})
```
