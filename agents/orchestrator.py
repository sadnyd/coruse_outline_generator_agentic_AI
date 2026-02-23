"""
PHASE 2: Orchestrator Agent

Traffic controller for single-pass course outline generation.

Responsibility:
- Accept validated UserInputSchema
- Build execution context
- Call ModuleCreationAgent (the ONLY intelligence provider in Phase 2)
- Validate output
- Log execution

Explicitly NOT responsible for:
- Calling LLM directly (delegated to agents)
- Deciding content logic (delegated to ModuleCreationAgent)
- Validation/scoring (Phase 6)
- Web search (Phase 4)
- PDF retrieval (Phase 3)
- Retry logic (Phase 6)

⚠️ Phase 2 Constraint: Orchestrator calls exactly ONE agent.
"""

import logging
from typing import Optional, Union
from uuid import uuid4

from schemas.user_input import UserInputSchema
from utils.flow_logger import function_logger, set_session_id, end_session, get_flow_logger
from schemas.course_outline import CourseOutlineSchema
from schemas.execution_context import ExecutionContext
from agents.module_creation_agent import ModuleCreationAgent, get_module_creation_agent
from agents.retrieval_agent import RetrievalAgent
from agents.web_search_agent import WebSearchAgent
from agents.query_agent import InteractiveQueryAgent, QuerySessionContext

logger = logging.getLogger(__name__)


