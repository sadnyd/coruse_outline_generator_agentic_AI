"""
8.9 UX Guardrails & Failure States - Graceful error handling.

Scenarios:
- Web search unavailable
- Retrieval returns nothing
- Validator fails repeatedly
- Token/context overflow

Response: Clear warnings, partial results allowed, recovery suggestions.
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from utils.flow_logger import function_logger


class FailureScenario(Enum):
    """Types of expected failures."""
    WEB_SEARCH_UNAVAILABLE = "web_search_unavailable"
    RETRIEVAL_NO_RESULTS = "retrieval_no_results"
    VALIDATOR_TIMEOUT = "validator_timeout"
    TOKEN_OVERFLOW = "token_overflow"
    LLM_FAILURE = "llm_failure"
    PDF_PARSE_ERROR = "pdf_parse_error"
    SESSION_EXPIRED = "session_expired"


class RecoverySuggestion(Enum):
    """Recovery actions for user."""
    RETRY = "retry"
    SKIP_STEP = "skip_step"
    USE_DEFAULTS = "use_defaults"
    SIMPLIFY_INPUT = "simplify_input"
    CHECK_CONNECTION = "check_connection"
    CONTACT_SUPPORT = "contact_support"


@function_logger("Initialize failure handler")
class FailureHandler:
    """Handle failures gracefully."""
    
    # Failure modes and recommended responses
    RECOVERY_MAP = {
        FailureScenario.WEB_SEARCH_UNAVAILABLE: {
            'message': 'Web search is temporarily unavailable',
            'severity': 'medium',
            'suggestions': [RecoverySuggestion.RETRY, RecoverySuggestion.USE_DEFAULTS],
            'allow_partial': True,
            'user_facing': 'We couldn\'t search the web right now. Using curriculum only.'
        },
        FailureScenario.RETRIEVAL_NO_RESULTS: {
            'message': 'No matching curricula found',
            'severity': 'low',
            'suggestions': [RecoverySuggestion.SIMPLIFY_INPUT],
            'allow_partial': True,
            'user_facing': 'No matching curricula found. Generating from first principles.'
        },
        FailureScenario.VALIDATOR_TIMEOUT: {
            'message': 'Quality check took too long',
            'severity': 'low',
            'suggestions': [RecoverySuggestion.SKIP_STEP],
            'allow_partial': True,
            'user_facing': 'Quality analysis timed out. Using baseline scoring.'
        },
        FailureScenario.TOKEN_OVERFLOW: {
            'message': 'Input too large for LLM',
            'severity': 'high',
            'suggestions': [RecoverySuggestion.SIMPLIFY_INPUT, RecoverySuggestion.CONTACT_SUPPORT],
            'allow_partial': False,
            'user_facing': 'Your input is too detailed. Try a shorter description.'
        },
        FailureScenario.LLM_FAILURE: {
            'message': 'LLM provider error',
            'severity': 'high',
            'suggestions': [RecoverySuggestion.RETRY, RecoverySuggestion.CHECK_CONNECTION],
            'allow_partial': False,
            'user_facing': 'LLM service error. Please check your connection and try again.'
        },
        FailureScenario.PDF_PARSE_ERROR: {
            'message': 'Could not parse PDF file',
            'severity': 'medium',
            'suggestions': [RecoverySuggestion.SKIP_STEP, RecoverySuggestion.SIMPLIFY_INPUT],
            'allow_partial': True,
            'user_facing': 'Could not read the PDF. Continuing without it.'
        },
        FailureScenario.SESSION_EXPIRED: {
            'message': 'Session has expired',
            'severity': 'high',
            'suggestions': [RecoverySuggestion.RETRY],
            'allow_partial': False,
            'user_facing': 'Your session expired. Please start over.'
        },
    }
    
    @staticmethod
    @function_logger("Handle failure scenario")
    def handle_failure(
        scenario: FailureScenario,
        error_details: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle a failure gracefully.
        
        Returns recovery plan for UX.
        """
        recovery = FailureHandler.RECOVERY_MAP.get(
            scenario,
            {
                'message': str(scenario),
                'severity': 'unknown',
                'suggestions': [RecoverySuggestion.CONTACT_SUPPORT],
                'allow_partial': False,
                'user_facing': 'An unexpected error occurred.'
            }
        )
        
        return {
            'scenario': scenario.value,
            'message': recovery['message'],
            'severity': recovery['severity'],
            'user_message': recovery['user_facing'],
            'suggestions': [s.value for s in recovery['suggestions']],
            'allow_partial_results': recovery['allow_partial'],
            'error_details': error_details,
            'context': context or {},
        }
    
    @staticmethod
    @function_logger("Determine if partial results acceptable")
    def can_proceed_partial(scenario: FailureScenario) -> bool:
        """Check if partial results are acceptable for this failure."""
        recovery = FailureHandler.RECOVERY_MAP.get(scenario, {})
        return recovery.get('allow_partial', False)
    
    @staticmethod
    @function_logger("Generate recovery suggestions")
    def get_recovery_steps(scenario: FailureScenario) -> List[Dict[str, Any]]:
        """Get actionable recovery steps."""
        recovery = FailureHandler.RECOVERY_MAP.get(scenario, {})
        suggestions = recovery.get('suggestions', [])
        
        steps = []
        for suggestion in suggestions:
            step = FailureHandler._suggestion_to_action(suggestion)
            steps.append(step)
        
        return steps
    
    @staticmethod
    @function_logger("Convert suggestion to action")
    def _suggestion_to_action(suggestion: RecoverySuggestion) -> Dict[str, Any]:
        """Convert suggestion enum to user action."""
        actions = {
            RecoverySuggestion.RETRY: {
                'action': 'retry',
                'label': '🔄 Retry',
                'description': 'Try again'
            },
            RecoverySuggestion.SKIP_STEP: {
                'action': 'skip',
                'label': '⏭️ Skip',
                'description': 'Skip this step and continue'
            },
            RecoverySuggestion.USE_DEFAULTS: {
                'action': 'use_defaults',
                'label': '📋 Use Defaults',
                'description': 'Use default settings'
            },
            RecoverySuggestion.SIMPLIFY_INPUT: {
                'action': 'simplify',
                'label': '✏️ Simplify',
                'description': 'Simplify your input and try again'
            },
            RecoverySuggestion.CHECK_CONNECTION: {
                'action': 'check_connection',
                'label': '🌐 Check Connection',
                'description': 'Check your internet connection'
            },
            RecoverySuggestion.CONTACT_SUPPORT: {
                'action': 'contact_support',
                'label': '📧 Contact Support',
                'description': 'Get help from support'
            },
        }
        
        return actions.get(suggestion, {
            'action': 'unknown',
            'label': 'Unknown',
            'description': 'Unknown action'
        })
    
    @staticmethod
    @function_logger("Check critical conditions")
    def check_health(
        web_search_ok: bool = True,
        llm_ok: bool = True,
        retrieval_ok: bool = True,
        validator_ok: bool = True
    ) -> Dict[str, Any]:
        """
        Quick health check of services.
        
        Returns status and recommendations.
        """
        status = {
            'services': {
                'web_search': 'healthy' if web_search_ok else 'degraded',
                'llm': 'healthy' if llm_ok else 'healthy',
                'retrieval': 'healthy' if retrieval_ok else 'degraded',
                'validator': 'healthy' if validator_ok else 'degraded',
            },
            'overall': 'healthy' if all([web_search_ok, llm_ok, retrieval_ok, validator_ok]) else 'degraded',
            'degraded_services': [],
            'recommendations': []
        }
        
        if not web_search_ok:
            status['degraded_services'].append('web_search')
            status['recommendations'].append('Web search is offline. Using local knowledge only.')
        
        if not llm_ok:
            status['degraded_services'].append('llm')
            status['recommendations'].append('LLM service unstable. May affect quality.')
        
        if not retrieval_ok:
            status['degraded_services'].append('retrieval')
            status['recommendations'].append('Knowledge base unavailable. Using defaults.')
        
        if not validator_ok:
            status['degraded_services'].append('validator')
            status['recommendations'].append('Quality validation skipped. Results unvalidated.')
        
        return status


