"""Test Mistral AI Client with a simple prompt."""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_mistral_client():
    """Test Mistral AI client with a sample prompt."""
    from services.llm_service import (
        LLMConfig, LLMFactory, LLMProvider
    )
    
    # Check if API key is available
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("⚠️  MISTRAL_API_KEY not found in environment variables")
        print("Set it with: export MISTRAL_API_KEY=your_key_here")
        return
    
    print("🚀 Testing Mistral AI Client")
    print("=" * 60)
    
    try:
        # Create Mistral config
        config = LLMConfig(
            provider=LLMProvider.MISTRAL,
            model="mistral-large",
            temperature=0.7,
            max_tokens=500
        )
        
        print(f"✓ Configuration created")
        print(f"  Provider: {config.provider.value}")
        print(f"  Model: {config.model}")
        print(f"  Temperature: {config.temperature}")
        print(f"  Max tokens: {config.max_tokens}")
        print()
        
        # Create client via factory
        service = LLMFactory.create_service(config)
        print(f"✓ Mistral client instantiated")
        print(f"  Client type: {type(service).__name__}")
        print()
        
        # Send test prompt
        prompt = "What is an aeroplane?"
        system_prompt = "You are a helpful assistant. Provide clear and concise answers."
        
        print(f"📝 Sending prompt: '{prompt}'")
        print(f"   System prompt: '{system_prompt}'")
        print()
        print("⏳ Waiting for response from Mistral API...")
        print("-" * 60)
        
        response = await service.generate(
            prompt=prompt,
            system_prompt=system_prompt
        )
        
        print("✅ Response received!")
        print()
        print("📋 Response Details:")
        print(f"  Provider: {response.provider}")
        print(f"  Model: {response.model}")
        print(f"  Tokens used: {response.tokens_used if response.tokens_used else 'N/A'}")
        print()
        print("💬 Response Content:")
        print("-" * 60)
        print(response.content)
        print("-" * 60)
        print()
        print("✅ Test completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Install mistralai package: pip install mistralai")
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
    except Exception as e:
        print(f"❌ Error occurred: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(test_mistral_client())
