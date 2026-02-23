from utils.flow_logger import function_logger
"""
PHASE 0: Contracts for individual agent outputs.

Each agent has its own output schema so it can be tested and replaced independently.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class WebSearchResult(BaseModel):
    """Single web search result (PHASE 4)."""
    
    title: str
    url: str
    snippet: str = Field(..., description="Short preview text")
    source: str = Field(..., description="e.g., 'tavily', 'duckduckgo', 'serpapi'")
    confidence: float = Field(..., ge=0, le=1, description="0.0-1.0 relevance score")


class WebSearchAgentOutput(BaseModel):
    """Output from Web Search Agent (PHASE 4)."""
    
    query: str = Field(..., description="What was searched")
    results: List[WebSearchResult] = Field(..., min_items=1)
    citations: List[Dict[str, str]] = Field(
        default_factory=list, 
        description="Formatted citations for results"
    )
    fallback_used: bool = Field(default=False, description="True if fallback provider was used")


class RetrievedChunk(BaseModel):
    """Single document chunk from vector DB (PHASE 3)."""
    
    chunk_id: str
    text: str
    metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="{'institution': '...', 'degree': '...', 'year': 2024, 'tags': [...]}"
    )
    similarity_score: float = Field(..., ge=0, le=1)
    source_document: str = Field(..., description="Original document name/ID")


class RetrievalAgentOutput(BaseModel):
    """Output from Retrieval Agent (PHASE 3)."""
    
    query_topic: str
    top_k_chunks: List[RetrievedChunk] = Field(..., min_items=1)
    search_filters_applied: Dict[str, Any] = Field(default_factory=dict)


class QueryAgentResponse(BaseModel):
    """
    Response from Query Agent (PHASE 7).
    
    Handles follow-ups, why-questions, and provenance lookups.
    """
    
    user_question: str
    answer: str = Field(..., description="Natural language response")
    sources: List[Dict[str, str]] = Field(
        default_factory=list, 
        description="[{'module': 'M_2', 'reference': '...', 'url': '...'}]"
    )
    confidence: float = Field(..., ge=0, le=1, description="How confident in the answer")
    can_regenerate_module: Optional[str] = Field(
        None, 
        description="Module ID that can be regenerated, e.g., 'M_3'"
    )


class OrchestratorContext(BaseModel):
    """
    In-memory session context (PHASE 1-2).
    
    Holds intermediate results and session state.
    """
    
    session_id: str
    user_input: Dict[str, Any]
    retrieval_results: Optional[RetrievalAgentOutput] = None
    web_search_results: Optional[WebSearchAgentOutput] = None
    generated_outline: Optional[Dict[str, Any]] = None
    validator_feedback: Optional[Dict[str, Any]] = None
    conversation_history: List[Dict[str, str]] = Field(
        default_factory=list, 
        description="[{'role': 'user|assistant', 'content': '...'}]"
    )
