"""
LLM Service Abstraction Layer

Centralizes LLM client selection and management.

Architecture:
- LLMConfig: Configuration for any LLM provider
- LLMResponse: Standardized response format
- BaseLLMService: Abstract interface all providers implement
- LLMFactory: Client selection strategy (provider → implementation)
- Global functions: Singleton management (get_llm_service, set_llm_service, etc.)

Provider implementations are located in services/providers/:
- services/providers/openai_client.py → OpenAIClient
- services/providers/anthropic_client.py → AnthropicClient
- services/providers/gemini_client.py → GeminiClient
- services/providers/mistral_client.py → MistralClient
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from enum import Enum
import os
from dataclasses import dataclass
from dotenv import load_dotenv
from utils.flow_logger import function_logger

# Load environment variables
load_dotenv()


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    MISTRAL = "mistral"
    AZURE_OPENAI = "azure_openai"
    GROQ = "groq"


@dataclass
class LLMResponse:
    """Standardized LLM response across all providers."""
    content: str
    tokens_used: Optional[int] = None
    model: Optional[str] = None
    provider: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class LLMConfig:
    """LLM Configuration for any provider."""
    provider: LLMProvider
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    timeout: int = 30
    extra_params: Optional[Dict[str, Any]] = None


class BaseLLMService(ABC):
    """
    Abstract base class all LLM providers must implement.
    
    Defines the interface contract for:
    - Text generation (single response)
    - Streaming generation (chunks)
    - Token estimation
    """

    @function_logger("Handle __init__")
    @function_logger("Handle __init__")
    def __init__(self, config: LLMConfig):
        """Initialize LLM service."""
        self.config = config
        self.provider = config.provider.value

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a single response from LLM.
        
        Args:
            prompt: Main prompt/query
            system_prompt: Optional system instructions
            **kwargs: Provider-specific parameters
            
        Returns:
            LLMResponse with content and metadata
            
        Raises:
            RuntimeError: If generation fails
        """
        pass

    @abstractmethod
    async def generate_streaming(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        """
        Stream response from LLM as async generator.
        
        Args:
            prompt: Main prompt/query
            system_prompt: Optional system instructions
            **kwargs: Provider-specific parameters
            
        Yields:
            str chunks of response content
            
        Raises:
            RuntimeError: If streaming fails
        """
        pass

    @abstractmethod
    @function_logger("Execute estimate tokens")
    @function_logger("Execute estimate tokens")
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text (provider-specific).
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Approximate token count
        """
        pass


class LLMFactory:
    """
    Factory for creating LLM service instances.
    
    Strategy: Map providers → implementations and instantiate on demand.
    """

    _providers = {}

    @classmethod
    @function_logger("Initialize LLM provider implementations")
    @function_logger("Execute  init providers")
    def _init_providers(cls):
        """Lazy-load provider implementations."""
        if cls._providers:
            return
        
        # Lazy import to avoid circular dependencies
        from services.providers.openai_client import OpenAIClient
        from services.providers.anthropic_client import AnthropicClient
        from services.providers.gemini_client import GeminiClient
        from services.providers.mistral_client import MistralClient
        
        cls._providers = {
            LLMProvider.OPENAI: OpenAIClient,
            LLMProvider.ANTHROPIC: AnthropicClient,
            LLMProvider.GEMINI: GeminiClient,
            LLMProvider.MISTRAL: MistralClient,
        }

    @classmethod
    @function_logger("Create LLM service for provider")
    @function_logger("Create service")
    def create_service(cls, config: LLMConfig) -> BaseLLMService:
        """
        Create LLM service instance for given provider.
        
        Args:
            config: LLMConfig with provider and model details
            
        Returns:
            Appropriate BaseLLMService subclass instance
            
        Raises:
            ValueError: If provider not supported or config invalid
        """
        cls._init_providers()
        
        service_class = cls._providers.get(config.provider)
        if not service_class:
            supported = ", ".join([p.value for p in cls._providers.keys()])
            raise ValueError(
                f"Provider '{config.provider.value}' not supported. "
                f"Supported: {supported}"
            )
        
        return service_class(config)

    @classmethod
    @function_logger("Register custom LLM provider")
    @function_logger("Execute register provider")
    def register_provider(cls, provider: LLMProvider, service_class: type):
        """Register custom LLM provider implementation."""
        cls._init_providers()
        cls._providers[provider] = service_class


# ============================================================================
# GLOBAL SINGLETON MANAGEMENT
# ============================================================================

_llm_service: Optional[BaseLLMService] = None


@function_logger("Get or create global LLM service")
@function_logger("Get llm service")
def get_llm_service() -> BaseLLMService:
    """
    Get or create the global LLM service instance.
    
    Configuration from environment variables:
    - LLM_PROVIDER: Provider name (openai, anthropic, gemini, etc.)
    - LLM_MODEL: Model identifier (gpt-4, claude-3-opus, gemini-pro, etc.)
    - LLM_TEMPERATURE: Sampling temperature (0.0-1.0, default 0.7)
    - LLM_MAX_TOKENS: Max output tokens (default varies by provider)
    - LLM_API_KEY: API key (overrides provider-specific env var)
    - LLM_API_BASE: API base URL (for custom endpoints)
    - LLM_TIMEOUT: Request timeout in seconds (default 30)
    
    Returns:
        BaseLLMService: Global LLM service instance
        
    Raises:
        ValueError: If provider not supported or config invalid
    """
    global _llm_service
    
    if _llm_service is None:
        # Load configuration from environment
        provider_str = os.getenv("LLM_PROVIDER", "gemini").lower()
        # Map common aliases
        provider_str = "gemini" if provider_str in ["google", "gemini"] else provider_str
        
        try:
            provider = LLMProvider(provider_str)
        except ValueError:
            raise ValueError(f"Invalid LLM_PROVIDER: {provider_str}")
        
        config = LLMConfig(
            provider=provider,
            model=os.getenv("LLM_MODEL", _get_default_model(provider)),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4000")) if os.getenv("LLM_MAX_TOKENS") else None,
            api_key=os.getenv("LLM_API_KEY"),
            api_base=os.getenv("LLM_API_BASE"),
            timeout=int(os.getenv("LLM_TIMEOUT", "30"))
        )
        
        _llm_service = LLMFactory.create_service(config)
    
    return _llm_service


@function_logger("Get default model for provider")
@function_logger("Execute  get default model")
def _get_default_model(provider: LLMProvider) -> str:
    """Get default model name for provider."""
    defaults = {
        LLMProvider.OPENAI: "gpt-4-turbo",
        LLMProvider.ANTHROPIC: "claude-3-opus-20240229",
        LLMProvider.GEMINI: "gemini-pro",
        LLMProvider.MISTRAL: "mistral-large-latest",
    }
    return defaults.get(provider, "gpt-4-turbo")


@function_logger("Override global LLM service")
@function_logger("Set llm service")
def set_llm_service(service: BaseLLMService) -> None:
    """
    Override global LLM service instance.
    
    Useful for testing or dynamic provider switching.
    
    Args:
        service: BaseLLMService instance to use globally
    """
    global _llm_service
    _llm_service = service


@function_logger("Reset global LLM service")
@function_logger("Execute reset llm service")
def reset_llm_service() -> None:
    """
    Reset global LLM service to None.
    
    Useful for testing. Next call to get_llm_service() will reinitialize.
    """
    global _llm_service
    _llm_service = None
