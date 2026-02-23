"""
8.4 Partial Regeneration - Surgical regeneration of specific parts.

Supports:
- Single module regeneration
- Objectives-only regeneration
- Depth adjustment for one module
- Learning mode switching per module

Behind the scenes: Orchestrator operates in targeted mode.
"""

from typing import Dict, Any, Optional, List
from enum import Enum

from utils.flow_logger import function_logger


class RegenerationMode(Enum):
    """Types of partial regeneration."""
    FULL = "full"  # Entire curriculum
    MODULE = "module"  # Single module
    OBJECTIVES = "objectives"  # Only learning objectives
    LESSONS = "lessons"  # Only lessons
    ASSESSMENTS = "assessments"  # Only assessments
    DEPTH_ADJUST = "depth_adjust"  # Change depth for module


@function_logger("Initialize partial regeneration service")
class PartialRegenerationService:
    """Manage surgical regeneration of outline parts."""
    
    @staticmethod
    @function_logger("Prepare module for single regeneration")
    def prepare_module_regen_input(
        original_user_input: Dict[str, Any],
        current_outline: Dict[str, Any],
        edited_outline: Dict[str, Any],
        module_id: str,
        depth_adjustment: Optional[str] = None,
        learning_mode_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Prepare input for single-module regeneration.
        
        Returns modified input that tells orchestrator:
        - Focus on this specific module
        - Preserve edits in other modules
        - Apply any adjustments
        """
        regen_input = {
            'mode': RegenerationMode.MODULE.value,
            'target_module_id': module_id,
            
            # Original context
            'original_user_input': original_user_input,
            
            # Current state
            'current_outline': current_outline,
            'edited_outline': edited_outline,
            
            # Adjustments
            'depth_adjustment': depth_adjustment,  # "increase", "decrease", or None
            'learning_mode_override': learning_mode_override,  # "project_based", "theory", etc.
            
            # Preservation rules
            'preserve_edits': True,
            'preserve_other_modules': True,
        }
        
        return regen_input
    
    @staticmethod
    @function_logger("Prepare objectives regeneration")
    def prepare_objectives_regen_input(
        original_user_input: Dict[str, Any],
        current_outline: Dict[str, Any],
        edited_outline: Dict[str, Any],
        module_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Regenerate learning objectives only.
        
        If module_id is None, regenerate objectives for ALL modules.
        """
        regen_input = {
            'mode': RegenerationMode.OBJECTIVES.value,
            'target_module_id': module_id,  # None = all modules
            
            'original_user_input': original_user_input,
            'current_outline': current_outline,
            'edited_outline': edited_outline,
            
            'preserve_edits': True,
            'preserve_structure': True,  # Keep module titles, lessons, etc.
        }
        
        return regen_input
    
    @staticmethod
    @function_logger("Prepare assessments regeneration")
    def prepare_assessments_regen_input(
        original_user_input: Dict[str, Any],
        current_outline: Dict[str, Any],
        module_id: str
    ) -> Dict[str, Any]:
        """Regenerate assessments for a specific module."""
        return {
            'mode': RegenerationMode.ASSESSMENTS.value,
            'target_module_id': module_id,
            
            'original_user_input': original_user_input,
            'current_outline': current_outline,
            
            'preserve_edits': True,
            'preserve_structure': True,
        }
    
    @staticmethod
    @function_logger("Prepare depth adjustment")
    def prepare_depth_adjustment(
        original_user_input: Dict[str, Any],
        current_outline: Dict[str, Any],
        module_id: str,
        new_depth: str  # "foundational", "intermediate", "advanced"
    ) -> Dict[str, Any]:
        """
        Adjust depth for single module.
        
        This changes detail level without restructuring.
        """
        return {
            'mode': RegenerationMode.DEPTH_ADJUST.value,
            'target_module_id': module_id,
            
            'original_user_input': original_user_input,
            'current_outline': current_outline,
            
            'depth_adjustment': new_depth,
            'preserve_edits': True,
            'preserve_other_structure': True,
        }
    
    @staticmethod
    @function_logger("Extract module for regeneration")
    def extract_module_for_regen(
        outline: Dict[str, Any],
        module_id: str
    ) -> Optional[Dict[str, Any]]:
        """Extract a single module from outline for focused processing."""
        modules = outline.get('modules', [])
        
        for module in modules:
            if module.get('module_id') == module_id:
                return module
        
        return None
    
    @staticmethod
    @function_logger("Merge regenerated module back")
    def merge_regenerated_module(
        original_outline: Dict[str, Any],
        module_id: str,
        regenerated_module: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge single regenerated module back into outline.
        
        Preserves all other modules and structure.
        """
        result = original_outline.copy()
        modules = result.get('modules', [])
        
        # Find and replace module
        for i, module in enumerate(modules):
            if module.get('module_id') == module_id:
                modules[i] = regenerated_module
                break
        
        return result
    
    @staticmethod
    @function_logger("Merge objectives for modules")
    def merge_objectives(
        original_outline: Dict[str, Any],
        objectives_map: Dict[str, List[Dict[str, Any]]]  # {module_id: [objectives]}
    ) -> Dict[str, Any]:
        """Merge regenerated objectives back into outline."""
        result = original_outline.copy()
        modules = result.get('modules', [])
        
        for module in modules:
            module_id = module.get('module_id')
            if module_id in objectives_map:
                module['learning_objectives'] = objectives_map[module_id]
        
        return result
    
    @staticmethod
    @function_logger("Detect what needs regeneration")
    def analyze_changes_for_regen(
        original_outline: Dict[str, Any],
        edited_outline: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze what changed and recommend regeneration strategy.
        
        Returns:
        {
            'has_module_changes': bool,
            'affected_modules': List[str],
            'suggested_mode': RegenerationMode,
            'recommendations': List[str]
        }
        """
        result = {
            'has_module_changes': False,
            'affected_modules': [],
            'suggested_mode': RegenerationMode.FULL,
            'recommendations': []
        }
        
        # Compare modules
        original_modules = {m.get('module_id'): m for m in original_outline.get('modules', [])}
        edited_modules = {m.get('module_id'): m for m in edited_outline.get('modules', [])}
        
        # Check each module for changes
        for module_id, edited_module in edited_modules.items():
            if module_id in original_modules:
                original_module = original_modules[module_id]
                
                # Check what changed in this module
                if edited_module.get('title') != original_module.get('title'):
                    result['affected_modules'].append(module_id)
                    result['recommendations'].append(f"Module title changed: {module_id}")
                
                if edited_module.get('learning_objectives') != original_module.get('learning_objectives'):
                    result['affected_modules'].append(module_id)
                    result['recommendations'].append(f"Objectives changed: {module_id}")
        
        # If only one module affected, suggest module regen
        if len(result['affected_modules']) == 1:
            result['suggested_mode'] = RegenerationMode.MODULE
            result['has_module_changes'] = True
        elif len(result['affected_modules']) > 0:
            result['suggested_mode'] = RegenerationMode.OBJECTIVES
            result['has_module_changes'] = True
            result['recommendations'].append("Multiple modules affected. Consider full regeneration.")
        
        return result
    
    @staticmethod
    @function_logger("Calculate regeneration impact")
    def calculate_impact(
        original_outline: Dict[str, Any],
        regenerated_outline: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Estimate impact of regeneration.
        
        What's changing?
        How many modules affected?
        Any data loss risk?
        """
        impact = {
            'total_modules': len(regenerated_outline.get('modules', [])),
            'modules_with_changes': 0,
            'new_modules': 0,
            'removed_modules': 0,
            'total_hours_change': 0.0,
            'objectives_change': 0,
        }
        
        original_modules = {m.get('module_id'): m for m in original_outline.get('modules', [])}
        regenerated_modules = {m.get('module_id'): m for m in regenerated_outline.get('modules', [])}
        
        # Analyze differences
        for module_id, regen_module in regenerated_modules.items():
            if module_id not in original_modules:
                impact['new_modules'] += 1
            else:
                orig_module = original_modules[module_id]
                if regen_module != orig_module:
                    impact['modules_with_changes'] += 1
                
                # Track hour changes
                orig_hours = orig_module.get('estimated_hours', 0)
                regen_hours = regen_module.get('estimated_hours', 0)
                impact['total_hours_change'] += (regen_hours - orig_hours)
                
                # Track objective changes
                orig_obj_count = len(orig_module.get('learning_objectives', []))
                regen_obj_count = len(regen_module.get('learning_objectives', []))
                impact['objectives_change'] += (regen_obj_count - orig_obj_count)
        
        # Check for removed modules
        for module_id in original_modules:
            if module_id not in regenerated_modules:
                impact['removed_modules'] += 1
        
        return impact
    
    @staticmethod
    @function_logger("Generate human readable regeneration summary")
    def generate_summary(
        mode: RegenerationMode,
        module_id: Optional[str] = None,
        impact: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate user-friendly summary of what will regenerate."""
        if mode == RegenerationMode.FULL:
            return "🔄 **Full Regeneration**: Entire curriculum will be recreated"
        
        elif mode == RegenerationMode.MODULE:
            return f"📦 **Module Regeneration**: Module will be fully regenerated, others preserved"
        
        elif mode == RegenerationMode.OBJECTIVES:
            return f"🎯 **Objectives Update**: Learning outcomes will be refreshed, structure maintained"
        
        elif mode == RegenerationMode.ASSESSMENTS:
            return f"📊 **Assessments Update**: Assessments will be regenerated"
        
        elif mode == RegenerationMode.DEPTH_ADJUST:
            return f"📈 **Depth Adjustment**: Content detail level will be adjusted"
        
        return "🔄 Regenerating..."
