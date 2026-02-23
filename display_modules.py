#!/usr/bin/env python3
from utils.flow_logger import function_logger
"""
Display Generated Course Modules

Shows a pretty-printed version of a generated course outline
with all modules, learning objectives, and metadata.
"""

import asyncio
import json
from datetime import datetime


async def display_generated_module():
    """Display the modules from the latest generated course."""
    
    print("\n" + "="*100)
    print("📚 GENERATED COURSE MODULES - DSA (Data Structures & Algorithms)")
    print("="*100 + "\n")
    
    # ========================================================================
    # Generate a fresh course
    # ========================================================================
    print("🔄 Generating fresh course outline with ModuleCreationAgent...\n")
    
    try:
        from schemas.user_input import (
            UserInputSchema, AudienceLevel, AudienceCategory, 
            LearningMode, DepthRequirement
        )
        from schemas.execution_context import ExecutionContext
        from agents.module_creation_agent import ModuleCreationAgent
        
        # Create user input
        user_input = UserInputSchema(
            course_title="Data Structures and Algorithms (DSA)",
            course_description="Master fundamental data structures (arrays, linked lists, trees, graphs) and algorithms (sorting, searching, dynamic programming). Includes complexity analysis and practical implementations.",
            audience_level=AudienceLevel.INTERMEDIATE,
            audience_category=AudienceCategory.COLLEGE_STUDENTS,
            learning_mode=LearningMode.PRACTICAL_HANDS_ON,
            depth_requirement=DepthRequirement.IMPLEMENTATION_LEVEL,
            duration_hours=40,
        )
        
        # Create context
        context = ExecutionContext(
            user_input=user_input,
            session_id="display-test",
        )
        
        # Generate outline
        agent = ModuleCreationAgent()
        outline = await agent.run(context)
        
        # ====================================================================
        # Display Course Header
        # ====================================================================
        print("✅ Course outline generated successfully!\n")
        print(f"📖 {outline.course_title}")
        print(f"{'─' * 100}")
        
        print(f"\n📝 Course Summary:")
        print(f"   {outline.course_summary[:200]}...")
        
        print(f"\n👥 Audience: {outline.audience_level} ({outline.audience_category})")
        print(f"⏱️  Duration: {outline.total_duration_hours} hours")
        print(f"🎓 Depth: {outline.depth_requirement}")
        print(f"📚 Learning Mode: {outline.learning_mode}")
        
        print(f"\n⭐ Scores:")
        print(f"   - Completeness: {outline.completeness_score:.1%}")
        print(f"   - Confidence: {outline.confidence_score:.1%}")
        
        # ====================================================================
        # Display Learning Objectives
        # ====================================================================
        print(f"\n" + "="*100)
        print("🎯 COURSE-LEVEL LEARNING OBJECTIVES")
        print("="*100 + "\n")
        
        for i, obj in enumerate(outline.course_level_learning_objectives, 1):
            print(f"{i}. {obj.statement}")
            print(f"   └─ Bloom Level: {obj.bloom_level.value}")
            print(f"   └─ Assessment: {obj.assessment_method}\n")
        
        # ====================================================================
        # Display Modules
        # ====================================================================
        print("="*100)
        print(f"📚 MODULES ({len(outline.modules)} total)")
        print("="*100 + "\n")
        
        for module in outline.modules:
            print(f"┌─ {module.module_id}: {module.title}")
            print(f"│  ⏱️  Duration: {module.estimated_hours}h")
            print(f"│  📝 {module.description[:80]}...")
            
            # Learning objectives for this module
            if module.learning_objectives:
                print(f"│  🎯 Learning Objectives:")
                for obj in module.learning_objectives[:2]:
                    print(f"│     • {obj.statement[:70]}...")
                if len(module.learning_objectives) > 2:
                    print(f"│     ... and {len(module.learning_objectives) - 2} more")
            
            # Lessons
            if module.lessons:
                print(f"│  📖 Lessons:")
                for lesson in module.lessons[:2]:
                    print(f"│     • {lesson.title} ({lesson.duration_minutes}min)")
                if len(module.lessons) > 2:
                    print(f"│     ... and {len(module.lessons) - 2} more")
            
            # Assessment & Prerequisites
            print(f"│  ✅ Assessment: {module.assessment_type}")
            if module.prerequisites:
                print(f"│  📋 Prerequisites: {', '.join(module.prerequisites)}")
            
            if module.has_capstone:
                print(f"│  🏆 CAPSTONE PROJECT INCLUDED")
                if module.project_description:
                    print(f"│     {module.project_description[:60]}...")
            
            print(f"└─" + "─"*95 + "\n")
        
        # ====================================================================
        # Display References
        # ====================================================================
        print("="*100)
        print(f"📖 REFERENCES & SOURCES ({len(outline.references)} total)")
        print("="*100 + "\n")
        
        for i, ref in enumerate(outline.references, 1):
            print(f"{i}. {ref.title}")
            print(f"   └─ Type: {ref.source_type.value}")
            print(f"   └─ Confidence: {ref.confidence_score:.0%}")
            if ref.url:
                print(f"   └─ URL: {ref.url[:80]}...")
            print()
        
        # ====================================================================
        # Display as JSON (for export)
        # ====================================================================
        print("="*100)
        print("💾 FULL COURSE OUTLINE (JSON)")
        print("="*100 + "\n")
        
        # Convert to dict
        course_dict = outline.model_dump(exclude_none=True)
        json_output = json.dumps(course_dict, indent=2, default=str)
        
        # Show first 2000 chars
        print(json_output[:2000])
        print(f"\n... ({len(json_output)} total chars) ...\n")
        
        # Save to file
        import time
        filename = f"displayed_course_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(course_dict, f, indent=2, default=str)
        
        print(f"✅ Full course saved to: {filename}\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run display."""
    success = await display_generated_module()
    
    print("="*100)
    if success:
        print("✅ COURSE MODULES DISPLAYED SUCCESSFULLY")
    else:
        print("❌ FAILED TO DISPLAY MODULES")
    print("="*100 + "\n")
    
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
