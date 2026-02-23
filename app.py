from utils.flow_logger import function_logger
"""
Main Streamlit app entry point 
"""

import streamlit as st
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

# Imports
from utils.session import SessionManager
from schemas.user_input import (
    UserInputSchema, AudienceLevel, AudienceCategory,
    LearningMode, DepthRequirement
)
from schemas.course_outline import CourseOutlineSchema
from agents.orchestrator import CourseOrchestratorAgent
from agents.query_agent import InteractiveQueryAgent, QuerySessionContext
from tools.pdf_loader import PDFProcessor
import json


# ============================================================================
# INITIALIZATION & GLOBAL STATE
# ============================================================================

@function_logger("Execute init session manager")
def init_session_manager():
    """Initialize session manager (stored in st.session_state)."""
    if "session_manager" not in st.session_state:
        st.session_state.session_manager = SessionManager(ttl_minutes=30)
    return st.session_state.session_manager


@function_logger("Execute init session")
def init_session():
    """Initialize or recover current user session."""
    sm = init_session_manager()
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = sm.create_session()
    
    return st.session_state.session_id


@function_logger("Get session data")
def get_session_data() -> Optional[Dict[str, Any]]:
    """Get current session data."""
    sm = init_session_manager()
    session_id = st.session_state.get("session_id")
    return sm.get_session(session_id)


@function_logger("Update session data")
def update_session_data(key: str, value: Any):
    """Update current session."""
    sm = init_session_manager()
    session_id = st.session_state.get("session_id")
    if session_id:
        sm.update_session(session_id, key, value)


