from utils.flow_logger import function_logger
"""Session management (PHASE 1+)."""

import uuid
import tempfile
import os
import shutil
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class SessionManager:
    """
    In-memory session store for course generation requests.
    
    Responsibilities:
    - Create and track session contexts
    - Store intermediate results (retrieval, web search, outline)
    - Manage uploaded PDF lifecycle (temp storage only, auto-cleanup)
    - Enforce session TTL (expire after completion or timeout)
    """
    
    @function_logger("Handle __init__")
    @function_logger("Handle __init__")
    def __init__(self, ttl_minutes: int = 30):
        """
        Initialize session manager.
        
        Args:
            ttl_minutes: Time-to-live for sessions (default 30 min)
        """
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.ttl_minutes = ttl_minutes
    
    @function_logger("Create session")
    @function_logger("Create session")
    def create_session(self) -> str:
        """
        Create a new session.
        
        Returns:
            session_id: Unique session identifier
        """
        session_id = str(uuid.uuid4())
        session_temp_dir = tempfile.mkdtemp(prefix=f"course_ai_{session_id[:8]}_")
        
        self.sessions[session_id] = {
            "session_id": session_id,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(minutes=self.ttl_minutes),
            "temp_dir": session_temp_dir,
            "user_input": None,
            "uploaded_pdf_path": None,
            "agent_outputs": {},
            "current_outline": None,
            "run_id": None,
            "debug_mode": False,
        }
        return session_id
    
    @function_logger("Get session")
    @function_logger("Get session")
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session context.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session dict or None if not found/expired
        """
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if expired
        if datetime.now() > session["expires_at"]:
            self.cleanup_session(session_id)
            return None
        
        return session
    
    @function_logger("Update session")
    @function_logger("Update session")
    def update_session(self, session_id: str, key: str, value: Any) -> None:
        """
        Update session value.
        
        Args:
            session_id: Session identifier
            key: Key to update
            value: New value
        """
        session = self.get_session(session_id)
        if session is not None:
            session[key] = value
            # Extend TTL on update
            session["expires_at"] = datetime.now() + timedelta(minutes=self.ttl_minutes)
    
    @function_logger("Execute cleanup session")
    @function_logger("Execute cleanup session")
    def cleanup_session(self, session_id: str) -> None:
        """
        Purge session and any associated temp files.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            
            # Delete temp directory
            if "temp_dir" in session:
                temp_dir = session["temp_dir"]
                if os.path.exists(temp_dir):
                    try:
                        shutil.rmtree(temp_dir)
                    except Exception:
                        pass  # Ignore cleanup errors
            
            # Remove from sessions
            del self.sessions[session_id]
