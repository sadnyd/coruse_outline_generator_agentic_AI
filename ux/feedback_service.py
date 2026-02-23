"""
8.8 Feedback Capture - Lightweight quality feedback collection.

Anonymous by default.
No course content stored unless opt-in.
Session-bound unless user consents.

Fuels Phase 9 observability and metrics.
"""

import json
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from enum import Enum

from utils.flow_logger import function_logger


class Usefulness(Enum):
    """User-provided usefulness rating."""
    VERY_POOR = 1
    POOR = 2
    NEUTRAL = 3
    GOOD = 4
    EXCELLENT = 5


@function_logger("Initialize feedback record")
class FeedbackRecord:
    """A single piece of user feedback."""
    
    def __init__(
        self,
        session_id: str,
        usefulness_rating: int,
        would_reuse: bool,
        is_anonymous: bool = True,
        text_feedback: Optional[str] = None,
        course_title_included: bool = False
    ):
        self.feedback_id = str(uuid.uuid4())[:8]
        self.session_id = session_id
        self.timestamp = datetime.now().isoformat()
        
        # Ratings
        self.usefulness_rating = usefulness_rating  # 1-5
        self.would_reuse = would_reuse  # bool
        self.text_feedback = text_feedback or ""
        
        # Privacy
        self.is_anonymous = is_anonymous
        self.course_title_included = course_title_included
        
        # System info (always included)
        self.python_version = self._get_python_version()
        self.streamlit_version = self._get_streamlit_version()
    
    @staticmethod
    def _get_python_version() -> str:
        """Get Python version."""
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}"
    
    @staticmethod
    def _get_streamlit_version() -> str:
        """Get Streamlit version."""
        try:
            import streamlit
            return streamlit.__version__
        except:
            return "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'feedback_id': self.feedback_id,
            'session_id': self.session_id,
            'timestamp': self.timestamp,
            'usefulness': self.usefulness_rating,
            'would_reuse': self.would_reuse,
            'text_feedback': self.text_feedback[:500],  # Limit text
            'is_anonymous': self.is_anonymous,
            'course_title_included': self.course_title_included,
            'python_version': self.python_version,
            'streamlit_version': self.streamlit_version,
        }


@function_logger("Initialize feedback service")
class FeedbackService:
    """Manage user feedback collection."""
    
    FEEDBACK_DIR = Path("feedback")
    
    def __init__(self):
        """Initialize service."""
        self.FEEDBACK_DIR.mkdir(exist_ok=True)
    
    @function_logger("Record user feedback")
    def record_feedback(self, feedback: FeedbackRecord) -> bool:
        """Store feedback to file."""
        try:
            # Store as JSONL (one JSON per line)
            feedback_file = self.FEEDBACK_DIR / "feedback.jsonl"
            
            with open(feedback_file, 'a') as f:
                f.write(json.dumps(feedback.to_dict()) + '\n')
            
            return True
        except Exception as e:
            print(f"Error recording feedback: {e}")
            return False
    
    @function_logger("Get feedback statistics")
    def get_stats(self) -> Dict[str, Any]:
        """Generate statistics from feedback."""
        stats = {
            'total_feedback': 0,
            'average_usefulness': 0.0,
            'reuse_rate': 0.0,
            'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            'anonymous_count': 0,
        }
        
        feedback_file = self.FEEDBACK_DIR / "feedback.jsonl"
        
        if not feedback_file.exists():
            return stats
        
        records = []
        usefulness_scores = []
        reuse_count = 0
        
        try:
            with open(feedback_file, 'r') as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line)
                        records.append(record)
                        
                        rating = record.get('usefulness', 0)
                        usefulness_scores.append(rating)
                        
                        if rating in stats['rating_distribution']:
                            stats['rating_distribution'][rating] += 1
                        
                        if record.get('would_reuse'):
                            reuse_count += 1
                        
                        if record.get('is_anonymous'):
                            stats['anonymous_count'] += 1
        except Exception as e:
            print(f"Error reading feedback: {e}")
            return stats
        
        # Calculate aggregates
        stats['total_feedback'] = len(records)
        
        if usefulness_scores:
            stats['average_usefulness'] = sum(usefulness_scores) / len(usefulness_scores)
        
        if records:
            stats['reuse_rate'] = reuse_count / len(records)
        
        return stats
    
    @function_logger("Get feedback summary")
    def get_summary(self) -> Dict[str, Any]:
        """Get human-readable feedback summary."""
        stats = self.get_stats()
        
        avg_rating = stats.get('average_usefulness', 0.0)
        rating_emoji = {
            1: '😞',
            2: '😕',
            3: '😐',
            4: '🙂',
            5: '😄'
        }
        
        return {
            'total_responses': stats['total_feedback'],
            'average_rating': avg_rating,
            'rating_emoji': rating_emoji.get(round(avg_rating), '😐'),
            'would_reuse_percentage': f"{stats['reuse_rate']:.0%}",
            'anonymous_percentage': f"{(stats['anonymous_count'] / max(1, stats['total_feedback'])):.0%}",
            'distribution': stats['rating_distribution'],
        }
    
    @function_logger("Delete old feedback")
    def cleanup_old_feedback(self, days: int = 30):
        """Remove feedback older than N days."""
        import time
        import os
        
        feedback_file = self.FEEDBACK_DIR / "feedback.jsonl"
        
        if not feedback_file.exists():
            return
        
        cutoff_time = time.time() - (days * 86400)
        
        if feedback_file.stat().st_mtime < cutoff_time:
            feedback_file.unlink()
    
    @function_logger("Export feedback for analysis")
    def export_feedback(self, output_file: Optional[str] = None) -> Optional[str]:
        """Export all feedback to JSON file."""
        feedback_file = self.FEEDBACK_DIR / "feedback.jsonl"
        
        if not feedback_file.exists():
            return None
        
        records = []
        try:
            with open(feedback_file, 'r') as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line))
        except Exception as e:
            print(f"Error reading feedback: {e}")
            return None
        
        # Generate export filename
        if output_file is None:
            output_file = f"feedback_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_path = Path(output_file)
        
        try:
            with open(export_path, 'w') as f:
                json.dump(records, f, indent=2)
            return str(export_path)
        except Exception as e:
            print(f"Error exporting feedback: {e}")
            return None


