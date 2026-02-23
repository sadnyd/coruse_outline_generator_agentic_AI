"""
Phase 5: Learning Mode Templates - Structural variations.

STEP 5.5: Different learning modes require different course structures.

Theory-oriented: Conceptual progression, exams
Project-based: Milestone-driven, capstone integration
Interview-prep: Problem categories, patterns, speed
Research: Methodology → theory → application → original contribution
"""

from typing import Dict, Any, List
from utils.flow_logger import function_logger


class LearningModeTemplates:
    """
    STEP 5.5: Provide structural templates based on learning mode.
    
    Each mode implies different:
    - Module sequencing
    - Lesson types
    - Assessment methods
    - Capstone structure
    """
    
    @staticmethod
    @function_logger("Get structural template for learning mode")
    @function_logger("Get template")
    def get_template(learning_mode: str) -> Dict[str, Any]:
        """
        Get template for specific learning mode.
        
        Args:
            learning_mode: One of theory, project_based, interview_prep, research
            
        Returns:
            Dict with:
            - template_name
            - structural_variations
            - module_structure
            - lesson_types
            - assessment_emphasis
            - capstone_structure
            - sequencing_notes
        """
        
        templates = {
            "theory": LearningModeTemplates._theory_template(),
            "project_based": LearningModeTemplates._project_based_template(),
            "interview_prep": LearningModeTemplates._interview_prep_template(),
            "research": LearningModeTemplates._research_template(),
        }
        
        return templates.get(learning_mode, templates["theory"])
    
    @staticmethod
    @function_logger("Execute  theory template")
    @function_logger("Execute  theory template")
    def _theory_template() -> Dict[str, Any]:
        """Conceptual knowledge with exams."""
        return {
            "template_name": "Theory-Oriented",
            "template_description": "Build conceptual understanding through theory, examples, and assessments",
            "structural_variations": {
                "module_sequencing": "Prerequisite-based (foundational → advanced)",
                "progression_model": "Linear, building on prior knowledge",
            },
            "module_structure": {
                "typical_module_flow": [
                    "1. Core concept introduction",
                    "2. Theoretical framework",
                    "3. Real-world examples",
                    "4. Practice problems",
                    "5. Summary & key takeaways"
                ],
                "ideal_module_duration": "5-7 hours",
                "lessons_per_module": 4,
            },
            "lesson_types": [
                "Lecture (recorded or text)",
                "Conceptual deep-dive",
                "Example walkthrough",
                "Practice problems",
                "Discussion forum"
            ],
            "assessment_emphasis": {
                "primary": ["quiz", "exam"],
                "secondary": ["discussion", "essay"],
                "capstone_type": "Comprehensive exam or final project"
            },
            "capstone_structure": {
                "required": False,
                "type": "Final exam or comprehensive project",
                "description": "Synthesizes course concepts into integrated understanding"
            },
            "sequencing_notes": "Start with definitions and core theory, progress to applications",
            "learning_objectives_guidance": "Emphasize 'understand' and 'apply' Bloom's levels"
        }
    
    @staticmethod
    @function_logger("Execute  project based template")
    @function_logger("Execute  project based template")
    def _project_based_template() -> Dict[str, Any]:
        """Hands-on skills through real projects."""
        return {
            "template_name": "Project-Based",
            "template_description": "Build practical skills through incremental projects leading to capstone",
            "structural_variations": {
                "module_sequencing": "Milestone-driven (each module outputs a deliverable)",
                "progression_model": "Non-linear, concurrent skills building",
            },
            "module_structure": {
                "typical_module_flow": [
                    "1. Project context & requirements",
                    "2. Skill building (mini-lessons)",
                    "3. Guided implementation",
                    "4. Project milestone",
                    "5. Peer review / feedback"
                ],
                "ideal_module_duration": "6-8 hours (includes coding/building)",
                "lessons_per_module": 3,
            },
            "lesson_types": [
                "Tool tutorial",
                "Implementation guide",
                "API reference",
                "Code walkthrough",
                "Debugging tips"
            ],
            "assessment_emphasis": {
                "primary": ["project", "code_review"],
                "secondary": ["peer_review", "presentation"],
                "capstone_type": "Full-scale project with documentation"
            },
            "capstone_structure": {
                "required": True,
                "type": "Capstone project integrating all modules",
                "description": "Build complete production-grade artifact or solution"
            },
            "sequencing_notes": "Earlier projects set up infrastructure; later projects add sophistication",
            "learning_objectives_guidance": "Heavy emphasis on 'apply' and 'analyze' Bloom's levels"
        }
    
    @staticmethod
    @function_logger("Execute  interview prep template")
    @function_logger("Execute  interview prep template")
    def _interview_prep_template() -> Dict[str, Any]:
        """Rapid problem-solving and pattern recognition."""
        return {
            "template_name": "Interview Preparation",
            "template_description": "Master problem categories and patterns for rapid problem-solving",
            "structural_variations": {
                "module_sequencing": "Problem category grouped (arrays, graphs, DP, etc.)",
                "progression_model": "Depth-based (easy → hard within each category)",
            },
            "module_structure": {
                "typical_module_flow": [
                    "1. Problem category overview",
                    "2. Pattern identification",
                    "3. Classic problems (3-5)",
                    "4. Variations & edge cases",
                    "5. Speed challenges"
                ],
                "ideal_module_duration": "4-5 hours (active problem solving)",
                "lessons_per_module": 2,
            },
            "lesson_types": [
                "Pattern guide",
                "Problem walkthrough",
                "Solution analysis",
                "Complexity breakdown",
                "Practice problems"
            ],
            "assessment_emphasis": {
                "primary": ["coding_problem", "timed_challenge"],
                "secondary": ["peer_solutions", "discussion"],
                "capstone_type": "Timed mock interview or problem set"
            },
            "capstone_structure": {
                "required": False,
                "type": "Mock interview or comprehensive problem set",
                "description": "Simulate interview environment under time pressure"
            },
            "sequencing_notes": "Category depth increases; time pressure increases; cross-pattern problems toward end",
            "learning_objectives_guidance": "Emphasize rapid pattern recognition and 'apply' Bloom's level"
        }
    
    @staticmethod
    @function_logger("Execute  research template")
    @function_logger("Execute  research template")
    def _research_template() -> Dict[str, Any]:
        """Methodology, theory, application, and original contribution."""
        return {
            "template_name": "Research-Oriented",
            "template_description": "Deep dive into research methodology, literature, and original contribution",
            "structural_variations": {
                "module_sequencing": "Chronological research journey (methodology → literature → application → contribution)",
                "progression_model": "Narrative-driven, building cumulative expertise",
            },
            "module_structure": {
                "typical_module_flow": [
                    "1. Research methodology / framework",
                    "2. Literature review for topic",
                    "3. Theoretical deep-dive",
                    "4. Application / experiment design",
                    "5. Analysis & implications"
                ],
                "ideal_module_duration": "8-10 hours (reading, analysis, writing)",
                "lessons_per_module": 3,
            },
            "lesson_types": [
                "Paper/article summary",
                "Methodology tutorial",
                "Hands-on experiment",
                "Data analysis guide",
                "Critique & discussion"
            ],
            "assessment_emphasis": {
                "primary": ["paper", "research_project"],
                "secondary": ["peer_review", "presentation", "seminar"],
                "capstone_type": "Research thesis or novel contribution"
            },
            "capstone_structure": {
                "required": True,
                "type": "Original research paper, thesis, or novel contribution",
                "description": "Make original contribution to field, publishable standard"
            },
            "sequencing_notes": "Narrow scope → expand literature review → deepen theory → conduct original research",
            "learning_objectives_guidance": "Emphasize 'analyze', 'evaluate', and 'create' Bloom's levels"
        }
    
    @staticmethod
    @function_logger("Get all modes")
    @function_logger("Get all modes")
    def get_all_modes() -> List[str]:
        """Get list of supported learning modes."""
        return ["theory", "project_based", "interview_prep", "research"]
