"""
Flow Logging Demo - Demonstrates request tracing across all agents.

This script shows how the complete flow is logged:
1. Frontend user input
2. Orchestrator processing
3. Agent execution
4. Utility function calls
5. LLM synthesis
6. Final output

Run this to see the flow.log file being populated with detailed execution traces.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from schemas.user_input import UserInputSchema, AudienceLevel, AudienceCategory, DepthRequirement, LearningMode
from agents.orchestrator import CourseOrchestratorAgent
from utils.flow_logger import (
    set_session_id, end_session, get_flow_logger, tail_logs, clear_logs, log_info
)
from uuid import uuid4


async def demo_full_flow():
    """Demonstrate a complete course generation flow with logging."""
    
    print("\n" + "="*80)
    print("FLOW LOGGING DEMONSTRATION")
    print("="*80)
    
    # Create session ID
    session_id = str(uuid4())
    print(f"\n📝 Session ID: {session_id[:8]}...\n")
    
    # Initialize logging for this session
    set_session_id(session_id)
    logger = get_flow_logger()
    
    log_info("Starting flow logging demonstration", {
        "session_id": session_id,
        "timestamp": "see flow.log for details"
    })
    
    try:
        # Step 1: Create user input (representing frontend form submission)
        print("Step 1: Creating user input...")
        user_input = UserInputSchema(
            course_title="Introduction to Machine Learning",
            course_description="Learn the fundamentals of ML including supervised learning, unsupervised learning, and basic deep learning concepts",
            audience_level=AudienceLevel.BEGINNER,
            audience_category=AudienceCategory.COLLEGE_STUDENTS,
            depth_requirement=DepthRequirement.IMPLEMENTATION_LEVEL,
            duration_hours=40,
            learning_mode=LearningMode.PROJECT_BASED
        )
        print(f"  ✓ Course: {user_input.course_title}")
        print(f"  ✓ Duration: {user_input.duration_hours} hours")
        print(f"  ✓ Audience: {user_input.audience_level.value}")
        
        # Step 2: Initialize orchestrator
        print("\nStep 2: Initializing orchestrator agent...")
        orchestrator = CourseOrchestratorAgent()
        print("  ✓ Orchestrator ready")
        
        # Step 3: Run orchestrator (this will call all sub-agents)
        print("\nStep 3: Executing orchestrator (this will trigger extensive logging)...")
        print("  → Retrieval Agent will query vector store")
        print("  → Web Search Agent will search for resources")
        print("  → Module Creation Agent will synthesize outline")
        print("  → All functions will be logged to flow.log\n")
        
        result = await orchestrator.run(user_input, session_id=session_id)
        
        if result:
            print("✅ Course generation completed!")
            if isinstance(result, dict):
                print(f"   Modules generated: {len(result.get('modules', []))}")
                print(f"   Total duration: {result.get('total_duration_hours', 0):.1f} hours")
        else:
            print("⚠️  Course generation returned None (likely due to missing LLM service or empty vector store)")
        
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # End session logging
        end_session()
        
        # Display sample logs
        print("\n" + "="*80)
        print("SAMPLE LOG ENTRIES (last 30 lines)")
        print("="*80)
        logs = tail_logs(30)
        print(logs)
        
        print("\n" + "="*80)
        print("📋 Full flow logged to: logs/flow.log")
        print("="*80)


def main():
    """Main entry point."""
    print("\n🔍 COMPREHENSIVE FLOW LOGGING SYSTEM\n")
    print("This demo will:")
    print("1. Initialize a course generation request")
    print("2. Execute the full orchestrator flow")
    print("3. Log every function call with inputs/outputs")
    print("4. Display sample log entries")
    print("\nCheck logs/flow.log for the complete detailed trace\n")
    
    input("Press Enter to start the demo...")
    
    # Clear logs for clean demonstration
    print("\n📝 Clearing previous logs...")
    clear_logs()
    
    # Run the demonstration
    asyncio.run(demo_full_flow())


if __name__ == "__main__":
    main()
