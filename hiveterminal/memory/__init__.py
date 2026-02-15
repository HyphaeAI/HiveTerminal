"""Memory management system for HiveTerminal.

This package provides the Hive Mind memory system, which enables intelligent
code context retrieval using ChromaDB vector storage.

Main components:
- MemoryManager: Main interface for memory operations
- CodeChunk: Data structure for code chunks
- MemoryConfig: Configuration for memory system
- MemoryStats: Database statistics
"""

from hiveterminal.memory.manager import MemoryManager, MemoryManagerError
from hiveterminal.memory.models import CodeChunk, MemoryConfig, MemoryStats

__all__ = [
    "MemoryManager",
    "MemoryManagerError",
    "CodeChunk",
    "MemoryConfig",
    "MemoryStats",
]
