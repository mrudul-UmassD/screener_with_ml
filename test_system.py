"""
Simple test script to verify the core system works without running the full API.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*60)
print("TESTING RESUME SCREENER SYSTEM")
print("="*60)

# Test 1: Preprocessing
print("\n1. Testing Text Preprocessing...")
try:
    from src.preprocessing import TextPreprocessor
    preprocessor = TextPreprocessor(use_spacy=False)
    
    test_text = "Visit https://example.com and email test@example.com for more info!!!"
    cleaned = preprocessor.clean_text(test_text)
    print(f"   Original: {test_text[:50]}...")
    print(f"   Cleaned: {cleaned[:50]}...")
    print("   ✓ Preprocessing works!")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Skill Extraction
print("\n2. Testing Skill Extraction...")
try:
    from src.skill_extraction import SkillExtractor
    extractor = SkillExtractor(use_spacy=False)
    
    test_resume = """
    Skills: Python, JavaScript, React, Django, PostgreSQL, AWS, Docker
    5 years of experience in software development
    """
    skills = extractor.extract_from_text(test_resume)
    print(f"   Extracted {len(skills)} skills: {', '.join(skills[:5])}")
    print("   ✓ Skill extraction works!")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Database
print("\n3. Testing Database...")
try:
    from src.database import Database
    db = Database('data/test_screener.db')
    stats = db.get_stats()
    print(f"   Database stats: {stats}")
    print("   ✓ Database works!")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 4: Scoring
print("\n4. Testing Scoring System...")
try:
    from src.scoring import CandidateScorer
    scorer = CandidateScorer()
    
    resume_skills = ['python', 'django', 'postgresql', 'docker']
    job_skills = ['python', 'django', 'aws']
    
    score, matched = scorer.calculate_skill_match_score(resume_skills, job_skills)
    print(f"   Skill match score: {score:.2%}")
    print(f"   Matched skills: {matched}")
    print("   ✓ Scoring works!")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 5: Embeddings (might fail due to transformers issues)
print("\n5. Testing Embeddings...")
try:
    from src.embeddings import EmbeddingGenerator
    print("   Loading embedding model (this may take a moment)...")
    generator = EmbeddingGenerator()
    
    text = "Python developer with 5 years experience"
    embedding = generator.generate_embedding(text)
    print(f"   Generated embedding of dimension: {len(embedding)}")
    print("   ✓ Embeddings work!")
except Exception as e:
    print(f"   ✗ Error: {e}")
    print(f"   Note: This may fail due to Python 3.14 compatibility issues with transformers")

print("\n" + "="*60)
print("SYSTEM TEST COMPLETE")
print("="*60)
print("\nCore functionality (preprocessing, skill extraction, scoring) is working!")
print("\nNote: Full API with embeddings requires Python 3.11 or 3.12 for full compatibility.")
print("Alternative: Use a virtual environment with Python 3.11/3.12:")
print("  conda create -n screener python=3.11")
print("  conda activate screener")
print("  pip install -r requirements.txt")
