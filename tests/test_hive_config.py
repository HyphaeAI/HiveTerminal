"""Tests for HiveTerminalConfig class."""

import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from hiveterminal.core.config import HiveTerminalConfig, MemoryConfig, SpecModeConfig


def test_hive_config_defaults():
    """Test that HiveTerminalConfig has correct default values."""
    config = HiveTerminalConfig()
    
    assert config.default_mode == "conversational"
    assert isinstance(config.memory, MemoryConfig)
    assert isinstance(config.spec_mode, SpecModeConfig)
    
    # Check memory defaults
    assert config.memory.database_path.endswith(".hive_memory")
    assert config.memory.embedding_model == "text-embedding-ada-002"
    assert config.memory.chunk_size == 1000
    assert config.memory.chunk_overlap == 200
    assert config.memory.top_k_results == 5
    assert config.memory.similarity_threshold == 0.7
    
    # Check spec_mode defaults
    assert config.spec_mode.create_backups is True
    assert config.spec_mode.backup_dir.endswith(".hive_backups")
    assert config.spec_mode.max_retries == 3
    assert config.spec_mode.timeout_seconds == 300


def test_hive_config_custom_values():
    """Test that HiveTerminalConfig accepts custom values."""
    config = HiveTerminalConfig(
        default_mode="spec",
        memory=MemoryConfig(
            database_path="/custom/path",
            chunk_size=500,
            chunk_overlap=100,
        ),
        spec_mode=SpecModeConfig(
            create_backups=False,
            max_retries=5,
        ),
    )
    
    assert config.default_mode == "spec"
    assert config.memory.chunk_size == 500
    assert config.memory.chunk_overlap == 100
    assert config.spec_mode.create_backups is False
    assert config.spec_mode.max_retries == 5


def test_hive_config_invalid_mode():
    """Test that HiveTerminalConfig rejects invalid modes."""
    with pytest.raises(ValidationError) as exc_info:
        HiveTerminalConfig(default_mode="invalid")
    
    assert "default_mode must be one of" in str(exc_info.value)


def test_hive_config_chunk_overlap_validation():
    """Test that chunk_overlap must be less than chunk_size."""
    with pytest.raises(ValidationError) as exc_info:
        HiveTerminalConfig(
            memory=MemoryConfig(
                chunk_size=100,
                chunk_overlap=100,  # Equal to chunk_size
            )
        )
    
    assert "chunk_overlap" in str(exc_info.value)
    assert "must be less than" in str(exc_info.value)


def test_hive_config_same_paths_validation():
    """Test that database_path and backup_dir cannot be the same."""
    with pytest.raises(ValidationError) as exc_info:
        HiveTerminalConfig(
            memory=MemoryConfig(database_path="/same/path"),
            spec_mode=SpecModeConfig(backup_dir="/same/path"),
        )
    
    assert "cannot be the same directory" in str(exc_info.value)


def test_hive_config_from_toml():
    """Test loading configuration from a TOML file."""
    toml_content = """
default_mode = "spec"

[memory]
database_path = "./.test_memory"
embedding_model = "all-MiniLM-L6-v2"
chunk_size = 800
chunk_overlap = 150
top_k_results = 10
similarity_threshold = 0.8

[spec_mode]
create_backups = false
backup_dir = "./.test_backups"
max_retries = 5
timeout_seconds = 600
"""
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(toml_content)
        temp_path = Path(f.name)
    
    try:
        config = HiveTerminalConfig.from_toml(temp_path)
        
        assert config.default_mode == "spec"
        assert config.memory.embedding_model == "all-MiniLM-L6-v2"
        assert config.memory.chunk_size == 800
        assert config.memory.chunk_overlap == 150
        assert config.memory.top_k_results == 10
        assert config.memory.similarity_threshold == 0.8
        assert config.spec_mode.create_backups is False
        assert config.spec_mode.max_retries == 5
        assert config.spec_mode.timeout_seconds == 600
    finally:
        temp_path.unlink()


def test_hive_config_from_toml_partial():
    """Test loading configuration with only some sections defined."""
    toml_content = """
default_mode = "conversational"

[memory]
chunk_size = 1500
"""
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(toml_content)
        temp_path = Path(f.name)
    
    try:
        config = HiveTerminalConfig.from_toml(temp_path)
        
        assert config.default_mode == "conversational"
        assert config.memory.chunk_size == 1500
        # Other memory settings should use defaults
        assert config.memory.chunk_overlap == 200
        assert config.memory.top_k_results == 5
        # spec_mode should use all defaults
        assert config.spec_mode.create_backups is True
        assert config.spec_mode.max_retries == 3
    finally:
        temp_path.unlink()


