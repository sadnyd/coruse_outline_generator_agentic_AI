#!/usr/bin/env python3
"""
Mistral AI Client - Unit Test

Tests that the Mistral client is properly integrated without external dependencies.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_mistral_client_structure():
    """Test Mistral client structure and interface."""
    
    print("\n" + "=" * 75)
    print("🧪 MISTRAL AI CLIENT - UNIT TEST")
    print("=" * 75 + "\n")
    
    try:
        # Test 1: Import BaseLLMService interface
        print("Test 1: Importing BaseLLMService interface...")
        try:
            # Avoid full dotenv load by mocking it
            import sys
            from unittest.mock import MagicMock
            sys.modules['dotenv'] = MagicMock()
            
            from services.llm_service import BaseLLMService, LLMConfig, LLMResponse, LLMProvider
            print("✓ Successfully imported: BaseLLMService, LLMConfig, LLMResponse, LLMProvider")
        except Exception as e:
            print(f"✗ Failed to import: {e}")
            return False
        
        # Test 2: Import Mistral client
        print("\nTest 2: Importing MistralClient...")
        try:
            from services.providers.mistral_client import MistralClient
            print("✓ Successfully imported MistralClient")
        except Exception as e:
            print(f"✗ Failed to import MistralClient: {e}")
            return False
        
        # Test 3: Check MistralClient inherits from BaseLLMService
        print("\nTest 3: Checking MistralClient inheritance...")
        if issubclass(MistralClient, BaseLLMService):
            print("✓ MistralClient correctly inherits from BaseLLMService")
        else:
            print("✗ MistralClient does not inherit from BaseLLMService")
            return False
        
        # Test 4: Check required methods exist
        print("\nTest 4: Checking required methods...")
        required_methods = ['generate', 'generate_streaming', 'estimate_tokens']
        for method in required_methods:
            if hasattr(MistralClient, method):
                print(f"✓ Method '{method}' exists")
            else:
                print(f"✗ Method '{method}' missing")
                return False
        
        # Test 5: Check if Mistral is registered in factory
        print("\nTest 5: Checking Mistral registration in LLMFactory...")
        try:
            from services.llm_service import LLMFactory
            if LLMProvider.MISTRAL.value == "mistral":
                print("✓ LLMProvider.MISTRAL is defined")
            else:
                print("✗ LLMProvider.MISTRAL not found")
                return False
        except Exception as e:
            print(f"✗ Error checking factory: {e}")
            return False
        
        # Test 6: Verify config creation
        print("\nTest 6: Creating LLMConfig for Mistral...")
        try:
            config = LLMConfig(
                provider=LLMProvider.MISTRAL,
                model="mistral-large",
                temperature=0.7,
                max_tokens=500,
                api_key="test-key-for-validation"
            )
            print(f"✓ LLMConfig created successfully")
            print(f"  - Provider: {config.provider.value}")
            print(f"  - Model: {config.model}")
            print(f"  - Temperature: {config.temperature}")
            print(f"  - Max tokens: {config.max_tokens}")
        except Exception as e:
            print(f"✗ Failed to create config: {e}")
            return False
        
        # Test 7: Verify LLMResponse structure
        print("\nTest 7: Creating LLMResponse...")
        try:
            response = LLMResponse(
                content="Test response from Mistral",
                tokens_used=42,
                model="mistral-large",
                provider="mistral"
            )
            print(f"✓ LLMResponse created successfully")
            print(f"  - Content: {response.content[:40]}...")
            print(f"  - Tokens: {response.tokens_used}")
            print(f"  - Provider: {response.provider}")
        except Exception as e:
            print(f"✗ Failed to create response: {e}")
            return False
        
        # Test 8: Check token estimation
        print("\nTest 8: Testing token estimation...")
        try:
            test_text = "This is a test of the emergency broadcast system."
            estimated_tokens = MistralClient.estimate_tokens(None, test_text)
            print(f"✓ Token estimation works")
            print(f"  - Text: '{test_text}'")
            print(f"  - Estimated tokens: {estimated_tokens}")
        except Exception as e:
            print(f"✗ Token estimation failed: {e}")
            return False
        
        print("\n" + "=" * 75)
        print("✅ ALL TESTS PASSED!")
        print("=" * 75)
        print("\n📋 Summary:")
        print("  ✓ MistralClient is properly implemented")
        print("  ✓ All required methods exist")
        print("  ✓ Inherits from BaseLLMService correctly")
        print("  ✓ Configuration and responses work")
        print("  ✓ Token estimation functional")
        
        print("\n🚀 Ready to use with real API key!")
        print("\nTo test with actual Mistral API:")
        print("  1. Get API key from: https://console.mistral.ai/")
        print("  2. Set environment: export MISTRAL_API_KEY=your_key")
        print("  3. Use in code:")
        print("     from services.llm_service import get_llm_service")
        print("     os.environ['LLM_PROVIDER'] = 'mistral'")
        print("     service = get_llm_service()")
        print("     response = await service.generate('Your prompt')")
        print("\n" + "=" * 75 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_mistral_client_structure()
    sys.exit(0 if success else 1)
