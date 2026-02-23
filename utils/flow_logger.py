"""
Flow Logging System - Comprehensive request tracing.

Logs every function call with:
- Function name and purpose
- Actual input values
- Actual output values
- Execution time
- Error details if applicable

Creates readable log files for flow analysis.
"""

import logging
import json
import functools
import time
from pathlib import Path
from typing import Any, Callable, Optional, Dict
from datetime import datetime
from enum import Enum
import traceback

# Create logs directory
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Log file path
LOG_FILE = LOGS_DIR / "flow.log"
SESSION_LOG_FILE = LOGS_DIR / "session.log"

# Current session ID (set when flow starts)
_current_session_id: Optional[str] = None
_session_start_time: Optional[datetime] = None


class LogLevel(str, Enum):
    """Log levels for different severity."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"


class FlowLogger:
    """Comprehensive flow logging for request tracing."""
    
    def __init__(self, log_file: Path = LOG_FILE):
        """Initialize flow logger."""
        self.log_file = log_file
        self.logger = logging.getLogger(__name__)
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger with file handler."""
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # File handler
        handler = logging.FileHandler(self.log_file, mode='a', encoding='utf-8')
        handler.setLevel(logging.DEBUG)
        
        # Format: timestamp | level | message
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log(
        self,
        level: LogLevel,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ):
        """Log a message with optional details."""
        log_msg = message
        
        if session_id or _current_session_id:
            sid = session_id or _current_session_id
            log_msg = f"[{sid[:8]}] {message}"
        
        if details:
            try:
                details_str = json.dumps(details, indent=2, default=str)
                log_msg += f"\n{details_str}"
            except Exception as e:
                log_msg += f"\n[Details serialization failed: {e}]"
        
        log_level_map = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.SUCCESS: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
        }
        
        self.logger.log(log_level_map[level], log_msg)
    
    def log_function_start(
        self,
        function_name: str,
        purpose: str,
        inputs: Dict[str, Any],
        session_id: Optional[str] = None
    ):
        """Log function entry."""
        message = f"→ ENTER: {function_name} | {purpose}"
        self.log(LogLevel.INFO, message, {"inputs": self._sanitize(inputs)}, session_id)
    
    def log_function_end(
        self,
        function_name: str,
        output: Any,
        execution_time: float,
        session_id: Optional[str] = None
    ):
        """Log function exit with output."""
        message = f"← EXIT: {function_name} | {execution_time:.3f}s"
        self.log(LogLevel.SUCCESS, message, {"output": self._sanitize(output)}, session_id)
    
    def log_function_error(
        self,
        function_name: str,
        error: Exception,
        execution_time: float,
        session_id: Optional[str] = None
    ):
        """Log function error."""
        message = f"✗ ERROR in {function_name} | {execution_time:.3f}s"
        details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc()
        }
        self.log(LogLevel.ERROR, message, details, session_id)
    
    def log_step(
        self,
        step_name: str,
        description: str,
        details: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ):
        """Log a processing step."""
        message = f"◆ STEP: {step_name} | {description}"
        self.log(LogLevel.INFO, message, details, session_id)
    
    def log_checkpoint(
        self,
        checkpoint_name: str,
        status: str,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ):
        """Log a checkpoint in the flow."""
        message = f"◆ CHECKPOINT: {checkpoint_name} | {status}"
        self.log(LogLevel.INFO, message, context, session_id)
    
    @staticmethod
    def _sanitize(obj: Any, max_depth: int = 2, current_depth: int = 0) -> Any:
        """Sanitize object for JSON serialization."""
        if current_depth >= max_depth:
            return f"<{type(obj).__name__}>"
        
        if obj is None:
            return None
        
        if isinstance(obj, (str, int, float, bool)):
            return obj
        
        if isinstance(obj, list):
            return [FlowLogger._sanitize(item, max_depth, current_depth + 1) for item in obj[:3]]
        
        if isinstance(obj, dict):
            return {
                k: FlowLogger._sanitize(v, max_depth, current_depth + 1)
                for k, v in list(obj.items())[:5]
            }
        
        if hasattr(obj, '__dict__'):
            try:
                return {
                    k: FlowLogger._sanitize(v, max_depth, current_depth + 1)
                    for k, v in list(obj.__dict__.items())[:5]
                }
            except:
                pass
        
        return f"<{type(obj).__name__}>"


