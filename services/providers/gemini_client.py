from utils.flow_logger import function_logger
"""Google Gemini LLM Client Implementation."""

import os
from typing import Optional
import asyncio

from services.llm_service import BaseLLMService, LLMConfig, LLMResponse


class GeminiClient(BaseLLMService):
    """Google Gemini LLM Client (Google Generative AI API)."""

    @function_logger("Handle __init__")
    def __init__(self, config: LLMConfig):
        """Initialize Gemini client."""
        super().__init__(config)
        try:
            from google import genai
            # Check for Gemini API key in environment (multiple names supported)
            api_key = config.api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not found in environment or config")
            # Create client with API key
            self.client = genai.Client(api_key=api_key)
            self.model_name = config.model
        except ImportError:
            raise ImportError("google-genai package required: pip install google-genai")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response from Gemini API."""
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            response = await self._async_generate(full_prompt, **kwargs)
            
            return LLMResponse(
                content=response.text,
                tokens_used=None,  # Gemini doesn't expose token count easily
                model=self.model_name,
                provider="gemini",
                raw_response={"raw": str(response)}
            )
        except Exception as e:
            raise RuntimeError(f"Gemini generation failed: {str(e)}")

    async def _async_generate(self, prompt: str, **kwargs):
        """Async wrapper for Gemini generate (which is sync)."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self._get_generation_config(**kwargs)
            )
        )

    async def generate_streaming(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        """Stream response from Gemini API (as async generator)."""
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        loop = asyncio.get_event_loop()
        
        response = await loop.run_in_executor(
            None,
            lambda: self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=self._get_generation_config(**kwargs),
                stream=True
            )
        )
        
        for chunk in response:
            if chunk.text:
                yield chunk.text

    @function_logger("Execute  get generation config")
    def _get_generation_config(self, **kwargs):
        """Get Gemini generation config."""
        try:
            from google.genai.types import GenerateContentConfig
            return GenerateContentConfig(
                temperature=kwargs.get('temperature', self.config.temperature),
                max_output_tokens=kwargs.get('max_tokens', self.config.max_tokens or 2048),
            )
        except ImportError:
            # Fallback if config import fails
            return None

    @function_logger("Execute estimate tokens")
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation for Gemini."""
        # Gemini uses roughly 4 chars per token (similar to OpenAI)
        return len(text) // 4
