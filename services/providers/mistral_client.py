from utils.flow_logger import function_logger
"""Mistral AI LLM Client Implementation."""

import os
from typing import Optional
import asyncio

from services.llm_service import BaseLLMService, LLMConfig, LLMResponse


class MistralClient(BaseLLMService):
    """Mistral AI LLM Client (Mistral API) - Using new async SDK."""

    @function_logger("Handle __init__")
    def __init__(self, config: LLMConfig):
        """Initialize Mistral client."""
        super().__init__(config)
        try:
            from mistralai import Mistral
            # Get API key from config or environment
            api_key = config.api_key or os.getenv("MISTRAL_API_KEY")
            if not api_key:
                raise ValueError("MISTRAL_API_KEY not found in environment or config")
            self.client = Mistral(api_key=api_key)
        except ImportError:
            raise ImportError("mistralai package required: pip install mistralai")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response from Mistral API."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Extract temperature and max_tokens from kwargs if provided
        temperature = kwargs.pop("temperature", self.config.temperature)
        max_tokens = kwargs.pop("max_tokens", self.config.max_tokens)
        
        # Merge remaining kwargs with extra_params (kwargs take precedence)
        call_params = {**(self.config.extra_params or {}), **kwargs}

        # Mistral client uses sync API, run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat.complete(
                model=self.config.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **call_params
            )
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            tokens_used=None,  # Mistral doesn't return token usage
            model=self.config.model,
            provider=self.provider,
            raw_response={"raw": str(response)}
        )

    async def generate_streaming(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        """Stream response from Mistral API."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Extract temperature and max_tokens from kwargs if provided
        temperature = kwargs.pop("temperature", self.config.temperature)
        max_tokens = kwargs.pop("max_tokens", self.config.max_tokens)
        
        # Merge remaining kwargs with extra_params (kwargs take precedence)
        call_params = {**(self.config.extra_params or {}), **kwargs}

        # Mistral streaming
        loop = asyncio.get_event_loop()
        stream = await loop.run_in_executor(
            None,
            lambda: self.client.chat.stream(
                model=self.config.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **call_params
            )
        )

        for event in stream:
            if hasattr(event, 'data') and hasattr(event.data, 'delta'):
                if event.data.delta.content:
                    yield event.data.delta.content

    @function_logger("Execute estimate tokens")
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation for Mistral."""
        # Mistral uses roughly 4 chars per token (similar to OpenAI)
        return len(text) // 4
