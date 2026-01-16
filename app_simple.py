"""
Simplified app launcher that works around Python 3.14 compatibility issues.
This version delays the problematic imports until they're actually needed.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*60)
print("Resume Screener API - Starting...")
print("="*60)

try:
    from flask import Flask, render_template, jsonify, request
    from flask_cors import CORS
    import json
    
    # Create Flask app
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    CORS(app)
    
    # Initialize components lazily
    db = None
    preprocessor = None
    skill_extractor = None
    scorer = None
    embedding_generator = None
    
    def init_components():
        """Initialize ML components only when needed."""
        global db, preprocessor, skill_extractor, scorer, embedding_generator
        
        if db is None:
            print("Initializing components...")
            from src.database import Database
            from src.preprocessing import TextPreprocessor
            from src.skill_extraction import SkillExtractor
            from src.scoring import CandidateScorer
            
            db = Database()
            preprocessor = TextPreprocessor(use_spacy=False)
            skill_extractor = SkillExtractor(use_spacy=False)
            scorer = CandidateScorer()
            print("✓ Core components initialized")
            
    def init_embeddings():
        """Initialize embedding generator separately (slow)."""
        global embedding_generator
        if embedding_generator is None:
            print("Loading embedding model (this may take a moment)...")
            from src.embeddings import EmbeddingGenerator
            embedding_generator = EmbeddingGenerator()
            print("✓ Embedding model loaded")
    
    # Routes
    @app.route('/')
    def index():
        """Serve the frontend."""
        return render_template('index.html')
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        from datetime import datetime
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    
    @app.route('/api/stats', methods=['GET'])
    def get_stats():
        """Get database statistics."""
        try:
            init_components()
            stats = db.get_stats()
            return jsonify({
                'success': True,
                'data': stats
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/upload/resume', methods=['POST'])
    def upload_resume():
        """Upload and process a resume."""
        try:
            init_components()
            init_embeddings()
            
            data = request.get_json()
            
            if not data.get('content'):
                return jsonify({
                    'success': False,
                    'error': 'Resume content is required'
                }), 400
            
            resume_id = data.get('resume_id') or str(__import__('uuid').uuid4())
            content = data['content']
            
            # Extract contact info
            contact_info = preprocessor.extract_contact_info(content)
            
            # Clean text
            clean_text = preprocessor.preprocess(content, remove_stops=False)
            
            # Extract skills
            extracted_skills = skill_extractor.extract_from_text(content)
            
            # Extract experience
            experience_years = preprocessor.extract_years_of_experience(content)
            
            # Generate embedding
            embedding = embedding_generator.generate_embedding(clean_text)
            
            # Save to database
            resume_data = {
                'resume_id': resume_id,
                'candidate_name': data.get('candidate_name') or contact_info.get('email', 'Unknown'),
                'email': data.get('email') or contact_info.get('email'),
                'phone': data.get('phone') or contact_info.get('phone'),
                'content': content,
                'extracted_skills': extracted_skills,
                'clean_text': clean_text,
                'embedding': embedding_generator.serialize_embedding(embedding),
                'experience_years': experience_years
            }
            
            db.insert_resume(resume_data)
            
            return jsonify({
                'success': True,
                'data': {
                    'resume_id': resume_id,
                    'candidate_name': resume_data['candidate_name'],
                    'skills_extracted': len(extracted_skills),
                    'experience_years': experience_years,
                    'skills': extracted_skills
                }
            })
            
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/upload/job', methods=['POST'])
    def upload_job():
        """Upload and process a job description."""
        try:
            init_components()
            init_embeddings()
            
            data = request.get_json()
            
            if not data.get('description'):
                return jsonify({
                    'success': False,
                    'error': 'Job description is required'
                }), 400
            
            job_id = data.get('job_id') or str(__import__('uuid').uuid4())
            description = data['description']
            title = data.get('title', 'Untitled Position')
            
            # Clean text
            clean_text = preprocessor.preprocess(description, remove_stops=False)
            
            # Extract required skills
            required_skills = skill_extractor.extract_from_text(description)
            
            # Generate embedding
            embedding = embedding_generator.generate_embedding(clean_text)
            
            # Save to database
            job_data = {
                'job_id': job_id,
                'title': title,
                'description': description,
                'required_skills': required_skills,
                'clean_text': clean_text,
                'embedding': embedding_generator.serialize_embedding(embedding)
            }
            
            db.insert_job_description(job_data)
            
            return jsonify({
                'success': True,
                'data': {
                    'job_id': job_id,
                    'title': title,
                    'skills_required': len(required_skills),
                    'skills': required_skills
                }
            })
            
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/jobs', methods=['GET'])
    def list_jobs():
        """List all job descriptions."""
        try:
            init_components()
            
            # Get all jobs from database
            jobs = db.get_all_jobs()
            
            # Parse JSON fields for each job
            for job in jobs:
                if job.get('required_skills'):
                    try:
                        job['required_skills'] = json.loads(job['required_skills'])
                    except:
                        pass
            
            return jsonify({
                'success': True,
                'data': jobs
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/screen', methods=['POST'])
    def screen_candidates():
        """Screen resumes against a job description."""
        try:
            init_components()
            init_embeddings()
            
            data = request.get_json()
            job_id = data.get('job_id')
            
            if not job_id:
                return jsonify({
                    'success': False,
                    'error': 'job_id is required'
                }), 400
            
            # Get job description
            job_data = db.get_job_description(job_id)
            if not job_data:
                return jsonify({
                    'success': False,
                    'error': f'Job {job_id} not found'
                }), 404
            
            # Get all resumes
            resumes = db.get_all_resumes()
            
            if not resumes:
                return jsonify({
                    'success': False,
                    'error': 'No resumes found to screen'
                }), 404
            
            # Screen candidates
            job_embedding = embedding_generator.deserialize_embedding(job_data.get('embedding'))
            job_skills = job_data.get('required_skills')
            if isinstance(job_skills, str):
                job_skills = json.loads(job_skills)
            
            results = []
            for resume in resumes:
                resume_embedding = embedding_generator.deserialize_embedding(resume.get('embedding'))
                resume_skills = resume.get('extracted_skills')
                if isinstance(resume_skills, str):
                    resume_skills = json.loads(resume_skills)
                
                resume_scoring_data = {
                    'extracted_skills': resume_skills,
                    'experience_years': resume.get('experience_years', 0)
                }
                
                job_scoring_data = {
                    'required_skills': job_skills
                }
                
                scoring = scorer.score_candidate(
                    resume_scoring_data,
                    job_scoring_data,
                    resume_embedding,
                    job_embedding
                )
                
                result = {
                    'job_id': job_data['job_id'],
                    'resume_id': resume['resume_id'],
                    'skill_match_score': round(scoring.skill_match_score, 4),
                    'semantic_similarity_score': round(scoring.semantic_similarity_score, 4),
                    'experience_score': round(scoring.experience_score, 4),
                    'overall_score': round(scoring.overall_score, 4),
                    'matched_skills': scoring.matched_skills,
                    'rank': 0
                }
                
                results.append(result)
            
            # Rank candidates
            results = scorer.rank_candidates(results)
            
            # Save results
            db.clear_screening_results(job_id)
            for result in results:
                db.insert_screening_result(result)
            
            return jsonify({
                'success': True,
                'data': {
                    'job_id': job_id,
                    'candidates_screened': len(results),
                    'results': results
                }
            })
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/results/<job_id>', methods=['GET'])
    def get_results(job_id):
        """Get screening results for a job."""
        try:
            init_components()
            results = db.get_screening_results(job_id)
            
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
    
    # Run the app
    print("\n" + "="*60)
    print("Resume Screener API Starting")
    print("="*60)
    print(f"Server: http://localhost:5000")
    print(f"API Docs: http://localhost:5000 (Web Interface)")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)

except KeyboardInterrupt:
    print("\n\nShutting down...")
except Exception as e:
    print(f"\n✗ Error starting server: {e}")
    import traceback
    traceback.print_exc()
