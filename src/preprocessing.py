"""
Text preprocessing module for Resume Screening System.
Handles text cleaning, normalization, and preparation for NLP tasks.
"""

import re
import string
from typing import List, Dict, Optional
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
import spacy


class TextPreprocessor:
    """
    Handles text preprocessing operations including:
    - Text cleaning and normalization
    - Tokenization
    - Stop word removal
    - Lemmatization
    """
    
    def __init__(self, use_spacy: bool = True):
        """
        Initialize the text preprocessor.
        
        Args:
            use_spacy: Whether to use spaCy for advanced NLP (default: True)
        """
        self.use_spacy = use_spacy
        
        # Download required NLTK data
        self._download_nltk_resources()
        
        # Initialize NLTK components
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Initialize spaCy if requested
        if self.use_spacy:
            try:
                self.nlp = spacy.load('en_core_web_sm')
            except OSError:
                print("Warning: spaCy model not found. Run: python -m spacy download en_core_web_sm")
                self.use_spacy = False
    
    def _download_nltk_resources(self):
        """Download required NLTK resources if not already present."""
        resources = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']
        for resource in resources:
            try:
                nltk.data.find(f'tokenizers/{resource}')
            except LookupError:
                try:
                    nltk.download(resource, quiet=True)
                except:
                    pass
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text input
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove phone numbers
        text = re.sub(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', '', text)
        
        # Remove special characters but keep spaces and basic punctuation
        text = re.sub(r'[^\w\s\.\,\-]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def remove_stopwords(self, text: str, custom_stopwords: Optional[List[str]] = None) -> str:
        """
        Remove stop words from text.
        
        Args:
            text: Input text
            custom_stopwords: Additional stop words to remove
            
        Returns:
            Text with stop words removed
        """
        # Combine default and custom stop words
        stop_words = self.stop_words.copy()
        if custom_stopwords:
            stop_words.update(custom_stopwords)
        
        # Tokenize and filter
        words = word_tokenize(text)
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        return ' '.join(filtered_words)
    
    def lemmatize_text(self, text: str) -> str:
        """
        Lemmatize text to reduce words to their base form.
        
        Args:
            text: Input text
            
        Returns:
            Lemmatized text
        """
        words = word_tokenize(text)
        lemmatized_words = [self.lemmatizer.lemmatize(word) for word in words]
        return ' '.join(lemmatized_words)
    
    def preprocess(self, text: str, 
                   remove_stops: bool = True,
                   lemmatize: bool = True) -> str:
        """
        Full preprocessing pipeline.
        
        Args:
            text: Raw text input
            remove_stops: Whether to remove stop words
            lemmatize: Whether to lemmatize
            
        Returns:
            Fully preprocessed text
        """
        # Clean text
        text = self.clean_text(text)
        
        # Remove stop words if requested
        if remove_stops:
            text = self.remove_stopwords(text)
        
        # Lemmatize if requested
        if lemmatize:
            text = self.lemmatize_text(text)
        
        return text
    
    def extract_sentences(self, text: str) -> List[str]:
        """
        Extract sentences from text.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        return sent_tokenize(text)
    
    def extract_entities_spacy(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities using spaCy.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of entity types and their values
        """
        if not self.use_spacy:
            return {}
        
        doc = self.nlp(text)
        entities = {}
        
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            entities[ent.label_].append(ent.text)
        
        return entities
    
    def extract_noun_phrases(self, text: str) -> List[str]:
        """
        Extract noun phrases using spaCy.
        
        Args:
            text: Input text
            
        Returns:
            List of noun phrases
        """
        if not self.use_spacy:
            return []
        
        doc = self.nlp(text)
        noun_phrases = [chunk.text for chunk in doc.noun_chunks]
        return noun_phrases
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        return word_tokenize(text)
    
    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract contact information from resume text.
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary with email, phone, and other contact info
        """
        contact_info = {
            'email': None,
            'phone': None,
            'linkedin': None,
            'github': None
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Extract phone
        phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info['phone'] = phones[0].strip()
        
        # Extract LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w\-]+'
        linkedin = re.findall(linkedin_pattern, text.lower())
        if linkedin:
            contact_info['linkedin'] = linkedin[0]
        
        # Extract GitHub
        github_pattern = r'github\.com/[\w\-]+'
        github = re.findall(github_pattern, text.lower())
        if github:
            contact_info['github'] = github[0]
        
        return contact_info
    
    def extract_years_of_experience(self, text: str) -> float:
        """
        Extract years of experience from resume text.
        
        Args:
            text: Resume text
            
        Returns:
            Estimated years of experience
        """
        # Common patterns for experience
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)',
            r'(?:experience|exp)(?:\s+of)?\s+(\d+)\+?\s*(?:years?|yrs?)',
            r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:professional|work|industry)',
        ]
        
        years = []
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            years.extend([float(m) for m in matches])
        
        # Return maximum found or 0
        return max(years) if years else 0.0
    
    def normalize_skill(self, skill: str) -> str:
        """
        Normalize skill name for consistent matching.
        
        Args:
            skill: Skill name
            
        Returns:
            Normalized skill name
        """
        # Convert to lowercase
        skill = skill.lower().strip()
        
        # Remove special characters except + and #
        skill = re.sub(r'[^\w\s\+\#]', '', skill)
        
        # Standardize common variations
        skill_mappings = {
            'javascript': 'javascript',
            'js': 'javascript',
            'typescript': 'typescript',
            'ts': 'typescript',
            'c++': 'c++',
            'cpp': 'c++',
            'c#': 'c#',
            'csharp': 'c#',
            'python': 'python',
            'py': 'python',
            'node': 'nodejs',
            'node.js': 'nodejs',
            'react.js': 'react',
            'reactjs': 'react',
            'vue.js': 'vue',
            'vuejs': 'vue',
            'angular.js': 'angular',
            'angularjs': 'angular',
        }
        
        return skill_mappings.get(skill, skill)
