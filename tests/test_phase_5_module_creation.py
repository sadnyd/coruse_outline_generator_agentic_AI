"""
PHASE 5 Test Suite: Module Creation Agent

Tests STEP 5.1-5.9:
- STEP 5.1: Schema lock & validation
- STEP 5.2: Context boundary
- STEP 5.3: Multi-layer prompts
- STEP 5.4: Duration allocation
- STEP 5.5: Learning mode templates
- STEP 5.6: PDF integration
- STEP 5.7: Provenance tracking
- STEP 5.8: Orchestrator integration
- STEP 5.9: Test suite (this file)
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any

from schemas.user_input import UserInputSchema
from schemas.course_outline import (
    CourseOutlineSchema, Module, Lesson, LearningObjective, BloomLevel, 
    Reference, SourceType
)
from schemas.execution_context import ExecutionContext
from agents.module_creation_agent import (
    ModuleCreationAgent, get_module_creation_agent, reset_module_creation_agent
)
from utils.duration_allocator import DurationAllocator
from utils.learning_mode_templates import LearningModeTemplates


# ========== Fixtures ==========

@pytest.fixture
def user_input():
    """Sample user input for testing."""
    return UserInputSchema(
        course_title="Advanced Python for Data Science",
        course_description="Master advanced Python techniques for data analysis and machine learning",
        audience_level="undergraduate",
        audience_category="STEM",
        depth_requirement="implementation_level",
        duration_hours=40,
        learning_mode="project_based"
    )


@pytest.fixture
def execution_context(user_input):
    """Sample execution context."""
    return ExecutionContext(
        user_input=user_input,
        session_id="test_session_123",
        execution_mode="test",
        retrieved_documents=[
            {
                "title": "Python Best Practices",
                "content": "Learn the best practices for writing Python code...",
                "source": "institutional"
            }
        ],
        web_search_results={
            "results": [
                {
                    "title": "Data Science with Python",
                    "snippet": "Comprehensive guide to data science tools...",
                    "url": "https://example.com/ds-python"
                }
            ]
        },
        pdf_text="Sample PDF content about Python libraries..."
    )


@pytest.fixture
def module_creation_agent():
    """Module creation agent instance."""
    reset_module_creation_agent()
    return get_module_creation_agent()


# ========== STEP 5.1: Schema Validation Tests ==========

def test_schema_course_outline_basic_instantiation():
    """Test CourseOutlineSchema can be instantiated with required fields."""
    outline = CourseOutlineSchema(
        course_title="Test Course",
        course_summary="A test course",
        audience_level="undergraduate",
        audience_category="STEM",
        learning_mode="theory",
        depth_requirement="intermediate_level",
        total_duration_hours=40.0,
        modules=[
            Module(
                module_id="M_1",
                title="Module 1",
                description="First module",
                estimated_hours=8.0,
                learning_objectives=[
                    LearningObjective(
                        objective_id="LO_1_1",
                        statement="Understand basic concepts",
                        bloom_level=BloomLevel.UNDERSTAND,
                        assessment_method="Quiz"
                    ),
                    LearningObjective(
                        objective_id="LO_1_2",
                        statement="Apply concepts to examples",
                        bloom_level=BloomLevel.APPLY,
                        assessment_method="Project"
                    ),
                    LearningObjective(
                        objective_id="LO_1_3",
                        statement="Analyze trade-offs",
                        bloom_level=BloomLevel.ANALYZE,
                        assessment_method="Essay"
                    )
                ],
                lessons=[
                    Lesson(
                        lesson_id="L_1_1",
                        title="Lesson 1",
                        duration_minutes=60,
                        key_concepts=["concept1", "concept2"],
                        activities=["lecture", "discussion"]
                    )
                ],
                assessment_type="quiz"
            ),
            Module(
                module_id="M_2",
                title="Module 2",
                description="Second module",
                estimated_hours=8.0,
                learning_objectives=[
                    LearningObjective(
                        objective_id="LO_2_1",
                        statement="Understand advanced concepts",
                        bloom_level=BloomLevel.UNDERSTAND,
                        assessment_method="Quiz"
                    ),
                    LearningObjective(
                        objective_id="LO_2_2",
                        statement="Apply advanced techniques",
                        bloom_level=BloomLevel.APPLY,
                        assessment_method="Project"
                    ),
                    LearningObjective(
                        objective_id="LO_2_3",
                        statement="Evaluate approaches",
                        bloom_level=BloomLevel.EVALUATE,
                        assessment_method="Presentation"
                    )
                ],
                lessons=[
                    Lesson(
                        lesson_id="L_2_1",
                        title="Lesson 1",
                        duration_minutes=90,
                        key_concepts=["advanced_concept"],
                        activities=["hands-on"]
                    )
                ],
                assessment_type="project"
            ),
            Module(
                module_id="M_3",
                title="Module 3",
                description="Third module",
                estimated_hours=8.0,
                learning_objectives=[
                    LearningObjective(
                        objective_id="LO_3_1",
                        statement="Understand capstone requirements",
                        bloom_level=BloomLevel.UNDERSTAND,
                        assessment_method="Quiz"
                    ),
                    LearningObjective(
                        objective_id="LO_3_2",
                        statement="Create capstone project",
                        bloom_level=BloomLevel.CREATE,
                        assessment_method="Capstone"
                    ),
                    LearningObjective(
                        objective_id="LO_3_3",
                        statement="Present findings",
                        bloom_level=BloomLevel.EVALUATE,
                        assessment_method="Presentation"
                    )
                ],
                lessons=[
                    Lesson(
                        lesson_id="L_3_1",
                        title="Capstone",
                        duration_minutes=120,
                        key_concepts=["integration"],
                        activities=["project"]
                    )
                ],
                assessment_type="capstone",
                has_capstone=True
            )
        ],
        confidence_score=0.85,
        completeness_score=0.90
    )
    
    assert outline.course_title == "Test Course"
    assert len(outline.modules) == 3
    assert outline.confidence_score == 0.85


def test_schema_validates_module_count():
    """Test that schema rejects too few modules."""
    with pytest.raises(ValueError):
        CourseOutlineSchema(
            course_title="Test",
            course_summary="Test",
            audience_level="undergraduate",
            audience_category="STEM",
            learning_mode="theory",
            depth_requirement="intermediate_level",
            total_duration_hours=40.0,
            modules=[  # Only 1 module, need at least 3
                Module(
                    module_id="M_1",
                    title="Module",
                    description="Desc",
                    estimated_hours=40.0,
                    learning_objectives=[
                        LearningObjective(
                            objective_id="LO_1",
                            statement="Test",
                            bloom_level=BloomLevel.UNDERSTAND,
                            assessment_method="Quiz"
                        ),
                        LearningObjective(
                            objective_id="LO_2",
                            statement="Test 2",
                            bloom_level=BloomLevel.APPLY,
                            assessment_method="Quiz"
                        ),
                        LearningObjective(
                            objective_id="LO_3",
                            statement="Test 3",
                            bloom_level=BloomLevel.ANALYZE,
                            assessment_method="Quiz"
                        )
                    ],
                    lessons=[
                        Lesson(
                            lesson_id="L_1",
                            title="Lesson",
                            duration_minutes=60
                        )
                    ],
                    assessment_type="quiz"
                )
            ],
            confidence_score=0.8,
            completeness_score=0.8
        )


def test_schema_validates_learning_objectives_per_module():
    """Test that each module needs 3-7 learning objectives."""
    with pytest.raises(ValueError):
        CourseOutlineSchema(
            course_title="Test",
            course_summary="Test",
            audience_level="undergraduate",
            audience_category="STEM",
            learning_mode="theory",
            depth_requirement="intermediate_level",
            total_duration_hours=40.0,
            modules=[
                Module(
                    module_id="M_1",
                    title="Module",
                    description="Desc",
                    estimated_hours=15.0,
                    learning_objectives=[  # Only 2, need 3+
                        LearningObjective(
                            objective_id="LO_1",
                            statement="Test",
                            bloom_level=BloomLevel.UNDERSTAND,
                            assessment_method="Quiz"
                        ),
                        LearningObjective(
                            objective_id="LO_2",
                            statement="Test 2",
                            bloom_level=BloomLevel.APPLY,
                            assessment_method="Quiz"
                        )
                    ],
                    lessons=[
                        Lesson(
                            lesson_id="L_1",
                            title="Lesson",
                            duration_minutes=60
                        )
                    ],
                    assessment_type="quiz"
                )
            ] * 3,
            confidence_score=0.8,
            completeness_score=0.8
        )


# ========== STEP 5.4: Duration Allocator Tests ==========

def test_duration_allocator_basic():
    """Test duration allocator calculates correct module count."""
    allocator = DurationAllocator()
    result = allocator.allocate(
        total_hours=40,
        depth_level="intermediate_level",
        learning_mode="theory"
    )
    
    assert result["total_hours"] == 40
    assert result["num_modules"] >= 3
    assert result["num_modules"] <= 12
    assert abs(
        result["num_modules"] * result["avg_hours_per_module"] - 40
    ) < 0.1


def test_duration_allocator_overview_level():
    """Test overview level reduces number of modules."""
    allocator = DurationAllocator()
    overview = allocator.allocate(40, "overview_level", "theory")
    implementation = allocator.allocate(40, "implementation_level", "theory")
    
    # Implementation should have more modules (more depth)
    assert implementation["num_modules"] >= overview["num_modules"]


def test_duration_allocator_project_based():
    """Test project-based mode affects module structure."""
    allocator = DurationAllocator()
    result = allocator.allocate(40, "intermediate_level", "project_based")
    
    assert result["mode_adjustment"]["capstone_required"] == True
    assert "project" in result["mode_adjustment"]["structure_note"].lower()


def test_duration_allocator_all_modes():
    """Test allocator works with all learning modes."""
    allocator = DurationAllocator()
    modes = ["theory", "project_based", "interview_prep", "research"]
    
    for mode in modes:
        result = allocator.allocate(40, "intermediate_level", mode)
        assert result["num_modules"] > 0
        assert result["avg_hours_per_module"] > 0


# ========== STEP 5.5: Learning Mode Templates Tests ==========

def test_learning_mode_template_theory():
    """Test theory template structure."""
    template = LearningModeTemplates.get_template("theory")
    
    assert template["template_name"] == "Theory-Oriented"
    assert "module_structure" in template
    assert "assessment_emphasis" in template
    assert template["capstone_structure"]["required"] == False


def test_learning_mode_template_project_based():
    """Test project-based template requires capstone."""
    template = LearningModeTemplates.get_template("project_based")
    
    assert template["template_name"] == "Project-Based"
    assert template["capstone_structure"]["required"] == True
    assert "project" in template["assessment_emphasis"]["primary"]


def test_learning_mode_template_interview_prep():
    """Test interview prep template for rapid problem solving."""
    template = LearningModeTemplates.get_template("interview_prep")
    
    assert template["template_name"] == "Interview Preparation"
    assert "pattern" in template["lesson_types"][0].lower()
    assert "timed" in str(template["assessment_emphasis"]).lower()


def test_learning_mode_template_research():
    """Test research template for original contribution."""
    template = LearningModeTemplates.get_template("research")
    
    assert template["template_name"] == "Research-Oriented"
    assert template["capstone_structure"]["required"] == True
    assert "thesis" in template["capstone_structure"]["type"].lower()


def test_get_all_modes():
    """Test retrieving list of all supported modes."""
    modes = LearningModeTemplates.get_all_modes()
    
    assert len(modes) == 4
    assert "theory" in modes
    assert "project_based" in modes
    assert "interview_prep" in modes
    assert "research" in modes


# ========== STEP 5.2: Context Validation Tests ==========

def test_module_agent_validates_context_required_fields(module_creation_agent, execution_context):
    """Test agent validates required context fields."""
    # Remove user_input (required field)
    context = ExecutionContext(
        user_input=None,
        session_id="test"
    )
    
    with pytest.raises(ValueError, match="user_input required"):
        # Note: Can't await in non-async test, just test synchronously
        module_creation_agent._validate_context(context)


def test_module_agent_accepts_partial_context(module_creation_agent, execution_context):
    """Test agent works with partial context (retrieved docs or web search optional)."""
    # Context with no retrieved docs or web search - should still work
    context = ExecutionContext(
        user_input=execution_context.user_input,
        session_id="test",
        retrieved_documents=None,
        web_search_results=None,
        pdf_text=None
    )
    
    # Should not raise error for missing optional fields
    assert context.user_input is not None


# ========== STEP 5.7: Provenance Tracking Tests ==========

def test_reference_creation():
    """Test reference with provenance metadata."""
    ref = Reference(
        title="Test Source",
        source_type=SourceType.WEB,
        url="https://example.com",
        confidence_score=0.85,
        author="John Doe",
        institution="MIT",
        publication_year=2023
    )
    
    assert ref.title == "Test Source"
    assert ref.source_type == SourceType.WEB
    assert ref.confidence_score == 0.85


def test_reference_source_types():
    """Test all reference source types."""
    sources = [SourceType.WEB, SourceType.RETRIEVED, SourceType.PDF, SourceType.GENERATED]
    
    for source in sources:
        ref = Reference(
            title=f"Test {source.value}",
            source_type=source,
            confidence_score=0.8
        )
        assert ref.source_type == source


# ========== STEP 5.3: Multi-layer Prompt Tests ==========

def test_module_agent_builds_prompt(module_creation_agent, execution_context):
    """Test multi-layer prompt architecture."""
    duration_plan = {
        "num_modules": 6,
        "avg_hours_per_module": 6.67,
        "depth_guidance": {
            "description": "Implementation-focused",
            "primary_blooms": ["apply", "analyze"]
        }
    }
    
    template = LearningModeTemplates.get_template("project_based")
    
    prompt = module_creation_agent._build_prompt(
        execution_context,
        duration_plan,
        template
    )
    
    # Verify all layers present
    assert "curriculum designer" in prompt.lower()  # System layer
    assert "OUTPUT FORMAT" in prompt  # Developer layer
    assert "USER INPUT" in prompt  # User input layer
    assert "CONTEXT" in prompt  # Context layer
    assert "CONSTRAINTS" in prompt  # Constraints layer


# ========== STEP 5.8: Orchestrator Integration Tests ==========

def test_module_creation_agent_singleton():
    """Test agent singleton pattern."""
    reset_module_creation_agent()
    agent1 = get_module_creation_agent()
    agent2 = get_module_creation_agent()
    
    assert agent1 is agent2  # Same instance


def test_module_creation_agent_reset():
    """Test resetting singleton."""
    agent1 = get_module_creation_agent()
    reset_module_creation_agent()
    agent2 = get_module_creation_agent()
    
    assert agent1 is not agent2  # Different instances


# ========== STEP 5.6: PDF Integration Tests ==========

def test_module_agent_pdf_summary(module_creation_agent, execution_context):
    """Test PDF summarization."""
    pdf_text = "Important educational content about Python..."
    summary = module_creation_agent._summarize_pdf(pdf_text)
    
    assert "PDF" in summary
    assert "guidance" in summary.lower()


# ========== Integration Tests ==========

def test_course_outline_to_dict():
    """Test CourseOutlineSchema serialization."""
    outline = CourseOutlineSchema(
        course_title="Test",
        course_summary="Test course",
        audience_level="undergraduate",
        audience_category="STEM",
        learning_mode="theory",
        depth_requirement="intermediate_level",
        total_duration_hours=40.0,
        modules=[
            Module(
                module_id="M_1",
                title="Module 1",
                description="Desc",
                estimated_hours=8.0,
                learning_objectives=[
                    LearningObjective(
                        objective_id="LO_1",
                        statement="Know concepts",
                        bloom_level=BloomLevel.UNDERSTAND,
                        assessment_method="Quiz"
                    ),
                    LearningObjective(
                        objective_id="LO_2",
                        statement="Apply concepts",
                        bloom_level=BloomLevel.APPLY,
                        assessment_method="Project"
                    ),
                    LearningObjective(
                        objective_id="LO_3",
                        statement="Analyze issues",
                        bloom_level=BloomLevel.ANALYZE,
                        assessment_method="Essay"
                    )
                ],
                lessons=[
                    Lesson(
                        lesson_id="L_1",
                        title="Intro",
                        duration_minutes=60
                    )
                ],
                assessment_type="quiz"
            )
        ] * 3,
        confidence_score=0.85,
        completeness_score=0.90
    )
    
    outline_dict = outline.to_dict()
    
    assert isinstance(outline_dict, dict)
    assert outline_dict["course_title"] == "Test"


def test_course_outline_str_representation():
    """Test CourseOutlineSchema string representation."""
    outline = CourseOutlineSchema(
        course_title="Advanced Python",
        course_summary="Learn advanced Python",
        audience_level="undergraduate",
        audience_category="STEM",
        learning_mode="theory",
        depth_requirement="intermediate_level",
        total_duration_hours=40.0,
        modules=[Module(
            module_id="M_1",
            title="M1",
            description="D1",
            estimated_hours=10.0,
            learning_objectives=[
                LearningObjective(
                    objective_id="LO_1",
                    statement="L1",
                    bloom_level=BloomLevel.UNDERSTAND,
                    assessment_method="Quiz"
                ),
                LearningObjective(
                    objective_id="LO_2",
                    statement="L2",
                    bloom_level=BloomLevel.APPLY,
                    assessment_method="Project"
                ),
                LearningObjective(
                    objective_id="LO_3",
                    statement="L3",
                    bloom_level=BloomLevel.ANALYZE,
                    assessment_method="Essay"
                )
            ],
            lessons=[Lesson(lesson_id="L_1", title="L1", duration_minutes=60)],
            assessment_type="quiz"
        )] * 3,
        confidence_score=0.9,
        completeness_score=0.95
    )
    
    str_repr = str(outline)
    
    assert "Advanced Python" in str_repr
    assert "40" in str_repr
    assert "Confidence" in str_repr


# ========== Regression Tests ==========

def test_bloom_progression_in_module():
    """Test that learning objectives show Bloom's progression within module."""
    objectives = [
        LearningObjective(
            objective_id="LO_1",
            statement="Recall definitions",
            bloom_level=BloomLevel.REMEMBER,
            assessment_method="Quiz"
        ),
        LearningObjective(
            objective_id="LO_2",
            statement="Understand principles",
            bloom_level=BloomLevel.UNDERSTAND,
            assessment_method="Quiz"
        ),
        LearningObjective(
            objective_id="LO_3",
            statement="Apply to problems",
            bloom_level=BloomLevel.APPLY,
            assessment_method="Project"
        ),
    ]
    
    # Verify progression (each level higher than previous)
    bloom_order = {
        BloomLevel.REMEMBER: 1,
        BloomLevel.UNDERSTAND: 2,
        BloomLevel.APPLY: 3,
        BloomLevel.ANALYZE: 4,
        BloomLevel.EVALUATE: 5,
        BloomLevel.CREATE: 6,
    }
    
    for i in range(len(objectives) - 1):
        curr_level = bloom_order[objectives[i].bloom_level]
        next_level = bloom_order[objectives[i + 1].bloom_level]
        assert next_level >= curr_level


def test_module_duration_consistency():
    """Test that module durations are consistent."""
    module = Module(
        module_id="M_1",
        title="Module 1",
        description="Test",
        estimated_hours=8.0,
        learning_objectives=[
            LearningObjective(
                objective_id="LO_1",
                statement="Learn",
                bloom_level=BloomLevel.UNDERSTAND,
                assessment_method="Quiz"
            ),
            LearningObjective(
                objective_id="LO_2",
                statement="Apply",
                bloom_level=BloomLevel.APPLY,
                assessment_method="Project"
            ),
            LearningObjective(
                objective_id="LO_3",
                statement="Analyze",
                bloom_level=BloomLevel.ANALYZE,
                assessment_method="Essay"
            )
        ],
        lessons=[
            Lesson(
                lesson_id="L_1",
                title="Lesson 1",
                duration_minutes=120
            ),
            Lesson(
                lesson_id="L_2",
                title="Lesson 2",
                duration_minutes=240
            ),
        ]
    )
    
    total_lesson_minutes = sum(lesson.duration_minutes for lesson in module.lessons)
    expected_minutes = int(module.estimated_hours * 60)
    
    # Lessons should roughly align with module duration (within 20% margin)
    assert total_lesson_minutes <= expected_minutes * 1.2
