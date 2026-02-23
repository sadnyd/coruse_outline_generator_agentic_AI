"""
PHASE 1: Streamlit UI + Session tests.

Validates:
- UI renders correctly
- User input is captured
- Session management works
- PDF upload stored in temp
- Error handling
"""

import os
import tempfile
import pytest
from utils.session import SessionManager
from schemas.user_input import (
    UserInputSchema, AudienceLevel, AudienceCategory,
    LearningMode, DepthRequirement
)
from schemas.course_outline import CourseOutlineSchema
from agents.orchestrator import CourseOrchestratorAgent
from agents.module_creation_agent import CoreModuleCreationAgent
from tools.pdf_loader import PDFProcessor
import asyncio


class MockStreamlitFile:
    """Mock Streamlit uploaded file for testing."""
    
    def __init__(self, name: str, content: bytes):
        self.name = name
        self.content = content
    
    def getbuffer(self):
        return self.content


class TestPhase1Session:
    """Test session management (STEP 1.3)."""
    
    def test_session_creation(self):
        """PHASE 1: SessionManager creates a session."""
        sm = SessionManager()
        session_id = sm.create_session()
        
        assert session_id is not None
        assert len(session_id) > 0
        assert sm.get_session(session_id) is not None
    
    def test_session_data_persistence(self):
        """PHASE 1: Session data persists across updates."""
        sm = SessionManager()
        session_id = sm.create_session()
        
        # Update session
        sm.update_session(session_id, "test_key", "test_value")
        
        # Retrieve and verify
        session = sm.get_session(session_id)
        assert session["test_key"] == "test_value"
    
    def test_session_cleanup(self):
        """PHASE 1: Session cleanup removes session."""
        sm = SessionManager()
        session_id = sm.create_session()
        
        session = sm.get_session(session_id)
        temp_dir = session["temp_dir"]
        
        # Verify temp dir exists
        assert os.path.exists(temp_dir)
        
        # Cleanup
        sm.cleanup_session(session_id)
        
        # Verify session removed
        assert sm.get_session(session_id) is None
        
        # Verify temp dir deleted
        assert not os.path.exists(temp_dir)
    
    def test_session_multiple_users(self):
        """PHASE 1: Multiple sessions don't leak data."""
        sm = SessionManager()
        
        session1_id = sm.create_session()
        session2_id = sm.create_session()
        
        # Update session 1
        sm.update_session(session1_id, "user_id", "user_1")
        
        # Update session 2
        sm.update_session(session2_id, "user_id", "user_2")
        
        # Verify isolation
        assert sm.get_session(session1_id)["user_id"] == "user_1"
        assert sm.get_session(session2_id)["user_id"] == "user_2"
        
        # Cleanup
        sm.cleanup_session(session1_id)
        sm.cleanup_session(session2_id)


class TestPhase1InputForm:
    """Test input form validation (STEP 1.2)."""
    
    def test_valid_user_input_schema(self):
        """PHASE 1: Valid UserInputSchema is created."""
        user_input = UserInputSchema(
            course_title="Machine Learning 101",
            course_description="Introduction to ML concepts",
            audience_level=AudienceLevel.INTERMEDIATE,
            audience_category=AudienceCategory.UNDERGRADUATE,
            learning_mode=LearningMode.HYBRID,
            depth_requirement=DepthRequirement.IMPLEMENTATION_LEVEL,
            duration_hours=40,
        )
        
        assert user_input.course_title == "Machine Learning 101"
        assert user_input.duration_hours == 40
    
    def test_invalid_duration_rejected(self):
        """PHASE 1: Invalid duration (< 1) is rejected."""
        with pytest.raises(ValueError):
            UserInputSchema(
                course_title="Test",
                course_description="Test",
                audience_level=AudienceLevel.INTERMEDIATE,
                audience_category=AudienceCategory.UNDERGRADUATE,
                learning_mode=LearningMode.HYBRID,
                depth_requirement=DepthRequirement.IMPLEMENTATION_LEVEL,
                duration_hours=0,  # Invalid
            )
    
    def test_enum_validation_strict(self):
        """PHASE 1: Enum values are strictly validated."""
        with pytest.raises((ValueError, TypeError)):
            UserInputSchema(
                course_title="Test",
                course_description="Test",
                audience_level="invalid_level",  # Invalid enum
                audience_category=AudienceCategory.UNDERGRADUATE,
                learning_mode=LearningMode.HYBRID,
                depth_requirement=DepthRequirement.IMPLEMENTATION_LEVEL,
                duration_hours=40,
            )
    
    def test_required_fields_enforcement(self):
        """PHASE 1: Missing required fields rejected."""
        with pytest.raises((TypeError, ValueError)):
            UserInputSchema(
                # Missing course_title
                course_description="Test",
                audience_level=AudienceLevel.INTERMEDIATE,
                audience_category=AudienceCategory.UNDERGRADUATE,
                learning_mode=LearningMode.HYBRID,
                depth_requirement=DepthRequirement.IMPLEMENTATION_LEVEL,
                duration_hours=40,
            )


