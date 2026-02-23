from utils.flow_logger import function_logger
"""
PHASE 5: CourseOutlineSchema - Locked curriculum contract.

STEP 5.1: Schema design locked with comprehensive validation.

This is the production-ready output contract for curriculum-grade courses:
- Bloom's taxonomy levels across all objectives
- Complete provenance tracking (source attribution)
- Confidence & completeness scoring
- Multi-modal assessment strategies
- Learning mode-specific structure variations

Used by: Module Creation Agent (Step 5) → Validator Agent (Phase 6) → Exports, UI
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class BloomLevel(str, Enum):
    """Bloom's taxonomy cognitive levels (Remember → Create)."""
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"


class AssessmentType(str, Enum):
    """Assessment method types (STEP 5.1)."""
    QUIZ = "quiz"
    PROJECT = "project"
    DISCUSSION = "discussion"
    EXAM = "exam"
    PRESENTATION = "presentation"
    PEER_REVIEW = "peer_review"
    CAPSTONE = "capstone"
    MIXED = "mixed"


class SourceType(str, Enum):
    """STEP 5.7: Reference source types."""
    RETRIEVED = "retrieved"  # From Phase 3 ChromaDB
    WEB = "web"  # From Phase 4 web search
    PDF = "pdf"  # User-provided PDF
    GENERATED = "generated"  # LLM output


class Reference(BaseModel):
    """
    STEP 5.7: Complete provenance tracking.
    
    Enables source validation and citation.
    """
    
    title: str = Field(..., description="Reference title")
    source_type: SourceType = Field(..., description="Where this came from")
    url: Optional[str] = Field(None, description="Source URL")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in accuracy")
    author: Optional[str] = Field(None, description="Author name")
    institution: Optional[str] = Field(None, description="Educational institution")
    publication_year: Optional[int] = Field(None, description="Year published")
    accessed_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class LearningObjective(BaseModel):
    """
    Measurable learning outcome aligned to Bloom's taxonomy.
    
    Pattern: "VERB + condition + measurable_metric"
    Example: "Implement a decision tree classifier using scikit-learn"
    """
    
    objective_id: str = Field(..., description="e.g., 'LO_1_1', 'CO_2'")
    statement: str = Field(..., description="Measurable objective statement")
    bloom_level: BloomLevel = Field(..., description="Cognitive level")
    assessment_method: str = Field(..., description="How assessed (quiz, project, etc)")
    is_measurable: bool = Field(default=True, description="Can be objectively assessed")


class Lesson(BaseModel):
    """Single lesson within a module."""
    
    lesson_id: str = Field(..., description="e.g., 'L_1_1'")
    title: str = Field(..., description="Lesson title")
    description: Optional[str] = Field(None, description="Detailed lesson description")
    duration_minutes: int = Field(..., ge=15, description="Lesson duration")
    key_concepts: List[str] = Field(default_factory=list, description="Main concepts covered")
    activities: List[str] = Field(default_factory=list, description="Learning activities")
    resources: List[Dict[str, str]] = Field(
        default_factory=list,
        description="[{'title': '...', 'url': '...', 'type': 'video|reading|tool'}]"
    )


class Module(BaseModel):
    """
    Single course module - fundamental unit of instruction.
    
    STEP 5.1: Locked structure with comprehensive validation.
    """
    
    module_id: str = Field(..., description="e.g., 'M_1', 'M_2'")
    title: str = Field(..., description="Module title")
    description: str = Field(..., description="Detailed module overview")
    estimated_hours: float = Field(..., gt=0, description="Estimated duration in hours")
    learning_objectives: List[LearningObjective] = Field(
        ..., 
        min_items=3, 
        max_items=7, 
        description="3-7 measurable objectives per module"
    )
    lessons: List[Lesson] = Field(..., min_items=1, description="Ordered list of lessons")
    assessment_type: str = Field(..., description="Primary assessment method")
    prerequisites: List[str] = Field(default_factory=list, description="Required prior knowledge")
    has_capstone: bool = Field(default=False, description="Is this a capstone module?")
    project_description: Optional[str] = Field(None, description="Project details if project-based")
    source_tags: List[str] = Field(
        default_factory=list, 
        description="Source tags for traceability"
    )