def test_hive_config_from_toml_file_not_found():
    """Test that from_toml raises FileNotFoundError for missing files."""
    with pytest.raises(FileNotFoundError) as exc_info:
        HiveTerminalConfig.from_toml("/nonexistent/path.toml")
    
    assert "Configuration file not found" in str(exc_info.value)


def test_hive_config_from_toml_invalid_toml():
    """Test that from_toml raises ValueError for invalid TOML."""
    invalid_toml = """
default_mode = "spec"
[memory
chunk_size = 1000
"""
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(invalid_toml)
        temp_path = Path(f.name)
    
    try:
        with pytest.raises(ValueError) as exc_info:
            HiveTerminalConfig.from_toml(temp_path)
        
        assert "Invalid TOML file" in str(exc_info.value)
    finally:
        temp_path.unlink()


def test_hive_config_from_toml_invalid_values():
    """Test that from_toml validates configuration values."""
    toml_content = """
default_mode = "invalid_mode"

[memory]
chunk_size = 1000
"""
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(toml_content)
        temp_path = Path(f.name)
    
    try:
        with pytest.raises(ValidationError) as exc_info:
            HiveTerminalConfig.from_toml(temp_path)
        
        assert "default_mode" in str(exc_info.value)
    finally:
        temp_path.unlink()


def test_hive_config_load_default():
    """Test that load() returns default config when no file exists."""
    # Use a non-existent path to ensure we get defaults
    config = HiveTerminalConfig.load(config_path="/nonexistent/config.toml")
    
    # Should fall back to defaults
    assert config.default_mode == "conversational"
    assert config.memory.chunk_size == 1000
    assert config.spec_mode.max_retries == 3


def test_hive_config_load_explicit_path():
    """Test that load() uses explicit path when provided."""
    toml_content = """
default_mode = "spec"

[memory]
chunk_size = 2000
"""
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(toml_content)
        temp_path = Path(f.name)
    
    try:
        config = HiveTerminalConfig.load(config_path=temp_path)
        
        assert config.default_mode == "spec"
        assert config.memory.chunk_size == 2000
    finally:
        temp_path.unlink()


def test_hive_config_to_dict():
    """Test that to_dict() returns correct dictionary representation."""
    config = HiveTerminalConfig(
        default_mode="spec",
        memory=MemoryConfig(chunk_size=1500),
        spec_mode=SpecModeConfig(max_retries=5),
    )
    
    config_dict = config.to_dict()
    
    assert config_dict["default_mode"] == "spec"
    assert config_dict["memory"]["chunk_size"] == 1500
    assert config_dict["spec_mode"]["max_retries"] == 5
    assert isinstance(config_dict, dict)
    assert isinstance(config_dict["memory"], dict)
    assert isinstance(config_dict["spec_mode"], dict)


def test_hive_config_memory_path_expansion():
    """Test that memory database_path expands user home directory."""
    config = HiveTerminalConfig(
        memory=MemoryConfig(database_path="~/.hive_memory")
    )
    
    # Path should be expanded
    assert "~" not in config.memory.database_path
    assert str(Path.home()) in config.memory.database_path


def test_hive_config_spec_mode_path_expansion():
    """Test that spec_mode backup_dir expands user home directory."""
    config = HiveTerminalConfig(
        spec_mode=SpecModeConfig(backup_dir="~/.hive_backups")
    )
    
    # Path should be expanded
    assert "~" not in config.spec_mode.backup_dir
    assert str(Path.home()) in config.spec_mode.backup_dir


def test_hive_config_complete_toml():
    """Test loading a complete configuration file with all settings."""
    toml_content = """
default_mode = "spec"

[memory]
database_path = "./.test_memory"
embedding_model = "all-MiniLM-L6-v2"
chunk_size = 1200
chunk_overlap = 250
top_k_results = 8
similarity_threshold = 0.75

[spec_mode]
create_backups = true
backup_dir = "./.test_backups"
max_retries = 4
timeout_seconds = 450
"""
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(toml_content)
        temp_path = Path(f.name)
    
    try:
        config = HiveTerminalConfig.from_toml(temp_path)
        
        # Verify all settings
        assert config.default_mode == "spec"
        
        assert config.memory.embedding_model == "all-MiniLM-L6-v2"
        assert config.memory.chunk_size == 1200
        assert config.memory.chunk_overlap == 250
        assert config.memory.top_k_results == 8
        assert config.memory.similarity_threshold == 0.75
        
        assert config.spec_mode.create_backups is True
        assert config.spec_mode.max_retries == 4
        assert config.spec_mode.timeout_seconds == 450
        
        # Verify validation passes
        assert config.memory.chunk_overlap < config.memory.chunk_size
    finally:
        temp_path.unlink()
