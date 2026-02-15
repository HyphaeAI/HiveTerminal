# Changelog

All notable changes to HiveTerminal will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Dual-mode operation: Conversational Mode (Vibe Mode) and Spec-First Mode
- Shared memory system (Hive Mind) powered by ChromaDB for intelligent code context retrieval
- LiteLLM integration supporting multiple AI providers (OpenAI, Anthropic, Ollama)
- Interactive mode selection prompt with clear examples and use cases
- Memory management commands (`--rebuild-memory`, `--memory-stats`)
- Configuration extensions for memory system, mode selection, and spec-first workflow
- Context-aware code retrieval using semantic similarity search
- Automatic code ingestion and embedding generation for modified files
- Three-phase workflow for Spec-First Mode (Plan → Approve → Execute)
- Runtime mode switching via `/mode` command
- Git-shareable vector database stored in `./.hive_memory`

### Changed
- Forked from Mistral Vibe and renamed to HiveTerminal
- Entry point changed from `vibe` to `hive`
- Replaced Mistral AI backend with LiteLLM for multi-provider support
- Extended configuration schema to support memory and dual-mode settings

### Notes
- Based on Mistral Vibe with extensions for dual-mode operation and memory capabilities
- Maintains full compatibility with Vibe's UI/UX and existing features
- All Vibe features (MCP integration, skills, tools) remain functional

## [1.0.0] - TBD

Initial release of HiveTerminal.

[Unreleased]: https://github.com/yourusername/hiveterminal/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yourusername/hiveterminal/releases/tag/v1.0.0
