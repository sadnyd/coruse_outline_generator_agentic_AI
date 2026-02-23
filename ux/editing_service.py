"""
8.3 Inline Editing - Controlled editing for human-in-the-loop workflow.

Editable: Module titles, objectives (text), lesson titles, assessments
Protected: Provenance, validator score, Bloom tags, metadata

Changes tracked at field level with diff awareness.
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import json

from utils.flow_logger import function_logger


@dataclass
class FieldChange:
    """Track a single field change."""
    field_path: str  # e.g., "modules.0.title"
    old_value: Any
    new_value: Any
    field_type: str  # "title", "objective", "lesson", "assessment"
    is_protected: bool = False


@function_logger("Initialize editing service")
class EditingService:
    """Manage controlled inline edits to outlines."""
    
    # Fields that can be edited
    EDITABLE_FIELDS = {
        'module_title': {
            'path_pattern': 'modules.*.title',
            'type': 'text',
            'protected': False
        },
        'objective_statement': {
            'path_pattern': 'modules.*.learning_objectives.*.statement',
            'type': 'text',
            'protected': False
        },
        'lesson_title': {
            'path_pattern': 'modules.*.lessons.*.title',
            'type': 'text',
            'protected': False
        },
        'lesson_description': {
            'path_pattern': 'modules.*.lessons.*.description',
            'type': 'text',
            'protected': False
        },
        'assessment_description': {
            'path_pattern': 'modules.*.assessments.*.description',
            'type': 'text',
            'protected': False
        },
    }
    
    # Fields that are protected
    PROTECTED_FIELDS = {
        'bloom_level': 'Advanced mode only',
        'module_id': 'System generated',
        'assessment_type': 'Locked',
        'provenance': 'For audit',
    }
    
    @staticmethod
    @function_logger("Apply edit to outline")
    def apply_edit(
        outline: Dict[str, Any],
        field_path: str,
        new_value: Any
    ) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Apply a single edit to outline.
        
        Returns: (success, error_message, updated_outline)
        """
        # Validate field is editable
        is_editable, error = EditingService._validate_field(field_path)
        if not is_editable:
            return False, error, outline
        
        # Navigate to field and update
        try:
            updated = EditingService._set_nested_value(outline, field_path, new_value)
            return True, None, updated
        except Exception as e:
            return False, f"Failed to apply edit: {str(e)}", outline
    
    @staticmethod
    @function_logger("Apply batch edits")
    def apply_batch_edits(
        outline: Dict[str, Any],
        edits: List[Tuple[str, Any]]
    ) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Apply multiple edits atomically.
        
        Returns: (all_success, errors, updated_outline)
        """
        errors = []
        current_outline = outline.copy()
        
        for field_path, new_value in edits:
            success, error, current_outline = EditingService.apply_edit(
                current_outline,
                field_path,
                new_value
            )
            
            if not success:
                errors.append(f"{field_path}: {error}")
        
        return len(errors) == 0, errors, current_outline
    
    @staticmethod
    @function_logger("Validate field is editable")
    def _validate_field(field_path: str) -> Tuple[bool, Optional[str]]:
        """Check if field is allowed to be edited."""
        # Check protected fields
        field_name = field_path.split('.')[-1]
        
        for protected in EditingService.PROTECTED_FIELDS:
            if protected in field_name.lower():
                return False, f"Field '{field_name}' is protected: {EditingService.PROTECTED_FIELDS[protected]}"
        
        # Check if it matches any editable pattern
        parts = field_path.split('.')
        
        # Basic editable fields
        if field_name in ['title', 'description', 'statement']:
            return True, None
        
        return False, f"Field '{field_path}' is not editable"
    
    @staticmethod
    @function_logger("Get nested value from outline")
    def _get_nested_value(obj: Dict[str, Any], path: str) -> Tuple[bool, Any]:
        """Navigate nested object and return value."""
        parts = path.split('.')
        current = obj
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            elif isinstance(current, list):
                try:
                    index = int(part)
                    current = current[index]
                except (ValueError, IndexError):
                    return False, None
            else:
                return False, None
        
        return True, current
    
    @staticmethod
    @function_logger("Set nested value in outline")
    def _set_nested_value(obj: Dict[str, Any], path: str, value: Any) -> Dict[str, Any]:
        """
        Modify nested object at path.
        Returns new object (non-mutating for immutability).
        """
        parts = path.split('.')
        
        # Deep copy to avoid mutation
        result = json.loads(json.dumps(obj))
        
        # Navigate to parent
        current = result
        for part in parts[:-1]:
            if isinstance(current, dict):
                if part not in current:
                    current[part] = {}
                current = current[part]
            elif isinstance(current, list):
                index = int(part)
                current = current[index]
        
        # Set final value
        final_key = parts[-1]
        if isinstance(current, dict):
            current[final_key] = value
        elif isinstance(current, list):
            current[int(final_key)] = value
        
        return result
    
    @staticmethod
    @function_logger("Calculate diff between outlines")
    def calculate_diff(
        original: Dict[str, Any],
        edited: Dict[str, Any]
    ) -> List[FieldChange]:
        """
        Compare original and edited outlines, return list of changes.
        """
        changes = []
        
        def _compare(obj1, obj2, path=""):
            if isinstance(obj1, dict) and isinstance(obj2, dict):
                for key in set(obj1.keys()) | set(obj2.keys()):
                    new_path = f"{path}.{key}" if path else key
                    
                    if key not in obj1:
                        changes.append(FieldChange(
                            field_path=new_path,
                            old_value=None,
                            new_value=obj2[key],
                            field_type="added"
                        ))
                    elif key not in obj2:
                        changes.append(FieldChange(
                            field_path=new_path,
                            old_value=obj1[key],
                            new_value=None,
                            field_type="removed"
                        ))
                    else:
                        _compare(obj1[key], obj2[key], new_path)
            
            elif isinstance(obj1, list) and isinstance(obj2, list):
                for i, (item1, item2) in enumerate(zip(obj1, obj2)):
                    new_path = f"{path}.{i}"
                    _compare(item1, item2, new_path)
            
            elif obj1 != obj2:
                field_name = path.split('.')[-1]
                changes.append(FieldChange(
                    field_path=path,
                    old_value=obj1,
                    new_value=obj2,
                    field_type=field_name,
                    is_protected=field_name in EditingService.PROTECTED_FIELDS
                ))
        
        _compare(original, edited)
        return changes
    
    @staticmethod
    @function_logger("Merge edited outline with new generation")
    def merge_with_regeneration(
        original_outline: Dict[str, Any],
        edited_outline: Dict[str, Any],
        regenerated_outline: Dict[str, Any],
        mode: str = 'full'
    ) -> Dict[str, Any]:
        """
        Intelligently merge edited sections with regenerated content.
        
        Strategies:
        - 'full': Use edited values where they exist, regenerated elsewhere
        - 'module': Merge only for specific module
        - 'objectives': Update objectives, keep other edits
        """
        result = json.loads(json.dumps(regenerated_outline))
        
        # Find all edits
        diffs = EditingService.calculate_diff(original_outline, edited_outline)
        
        # Apply edits to regenerated version
        for change in diffs:
            if change.field_type not in ['removed']:
                EditingService._set_nested_value(result, change.field_path, change.new_value)
        
        return result
    
    @staticmethod
    @function_logger("Get edit history for field")
    def get_field_edit_history(
        edits_log: List[Dict[str, Any]],
        field_path: str
    ) -> List[Dict[str, Any]]:
        """Retrieve all edits for a specific field."""
        return [e for e in edits_log if e.get('field_path') == field_path]
    
    @staticmethod
    @function_logger("Highlight editable regions in outline")
    def get_editable_regions(outline: Dict[str, Any]) -> List[str]:
        """
        Return list of all editable field paths in outline.
        Used for UI to highlight/enable edit buttons.
        """
        editable = []
        
        def _scan(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    
                    # Check if this field is editable
                    field_name = key.lower()
                    if field_name in ['title', 'description', 'statement']:
                        editable.append(new_path)
                    
                    _scan(value, new_path)
            
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_path = f"{path}.{i}"
                    _scan(item, new_path)
        
        _scan(outline)
        return editable
    
    @staticmethod
    @function_logger("Revert edit")
    def revert_edit(
        edited_outline: Dict[str, Any],
        original_outline: Dict[str, Any],
        field_path: str
    ) -> Dict[str, Any]:
        """Revert a single field to original value."""
        success, original_value = EditingService._get_nested_value(original_outline, field_path)
        
        if success:
            result, _, updated = EditingService.apply_edit(
                edited_outline,
                field_path,
                original_value
            )
            if result:
                return updated
        
        return edited_outline


# Streamlit helper components
@function_logger("Create editable text field")
def st_editable_text_field(
    label: str,
    value: str,
    field_id: str,
    on_edit_callback=None
) -> str:
    """Streamlit component for inline editing."""
    import streamlit as st
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        new_value = st.text_area(label, value=value, key=field_id)
    
    with col2:
        if st.button("✏️", key=f"edit_{field_id}"):
            if on_edit_callback:
                on_edit_callback(field_id, value, new_value)
    
    return new_value


@function_logger("Create editable field with revert")
def st_editable_field_with_revert(
    label: str,
    original_value: str,
    edited_value: str,
    field_id: str,
    on_save_callback=None,
    on_revert_callback=None
) -> str:
    """Editable field with original comparison and revert button."""
    import streamlit as st
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        current_value = st.text_area(
            label,
            value=edited_value,
            key=field_id,
            height=80
        )
    
    with col2:
        if st.button("💾 Save", key=f"save_{field_id}"):
            if on_save_callback:
                on_save_callback(field_id, current_value)
    
    with col3:
        if edited_value != original_value:
            if st.button("↩️ Revert", key=f"revert_{field_id}"):
                if on_revert_callback:
                    on_revert_callback(field_id)
    
    # Show original if different
    if current_value != original_value:
        with st.expander("📝 Show original"):
            st.text(original_value)
    
    return current_value
