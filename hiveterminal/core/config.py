"""Configuration management for HiveTerminal.

This module extends Vibe's configuration with memory-specific settings.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Annotated, Any

from pydantic import BaseModel, Field, field_validator, model_validator


class MemoryConfig(BaseModel):
    """Configuration for the Hive Mind memory system.
    
    This configuration controls how code is ingested, embedded, and retrieved
    from the ChromaDB vector database.
    
    Attributes:
        database_path: Path to the ChromaDB database directory (default: ./.hive_memory)
        embedding_model: Model to use for generating embeddings (default: text-embedding-ada-002)
        chunk_size: Maximum number of tokens per code chunk (default: 1000)
        chunk_overlap: Number of overlapping tokens between chunks (default: 200)
        top_k_results: Number of top results to return from similarity search (default: 5)
        similarity_threshold: Minimum similarity score for results (0.0-1.0, default: 0.7)
    """
    
    database_path: Annotated[
        str,
        Field(
            default="./.hive_memory",
            description="Path to the ChromaDB database directory"
        )
    ]
    
    embedding_model: Annotated[
        str,
        Field(
            default="text-embedding-ada-002",
            description="Model to use for generating embeddings"
        )
    ]
    
    chunk_size: Annotated[
        int,
        Field(
            default=1000,
            gt=0,
            le=8000,
            description="Maximum number of tokens per code chunk"
        )
    ]
    
    chunk_overlap: Annotated[
        int,
        Field(
            default=200,
            ge=0,
            description="Number of overlapping tokens between chunks"
        )
    ]
    
    top_k_results: Annotated[
        int,
        Field(
            default=5,
            gt=0,
            le=50,
            description="Number of top results to return from similarity search"
        )
    ]
    
    similarity_threshold: Annotated[
        float,
        Field(
            default=0.7,
            ge=0.0,
            le=1.0,
            description="Minimum similarity score for results (0.0-1.0)"
        )
    ]
    
    @field_validator("database_path", mode="after")
    @classmethod
    def expand_database_path(cls, v: str) -> str:
        """Expand user home directory and resolve path."""
        return str(Path(v).expanduser().resolve())
    
    @field_validator("chunk_overlap", mode="after")
    @classmethod
    def validate_chunk_overlap(cls, v: int, info) -> int:
        """Ensure chunk_overlap is less than chunk_size."""
        # Note: chunk_size validation happens first, so we can access it from values
        if hasattr(info, 'data') and 'chunk_size' in info.data:
            chunk_size = info.data['chunk_size']
            if v >= chunk_size:
                raise ValueError(
                    f"chunk_overlap ({v}) must be less than chunk_size ({chunk_size})"
                )
        return v


class ModeConfig(BaseModel):
    """Configuration for operation mode selection.
    
    This configuration controls which mode HiveTerminal operates in by default.
    
    Attributes:
        default_mode: Default operation mode - 'conversational' for Vibe mode or 'spec' for Spec-First mode
    """
    
    default_mode: Annotated[
        str,
        Field(
            default="conversational",
            description="Default operation mode: 'conversational' or 'spec'"
        )
    ]
    
    @field_validator("default_mode", mode="after")
    @classmethod
    def validate_default_mode(cls, v: str) -> str:
        """Ensure default_mode is either 'conversational' or 'spec'."""
        valid_modes = {"conversational", "spec"}
        if v not in valid_modes:
            raise ValueError(
                f"default_mode must be one of {valid_modes}, got '{v}'"
            )
        return v


class SpecModeConfig(BaseModel):
    """Configuration for Spec-First mode behavior.
    
    This configuration controls how Spec-First mode operates, including
    backup creation, retry behavior, and execution timeouts.
    
    Attributes:
        create_backups: Whether to create backups before modifying files (default: True)
        backup_dir: Directory to store file backups (default: ./.hive_backups)
        max_retries: Maximum number of retries for failed actions (default: 3)
        timeout_seconds: Timeout in seconds for plan execution (default: 300)
    """
    
    create_backups: Annotated[
        bool,
        Field(
            default=True,
            description="Whether to create backups before modifying files"
        )
    ]
    
    backup_dir: Annotated[
        str,
        Field(
            default="./.hive_backups",
            description="Directory to store file backups"
        )
    ]
    
    max_retries: Annotated[
        int,
        Field(
            default=3,
            ge=0,
            le=10,
            description="Maximum number of retries for failed actions"
        )
    ]
    
    timeout_seconds: Annotated[
        int,
        Field(
            default=300,
            gt=0,
            le=3600,
            description="Timeout in seconds for plan execution"
        )
    ]
    
    @field_validator("backup_dir", mode="after")
    @classmethod
    def expand_backup_dir(cls, v: str) -> str:
        """Expand user home directory and resolve path."""
        return str(Path(v).expanduser().resolve())



class HiveTerminalConfig(BaseModel):
    """Main configuration class for HiveTerminal.
    
    This class integrates all HiveTerminal-specific configuration sections
    and provides methods for loading from TOML files.
    
    Attributes:
        default_mode: Default operation mode (from ModeConfig)
        memory: Memory system configuration
        spec_mode: Spec-First mode configuration
    """
    
    default_mode: Annotated[
        str,
        Field(
            default="conversational",
            description="Default operation mode: 'conversational' or 'spec'"
        )
    ]
    
    memory: Annotated[
        MemoryConfig,
        Field(
            default_factory=MemoryConfig,
            description="Memory system configuration"
        )
    ]
    
    spec_mode: Annotated[
        SpecModeConfig,
        Field(
            default_factory=SpecModeConfig,
            description="Spec-First mode configuration"
        )
    ]
    
    @field_validator("default_mode", mode="after")
    @classmethod
    def validate_default_mode(cls, v: str) -> str:
        """Ensure default_mode is either 'conversational' or 'spec'."""
        valid_modes = {"conversational", "spec"}
        if v not in valid_modes:
            raise ValueError(
                f"default_mode must be one of {valid_modes}, got '{v}'"
            )
        return v
    
    @model_validator(mode="after")
    def validate_config(self) -> HiveTerminalConfig:
        """Perform cross-field validation."""
        # Validate that chunk_overlap is less than chunk_size
        if self.memory.chunk_overlap >= self.memory.chunk_size:
            raise ValueError(
                f"memory.chunk_overlap ({self.memory.chunk_overlap}) must be less than "
                f"memory.chunk_size ({self.memory.chunk_size})"
            )
        
        # Validate that database_path and backup_dir are not the same
        if Path(self.memory.database_path).resolve() == Path(self.spec_mode.backup_dir).resolve():
            raise ValueError(
                "memory.database_path and spec_mode.backup_dir cannot be the same directory"
            )
        
        return self
    
    @classmethod
    def from_toml(cls, path: Path | str) -> HiveTerminalConfig:
        """Load configuration from a TOML file.
        
        Args:
            path: Path to the TOML configuration file
            
        Returns:
            HiveTerminalConfig instance with loaded settings
            
        Raises:
            FileNotFoundError: If the config file doesn't exist
            ValueError: If the TOML file is invalid or contains invalid values
        """
        config_path = Path(path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with config_path.open("rb") as f:
                data = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            raise ValueError(f"Invalid TOML file: {e}") from e
        
        # Extract HiveTerminal-specific configuration
        config_data: dict[str, Any] = {}
        
        # Extract default_mode (top-level)
        if "default_mode" in data:
            config_data["default_mode"] = data["default_mode"]
        
        # Extract memory configuration
        if "memory" in data:
            config_data["memory"] = data["memory"]
        
        # Extract spec_mode configuration
        if "spec_mode" in data:
            config_data["spec_mode"] = data["spec_mode"]
        
        return cls(**config_data)
    
    @classmethod
    def load(cls, config_path: Path | str | None = None) -> HiveTerminalConfig:
        """Load configuration from default or specified path.
        
        This method looks for configuration in the following order:
        1. Specified config_path (if provided and exists)
        2. ./.hive_config.toml (workspace root)
        3. ~/.hive_config.toml (user home)
        4. Default configuration (if no file found)
        
        Args:
            config_path: Optional path to configuration file
            
        Returns:
            HiveTerminalConfig instance
        """
        # If explicit path provided and exists, use it
        if config_path:
            path = Path(config_path)
            if path.exists():
                return cls.from_toml(path)
            # If explicit path doesn't exist, fall through to defaults
        
        # Try workspace root
        workspace_config = Path(".hive_config.toml")
        if workspace_config.exists():
            return cls.from_toml(workspace_config)
        
        # Try user home
        home_config = Path.home() / ".hive_config.toml"
        if home_config.exists():
            return cls.from_toml(home_config)
        
        # Return default configuration
        return cls()
    
    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            "default_mode": self.default_mode,
            "memory": self.memory.model_dump(),
            "spec_mode": self.spec_mode.model_dump(),
        }
