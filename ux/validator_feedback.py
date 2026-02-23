"""
8.5 Validator Feedback Visibility - Expose quality feedback strategically.

Visible: Overall score, high-level feedback, warnings
Hidden: Internal heuristics, system messages, control logic

Provides educator confidence without technical details.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import json

from utils.flow_logger import function_logger


class FeedbackLevel(Enum):
    """Depth of feedback to expose."""
    SUMMARY = "summary"  # Score + headline findings
    DETAILED = "detailed"  # + explanations
    EXPERT = "expert"  # + internal scoring details


class FeedbackCategory(Enum):
    """Categories of validator feedback."""
    ALIGNMENT = "alignment"
    COVERAGE = "coverage"
    DEPTH = "depth"
    ASSESSMENT = "assessment"
    STRUCTURE = "structure"
    CLARITY = "clarity"


@function_logger("Initialize validator feedback service")
class ValidatorFeedbackService:
    """Manage and present validator feedback to educators."""
    
    # Mapping of internal scores to human-friendly descriptions
    SCORE_RANGES = {
        (0.0, 0.4): ("🔴 Poor", "Significant issues need attention"),
        (0.4, 0.6): ("🟠 Fair", "Some important improvements needed"),
        (0.6, 0.8): ("🟡 Good", "Generally well-structured with minor suggestions"),
        (0.8, 0.95): ("🟢 Excellent", "High quality, ready for use"),
        (0.95, 1.0): ("🟣 Outstanding", "Exemplary structure and coverage"),
    }
    
    @staticmethod
    @function_logger("Extract public feedback from validator output")
    def extract_public_feedback(
        validator_output: Dict[str, Any],
        level: FeedbackLevel = FeedbackLevel.DETAILED
    ) -> Dict[str, Any]:
        """
        Extract only the parts of validator feedback safe/useful for educators.
        
        Filters out:
        - Internal heuristic scores
        - System messages
        - Regeneration hints
        - Implementation details
        """
        public = {
            'overall_score': validator_output.get('quality_score', 0.0),
            'level_emoji': ValidatorFeedbackService._get_score_emoji(
                validator_output.get('quality_score', 0.0)
            ),
            'level_text': ValidatorFeedbackService._get_score_text(
                validator_output.get('quality_score', 0.0)
            ),
            'key_findings': [],
            'warnings': [],
            'suggestions': []
        }
        
        # Extract key findings
        findings = validator_output.get('findings', {})
        
        if findings.get('alignment_score', 0.0) < 0.7:
            public['key_findings'].append({
                'category': FeedbackCategory.ALIGNMENT.value,
                'message': f"Alignment with audience: {findings.get('alignment_feedback', 'Could be improved')}",
                'severity': 'medium' if findings.get('alignment_score', 0.0) > 0.5 else 'high'
            })
        
        if findings.get('coverage_score', 0.0) < 0.7:
            public['key_findings'].append({
                'category': FeedbackCategory.COVERAGE.value,
                'message': f"Coverage: {findings.get('coverage_feedback', 'Some topics may be undercovered')}",
                'severity': 'medium' if findings.get('coverage_score', 0.0) > 0.5 else 'high'
            })
        
        if findings.get('structure_score', 0.0) < 0.8:
            public['key_findings'].append({
                'category': FeedbackCategory.STRUCTURE.value,
                'message': f"Structure: {findings.get('structure_feedback', 'Could be more logical')}",
                'severity': 'low'
            })
        
        # Extract warnings
        warnings = validator_output.get('warnings', [])
        for warning in warnings:
            # Filter out system warnings
            if not warning.startswith('_'):
                public['warnings'].append(warning)
        
        # Extract suggestions (if level allows)
        if level in [FeedbackLevel.DETAILED, FeedbackLevel.EXPERT]:
            suggestions = validator_output.get('suggestions', [])
            # Limit suggestions to practical ones, not internal guidance
            practical_suggestions = [
                s for s in suggestions 
                if not any(term in s.lower() for term in ['regenerate', 'internal', 'system'])
            ]
            public['suggestions'] = practical_suggestions[:5]  # Top 5 only
        
        return public
    
    @staticmethod
    @function_logger("Get score emoji")
    def _get_score_emoji(score: float) -> str:
        """Get emoji for score range."""
        for (low, high), (emoji, _) in ValidatorFeedbackService.SCORE_RANGES.items():
            if low <= score < high:
                return emoji.split()[0]  # Just emoji
        return "⚪"
    
    @staticmethod
    @function_logger("Get score text description")
    def _get_score_text(score: float) -> str:
        """Get human text for score."""
        for (low, high), (_, text) in ValidatorFeedbackService.SCORE_RANGES.items():
            if low <= score < high:
                return text
        return "Unknown"
    
    @staticmethod
    @function_logger("Format feedback for display")
    def format_for_display(
        public_feedback: Dict[str, Any],
        include_metrics: bool = True
    ) -> Dict[str, Any]:
        """
        Format feedback for Streamlit display.
        
        Returns structure ready for rendering.
        """
        display = {
            'score': public_feedback['overall_score'],
            'score_display': f"{public_feedback['level_emoji']} {public_feedback['level_text']}",
            'findings': public_feedback['key_findings'],
            'warnings': public_feedback['warnings'],
            'suggestions': public_feedback['suggestions'],
        }
        
        if include_metrics:
            display['metrics'] = ValidatorFeedbackService._compute_metrics(public_feedback)
        
        return display
    
    @staticmethod
    @function_logger("Compute metrics summary")
    def _compute_metrics(public_feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Compute aggregate metrics for display."""
        metrics = {
            'finding_count': len(public_feedback.get('key_findings', [])),
            'warning_count': len(public_feedback.get('warnings', [])),
            'suggestion_count': len(public_feedback.get('suggestions', [])),
            'total_items': 0
        }
        
        metrics['total_items'] = sum([
            metrics['finding_count'],
            metrics['warning_count'],
            metrics['suggestion_count']
        ])
        
        return metrics
    
    @staticmethod
    @function_logger("Generate feedback summary card")
    def generate_summary_card(
        validator_output: Dict[str, Any]
    ) -> str:
        """Generate short summary for quick reference."""
        score = validator_output.get('quality_score', 0.0)
        emoji = ValidatorFeedbackService._get_score_emoji(score)
        text = ValidatorFeedbackService._get_score_text(score)
        
        return f"{emoji} **Quality Score: {score:.1%}**\n{text}"
    
    @staticmethod
    @function_logger("Extract actionable warnings")
    def extract_critical_warnings(
        public_feedback: Dict[str, Any],
        threshold: str = 'high'
    ) -> List[str]:
        """
        Extract only the most critical warnings educator should address.
        
        threshold: 'high', 'medium', 'low'
        """
        critical = []
        
        for finding in public_feedback.get('key_findings', []):
            severity = finding.get('severity', 'low')
            
            # Filter by threshold
            if threshold == 'high' and severity == 'high':
                critical.append(finding['message'])
            elif threshold == 'medium' and severity in ['high', 'medium']:
                critical.append(finding['message'])
            elif threshold == 'low':  # All
                critical.append(finding['message'])
        
        # Add direct warnings
        critical.extend(public_feedback.get('warnings', []))
        
        return critical
    
    @staticmethod
    @function_logger("Check if feedback indicates regeneration needed")
    def should_regenerate(
        validator_output: Dict[str, Any],
        threshold: float = 0.65
    ) -> tuple[bool, Optional[str]]:
        """
        Determine if quality is low enough to suggest regeneration.
        
        Returns: (should_regenerate, reason)
        """
        score = validator_output.get('quality_score', 0.0)
        
        if score < threshold:
            reason = f"Quality score {score:.1%} below ideal threshold ({threshold:.1%})"
            return True, reason
        
        # Check for critical issues
        findings = validator_output.get('findings', {})
        
        if findings.get('coverage_score', 0.0) < 0.5:
            return True, "Critical: Coverage gaps detected"
        
        if findings.get('alignment_score', 0.0) < 0.5:
            return True, "Critical: Audience alignment is poor"
        
        return False, None
    
    @staticmethod
    @function_logger("Compare feedback between versions")
    def compare_feedback(
        before: Dict[str, Any],
        after: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare validator feedback before/after changes.
        
        Shows what improved or regressed.
        """
        comparison = {
            'score_before': before.get('quality_score', 0.0),
            'score_after': after.get('quality_score', 0.0),
            'score_change': after.get('quality_score', 0.0) - before.get('quality_score', 0.0),
            'improved_areas': [],
            'regressed_areas': [],
            'maintained_areas': []
        }
        
        # Compare findings
        before_findings = before.get('findings', {})
        after_findings = after.get('findings', {})
        
        categories = ['alignment_score', 'coverage_score', 'depth_score', 'structure_score']
        
        for category in categories:
            before_val = before_findings.get(category, 0.0)
            after_val = after_findings.get(category, 0.0)
            
            change = after_val - before_val
            category_name = category.replace('_score', '').title()
            
            if change > 0.05:
                comparison['improved_areas'].append(
                    f"{category_name}: {before_val:.0%} → {after_val:.0%}"
                )
            elif change < -0.05:
                comparison['regressed_areas'].append(
                    f"{category_name}: {before_val:.0%} → {after_val:.0%}"
                )
            else:
                comparison['maintained_areas'].append(category_name)
        
        return comparison


# Streamlit display helpers
@function_logger("Display feedback in streamlit")
def st_display_feedback(
    validator_output: Dict[str, Any],
    level: FeedbackLevel = FeedbackLevel.DETAILED
):
    """Streamlit component to display validator feedback."""
    import streamlit as st
    
    public_feedback = ValidatorFeedbackService.extract_public_feedback(validator_output, level)
    display = ValidatorFeedbackService.format_for_display(public_feedback)
    
    # Score card
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Quality Score", f"{display['score']:.1%}")
    with col2:
        st.write(f"### {display['score_display']}")
    with col3:
        metrics = display.get('metrics', {})
        st.metric("Findings", metrics.get('finding_count', 0))
    
    st.divider()
    
    # Findings
    if display['findings']:
        st.subheading("🎯 Key Findings")
        for finding in display['findings']:
            severity_emoji = {"high": "🔴", "medium": "🟠", "low": "🟡"}
            emoji = severity_emoji.get(finding.get('severity', 'low'), "⚪")
            st.write(f"{emoji} **{finding['category'].title()}**: {finding['message']}")
    
    # Warnings
    if display['warnings']:
        st.warning(f"⚠️ **Warnings** ({len(display['warnings'])})")
        for warning in display['warnings']:
            st.write(f"• {warning}")
    
    # Suggestions
    if display['suggestions']:
        with st.expander("💡 Suggestions for Improvement"):
            for suggestion in display['suggestions']:
                st.write(f"• {suggestion}")
