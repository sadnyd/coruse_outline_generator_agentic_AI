#!/usr/bin/env python3
"""
Mistral AI Client - Direct Functional Test

Tests the Mistral client by directly setting API key and sending a prompt.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_mistral_direct():
    """Test Mistral client directly."""
    
    print("\n" + "=" * 75)
    print("🚀 MISTRAL AI CLIENT - DIRECT TEST")
    print("=" * 75 + "\n")
    
    # Get API key from environment
    mistral_api_key = os.getenv("MISTRAL_API_KEY", "").strip()
    
    if not mistral_api_key:
        print("❌ ERROR: MISTRAL_API_KEY not set in environment")
        print("\n📝 How to set up:")
        print("-" * 75)
        print("Option 1: Set in terminal before running")
        print("  $ export MISTRAL_API_KEY=your_api_key_here")
        print("  $ python tests/test_mistral_direct.py")
        print()
        print("Option 2: Add to .env file and load it")
        print("  Edit .env file:")
        print("    MISTRAL_API_KEY=your_api_key_here")
        print("  Then run with: python -c \"import os; exec(open('.env').read()); ...")
        print()
        print("Get your Mistral API key from: https://console.mistral.ai/")
        print("-" * 75 + "\n")
        return False
    
    print("✓ Mistral API key found")
    print(f"  Key: {mistral_api_key[:15]}..." + "\n")
    
    try:
        # Import required modules
        from services.llm_service import (
            LLMConfig, LLMFactory, LLMProvider
        )
        print("✓ LLM services imported\n")
        
        # Create config with explicit API key
        config = LLMConfig(
            provider=LLMProvider.MISTRAL,
            model="mistral-large",
            temperature=0.7,
            max_tokens=500,
            api_key=mistral_api_key
        )
        
        print("📋 Configuration:")
        print(f"   Provider: {config.provider.value}")
        print(f"   Model: {config.model}")
        print(f"   Temperature: {config.temperature}")
        print(f"   Max tokens: {config.max_tokens}\n")
        
        # Create Mistral client
        print("⏳ Creating Mistral client...")
        service = LLMFactory.create_service(config)
        print(f"✓ Client created: {type(service).__name__}\n")
        
        # Send test prompt
        prompt = "What is an aeroplane? Give a short, clear answer (2-3 sentences)."
        system_prompt = "You are a helpful assistant. Be concise and clear."
        
        print("📝 Sending test prompt to Mistral...")
        print(f"   Prompt: \"{prompt}\"")
        print(f"   System: \"{system_prompt}\"\n")
        print("-" * 75)
        print("⏳ Waiting for response...\n")
        
        # Call generate
        response = await service.generate(
            prompt=prompt,
            system_prompt=system_prompt
        )
        
        print("-" * 75 + "\n")
        print("✅ Response received!\n")
        
        # Show response details
        print("📊 Response Metadata:")
        print(f"   Provider: {response.provider}")
        print(f"   Model: {response.model}")
        print(f"   Tokens used: {response.tokens_used if response.tokens_used else 'N/A'}")
        print(f"   Content length: {len(response.content)} chars\n")
        
        print("💬 Response Content:")
        print("-" * 75)
        print(response.content)
        print("-" * 75 + "\n")
        
        # Validate response
        is_good = (
            len(response.content) > 50 and
            any(word in response.content.lower() for word in 
                ["aeroplane", "airplane", "aircraft", "flying", "vehicle"])
        )
        
        print("✓ Response validation:")
        print(f"   ✓ Non-empty: {len(response.content) > 0}")
        print(f"   ✓ Substantial: {len(response.content) > 50} ({len(response.content)} chars)")
        print(f"   ✓ Relevant: {is_good}")
        
        print("\n" + "=" * 75)
        print("✅ MISTRAL CLIENT TEST PASSED!")
        print("=" * 75 + "\n")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}\n")
        print("📦 Missing package. Install it with:")
        print("   pip install mistralai\n")
        return False
    
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error: {type(e).__name__}")
        print(f"   {error_msg}\n")
        
        if "401" in error_msg or "unauthorized" in error_msg.lower():
            print("💡 Hint: Your API key might be invalid or expired")
            print("   Check your Mistral console: https://console.mistral.ai/")
        elif "connection" in error_msg.lower():
            print("💡 Hint: Network connection issue")
            print("   Check your internet connection")
        
        print()
        return False


async def main():
    """Main entry point."""
    success = await test_mistral_direct()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
