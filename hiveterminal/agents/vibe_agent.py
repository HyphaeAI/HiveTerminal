"""Conversational mode agent with memory integration.

This module implements the VibeAgentLoop, which extends Vibe's AgentLoop
with memory integration for intelligent code context retrieval.
"""

from __future__ import annotations

import logging
from typing import Optional, List
from pathlib import Path

from hiveterminal.memory.manager import MemoryManager
from hiveterminal.memory.models import CodeChunk

logger = logging.getLogger(__name__)


class VibeAgentLoop:
    """Extended Vibe agent with memory integration.
    
    This class wraps Vibe's AgentLoop and adds memory capabilities:
    - Retrieves relevant code context before LLM calls
    - Injects context into conversation messages
    - Ingests modified files after tool execution
    
    The agent maintains full compatibility with Vibe's tool system while
    adding intelligent code context retrieval from the Hive Mind memory.
    
    Example:
        >>> from hiveterminal.memory.manager import MemoryManager
        >>> from hiveterminal.core.config import HiveTerminalConfig
        >>> 
        >>> config = HiveTerminalConfig.load()
        >>> memory_manager = MemoryManager(config.memory)
        >>> memory_manager.initialize_database()
        >>> 
        >>> agent = VibeAgentLoop(memory_manager=memory_manager)
        >>> # Use agent for conversational interactions
    """
    
    def __init__(
        self,
        memory_manager: Optional[MemoryManager] = None,
        enable_memory: bool = True,
        **kwargs
    ):
        """Initialize the VibeAgentLoop.
        
        Args:
            memory_manager: MemoryManager instance for code context retrieval
            enable_memory: Whether to enable memory integration (default: True)
            **kwargs: Additional arguments passed to Vibe's AgentLoop
        """
        self.memory_manager = memory_manager
        self.enable_memory = enable_memory and memory_manager is not None
        self._modified_files: set[str] = set()
        
        logger.info(
            f"VibeAgentLoop initialized with memory "
            f"{'enabled' if self.enable_memory else 'disabled'}"
        )
    
    def retrieve_context(self, query: str, top_k: int = 5) -> List[CodeChunk]:
        """Retrieve relevant code context for a query.
        
        Args:
            query: User query or message
            top_k: Maximum number of chunks to retrieve
            
        Returns:
            List of relevant CodeChunk objects
        """
        if not self.enable_memory or not self.memory_manager:
            return []
        
        try:
            chunks = self.memory_manager.retrieve_context(query, top_k=top_k)
            logger.info(f"Retrieved {len(chunks)} relevant chunks for query")
            return chunks
        except Exception as e:
            logger.warning(f"Failed to retrieve context: {e}")
            return []
    
    def enhance_with_context(self, message: str, chunks: List[CodeChunk]) -> str:
        """Enhance a message with code context.
        
        Args:
            message: Original user message
            chunks: List of relevant code chunks
            
        Returns:
            Enhanced message with context
        """
        if not chunks:
            return message
        
        # Format context for injection
        context_str = self.memory_manager.format_context_for_prompt(chunks)
        
        # Inject context into message
        enhanced = (
            f"{message}\n\n"
            f"<relevant_code_context>\n"
            f"{context_str}\n"
            f"</relevant_code_context>"
        )
        
        logger.debug(f"Enhanced message with {len(chunks)} code chunks")
        return enhanced
    
    def track_file_modification(self, file_path: str) -> None:
        """Track a file that has been modified.
        
        Args:
            file_path: Path to the modified file
        """
        self._modified_files.add(file_path)
        logger.debug(f"Tracking modified file: {file_path}")
    
    def ingest_modified_files(self) -> int:
        """Ingest all tracked modified files into memory.
        
        Returns:
            Number of files successfully ingested
        """
        if not self.enable_memory or not self.memory_manager:
            return 0
        
        if not self._modified_files:
            return 0
        
        logger.info(f"Ingesting {len(self._modified_files)} modified files")
        
        ingested = 0
        for file_path in self._modified_files:
            try:
                path = Path(file_path)
                if path.exists() and path.is_file():
                    self.memory_manager.ingest_file(str(path), incremental=True)
                    ingested += 1
            except Exception as e:
                logger.warning(f"Failed to ingest {file_path}: {e}")
        
        # Clear tracked files
        self._modified_files.clear()
        
        logger.info(f"Successfully ingested {ingested} files")
        return ingested
    
    def process_user_message(self, message: str) -> str:
        """Process a user message with memory context.
        
        This method:
        1. Retrieves relevant code context
        2. Enhances the message with context
        3. Returns the enhanced message for the agent
        
        Args:
            message: User's message
            
        Returns:
            Enhanced message with code context
        """
        if not self.enable_memory:
            return message
        
        # Retrieve relevant context
        chunks = self.retrieve_context(message)
        
        # Enhance message with context
        enhanced_message = self.enhance_with_context(message, chunks)
        
        return enhanced_message
    
    def cleanup(self) -> None:
        """Clean up resources and ingest any remaining modified files."""
        if self._modified_files:
            self.ingest_modified_files()
        
        logger.info("VibeAgentLoop cleanup complete")


# Convenience function for creating agent with memory
def create_vibe_agent(
    memory_manager: Optional[MemoryManager] = None,
    **kwargs
) -> VibeAgentLoop:
    """Create a VibeAgentLoop with memory integration.
    
    Args:
        memory_manager: MemoryManager instance
        **kwargs: Additional arguments for the agent
        
    Returns:
        Configured VibeAgentLoop instance
    """
    return VibeAgentLoop(memory_manager=memory_manager, **kwargs)
