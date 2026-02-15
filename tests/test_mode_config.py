"""Tests for mode and spec mode configuration."""

import pytest
from pydantic import ValidationError

from hiveterminal.core.config import ModeConfig, SpecModeConfig


# ModeConfig Tests

def test_mode_config_defaults():
    """Test that ModeConfig has correct default values."""
    config = ModeConfig()
    
    assert config.default_mode == "conversational"


def test_mode_config_conversational():
    """Test that ModeConfig accepts 'conversational' mode."""
    config = ModeConfig(default_mode="conversational")
    assert config.default_mode == "conversational"


def test_mode_config_spec():
    """Test that ModeConfig accepts 'spec' mode."""
    config = ModeConfig(default_mode="spec")
    assert config.default_mode == "spec"


def test_mode_config_invalid_mode():
    """Test that ModeConfig rejects invalid modes."""
    with pytest.raises(ValidationError) as exc_info:
        ModeConfig(default_mode="invalid")
    
    assert "default_mode must be one of" in str(exc_info.value)


def test_mode_config_case_sensitive():
    """Test that mode validation is case-sensitive."""
    # These should fail because they're not lowercase
    with pytest.raises(ValidationError):
        ModeConfig(default_mode="Conversational")
    
    with pytest.raises(ValidationError):
        ModeConfig(default_mode="SPEC")


# SpecModeConfig Tests

def test_spec_mode_config_defaults():
    """Test that SpecModeConfig has correct default values."""
    config = SpecModeConfig()
    
    assert config.create_backups is True
    assert config.backup_dir.endswith(".hive_backups")
    assert config.max_retries == 3
    assert config.timeout_seconds == 300


def test_spec_mode_config_custom_values():
    """Test that SpecModeConfig accepts custom values."""
    config = SpecModeConfig(
        create_backups=False,
        backup_dir="/custom/backups",
        max_retries=5,
        timeout_seconds=600
    )
    
    assert config.create_backups is False
    assert config.backup_dir.endswith("backups")
    assert config.max_retries == 5
    assert config.timeout_seconds == 600


def test_spec_mode_config_create_backups_boolean():
    """Test that create_backups accepts boolean values."""
    config_true = SpecModeConfig(create_backups=True)
    assert config_true.create_backups is True
    
    config_false = SpecModeConfig(create_backups=False)
    assert config_false.create_backups is False


def test_spec_mode_config_max_retries_validation():
    """Test that max_retries must be non-negative and within limits."""
    # Valid retries
    config = SpecModeConfig(max_retries=0)
    assert config.max_retries == 0
    
    config = SpecModeConfig(max_retries=5)
    assert config.max_retries == 5
    
    config = SpecModeConfig(max_retries=10)
    assert config.max_retries == 10
    
    # Invalid: negative
    with pytest.raises(ValidationError):
        SpecModeConfig(max_retries=-1)
    
    # Invalid: too large
    with pytest.raises(ValidationError):
        SpecModeConfig(max_retries=11)


def test_spec_mode_config_timeout_validation():
    """Test that timeout_seconds must be positive and within limits."""
    # Valid timeouts
    config = SpecModeConfig(timeout_seconds=1)
    assert config.timeout_seconds == 1
    
    config = SpecModeConfig(timeout_seconds=300)
    assert config.timeout_seconds == 300
    
    config = SpecModeConfig(timeout_seconds=3600)
    assert config.timeout_seconds == 3600
    
    # Invalid: zero
    with pytest.raises(ValidationError):
        SpecModeConfig(timeout_seconds=0)
    
    # Invalid: negative
    with pytest.raises(ValidationError):
        SpecModeConfig(timeout_seconds=-100)
    
    # Invalid: too large
    with pytest.raises(ValidationError):
        SpecModeConfig(timeout_seconds=3601)


def test_spec_mode_config_path_expansion():
    """Test that backup_dir expands user home directory."""
    config = SpecModeConfig(backup_dir="~/.hive_backups")
    assert "~" not in config.backup_dir
    assert config.backup_dir.endswith(".hive_backups")


def test_spec_mode_config_all_fields():
    """Test that all fields can be set together."""
    config = SpecModeConfig(
        create_backups=True,
        backup_dir="/tmp/backups",
        max_retries=2,
        timeout_seconds=120
    )
    
    assert config.create_backups is True
    assert config.backup_dir.endswith("backups")
    assert config.max_retries == 2
    assert config.timeout_seconds == 120
