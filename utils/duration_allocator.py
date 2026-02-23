"""
Phase 5: Duration & Depth Allocator - Pre-LLM processing logic.

STEP 5.4: Before calling LLM, calculate realistic module structure.

This prevents LLM hallucinating unrealistic timelines and ensures
duration constraints are respected without validator intervention.
"""

from typing import Dict, Any
from utils.flow_logger import function_logger


class DurationAllocator:
    """
    STEP 5.4: Pre-process duration and depth allocation.
    
    Calculates:
    - Number of modules
    - Average hours per module
    - Depth distribution
    - Module sequencing hints
    """
    
    # Heuristics based on empirical course data
    HOURS_PER_MODULE_BASE = 6.0  # Average module duration
    MIN_MODULES = 3
    MAX_MODULES = 12
    
    DEPTH_MULTIPLIER = {
        "overview_level": 0.7,  # Fewer, broader modules
        "intermediate_level": 1.0,  # Standard depth
        "implementation_level": 1.3,  # More detailed, practical
        "research_level": 1.5,  # Deepest, most comprehensive
    }
    
    @function_logger("Allocate course duration across modules based on depth and mode")
    @function_logger("Execute allocate")
    def allocate(
        self,
        total_hours: float,
        depth_level: str = "intermediate_level",
        learning_mode: str = "theory"
    ) -> Dict[str, Any]:
        """
        Calculate realistic module structure.
        
        Args:
            total_hours: Total course duration (e.g., 40h)
            depth_level: Cognitive depth (overview/intermediate/implementation/research)
            learning_mode: Course format (theory/project_based/interview_prep/research)
            
        Returns:
            Dict with:
            - num_modules: Expected number of modules
            - avg_hours_per_module: Average duration per module
            - total_hours: Total duration (input)
            - depth_guidance: Blooms taxonomy focus
            - mode_adjustment: How learning_mode affects structure
        """
        
        # Get depth multiplier
        depth_mult = self.DEPTH_MULTIPLIER.get(depth_level, 1.0)
        
        # Calculate base module count
        base_per_module = self.HOURS_PER_MODULE_BASE / depth_mult
        num_modules = max(
            self.MIN_MODULES,
            min(self.MAX_MODULES, round(total_hours / base_per_module))
        )
        
        # Adjust based on learning mode
        mode_adjustment = self._get_mode_adjustment(learning_mode)
        if mode_adjustment.get("affects_module_count"):
            num_modules = max(self.MIN_MODULES, int(num_modules * mode_adjustment["module_count_multiplier"]))
        
        avg_hours_per_module = total_hours / num_modules
        
        return {
            "total_hours": total_hours,
            "num_modules": num_modules,
            "avg_hours_per_module": avg_hours_per_module,
            "depth_level": depth_level,
            "depth_multiplier": depth_mult,
            "learning_mode": learning_mode,
            "mode_adjustment": mode_adjustment,
            "depth_guidance": self._get_depth_guidance(depth_level),
            "note": f"Expected {num_modules} modules, ~{avg_hours_per_module:.1f}h each"
        }
    
    @function_logger("Execute  get mode adjustment")
    @function_logger("Execute  get mode adjustment")
    def _get_mode_adjustment(self, learning_mode: str) -> Dict[str, Any]:
        """Get learning mode specific adjustments."""
        adjustments = {
            "theory": {
                "affects_module_count": False,
                "module_count_multiplier": 1.0,
                "structure_note": "Conceptual flow, exams emphasized",
                "capstone_required": False
            },
            "project_based": {
                "affects_module_count": True,
                "module_count_multiplier": 1.1,  # More modules for milestones
                "structure_note": "Project milestone per 1-2 modules, capstone mandatory",
                "capstone_required": True
            },
            "interview_prep": {
                "affects_module_count": True,
                "module_count_multiplier": 1.3,  # More, bite-sized modules
                "structure_note": "Problem categories as modules, pattern emphasis",
                "capstone_required": False
            },
            "research": {
                "affects_module_count": False,
                "module_count_multiplier": 1.0,
                "structure_note": "Methodology → theory → application → paper",
                "capstone_required": True
            }
        }
        return adjustments.get(learning_mode, adjustments["theory"])
    
    @function_logger("Execute  get depth guidance")
    @function_logger("Execute  get depth guidance")
    def _get_depth_guidance(self, depth_level: str) -> Dict[str, Any]:
        """Get Bloom's taxonomy guidance based on depth."""
        guidance = {
            "overview_level": {
                "primary_blooms": ["remember", "understand"],
                "avoid_blooms": ["create", "evaluate"],
                "description": "High-level concepts, memorization & comprehension focused",
                "typical_assessments": ["quizzes", "discussion"]
            },
            "intermediate_level": {
                "primary_blooms": ["understand", "apply"],
                "avoid_blooms": [],
                "description": "Balanced theory and application",
                "typical_assessments": ["quizzes", "small projects", "discussions"]
            },
            "implementation_level": {
                "primary_blooms": ["apply", "analyze"],
                "avoid_blooms": ["remember"],  # Too shallow
                "description": "Hands-on skills, problem-solving, implementation focus",
                "typical_assessments": ["projects", "labs", "coding assignments"]
            },
            "research_level": {
                "primary_blooms": ["analyze", "evaluate", "create"],
                "avoid_blooms": [],
                "description": "Deep theory, original research, novel contributions",
                "typical_assessments": ["research papers", "thesis projects", "peer reviews"]
            }
        }
        return guidance.get(depth_level, guidance["intermediate_level"])