# Global logger instance
_flow_logger: Optional[FlowLogger] = None


def get_flow_logger() -> FlowLogger:
    """Get or create global flow logger."""
    global _flow_logger
    if _flow_logger is None:
        _flow_logger = FlowLogger()
    return _flow_logger


def set_session_id(session_id: str):
    """Set current session ID for logging."""
    global _current_session_id, _session_start_time
    _current_session_id = session_id
    _session_start_time = datetime.now()
    logger = get_flow_logger()
    logger.log(LogLevel.INFO, f"═══════════════════ SESSION START ═══════════════════", session_id=session_id)


def get_current_session_id() -> Optional[str]:
    """Get current session ID."""
    return _current_session_id


def end_session():
    """End current session and log summary."""
    global _current_session_id, _session_start_time
    if _current_session_id and _session_start_time:
        duration = (datetime.now() - _session_start_time).total_seconds()
        logger = get_flow_logger()
        logger.log(
            LogLevel.INFO,
            f"═══════════════════ SESSION END ═══════════════════",
            {"total_duration_seconds": duration},
            session_id=_current_session_id
        )
    _current_session_id = None
    _session_start_time = None


def function_logger(purpose: str = ""):
    """
    Decorator for logging function calls with inputs and outputs.
    
    Args:
        purpose: Human-readable description of function purpose
        
    Usage:
        @function_logger("Build prompt for LLM")
        def _build_prompt(self, context, duration_plan):
            return prompt
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_flow_logger()
            function_name = func.__qualname__
            func_purpose = purpose or func.__doc__ or ""
            
            # Prepare inputs (skip 'self')
            inputs = {}
            if args and hasattr(args[0], '__class__') and args[0].__class__.__module__ != 'builtins':
                # Skip self for methods
                call_args = args[1:]
            else:
                call_args = args
            
            # Build inputs dict
            for i, arg in enumerate(call_args):
                inputs[f"arg{i}"] = arg
            inputs.update(kwargs)
            
            # Log function start
            logger.log_function_start(function_name, func_purpose, inputs, _current_session_id)
            
            # Execute function
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log function end
                logger.log_function_end(function_name, result, execution_time, _current_session_id)
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.log_function_error(function_name, e, execution_time, _current_session_id)
                raise
        
        return wrapper
    
    return decorator


def step_logger(step_name: str, description: str = ""):
    """
    Log a processing step.
    
    Usage:
        logger = get_flow_logger()
        logger.log_step("Validation", "Checking input schema", {"status": "ok"})
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_flow_logger()
            logger.log_step(step_name, description or func.__doc__ or "")
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.log(LogLevel.ERROR, f"Step failed: {e}", session_id=_current_session_id)
                raise
        
        return wrapper
    
    return decorator


# Convenience functions
def log_info(message: str, details: Optional[Dict[str, Any]] = None):
    """Log info message."""
    get_flow_logger().log(LogLevel.INFO, message, details, _current_session_id)


def log_success(message: str, details: Optional[Dict[str, Any]] = None):
    """Log success message."""
    get_flow_logger().log(LogLevel.SUCCESS, message, details, _current_session_id)


def log_warning(message: str, details: Optional[Dict[str, Any]] = None):
    """Log warning message."""
    get_flow_logger().log(LogLevel.WARNING, message, details, _current_session_id)


def log_error(message: str, details: Optional[Dict[str, Any]] = None):
    """Log error message."""
    get_flow_logger().log(LogLevel.ERROR, message, details, _current_session_id)


def clear_logs():
    """Clear existing log file."""
    if LOG_FILE.exists():
        LOG_FILE.unlink()
    get_flow_logger()  # Recreate logger


def tail_logs(n: int = 50) -> str:
    """Get last n lines of log file."""
    if not LOG_FILE.exists():
        return "No logs yet"
    
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    return ''.join(lines[-n:])
