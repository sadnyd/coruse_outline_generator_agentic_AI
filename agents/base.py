from utils.flow_logger import function_logger
"""PHASE 0: Agent stubs with responsibility contracts."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseAgent(ABC):
    """All agents inherit from this base contract."""
    
    @abstractmethod
    async def run(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute agent logic.
        
        Must be idempotent and stateless.
        Must return a valid schema-compliant output.
        """
        pass


class OrchestratorAgent(BaseAgent):
    """
    PHASE 2+: Central coordinator.
    
    Responsibilities:
    - Accept UserInputSchema from frontend
    - Dispatch to parallel agents (Retrieval, WebSearch)
    - Call Module Creation Agent with aggregated inputs
    - Hand off to Validator Agent
    - Retry logic if validation fails (PHASE 6)
    - Return final CourseOutlineSchema to frontend
    
    Maintains in-memory session context.
    """
    
    async def run(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main orchestration entry point.
        
        Args:
            user_input: UserInputSchema (validated by UI)
        
        Returns:
            CourseOutlineSchema
        """
        raise NotImplementedError("PHASE 2")


class WebSearchAgent(BaseAgent):
    """
    PHASE 4: Public knowledge retrieval.
    
    Responsibilities:
    - Accept query context (course topic, audience, depth)
    - Try primary tool (Tavily) → fallback (DuckDuckGo/SerpAPI)
    - Parse & rank results
    - Return WebSearchAgentOutput with URLs + snippets + confidence
    
    Key Design:
    - Isolated from other agents
    - Can be disabled for private deployments
    - Returns structured provenance
    """
    
    async def run(self, query_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute web search.
        
        Args:
            query_context: {'topic': '...', 'audience_level': '...', 'depth': '...'}
        
        Returns:
            WebSearchAgentOutput
        """
        raise NotImplementedError("PHASE 4")


class RetrievalAgent(BaseAgent):
    """
    PHASE 3: Private knowledge retrieval (RAG).
    
    Responsibilities:
    - Connect to ChromaDB vector store
    - Embed user query (topic + audience metadata)
    - Search with optional metadata filtering
    - Return top-k RetrievedChunks with similarity scores + provenance
    
    Key Design:
    - Decides what to search (autonomous)
    - Manages vector store lifecycle
    - Supports metadata-based filtering
    """
    
    async def run(self, query_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute retrieval.
        
        Args:
            query_context: {'topic': '...', 'filters': {'institution': '...', 'degree': '...'}}
        
        Returns:
            RetrievalAgentOutput
        """
        raise NotImplementedError("PHASE 3")


class ModuleCreationAgent(BaseAgent):
    """
    PHASE 5: Core synthesis engine.
    
    Responsibilities:
    - Accept UserInputSchema + retrieved chunks + web results + PDF content
    - Generate course outline respecting:
      * duration_hours
      * depth_requirement
      * audience_level
      * learning_mode
    - Use Bloom's taxonomy for objective mapping
    - Apply curriculum heuristics (backward design)
    - Return CourseOutlineSchema
    
    Key Design:
    - Fully stateless and reproducible
    - Respects all input constraints
    - Leverages prompt templates
    - Can be called iteratively with feedback (PHASE 6)
    """
    
    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate course outline.
        
        Args:
            inputs: {
                'user_input': UserInputSchema,
                'retrieved_docs': [RetrievedChunk],
                'web_results': [WebSearchResult],
                'pdf_content': Optional[str]
            }
        
        Returns:
            CourseOutlineSchema
        """
        raise NotImplementedError("PHASE 5")


class ValidatorAgent(BaseAgent):
    """
    PHASE 6: Quality gate + self-correction trigger.
    
    Responsibilities:
    - Score CourseOutlineSchema using rubric:
      * Coverage & Coherence (0-25)
      * Audience Alignment (0-20)
      * Depth & Technical Accuracy (0-20)
      * Assessability (0-15)
      * Practicality / Feasibility (0-10)
      * Originality & Duplication (0-10)
    - Generate ValidatorFeedbackSchema with:
      * numeric score (0-100)
      * rubric breakdown
      * targeted feedback
      * modules needing regeneration
    - Accept/Reject decision (threshold = 75 by default)
    
    Key Design:
    - Marks this system as "agentic" (has feedback loop)
    - Can trigger regeneration up to N times
    - Provides explainable feedback
    """
    
    async def run(self, outline: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score & validate outline.
        
        Args:
            outline: CourseOutlineSchema
        
        Returns:
            ValidatorFeedbackSchema
        """
        raise NotImplementedError("PHASE 6")


class QueryAgent(BaseAgent):
    """
    PHASE 7: Interactive explanation & refinement.
    
    Responsibilities:
    - Answer educator follow-ups:
      * "Why is this module included?"
      * "What sources influenced this?"
      * "Can you simplify Module 3?"
    - Pull context from:
      * User input
      * Retrieved docs
      * Web results
      * Final outline
    - Return QueryAgentResponse with:
      * natural language answer
      * source provenance
      * confidence score
      * optional regenerate signal
    
    Key Design:
    - Session-aware (accesses orchestrator context)
    - No hallucinated sources
    - Can trigger single-module regeneration
    """
    
    async def run(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Answer educator question.
        
        Args:
            query: Free-text question from educator
            context: OrchestratorContext (session data)
        
        Returns:
            QueryAgentResponse
        """
        raise NotImplementedError("PHASE 7")
