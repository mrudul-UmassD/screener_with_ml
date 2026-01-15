"""
Unit tests for Resume Screening System components.
"""

import unittest
import numpy as np
from src.preprocessing import TextPreprocessor
from src.skill_extraction import SkillExtractor
from src.embeddings import EmbeddingGenerator
from src.scoring import CandidateScorer


class TestTextPreprocessor(unittest.TestCase):
    """Test cases for TextPreprocessor."""
    
    def setUp(self):
        self.preprocessor = TextPreprocessor(use_spacy=False)
    
    def test_clean_text(self):
        """Test text cleaning."""
        text = "Check out https://example.com and email me@example.com!!!"
        cleaned = self.preprocessor.clean_text(text)
        
        self.assertNotIn('https://', cleaned)
        self.assertNotIn('me@example.com', cleaned)
        self.assertNotIn('!!!', cleaned)
    
    def test_extract_contact_info(self):
        """Test contact information extraction."""
        text = "John Doe, john.doe@email.com, +1-555-1234, linkedin.com/in/johndoe"
        contact = self.preprocessor.extract_contact_info(text)
        
        self.assertIsNotNone(contact['email'])
        self.assertIn('@', contact['email'])
    
    def test_extract_years_of_experience(self):
        """Test experience extraction."""
        text = "I have 5 years of experience in software development"
        years = self.preprocessor.extract_years_of_experience(text)
        
        self.assertEqual(years, 5.0)


class TestSkillExtractor(unittest.TestCase):
    """Test cases for SkillExtractor."""
    
    def setUp(self):
        self.extractor = SkillExtractor(use_spacy=False)
    
    def test_extract_from_text(self):
        """Test skill extraction from text."""
        text = """
        Skills: Python, JavaScript, React, Django, PostgreSQL, AWS, Docker
        Experience with machine learning and data science.
        """
        skills = self.extractor.extract_from_text(text)
        
        self.assertIn('python', skills)
        self.assertIn('javascript', skills)
        self.assertIn('react', skills)
        self.assertGreater(len(skills), 3)
    
    def test_calculate_skill_match(self):
        """Test skill matching calculation."""
        resume_skills = ['python', 'javascript', 'react', 'docker']
        job_skills = ['python', 'react', 'aws']
        
        score, matched = self.extractor.calculate_skill_match(resume_skills, job_skills)
        
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 1.0)
        self.assertIn('python', matched)
        self.assertIn('react', matched)
    
    def test_categorize_skills(self):
        """Test skill categorization."""
        skills = ['python', 'javascript', 'react', 'postgresql', 'aws', 'docker']
        categories = self.extractor.categorize_skills(skills)
        
        self.assertIn('programming_languages', categories)
        self.assertIn('frameworks', categories)


class TestEmbeddingGenerator(unittest.TestCase):
    """Test cases for EmbeddingGenerator."""
    
    @classmethod
    def setUpClass(cls):
        """Set up embedding generator once for all tests."""
        cls.generator = EmbeddingGenerator()
    
    def test_generate_embedding(self):
        """Test single embedding generation."""
        text = "Python developer with 5 years experience"
        embedding = self.generator.generate_embedding(text)
        
        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(len(embedding.shape), 1)
        self.assertGreater(len(embedding), 0)
    
    def test_generate_embeddings_batch(self):
        """Test batch embedding generation."""
        texts = [
            "Python developer",
            "Data scientist",
            "Frontend engineer"
        ]
        embeddings = self.generator.generate_embeddings(texts)
        
        self.assertEqual(len(embeddings), 3)
        self.assertEqual(embeddings.shape[0], 3)
    
    def test_compute_similarity(self):
        """Test similarity computation."""
        text1 = "Python developer with Django experience"
        text2 = "Django developer with Python skills"
        text3 = "Frontend React developer"
        
        emb1 = self.generator.generate_embedding(text1)
        emb2 = self.generator.generate_embedding(text2)
        emb3 = self.generator.generate_embedding(text3)
        
        sim_12 = self.generator.compute_similarity(emb1, emb2)
        sim_13 = self.generator.compute_similarity(emb1, emb3)
        
        # Similar texts should have higher similarity
        self.assertGreater(sim_12, sim_13)
    
    def test_serialization(self):
        """Test embedding serialization/deserialization."""
        text = "Test embedding serialization"
        embedding = self.generator.generate_embedding(text)
        
        # Serialize
        serialized = self.generator.serialize_embedding(embedding)
        self.assertIsInstance(serialized, bytes)
        
        # Deserialize
        deserialized = self.generator.deserialize_embedding(serialized)
        self.assertTrue(np.allclose(embedding, deserialized))


class TestCandidateScorer(unittest.TestCase):
    """Test cases for CandidateScorer."""
    
    def setUp(self):
        self.scorer = CandidateScorer()
        self.generator = EmbeddingGenerator()
    
    def test_calculate_skill_match_score(self):
        """Test skill match scoring."""
        resume_skills = ['python', 'django', 'postgresql', 'docker']
        job_skills = ['python', 'django', 'aws']
        
        score, matched = self.scorer.calculate_skill_match_score(resume_skills, job_skills)
        
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1.0)
        self.assertEqual(len(matched), 2)  # python and django
    
    def test_calculate_experience_score(self):
        """Test experience scoring."""
        # Candidate meets requirement
        score1 = self.scorer.calculate_experience_score(5.0, 5.0)
        self.assertGreaterEqual(score1, 0.9)
        
        # Candidate exceeds requirement
        score2 = self.scorer.calculate_experience_score(8.0, 5.0)
        self.assertGreaterEqual(score2, 1.0)
        
        # Candidate below requirement
        score3 = self.scorer.calculate_experience_score(3.0, 5.0)
        self.assertLess(score3, 1.0)
    
    def test_calculate_overall_score(self):
        """Test overall score calculation."""
        skill_score = 0.8
        semantic_score = 0.7
        experience_score = 0.9
        
        overall = self.scorer.calculate_overall_score(
            skill_score, semantic_score, experience_score
        )
        
        self.assertGreaterEqual(overall, 0)
        self.assertLessEqual(overall, 1.0)
    
    def test_rank_candidates(self):
        """Test candidate ranking."""
        candidates = [
            {'resume_id': '1', 'overall_score': 0.75},
            {'resume_id': '2', 'overall_score': 0.90},
            {'resume_id': '3', 'overall_score': 0.60}
        ]
        
        ranked = self.scorer.rank_candidates(candidates)
        
        # Check correct order
        self.assertEqual(ranked[0]['resume_id'], '2')
        self.assertEqual(ranked[1]['resume_id'], '1')
        self.assertEqual(ranked[2]['resume_id'], '3')
        
        # Check ranks assigned
        self.assertEqual(ranked[0]['rank'], 1)
        self.assertEqual(ranked[1]['rank'], 2)
        self.assertEqual(ranked[2]['rank'], 3)


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    run_tests()
