from utils.flow_logger import function_logger
"""LangChain tools for agents (PHASE 4+)."""


class PDFLoaderTool:
    """Load and parse uploaded PDF (PHASE 1)."""
    
    @staticmethod
    @function_logger("Execute load pdf")
    def load_pdf(file_path: str) -> str:
        """Extract text from PDF."""
        raise NotImplementedError("PHASE 1")


class WebSearchTool:
    """
    LangChain tool wrappers for web search (PHASE 4).
    
    Supports:
    - Tavily Search (primary)
    - DuckDuckGo (fallback)
    - SerpAPI (fallback)
    """
    
    @staticmethod
    @function_logger("Execute tavily search")
    def tavily_search(query: str, max_results: int = 10) -> list:
        """Search using Tavily."""
        raise NotImplementedError("PHASE 4")
    
    @staticmethod
    @function_logger("Execute duckduckgo search")
    def duckduckgo_search(query: str, max_results: int = 10) -> list:
        """Search using DuckDuckGo."""
        raise NotImplementedError("PHASE 4")
    
    @staticmethod
    @function_logger("Execute serpapi search")
    def serpapi_search(query: str, max_results: int = 10) -> list:
        """Search using SerpAPI."""
        raise NotImplementedError("PHASE 4")
