"""Tests for memory configuration."""

import pytest
from pydantic import ValidationError

from hiveterminal.core.config import MemoryConfig


def test_memory_config_defaults():
    """Test that MemoryConfig has correct default values."""
    config = MemoryConfig()
    
    assert config.database_path.endswith(".hive_memory")
    assert config.embedding_model == "text-embedding-ada-002"
    assert config.chunk_size == 1000
    assert config.chunk_overlap == 200
    assert config.top_k_results == 5
    assert config.similarity_threshold == 0.7


def test_memory_config_custom_values():
    """Test that MemoryConfig accepts custom values."""
    config = MemoryConfig(
        database_path="/custom/path/.hive_memory",
        embedding_model="custom-model",
        chunk_size=500,
        chunk_overlap=100,
        top_k_results=10,
        similarity_threshold=0.8
    )
    
    assert config.database_path.endswith(".hive_memory")
    assert config.embedding_model == "custom-model"
    assert config.chunk_size == 500
    assert config.chunk_overlap == 100
    assert config.top_k_results == 10
    assert config.similarity_threshold == 0.8


def test_memory_config_chunk_size_validation():
    """Test that chunk_size must be positive and within limits."""
    # Valid chunk size
    config = MemoryConfig(chunk_size=1000)
    assert config.chunk_size == 1000
    
    # Invalid: zero
    with pytest.raises(ValidationError):
        MemoryConfig(chunk_size=0)
    
    # Invalid: negative
    with pytest.raises(ValidationError):
        MemoryConfig(chunk_size=-100)
    
    # Invalid: too large
    with pytest.raises(ValidationError):
        MemoryConfig(chunk_size=10000)


def test_memory_config_chunk_overlap_validation():
    """Test that chunk_overlap must be non-negative and less than chunk_size."""
    # Valid overlap
    config = MemoryConfig(chunk_size=1000, chunk_overlap=200)
    assert config.chunk_overlap == 200
    
    # Invalid: negative
    with pytest.raises(ValidationError):
        MemoryConfig(chunk_overlap=-50)
    
    # Invalid: greater than or equal to chunk_size
    with pytest.raises(ValidationError):
        MemoryConfig(chunk_size=500, chunk_overlap=500)
    
    with pytest.raises(ValidationError):
        MemoryConfig(chunk_size=500, chunk_overlap=600)


def test_memory_config_top_k_validation():
    """Test that top_k_results must be positive and within limits."""
    # Valid top_k
    config = MemoryConfig(top_k_results=5)
    assert config.top_k_results == 5
    
    # Invalid: zero
    with pytest.raises(ValidationError):
        MemoryConfig(top_k_results=0)
    
    # Invalid: negative
    with pytest.raises(ValidationError):
        MemoryConfig(top_k_results=-5)
    
    # Invalid: too large
    with pytest.raises(ValidationError):
        MemoryConfig(top_k_results=100)


def test_memory_config_similarity_threshold_validation():
    """Test that similarity_threshold must be between 0.0 and 1.0."""
    # Valid thresholds
    config = MemoryConfig(similarity_threshold=0.0)
    assert config.similarity_threshold == 0.0
    
    config = MemoryConfig(similarity_threshold=0.5)
    assert config.similarity_threshold == 0.5
    
    config = MemoryConfig(similarity_threshold=1.0)
    assert config.similarity_threshold == 1.0
    
    # Invalid: negative
    with pytest.raises(ValidationError):
        MemoryConfig(similarity_threshold=-0.1)
    
    # Invalid: greater than 1.0
    with pytest.raises(ValidationError):
        MemoryConfig(similarity_threshold=1.5)


def test_memory_config_path_expansion():
    """Test that database_path expands user home directory."""
    config = MemoryConfig(database_path="~/.hive_memory")
    assert "~" not in config.database_path
    assert config.database_path.endswith(".hive_memory")
