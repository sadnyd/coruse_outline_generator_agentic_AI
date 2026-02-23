"""
Services Package

Abstraction layers for external dependencies:
- LLM providers (OpenAI, Anthropic, etc.)
- Database providers (PostgreSQL, MongoDB, etc.)

Usage:
    from services import get_llm_service, get_db_service
    
    llm = get_llm_service()
    db = get_db_service()
"""

from .llm_service import (
    BaseLLMService,
    LLMProvider,
    LLMConfig,
    LLMResponse,
    LLMFactory,
    get_llm_service,
    set_llm_service,
    reset_llm_service,
)

from .db_service import (
    BaseDatabase,
    DatabaseProvider,
    DatabaseConfig,
    DatabaseFactory,
    PostgreSQLDatabase,
    MockDatabase,
    get_db_service,
    set_db_service,
    reset_db_service,
)

__all__ = [
    # LLM
    "BaseLLMService",
    "LLMProvider",
    "LLMConfig",
    "LLMResponse",
    "LLMFactory",
    "get_llm_service",
    "set_llm_service",
    "reset_llm_service",
    
    # Database
    "BaseDatabase",
    "DatabaseProvider",
    "DatabaseConfig",
    "DatabaseFactory",
    "PostgreSQLDatabase",
    "MockDatabase",
    "get_db_service",
    "set_db_service",
    "reset_db_service",
]
