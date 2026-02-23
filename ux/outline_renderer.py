"""
8.2 Structured Outline Renderer - Human-readable rendering of CourseOutlineSchema.

Renders structured outlines for educators, not raw JSON.
- Clean hierarchical display
- Expandable/collapsible modules
- Bloom level visualization
- Duration transparency
- No JSON visible to users
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from enum import Enum

from utils.flow_logger import function_logger
from schemas.course_outline import CourseOutlineSchema, BloomLevel


class BloomLevelColor(Enum):
    """Visual indicators for Bloom levels."""
    REMEMBER = "🔵"
    UNDERSTAND = "🟢"
    APPLY = "🟡"
    ANALYZE = "🟠"
    EVALUATE = "🔴"
    CREATE = "🟣"


@function_logger("Initialize outline renderer")
class OutlineRenderer:
    """Renders CourseOutlineSchema in educator-friendly format."""
    
    @staticmethod
    @function_logger("Render bloom level badge")
    def _render_bloom_level(level: str) -> str:
        """Render Bloom level with visual indicator."""
        try:
            bloom = BloomLevel(level.lower())
            color_map = {
                BloomLevel.REMEMBER: "🔵",
                BloomLevel.UNDERSTAND: "🟢",
                BloomLevel.APPLY: "🟡",
                BloomLevel.ANALYZE: "🟠",
                BloomLevel.EVALUATE: "🔴",
                BloomLevel.CREATE: "🟣",
            }
            emoji = color_map.get(bloom, "⚪")
            return f"{emoji} {level.title()}"
        except:
            return f"⚪ {level}"
    
    @staticmethod
    @function_logger("Render learning objective")
    def render_objective(objective: Dict[str, Any], index: int = 0) -> None:
        """Render a single learning objective."""
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.write(f"**{index + 1}. {objective.get('statement', 'Unknown')}**")
            
            # Sub-details
            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                bloom_text = OutlineRenderer._render_bloom_level(
                    objective.get('bloom_level', 'remember')
                )
                st.caption(f"{bloom_text}")
            
            with sub_col2:
                assessment = objective.get('assessment_method', 'Not specified')
                st.caption(f"📋 {assessment}")
        
        with col2:
            is_measurable = objective.get('is_measurable', False)
            emoji = "✅" if is_measurable else "⚠️"
            st.caption(f"{emoji} Measurable")
    
    @staticmethod
    @function_logger("Render module content")
    def render_module(module: Dict[str, Any], module_num: int = 1) -> None:
        """Render a single module with all details."""
        
        # Module header
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.subheading(f"Module {module_num}: {module.get('title', 'Untitled')}")
        with col2:
            hours = module.get('estimated_hours', 0)
            st.metric(label="Duration", value=f"{hours}h")
        with col3:
            module_id = module.get('module_id', 'N/A')
            st.caption(f"ID: {module_id}")
        
        # Module description
        description = module.get('description', '')
        if description:
            st.write(f"**Overview:** {description}")
        
        # Learning Objectives
        st.write("### 🎯 Learning Objectives")
        objectives = module.get('learning_objectives', [])
        if objectives:
            for i, obj in enumerate(objectives):
                OutlineRenderer.render_objective(obj, i)
        else:
            st.info("No learning objectives defined")
        
        # Lessons
        lessons = module.get('lessons', [])
        if lessons:
            with st.expander("📚 Lessons", expanded=False):
                for i, lesson in enumerate(lessons, 1):
                    st.write(f"**Lesson {i}: {lesson.get('title', 'Untitled')}**")
                    if lesson.get('description'):
                        st.write(lesson.get('description'))
                    
                    # Resources if available
                    resources = lesson.get('resources', [])
                    if resources:
                        st.caption("Resources:")
                        for resource in resources:
                            st.write(f"  - {resource}")
        
        # Assessments
        assessments = module.get('assessments', [])
        if assessments:
            with st.expander("📊 Assessments", expanded=False):
                for i, assessment in enumerate(assessments, 1):
                    st.write(f"**Assessment {i}: {assessment.get('title', 'Untitled')}**")
                    st.write(f"Type: {assessment.get('type', 'Unknown')}")
                    if assessment.get('description'):
                        st.write(f"Description: {assessment.get('description')}")
                    if assessment.get('rubric'):
                        st.write(f"Rubric: {assessment.get('rubric')}")
    
    @staticmethod
    @function_logger("Render full course outline")
    def render_full_outline(outline: Dict[str, Any]) -> None:
        """Render complete course outline beautifully."""
        
        # Title and summary
        st.title(outline.get('course_title', 'Untitled Course'))
        st.write(outline.get('course_summary', ''))
        
        # Key metadata
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Level", outline.get('audience_level', 'N/A').title())
        with col2:
            st.metric("Category", outline.get('audience_category', 'N/A').title())
        with col3:
            st.metric("Mode", outline.get('learning_mode', 'N/A').title())
        with col4:
            # Calculate total duration
            modules = outline.get('modules', [])
            total_hours = sum(m.get('estimated_hours', 0) for m in modules)
            st.metric("Total Duration", f"{total_hours}h")
        
        st.divider()
        
        # Course-level learning outcomes
        course_objectives = outline.get('course_objectives', [])
        if course_objectives:
            st.heading("🎯 Course-Level Learning Outcomes")
            for i, obj in enumerate(course_objectives):
                OutlineRenderer.render_objective(obj, i)
            st.divider()
        
        # Modules
        st.heading("📖 Course Modules")
        modules = outline.get('modules', [])
        
        if modules:
            for i, module in enumerate(modules, 1):
                with st.expander(
                    f"**Module {i}: {module.get('title', 'Untitled')}** "
                    f"({module.get('estimated_hours', 0)}h)",
                    expanded=(i == 1)  # First module expanded by default
                ):
                    OutlineRenderer.render_module(module, i)
        else:
            st.info("No modules defined yet")
        
        st.divider()
        
        # Capstone if exists
        capstone = outline.get('capstone', {})
        if capstone:
            st.heading("🏆 Capstone Project")
            st.write(f"**Title:** {capstone.get('title', 'Untitled')}")
            st.write(capstone.get('description', ''))
            
            # Requirements
            requirements = capstone.get('requirements', [])
            if requirements:
                st.write("**Requirements:**")
                for req in requirements:
                    st.write(f"- {req}")
        
        # Evaluation strategy
        evaluation = outline.get('evaluation_strategy', '')
        if evaluation:
            st.divider()
            st.heading("📋 Evaluation Strategy")
            st.write(evaluation)
    
    @staticmethod
    @function_logger("Validate outline for rendering")
    def validate_outline(outline: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate outline has minimum required fields for rendering.
        
        Returns: (is_valid, error_message)
        """
        required_fields = ['course_title', 'modules']
        
        for field in required_fields:
            if field not in outline or not outline[field]:
                return False, f"Missing required field: {field}"
        
        if not isinstance(outline['modules'], list):
            return False, "Modules must be a list"
        
        if len(outline['modules']) == 0:
            return False, "At least one module required"
        
        # Validate each module
        for i, module in enumerate(outline['modules']):
            if 'title' not in module:
                return False, f"Module {i} missing title"
            if 'estimated_hours' not in module:
                return False, f"Module {i} missing estimated_hours"
        
        return True, ""
    
    @staticmethod
    @function_logger("Render outline with validation")
    def render(outline: Dict[str, Any]) -> bool:
        """
        Render outline with validation.
        
        Returns: True if rendered successfully, False otherwise
        """
        is_valid, error_msg = OutlineRenderer.validate_outline(outline)
        
        if not is_valid:
            st.error(f"❌ Cannot render outline: {error_msg}")
            return False
        
        try:
            OutlineRenderer.render_full_outline(outline)
            return True
        except Exception as e:
            st.error(f"❌ Error rendering outline: {str(e)}")
            return False
    
    @staticmethod
    @function_logger("Render module preview")
    def render_preview(outline: Dict[str, Any], max_modules: int = 3) -> None:
        """Render a preview of the outline (first N modules)."""
        st.write(f"### {outline.get('course_title', 'Course')}")
        st.write(f"*{outline.get('course_summary', '')[:200]}...*")
        
        modules = outline.get('modules', [])
        
        for i, module in enumerate(modules[:max_modules]):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{i + 1}. {module.get('title', 'Untitled')}**")
                objectives = module.get('learning_objectives', [])
                if objectives:
                    st.caption(f"{len(objectives)} learning objectives")
            with col2:
                st.caption(f"{module.get('estimated_hours', 0)}h")
        
        remaining = len(modules) - max_modules
        if remaining > 0:
            st.caption(f"... and {remaining} more modules")


# Streamlit helper
@function_logger("Display outline in streamlit")
def st_display_outline(outline: Dict[str, Any]) -> bool:
    """Helper function for Streamlit integration."""
    renderer = OutlineRenderer()
    return renderer.render(outline)
