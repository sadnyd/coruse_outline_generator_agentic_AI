#!/usr/bin/env python3
"""
ModuleCreationAgent Unit Test

Tests all core functionality:
- Context validation
- Duration allocation
- Prompt building
- LLM integration
- JSON parsing
- Schema structuring
- Error handling
"""

import asyncio
import json


async def test_module_creation_agent():
    """Comprehensive test of ModuleCreationAgent."""
    
    print("\n" + "="*100)
    print("🧪 MODULE CREATION AGENT TEST")
    print("="*100 + "\n")
    
    # ========================================================================
    # SETUP: Import dependencies
    # ========================================================================
    print("📦 SETUP: Loading dependencies...")
    
    try:
        from schemas.user_input import (
            UserInputSchema, AudienceLevel, AudienceCategory, 
            LearningMode, DepthRequirement
        )
        from schemas.execution_context import ExecutionContext
        from agents.module_creation_agent import ModuleCreationAgent
        from schemas.course_outline import CourseOutlineSchema
        print("✅ All imports successful\n")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # ========================================================================
    # TEST 1: Context Validation
    # ========================================================================
    print("-"*100)
    print("TEST 1: Context Validation")
    print("-"*100 + "\n")
    
    agent = ModuleCreationAgent()
    
    # Test invalid context
    try:
        agent._validate_context(None)
        print("❌ Should have rejected None context")
        return False
    except ValueError as e:
        print(f"✅ Correctly rejected None context: {str(e)[:60]}...")
    
    # Test valid context
    user_input = UserInputSchema(
        course_title="DSA",
        course_description="Learn Data Structures and Algorithms from scratch",
        audience_level=AudienceLevel.BEGINNER,
        audience_category=AudienceCategory.COLLEGE_STUDENTS,
        learning_mode=LearningMode.HYBRID,
        depth_requirement=DepthRequirement.CONCEPTUAL,
        duration_hours=20,
    )
    
    context = ExecutionContext(
        user_input=user_input,
        session_id="test-session",
    )
    
    try:
        agent._validate_context(context)
        print("✅ Valid context accepted\n")
    except Exception as e:
        print(f"❌ Valid context rejected: {e}\n")
        return False
    
    # ========================================================================
    # TEST 2: Duration Allocation
    # ========================================================================
    print("-"*100)
    print("TEST 2: Duration Allocation")
    print("-"*100 + "\n")
    
    try:
        duration_plan = agent.duration_allocator.allocate(
            total_hours=20,
            depth_level=DepthRequirement.CONCEPTUAL,
            learning_mode=LearningMode.HYBRID
        )
        print(f"✅ Duration plan generated:")
        print(f"   - Modules: {duration_plan.get('num_modules')}")
        print(f"   - Avg per module: {duration_plan.get('avg_hours_per_module'):.1f}h")
        print(f"   - Depth guidance: {duration_plan.get('depth_guidance', {}).get('primary_blooms')}\n")
    except Exception as e:
        print(f"❌ Duration allocation failed: {e}\n")
        return False
    
    # ========================================================================
    # TEST 3: Prompt Building
    # ========================================================================
    print("-"*100)
    print("TEST 3: Prompt Building")
    print("-"*100 + "\n")
    
    try:
        from utils.learning_mode_templates import LearningModeTemplates
        
        mode_template = LearningModeTemplates.get_template(LearningMode.HYBRID)
        prompt = agent._build_prompt(context, duration_plan, mode_template)
        
        print(f"✅ Prompt generated ({len(prompt)} chars)")
        print(f"   - Contains course title: {'Test Course' in prompt}")
        print(f"   - Contains duration: {'20' in prompt}")
        print(f"   - Contains JSON format: {'json' in prompt.lower()}")
        print(f"   - Contains constraints: {'Bloom' in prompt or 'bloom' in prompt}\n")
    except Exception as e:
        print(f"❌ Prompt building failed: {e}\n")
        return False
    
    # ========================================================================
    # TEST 4: JSON Parsing (Edge Cases)
    # ========================================================================
    print("-"*100)
    print("TEST 4: JSON Parsing")
    print("-"*100 + "\n")
    
    test_cases = [
        ('Direct JSON', '{"modules": []}'),
        ('Markdown code block', '```json\n{"modules": []}\n```'),
        ('With extra text', 'Here is the outline: ```json\n{"modules": []}\n```'),
    ]
    
    all_parsing_passed = True
    for name, test_json in test_cases:
        try:
            result = agent._parse_llm_response(test_json)
            print(f"✅ {name}: Parsed successfully")
        except Exception as e:
            print(f"❌ {name}: {e}")
            all_parsing_passed = False
    
    if all_parsing_passed:
        print()
    else:
        return False
    
    # ========================================================================
    # TEST 5: Reference Building
    # ========================================================================
    print("-"*100)
    print("TEST 5: Reference Building")
    print("-"*100 + "\n")
    
    try:
        parsed_data = {
            "modules": [{"module_id": "M_1", "title": "Module 1"}],
            "references": [
                {"title": "Reference 1", "source_type": "web", "confidence_score": 0.9}
            ]
        }
        
        references = agent._build_references(parsed_data, context)
        print(f"✅ References built ({len(references)} total)")
        print(f"   - Types included: {set(ref.source_type for ref in references)}\n")
    except Exception as e:
        print(f"❌ Reference building failed: {e}\n")
        return False
    
    # ========================================================================
    # TEST 6: Score Calculation
    # ========================================================================
    print("-"*100)
    print("TEST 6: Score Calculation")
    print("-"*100 + "\n")
    
    try:
        # Test confidence score
        confidence = agent._calculate_confidence(context)
        print(f"✅ Confidence score: {confidence:.2f}")
        
        # Test completeness score
        completeness = agent._calculate_completeness([], [])
        print(f"✅ Completeness score (empty): {completeness:.2f}")
        print()
    except Exception as e:
        print(f"❌ Score calculation failed: {e}\n")
        return False
    
    # ========================================================================
    # TEST 7: Full Pipeline Integration (Real LLM Call)
    # ========================================================================
    print("-"*100)
    print("TEST 7: Full Pipeline Integration (Real LLM)")
    print("-"*100 + "\n")
    
    try:
        print("Running full agent pipeline with context...")
        print("(This will call Mistral LLM - may take 15-30 seconds)\n")
        
        result = await agent.run(context)
        
        # Validate result
        if not isinstance(result, CourseOutlineSchema):
            print(f"❌ Expected CourseOutlineSchema, got {type(result)}")
            return False
        
        print(f"✅ Pipeline completed successfully!")
        print(f"\nGenerated outline:")
        print(f"   - Title: {result.course_title}")
        print(f"   - Modules: {len(result.modules)}")
        print(f"   - Learning objectives: {len(result.course_level_learning_objectives)}")
        print(f"   - References: {len(result.references)}")
        print(f"   - Completeness: {result.completeness_score:.2f}")
        print(f"   - Confidence: {result.confidence_score:.2f}\n")
        
    except Exception as e:
        print(f"❌ Full pipeline failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False
    
    # ========================================================================
    # TEST 8: Error Handling
    # ========================================================================
    print("-"*100)
    print("TEST 8: Error Handling")
    print("-"*100 + "\n")
    
    # Test invalid JSON parsing
    try:
        agent._parse_llm_response("This is not JSON at all")
        print("❌ Should have rejected invalid JSON")
        return False
    except ValueError:
        print("✅ Correctly rejected invalid JSON")
    
    # Test objective parsing with invalid bloom level
    try:
        obj = agent._parse_objective({"statement": "Test", "bloom_level": "invalid"})
        print(f"✅ Fallback bloom level applied: {obj.bloom_level.value}")
    except Exception as e:
        print(f"❌ Objective parsing failed: {e}")
        return False
    
    print()
    
    return True


async def main():
    """Run all tests."""
    success = await test_module_creation_agent()
    
    print("="*100)
    if success:
        print("✅ MODULE CREATION AGENT - ALL TESTS PASSED")
    else:
        print("❌ MODULE CREATION AGENT - TESTS FAILED")
    print("="*100 + "\n")
    
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
