"""
UX Module - Phase 8 Implementation (Streamlit UX Polish + Exports)

Provides comprehensive UX layer for educators:
- Session state hardening (8.1)
- Structured outline rendering (8.2)
- Inline editing (8.3)
- Partial regeneration (8.4)
- Validator feedback visibility (8.5)
- Provenance tracking (8.6)
- Export system (8.7)
- Feedback capture (8.8)
- Error handling (8.9)
"""

from utils.flow_logger import function_logger

# Session management
from ux.session_state import (
    SessionState,
    SessionPhase,
    SessionStateManager,
    get_session_manager,
)

# Rendering
from ux.outline_renderer import (
    OutlineRenderer,
    st_display_outline,
)

# Editing
from ux.editing_service import (
    EditingService,
    st_editable_text_field,
    st_editable_field_with_revert,
)

# Regeneration
from ux.partial_regeneration import (
    PartialRegenerationService,
    RegenerationMode,
)

# Feedback
from ux.validator_feedback import (
    ValidatorFeedbackService,
    st_display_feedback,
)

# Provenance
from ux.provenance import (
    ProvenanceTracker,
    Source,
    ModuleProvenance,
    st_display_sources,
    st_display_integrity_report,
)

# Exports
from ux.export_service import (
    ExportService,
    st_download_export,
)

# Feedback collection
from ux.feedback_service import (
    FeedbackService,
    FeedbackRecord,
    get_feedback_service,
    st_feedback_form,
    st_display_feedback_stats,
)

# Error handling
from ux.error_handling import (
    FailureHandler,
    FallbackHandler,
    FailureScenario,
    st_display_error,
    st_display_health,
)

__all__ = [
    # Session
    'SessionState',
    'SessionPhase',
    'SessionStateManager',
    'get_session_manager',
    
    # Rendering
    'OutlineRenderer',
    'st_display_outline',
    
    # Editing
    'EditingService',
    'st_editable_text_field',
    'st_editable_field_with_revert',
    
    # Regeneration
    'PartialRegenerationService',
    'RegenerationMode',
    
    # Feedback
    'ValidatorFeedbackService',
    'st_display_feedback',
    
    # Provenance
    'ProvenanceTracker',
    'Source',
    'ModuleProvenance',
    'st_display_sources',
    'st_display_integrity_report',
    
    # Exports
    'ExportService',
    'st_download_export',
    
    # Feedback collection
    'FeedbackService',
    'FeedbackRecord',
    'get_feedback_service',
    'st_feedback_form',
    'st_display_feedback_stats',
    
    # Error handling
    'FailureHandler',
    'FallbackHandler',
    'FailureScenario',
    'st_display_error',
    'st_display_health',
]

@function_logger("Initialize UX module")
def init_ux():
    """Initialize all UX services."""
    session_manager = get_session_manager()
    feedback_service = get_feedback_service()
    return {
        'session_manager': session_manager,
        'feedback_service': feedback_service,
    }
