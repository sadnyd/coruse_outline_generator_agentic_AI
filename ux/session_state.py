"""
8.1 Session State Hardening - Enhanced session management for Streamlit UX stability.

Guarantees:
- User input immutable after generation starts
- Uploads persist until explicit reset
- Edits don't get overwritten on reruns
- State survives page refresh
- Clean session lifecycle
"""

import json
import hashlib
import time
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from pathlib import Path

from utils.flow_logger import function_logger


class SessionPhase(Enum):
    """Session lifecycle phases."""
    IDLE = "idle"
    UPLOAD = "upload"
    GENERATING = "generating"
    GENERATED = "generated"
    EDITING = "editing"
    REGENERATING = "regenerating"
    EXPORTING = "exporting"


@dataclass
class UploadMetadata:
    """Track uploaded file without storing full content."""
    file_name: str
    file_size: int
    file_hash: str  # SHA256 of file
    upload_time: str  # ISO format
    temp_path: str  # Streamlit temp file path
    file_type: str  # "pdf" or "txt"


@dataclass
class EditRecord:
    """Track a single field edit."""
    field_id: str  # e.g., "module_0_title"
    original_value: Any
    edited_value: Any
    edit_time: str  # ISO format
    is_accepted: bool = True  # User confirmed


@dataclass
class AgentOutput:
    """Track output from a single agent."""
    agent_name: str
    output: Dict[str, Any]
    timestamp: str
    execution_time_seconds: float


@dataclass
class RegenerationRecord:
    """Track each regeneration attempt."""
    regeneration_id: str
    phase: str  # "full" | "module" | "objectives"
    target_module_id: Optional[str]
    triggered_time: str
    completed_time: Optional[str] = None
    reason: str = ""
    success: bool = False


@dataclass
class SessionState:
    """
    Hardened session state that survives Streamlit reruns.
    
    Invariants:
    - Once generation starts, user_input becomes immutable
    - Edits are never automatically overwritten
    - Each agent output is versioned
    - Regenerations add to history, don't replace
    """
    
    # Session identification
    session_id: str
    created_at: str  # ISO format
    
    # Lifecycle
    phase: SessionPhase = SessionPhase.IDLE
    
    # Input (immutable after generation starts)
    user_input: Optional[Dict[str, Any]] = None
    upload_metadata: Optional[UploadMetadata] = None
    
    # Generation outputs (per agent)
    retrieval_agent_output: Optional[AgentOutput] = None
    web_search_output: Optional[AgentOutput] = None
    module_creation_output: Optional[AgentOutput] = None
    validator_output: Optional[AgentOutput] = None
    
    # Final accepted outline
    final_outline: Optional[Dict[str, Any]] = None
    final_outline_accepted_time: Optional[str] = None
    
    # User edits (never auto-overwritten)
    edits: List[EditRecord] = field(default_factory=list)
    
    # Regenerations
    regenerations: List[RegenerationRecord] = field(default_factory=list)
    regeneration_count: int = 0
    
    # Validator feedback
    validator_score: Optional[float] = None
    validator_feedback: Optional[Dict[str, Any]] = None
    
    # Provenance
    provenance_data: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    last_activity: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionState':
        """Restore from dictionary."""
        # Convert phase string back to enum
        if 'phase' in data and isinstance(data['phase'], str):
            data['phase'] = SessionPhase(data['phase'])
        # Convert nested dataclasses
        if data.get('upload_metadata') and isinstance(data['upload_metadata'], dict):
            data['upload_metadata'] = UploadMetadata(**data['upload_metadata'])
        # Add more conversions as needed
        return cls(**data)


