"""
Embedding generation module for Resume Screening System.
Uses sentence-transformers to generate semantic embeddings for text.
"""

import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer
import pickle
import config


class EmbeddingGenerator:
    """
    Generates semantic embeddings using sentence-transformers.
    Supports various transformer models for encoding text into dense vectors.
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: Name of the sentence-transformer model to use
                       Default: all-MiniLM-L6-v2 (fast and accurate)
        """
        self.model_name = model_name or config.EMBEDDING_MODEL
        
        # Load the sentence transformer model
        print(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        print(f"Model loaded successfully. Embedding dimension: {self.get_embedding_dimension()}")
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by the model.
        
        Returns:
            Embedding dimension size
        """
        return self.model.get_sentence_embedding_dimension()
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Numpy array containing the embedding vector
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return np.zeros(self.get_embedding_dimension())
        
        # Generate embedding
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def generate_embeddings(self, texts: List[str], 
                          batch_size: int = 32,
                          show_progress: bool = False) -> np.ndarray:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            batch_size: Number of texts to process at once
            show_progress: Whether to show progress bar
            
        Returns:
            Numpy array of shape (n_texts, embedding_dim)
        """
        if not texts:
            return np.array([])
        
        # Generate embeddings in batches
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        
        return embeddings
    
    def compute_similarity(self, embedding1: np.ndarray, 
                          embedding2: np.ndarray,
                          method: str = 'cosine') -> float:
        """
        Compute similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            method: Similarity method ('cosine', 'dot', 'euclidean')
            
        Returns:
            Similarity score
        """
        if method == 'cosine':
            # Cosine similarity
            dot_product = np.dot(embedding1, embedding2)
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        
        elif method == 'dot':
            # Dot product similarity
            return np.dot(embedding1, embedding2)
        
        elif method == 'euclidean':
            # Euclidean distance (converted to similarity)
            distance = np.linalg.norm(embedding1 - embedding2)
            # Convert distance to similarity (0 to 1 range)
            return 1 / (1 + distance)
        
        else:
            raise ValueError(f"Unknown similarity method: {method}")
    
    def compute_similarity_matrix(self, embeddings1: np.ndarray,
                                 embeddings2: np.ndarray,
                                 method: str = 'cosine') -> np.ndarray:
        """
        Compute similarity matrix between two sets of embeddings.
        
        Args:
            embeddings1: First set of embeddings (n1 x dim)
            embeddings2: Second set of embeddings (n2 x dim)
            method: Similarity method
            
        Returns:
            Similarity matrix of shape (n1, n2)
        """
        if method == 'cosine':
            # Normalize embeddings
            norms1 = np.linalg.norm(embeddings1, axis=1, keepdims=True)
            norms2 = np.linalg.norm(embeddings2, axis=1, keepdims=True)
            
            embeddings1_norm = embeddings1 / np.where(norms1 == 0, 1, norms1)
            embeddings2_norm = embeddings2 / np.where(norms2 == 0, 1, norms2)
            
            # Compute cosine similarity matrix
            similarity_matrix = np.dot(embeddings1_norm, embeddings2_norm.T)
            
        elif method == 'dot':
            # Dot product similarity matrix
            similarity_matrix = np.dot(embeddings1, embeddings2.T)
        
        else:
            raise ValueError(f"Method {method} not supported for matrix computation")
        
        return similarity_matrix
    
    def find_most_similar(self, query_embedding: np.ndarray,
                         candidate_embeddings: np.ndarray,
                         top_k: int = 5) -> List[tuple]:
        """
        Find most similar candidates to a query.
        
        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: Array of candidate embeddings
            top_k: Number of top candidates to return
            
        Returns:
            List of (index, similarity_score) tuples
        """
        # Compute similarities
        similarities = []
        for idx, candidate_emb in enumerate(candidate_embeddings):
            sim = self.compute_similarity(query_embedding, candidate_emb)
            similarities.append((idx, sim))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top-k
        return similarities[:top_k]
    
    def serialize_embedding(self, embedding: np.ndarray) -> bytes:
        """
        Serialize embedding for database storage.
        
        Args:
            embedding: Numpy array embedding
            
        Returns:
            Serialized bytes
        """
        return pickle.dumps(embedding)
    
    def deserialize_embedding(self, embedding_bytes: bytes) -> np.ndarray:
        """
        Deserialize embedding from database.
        
        Args:
            embedding_bytes: Serialized embedding
            
        Returns:
            Numpy array embedding
        """
        if embedding_bytes is None:
            return np.zeros(self.get_embedding_dimension())
        
        return pickle.loads(embedding_bytes)
    
    def generate_weighted_embedding(self, texts: List[str], 
                                   weights: List[float] = None) -> np.ndarray:
        """
        Generate a weighted average embedding from multiple texts.
        Useful for combining different sections of a resume or job description.
        
        Args:
            texts: List of text segments
            weights: Weight for each text segment (default: equal weights)
            
        Returns:
            Weighted average embedding
        """
        if not texts:
            return np.zeros(self.get_embedding_dimension())
        
        # Generate embeddings for all texts
        embeddings = self.generate_embeddings(texts)
        
        # Set equal weights if not provided
        if weights is None:
            weights = [1.0 / len(texts)] * len(texts)
        
        # Normalize weights
        weights = np.array(weights)
        weights = weights / weights.sum()
        
        # Compute weighted average
        weighted_embedding = np.average(embeddings, axis=0, weights=weights)
        
        return weighted_embedding
    
    def embed_resume(self, resume_text: str, 
                    sections: dict = None) -> np.ndarray:
        """
        Generate embedding for a resume, optionally with section weights.
        
        Args:
            resume_text: Full resume text
            sections: Optional dict with section names and their text
                     e.g., {'experience': '...', 'skills': '...', 'education': '...'}
            
        Returns:
            Resume embedding
        """
        if sections:
            # Generate weighted embedding based on sections
            # Weight skills and experience more heavily
            section_weights = {
                'skills': 0.35,
                'experience': 0.35,
                'education': 0.15,
                'projects': 0.10,
                'other': 0.05
            }
            
            texts = []
            weights = []
            
            for section_name, section_text in sections.items():
                if section_text and section_text.strip():
                    texts.append(section_text)
                    weight = section_weights.get(section_name.lower(), 0.05)
                    weights.append(weight)
            
            if texts:
                return self.generate_weighted_embedding(texts, weights)
        
        # Fall back to simple embedding of full text
        return self.generate_embedding(resume_text)
    
    def embed_job_description(self, job_text: str,
                            requirements: str = None,
                            responsibilities: str = None) -> np.ndarray:
        """
        Generate embedding for a job description.
        
        Args:
            job_text: Full job description text
            requirements: Extracted requirements section
            responsibilities: Extracted responsibilities section
            
        Returns:
            Job description embedding
        """
        if requirements or responsibilities:
            texts = []
            weights = []
            
            # Weight requirements more heavily
            if requirements:
                texts.append(requirements)
                weights.append(0.6)
            
            if responsibilities:
                texts.append(responsibilities)
                weights.append(0.4)
            
            return self.generate_weighted_embedding(texts, weights)
        
        # Fall back to simple embedding of full text
        return self.generate_embedding(job_text)
