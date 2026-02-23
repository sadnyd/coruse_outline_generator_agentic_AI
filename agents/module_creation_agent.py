"""
PHASE 5: Module Creation Agent - Core Intelligence Layer

Curriculum-grade course outline synthesis from multi-source context.

FEATURES (STEPS 5.1-5.7):
- STEP 5.1: CourseOutlineSchema lock (final curriculum contract)
- STEP 5.2: Agent responsibility boundary (pure synthesis, no tools)
- STEP 5.3: Multi-layer prompt architecture (system/developer/user/context/constraints)
- STEP 5.4: Duration & depth allocation (pre-LLM logic)
- STEP 5.5: Learning mode-driven structure (theory/project/interview/research)
- STEP 5.6: PDF integration (contextual guidance)
- STEP 5.7: Provenance & attribution tracking (source validation)

INPUT:
- ExecutionContext (user_input, retrieved_documents, web_search_results, pdf_text)

OUTPUT:
- CourseOutlineSchema (validated, production-ready, curriculum-grade)

INTEGRATION:
- Orchestrator Step 6: Calls ModuleCreationAgent.run(context)
- Non-blocking: Failures flagged but pipeline continues
"""

import logging
import json
import math
from typing import Optional, Dict, Any, List
from datetime import datetime

from schemas.user_input import UserInputSchema
from schemas.course_outline import (
    CourseOutlineSchema, Module, Lesson, LearningObjective, BloomLevel, Reference, SourceType
)
from schemas.execution_context import ExecutionContext
from services.llm_service import get_llm_service
from utils.duration_allocator import DurationAllocator
from utils.learning_mode_templates import LearningModeTemplates
from utils.prompt_loader import get_prompt_loader
from utils.flow_logger import function_logger, get_current_session_id

logger = logging.getLogger(__name__)

# Singleton instance
_module_creation_agent: Optional["ModuleCreationAgent"] = None


@function_logger("Get module creation agent")
@function_logger("Get module creation agent")
def get_module_creation_agent() -> "ModuleCreationAgent":
    """Get or create module creation agent singleton."""
    global _module_creation_agent
    if _module_creation_agent is None:
        _module_creation_agent = ModuleCreationAgent()
    return _module_creation_agent


@function_logger("Execute reset module creation agent")
@function_logger("Execute reset module creation agent")
def reset_module_creation_agent():
    """Reset module creation agent singleton."""
    global _module_creation_agent
    _module_creation_agent = None