# Streamlit components
@function_logger("Create feedback form in streamlit")
def st_feedback_form():
    """Create Streamlit feedback form component."""
    import streamlit as st
    
    st.markdown("### 📝 Help Us Improve")
    st.markdown("Your feedback is anonymous and helps us make this tool better.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        usefulness = st.radio(
            "How useful was this outline?",
            options=[
                "😞 Very Poor",
                "😕 Poor",
                "😐 Neutral",
                "🙂 Good",
                "😄 Excellent"
            ],
            key="usefulness_rating"
        )
        
        usefulness_map = {
            "😞 Very Poor": 1,
            "😕 Poor": 2,
            "😐 Neutral": 3,
            "🙂 Good": 4,
            "😄 Excellent": 5
        }
        rating = usefulness_map.get(usefulness, 3)
    
    with col2:
        would_reuse = st.checkbox(
            "Would you reuse this outline or tool?",
            key="would_reuse_checkbox"
        )
    
    # Optional text feedback
    with st.expander("💬 Add optional comments"):
        text_feedback = st.text_area(
            "Any additional feedback?",
            placeholder="Tell us what worked well or what could be improved...",
            max_chars=500,
            key="feedback_text"
        )
    
    # Privacy options
    st.divider()
    st.markdown("**Privacy**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        is_anonymous = st.checkbox("Keep my feedback anonymous", value=True, key="anonymous_checkbox")
    
    with col2:
        include_title = st.checkbox("Include course title for context", value=False, key="include_title_checkbox")
        st.caption("Helps us understand patterns")
    
    # Submit
    if st.button("📤 Submit Feedback", use_container_width=True):
        return {
            'usefulness': rating,
            'would_reuse': would_reuse,
            'text_feedback': text_feedback,
            'is_anonymous': is_anonymous,
            'include_title': include_title,
            'submitted': True
        }
    
    return None


@function_logger("Display feedback stats in streamlit")
def st_display_feedback_stats(service: FeedbackService):
    """Display feedback statistics in Streamlit."""
    import streamlit as st
    
    summary = service.get_summary()
    
    st.markdown("### 📊 Feedback Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Responses", summary['total_responses'])
    
    with col2:
        st.metric("Average Rating", f"{summary['average_rating']:.1f} {summary['rating_emoji']}")
    
    with col3:
        st.metric("Would Reuse", summary['would_reuse_percentage'])
    
    with col4:
        st.metric("Anonymous", summary['anonymous_percentage'])
    
    # Distribution chart
    distribution = summary['distribution']
    st.bar_chart({
        'Poor': distribution[1] + distribution[2],
        'Neutral': distribution[3],
        'Good': distribution[4] + distribution[5]
    })


# Global instance
_feedback_service: Optional[FeedbackService] = None

@function_logger("Get feedback service singleton")
def get_feedback_service() -> FeedbackService:
    """Get global feedback service."""
    global _feedback_service
    if _feedback_service is None:
        _feedback_service = FeedbackService()
    return _feedback_service
