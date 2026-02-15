# HiveTerminal

HiveTerminal is a dual-mode terminal-based agentic IDE built on top of Mistral Vibe.

## Directory Structure

- `core/` - Core functionality and LLM backend integration
- `cli/` - Command-line interface and entry points
- `memory/` - Memory management system (ChromaDB-based Hive Mind)
- `agents/` - Agent implementations (Vibe Mode and Spec Mode)

## Overview

HiveTerminal extends Vibe with:
- **Dual-mode operation**: Conversational Mode (Vibe) and Spec-First Mode
- **Shared memory system**: ChromaDB-powered vector database for code context
- **Multi-provider support**: OpenAI, Anthropic, Ollama via LiteLLM

## Status

This is the extended implementation directory. The original Vibe codebase is preserved in the `Vibe/` directory for reference.