class CourseOutlineSchema(BaseModel):
    """
    STEP 5.1: Complete course outline - locked curriculum contract.
    
    Production-ready output from Module Creation Agent (Phase 5).
    Input to Validator Agent (Phase 6).
    
    Guarantees:
    - All modules have 3-7 Bloom-aligned objectives
    - Duration respected (total_hours enforced)
    - Complete provenance (all sources tracked)
    - Confidence & completeness scored
    - Learning mode-specific structure variations
    """
    
    # ========== Course Metadata ==========
    course_title: str = Field(..., description="Official course title")
    course_summary: str = Field(
        ..., 
        description="150-500 word overview of course content and learning outcomes",
        min_length=50,
        max_length=2000
    )
    
    # ========== Audience Definition ==========
    audience_level: str = Field(
        ..., 
        description="high_school|undergraduate|postgraduate|professional"
    )
    audience_category: str = Field(..., description="e.g., 'STEM', 'Business', 'Creative'")
    
    # ========== Learning Configuration ==========
    learning_mode: str = Field(
        ..., 
        description="theory|project_based|interview_prep|research"
    )
    depth_requirement: str = Field(
        ..., 
        description="overview_level|intermediate_level|implementation_level|research_level"
    )
    total_duration_hours: float = Field(..., gt=0, description="Total course duration")
    
    # ========== Structure ==========
    prerequisites: List[str] = Field(
        default_factory=list, 
        description="Required knowledge"
    )
    course_level_learning_objectives: List[LearningObjective] = Field(
        default_factory=list, 
        description="Overall course goals"
    )
    modules: List[Module] = Field(
        ..., 
        min_items=3, 
        max_items=12, 
        description="3-12 modules per course"
    )
    
    # ========== Assessment & Strategy ==========
    assessment_strategy: Dict[str, Any] = Field(
        default_factory=dict, 
        description="{'formative': [...], 'summative': [...]}"
    )
    
    # ========== STEP 5.7: Provenance Tracking ==========
    references: List[Reference] = Field(
        default_factory=list, 
        description="Complete source attribution"
    )
    
    # ========== Quality Metrics ==========
    confidence_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Confidence in curriculum quality (0.0-1.0)"
    )
    completeness_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Completeness of course outline (0.0-1.0)"
    )
    
    # ========== Metadata ==========
    generated_by_agent: str = Field(default="module_creation_agent")
    generation_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # ========== Validation Rules ==========
    
    @validator("modules")
    @function_logger("Execute validate duration")
    def validate_duration(cls, modules, values):
        """Validate total module duration matches course duration."""
        if "total_duration_hours" in values:
            total = sum(m.estimated_hours for m in modules)
            expected = values["total_duration_hours"]
            # Allow 10% variance
            if not (expected * 0.9 <= total <= expected * 1.1):
                raise ValueError(f"Module duration sum ({total}h) must be ~{expected}h")
        return modules
    
    @validator("modules")
    @function_logger("Execute validate module objectives")
    def validate_module_objectives(cls, modules):
        """Validate each module has 3-7 learning objectives."""
        for module in modules:
            obj_count = len(module.learning_objectives)
            if obj_count < 3 or obj_count > 7:
                raise ValueError(f"Module {module.module_id}: expected 3-7 objectives, got {obj_count}")
        return modules
    
    @validator("course_level_learning_objectives")
    @function_logger("Execute validate course objectives")
    def validate_course_objectives(cls, objectives):
        """Validate course level objectives progression."""
        if objectives:
            # Should progress through Bloom levels
            bloom_levels = [obj.bloom_level for obj in objectives]
            if len(objectives) > 1:
                # At least some progression expected
                if bloom_levels[0] == bloom_levels[-1]:
                    raise ValueError("Course objectives should show cognitive progression")
        return objectives
    
    @function_logger("Execute to dict")
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return self.model_dump()
    
    @function_logger("Handle __str__")
    def __str__(self) -> str:
        """Human-readable representation."""
        return f"{self.course_title} ({self.total_duration_hours}h, {len(self.modules)} modules)" \
               f" - Confidence: {self.confidence_score:.2%}, Completeness: {self.completeness_score:.2%}"


class ValidatorFeedbackSchema(BaseModel):
    """PHASE 6: Validator Agent feedback on course outline."""
    
    score: float = Field(..., ge=0, le=100, description="Numeric score out of 100")
    
    rubric_breakdown: Dict[str, float] = Field(
        default_factory=dict, 
        description="{'coverage': 25, 'depth_alignment': 18, ...}"
    )
    
    accept: bool = Field(..., description="True if score >= threshold")
    
    feedback: List[str] = Field(
        default_factory=list, 
        description="Human-readable feedback for improvements"
    )
    
    targeted_edits: Optional[Dict[str, str]] = Field(
        None, 
        description="{'module_2_increase_examples': '...', 'add_assessment_for_lo_2_3': '...'}"
    )
    
    regenerate_modules: Optional[List[str]] = Field(
        None, 
        description="List of module IDs needing regeneration"
    )
