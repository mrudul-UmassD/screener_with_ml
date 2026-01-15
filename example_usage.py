"""
Example script demonstrating how to use the Resume Screening System.
"""

import json
import requests
from typing import List, Dict


# API base URL
BASE_URL = "http://localhost:5000/api"


def upload_sample_resumes() -> List[str]:
    """Upload sample resumes and return their IDs."""
    
    sample_resumes = [
        {
            "candidate_name": "Alice Johnson",
            "email": "alice.johnson@email.com",
            "phone": "+1-555-0101",
            "content": """
            Alice Johnson
            alice.johnson@email.com | +1-555-0101
            
            PROFESSIONAL SUMMARY
            Senior Software Engineer with 8 years of experience in full-stack development.
            Expert in Python, JavaScript, and cloud technologies.
            
            SKILLS
            Programming: Python, JavaScript, TypeScript, Java, SQL
            Frameworks: React, Django, Flask, Node.js, Express
            Cloud: AWS, Docker, Kubernetes, CI/CD
            Databases: PostgreSQL, MongoDB, Redis
            Tools: Git, Jenkins, Terraform
            
            EXPERIENCE
            Senior Software Engineer | Tech Corp | 2020-Present
            - Led development of microservices architecture using Python and Docker
            - Implemented CI/CD pipelines reducing deployment time by 60%
            - Mentored team of 5 junior developers
            
            Software Engineer | StartupXYZ | 2016-2020
            - Built RESTful APIs using Flask and Django
            - Developed React-based frontend applications
            - Managed AWS infrastructure
            
            EDUCATION
            BS Computer Science | University of Technology | 2016
            """
        },
        {
            "candidate_name": "Bob Smith",
            "email": "bob.smith@email.com",
            "phone": "+1-555-0102",
            "content": """
            Bob Smith
            bob.smith@email.com | +1-555-0102
            
            SUMMARY
            Data Scientist with 5 years experience in machine learning and data analysis.
            
            TECHNICAL SKILLS
            Languages: Python, R, SQL
            ML/AI: TensorFlow, PyTorch, scikit-learn, Keras
            Data: Pandas, NumPy, Matplotlib, Tableau
            Cloud: AWS, GCP
            
            PROFESSIONAL EXPERIENCE
            Data Scientist | Analytics Inc | 2019-Present (5 years)
            - Developed machine learning models for customer segmentation
            - Built recommendation systems using collaborative filtering
            - Created data visualization dashboards
            
            Junior Data Analyst | DataCorp | 2018-2019
            - Performed statistical analysis on large datasets
            - Created reports and presentations for stakeholders
            
            EDUCATION
            MS Data Science | State University | 2018
            BS Statistics | State University | 2016
            """
        },
        {
            "candidate_name": "Carol Davis",
            "email": "carol.davis@email.com",
            "phone": "+1-555-0103",
            "content": """
            Carol Davis
            carol.davis@email.com | +1-555-0103
            GitHub: github.com/caroldavis
            
            ABOUT ME
            Full-stack developer with 3 years of experience. Passionate about building
            scalable web applications and learning new technologies.
            
            TECHNICAL PROFICIENCIES
            Frontend: JavaScript, React, Vue, HTML, CSS
            Backend: Node.js, Express, Python, Flask
            Database: MySQL, MongoDB
            Tools: Git, Docker, VS Code
            
            WORK HISTORY
            Full Stack Developer | WebDev Agency | 2021-Present
            - Developed e-commerce platforms using MERN stack
            - Implemented responsive designs for mobile and desktop
            - Collaborated with designers and product managers
            
            Junior Developer | SmallStartup | 2020-2021
            - Built web applications using React and Node.js
            - Fixed bugs and improved application performance
            
            EDUCATION
            BS Software Engineering | Tech Institute | 2020
            """
        }
    ]
    
    print("Uploading sample resumes...")
    resume_ids = []
    
    for resume in sample_resumes:
        response = requests.post(f"{BASE_URL}/upload/resume", json=resume)
        if response.status_code == 200:
            data = response.json()
            resume_id = data['data']['resume_id']
            resume_ids.append(resume_id)
            print(f"✓ Uploaded: {resume['candidate_name']} (ID: {resume_id})")
        else:
            print(f"✗ Failed to upload: {resume['candidate_name']}")
    
    return resume_ids