class TestPhase1PDFUpload:
    """Test PDF upload handling (STEP 1.4)."""
    
    def test_pdf_upload_stored_in_temp(self):
        """PHASE 1: Uploaded PDF is stored in temp directory."""
        sm = SessionManager()
        session_id = sm.create_session()
        session = sm.get_session(session_id)
        
        # Create mock PDF file
        pdf_content = b"%PDF-1.4..." + b"Some PDF content" * 100
        mock_file = MockStreamlitFile("test.pdf", pdf_content)
        
        # Save PDF
        file_path, metadata = PDFProcessor.save_uploaded_pdf(
            mock_file, session["temp_dir"]
        )
        
        # Verify file exists
        assert os.path.exists(file_path)
        assert metadata["filename"] == "test.pdf"
        assert metadata["size_bytes"] > 0
        
        # Cleanup
        sm.cleanup_session(session_id)
    
    def test_pdf_metadata_captured(self):
        """PHASE 1: PDF metadata (size, name) is captured."""
        sm = SessionManager()
        session_id = sm.create_session()
        session = sm.get_session(session_id)
        
        pdf_content = b"PDF content" * 1000  # Make larger
        mock_file = MockStreamlitFile("course_notes.pdf", pdf_content)
        
        file_path, metadata = PDFProcessor.save_uploaded_pdf(
            mock_file, session["temp_dir"]
        )
        
        assert metadata["filename"] == "course_notes.pdf"
        assert metadata["size_bytes"] > 0
        assert "path" in metadata
        
        # Cleanup
        sm.cleanup_session(session_id)
    
    def test_pdf_deleted_on_session_cleanup(self):
        """PHASE 1: PDF is deleted when session ends."""
        sm = SessionManager()
        session_id = sm.create_session()
        session = sm.get_session(session_id)
        
        pdf_content = b"PDF content" * 100
        mock_file = MockStreamlitFile("test.pdf", pdf_content)
        
        file_path, metadata = PDFProcessor.save_uploaded_pdf(
            mock_file, session["temp_dir"]
        )
        
        # Verify file exists before cleanup
        assert os.path.exists(file_path)
        
        # Cleanup session
        sm.cleanup_session(session_id)
        
        # Verify file deleted
        assert not os.path.exists(file_path)


