"""
PHASE 4 — Web Search Agent

Iteratively fetches public educational information from the web.
Uses multi-tool orchestration (Tavily → DuckDuckGo → SerpAPI with fallback).
Synthesizes results into structured curriculum recommendations.

Design Principles:
- Pure data gathering (no module generation)
- Graceful degradation (no hard failures)
- Clean provenance (every URL traced)
- LLM-powered synthesis (structured output)
"""

import asyncio
import logging
import json
import time
from typing import List, Optional, Tuple
from datetime import datetime

from schemas.user_input import UserInputSchema
from schemas.execution_context import ExecutionContext
from schemas.web_search_agent_output import (
    WebSearchAgentOutput,
    SearchTool,
    RecommendedModule,
    SourceLink,
)
from tools.web_search_tools import (
    get_web_search_toolchain,
    SearchResult,
    reset_web_search_toolchain,
)
from services.llm_service import get_llm_service
from utils.prompt_loader import get_prompt_loader
from utils.flow_logger import function_logger


logger = logging.getLogger(__name__)


class WebSearchAgent:
    """
    Agent responsible for gathering external knowledge via web search.
    
    Workflow:
    1. Receive user input & context
    2. Generate contextual search queries
    3. Execute multi-tool search
    4. Synthesize results via LLM
    5. Return structured output with provenance
    
    Explicit boundaries:
    ✅ Search public sources
    ✅ Summarize with LLM
    ✅ Structure output
    ✅ Track provenance
    
    ❌ No module generation
    ❌ No internal db access
    ❌ No validation/scoring
    ❌ No direct UI access
    """
    
    @function_logger("Handle __init__")
    @function_logger("Handle __init__")
    def __init__(self):
        """Initialize Web Search Agent."""
        self.agent_name = "WebSearchAgent"
        self.logger = logging.getLogger(self.agent_name)
        self.toolchain = get_web_search_toolchain()
        self.llm_service = None  # Lazy loaded
        self.search_budget = 3  # Max searches per request
    
    @function_logger("Execute  get llm service")
    @function_logger("Execute  get llm service")
    def _get_llm_service(self):
        """Lazy load LLM service."""
        if self.llm_service is None:
            try:
                self.llm_service = get_llm_service()
            except Exception as e:
                self.logger.warning(f"LLM service not available: {e}")
                self.llm_service = None
        return self.llm_service
    
    @function_logger("Search web for curriculum resources and synthesize findings")
    async def run(
        self, 
        context: ExecutionContext
    ) -> WebSearchAgentOutput:
        """
        Main entry point: search web for knowledge relevant to course request.
        
        Args:
            context: ExecutionContext with user input
            
        Returns:
            WebSearchAgentOutput with structured findings
        """
        start_time = time.time()
        self.logger.info(f"WebSearchAgent.run() started for session {context.session_id}")
        
        try:
            user_input = context.user_input
            
            # Step 1: Generate search queries
            queries = await self._generate_search_queries(user_input)
            self.logger.debug(f"Generated {len(queries)} search queries")
            
            # Step 2: Execute batch search
            all_results, stats = await self._execute_batch_search(queries)
            self.logger.info(f"Search results: {len(all_results)} total across {len(queries)} queries")
            
            # Step 3: Deduplicate and score
            unique_results = self.toolchain.deduplicate_results(all_results)
            self.logger.info(f"After dedup: {len(unique_results)} unique results")
            
            # Step 4: Synthesize with LLM
            output = await self._synthesize_results(user_input, queries, unique_results)
            
            # Step 5: Calculate metrics
            output.execution_time_ms = (time.time() - start_time) * 1000
            output.result_count = len(unique_results)
            output.high_quality_result_count = len([r for r in unique_results if r.relevance_score > 0.7])
            
            self.logger.info(
                f"WebSearchAgent complete: confidence={output.confidence_score:.2f}, "
                f"time={output.execution_time_ms:.0f}ms, results={output.result_count}"
            )
            
            return output
            
        except Exception as e:
            self.logger.error(f"WebSearchAgent failed: {e}")
            return WebSearchAgentOutput.empty_search()
    
    async def _generate_search_queries(
        self, 
        user_input: UserInputSchema
    ) -> List[str]:
        """
        Generate search queries from course title and description only.
        
        Args:
            user_input: User course requirements
            
        Returns:
            List of search queries
        """
        queries = []
        
        # Query 1: Course title
        queries.append(f"{user_input.course_title} curriculum")
        
        # Query 2: Title + description keywords
        if user_input.course_description:
            first_sentence = user_input.course_description.split(".")[0].strip()
            queries.append(f"{user_input.course_title} {first_sentence}")
        
        # Limit to budget
        queries = queries[:self.search_budget]
        
        self.logger.debug(f"Search queries: {queries}")
        return queries
    
    async def _execute_batch_search(
        self, 
        queries: List[str]
    ) -> Tuple[List[SearchResult], dict]:
        """
        Execute batch search across all queries with fallback.
        
        Args:
            queries: Search queries
            
        Returns:
            Tuple of (all_results, stats)
        """
        all_results, stats = self.toolchain.batch_search(
            queries, 
            max_results_per_query=5
        )
        
        return all_results, stats
    
    async def _synthesize_results(
        self,
        user_input: UserInputSchema,
        queries: List[str],
        results: List[SearchResult],
    ) -> WebSearchAgentOutput:
        """
        Use LLM to synthesize search results into structured output.
        
        Args:
            user_input: Course request
            queries: Queries executed
            results: Raw search results
            
        Returns:
            Structured WebSearchAgentOutput
        """
        # If no results, return empty
        if not results:
            return WebSearchAgentOutput(
                search_query=" | ".join(queries),
                search_summary="No web search results available.",
                confidence_score=0.0,
                tool_used=SearchTool.UNKNOWN,
            )
        
        try:
            # Format results for LLM
            formatted_results = self._format_search_results(results)
            
            # Build LLM prompt
            prompt = self._build_synthesis_prompt(
                user_input=user_input,
                queries=queries,
                formatted_results=formatted_results,
            )
            
            # Call LLM (mock for now)
            llm_output = self._mock_llm_synthesis(user_input, results)
            
            # Parse LLM response
            output = self._parse_synthesized_output(llm_output, queries, results)
            
            return output
            
        except Exception as e:
            self.logger.error(f"LLM synthesis failed: {e}. Falling back to simple extraction.")
            return self._simple_result_extraction(queries, results)
    
    @function_logger("Execute  format search results")
    @function_logger("Execute  format search results")
    def _format_search_results(self, results: List[SearchResult]) -> str:
        """Format search results for LLM input."""
        formatted = []
        
        for i, result in enumerate(results[:10], 1):  # Top 10
            formatted.append(
                f"{i}. {result.title}\n"
                f"   URL: {result.url}\n"
                f"   Source: {result.source} (score: {result.relevance_score:.2f})\n"
                f"   {result.snippet[:150]}...\n"
            )
        
        return "\n".join(formatted)
    
    @function_logger("Build  synthesis prompt")
    @function_logger("Build  synthesis prompt")
    def _build_synthesis_prompt(
        self,
        user_input: UserInputSchema,
        queries: List[str],
        formatted_results: str,
    ) -> str:
        """Build LLM prompt for synthesis using centralized prompt loader."""
        prompt_loader = get_prompt_loader()
        
        prompt = prompt_loader.load_prompt(
            'web_search_synthesis',
            {
                'course_title': user_input.course_title,
                'course_description': user_input.course_description,
                'formatted_results': formatted_results
            }
        )
        
        return prompt
    
    @function_logger("Execute  mock llm synthesis")
    @function_logger("Execute  mock llm synthesis")
    def _mock_llm_synthesis(
        self,
        user_input: UserInputSchema,
        results: List[SearchResult],
    ) -> dict:
        """
        Mock LLM synthesis for testing (replace with real LLM call).
        
        Returns: Simulated LLM response
        """
        # Extract topics from results
        topics = set()
        for result in results:
            # Simple keyword extraction
            words = (result.title + " " + result.snippet).lower().split()
            topics.update([w for w in words if len(w) > 5])
        
        topics = list(topics)[:8]
        
        return {
            "search_summary": f"Web search found {len(results)} resources about {user_input.course_title}. "
                            f"Key topics identified: {', '.join(topics[:3])}. "
                            f"Multiple sources available with varying depth levels.",
            "key_topics_found": topics,
            "recommended_modules": [
                {
                    "title": f"{user_input.course_title} Fundamentals",
                    "description": "Foundation course covering core concepts",
                    "key_topics": topics[:3],
                    "estimated_hours": 40,
                    "difficulty_level": "beginner",
                    "source_urls": [r.url for r in results[:2]],
                }
            ],
            "learning_objectives_found": [
                f"Understand principles of {user_input.course_title}",
                f"Apply {user_input.course_title} concepts to real-world problems",
            ],
            "skillset_recommendations": ["Problem solving", "Critical thinking", "Technical foundation"],
            "confidence_notes": f"Based on {len(results)} reliable sources with good relevance scores.",
        }
    
    @function_logger("Execute  parse synthesized output")
    @function_logger("Execute  parse synthesized output")
    def _parse_synthesized_output(
        self,
        llm_output: dict,
        queries: List[str],
        results: List[SearchResult],
    ) -> WebSearchAgentOutput:
        """Parse LLM synthesis into WebSearchAgentOutput schema."""
        
        # Determine primary tool used
        tool_used = SearchTool.TAVILY  # Default
        if results:
            # Use the source from top result
            source_map = {
                "tavily": SearchTool.TAVILY,
                "duckduckgo": SearchTool.DUCKDUCKGO,
                "serpapi": SearchTool.SERPAPI,
            }
            tool_used = source_map.get(results[0].source, SearchTool.UNKNOWN)
        
        # Build output
        output = WebSearchAgentOutput(
            search_query=" | ".join(queries),
            search_summary=llm_output.get("search_summary", ""),
            key_topics_found=llm_output.get("key_topics_found", []),
            source_links=[
                SourceLink(
                    url=r.url,
                    title=r.title,
                    relevance_score=r.relevance_score,
                    source_type="external",
                    accessed_at=datetime.now().isoformat(),
                )
                for r in results
            ],
            learning_objectives_found=llm_output.get("learning_objectives_found", []),
            skillset_recommendations=llm_output.get("skillset_recommendations", []),
            confidence_score=0.7 if len(results) > 2 else 0.5,
            tool_used=tool_used,
            result_count=len(results),
        )
        
        # Parse modules if present
        for module_data in llm_output.get("recommended_modules", []):
            module = RecommendedModule(**module_data)
            output.recommended_modules.append(module)
        
        return output
    
    @function_logger("Execute  simple result extraction")
    @function_logger("Execute  simple result extraction")
    def _simple_result_extraction(
        self,
        queries: List[str],
        results: List[SearchResult],
    ) -> WebSearchAgentOutput:
        """
        Fallback: simple extraction without LLM.
        Works when LLM synthesis fails.
        """
        return WebSearchAgentOutput(
            search_query=" | ".join(queries),
            search_summary=f"Found {len(results)} search results. "
                          f"Top sources: {', '.join([r.title for r in results[:3]])}.",
            key_topics_found=[],
            source_links=[
                SourceLink(
                    url=r.url,
                    title=r.title,
                    relevance_score=r.relevance_score,
                )
                for r in results
            ],
            confidence_score=0.5,
            tool_used=SearchTool.UNKNOWN,
            result_count=len(results),
            search_notes="Fallback extraction (LLM synthesis failed)",
        )


# Singleton instance
_agent_instance = None


@function_logger("Get web search agent")
@function_logger("Get web search agent")
def get_web_search_agent() -> WebSearchAgent:
    """Get or create Web Search Agent singleton."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = WebSearchAgent()
    return _agent_instance


@function_logger("Execute reset web search agent")
@function_logger("Execute reset web search agent")
def reset_web_search_agent():
    """Reset agent singleton (for testing)."""
    global _agent_instance
    _agent_instance = None
