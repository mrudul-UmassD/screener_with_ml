"""
Initialize the src package.
Components are imported directly when needed to avoid circular imports
and compatibility issues.
"""

__all__ = [
    'TextPreprocessor',
    'SkillExtractor',
    'EmbeddingGenerator',
    'CandidateScorer',
    'Database'
]