class CourseOrchestratorAgent:
    """
    Single-pass orchestrator for Phase 2.
    
    Routes: UserInputSchema → ModuleCreationAgent → CourseOutlineSchema
    
    This agent is deliberately simple. Complexity is delegated to:
    - ModuleCreationAgent: Intelligence (prompt, LLM, schema validation)
    - LLMService: Provider abstraction
    - ExecutionContext: Data structuring
    """
    
    @function_logger("Handle __init__")
    @function_logger("Handle __init__")
    def __init__(self):
        """Initialize orchestrator with agents for all phases."""
        self.module_agent = get_module_creation_agent()  # Phase 5 singleton
        self.retrieval_agent = RetrievalAgent()
        self.web_search_agent = WebSearchAgent()
        self.query_agent = InteractiveQueryAgent()  # Phase 7 query support
        self.logger = logger
    
    @function_logger("Execute orchestrator: coordinate all agents for course outline generation")
    async def run(
        self,
        user_input: Union[UserInputSchema, dict],
        session_id: Optional[str] = None,
    ) -> dict:
        """
        Execute single-pass course generation.
        
        Phase 2: Straight-through pipeline
        - No validation agent
        - No web search
        - No PDF retrieval
        - No retry logic
        
        Args:
            user_input: UserInputSchema or dict with educator requirements
            session_id: Session identifier for logging/persistence
            
        Returns:
            CourseOutlineSchema as dict with generated course outline
            
        Raises:
            ValueError: If input invalid or output doesn't match schema
            TimeoutError: If LLM times out
            RuntimeError: If LLM service fails
        """
        
        # Step 1: Normalize input
        user_input = self._validate_and_normalize_input(user_input)
        
        # Step 2: Build execution context
        context = ExecutionContext(
            user_input=user_input,
            session_id=session_id or str(uuid4()),
            execution_mode="single_pass",
        )
        
        # Step 3: Log execution start
        self.logger.info(
            "Starting course generation",
            extra={
                "execution_id": context.execution_id,
                "session_id": context.session_id,
                "course_title": user_input.course_title,
                "duration_hours": user_input.duration_hours,
            }
        )
        
        # Step 4: Call RetrievalAgent (Phase 3 - gets institutional knowledge)
        try:
            retrieval_output = await self.retrieval_agent.run(context)
            context.retrieved_documents = retrieval_output.to_dict()
            
            self.logger.info(
                f"Retrieval complete: {retrieval_output.returned_count} chunks retrieved",
                extra={
                    "execution_id": context.execution_id,
                    "retrieval_confidence": retrieval_output.retrieval_confidence,
                }
            )
        except Exception as e:
            self.logger.warning(
                f"Retrieval failed (non-blocking): {str(e)}",
                extra={"execution_id": context.execution_id},
            )
            # Phase 3 is non-blocking: if retrieval fails, continue to generation
            context.retrieved_documents = None
        
        # Step 5: Call WebSearchAgent (Phase 4 - gets public knowledge)
        try:
            web_search_output = await self.web_search_agent.run(context)
            context.web_search_results = web_search_output.to_dict()
            
            self.logger.info(
                f"Web search complete: {web_search_output.result_count} external results, "
                f"confidence={web_search_output.confidence_score:.2f}",
                extra={
                    "execution_id": context.execution_id,
                    "web_search_tool": web_search_output.tool_used.value,
                    "web_search_confidence": web_search_output.confidence_score,
                }
            )
        except Exception as e:
            self.logger.warning(
                f"Web search failed (non-blocking): {str(e)}",
                extra={"execution_id": context.execution_id},
            )
            # Phase 4 is non-blocking: if web search fails, continue to generation
            context.web_search_results = None
        
        # Step 6: Call ModuleCreationAgent (now uses both institutional + public knowledge)
        try:
            outline = await self.module_agent.run(context)
        except Exception as e:
            self.logger.error(
                f"Module agent failed: {str(e)}",
                extra={"execution_id": context.execution_id},
                exc_info=True,
            )
            raise
        
        # Step 7: Validate output
        if not isinstance(outline, CourseOutlineSchema):
            raise ValueError(f"Expected CourseOutlineSchema, got {type(outline)}")
        
        # Step 8: Log completion
        self.logger.info(
            "Course generation complete",
            extra={
                "execution_id": context.execution_id,
                "modules": len(outline.modules),
                "duration_hours": outline.total_duration_hours,
            }
        )
        
        # Convert to dict for downstream consumers
        return outline.model_dump()
    
    @function_logger("Validate  and normalize input")
    @function_logger("Validate  and normalize input")
    def _validate_and_normalize_input(
        self,
        user_input: Union[UserInputSchema, dict]
    ) -> UserInputSchema:
        """
        Convert input to UserInputSchema if needed.
        
        Args:
            user_input: UserInputSchema or dict
            
        Returns:
            UserInputSchema
            
        Raises:
            ValueError: If input invalid
        """
        if isinstance(user_input, UserInputSchema):
            return user_input
        elif isinstance(user_input, dict):
            try:
                # Pydantic V2 will automatically convert string enum values to enum instances
                return UserInputSchema.model_validate(user_input)
            except Exception as e:
                raise ValueError(f"Invalid UserInputSchema: {str(e)}")
        else:
            raise ValueError(
                f"Expected UserInputSchema or dict, got {type(user_input)}"
            )
    
    @function_logger("Execute query on course outline")
    async def query(
        self,
        query_text: str,
        user_input: Union[UserInputSchema, dict],
        outline: Union[CourseOutlineSchema, dict]
    ) -> dict:
        """
        Process educator query on generated course outline.
        
        Phase 7: Interactive querying for explanations, refinements, exports.
        
        Args:
            query_text: Educator question/request
            user_input: Original UserInputSchema or dict
            outline: Generated CourseOutlineSchema or dict
            
        Returns:
            Query response dict with status, intent, response, etc.
            
        Raises:
            ValueError: If inputs invalid
        """
        # Normalize inputs
        user_input = self._validate_and_normalize_input(user_input)
        
        if isinstance(outline, dict):
            outline = CourseOutlineSchema.model_validate(outline)
        
        # Create query session context
        context = QuerySessionContext(
            user_input=user_input,
            final_outline=outline,
            retrieved_docs=[],
            web_results=[],
            validator_feedback={}
        )
        
        # Process query through query agent
        return await self.query_agent.process_query(query_text, context)
