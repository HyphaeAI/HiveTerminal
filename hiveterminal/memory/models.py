"""Data models for the HiveTerminal memory system.

This module defines the core data structures used by the memory manager:
- CodeChunk: Represents a semantic chunk of code with metadata
- MemoryConfig: Configuration for memory system (imported from core.config)
- MemoryStats: Statistics about the memory database
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# Import MemoryConfig from core config (already defined there)
from hiveterminal.core.config import MemoryConfig


@dataclass
class CodeChunk:
    """Represents a semantic chunk of code with metadata.
    
    A CodeChunk is a unit of code that has been extracted from a source file
    and stored in the vector database. Each chunk contains the actual code
    content along with metadata about its location and context.
    
    Attributes:
        content: The actual code content of this chunk
        file_path: Path to the source file (relative to project root)
        start_line: Starting line number in the source file (1-indexed)
        end_line: Ending line number in the source file (1-indexed, inclusive)
        language: Programming language of the code (e.g., 'python', 'javascript')
        timestamp: When this chunk was created/last updated
        chunk_id: Unique identifier for this chunk (UUID string)
    """
    
    content: str
    file_path: str
    start_line: int
    end_line: int
    language: str
    timestamp: datetime
    chunk_id: str
    
    def __post_init__(self):
        """Validate chunk data after initialization."""
        if self.start_line < 1:
            raise ValueError(f"start_line must be >= 1, got {self.start_line}")
        if self.end_line < self.start_line:
            raise ValueError(
                f"end_line ({self.end_line}) must be >= start_line ({self.start_line})"
            )
        if not self.content.strip():
            raise ValueError("content cannot be empty or whitespace-only")
        if not self.file_path:
            raise ValueError("file_path cannot be empty")
        if not self.chunk_id:
            raise ValueError("chunk_id cannot be empty")
    
    def line_count(self) -> int:
        """Return the number of lines in this chunk."""
        return self.end_line - self.start_line + 1
    
    def to_dict(self) -> dict:
        """Convert chunk to dictionary for storage."""
        return {
            "content": self.content,
            "file_path": self.file_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "language": self.language,
            "timestamp": self.timestamp.isoformat(),
            "chunk_id": self.chunk_id,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CodeChunk":
        """Create a CodeChunk from a dictionary."""
        return cls(
            content=data["content"],
            file_path=data["file_path"],
            start_line=data["start_line"],
            end_line=data["end_line"],
            language=data["language"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            chunk_id=data["chunk_id"],
        )


@dataclass
class MemoryStats:
    """Statistics about the memory database.
    
    This class provides insights into the current state of the Hive Mind
    memory system, including how much code has been indexed and the size
    of the database.
    
    Attributes:
        total_chunks: Total number of code chunks stored in the database
        total_files: Total number of unique files indexed
        database_size_bytes: Size of the database on disk in bytes
        languages: Dictionary mapping language names to chunk counts
        last_updated: Timestamp of the most recent chunk update
        oldest_chunk: Timestamp of the oldest chunk in the database
    """
    
    total_chunks: int
    total_files: int
    database_size_bytes: int
    languages: dict[str, int]
    last_updated: Optional[datetime] = None
    oldest_chunk: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate stats data after initialization."""
        if self.total_chunks < 0:
            raise ValueError(f"total_chunks must be >= 0, got {self.total_chunks}")
        if self.total_files < 0:
            raise ValueError(f"total_files must be >= 0, got {self.total_files}")
        if self.database_size_bytes < 0:
            raise ValueError(
                f"database_size_bytes must be >= 0, got {self.database_size_bytes}"
            )
    
    def database_size_mb(self) -> float:
        """Return database size in megabytes."""
        return self.database_size_bytes / (1024 * 1024)
    
    def average_chunks_per_file(self) -> float:
        """Return average number of chunks per file."""
        if self.total_files == 0:
            return 0.0
        return self.total_chunks / self.total_files
    
    def to_dict(self) -> dict:
        """Convert stats to dictionary for display."""
        return {
            "total_chunks": self.total_chunks,
            "total_files": self.total_files,
            "database_size_bytes": self.database_size_bytes,
            "database_size_mb": round(self.database_size_mb(), 2),
            "languages": self.languages,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "oldest_chunk": self.oldest_chunk.isoformat() if self.oldest_chunk else None,
            "average_chunks_per_file": round(self.average_chunks_per_file(), 2),
        }


# Re-export MemoryConfig for convenience
__all__ = ["CodeChunk", "MemoryConfig", "MemoryStats"]
