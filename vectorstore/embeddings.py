from utils.flow_logger import function_logger
"""Embeddings wrapper (PHASE 3)."""

from vectorstore.chroma_client import EmbeddingProvider


class LangChainEmbeddings(EmbeddingProvider):
    """
    Use LangChain Embeddings abstraction for flexibility.
    
    Supports:
    - OpenAI Embeddings
    - Anthropic Embeddings
    - Local embeddings (sentence-transformers)
    """
    
    pass
