"""
Skill extraction module for Resume Screening System.
Combines keyword matching with NLP-based entity recognition.
"""

import re
from typing import List, Set, Dict, Tuple
import spacy
from config import SKILL_KEYWORDS
from src.preprocessing import TextPreprocessor


class SkillExtractor:
    """
    Extracts skills from resumes and job descriptions using:
    1. Keyword matching against a predefined skill database
    2. NLP-based entity recognition
    3. Contextual pattern matching
    """
    
    def __init__(self, custom_skills: Set[str] = None, use_spacy: bool = True):
        """
        Initialize skill extractor.
        
        Args:
            custom_skills: Additional skill keywords to include
            use_spacy: Whether to use spaCy for NLP-based extraction
        """
        # Combine default and custom skills
        self.skill_keywords = SKILL_KEYWORDS.copy()
        if custom_skills:
            self.skill_keywords.update(custom_skills)
        
        # Normalize all skill keywords
        self.skill_keywords = {skill.lower().strip() for skill in self.skill_keywords}
        
        # Initialize preprocessor
        self.preprocessor = TextPreprocessor(use_spacy=use_spacy)
        self.use_spacy = use_spacy
        
        # Load spaCy model if available
        if use_spacy:
            try:
                self.nlp = spacy.load('en_core_web_sm')
            except OSError:
                print("Warning: spaCy model not found. Using keyword matching only.")
                self.use_spacy = False
        
        # Compile regex patterns for common skill formats
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for skill extraction."""
        # Pattern for skills sections
        self.section_patterns = [
            r'(?:technical\s+)?skills?(?:\s+and\s+technologies)?[:\s]+([^\.]+)',
            r'(?:core\s+)?competencies[:\s]+([^\.]+)',
            r'technologies[:\s]+([^\.]+)',
            r'expertise[:\s]+([^\.]+)',
            r'proficient\s+in[:\s]+([^\.]+)',
            r'experienced\s+(?:in|with)[:\s]+([^\.]+)',
        ]
        
        # Compile patterns
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.section_patterns
        ]
    
    def extract_from_text(self, text: str) -> List[str]:
        """
        Extract skills from text using multiple methods.
        
        Args:
            text: Input text (resume or job description)
            
        Returns:
            List of extracted skills
        """
        skills = set()
        
        # Method 1: Keyword matching
        skills.update(self._extract_by_keywords(text))
        
        # Method 2: Section-based extraction
        skills.update(self._extract_from_sections(text))
        
        # Method 3: NLP-based extraction (if spaCy is available)
        if self.use_spacy:
            skills.update(self._extract_by_nlp(text))
        
        # Method 4: Pattern-based extraction
        skills.update(self._extract_by_patterns(text))
        
        return sorted(list(skills))
    
    def _extract_by_keywords(self, text: str) -> Set[str]:
        """
        Extract skills by matching against keyword database.
        
        Args:
            text: Input text
            
        Returns:
            Set of matched skills
        """
        text_lower = text.lower()
        matched_skills = set()
        
        for skill in self.skill_keywords:
            # Use word boundaries for accurate matching
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                matched_skills.add(skill)
        
        return matched_skills
    
    def _extract_from_sections(self, text: str) -> Set[str]:
        """
        Extract skills from dedicated skills sections.
        
        Args:
            text: Input text
            
        Returns:
            Set of extracted skills
        """
        skills = set()
        
        for pattern in self.compiled_patterns:
            matches = pattern.findall(text)
            for match in matches:
                # Split by common delimiters
                skill_list = re.split(r'[,;|•\n\t]', match)
                for skill in skill_list:
                    skill = skill.strip().lower()
                    # Check if extracted skill is in our database
                    if skill in self.skill_keywords:
                        skills.add(skill)
                    # Also check individual words
                    for word in skill.split():
                        word = word.strip()
                        if word in self.skill_keywords and len(word) > 2:
                            skills.add(word)
        
        return skills
    
    def _extract_by_nlp(self, text: str) -> Set[str]:
        """
        Extract skills using NLP techniques (entity recognition, noun phrases).
        
        Args:
            text: Input text
            
        Returns:
            Set of extracted skills
        """
        if not self.use_spacy:
            return set()
        
        skills = set()
        doc = self.nlp(text)
        
        # Extract from named entities
        for ent in doc.ents:
            ent_text = ent.text.lower().strip()
            if ent_text in self.skill_keywords:
                skills.add(ent_text)
        
        # Extract from noun phrases
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower().strip()
            if chunk_text in self.skill_keywords:
                skills.add(chunk_text)
            # Check individual words in chunk
            for token in chunk:
                token_text = token.text.lower().strip()
                if token_text in self.skill_keywords and len(token_text) > 2:
                    skills.add(token_text)
        
        return skills
    
    def _extract_by_patterns(self, text: str) -> Set[str]:
        """
        Extract skills using contextual patterns.
        
        Args:
            text: Input text
            
        Returns:
            Set of extracted skills
        """
        skills = set()
        text_lower = text.lower()
        
        # Common patterns indicating skills
        context_patterns = [
            r'(?:proficient|skilled|experienced|expert)\s+(?:in|with)\s+([^,\.]+)',
            r'(?:knowledge|understanding)\s+of\s+([^,\.]+)',
            r'(?:working\s+)?(?:experience|exposure)\s+(?:with|in)\s+([^,\.]+)',
            r'strong\s+(?:background|foundation)\s+in\s+([^,\.]+)',
            r'hands-on\s+(?:experience\s+)?(?:with|in)\s+([^,\.]+)',
        ]
        
        for pattern in context_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                # Extract potential skills from the matched text
                tokens = re.split(r'[,;|•\n\t\s]+', match)
                for token in tokens:
                    token = token.strip()
                    if token in self.skill_keywords and len(token) > 2:
                        skills.add(token)
        
        return skills
    
    def calculate_skill_match(self, resume_skills: List[str], 
                            job_skills: List[str]) -> Tuple[float, List[str]]:
        """
        Calculate skill match score between resume and job description.
        
        Args:
            resume_skills: Skills extracted from resume
            job_skills: Skills required for job
            
        Returns:
            Tuple of (match_score, matched_skills)
        """
        if not job_skills:
            return 0.0, []
        
        resume_set = set(skill.lower() for skill in resume_skills)
        job_set = set(skill.lower() for skill in job_skills)
        
        # Find matched skills
        matched = resume_set.intersection(job_set)
        
        # Calculate match percentage
        match_score = len(matched) / len(job_set) if job_set else 0.0
        
        return match_score, sorted(list(matched))
    
    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """
        Categorize skills into different types.
        
        Args:
            skills: List of skills
            
        Returns:
            Dictionary of skill categories
        """
        categories = {
            'programming_languages': [],
            'frameworks': [],
            'databases': [],
            'cloud': [],
            'tools': [],
            'soft_skills': [],
            'other': []
        }
        
        # Define category keywords
        prog_langs = {'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 
                     'ruby', 'go', 'rust', 'php', 'swift', 'kotlin', 'scala', 'r'}
        
        frameworks = {'react', 'angular', 'vue', 'django', 'flask', 'spring', 
                     'nodejs', 'express', 'tensorflow', 'pytorch', 'keras'}
        
        databases = {'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 
                    'oracle', 'sqlite', 'dynamodb', 'elasticsearch'}
        
        cloud = {'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible'}
        
        tools = {'git', 'github', 'gitlab', 'jenkins', 'ci/cd', 'linux', 'unix'}
        
        soft_skills = {'leadership', 'communication', 'teamwork', 'problem solving',
                      'critical thinking', 'project management', 'agile', 'scrum'}
        
        # Categorize each skill
        for skill in skills:
            skill_lower = skill.lower()
            if skill_lower in prog_langs:
                categories['programming_languages'].append(skill)
            elif skill_lower in frameworks:
                categories['frameworks'].append(skill)
            elif skill_lower in databases:
                categories['databases'].append(skill)
            elif skill_lower in cloud:
                categories['cloud'].append(skill)
            elif skill_lower in tools:
                categories['tools'].append(skill)
            elif skill_lower in soft_skills:
                categories['soft_skills'].append(skill)
            else:
                categories['other'].append(skill)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def extract_required_vs_preferred(self, job_text: str) -> Dict[str, List[str]]:
        """
        Distinguish between required and preferred skills in job description.
        
        Args:
            job_text: Job description text
            
        Returns:
            Dictionary with 'required' and 'preferred' skill lists
        """
        result = {
            'required': [],
            'preferred': []
        }
        
        # Patterns for required skills
        required_patterns = [
            r'(?:required|must\s+have|mandatory|essential)[:\s]+([^\.]+)',
            r'requirements?[:\s]+([^\.]+)',
        ]
        
        # Patterns for preferred skills
        preferred_patterns = [
            r'(?:preferred|nice\s+to\s+have|bonus|desired)[:\s]+([^\.]+)',
            r'(?:plus|advantage)[:\s]+([^\.]+)',
        ]
        
        # Extract required skills
        for pattern in required_patterns:
            matches = re.findall(pattern, job_text, re.IGNORECASE)
            for match in matches:
                skills = self._extract_by_keywords(match)
                result['required'].extend(skills)
        
        # Extract preferred skills
        for pattern in preferred_patterns:
            matches = re.findall(pattern, job_text, re.IGNORECASE)
            for match in matches:
                skills = self._extract_by_keywords(match)
                result['preferred'].extend(skills)
        
        # If no specific sections found, all skills are considered required
        if not result['required'] and not result['preferred']:
            all_skills = self.extract_from_text(job_text)
            result['required'] = all_skills
        
        # Remove duplicates
        result['required'] = list(set(result['required']))
        result['preferred'] = list(set(result['preferred']))
        
        return result
