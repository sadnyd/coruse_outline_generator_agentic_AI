# LLM Service Architecture - Quick Reference

## 📚 Import Paths (For Agents)

```python
# Main public API
from services.llm_service import (
    get_llm_service,           # Get global singleton
    set_llm_service,           # Override (testing)
    reset_llm_service,         # Reset singleton
    LLMConfig,                 # Configuration
    LLMResponse,               # Response template
    LLMProvider,               # Provider enum
    BaseLLMService,            # Abstract base
    LLMFactory,                # Factory (advanced)
)
```

## 🏗️ Directory Structure

```
services/
├── __init__.py                 (Clean public API exports)
├── llm_service.py              (280 lines - Abstraction only)
│   └─ No provider imports at module level (lazy load)
│
├── providers/
│   ├── __init__.py             (Provider exports)
│   ├── openai_client.py        (88 lines)
│   ├── anthropic_client.py     (85 lines)
│   └── gemini_client.py        (103 lines)
│
└── (other services: db_service.py, vector_store.py, etc.)
```

## 🔌 Provider Implementations

| Provider | File | Class | Interface |
|----------|------|-------|-----------|
| OpenAI | `providers/openai_client.py` | `OpenAIClient` | `BaseLLMService` |
| Anthropic | `providers/anthropic_client.py` | `AnthropicClient` | `BaseLLMService` |
| Gemini | `providers/gemini_client.py` | `GeminiClient` | `BaseLLMService` |

## 📋 Common Tasks

### Use Default LLM
```python
from services.llm_service import get_llm_service

service = get_llm_service()  # Auto-initializes from env vars
response = await service.generate("Your prompt")
```

### Override Provider (Testing)
```python
from services.llm_service import set_llm_service, LLMConfig, LLMFactory, LLMProvider

config = LLMConfig(provider=LLMProvider.OPENAI, model="gpt-4")
custom_service = LLMFactory.create_service(config)
set_llm_service(custom_service)

# All agents now use OpenAI
```

### Add New Provider
```
1. Create: services/providers/new_provider_client.py

class NewProviderClient(BaseLLMService):
    async def generate(self, prompt, system_prompt=None, **kwargs):
        # Implementation
        pass
    async def generate_streaming(self, prompt, system_prompt=None, **kwargs):
        # Implementation
        pass
    def estimate_tokens(self, text: str) -> int:
        # Implementation
        pass

2. Register in services/llm_service.py:
   Add to LLMFactory._init_providers():
   cls._providers[LLMProvider.NEW_PROVIDER] = NewProviderClient

3. Done! No other files need changes.
```

### Test Individual Provider
```python
from services.providers.openai_client import OpenAIClient
from services.llm_service import LLMConfig, LLMProvider

config = LLMConfig(
    provider=LLMProvider.OPENAI, 
    model="gpt-4",
    api_key="test_key"
)
client = OpenAIClient(config)
response = await client.generate("test prompt")
```

## 🌍 Environment Variables

```bash
LLM_PROVIDER=gemini              # Provider name
LLM_MODEL=gemini-pro             # Model identifier
LLM_TEMPERATURE=0.7              # Sampling temp (0.0-1.0)
LLM_MAX_TOKENS=4000              # Max output tokens
LLM_API_KEY=your_api_key         # API key
LLM_API_BASE=https://...         # Custom endpoint (optional)
LLM_TIMEOUT=30                   # Request timeout (seconds)
```

## ✅ Design Principles

| Principle | How It's Achieved |
|-----------|-------------------|
| **Single Responsibility** | Each provider in own file, llm_service = factory only |
| **Dependency Inversion** | Agents depend on BaseLLMService interface, not implementations |
| **No Circular Imports** | Lazy loading in factory._init_providers() method |
| **Backward Compatible** | Agent code unchanged, same import paths |
| **Extensible** | Add provider = add one file + register in factory |
| **Testable** | Mock BaseLLMService, test providers in isolation |

## ❌ Anti-Patterns (Fixed)

| ❌ Before | ✅ After |
|----------|---------|
| Monolithic 447-line file | Separated into 4 focused files |
| All logic in one place | Clear layer separation |
| Hard to find provider code | Each provider in own file |
| Editing one file to add provider | Add one new file |
| No isolation for testing | Test providers independently |

## 🚀 Performance Notes

- **Lazy Loading**: Providers only imported when factory creates them
  - If only Gemini used → OpenAI/Anthropic code never loaded
  - Faster startup, smaller memory footprint
  
- **Singleton Management**: `get_llm_service()` creates once, reuses
  - First call: Initialize from env vars
  - Subsequent calls: Return cached instance

- **Async Support**: All provider methods are async-ready
  - `generate()`: Single response
  - `generate_streaming()`: Async generator yields chunks

---

## 📞 For Questions

- Architecture: Read `docs/LLM_SERVICE_REFACTORING.md`
- Quick start: See above "Common Tasks"
- Implementation: Check `services/providers/openai_client.py` (example)
- Factory logic: See `services/llm_service.py` (lines 120-180)
