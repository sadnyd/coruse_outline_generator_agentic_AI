from utils.flow_logger import function_logger
"""
PHASE 3 — Retrieval Agent Output Schema

Standardized output from the Retrieval Agent.
Used to pass retrieved knowledge through the orchestrator to downstream agents.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class RetrievedChunk:
    """A single retrieved chunk with scoring."""
    
    content: str
    """The actual text content"""
    
    similarity_score: float
    """Similarity score from vector search (0.0 to 1.0)"""
    
    metadata: Dict[str, Any]
    """Chunk metadata (institution, domain, etc.)"""
    
    document_id: str
    """Unique document identifier"""
    
    chunk_index: int = 0
    """Position in original document"""


@dataclass
class RetrievalAgentOutput:
    """
    Output schema for the Retrieval Agent (Phase 3).
    
    Passed through orchestrator to other agents.
    Built to extend ExecutionContext seamlessly.
    """
    
    agent_name: str = "RetrievalAgent"
    """Identifier for this agent"""
    
    retrieved_chunks: List[RetrievedChunk] = field(default_factory=list)
    """All retrieved chunks with relevance scores"""
    
    knowledge_summary: str = ""
    """Human-readable summary of retrieved knowledge"""
    
    search_queries_executed: List[str] = field(default_factory=list)
    """Which internal search queries were fired"""
    
    metadata_filters_applied: List[str] = field(default_factory=list)
    """Filters used to narrow the search"""
    
    total_hits: int = 0
    """Total chunks matched before ranking"""
    
    returned_count: int = 0
    """Actual chunks returned (top-k)"""
    
    retrieval_confidence: float = 0.0
    """Confidence in retrieval quality (0.0 to 1.0)"""
    
    fallback_used: bool = False
    """Whether fallback retrieval was triggered"""
    
    execution_notes: str = ""
    """Debug/explanation notes"""
    
    @function_logger("Execute to dict")
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for session storage."""
        return {
            "agent_name": self.agent_name,
            "retrieved_chunks": [
                {
                    "content": chunk.content,
                    "similarity_score": chunk.similarity_score,
                    "metadata": chunk.metadata,
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                }
                for chunk in self.retrieved_chunks
            ],
            "knowledge_summary": self.knowledge_summary,
            "search_queries_executed": self.search_queries_executed,
            "metadata_filters_applied": self.metadata_filters_applied,
            "total_hits": self.total_hits,
            "returned_count": self.returned_count,
            "retrieval_confidence": self.retrieval_confidence,
            "fallback_used": self.fallback_used,
            "execution_notes": self.execution_notes,
        }
    
    @staticmethod
    @function_logger("Execute from dict")
    def from_dict(data: Dict[str, Any]) -> "RetrievalAgentOutput":
        """Reconstruct from dictionary."""
        chunks = [
            RetrievedChunk(
                content=c["content"],
                similarity_score=c["similarity_score"],
                metadata=c["metadata"],
                document_id=c["document_id"],
                chunk_index=c.get("chunk_index", 0),
            )
            for c in data.get("retrieved_chunks", [])
        ]
        
        return RetrievalAgentOutput(
            agent_name=data.get("agent_name", "RetrievalAgent"),
            retrieved_chunks=chunks,
            knowledge_summary=data.get("knowledge_summary", ""),
            search_queries_executed=data.get("search_queries_executed", []),
            metadata_filters_applied=data.get("metadata_filters_applied", []),
            total_hits=data.get("total_hits", 0),
            returned_count=data.get("returned_count", 0),
            retrieval_confidence=data.get("retrieval_confidence", 0.0),
            fallback_used=data.get("fallback_used", False),
            execution_notes=data.get("execution_notes", ""),
        )
