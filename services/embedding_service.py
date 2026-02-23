"""
PHASE 3 — Embedding Service

Standardizes embedding generation across the system.
Single source of truth for embeddings to avoid drift.
Uses deterministic embeddings for reproducibility.
"""

import hashlib
from typing import List, Optional
import json
from utils.flow_logger import function_logger


class EmbeddingService:
    """
    Vendor-agnostic embedding service.
    Currently uses deterministic embeddings for Phase 3 testing.
    Will be replaced with OllamaEmbeddings or HuggingFaceEmbeddings in Phase 5.
    """
    
    @function_logger("Initialize embedding service")
    @function_logger("Handle __init__")
    def __init__(self, model_name: str = "mock-embedding-v1", embedding_dim: int = 384):
        """
        Initialize embedding service.
        
        Args:
            model_name: Identifier for the embedding model
            embedding_dim: Dimensionality of embeddings (locked for consistency)
        """
        self.model_name = model_name
        self.embedding_dim = embedding_dim
        self.version = "1.0"
        
    @function_logger("Generate embedding for single text")
    @function_logger("Execute embed text")
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector of length embedding_dim
            
        Raises:
            ValueError: If text is empty
        """
        if not text or len(text.strip()) == 0:
            raise ValueError("Cannot embed empty text")
        
        # Deterministic embedding for Phase 3 testing
        # Hash the text to get consistent pseudo-random values
        hash_obj = hashlib.sha256(text.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        
        # Generate embedding by seeding pseudo-random sequence
        embeddings = []
        for i in range(self.embedding_dim):
            seed = (hash_int + i) % (2**32)
            # Simple pseudo-random: scale to [-1, 1]
            value = ((seed * 1103515245 + 12345) % (2**31)) / (2**30) - 1.0
            embeddings.append(value)
        
        # Normalize to unit length
        magnitude = sum(x**2 for x in embeddings) ** 0.5
        if magnitude > 0:
            embeddings = [x / magnitude for x in embeddings]
        
        return embeddings
    
    @function_logger("Generate embeddings for multiple texts")
    @function_logger("Execute embed texts")
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        return [self.embed_text(text) for text in texts]
    
    @function_logger("Generate embedding for search query")
    @function_logger("Execute embed query")
    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.
        Uses same logic as embed_text for consistency.
        
        Args:
            query: Search query text
            
        Returns:
            Embedding vector
        """
        return self.embed_text(query)
    
    @function_logger("Get embedding service configuration")
    @function_logger("Get config")
    def get_config(self) -> dict:
        """
        Get embedding service configuration.
        
        Returns:
            Config dict with model name, dimension, version
        """
        return {
            "model_name": self.model_name,
            "embedding_dim": self.embedding_dim,
            "version": self.version,
        }
    
    @function_logger("Validate embedding vector")
    @function_logger("Execute validate embedding")
    def validate_embedding(self, embedding: List[float]) -> bool:
        """
        Validate that an embedding meets service requirements.
        
        Args:
            embedding: Embedding vector to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If embedding is invalid
        """
        if not isinstance(embedding, list):
            raise ValueError("Embedding must be a list")
        
        if len(embedding) != self.embedding_dim:
            raise ValueError(f"Embedding dimension {len(embedding)} != expected {self.embedding_dim}")
        
        if not all(isinstance(x, (int, float)) for x in embedding):
            raise ValueError("All embedding values must be numeric")
        
        return True


# Singleton instance
_embedding_service: Optional[EmbeddingService] = None


@function_logger("Get or create global embedding service")
@function_logger("Get embedding service")
def get_embedding_service(force_new: bool = False) -> EmbeddingService:
    """
    Get or create the global embedding service.
    
    Args:
        force_new: Create new instance (for testing)
        
    Returns:
        EmbeddingService instance
    """
    global _embedding_service
    
    if force_new or _embedding_service is None:
        _embedding_service = EmbeddingService()
    
    return _embedding_service


@function_logger("Reset global embedding service")
@function_logger("Execute reset embedding service")
def reset_embedding_service():
    """Reset the global embedding service (for testing)."""
    global _embedding_service
    _embedding_service = None
