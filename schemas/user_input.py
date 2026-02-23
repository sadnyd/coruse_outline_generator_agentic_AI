from utils.flow_logger import function_logger
"""
PHASE 0: Contract for user input.

Validates frontend form submissions.
This is the first contract any agent receives.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum


class AudienceLevel(str, Enum):
    """🎯 Skill level of learners."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    PRO_EXPERT = "pro_expert"
    MIXED_LEVEL = "mixed_level"


class AudienceCategory(str, Enum):
    """👥 Who the course is designed for."""
    SCHOOL_STUDENTS = "school_students"
    COLLEGE_STUDENTS = "college_students"
    UNDERGRADUATE = "undergraduate"
    POSTGRADUATE = "postgraduate"
    RESEARCHERS = "researchers"
    PROFESSORS_FACULTY = "professors_faculty"
    WORKING_PROFESSIONALS = "working_professionals"
    INDUSTRY_EXPERTS = "industry_experts"


class LearningMode(str, Enum):
    """📚 How the content should be structured."""
    THEORY_ORIENTED = "theory_oriented"
    PRACTICAL_HANDS_ON = "practical_hands_on"
    PROJECT_BASED = "project_based"
    CASE_STUDY_DRIVEN = "case_study_driven"
    RESEARCH_ORIENTED = "research_oriented"
    EXAM_ORIENTED = "exam_oriented"
    INTERVIEW_PREPARATION = "interview_preparation"
    HYBRID = "hybrid"


class DepthRequirement(str, Enum):
    """🔬 How deep the explanations should go."""
    INTRODUCTORY = "introductory"
    CONCEPTUAL = "conceptual"
    IMPLEMENTATION_LEVEL = "implementation_level"
    ADVANCED_IMPLEMENTATION = "advanced_implementation"
    INDUSTRY_LEVEL = "industry_level"
    RESEARCH_LEVEL = "research_level"
    PHD_LEVEL = "phd_level"


class UserInputSchema(BaseModel):
    """
    Educator input from Streamlit UI (PHASE 1).
    
    This is the entry point for the orchestrator.
    All fields are required except pdf_path (optional upload).
    """
    
    course_title: str = Field(
        ..., 
        description="e.g., 'Introduction to Machine Learning'"
    )
    
    course_description: str = Field(
        ..., 
        description="Free-text description of course goals and scope"
    )
    
    audience_level: AudienceLevel = Field(
        ..., 
        description="Target educational level"
    )
    
    audience_category: AudienceCategory = Field(
        ..., 
        description="Learner background / role"
    )
    
    learning_mode: LearningMode = Field(
        ..., 
        description="Delivery method"
    )
    
    depth_requirement: DepthRequirement = Field(
        ..., 
        description="Depth / theory vs practice balance"
    )
    
    duration_hours: int = Field(
        ..., 
        ge=1, 
        le=500, 
        description="Total course duration in hours"
    )
    
    pdf_path: Optional[str] = Field(
        None, 
        description="Path to uploaded session PDF (temp storage, PHASE 1)"
    )
    
    custom_constraints: Optional[str] = Field(
        None, 
        description="Free-text additional requirements/constraints"
    )
    
    model_config = ConfigDict(use_enum_values=True)  # Serialize enums as strings
