"""Local Brain mode for HiveTerminal.

A lightweight, privacy-focused agent using local Ollama models
with JSON-based tool calling optimized for 8GB RAM systems.
"""

from .agent import run_local_agent

__all__ = ["run_local_agent"]
