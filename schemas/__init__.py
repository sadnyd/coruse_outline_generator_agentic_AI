"""
Schemas package - All data contracts.

This package contains all Pydantic schemas used throughout the system.
These serve as contracts between components and should be versioned carefully.
"""

from schemas.user_input import (
    UserInputSchema,
    AudienceLevel,
    AudienceCategory,
    LearningMode,
    DepthRequirement,
)

from schemas.course_outline import (
    CourseOutlineSchema,
    Module,
    Lesson,
    LearningObjective,
    BloomLevel,
    ValidatorFeedbackSchema,
)

from schemas.agent_outputs import (
    WebSearchResult,
    WebSearchAgentOutput,
    RetrievedChunk,
    RetrievalAgentOutput,
    QueryAgentResponse,
    OrchestratorContext,
)

__all__ = [
    # User Input
    "UserInputSchema",
    "AudienceLevel",
    "AudienceCategory",
    "LearningMode",
    "DepthRequirement",
    # Course Outline
    "CourseOutlineSchema",
    "Module",
    "Lesson",
    "LearningObjective",
    "BloomLevel",
    "ValidatorFeedbackSchema",
    # Agent Outputs
    "WebSearchResult",
    "WebSearchAgentOutput",
    "RetrievedChunk",
    "RetrievalAgentOutput",
    "QueryAgentResponse",
    "OrchestratorContext",
]
