"""
Scoring and ranking module for Resume Screening System.
Combines multiple scoring methods to rank candidates.
"""

import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
import config


@dataclass
class ScoringComponents:
    """Container for individual scoring components."""
    skill_match_score: float
    semantic_similarity_score: float
    experience_score: float
    overall_score: float
    matched_skills: List[str]


class CandidateScorer:
    """
    Scores and ranks candidates based on multiple criteria:
    1. Skill match score (keyword-based matching)
    2. Semantic similarity score (embedding-based)
    3. Experience score (years of experience)
    """
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize the scorer with custom weights.
        
        Args:
            weights: Dictionary with scoring weights
                    Default: {'skill_match': 0.4, 'semantic_similarity': 0.4, 'experience': 0.2}
        """
        self.weights = weights or config.WEIGHTS
        
        # Ensure weights sum to 1.0
        total_weight = sum(self.weights.values())
        if not np.isclose(total_weight, 1.0):
            # Normalize weights
            self.weights = {k: v / total_weight for k, v in self.weights.items()}
    
    def calculate_skill_match_score(self, resume_skills: List[str],
                                   job_skills: List[str]) -> Tuple[float, List[str]]:
        """
        Calculate skill match score between resume and job requirements.
        
        Args:
            resume_skills: Skills extracted from resume
            job_skills: Required skills from job description
            
        Returns:
            Tuple of (score, matched_skills)
        """
        if not job_skills:
            return 1.0, []
        
        resume_set = set(skill.lower() for skill in resume_skills)
        job_set = set(skill.lower() for skill in job_skills)
        
        # Find matched skills
        matched = resume_set.intersection(job_set)
        
        # Calculate Jaccard similarity
        union = resume_set.union(job_set)
        jaccard_score = len(matched) / len(union) if union else 0.0
        
        # Calculate coverage (what percentage of required skills are met)
        coverage_score = len(matched) / len(job_set) if job_set else 0.0
        
        # Combined score (weighted average favoring coverage)
        skill_score = 0.7 * coverage_score + 0.3 * jaccard_score
        
        return skill_score, sorted(list(matched))
    
    def calculate_semantic_similarity(self, resume_embedding: np.ndarray,
                                    job_embedding: np.ndarray) -> float:
        """
        Calculate semantic similarity using cosine similarity of embeddings.
        
        Args:
            resume_embedding: Resume embedding vector
            job_embedding: Job description embedding vector
            
        Returns:
            Similarity score (0 to 1)
        """
        # Cosine similarity
        dot_product = np.dot(resume_embedding, job_embedding)
        norm1 = np.linalg.norm(resume_embedding)
        norm2 = np.linalg.norm(job_embedding)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Normalize to 0-1 range (cosine similarity is -1 to 1)
        normalized_similarity = (similarity + 1) / 2
        
        return normalized_similarity
    
    def calculate_experience_score(self, candidate_years: float,
                                  required_years: float = None,
                                  max_years: float = 20.0) -> float:
        """
        Calculate experience score based on years of experience.
        
        Args:
            candidate_years: Candidate's years of experience
            required_years: Required years of experience (optional)
            max_years: Maximum years to consider for normalization
            
        Returns:
            Experience score (0 to 1)
        """
        if required_years is None:
            # If no requirement specified, normalize by max_years
            return min(candidate_years / max_years, 1.0)
        
        if candidate_years >= required_years:
            # Meets or exceeds requirement
            # Cap the benefit of extra experience
            excess_years = candidate_years - required_years
            bonus = min(excess_years / 5, 0.2)  # Max 0.2 bonus for extra experience
            return min(1.0 + bonus, 1.0)
        else:
            # Below requirement, penalize proportionally
            return candidate_years / required_years
    
    def calculate_overall_score(self, skill_score: float,
                              semantic_score: float,
                              experience_score: float) -> float:
        """
        Calculate weighted overall score.
        
        Args:
            skill_score: Skill match score
            semantic_score: Semantic similarity score
            experience_score: Experience score
            
        Returns:
            Overall weighted score (0 to 1)
        """
        overall = (
            self.weights['skill_match'] * skill_score +
            self.weights['semantic_similarity'] * semantic_score +
            self.weights['experience'] * experience_score
        )
        
        return overall
    
    def score_candidate(self, 
                       resume_data: Dict,
                       job_data: Dict,
                       resume_embedding: np.ndarray,
                       job_embedding: np.ndarray) -> ScoringComponents:
        """
        Calculate all scoring components for a candidate.
        
        Args:
            resume_data: Resume information dictionary
            job_data: Job description information dictionary
            resume_embedding: Resume embedding vector
            job_embedding: Job embedding vector
            
        Returns:
            ScoringComponents object with all scores
        """
        # Extract data
        resume_skills = resume_data.get('extracted_skills', [])
        job_skills = job_data.get('required_skills', [])
        candidate_years = resume_data.get('experience_years', 0.0)
        required_years = job_data.get('required_experience_years', None)
        
        # Calculate individual scores
        skill_score, matched_skills = self.calculate_skill_match_score(
            resume_skills, job_skills
        )
        
        semantic_score = self.calculate_semantic_similarity(
            resume_embedding, job_embedding
        )
        
        experience_score = self.calculate_experience_score(
            candidate_years, required_years
        )
        
        # Calculate overall score
        overall = self.calculate_overall_score(
            skill_score, semantic_score, experience_score
        )
        
        return ScoringComponents(
            skill_match_score=skill_score,
            semantic_similarity_score=semantic_score,
            experience_score=experience_score,
            overall_score=overall,
            matched_skills=matched_skills
        )
    
    def rank_candidates(self, scoring_results: List[Dict]) -> List[Dict]:
        """
        Rank candidates by overall score and assign ranks.
        
        Args:
            scoring_results: List of candidate scoring results
            
        Returns:
            Sorted list with rank assignments
        """
        # Sort by overall score (descending)
        sorted_results = sorted(
            scoring_results,
            key=lambda x: x['overall_score'],
            reverse=True
        )
        
        # Assign ranks
        for rank, result in enumerate(sorted_results, start=1):
            result['rank'] = rank
        
        return sorted_results
    
    def filter_by_threshold(self, scored_candidates: List[Dict],
                          threshold: float = None) -> List[Dict]:
        """
        Filter candidates by minimum score threshold.
        
        Args:
            scored_candidates: List of scored candidates
            threshold: Minimum overall score (default from config)
            
        Returns:
            Filtered list of candidates
        """
        threshold = threshold or config.SIMILARITY_THRESHOLD
        
        return [
            candidate for candidate in scored_candidates
            if candidate.get('overall_score', 0) >= threshold
        ]
    
    def get_top_k_candidates(self, scored_candidates: List[Dict],
                           k: int = 10) -> List[Dict]:
        """
        Get top K candidates by score.
        
        Args:
            scored_candidates: List of scored candidates
            k: Number of top candidates to return
            
        Returns:
            Top K candidates
        """
        # Sort by overall score
        sorted_candidates = sorted(
            scored_candidates,
            key=lambda x: x.get('overall_score', 0),
            reverse=True
        )
        
        return sorted_candidates[:k]
    
    def generate_ranking_explanation(self, scoring: ScoringComponents) -> str:
        """
        Generate human-readable explanation of ranking.
        
        Args:
            scoring: ScoringComponents object
            
        Returns:
            Explanation string
        """
        explanations = []
        
        # Skill match explanation
        skill_pct = scoring.skill_match_score * 100
        if skill_pct >= 80:
            explanations.append(f"Excellent skill match ({skill_pct:.0f}%)")
        elif skill_pct >= 60:
            explanations.append(f"Good skill match ({skill_pct:.0f}%)")
        elif skill_pct >= 40:
            explanations.append(f"Moderate skill match ({skill_pct:.0f}%)")
        else:
            explanations.append(f"Limited skill match ({skill_pct:.0f}%)")
        
        # Semantic similarity explanation
        semantic_pct = scoring.semantic_similarity_score * 100
        if semantic_pct >= 75:
            explanations.append(f"Strong semantic alignment ({semantic_pct:.0f}%)")
        elif semantic_pct >= 50:
            explanations.append(f"Moderate semantic alignment ({semantic_pct:.0f}%)")
        else:
            explanations.append(f"Weak semantic alignment ({semantic_pct:.0f}%)")
        
        # Experience explanation
        exp_pct = scoring.experience_score * 100
        if exp_pct >= 100:
            explanations.append("Meets or exceeds experience requirements")
        elif exp_pct >= 75:
            explanations.append("Close to experience requirements")
        else:
            explanations.append("Below experience requirements")
        
        # Matched skills
        if scoring.matched_skills:
            skill_list = ', '.join(scoring.matched_skills[:5])
            if len(scoring.matched_skills) > 5:
                skill_list += f" (+{len(scoring.matched_skills) - 5} more)"
            explanations.append(f"Matched skills: {skill_list}")
        
        return " | ".join(explanations)
    
    def compare_candidates(self, candidate1: Dict, candidate2: Dict) -> Dict:
        """
        Compare two candidates and highlight differences.
        
        Args:
            candidate1: First candidate's data
            candidate2: Second candidate's data
            
        Returns:
            Comparison results dictionary
        """
        comparison = {
            'skill_match_diff': candidate1.get('skill_match_score', 0) - 
                               candidate2.get('skill_match_score', 0),
            'semantic_diff': candidate1.get('semantic_similarity_score', 0) - 
                           candidate2.get('semantic_similarity_score', 0),
            'experience_diff': candidate1.get('experience_score', 0) - 
                             candidate2.get('experience_score', 0),
            'overall_diff': candidate1.get('overall_score', 0) - 
                          candidate2.get('overall_score', 0)
        }
        
        # Determine stronger candidate
        if comparison['overall_diff'] > 0.05:
            comparison['recommendation'] = 'candidate1'
        elif comparison['overall_diff'] < -0.05:
            comparison['recommendation'] = 'candidate2'
        else:
            comparison['recommendation'] = 'tie'
        
        return comparison