class ModuleCreationAgent:
    """
    STEP 5.2: Core curriculum synthesis engine.
    
    RESPONSIBILITY BOUNDARY:
    - Input: ExecutionContext with multi-source context
    - Processing: Pure synthesis (no tool calls)
    - Output: CourseOutlineSchema (curriculum-grade)
    
    NOT RESPONSIBLE FOR:
    - Context building (Orchestrator Steps 1-5)
    - Validation/retry (Phase 6 Validator Agent)
    - Orchestration logic (Orchestrator)
    """
    
    @function_logger("Handle __init__")
    @function_logger("Handle __init__")
    def __init__(self):
        """Initialize with LLM service and utilities."""
        self.llm_service = get_llm_service()
        self.duration_allocator = DurationAllocator()
    
    @function_logger("Synthesize course outline using multi-layer prompts and LLM")
    async def run(self, context: ExecutionContext) -> CourseOutlineSchema:
        """
        STEP 5.8: Full 8-step pipeline execution.
        
        Args:
            context: ExecutionContext with user_input, retrieved_docs, web_results, pdf_text
            
        Returns:
            CourseOutlineSchema (validated, production-ready)
            
        Raises:
            ValueError: If context invalid or synthesis fails
        """
        
        # 1. Validate context
        self._validate_context(context)
        user_input = context.user_input
        
        logger.info(
            "Phase 5: Module Creation Agent - Starting synthesis pipeline",
            extra={"execution_id": context.execution_id, "course": user_input.course_title}
        )
        
        # 2. Pre-process duration & depth allocation (STEP 5.4)
        duration_plan = self.duration_allocator.allocate(
            total_hours=user_input.duration_hours,
            depth_level=user_input.depth_requirement,
            learning_mode=user_input.learning_mode
        )
        
        # 3. Get learning mode template (STEP 5.5)
        mode_template = LearningModeTemplates.get_template(user_input.learning_mode)
        
        # 4. Build multi-layer prompt (STEP 5.3)
        prompt = self._build_prompt(context, duration_plan, mode_template)
        
        # 5. Call LLM
        logger.debug(f"Calling LLM for outline synthesis (execution_id={context.execution_id})")
        llm_response = await self.llm_service.generate(prompt, temperature=0.7, max_tokens=8000)
        
        # 6. Parse response
        parsed_data = self._parse_llm_response(llm_response.content)
        
        # 7. Structure into CourseOutlineSchema
        outline = self._structure_outline(
            parsed_data, context, user_input, duration_plan, mode_template
        )
        
        # 8. Validate schema
        if not isinstance(outline, CourseOutlineSchema):
            raise ValueError(f"Expected CourseOutlineSchema, got {type(outline)}")
        
        logger.info(
            "Phase 5: Course outline synthesized successfully",
            extra={
                "execution_id": context.execution_id,
                "modules": len(outline.modules),
                "duration": outline.total_duration_hours,
                "confidencecore": outline.confidence_score,
            }
        )
        
        return outline
    
    @function_logger("Validate  context")
    @function_logger("Validate  context")
    def _validate_context(self, context: ExecutionContext):
        """
        STEP 5.2: Validate execution context.
        
        Required fields:
        - user_input (UserInputSchema)
        - execution_id
        
        Optional but helpful:
        - retrieved_documents (Phase 3)
        - web_search_results (Phase 4)
        - pdf_text (user uploads)
        """
        if not context:
            raise ValueError("ExecutionContext required")
        
        if not context.user_input:
            raise ValueError("user_input required in ExecutionContext")
        
        if not isinstance(context.user_input, UserInputSchema):
            raise ValueError(f"user_input must be UserInputSchema, got {type(context.user_input)}")
        
        logger.debug(f"Context validation passed (execution_id={context.execution_id})")
    
    @function_logger("Build  prompt")
    @function_logger("Build  prompt")
    def _build_prompt(
        self,
        context: ExecutionContext,
        duration_plan: Dict[str, Any],
        mode_template: Dict[str, Any]
    ) -> str:
        """
        STEP 5.3: Build compact multi-layer prompt using centralized prompt loader.
        
        Optimized for token efficiency while maintaining quality.
        Replaces inline prompts with files from prompts/ folder.
        """
        
        user_input = context.user_input
        prompt_loader = get_prompt_loader()
        
        # LAYER 1: System prompt (loaded from file)
        system_layer = prompt_loader.load_prompt('module_creation_system')
        
        # LAYER 2: Developer instructions (loaded from file)
        schema_instructions = prompt_loader.load_prompt('module_creation_schema')
        
        # LAYER 3: User input (loaded from file with variable substitution)
        user_section = prompt_loader.load_prompt(
            'module_creation_user_input',
            {
                'course_title': user_input.course_title,
                'course_description': user_input.course_description,
                'audience_level': user_input.audience_level,
                'audience_category': user_input.audience_category,
                'depth_requirement': user_input.depth_requirement,
                'duration_hours': user_input.duration_hours,
                'learning_mode': user_input.learning_mode
            }
        )
        
        # LAYER 4: Context (trimmed)
        context_section = self._summarize_context(context)
        
        # LAYER 5: Constraints (loaded from file with variable substitution)
        constraints_section = prompt_loader.load_prompt(
            'module_creation_constraints',
            {
                'num_modules': duration_plan['num_modules'],
                'avg_hours_per_module': duration_plan['avg_hours_per_module'],
                'total_hours': user_input.duration_hours,
                'primary_bloom_start': duration_plan['depth_guidance']['primary_blooms'][0],
                'mode_emphasis': ', '.join(mode_template['assessment_emphasis']['primary'])
            }
        )
        
        # Combine layers
        full_prompt = f"""{system_layer}

{schema_instructions}

{user_section}

{context_section}

{constraints_section}

Generate the course outline."""
        
        return full_prompt
    
    @function_logger("Execute  summarize context")
    @function_logger("Execute  summarize context")
    def _summarize_context(self, context: ExecutionContext) -> str:
        """STEP 5.4: Summarize multi-source context."""
        sections = []
        
        # Summarize retrieved documents (Phase 3)
        if context.retrieved_documents:
            sections.append(self._summarize_retrieved_docs(context.retrieved_documents))
        
        # Summarize web search results (Phase 4)
        if context.web_search_results:
            sections.append(self._summarize_web_results(context.web_search_results))
        
        # Summarize PDF (if provided)
        if context.uploaded_pdf_text:
            sections.append(self._summarize_pdf(context.uploaded_pdf_text))
        
        if not sections:
            return "CONTEXT: No external sources provided. Course outline based on user input and general knowledge."
        
        return "CONTEXT:\n" + "\n".join(sections)
    
    @function_logger("Execute  summarize retrieved docs")
    @function_logger("Execute  summarize retrieved docs")
    def _summarize_retrieved_docs(self, retrieved_documents: List[Dict]) -> str:
        """STEP 5.6: Concise summary of retrieved documents."""
        if not retrieved_documents:
            return ""
        
        docs_list = retrieved_documents.get('retrieved_chunks', []) if isinstance(retrieved_documents, dict) else retrieved_documents
        if not docs_list:
            return ""
        
        summary = f"Institutional Sources ({len(docs_list)} docs):"
        for doc in docs_list[:2]:  # Top 2 only
            title = doc.get('title', 'Source') if isinstance(doc, dict) else getattr(doc, 'title', 'Source')
            summary += f" {title};"
        
        return summary
    
    @function_logger("Execute  summarize web results")
    @function_logger("Execute  summarize web results")
    def _summarize_web_results(self, web_search_results: Dict) -> str:
        """STEP 5.6: Concise web search summary."""
        if not web_search_results:
            return ""
        
        results = web_search_results.get("results", [])
        if not results:
            return ""
        
        summary = f"Web Sources ({len(results)} results):"
        for result in results[:2]:  # Top 2 only
            title = result.get('title', 'Source')
            summary += f" {title};"
        
        return summary
    
    @function_logger("Execute  summarize pdf")
    @function_logger("Execute  summarize pdf")
    def _summarize_pdf(self, pdf_text: str) -> str:
        """STEP 5.6: Summarize user-provided PDF."""
        if not pdf_text:
            return ""
        
        # Summarize first 500 chars
        preview = pdf_text[:500].replace("\n", " ").strip()
        return f"PDF Guidance Material: {preview}...\n(Use this as supplementary guidance, not primary source)"
    
    @function_logger("Execute  parse llm response")
    @function_logger("Execute  parse llm response")
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM JSON response with fallback handling.
        
        Handles:
        - Clean JSON
        - JSON in markdown code blocks
        - JSON in text with extra content
        """
        
        response = response.strip()
        
        # Try 1: Direct JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Try 2: Extract from markdown code block
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            if end > start:
                try:
                    return json.loads(response[start:end].strip())
                except json.JSONDecodeError:
                    pass
        
        # Try 3: Extract from code block without language tag
        if "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end > start:
                try:
                    return json.loads(response[start:end].strip())
                except json.JSONDecodeError:
                    pass
        
        # Try 4: Find JSON object in text
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(response[start:end])
            except json.JSONDecodeError:
                pass
        
        raise ValueError(f"Unable to extract valid JSON from LLM response: {response[:200]}...")
    
    @function_logger("Execute  structure outline")
    @function_logger("Execute  structure outline")
    def _structure_outline(
        self,
        parsed_data: Dict[str, Any],
        context: ExecutionContext,
        user_input: UserInputSchema,
        duration_plan: Dict[str, Any],
        mode_template: Dict[str, Any]
    ) -> CourseOutlineSchema:
        """
        STEP 5.1: Assemble into CourseOutlineSchema with validation.
        
        Applies business rules:
        - Enforce duration constraints
        - Validate module structure
        - Add provenance (STEP 5.7)
        - Calculate confidence & completeness
        """
        
        # Create modules from parsed data
        modules = []
        for module_data in parsed_data.get("modules", []):
            module = self._create_module(module_data)
            modules.append(module)
        
        # Build references with complete provenance (STEP 5.7)
        references = self._build_references(parsed_data, context)
        
        # Create outline
        outline = CourseOutlineSchema(
            course_title=user_input.course_title,
            course_summary=parsed_data.get("course_summary", user_input.course_description),
            audience_level=user_input.audience_level,
            audience_category=user_input.audience_category,
            learning_mode=user_input.learning_mode,
            depth_requirement=user_input.depth_requirement,
            total_duration_hours=user_input.duration_hours,
            prerequisites=parsed_data.get("prerequisites", []),
            course_level_learning_objectives=  # STEP 5.7: Parse objectives from LLM
                [self._parse_objective(obj) for obj in parsed_data.get("course_level_objectives", [])],
            modules=modules,
            assessment_strategy=parsed_data.get("assessment_strategy", {}),
            references=references,
            confidence_score=self._calculate_confidence(context),
            completeness_score=self._calculate_completeness(modules, references),
            generated_by_agent="module_creation_agent",
            generation_timestamp=datetime.now().isoformat(),
        )
        
        return outline
    
    @function_logger("Execute  create module")
    @function_logger("Execute  create module")
    def _create_module(self, module_data: Dict[str, Any]) -> Module:
        """STEP 5.1: Build individual Module object."""
        
        lessons = []
        for lesson_data in module_data.get("lessons", []):
            lesson = Lesson(
                lesson_id=f"L_{module_data.get('module_id', 'unknown')}_{len(lessons) + 1}",
                title=lesson_data.get("title", "Untitled Lesson"),
                description=lesson_data.get("description", ""),
                duration_minutes=int(lesson_data.get("duration_minutes", 60)),
                key_concepts=lesson_data.get("key_concepts", []),
                activities=lesson_data.get("activities", []),
                resources=lesson_data.get("resources", [])
            )
            lessons.append(lesson)
        
        learning_objectives = []
        for obj_data in module_data.get("learning_objectives", []):
            obj = self._parse_objective(obj_data)
            learning_objectives.append(obj)
        
        module = Module(
            module_id=module_data.get("module_id", "M_unknown"),
            title=module_data.get("title", "Untitled Module"),
            description=module_data.get("description", ""),
            estimated_hours=float(module_data.get("estimated_hours", 6.0)),
            learning_objectives=learning_objectives,
            lessons=lessons,
            assessment_type=module_data.get("assessment_type", "quiz"),
            prerequisites=module_data.get("prerequisites", []),
            has_capstone=module_data.get("has_capstone", False),
            project_description=module_data.get("project_description", None),
            source_tags=module_data.get("source_tags", [])
        )
        
        return module
    
    @function_logger("Execute  parse objective")
    @function_logger("Execute  parse objective")
    def _parse_objective(self, obj_data: Dict[str, Any]) -> LearningObjective:
        """Parse single learning objective."""
        bloom_level = obj_data.get("bloom_level", "understand").lower()
        try:
            bloom = BloomLevel[bloom_level.upper()]
        except KeyError:
            bloom = BloomLevel.UNDERSTAND
        
        return LearningObjective(
            objective_id=obj_data.get("objective_id", "LO_unknown"),
            statement=obj_data.get("statement", ""),
            bloom_level=bloom,
            assessment_method=obj_data.get("assessment_method", "Quiz")
        )
    
    @function_logger("Build  references")
    @function_logger("Build  references")
    def _build_references(self, parsed_data: Dict[str, Any], context: ExecutionContext) -> List[Reference]:
        """
        STEP 5.7: Complete provenance tracking from all sources.
        
        Sources:
        1. LLM output references (from parsed_data)
        2. Web search results (context.web_search_results)
        3. Retrieved documents (context.retrieved_documents)
        4. PDF guidance (context.pdf_text - if provided)
        """
        
        references = []
        
        # 1. References cited by LLM
        for ref_data in parsed_data.get("references", []):
            ref = Reference(title=ref_data.get("title", "Reference"),
                source_type=SourceType.WEB if ref_data.get("source_type") == "web" else SourceType.GENERATED,
                url=ref_data.get("url"),
                confidence_score=float(ref_data.get("confidence_score", 0.8)),
                author=ref_data.get("author"),
                institution=ref_data.get("institution"),
                publication_year=ref_data.get("publication_year"),
                accessed_at=datetime.now().isoformat())
            references.append(ref)
        
        # 2. Web search results
        if context.web_search_results:
            for result in context.web_search_results.get("results", [])[:3]:
                ref = Reference(
                    title=result.get("title", "Web Result"),
                    source_type=SourceType.WEB,
                    url=result.get("url"),
                    confidence_score=0.85,
                    author=result.get("author"),
                    institution=result.get("institution"),
                    publication_year=result.get("publication_year"),
                    accessed_at=datetime.now().isoformat()
                )
                references.append(ref)
        
        # 3. Retrieved documents
        if context.retrieved_documents:
            # Handle both dict and list formats
            docs = context.retrieved_documents
            if isinstance(docs, dict):
                # If it's a dict with 'documents' key, use that
                docs = docs.get('documents', [])
                if not isinstance(docs, list):
                    docs = [docs] if docs else []
            
            for doc in docs[:3]:
                ref = Reference(
                    title=doc.get("title", "Retrieved Document") if isinstance(doc, dict) else str(doc),
                    source_type=SourceType.RETRIEVED,
                    url=doc.get("url") if isinstance(doc, dict) else None,
                    confidence_score=0.9,
                    author=doc.get("author") if isinstance(doc, dict) else None,
                    institution=doc.get("institution") if isinstance(doc, dict) else None,
                    publication_year=doc.get("publication_year") if isinstance(doc, dict) else None,
                    accessed_at=datetime.now().isoformat()
                )
                references.append(ref)
        
        # 4. PDF guidance
        if context.uploaded_pdf_text:
            ref = Reference(
                title="User-provided PDF guidance",
                source_type=SourceType.PDF,
                url=None,
                confidence_score=0.8,
                author=None,
                institution=None,
                publication_year=None,
                accessed_at=datetime.now().isoformat()
            )
            references.append(ref)
        
        return references
    
    @function_logger("Execute  calculate confidence")
    @function_logger("Execute  calculate confidence")
    def _calculate_confidence(self, context: ExecutionContext) -> float:
        """
        Calculate confidence score (0.0-1.0) based on context richness.
        
        Factors:
        - Retrieved docs: +0.15
        - Web search: +0.15
        - PDF: +0.10
        - Base: 0.6
        """
        
        score = 0.6  # Base confidence
        
        if context.retrieved_documents:
            score += 0.15
        
        if context.web_search_results:
            score += 0.15
        
        if context.uploaded_pdf_text:
            score += 0.10
        
        return min(1.0, score)
    
    @function_logger("Execute  calculate completeness")
    @function_logger("Execute  calculate completeness")
    def _calculate_completeness(self, modules: List[Module], references: List[Reference]) -> float:
        """
        Calculate completeness score (0.0-1.0).
        
        Factors:
        - Module count: +0.25 (3+ modules)
        - Learning objectives: +0.25 (each module has objectives)
        - References: +0.25 (references present)
        - Assessment: +0.25 (clear assessment strategy)
        """
        
        score = 0.0
        
        # Module count
        if len(modules) >= 3:
            score += 0.25
        else:
            score += (0.25 * len(modules) / 3)
        
        # Learning objectives
        modules_with_objectives = sum(1 for m in modules if m.learning_objectives)
        score += (0.25 * modules_with_objectives / max(1, len(modules)))
        
        # References
        if references and len(references) >= 3:
            score += 0.25
        elif references:
            score += (0.25 * len(references) / 3)
        
        # Assessment
        modules_with_assessment = sum(1 for m in modules if m.assessment_type)
        score += (0.25 * modules_with_assessment / max(1, len(modules)))
        
        return min(1.0, score)
