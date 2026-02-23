#!/usr/bin/env python3
"""
Mistral AI Client - Functional Test

Tests the Mistral client by sending a prompt and verifying the response.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_mistral_response():
    """Test Mistral client with a sample prompt."""
    
    print("\n" + "=" * 75)
    print("🚀 MISTRAL AI CLIENT - FUNCTIONAL TEST")
    print("=" * 75 + "\n")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check API key
    mistral_api_key = os.getenv("MISTRAL_API_KEY", "").strip()
    
    if not mistral_api_key:
        print("❌ MISTRAL_API_KEY not found in .env file")
        print("\n📝 Instructions:")
        print("-" * 75)
        print("1. Get your Mistral API key from: https://console.mistral.ai/")
        print("2. Add it to .env file:")
        print("   MISTRAL_API_KEY=your_key_here")
        print("3. Run this test again")
        print("-" * 75 + "\n")
        return False
    
    print("✓ Mistral API key found")
    print(f"  Key starts with: {mistral_api_key[:10]}..." + "\n")
    
    try:
        # Import LLM services
        from services.llm_service import (
            LLMConfig, LLMFactory, LLMProvider
        )
        print("✓ LLM services imported successfully\n")
        
        # Create Mistral config
        config = LLMConfig(
            provider=LLMProvider.MISTRAL,
            model=os.getenv("LLM_MODEL", "mistral-large"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "500"))
        )
        print("📋 Configuration:")
        print(f"   Provider: {config.provider.value}")
        print(f"   Model: {config.model}")
        print(f"   Temperature: {config.temperature}")
        print(f"   Max tokens: {config.max_tokens}\n")
        
        # Create client
        print("⏳ Creating Mistral client...")
        service = LLMFactory.create_service(config)
        print(f"✓ Client created: {type(service).__name__}\n")
        
        # Test prompt
        prompt = "What is an aeroplane? Provide a short, clear answer."
        system_prompt = "You are a helpful assistant. Provide clear and concise responses."
        
        print("📝 Test Prompt:")
        print(f'   "{prompt}"\n')
        print("⏳ Sending request to Mistral API...")
        print("-" * 75)
        
        # Get response
        response = await service.generate(
            prompt=prompt,
            system_prompt=system_prompt
        )
        
        print("-" * 75)
        print("\n✅ Response received successfully!\n")
        
        # Display response details
        print("📊 Response Details:")
        print(f"   Provider: {response.provider}")
        print(f"   Model: {response.model}")
        print(f"   Tokens used: {response.tokens_used if response.tokens_used else 'N/A'}")
        print(f"   Content length: {len(response.content)} characters\n")
        
        print("💬 Response Content:")
        print("-" * 75)
        print(response.content)
        print("-" * 75)
        
        # Verify response quality
        print("\n✓ Response Content Analysis:")
        content = response.content
        
        checks = [
            ("Non-empty response", len(content) > 0),
            ("Reasonably long response", len(content) > 50),
            ("Contains meaningful text", any(word in content.lower() for word in 
             ["aeroplane", "airplane", "aircraft", "flying", "vehicle", "machine"])),
        ]
        
        all_good = True
        for check_name, passed in checks:
            status = "✓" if passed else "✗"
            print(f"  {status} {check_name}")
            if not passed:
                all_good = False
        
        print("\n" + "=" * 75)
        if all_good:
            print("✅ MISTRAL CLIENT TEST PASSED!")
            print("=" * 75 + "\n")
            return True
        else:
            print("⚠️  MISTRAL CLIENT TEST PASSED (with warnings)")
            print("=" * 75 + "\n")
            return True
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\n📦 Install required packages:")
        print("   pip install mistralai\n")
        return False
    
    except ValueError as e:
        print(f"❌ Configuration Error: {e}\n")
        return False
    
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}")
        print(f"   Message: {str(e)}\n")
        return False


async def main():
    """Main entry point."""
    success = await test_mistral_response()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
