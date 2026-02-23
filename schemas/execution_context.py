from utils.flow_logger import function_logger
"""
PHASE 2: Execution Context

Standardizes what agents receive across all phases.
Designed to support Phase 3-9 extensions without code changes.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


@dataclass
class ExecutionContext:
    """
    Context passed from Orchestrator to agents.
    
    Phase 2: Basic context (user input + tracking)
    Phase 3: Will add retrieved_documents
    Phase 4: Will add web_search_results
    Phase 6: Will add validator_feedback
    
    Breaking changes prevented by design.
    """
    
    # Core input
    user_input: Any  # UserInputSchema
    
    # Tracking
    session_id: str
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Optional enrichment (from file upload or previous phases)
    uploaded_pdf_text: Optional[str] = None
    uploaded_pdf_metadata: Optional[Dict[str, Any]] = None
    
    # Execution control
    execution_mode: str = "single_pass"  # Phase 2 only
    max_tokens: int = 8000
    
    # Phase 3+ extensions (initialized as None)
    retrieved_documents: Optional[Any] = None
    
    # Phase 4+ extensions
    web_search_results: Optional[Any] = None
    
    # Phase 6+ extensions
    validator_feedback: Optional[Dict[str, Any]] = None
    
    @function_logger("Execute to dict")
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize context to dict for logging/debugging.
        
        Returns:
            Dict with context fields (safe for JSON)
        """
        return {
            "session_id": self.session_id,
            "execution_id": self.execution_id,
            "execution_mode": self.execution_mode,
            "created_at": self.created_at.isoformat(),
            "user_input": self.user_input.model_dump() if hasattr(self.user_input, 'model_dump') else (self.user_input.dict() if hasattr(self.user_input, 'dict') else str(self.user_input)),
            "has_pdf_text": self.uploaded_pdf_text is not None,
        }
    
    @function_logger("Handle __repr__")
    def __repr__(self) -> str:
        """Human-readable representation."""
        return (
            f"ExecutionContext("
            f"execution_id={self.execution_id[:8]}..., "
            f"session_id={self.session_id[:8]}..., "
            f"mode={self.execution_mode}"
            f")"
        )
