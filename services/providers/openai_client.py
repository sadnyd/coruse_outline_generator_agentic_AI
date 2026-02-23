from utils.flow_logger import function_logger
"""OpenAI LLM Client Implementation."""

import os
from typing import Optional
from abc import ABC

from services.llm_service import BaseLLMService, LLMConfig, LLMResponse


class OpenAIClient(BaseLLMService):
    """OpenAI GPT LLM Client (OpenAI API)."""

    @function_logger("Handle __init__")
    def __init__(self, config: LLMConfig):
        """Initialize OpenAI client."""
        super().__init__(config)
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=config.api_key or os.getenv("OPENAI_API_KEY"))
        except ImportError:
            raise ImportError("openai package required: pip install openai")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response from OpenAI API."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Extract temperature and max_tokens from kwargs if provided
        temperature = kwargs.pop("temperature", self.config.temperature)
        max_tokens = kwargs.pop("max_tokens", self.config.max_tokens)
        
        # Merge remaining kwargs with extra_params (kwargs take precedence)
        call_params = {**(self.config.extra_params or {}), **kwargs}

        response = await self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=self.config.timeout,
            **call_params
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            tokens_used=response.usage.total_tokens if response.usage else None,
            model=response.model,
            provider=self.provider,
            raw_response=response.model_dump() if hasattr(response, "model_dump") else None
        )

    async def generate_streaming(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        """Stream response from OpenAI API."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        stream = await self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            stream=True,
            timeout=self.config.timeout,
            **(self.config.extra_params or {}),
            **kwargs
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    @function_logger("Execute estimate tokens")
    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens using tiktoken."""
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.config.model)
            return len(encoding.encode(text))
        except ImportError:
            # Rough estimate: 1 token ≈ 4 characters
            return len(text) // 4