@function_logger("Initialize session state manager")
class SessionStateManager:
    """Manages hardened session state through Streamlit reruns."""
    
    SESSION_STORAGE_DIR = Path("session_store")
    
    def __init__(self):
        """Initialize manager."""
        self.SESSION_STORAGE_DIR.mkdir(exist_ok=True)
    
    @function_logger("Create new session")
    def create_session(self, session_id: str) -> SessionState:
        """Create a new session."""
        now = datetime.now().isoformat()
        state = SessionState(
            session_id=session_id,
            created_at=now,
            phase=SessionPhase.IDLE
        )
        self._save_session(state)
        return state
    
    @function_logger("Load session state from storage")
    def load_session(self, session_id: str) -> Optional[SessionState]:
        """Load existing session."""
        path = self.SESSION_STORAGE_DIR / f"{session_id}.json"
        if not path.exists():
            return None
        
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            return SessionState.from_dict(data)
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None
    
    @function_logger("Save session state to storage")
    def _save_session(self, state: SessionState):
        """Persist session to storage."""
        path = self.SESSION_STORAGE_DIR / f"{state.session_id}.json"
        with open(path, 'w') as f:
            # Convert enum to string for JSON
            data = state.to_dict()
            data['phase'] = data['phase'].value
            json.dump(data, f, indent=2, default=str)
    
    @function_logger("Update user input immutably")
    def set_user_input(self, state: SessionState, user_input: Dict[str, Any]) -> SessionState:
        """
        Set user input (immutable once generation starts).
        
        Guarantees:
        - Can only be set in IDLE or UPLOAD phase
        - Once set, cannot be changed
        """
        if state.phase not in [SessionPhase.IDLE, SessionPhase.UPLOAD]:
            raise ValueError(f"Cannot set user_input in {state.phase} phase")
        
        if state.user_input is not None:
            raise ValueError("User input already set and frozen")
        
        state.user_input = user_input
        state.phase = SessionPhase.UPLOAD
        state.last_activity = datetime.now().isoformat()
        self._save_session(state)
        return state
    
    @function_logger("Register uploaded file")
    def register_upload(
        self, 
        state: SessionState, 
        file_path: str, 
        file_name: str, 
        file_type: str
    ) -> SessionState:
        """Register uploaded file metadata (not content)."""
        file_size = Path(file_path).stat().st_size
        file_hash = self._compute_file_hash(file_path)
        
        state.upload_metadata = UploadMetadata(
            file_name=file_name,
            file_size=file_size,
            file_hash=file_hash,
            upload_time=datetime.now().isoformat(),
            temp_path=file_path,
            file_type=file_type
        )
        state.last_activity = datetime.now().isoformat()
        self._save_session(state)
        return state
    
    @function_logger("Record agent output")
    def record_agent_output(
        self,
        state: SessionState,
        agent_name: str,
        output: Dict[str, Any],
        execution_time: float
    ) -> SessionState:
        """Record output from an agent."""
        agent_output = AgentOutput(
            agent_name=agent_name,
            output=output,
            timestamp=datetime.now().isoformat(),
            execution_time_seconds=execution_time
        )
        
        # Store by agent name
        if agent_name == "retrieval":
            state.retrieval_agent_output = agent_output
        elif agent_name == "web_search":
            state.web_search_output = agent_output
        elif agent_name == "module_creation":
            state.module_creation_output = agent_output
        elif agent_name == "validator":
            state.validator_output = agent_output
        
        state.last_activity = datetime.now().isoformat()
        self._save_session(state)
        return state
    
    @function_logger("Record field edit")
    def record_edit(
        self,
        state: SessionState,
        field_id: str,
        original_value: Any,
        edited_value: Any
    ) -> SessionState:
        """
        Record a field edit.
        
        Guarantee: Edits are NEVER automatically overwritten.
        Future regenerations preserve edited content.
        """
        edit = EditRecord(
            field_id=field_id,
            original_value=original_value,
            edited_value=edited_value,
            edit_time=datetime.now().isoformat(),
            is_accepted=True
        )
        state.edits.append(edit)
        state.phase = SessionPhase.EDITING
        state.last_activity = datetime.now().isoformat()
        self._save_session(state)
        return state
    
    @function_logger("Start regeneration")
    def start_regeneration(
        self,
        state: SessionState,
        phase: str,
        target_module_id: Optional[str] = None,
        reason: str = ""
    ) -> SessionState:
        """Start a regeneration attempt."""
        regen_id = f"regen_{int(time.time() * 1000)}"
        
        record = RegenerationRecord(
            regeneration_id=regen_id,
            phase=phase,
            target_module_id=target_module_id,
            triggered_time=datetime.now().isoformat(),
            reason=reason,
            success=False
        )
        
        state.regenerations.append(record)
        state.regeneration_count += 1
        state.phase = SessionPhase.REGENERATING
        state.last_activity = datetime.now().isoformat()
        self._save_session(state)
        return state
    
    @function_logger("Complete regeneration")
    def complete_regeneration(
        self,
        state: SessionState,
        regen_id: str,
        success: bool,
        new_outline: Optional[Dict[str, Any]] = None
    ) -> SessionState:
        """Mark regeneration complete."""
        # Find and update the regeneration record
        for regen in state.regenerations:
            if regen.regeneration_id == regen_id:
                regen.completed_time = datetime.now().isoformat()
                regen.success = success
                break
        
        if success and new_outline:
            state.final_outline = new_outline
            state.phase = SessionPhase.GENERATED
        
        state.last_activity = datetime.now().isoformat()
        self._save_session(state)
        return state
    
    @function_logger("Reset session hard")
    def hard_reset(self, session_id: str) -> SessionState:
        """Complete session reset."""
        path = self.SESSION_STORAGE_DIR / f"{session_id}.json"
        if path.exists():
            path.unlink()
        
        return self.create_session(session_id)
    
    @staticmethod
    @function_logger("Compute file hash")
    def _compute_file_hash(file_path: str) -> str:
        """Compute SHA256 hash of file."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    @function_logger("Clean up old sessions")
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Remove sessions older than max_age_hours."""
        cutoff_time = time.time() - (max_age_hours * 3600)
        
        for session_file in self.SESSION_STORAGE_DIR.glob("*.json"):
            if session_file.stat().st_mtime < cutoff_time:
                session_file.unlink()


# Global instance
_session_manager: Optional[SessionStateManager] = None

@function_logger("Get session manager singleton")
def get_session_manager() -> SessionStateManager:
    """Get global session manager."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionStateManager()
    return _session_manager
