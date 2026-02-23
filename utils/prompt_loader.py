"""
Centralized prompt loader for all LLM agents.

Loads prompts from files in the prompts/ folder and supports variable substitution.
Caches prompts in memory for performance.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging
from utils.flow_logger import function_logger

logger = logging.getLogger(__name__)


class PromptLoader:
    """Load and manage prompts from centralized prompts/ folder."""
    
    @function_logger("Handle __init__")
    @function_logger("Handle __init__")
    def __init__(self, prompts_dir: Optional[str] = None):
        """
        Initialize prompt loader.
        
        Args:
            prompts_dir: Path to prompts folder. Defaults to ./prompts relative to project root.
        """
        if prompts_dir is None:
            # Calculate path relative to this file
            current_dir = Path(__file__).parent  # utils/
            project_root = current_dir.parent  # root
            prompts_dir = str(project_root / "prompts")
        
        self.prompts_dir = Path(prompts_dir)
        self._cache: Dict[str, str] = {}
        
        if not self.prompts_dir.exists():
            logger.warning(f"Prompts directory not found: {self.prompts_dir}")
    
    @function_logger("Load prompt from centralized prompts folder")
    @function_logger("Execute load prompt")
    def load_prompt(self, prompt_name: str, variables: Optional[Dict[str, Any]] = None) -> str:
        """
        Load a prompt by name and optionally substitute variables.
        
        Args:
            prompt_name: Name of prompt file without .txt extension (e.g., 'module_creation_system')
            variables: Dict of variables to substitute in the prompt {'{key}': value}
            
        Returns:
            Loaded and formatted prompt string
            
        Raises:
            FileNotFoundError: If prompt file doesn't exist
            ValueError: If variable substitution fails
        """
        # Check cache first
        if prompt_name in self._cache:
            prompt = self._cache[prompt_name]
        else:
            # Load from file
            prompt_path = self.prompts_dir / f"{prompt_name}.txt"
            
            if not prompt_path.exists():
                raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
            
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    prompt = f.read()
                
                # Cache it
                self._cache[prompt_name] = prompt
                logger.debug(f"Loaded prompt from {prompt_path}")
            except Exception as e:
                raise RuntimeError(f"Failed to load prompt {prompt_name}: {str(e)}")
        
        # Substitute variables if provided
        if variables:
            try:
                prompt = prompt.format(**variables)
            except KeyError as e:
                raise ValueError(f"Missing variable in prompt {prompt_name}: {e}")
        
        return prompt
    
    @function_logger("Execute load prompt section")
    @function_logger("Execute load prompt section")
    def load_prompt_section(
        self, 
        prompt_name: str, 
        variables: Optional[Dict[str, Any]] = None
    ) -> str:
        """Alias for load_prompt for semantic clarity."""
        return self.load_prompt(prompt_name, variables)
    
    @function_logger("Execute combine prompts")
    @function_logger("Execute combine prompts")
    def combine_prompts(
        self,
        prompt_names: list,
        variables: Optional[Dict[str, Any]] = None,
        separator: str = "\n\n"
    ) -> str:
        """
        Combine multiple prompts into one.
        
        Args:
            prompt_names: List of prompt names to combine
            variables: Dict of variables to substitute in ALL prompts
            separator: String to join prompts with (default: double newline)
            
        Returns:
            Combined prompt string
        """
        prompts = []
        for name in prompt_names:
            prompt = self.load_prompt(name, variables)
            prompts.append(prompt)
        
        return separator.join(prompts)
    
    @function_logger("Execute clear cache")
    @function_logger("Execute clear cache")
    def clear_cache(self) -> None:
        """Clear in-memory prompt cache."""
        self._cache.clear()
        logger.info("Prompt cache cleared")
    
    @function_logger("List available prompts")
    @function_logger("List available prompts")
    def list_available_prompts(self) -> list:
        """
        List all available prompts in the prompts/ folder.
        
        Returns:
            List of prompt names (without .txt extension)
        """
        if not self.prompts_dir.exists():
            return []
        
        prompts = []
        for file in self.prompts_dir.glob("*.txt"):
            name = file.stem  # filename without extension
            prompts.append(name)
        
        return sorted(prompts)


# Global instance
_prompt_loader_instance: Optional[PromptLoader] = None


@function_logger("Get prompt loader")
@function_logger("Get prompt loader")
def get_prompt_loader(prompts_dir: Optional[str] = None) -> PromptLoader:
    """
    Get or create the global prompt loader instance (singleton).
    
    Args:
        prompts_dir: Path to prompts folder (only used on first call)
        
    Returns:
        PromptLoader instance
    """
    global _prompt_loader_instance
    
    if _prompt_loader_instance is None:
        _prompt_loader_instance = PromptLoader(prompts_dir)
    
    return _prompt_loader_instance


@function_logger("Execute reset prompt loader")
@function_logger("Execute reset prompt loader")
def reset_prompt_loader() -> None:
    """Reset the global prompt loader instance."""
    global _prompt_loader_instance
    _prompt_loader_instance = None