def upload_sample_job() -> str:
    """Upload a sample job description and return its ID."""
    
    job_description = {
        "title": "Senior Python Developer",
        "description": """
        Senior Python Developer
        
        We are seeking an experienced Python Developer to join our growing team.
        
        REQUIREMENTS:
        - 5+ years of professional Python development experience
        - Strong experience with web frameworks (Django, Flask)
        - Proficiency in SQL and database design (PostgreSQL, MySQL)
        - Experience with RESTful API development
        - Knowledge of Docker and containerization
        - Familiarity with cloud platforms (AWS, Azure, or GCP)
        - Strong problem-solving skills and attention to detail
        - Excellent communication and teamwork abilities
        
        PREFERRED QUALIFICATIONS:
        - Experience with React or other frontend frameworks
        - Knowledge of CI/CD pipelines
        - Experience with microservices architecture
        - Familiarity with Redis or other caching systems
        - Understanding of Agile/Scrum methodologies
        
        RESPONSIBILITIES:
        - Design and develop scalable Python applications
        - Build and maintain RESTful APIs
        - Collaborate with cross-functional teams
        - Write clean, maintainable code with proper documentation
        - Participate in code reviews and mentoring
        - Troubleshoot and debug production issues
        """
    }
    
    print("\nUploading job description...")
    response = requests.post(f"{BASE_URL}/upload/job", json=job_description)
    
    if response.status_code == 200:
        data = response.json()
        job_id = data['data']['job_id']
        print(f"✓ Uploaded: {job_description['title']} (ID: {job_id})")
        return job_id
    else:
        print(f"✗ Failed to upload job description")
        return None


def screen_candidates(job_id: str, resume_ids: List[str] = None):
    """Screen candidates for a job."""
    
    print(f"\nScreening candidates for job {job_id}...")
    
    payload = {"job_id": job_id}
    if resume_ids:
        payload["resume_ids"] = resume_ids
    
    response = requests.post(f"{BASE_URL}/screen", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Screened {data['data']['candidates_screened']} candidates")
        return data['data']['results']
    else:
        print(f"✗ Screening failed: {response.text}")
        return None


def display_results(job_id: str):
    """Display screening results."""
    
    print(f"\nFetching results for job {job_id}...")
    response = requests.get(f"{BASE_URL}/results/{job_id}")
    
    if response.status_code != 200:
        print(f"✗ Failed to fetch results")
        return
    
    data = response.json()
    results = data['data']['results']
    
    print(f"\n{'='*80}")
    print(f"SCREENING RESULTS - Total Candidates: {len(results)}")
    print(f"{'='*80}\n")
    
    for result in results:
        print(f"Rank #{result['rank']}: {result['candidate_name']}")
        print(f"  Overall Score: {result['overall_score']:.2%}")
        print(f"  Skills Match: {result['skill_match_score']:.2%}")
        print(f"  Semantic Similarity: {result['semantic_similarity_score']:.2%}")
        print(f"  Experience Score: {result['experience_score']:.2%}")
        
        if result.get('matched_skills'):
            skills = result['matched_skills']
            if isinstance(skills, str):
                skills = json.loads(skills)
            print(f"  Matched Skills: {', '.join(skills[:5])}")
            if len(skills) > 5:
                print(f"                  (+{len(skills) - 5} more)")
        
        print(f"  Email: {result.get('email', 'N/A')}")
        print(f"  Experience: {result.get('experience_years', 0)} years")
        print()


def check_api_health():
    """Check if API is running."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def main():
    """Run the example workflow."""
    
    print("Resume Screening System - Example Usage")
    print("="*80)
    
    # Check if API is running
    if not check_api_health():
        print("\n❌ API is not running!")
        print("Please start the API first by running: python app.py")
        return
    
    print("✓ API is running\n")
    
    # Upload sample data
    resume_ids = upload_sample_resumes()
    job_id = upload_sample_job()
    
    if not resume_ids or not job_id:
        print("\n❌ Failed to upload sample data")
        return
    
    # Screen candidates
    results = screen_candidates(job_id, resume_ids)
    
    if not results:
        print("\n❌ Screening failed")
        return
    
    # Display results
    display_results(job_id)
    
    print("\n" + "="*80)
    print("Example completed successfully!")
    print("="*80)
    print("\nYou can now use the API endpoints:")
    print(f"  - GET  {BASE_URL}/health")
    print(f"  - GET  {BASE_URL}/stats")
    print(f"  - POST {BASE_URL}/upload/resume")
    print(f"  - POST {BASE_URL}/upload/job")
    print(f"  - POST {BASE_URL}/screen")
    print(f"  - GET  {BASE_URL}/results/<job_id>")
    print(f"  - GET  {BASE_URL}/resume/<resume_id>")
    print(f"  - GET  {BASE_URL}/job/<job_id>")


if __name__ == '__main__':
    main()
