"""
Flask REST API for Resume Screening System.
Provides endpoints for uploading resumes, job descriptions, and retrieving screening results.
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from typing import Dict, List
import json
import uuid
from datetime import datetime
import os

from src.preprocessing import TextPreprocessor
from src.skill_extraction import SkillExtractor
from src.embeddings import EmbeddingGenerator
from src.scoring import CandidateScorer
from src.database import Database
import config


class ResumeScreenerAPI:
    """Flask API wrapper for resume screening system."""
    
    def __init__(self):
        """Initialize the API with all required components."""
        # Set template and static folders
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
        
        self.app = Flask(__name__, 
                        template_folder=template_dir,
                        static_folder=static_dir)
        CORS(self.app)
        
        # Initialize components
        print("Initializing Resume Screener API...")
        self.preprocessor = TextPreprocessor(use_spacy=False)
        self.skill_extractor = SkillExtractor(use_spacy=False)
        self.embedding_generator = EmbeddingGenerator()
        self.scorer = CandidateScorer()
        self.db = Database()
        
        # Register routes
        self._register_routes()
        print("API initialized successfully!")
    
    def _register_routes(self):
        """Register all API endpoints."""
        
        @self.app.route('/')
        def index():
            """Serve the frontend."""
            return render_template('index.html')
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint."""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            })
        
        @self.app.route('/api/stats', methods=['GET'])
        def get_stats():
            """Get database statistics."""
            try:
                stats = self.db.get_stats()
                return jsonify({
                    'success': True,
                    'data': stats
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/upload/resume', methods=['POST'])
        def upload_resume():
            """
            Upload and process a resume.
            
            Expected JSON:
            {
                "resume_id": "optional_id",
                "candidate_name": "John Doe",
                "email": "john@example.com",
                "phone": "+1234567890",
                "content": "Resume text content..."
            }
            """
            try:
                data = request.get_json()
                
                # Validate required fields
                if not data.get('content'):
                    return jsonify({
                        'success': False,
                        'error': 'Resume content is required'
                    }), 400
                
                # Generate resume ID if not provided
                resume_id = data.get('resume_id') or str(uuid.uuid4())
                
                # Process resume
                result = self._process_resume(data, resume_id)
                
                return jsonify({
                    'success': True,
                    'data': result
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/upload/resumes/batch', methods=['POST'])
        def upload_resumes_batch():
            """
            Upload multiple resumes at once.
            
            Expected JSON:
            {
                "resumes": [
                    {"candidate_name": "...", "content": "..."},
                    ...
                ]
            }
            """
            try:
                data = request.get_json()
                resumes = data.get('resumes', [])
                
                if not resumes:
                    return jsonify({
                        'success': False,
                        'error': 'No resumes provided'
                    }), 400
                
                results = []
                for resume_data in resumes:
                    resume_id = resume_data.get('resume_id') or str(uuid.uuid4())
                    result = self._process_resume(resume_data, resume_id)
                    results.append(result)
                
                return jsonify({
                    'success': True,
                    'data': {
                        'processed': len(results),
                        'results': results
                    }
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/upload/job', methods=['POST'])
        def upload_job():
            """
            Upload and process a job description.
            
            Expected JSON:
            {
                "job_id": "optional_id",
                "title": "Senior Software Engineer",
                "description": "Job description text..."
            }
            """
            try:
                data = request.get_json()
                
                # Validate required fields
                if not data.get('description'):
                    return jsonify({
                        'success': False,
                        'error': 'Job description is required'
                    }), 400
                
                # Generate job ID if not provided
                job_id = data.get('job_id') or str(uuid.uuid4())
                
                # Process job description
                result = self._process_job(data, job_id)
                
                return jsonify({
                    'success': True,
                    'data': result
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/screen', methods=['POST'])
        def screen_resumes():
            """
            Screen resumes against a job description.
            
            Expected JSON:
            {
                "job_id": "job123",
                "resume_ids": ["resume1", "resume2", ...] (optional - if not provided, screen all)
            }
            """
            try:
                data = request.get_json()
                job_id = data.get('job_id')
                
                if not job_id:
                    return jsonify({
                        'success': False,
                        'error': 'job_id is required'
                    }), 400
                
                # Get job description
                job_data = self.db.get_job_description(job_id)
                if not job_data:
                    return jsonify({
                        'success': False,
                        'error': f'Job {job_id} not found'
                    }), 404
                
                # Get resumes to screen
                resume_ids = data.get('resume_ids')
                if resume_ids:
                    resumes = [self.db.get_resume(rid) for rid in resume_ids]
                    resumes = [r for r in resumes if r]  # Filter out None values
                else:
                    resumes = self.db.get_all_resumes()
                
                if not resumes:
                    return jsonify({
                        'success': False,
                        'error': 'No resumes found to screen'
                    }), 404
                
                # Perform screening
                results = self._screen_candidates(job_data, resumes)
                
                # Clear previous results and save new ones
                self.db.clear_screening_results(job_id)
                for result in results:
                    self.db.insert_screening_result(result)
                
                return jsonify({
                    'success': True,
                    'data': {
                        'job_id': job_id,
                        'candidates_screened': len(results),
                        'results': results
                    }
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/results/<job_id>', methods=['GET'])
        def get_results(job_id):
            """Get screening results for a job."""
            try:
                results = self.db.get_screening_results(job_id)
                
                # Parse JSON fields
                for result in results:
                    if result.get('matched_skills'):
                        try:
                            result['matched_skills'] = json.loads(result['matched_skills'])
                        except:
                            pass
                
                return jsonify({
                    'success': True,
                    'data': {
                        'job_id': job_id,
                        'total_candidates': len(results),
                        'results': results
                    }
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/resume/<resume_id>', methods=['GET'])
        def get_resume(resume_id):
            """Get resume details."""
            try:
                resume = self.db.get_resume(resume_id)
                
                if not resume:
                    return jsonify({
                        'success': False,
                        'error': 'Resume not found'
                    }), 404
                
                # Parse JSON fields
                if resume.get('extracted_skills'):
                    try:
                        resume['extracted_skills'] = json.loads(resume['extracted_skills'])
                    except:
                        pass
                
                # Don't include large fields
                resume.pop('embedding', None)
                
                return jsonify({
                    'success': True,
                    'data': resume
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/job/<job_id>', methods=['GET'])
        def get_job(job_id):
            """Get job description details."""
            try:
                job = self.db.get_job_description(job_id)
                
                if not job:
                    return jsonify({
                        'success': False,
                        'error': 'Job not found'
                    }), 404
                
                # Parse JSON fields
                if job.get('required_skills'):
                    try:
                        job['required_skills'] = json.loads(job['required_skills'])
                    except:
                return jsonify({
                    'success': True,
                    'data': job
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/jobs', methods=['GET'])
        def list_jobs():
            """List all job descriptions."""
            try:
                # This is a simplified version - you'd implement get_all_jobs in Database
                return jsonify({
                    'success': True,
                    'data': []
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
    
    def _process_resume(self, data: Dict, resume_id: str) -> Dict:
        """Process a resume and store in database."""
        content = data['content']
        
        # Extract contact info
        contact_info = self.preprocessor.extract_contact_info(content)
        
        # Clean text
        clean_text = self.preprocessor.preprocess(content, remove_stops=False)
        
        # Extract skills
        extracted_skills = self.skill_extractor.extract_from_text(content)
        
        # Extract experience
        experience_years = self.preprocessor.extract_years_of_experience(content)
        
        # Generate embedding
        embedding = self.embedding_generator.generate_embedding(clean_text)
        
        # Prepare data for database
        resume_data = {
            'resume_id': resume_id,
            'candidate_name': data.get('candidate_name') or contact_info.get('email', 'Unknown'),
            'email': data.get('email') or contact_info.get('email'),
            'phone': data.get('phone') or contact_info.get('phone'),
            'content': content,
            'extracted_skills': extracted_skills,
            'clean_text': clean_text,
            'embedding': self.embedding_generator.serialize_embedding(embedding),
            'experience_years': experience_years
        }
        
        # Save to database
        self.db.insert_resume(resume_data)
        
        return {
            'resume_id': resume_id,
            'candidate_name': resume_data['candidate_name'],
            'skills_extracted': len(extracted_skills),
            'experience_years': experience_years,
            'skills': extracted_skills
        }
    
    def _process_job(self, data: Dict, job_id: str) -> Dict:
        """Process a job description and store in database."""
        description = data['description']
        title = data.get('title', 'Untitled Position')
        
        # Clean text
        clean_text = self.preprocessor.preprocess(description, remove_stops=False)
        
        # Extract required skills
        required_skills = self.skill_extractor.extract_from_text(description)
        
        # Generate embedding
        embedding = self.embedding_generator.generate_embedding(clean_text)
        
        # Prepare data for database
        job_data = {
            'job_id': job_id,
            'title': title,
            'description': description,
            'required_skills': required_skills,
            'clean_text': clean_text,
            'embedding': self.embedding_generator.serialize_embedding(embedding)
        }
        
        # Save to database
        self.db.insert_job_description(job_data)
        
        return {
            'job_id': job_id,
            'title': title,
            'skills_required': len(required_skills),
            'skills': required_skills
        }
    
    def _screen_candidates(self, job_data: Dict, resumes: List[Dict]) -> List[Dict]:
        """Screen candidates against a job."""
        # Deserialize job embedding
        job_embedding = self.embedding_generator.deserialize_embedding(
            job_data.get('embedding')
        )
        
        # Parse job skills
        job_skills = job_data.get('required_skills')
        if isinstance(job_skills, str):
            job_skills = json.loads(job_skills)
        
        results = []
        
        for resume in resumes:
            # Deserialize resume embedding
            resume_embedding = self.embedding_generator.deserialize_embedding(
                resume.get('embedding')
            )
            
            # Parse resume skills
            resume_skills = resume.get('extracted_skills')
            if isinstance(resume_skills, str):
                resume_skills = json.loads(resume_skills)
            
            # Prepare data for scoring
            resume_scoring_data = {
                'extracted_skills': resume_skills,
                'experience_years': resume.get('experience_years', 0)
            }
            
            job_scoring_data = {
                'required_skills': job_skills
            }
            
            # Calculate scores
            scoring = self.scorer.score_candidate(
                resume_scoring_data,
                job_scoring_data,
                resume_embedding,
                job_embedding
            )
            
            # Create result
            result = {
                'job_id': job_data['job_id'],
                'resume_id': resume['resume_id'],
                'skill_match_score': round(scoring.skill_match_score, 4),
                'semantic_similarity_score': round(scoring.semantic_similarity_score, 4),
                'experience_score': round(scoring.experience_score, 4),
                'overall_score': round(scoring.overall_score, 4),
                'matched_skills': scoring.matched_skills,
                'rank': 0  # Will be assigned during ranking
            }
            
            results.append(result)
        
        # Rank candidates
        results = self.scorer.rank_candidates(results)
        
        return results
    
    def run(self, host: str = None, port: int = None, debug: bool = None):
        """
        Run the Flask application.
        
        Args:
            host: Host address
            port: Port number
            debug: Debug mode
        """
        host = host or config.FLASK_HOST
        port = port or config.FLASK_PORT
        debug = debug if debug is not None else config.FLASK_DEBUG
        
        print(f"\n{'='*60}")
        print(f"Resume Screener API Starting")
        print(f"{'='*60}")
        print(f"Host: {host}")
        print(f"Port: {port}")
        print(f"Debug: {debug}")
        print(f"{'='*60}\n")
        
        self.app.run(host=host, port=port, debug=debug)


def create_app():
    """Factory function to create Flask app."""
    api = ResumeScreenerAPI()
    return api.app


if __name__ == '__main__':
    api = ResumeScreenerAPI()
    api.run()