@function_logger("Initialize fallback handler")
class FallbackHandler:
    """Provide fallback behavior when systems fail."""
    
    @staticmethod
    @function_logger("Get default curriculum structure")
    def get_default_structure() -> Dict[str, Any]:
        """Return default course structure when retrieval fails."""
        return {
            'modules': [
                {
                    'title': 'Fundamentals',
                    'description': 'Building blocks and core concepts',
                    'estimated_hours': 10,
                    'learning_objectives': [
                        {'statement': 'Understand core principles', 'bloom_level': 'understand'}
                    ]
                },
                {
                    'title': 'Intermediate Concepts',
                    'description': 'Building on fundamentals',
                    'estimated_hours': 15,
                    'learning_objectives': [
                        {'statement': 'Apply concepts in practice', 'bloom_level': 'apply'}
                    ]
                },
                {
                    'title': 'Advanced Topics',
                    'description': 'Mastery and specialization',
                    'estimated_hours': 15,
                    'learning_objectives': [
                        {'statement': 'Analyze complex problems', 'bloom_level': 'analyze'}
                    ]
                }
            ]
        }
    
    @staticmethod
    @function_logger("Get default validator score")
    def get_default_validator_output() -> Dict[str, Any]:
        """Return default validator output when validation fails."""
        return {
            'quality_score': 0.65,
            'message': 'Validation skipped - using baseline scoring',
            'warnings': ['Quality validation could not complete'],
            'findings': {
                'alignment_score': 0.7,
                'coverage_score': 0.65,
                'depth_score': 0.65
            }
        }
    
    @staticmethod
    @function_logger("Get safe partial outline")
    def create_safe_outline(
        user_input: Dict[str, Any],
        partial_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create safe outline with available data.
        
        Combines partial data with fallbacks.
        """
        outline = {
            'course_title': user_input.get('course_title', 'Untitled Course'),
            'course_summary': user_input.get('course_description', ''),
            'audience_level': user_input.get('audience_level', 'intermediate'),
            'audience_category': user_input.get('audience_category', 'general'),
            'learning_mode': user_input.get('learning_mode', 'mixed'),
        }
        
        # Use partial data if available
        if partial_data:
            outline.update(partial_data)
        
        # Use fallback modules if not available
        if 'modules' not in outline or not outline['modules']:
            outline.update(FallbackHandler.get_default_structure())
        
        # Use fallback validator if not available
        if '_validator_feedback' not in outline:
            outline['_validator_feedback'] = FallbackHandler.get_default_validator_output()
        
        return outline


# Streamlit display helpers
@function_logger("Display error state in streamlit")
def st_display_error(scenario: FailureScenario, details: Optional[str] = None):
    """Display error to user in Streamlit."""
    import streamlit as st
    
    recovery = FailureHandler.handle_failure(scenario, details)
    
    # Determine alert type
    severity = recovery['severity']
    if severity == 'high':
        alert_func = st.error
        emoji = "❌"
    elif severity == 'medium':
        alert_func = st.warning
        emoji = "⚠️"
    else:
        alert_func = st.info
        emoji = "ℹ️"
    
    alert_func(f"{emoji} **{recovery['user_message']}**")
    
    # Show suggestions
    suggestions = recovery['suggestions']
    if suggestions:
        st.markdown("**What you can do:**")
        for suggestion_val in suggestions:
            action = FailureHandler._suggestion_to_action(
                RecoverySuggestion(suggestion_val)
            )
            st.write(f"• {action['label']}: {action['description']}")


@function_logger("Display health status in streamlit")
def st_display_health(status: Dict[str, Any]):
    """Display system health in Streamlit."""
    import streamlit as st
    
    overall = status['overall']
    
    if overall == 'healthy':
        st.success("✅ All systems operational")
    else:
        st.warning(f"⚠️ Some services degraded")
        
        for service, health in status.get('services', {}).items():
            emoji = "✅" if health == 'healthy' else "⚠️"
            st.write(f"{emoji} {service.title()}: {health}")
    
    if status.get('recommendations'):
        st.info("**Recommendations:** " + " | ".join(status['recommendations']))
