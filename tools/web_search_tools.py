"""
PHASE 4 — Web Search Tool Wrappers

Abstract interface for multiple search providers (Tavily, DuckDuckGo, SerpAPI).
Handles tool selection, fallback, error handling gracefully.

Design:
- Tool providers never crash main agent
- All tools return standardized format
- Fallback chain: Tavily → DuckDuckGo → SerpAPI
- Every call is tracked for observability
"""

import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import os
from utils.flow_logger import function_logger

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Standardized search result from any provider."""
    title: str
    url: str
    snippet: str
    source: str  # "tavily", "duckduckgo", "serpapi"
    relevance_score: float = 0.5  # 0.0 - 1.0


class TavilySearchTool:
    """
    Primary search provider: Tavily API
    
    Strengths: Educational focus, high quality results, built-in relevance scoring
    Fallback: If unavailable or quota exceeded
    """
    
    @function_logger("Handle __init__")
    def __init__(self):
        """Initialize Tavily search tool."""
        self.api_key = os.getenv("TAVILY_API_KEY", "")
        self.is_available = self._check_availability()
    
    @function_logger("Check  availability")
    def _check_availability(self) -> bool:
        """Check if Tavily is available."""
        if not self.api_key:
            logger.warning("TAVILY_API_KEY not set. Tavily will be skipped.")
            return False
        
        try:
            # In production, this would verify the API key
            import requests
            return True
        except ImportError:
            logger.warning("requests library not available. Tavily disabled.")
            return False
    
    @function_logger("Execute search")
    def search(self, query: str, max_results: int = 5) -> Tuple[bool, List[SearchResult]]:
        """
        Search using Tavily API.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            Tuple of (success, results)
        """
        if not self.is_available:
            return False, []
        
        try:
            # Mock implementation (replace with real Tavily API call)
            import requests
            
            # In production:
            # response = requests.post(
            #     "https://api.tavily.com/search",
            #     json={
            #         "api_key": self.api_key,
            #         "query": query,
            #         "max_results": max_results,
            #         "include_answer": True,
            #     }
            # )
            # results = response.json()["results"]
            
            # For now, mock mode:
            results = self._mock_search(query, max_results)
            
            parsed = [
                SearchResult(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    snippet=r.get("snippet", "")[:200],
                    source="tavily",
                    relevance_score=r.get("score", 0.5),
                )
                for r in results
            ]
            
            logger.info(f"Tavily: found {len(parsed)} results for '{query}'")
            return True, parsed
            
        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return False, []
    
    @staticmethod
    @function_logger("Execute  mock search")
    def _mock_search(query: str, max_results: int) -> List[Dict]:
        """Mock Tavily search results for testing."""
        mock_data = {
            "machine learning": [
                {"title": "ML Course Syllabus - Stanford", 
                 "url": "https://example.com/ml-syllabus",
                 "snippet": "Comprehensive ML curriculum covering supervised, unsupervised learning", 
                 "score": 0.95},
                {"title": "Deep Learning Fundamentals - MIT", 
                 "url": "https://example.com/dl-course", 
                 "snippet": "Neural networks, backpropagation, deep architectures", 
                 "score": 0.92},
            ],
            "java": [
                {"title": "Java Programming Guide", 
                 "url": "https://example.com/java-guide", 
                 "snippet": "Object-oriented programming, design patterns, best practices", 
                 "score": 0.90},
                {"title": "Advanced Java Course", 
                 "url": "https://example.com/java-advanced", 
                 "snippet": "Concurrency, streams, lambdas, modern Java 21 features", 
                 "score": 0.88},
            ],
            "python": [
                {"title": "Python Data Science", 
                 "url": "https://example.com/python-ds", 
                 "snippet": "Pandas, NumPy, scikit-learn, data analysis", 
                 "score": 0.93},
            ],
        }
        
        # Find matching results
        for key, results in mock_data.items():
            if key.lower() in query.lower():
                return results[:max_results]
        
        # Default if no match
        return [
            {"title": f"Search Results for {query}", 
             "url": "https://example.com/results", 
             "snippet": f"Educational resources about {query}", 
             "score": 0.5},
        ]


class DuckDuckGoSearchTool:
    """
    Secondary search provider: DuckDuckGo (no API key required)
    
    Strengths: No authentication needed, privacy-focused, reliable fallback
    Fallback to: SerpAPI
    """
    
    @function_logger("Handle __init__")
    def __init__(self):
        """Initialize DuckDuckGo search tool."""
        self.is_available = self._check_availability()
    
    @function_logger("Check  availability")
    def _check_availability(self) -> bool:
        """Check if DuckDuckGo is available."""
        try:
            # ddgs package required (formerly duckduckgo_search)
            from ddgs import DDGS
            return True
        except ImportError:
            logger.warning("ddgs not installed. DuckDuckGo disabled.")
            return False
    
    @function_logger("Execute search")
    def search(self, query: str, max_results: int = 5) -> Tuple[bool, List[SearchResult]]:
        """
        Search using DuckDuckGo (no auth needed).
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            Tuple of (success, results)
        """
        if not self.is_available:
            return False, []
        
        try:
            from ddgs import DDGS
            
            ddgs = DDGS()
            # Add educational qualifier
            educational_query = f"{query} education curriculum course"
            results = ddgs.text(educational_query, max_results=max_results)
            
            parsed = [
                SearchResult(
                    title=r.get("title", ""),
                    url=r.get("href", ""),
                    snippet=r.get("body", "")[:200],
                    source="duckduckgo",
                    relevance_score=0.7,  # DuckDuckGo doesn't provide scores
                )
                for r in results
            ]
            
            logger.info(f"DuckDuckGo: found {len(parsed)} results for '{query}'")
            return True, parsed
            
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}. Will try SerpAPI.")
            return False, []


class SerpAPISearchTool:
    """
    Tertiary search provider: SerpAPI (requires API key)
    
    Strengths: Reliable, structured results
    Fallback to: Return empty (allow graceful degradation)
    """
    
    @function_logger("Handle __init__")
    def __init__(self):
        """Initialize SerpAPI search tool."""
        self.api_key = os.getenv("SERPAPI_API_KEY", "")
        self.is_available = self._check_availability()
    
    @function_logger("Check  availability")
    def _check_availability(self) -> bool:
        """Check if SerpAPI is available."""
        if not self.api_key:
            logger.warning("SERPAPI_API_KEY not set. SerpAPI will be skipped.")
            return False
        
        try:
            import requests
            return True
        except ImportError:
            logger.warning("requests library not available. SerpAPI disabled.")
            return False
    
    @function_logger("Execute search")
    def search(self, query: str, max_results: int = 5) -> Tuple[bool, List[SearchResult]]:
        """
        Search using SerpAPI.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            Tuple of (success, results)
        """
        if not self.is_available:
            return False, []
        
        try:
            import requests
            
            params = {
                "q": query,
                "api_key": self.api_key,
                "num": max_results,
                "tbm": "nws",  # News results (educational)
            }
            
            # In production: response = requests.get("https://serpapi.com/search", params=params)
            # For now mock:
            results = self._mock_search(query, max_results)
            
            parsed = [
                SearchResult(
                    title=r.get("title", ""),
                    url=r.get("link", ""),
                    snippet=r.get("snippet", "")[:200],
                    source="serpapi",
                    relevance_score=r.get("score", 0.6),
                )
                for r in results
            ]
            
            logger.info(f"SerpAPI: found {len(parsed)} results for '{query}'")
            return True, parsed
            
        except Exception as e:
            logger.error(f"SerpAPI search failed: {e}")
            return False, []
    
    @staticmethod
    @function_logger("Execute  mock search")
    def _mock_search(query: str, max_results: int) -> List[Dict]:
        """Mock SerpAPI search results."""
        return [
            {"title": f"{query} - Educational Resource",
             "link": "https://example.com/resource",
             "snippet": f"Information about {query}",
             "score": 0.6},
        ]


class WebSearchToolchain:
    """
    Master tool chain: orchestrates all search providers with fallback logic.
    
    Fallback chain: Tavily → DuckDuckGo → SerpAPI
    Never fails completely — always returns something or empty list.
    """
    
    @function_logger("Handle __init__")
    def __init__(self):
        """Initialize all search tools."""
        self.tavily = TavilySearchTool()
        self.duckduckgo = DuckDuckGoSearchTool()
        self.serpapi = SerpAPISearchTool()
        self.search_history = []
    
    @function_logger("Execute search")
    def search(self, query: str, max_results: int = 5) -> Tuple[List[SearchResult], str]:
        """
        Execute search with intelligent fallback.
        
        Args:
            query: Search query
            max_results: Maximum results per tool
            
        Returns:
            Tuple of (results, tool_used)
        """
        logger.info(f"Starting web search: '{query}'")
        
        # Try Tavily (primary)
        success, results = self.tavily.search(query, max_results)
        if success and len(results) > 2:  # Good results
            tool_used = "tavily"
        else:
            # Fallback to DuckDuckGo
            logger.info("Tavily insufficient, trying DuckDuckGo...")
            success, results = self.duckduckgo.search(query, max_results)
            if success and len(results) > 2:
                tool_used = "duckduckgo"
            else:
                # Final fallback to SerpAPI
                logger.info("DuckDuckGo insufficient, trying SerpAPI...")
                success, results = self.serpapi.search(query, max_results)
                tool_used = "serpapi"
        
        # Track search
        self.search_history.append({
            "query": query,
            "tool": tool_used,
            "result_count": len(results),
            "timestamp": datetime.now().isoformat(),
        })
        
        logger.info(f"Search complete: {len(results)} results from {tool_used}")
        return results, tool_used
    
    @function_logger("Execute batch search")
    def batch_search(
        self, 
        queries: List[str], 
        max_results_per_query: int = 3
    ) -> Tuple[List[SearchResult], Dict]:
        """
        Execute multiple searches efficiently.
        
        Args:
            queries: List of queries
            max_results_per_query: Limit per query
            
        Returns:
            Tuple of (all_results, stats)
        """
        all_results = []
        stats = {}
        
        for query in queries:
            results, tool = self.search(query, max_results_per_query)
            all_results.extend(results)
            stats[query] = {"count": len(results), "tool": tool}
        
        logger.info(f"Batch search complete: {len(all_results)} total results from {len(queries)} queries")
        return all_results, stats
    
    @function_logger("Execute deduplicate results")
    def deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate URLs from results."""
        seen = set()
        unique = []
        
        for result in results:
            if result.url not in seen:
                seen.add(result.url)
                unique.append(result)
        
        return unique
    
    @function_logger("Get search stats")
    def get_search_stats(self) -> Dict:
        """Get statistics about search history."""
        if not self.search_history:
            return {"total_searches": 0, "tools_used": {}}
        
        tool_counts = {}
        for entry in self.search_history:
            tool = entry["tool"]
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
        
        return {
            "total_searches": len(self.search_history),
            "tools_used": tool_counts,
            "last_search": self.search_history[-1] if self.search_history else None,
        }


# Singleton instance
_toolchain_instance = None


@function_logger("Get web search toolchain")
def get_web_search_toolchain() -> WebSearchToolchain:
    """Get or create web search toolchain singleton."""
    global _toolchain_instance
    if _toolchain_instance is None:
        _toolchain_instance = WebSearchToolchain()
    return _toolchain_instance


@function_logger("Execute reset web search toolchain")
def reset_web_search_toolchain():
    """Reset toolchain singleton (for testing)."""
    global _toolchain_instance
    _toolchain_instance = None
