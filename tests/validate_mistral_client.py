"""Validation test for Mistral AI Client structure."""

import sys
import os

def validate_mistral_integration():
    """Validate that Mistral client is properly integrated."""
    
    print("🔍 Validating Mistral AI Client Integration")
    print("=" * 70)
    
    checks = []
    
    # Check 1: Mistral client file exists
    mistral_file = "services/providers/mistral_client.py"
    exists = os.path.exists(mistral_file)
    checks.append((f"✓ {mistral_file} exists" if exists else f"✗ {mistral_file} missing", exists))
    
    # Check 2: Check llm_service.py has MISTRAL in enum
    try:
        with open("services/llm_service.py", "r") as f:
            content = f.read()
            has_mistral_enum = "MISTRAL = \"mistral\"" in content
            checks.append((f"✓ MISTRAL in LLMProvider enum" if has_mistral_enum else f"✗ MISTRAL not in enum", has_mistral_enum))
            
            has_mistral_import = "from services.providers.mistral_client import MistralClient" in content
            checks.append((f"✓ MistralClient imported in factory" if has_mistral_import else f"✗ MistralClient not imported", has_mistral_import))
            
            has_mistral_registered = "LLMProvider.MISTRAL: MistralClient" in content
            checks.append((f"✓ MistralClient registered in factory" if has_mistral_registered else f"✗ MistralClient not registered", has_mistral_registered))
            
            has_mistral_default = "LLMProvider.MISTRAL: \"mistral-large\"" in content
            checks.append((f"✓ Mistral default model set" if has_mistral_default else f"✗ Mistral default model missing", has_mistral_default))
    except Exception as e:
        checks.append((f"✗ Could not read llm_service.py: {e}", False))
    
    # Check 3: Check providers __init__.py exports MistralClient
    try:
        with open("services/providers/__init__.py", "r") as f:
            content = f.read()
            has_mistral_export = "from services.providers.mistral_client import MistralClient" in content
            checks.append((f"✓ MistralClient exported from providers" if has_mistral_export else f"✗ MistralClient not exported", has_mistral_export))
    except Exception as e:
        checks.append((f"✗ Could not read providers/__init__.py: {e}", False))
    
    # Check 4: Verify MistralClient class structure
    if exists:
        try:
            with open(mistral_file, "r") as f:
                content = f.read()
                has_class = "class MistralClient(BaseLLMService)" in content
                checks.append((f"✓ MistralClient class defined correctly" if has_class else f"✗ MistralClient class malformed", has_class))
                
                has_generate = "async def generate(" in content
                checks.append((f"✓ generate() method implemented" if has_generate else f"✗ generate() missing", has_generate))
                
                has_streaming = "async def generate_streaming(" in content
                checks.append((f"✓ generate_streaming() method implemented" if has_streaming else f"✗ generate_streaming() missing", has_streaming))
                
                has_tokens = "def estimate_tokens(" in content
                checks.append((f"✓ estimate_tokens() method implemented" if has_tokens else f"✗ estimate_tokens() missing", has_tokens))
        except Exception as e:
            checks.append((f"✗ Could not read mistral_client.py: {e}", False))
    
    # Print results
    print()
    all_passed = True
    for check_msg, passed in checks:
        print(check_msg)
        if not passed:
            all_passed = False
    
    print()
    print("=" * 70)
    
    if all_passed:
        print("✅ All validation checks PASSED!")
        print()
        print("📋 Mistral Client is ready to use!")
        print()
        print("Usage:")
        print("-" * 70)
        print("""
from services.llm_service import LLMConfig, LLMFactory, LLMProvider

# Create config
config = LLMConfig(
    provider=LLMProvider.MISTRAL,
    model="mistral-large",
    api_key="your_mistral_api_key"
)

# Get client
client = LLMFactory.create_service(config)

# Use it
response = await client.generate("Your prompt here")
print(response.content)
""")
        print("-" * 70)
        return 0
    else:
        print("❌ Some validation checks FAILED!")
        print("Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = validate_mistral_integration()
    sys.exit(exit_code)