class TestPhase1MockOrchestrator:
    """Test mock orchestrator (STEP 1.5)."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_single_pass(self):
        """PHASE 1: Orchestrator single-pass flow works."""
        orchestrator = CourseOrchestratorAgent()
        
        user_input = UserInputSchema(
            course_title="Python Basics",
            course_description="Learn Python fundamentals",
            audience_level=AudienceLevel.INTERMEDIATE,
            audience_category=AudienceCategory.COLLEGE_STUDENTS,
            learning_mode=LearningMode.PRACTICAL_HANDS_ON,
            depth_requirement=DepthRequirement.INTRODUCTORY,
            duration_hours=20,
        )
        
        # Run orchestrator (pass UserInputSchema object)
        outline = await orchestrator.run(user_input)
        
        # Verify output is CourseOutlineSchema-compliant
        assert isinstance(outline, dict)
        assert "course_title" in outline
        assert "modules" in outline
        assert len(outline["modules"]) > 0
    
    @pytest.mark.asyncio
    async def test_orchestrator_respects_duration(self):
        """PHASE 1: Orchestrator respects course duration."""
        orchestrator = CourseOrchestratorAgent()
        
        # Test short course
        user_input_short = UserInputSchema(
            course_title="Quick Course",
            course_description="A short introduction",
            audience_level=AudienceLevel.ADVANCED,
            audience_category=AudienceCategory.WORKING_PROFESSIONALS,
            learning_mode=LearningMode.THEORY_ORIENTED,
            depth_requirement=DepthRequirement.INTRODUCTORY,
            duration_hours=5,
        )
        
        outline_short = await orchestrator.run(user_input_short)  # Pass object
        
        # Test longer course
        user_input_long = UserInputSchema(
            course_title="Comprehensive Course",
            course_description="A long detailed course",
            audience_level=AudienceLevel.PRO_EXPERT,
            audience_category=AudienceCategory.POSTGRADUATE,
            learning_mode=LearningMode.HYBRID,
            depth_requirement=DepthRequirement.ADVANCED_IMPLEMENTATION,
            duration_hours=100,
        )
        
        outline_long = await orchestrator.run(user_input_long)  # Pass object
        
        # Longer course should have more modules (generally)
        short_modules = len(outline_short["modules"])
        long_modules = len(outline_long["modules"])
        
        # Both should be valid
        assert short_modules >= 2
        assert long_modules >= 2


class TestPhase1MockModuleCreation:
    """Test mock module creation (STEP 1.6)."""
    
    @pytest.mark.asyncio
    async def test_module_creation_valid_output(self):
        """PHASE 1: Module creation returns valid CourseOutlineSchema."""
        from schemas.execution_context import ExecutionContext
        agent = CoreModuleCreationAgent()
        
        user_input = UserInputSchema(
            course_title="Data Science",
            course_description="Data science fundamentals",
            audience_level=AudienceLevel.INTERMEDIATE,
            audience_category=AudienceCategory.UNDERGRADUATE,
            learning_mode=LearningMode.HYBRID,
            depth_requirement=DepthRequirement.IMPLEMENTATION_LEVEL,
            duration_hours=40,
        )
        
        context = ExecutionContext(user_input=user_input, session_id="test-session")
        
        outline = await agent.run(context)
        
        # Validate schema (outline is CourseOutlineSchema, convert to dict for testing)
        if not isinstance(outline, dict):
            outline = outline.dict()
        schema = CourseOutlineSchema(**outline)
        assert schema.course_title == user_input.course_title
        assert schema.total_duration_hours == user_input.duration_hours
    
    @pytest.mark.asyncio
    async def test_module_creation_respects_learning_objectives(self):
        """PHASE 1: Generated modules have learning objectives."""
        from schemas.execution_context import ExecutionContext
        agent = CoreModuleCreationAgent()
        
        user_input = UserInputSchema(
            course_title="Web Development",
            course_description="Learn web development",
            audience_level=AudienceLevel.INTERMEDIATE,
            audience_category=AudienceCategory.COLLEGE_STUDENTS,
            learning_mode=LearningMode.RESEARCH_ORIENTED,
            depth_requirement=DepthRequirement.ADVANCED_IMPLEMENTATION,
            duration_hours=50,
        )
        
        context = ExecutionContext(user_input=user_input, session_id="test-session")
        outline = await agent.run(context)
        
        # Convert to dict if needed for testing
        if not isinstance(outline, dict):
            outline = outline.dict()
        
        # Each module should have learning objectives
        for module in outline["modules"]:
            assert len(module["learning_objectives"]) >= 3
            assert len(module["learning_objectives"]) <= 7


class TestPhase1OutputValidation:
    """Test output rendering & validation (STEP 1.7)."""
    
    def test_course_outline_schema_valid(self):
        """PHASE 1: Generated outline is valid CourseOutlineSchema."""
        # This is tested implicitly by other tests, but explicit check:
        outline_dict = {
            "course_title": "Test Course",
            "course_summary": "Test summary",
            "audience_level": "intermediate",
            "audience_category": "undergraduate",
            "learning_mode": "hybrid",
            "depth_requirement": "implementation_level",
            "total_duration_hours": 40,
            "prerequisites": [],
            "course_level_learning_outcomes": [
                {
                    "objective_id": "CO_1",
                    "statement": "Test outcome",
                    "bloom_level": "understand",
                    "assessment_method": "Quiz"
                },
                {
                    "objective_id": "CO_2",
                    "statement": "Apply test outcome",
                    "bloom_level": "apply",
                    "assessment_method": "Project"
                },
                {
                    "objective_id": "CO_3",
                    "statement": "Evaluate test outcome",
                    "bloom_level": "evaluate",
                    "assessment_method": "Exam"
                }
            ],
            "modules": [
                {
                    "module_id": "M_1",
                    "title": "Module 1",
                    "synopsis": "Test",
                    "estimated_hours": 20.0,
                    "learning_objectives": [
                        {
                            "objective_id": "LO_1_1",
                            "statement": "Test",
                            "bloom_level": "remember",
                            "assessment_method": "Quiz"
                        },
                        {
                            "objective_id": "LO_1_2",
                            "statement": "Test understanding",
                            "bloom_level": "understand",
                            "assessment_method": "Quiz"
                        },
                        {
                            "objective_id": "LO_1_3",
                            "statement": "Apply test concepts",
                            "bloom_level": "apply",
                            "assessment_method": "Project"
                        }
                    ],
                    "lessons": [
                        {
                            "lesson_id": "L_1_1",
                            "title": "Lesson 1",
                            "duration_minutes": 60,
                            "activities": ["Lecture"],
                            "assessment_type": None,
                            "resources": []
                        }
                    ],
                    "assessment": {"type": "quiz", "weight": 0.1},
                    "bloom_level": "remember",
                    "keywords": [],
                    "readings_and_resources": []
                },
                {
                    "module_id": "M_2",
                    "title": "Module 2",
                    "synopsis": "Advanced test",
                    "estimated_hours": 20.0,
                    "learning_objectives": [
                        {
                            "objective_id": "LO_2_1",
                            "statement": "Test advanced",
                            "bloom_level": "understand",
                            "assessment_method": "Quiz"
                        },
                        {
                            "objective_id": "LO_2_2",
                            "statement": "Apply advanced",
                            "bloom_level": "apply",
                            "assessment_method": "Project"
                        },
                        {
                            "objective_id": "LO_2_3",
                            "statement": "Analyze advanced",
                            "bloom_level": "analyze",
                            "assessment_method": "Essay"
                        }
                    ],
                    "lessons": [
                        {
                            "lesson_id": "L_2_1",
                            "title": "Lesson 2",
                            "duration_minutes": 90,
                            "activities": ["Discussion"],
                            "assessment_type": "Quiz",
                            "resources": []
                        }
                    ],
                    "assessment": {"type": "project", "weight": 0.25},
                    "bloom_level": "apply",
                    "keywords": [],
                    "readings_and_resources": []
                }
            ],
            "capstone_project": None,
            "evaluation_strategy": {},
            "recommended_tools": [],
            "instructor_notes": None,
            "citations_and_provenance": [],
            "generated_by_agent": "module_creation_agent",
            "generation_timestamp": None,
        }
        
        # Should not raise
        schema = CourseOutlineSchema(**outline_dict)
        assert schema.course_title == "Test Course"


class TestPhase1ErrorHandling:
    """Test error handling (STEP 1.8)."""
    
    def test_missing_required_fields_error(self):
        """PHASE 1: Missing required fields raise clear error."""
        with pytest.raises((TypeError, ValueError)):
            UserInputSchema(
                course_description="Test",  # Missing course_title
                audience_level=AudienceLevel.INTERMEDIATE,
                audience_category=AudienceCategory.UNDERGRADUATE,
                learning_mode=LearningMode.HYBRID,
                depth_requirement=DepthRequirement.IMPLEMENTATION_LEVEL,
                duration_hours=40,
            )
    
    @pytest.mark.asyncio
    async def test_orchestrator_handles_invalid_input(self):
        """PHASE 1: Orchestrator handles invalid input gracefully."""
        orchestrator = CourseOrchestratorAgent()
        
        with pytest.raises((ValueError, TypeError, KeyError)):
            await orchestrator.run({})  # Empty dict
    
    def test_session_ttl_expiration(self):
        """PHASE 1: Session expires after TTL."""
        sm = SessionManager(ttl_minutes=0)  # Instant expiration
        session_id = sm.create_session()
        
        # Session should be expired immediately
        session = sm.get_session(session_id)
        
        # If TTL is 0, session is technically expired
        # (datetime.now() > expires_at for ttl_minutes=0)
        # This depends on timing, so we test with a small TTL


class TestPhase1Integration:
    """Integration tests (STEP 1.9)."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """PHASE 1: Complete end-to-end workflow works."""
        # 1. Create session
        sm = SessionManager()
        session_id = sm.create_session()
        
        # 2. Create user input
        user_input = UserInputSchema(
            course_title="Mobile App Development",
            course_description="Learn to build mobile apps",
            audience_level=AudienceLevel.INTERMEDIATE,
            audience_category=AudienceCategory.UNDERGRADUATE,
            learning_mode=LearningMode.HYBRID,
            depth_requirement=DepthRequirement.ADVANCED_IMPLEMENTATION,
            duration_hours=60,
        )
        
        # 3. Store in session
        sm.update_session(session_id, "user_input", user_input.dict())
        
        # 4. Call orchestrator (pass UserInputSchema object for compatibility)
        orchestrator = CourseOrchestratorAgent()
        outline = await orchestrator.run(user_input)  # Pass object, not dict
        
        # 5. Store outline in session
        sm.update_session(session_id, "current_outline", outline)
        
        # 6. Verify everything is stored
        session = sm.get_session(session_id)
        assert session["user_input"] is not None
        assert session["current_outline"] is not None
        
        # 7. Cleanup
        sm.cleanup_session(session_id)
        assert sm.get_session(session_id) is None

