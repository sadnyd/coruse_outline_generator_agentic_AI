from utils.flow_logger import function_logger
"""
PHASE 4 — Web Search Agent Output Schema

Standardized container for web search results.
Ensures downstream agents receive clean, structured data with provenance.

Key guarantees:
- No raw HTML
- No confusing source mixing
- Every result is traceable
- Confidence scores present
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class SearchTool(str, Enum):
    """Which search tool was used (for observability)."""
    TAVILY = "tavily"
    DUCKDUCKGO = "duckduckgo"
    SERPAPI = "serpapi"
    UNKNOWN = "unknown"


@dataclass
class RecommendedModule:
    """Curriculum module recommended by web search results."""
    title: str
    description: str
    key_topics: List[str] = field(default_factory=list)
    estimated_hours: Optional[float] = None
    difficulty_level: Optional[str] = None  # "beginner", "intermediate", "advanced"
    source_urls: List[str] = field(default_factory=list)


@dataclass
class SourceLink:
    """URL and metadata from search results."""
    url: str
    title: str
    source_type: str = "external"  # "external", "institution", "mooc", "textbook"
    relevance_score: float = 0.5  # 0.0-1.0
    accessed_at: Optional[str] = None


@dataclass
class WebSearchAgentOutput:
    """
    Output from Web Search Agent.
    
    Consumed by:
    - Module Creation Agent (as reference material)
    - Query Agent (for follow-ups)
    - Session storage (for provenance)
    
    Constraints:
    - Everything summarized (max 1000 words)
    - Only valid URLs
    - Confidence score required
    - No empty searches marked as success
    """
    
    # ===== CORE FIELDS =====
    search_query: str
    """Original query that triggered this search"""
    
    search_summary: str
    """Natural language summary of findings (max 1000 words)"""
    
    key_topics_found: List[str] = field(default_factory=list)
    """Top topics extracted from search results"""
    
    # ===== OPTIONAL STRUCTURED DATA =====
    recommended_modules: List[RecommendedModule] = field(default_factory=list)
    """Curriculum modules found in search"""
    
    source_links: List[SourceLink] = field(default_factory=list)
    """All sources with URLs and titles"""
    
    learning_objectives_found: List[str] = field(default_factory=list)
    """Objectives extracted from external sources"""
    
    skillset_recommendations: List[str] = field(default_factory=list)
    """Technical skills identified as important"""
    
    # ===== QUALITY METRICS =====
    confidence_score: float = 0.5
    """
    Overall confidence 0.0-1.0:
    1.0 = multiple authoritative sources
    0.7 = reasonable results found
    0.5 = limited results, low quality
    0.2 = very poor results
    0.0 = no meaningful results
    """
    
    result_count: int = 0
    """Number of results processed"""
    
    high_quality_result_count: int = 0
    """Results with score > 0.7"""
    
    # ===== PROVENANCE =====
    tool_used: SearchTool = SearchTool.UNKNOWN
    """Which search provider returned results"""
    
    execution_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    """When search was executed"""
    
    execution_time_ms: Optional[float] = None
    """How long search took"""
    
    fallback_used: bool = False
    """Whether primary tool failed and fallback was used"""
    
    # ===== METADATA =====
    search_notes: str = ""
    """Debug notes about search execution"""
    
    @staticmethod
    @function_logger("Execute empty search")
    def empty_search() -> "WebSearchAgentOutput":
        """Create failed search result with low confidence."""
        return WebSearchAgentOutput(
            search_query="",
            search_summary="No search results available.",
            confidence_score=0.0,
            result_count=0,
            search_notes="Search failed or returned no results.",
        )
    
    @function_logger("Execute is high confidence")
    def is_high_confidence(self) -> bool:
        """Check if search results are reliable."""
        return self.confidence_score >= 0.7 and self.result_count > 0
    
    @function_logger("Execute is usable")
    def is_usable(self) -> bool:
        """Check if results are good enough to use."""
        return self.confidence_score >= 0.5 and len(self.source_links) > 0
    
    @function_logger("Execute to dict")
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for serialization.
        Handles dataclass nesting.
        """
        return {
            "search_query": self.search_query,
            "search_summary": self.search_summary,
            "key_topics_found": self.key_topics_found,
            "recommended_modules": [asdict(m) for m in self.recommended_modules],
            "source_links": [asdict(s) for s in self.source_links],
            "learning_objectives_found": self.learning_objectives_found,
            "skillset_recommendations": self.skillset_recommendations,
            "confidence_score": self.confidence_score,
            "result_count": self.result_count,
            "high_quality_result_count": self.high_quality_result_count,
            "tool_used": self.tool_used.value,
            "execution_timestamp": self.execution_timestamp,
            "execution_time_ms": self.execution_time_ms,
            "fallback_used": self.fallback_used,
            "search_notes": self.search_notes,
        }
    
    @staticmethod
    @function_logger("Execute from dict")
    def from_dict(data: Dict[str, Any]) -> "WebSearchAgentOutput":
        """
        Reconstruct from dictionary (session persistence).
        """
        # Parse nested objects
        modules = [
            RecommendedModule(**m) for m in data.get("recommended_modules", [])
        ]
        links = [
            SourceLink(**s) for s in data.get("source_links", [])
        ]
        
        tool = SearchTool(data.get("tool_used", "unknown"))
        
        return WebSearchAgentOutput(
            search_query=data.get("search_query", ""),
            search_summary=data.get("search_summary", ""),
            key_topics_found=data.get("key_topics_found", []),
            recommended_modules=modules,
            source_links=links,
            learning_objectives_found=data.get("learning_objectives_found", []),
            skillset_recommendations=data.get("skillset_recommendations", []),
            confidence_score=data.get("confidence_score", 0.0),
            result_count=data.get("result_count", 0),
            high_quality_result_count=data.get("high_quality_result_count", 0),
            tool_used=tool,
            execution_timestamp=data.get("execution_timestamp", ""),
            execution_time_ms=data.get("execution_time_ms"),
            fallback_used=data.get("fallback_used", False),
            search_notes=data.get("search_notes", ""),
        )
    
    @function_logger("Handle __str__")
    def __str__(self) -> str:
        """Human-readable summary."""
        return (
            f"WebSearchAgentOutput(\n"
            f"  query: {self.search_query}\n"
            f"  confidence: {self.confidence_score:.2f}\n"
            f"  results: {self.result_count}\n"
            f"  tool: {self.tool_used.value}\n"
            f"  topics: {len(self.key_topics_found)}\n"
            f")"
        )