@function_logger("Process query with query agent")
async def process_query(query: str, outline_dict: Dict[str, Any], user_input_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process educator query using Query Agent.
    
    Args:
        query: User question/request
        outline_dict: Generated course outline
        user_input_dict: Original user input
    
    Returns:
        Query result with response and metadata
    """
    try:
        # Convert outline dict to CourseOutlineSchema
        outline = CourseOutlineSchema.model_validate(outline_dict)
        
        # Convert user input dict to UserInputSchema
        user_input = UserInputSchema.model_validate(user_input_dict)
        
        # Create query session context
        context = QuerySessionContext(
            user_input=user_input,
            final_outline=outline,
            retrieved_docs=[],
            web_results=[],
            validator_feedback={}
        )
        
        # Initialize query agent and process query
        query_agent = InteractiveQueryAgent()
        result = await query_agent.process_query(query, context)
        
        return result
    
    except Exception as e:
        return {
            "status": "error",
            "response": f"Query processing failed: {str(e)}",
            "requires_action": False
        }


# ============================================================================
# UI SECTIONS
# ============================================================================

@function_logger("Execute render header")
def render_header():
    """Render app header."""
    st.set_page_config(
        page_title="Course AI Agent",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    st.title("📚 Course Outline Generator")
    st.markdown(
        "Create comprehensive, educator-friendly course outlines. "
        "Combine your expertise with intelligent synthesis."
    )


@function_logger("Execute render input form")
def render_input_form() -> tuple[Optional[UserInputSchema], Optional[str]]:
    """
    Render input form in persistent left sidebar (STEP 1.2).
    
    Returns:
        Tuple of (UserInputSchema if valid, PDF path if uploaded), (None, None) otherwise
    """
    with st.form("course_form", clear_on_submit=False):
        # Required text fields
        course_title = st.text_input(
            "Course Title *",
            placeholder="e.g., 'Introduction to Machine Learning'",
            help="Short, descriptive title"
        )
        
        duration_hours = st.number_input(
            "Duration (hours) *",
            min_value=1, max_value=500,
            value=40,
            help="Total course duration in hours"
        )
        
        # Course description
        course_description = st.text_area(
            "Course Description *",
            placeholder="Describe the course goals, scope, and key topics...",
            height=80,
            help="Free-text description of what this course covers"
        )
        
        # Dropdowns
        audience_level = st.selectbox(
            "Audience Level *",
            options=[level.value for level in AudienceLevel],
            format_func=lambda x: x.replace("_", " ").title(),
            help="Educational level of your target learners"
        )
        
        audience_category = st.selectbox(
            "Audience Background *",
            options=[cat.value for cat in AudienceCategory],
            format_func=lambda x: x.replace("_", " ").title(),
            help="Professional or educational background"
        )
        
        learning_mode = st.selectbox(
            "Learning Mode *",
            options=[mode.value for mode in LearningMode],
            format_func=lambda x: x.replace("_", " ").title(),
            help="How will the course be delivered?"
        )
        
        depth_requirement = st.selectbox(
            "Depth Requirement *",
            options=[depth.value for depth in DepthRequirement],
            format_func=lambda x: x.replace("_", " ").title(),
            help="Theoretical vs practical balance"
        )
        
        # Optional custom constraints
        custom_constraints = st.text_area(
            "Custom Constraints (Optional)",
            placeholder="e.g., 'Focus on accessibility', 'Include hands-on labs'",
            height=60,
        )
        
        # PDF upload in sidebar
        st.markdown("#### 📄 Reference Material")
        uploaded_file = st.file_uploader(
            "Upload a PDF (optional)",
            type=["pdf"],
            help="Your course syllabus, notes, or reference materials"
        )
        
        pdf_path = None
        if uploaded_file:
            session_data = get_session_data()
            if session_data:
                try:
                    file_path, metadata = PDFProcessor.save_uploaded_pdf(
                        uploaded_file, session_data["temp_dir"]
                    )
                    pdf_path = file_path
                    st.success(f"✅ {metadata['filename']} uploaded")
                except Exception as e:
                    st.error(f"❌ Upload failed: {str(e)}")
        
        # Submit button
        submitted = st.form_submit_button("✨ Generate Outline", use_container_width=True)

    if submitted:
        # Validate required fields
        if not course_title or not course_description or not audience_level or not learning_mode:
            st.error("❌ Please fill all required fields marked with *")
            return None, None
        
        try:
            # Create schema
            user_input = UserInputSchema(
                course_title=course_title,
                course_description=course_description,
                audience_level=AudienceLevel(audience_level),
                audience_category=AudienceCategory(audience_category),
                learning_mode=LearningMode(learning_mode),
                depth_requirement=DepthRequirement(depth_requirement),
                duration_hours=int(duration_hours),
                custom_constraints=custom_constraints if custom_constraints else None,
                pdf_path=pdf_path,  # Set from inline upload
            )
            
            return user_input, pdf_path
        
        except Exception as e:
            st.error(f"❌ Validation error: {str(e)}")
            return None, None
    
    return None, None





@function_logger("Execute render output panel")
def render_output_panel(outline_dict: Dict[str, Any]):
    """
    Render generated course outline (STEP 1.7).
    
    Args:
        outline_dict: CourseOutlineSchema dict
    """
    st.subheader("📖 Generated Course Outline")
    
    # Course summary card
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Duration", f"{outline_dict.get('total_duration_hours', 0)} hours")
    
    with col2:
        modules_count = len(outline_dict.get("modules", []))
        st.metric("Modules", modules_count)
    
    with col3:
        outcomes = outline_dict.get("course_level_learning_outcomes", [])
        st.metric("Learning Outcomes", len(outcomes))
    
    # Course summary
    st.markdown("### 📋 Course Summary")
    st.write(outline_dict.get("course_summary", ""))
    
    # Audience info
    st.markdown("### 👥 Target Audience")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.caption("Level")
        st.write(outline_dict.get("audience_level", "").replace("_", " ").title())
    with col2:
        st.caption("Category")
        st.write(outline_dict.get("audience_category", "").replace("_", " ").title())
    with col3:
        st.caption("Mode")
        st.write(outline_dict.get("learning_mode", "").replace("_", " ").title())
    with col4:
        st.caption("Depth")
        st.write(outline_dict.get("depth_requirement", "").replace("_", " ").title())
    
    # Prerequisites
    if outline_dict.get("prerequisites"):
        st.markdown("### 📚 Prerequisites")
        for prereq in outline_dict["prerequisites"]:
            st.write(f"- {prereq}")
    
    # Course-level learning outcomes
    if outline_dict.get("course_level_learning_outcomes"):
        st.markdown("### 🎯 Course-Level Learning Outcomes")
        for lo in outline_dict["course_level_learning_outcomes"]:
            with st.container():
                st.write(f"**{lo['objective_id']}:** {lo['statement']}")
                st.caption(f"Bloom's Level: {lo['bloom_level'].title()}")
    
    # Modules (expandable)
    st.markdown("### 📚 Course Modules")
    
    modules = outline_dict.get("modules", [])
    for module in modules:
        with st.expander(f"**{module['title']}** ({module['estimated_hours']:.1f} hours)"):
            st.write(module.get("description", module.get("synopsis", "")))
            
            # Module learning objectives
            st.markdown("#### Learning Objectives")
            for lo in module.get("learning_objectives", []):
                st.write(f"- {lo['statement']} ({lo['bloom_level'].title()})")
            
            # Module lessons
            st.markdown("#### Lessons")
            for lesson in module.get("lessons", []):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📌 {lesson['title']}")
                with col2:
                    st.caption(f"{lesson['duration_minutes']} min")
            
            # Assessment
            if module.get("assessment"):
                st.markdown("#### Assessment")
                assessment = module["assessment"]
                st.write(f"**Type:** {assessment.get('type', 'N/A').title()}")
                st.write(f"**Weight:** {assessment.get('weight', 0):.1%}")
    
    # Capstone project
    capstone = outline_dict.get("capstone_project")
    if capstone:
        st.markdown("### 🏆 Capstone Project")
        st.write(f"**{capstone['title']}**")
        st.write(f"*Scope:* {capstone['scope']}")
        if capstone.get("deliverables"):
            st.markdown("**Deliverables:**")
            for deliverable in capstone["deliverables"]:
                st.write(f"- {deliverable}")
    
    # Recommended tools
    if outline_dict.get("recommended_tools"):
        st.markdown("### 🛠️ Recommended Tools & Technologies")
        tools = outline_dict["recommended_tools"]
        st.write(", ".join(tools) if tools else "None")
    
    # Instructor notes
    if outline_dict.get("instructor_notes"):
        st.markdown("### 📌 Instructor Notes")
        st.info(outline_dict["instructor_notes"])
    
    # ========== QUERY SECTION ==========
    st.markdown("---")
    st.markdown("### 💬 Query & Refine")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        query_input = st.text_input(
            "Ask a question about this course outline",
            placeholder="e.g., 'Why is module 2 included?' or 'Explain the assessment strategy'",
            key="query_input"
        )
    with col2:
        query_button = st.button("🔍 Query", use_container_width=True)
    
    if query_button and query_input:
        st.info("⏳ Processing query...")
        
        try:
            # Get user input from session
            session_data = get_session_data()
            user_input_dict = session_data.get("user_input", {}) if session_data else {}
            
            # Process query through Query Agent
            result = asyncio.run(process_query(query_input, outline_dict, user_input_dict))
            
            # Display result based on status
            if result["status"] == "success":
                st.success("✅ Query processed")
                st.markdown(f"**Intent:** {result.get('intent', 'General')}")
                st.markdown(f"**Response:**\n\n{result.get('response', 'No response')}")
                
                if result.get("action_type") and result["action_type"] != "none":
                    st.info(f"💡 {result.get('action_type', '').replace('_', ' ').title()} available")
            
            elif result["status"] == "clarification":
                st.warning("❓ Clarification needed")
                st.markdown(result.get("response", "Please provide more details"))
            
            else:
                st.error(f"❌ {result.get('response', 'Query failed')}")
        
        except Exception as e:
            st.error(f"❌ Query error: {str(e)}")
            if st.session_state.get("debug_mode", False):
                st.exception(e)
    
    # Query history (if available)
    with st.expander("📋 Query History"):
        session_data = get_session_data()
        if session_data and session_data.get("queries"):
            for i, q in enumerate(session_data.get("queries", [])[-5:], 1):
                st.caption(f"**Q{i}:** {q}")
        else:
            st.caption("No queries yet")
    
    # Dev/debug section
    if st.session_state.get("debug_mode", False):
        st.markdown("---")
        st.markdown("### 🔧 Debug Info")
        if st.checkbox("Show raw JSON"):
            st.json(outline_dict)
        
        st.caption("Schema validation: ✅ Valid")


@function_logger("Execute render sidebar controls")
def render_sidebar_controls():
    """Render sidebar controls (reset, debug) in persistent left column."""
    st.markdown("---")
    st.markdown("### ⚙️ Controls")
    
    # Reset button
    if st.button("🔄 Reset Session", use_container_width=True):
        sm = init_session_manager()
        session_id = st.session_state.get("session_id")
        if session_id:
            sm.cleanup_session(session_id)
        
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        st.success("✅ Session reset. Refresh to continue.")
        st.stop()
    
    # Debug toggle
    st.markdown("---")
    debug_mode = st.checkbox("Debug Mode", value=False)
    update_session_data("debug_mode", debug_mode)
    
    # Session info (debug)
    if debug_mode:
        st.markdown("### Session Info")
        session_data = get_session_data()
        if session_data:
            st.caption(f"Session ID: {session_data['session_id'][:8]}...")
            st.caption(f"Created: {session_data['created_at'].strftime('%H:%M:%S')}")
            if session_data.get("current_outline"):
                st.caption("✅ Outline generated")


# ============================================================================
# MAIN APP FLOW
# ============================================================================

@function_logger("Execute main")
def main():
    """Main Streamlit app (STEPS 1.1-1.8) with persistent left sidebar."""
    
    # Initialize
    render_header()
    init_session()
    
    # Create persistent two-column layout: 25% left sidebar, 75% right content
    col_left, col_right = st.columns([1, 3], gap="medium")
    
    # LEFT COLUMN: Input form and controls (persistent sidebar)
    with col_left:
        st.markdown("### 📝 Course Details")
        user_input, pdf_path = render_input_form()
        render_sidebar_controls()
    
    # RIGHT COLUMN: Main content area (scrollable)
    with col_right:
        if user_input:
            # Store PDF path in session if uploaded
            if pdf_path:
                update_session_data("uploaded_pdf_path", pdf_path)
            
            # Generate outline
            st.info("⏳ Generating course outline...")
            
            try:
                # Call orchestrator
                orchestrator = CourseOrchestratorAgent()
                
                # Run async agent
                outline = asyncio.run(orchestrator.run(user_input.model_dump()))
                
                # Store in session
                update_session_data("current_outline", outline)
                update_session_data("user_input", user_input.model_dump())
                update_session_data("run_id", outline.get("generated_by_agent", ""))
                
                # Render output
                st.success("✅ Course outline generated!")
                st.balloons()
                render_output_panel(outline)
            
            except Exception as e:
                st.error(f"❌ Generation failed: {str(e)}")
                
                if st.session_state.get("debug_mode", False):
                    st.exception(e)
        else:
            # Show existing outline from session
            session_data = get_session_data()
            if session_data and session_data.get("current_outline"):
                render_output_panel(session_data["current_outline"])
            else:
                st.markdown(
                    "<div style='text-align: center; padding: 80px 20px;'>"
                    "<h2>👈 Course Details</h2>"
                    "<p>Fill in the course details in the left sidebar to generate an outline</p>"
                    "</div>",
                    unsafe_allow_html=True
                )


if __name__ == "__main__":
    main()
