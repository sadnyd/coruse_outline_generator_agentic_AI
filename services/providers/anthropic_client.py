from utils.flow_logger import function_logger
"""Anthropic Claude LLM Client Implementation."""

import os
from typing import Optional

from services.llm_service import BaseLLMService, LLMConfig, LLMResponse


class AnthropicClient(BaseLLMService):
    """Anthropic Claude LLM Client (Claude API)."""

    @function_logger("Handle __init__")
    def __init__(self, config: LLMConfig):
        """Initialize Anthropic client."""
        super().__init__(config)
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=config.api_key or os.getenv("ANTHROPIC_API_KEY"))
        except ImportError:
            raise ImportError("anthropic package required: pip install anthropic")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response from Anthropic API."""
        import asyncio
        loop = asyncio.get_event_loop()
        
        # Extract temperature and max_tokens from kwargs if provided
        temperature = kwargs.pop("temperature", self.config.temperature)
        max_tokens = kwargs.pop("max_tokens", self.config.max_tokens or 1024)
        
        # Merge remaining kwargs with extra_params (kwargs take precedence)
        call_params = {**(self.config.extra_params or {}), **kwargs}
        
        response = await loop.run_in_executor(
            None,
            lambda: self.client.messages.create(
                model=self.config.model,
                max_tokens=max_tokens,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                timeout=self.config.timeout,
                **call_params
            )
        )

        return LLMResponse(
            content=response.content[0].text if response.content else "",
            tokens_used=response.usage.output_tokens if response.usage else None,
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
        """Stream response from Anthropic API (sync streams as async generator)."""
        import asyncio
        loop = asyncio.get_event_loop()
        
        # Get stream in thread executor
        stream = await loop.run_in_executor(
            None,
            lambda: self.client.messages.stream(
                model=self.config.model,
                max_tokens=self.config.max_tokens or 1024,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.temperature,
                timeout=self.config.timeout,
                **(self.config.extra_params or {}),
                **kwargs
            ).__enter__()
        )
        
        for text in stream.text_stream:
            yield text

    @function_logger("Execute estimate tokens")
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation for Anthropic."""
        # Anthropic uses roughly 75 tokens per 500 characters
        return int((len(text) / 500) * 75)
