# Implementation Tasks: HiveTerminal

## Overview

This document outlines the implementation tasks for building HiveTerminal by forking and extending Mistral Vibe. The project is organized into phases, with each phase building on the previous one.

**Estimated Timeline:** 8 weeks
**Base:** Mistral Vibe (forked)
**Key Additions:** Dual-mode operation, Memory system, LiteLLM integration

---

## Phase 1: Foundation Setup (Week 1-2)

### 1. Repository Setup

- [x] 1.1 Fork Mistral Vibe repository
- [x] 1.2 Rename project to HiveTerminal
- [x] 1.3 Update package name in pyproject.toml
- [x] 1.4 Update entry point from `vibe` to `hive`
- [x] 1.5 Create development branch `hiveterminal-dev`
- [x] 1.6 Set up Git workflow and branching strategy
- [x] 1.7 Update README.md with HiveTerminal information
- [x] 1.8 Create CHANGELOG.md for tracking changes

### 2. LiteLLM Integration

- [x] 2.1 Remove mistralai dependency from pyproject.toml
- [x] 2.2 Add litellm>=1.0.0 to dependencies
- [x] 2.3 Create new backend adapter: `hiveterminal/core/llm/backend/litellm_backend.py`
  - [x] 2.3.1 Implement LiteLLMBackend class
  - [x] 2.3.2 Support OpenAI provider
  - [x] 2.3.3 Support Anthropic provider
  - [x] 2.3.4 Support Ollama provider
  - [x] 2.3.5 Implement streaming support
  - [x] 2.3.6 Implement token counting
- [x] 2.4 Update `vibe/core/llm/backend/factory.py` to include LiteLLM backend
- [x] 2.5 Update configuration schema in `vibe/core/config.py`
  - [x] 2.5.1 Add OpenAI provider configuration
  - [x] 2.5.2 Add Anthropic provider configuration
  - [x] 2.5.3 Add Ollama provider configuration
  - [x] 2.5.4 Update default models list
- [x] 2.6 Test LiteLLM with OpenAI API
- [x] 2.7 Test LiteLLM with Anthropic API
- [x] 2.8 Test LiteLLM with Ollama (local)
- [x] 2.9 Update error handling for multi-provider support
- [x] 2.10 Update API key validation for multiple providers

### 3. Configuration Extensions

- [x] 3.1 Add memory configuration section to config schema
  - [x] 3.1.1 Add `database_path` field
  - [x] 3.1.2 Add `embedding_model` field
  - [x] 3.1.3 Add `chunk_size` field
  - [x] 3.1.4 Add `chunk_overlap` field
  - [x] 3.1.5 Add `top_k_results` field
  - [x] 3.1.6 Add `similarity_threshold` field
- [x] 3.2 Add mode configuration section
  - [x] 3.2.1 Add `default_mode` field (conversational or spec)
- [x] 3.3 Add spec mode configuration section
  - [x] 3.3.1 Add `create_backups` field
  - [x] 3.3.2 Add `backup_dir` field
  - [x] 3.3.3 Add `max_retries` field
  - [x] 3.3.4 Add `timeout_seconds` field
- [x] 3.4 Create example configuration file `.hive_config.toml`
- [x] 3.5 Update configuration validation
- [x] 3.6 Test configuration loading and validation

---

## Phase 2: Memory System (Week 3-4)

### 4. Memory Manager Core

- [x] 4.1 Create `hiveterminal/memory/` directory
- [x] 4.2 Add ChromaDB dependency: `chromadb>=0.4.0`
- [x] 4.3 Add sentence-transformers dependency: `sentence-transformers>=2.2.0`
- [x] 4.4 Add tiktoken dependency: `tiktoken>=0.5.0`
- [x] 4.5 Create `hiveterminal/memory/manager.py`
  - [x] 4.5.1 Implement MemoryManager class
  - [x] 4.5.2 Implement `initialize_database()` method
  - [x] 4.5.3 Implement `get_database_stats()` method
  - [x] 4.5.4 Add configuration loading
  - [x] 4.5.5 Add error handling
- [x] 4.6 Create `hiveterminal/memory/models.py`
  - [x] 4.6.1 Define CodeChunk dataclass
  - [x] 4.6.2 Define MemoryConfig model
  - [x] 4.6.3 Define MemoryStats model

### 5. Code Chunking

- [x] 5.1 Create `hiveterminal/memory/chunker.py`
  - [x] 5.1.1 Implement CodeChunker class
  - [x] 5.1.2 Implement function-level chunking
  - [x] 5.1.3 Implement class-level chunking
  - [x] 5.1.4 Implement sliding window chunking
  - [x] 5.1.5 Add language detection
  - [x] 5.1.6 Add token counting per chunk
- [x] 5.2 Support Python chunking
- [x] 5.3 Support JavaScript/TypeScript chunking
- [x] 5.4 Support Java chunking
- [x] 5.5 Support Go chunking
- [x] 5.6 Support Rust chunking
- [x] 5.7 Add fallback for unsupported languages
- [x] 5.8 Test chunking with various file sizes
- [x] 5.9 Test chunking with edge cases (empty files, very large files)

### 6. Embedding and Storage

- [ ] 6.1 Implement embedding generation in MemoryManager
  - [x] 6.1.1 Add `generate_embeddings()` method
  - [x] 6.1.2 Support OpenAI embeddings (text-embedding-ada-002)
  - [x] 6.1.3 Support local embeddings (sentence-transformers)
  - [x] 6.1.4 Add batch embedding support
  - [x] 6.1.5 Add embedding caching
- [ ] 6.2 Implement storage in ChromaDB
  - [x] 6.2.1 Add `store_chunks()` method
  - [x] 6.2.2 Create ChromaDB collection schema
  - [x] 6.2.3 Store metadata (file_path, line numbers, timestamp)
  - [x] 6.2.4 Add duplicate detection
  - [x] 6.2.5 Add incremental updates
- [ ] 6.3 Implement file ingestion
  - [x] 6.3.1 Add `ingest_file()` method
  - [x] 6.3.2 Add `ingest_directory()` method
  - [x] 6.3.3 Add file watching for auto-ingestion
  - [x] 6.3.4 Add .gitignore respect
  - [x] 6.3.5 Add binary file detection and skipping
- [ ] 6.4 Test ingestion with sample codebases
- [ ] 6.5 Test incremental updates
- [ ] 6.6 Measure ingestion performance

### 7. Context Retrieval

- [ ] 7.1 Implement semantic search
  - [x] 7.1.1 Add `retrieve_context()` method
  - [x] 7.1.2 Implement similarity search with ChromaDB
  - [x] 7.1.3 Add top-k filtering
  - [x] 7.1.4 Add similarity threshold filtering
  - [x] 7.1.5 Add result ranking
- [ ] 7.2 Implement filtering
  - [x] 7.2.1 Add file type filtering
  - [x] 7.2.2 Add directory filtering
  - [x] 7.2.3 Add recency filtering
- [ ] 7.3 Implement result formatting
  - [x] 7.3.1 Add `format_results()` method
  - [x] 7.3.2 Format for injection into prompts
  - [x] 7.3.3 Add context window management
- [ ] 7.4 Test retrieval accuracy
- [ ] 7.5 Test retrieval performance
- [ ] 7.6 Optimize query performance

### 8. Memory Management Commands

- [x] 8.1 Implement `rebuild_database()` function
- [x] 8.2 Implement `display_memory_stats()` function
- [x] 8.3 Add `--rebuild-memory` CLI flag
- [x] 8.4 Add `--memory-stats` CLI flag
- [x] 8.5 Create memory statistics display with Rich tables
- [ ] 8.6 Test rebuild functionality
- [ ] 8.7 Test statistics display

---

## Phase 3: Dual-Mode Operation (Week 5-6)

### 9. Conversational Mode (Vibe Mode)

- [x] 9.1 Create `hiveterminal/agents/` directory
- [ ] 9.2 Create `hiveterminal/agents/vibe_agent.py`
  - [x] 9.2.1 Create VibeAgentLoop class extending Vibe's AgentLoop
  - [x] 9.2.2 Add memory_manager parameter to __init__
  - [x] 9.2.3 Override `_conversation_loop()` method
  - [x] 9.2.4 Implement context retrieval before LLM calls
  - [x] 9.2.5 Implement `_enhance_with_context()` method
  - [x] 9.2.6 Implement `_ingest_modified_files()` method
  - [x] 9.2.7 Add file change detection
- [ ] 9.3 Test conversational mode with memory integration
- [ ] 9.4 Test tool-by-tool approval workflow
- [ ] 9.5 Test context injection
- [ ] 9.6 Test file ingestion after modifications
- [ ] 9.7 Verify compatibility with Vibe's tool system
- [ ] 9.8 Verify compatibility with Vibe's MCP integration

### 10. Spec-First Mode

- [x] 10.1 Create `hiveterminal/agents/spec_agent.py`
  - [x] 10.1.1 Create SpecAgentLoop class extending Vibe's AgentLoop
  - [x] 10.1.2 Add memory_manager parameter to __init__
  - [x] 10.1.3 Implement `process_request()` method
  - [x] 10.1.4 Implement Phase 1: `phase1_generate_plan()`
  - [x] 10.1.5 Implement Phase 2: `phase2_get_approval()`
  - [x] 10.1.6 Implement Phase 3: `phase3_execute_plan()`
- [x] 10.2 Create plan generation system prompt
  - [x] 10.2.1 Create `hiveterminal/prompts/plan_generation.md`
  - [x] 10.2.2 Define plan format specification
  - [x] 10.2.3 Add context injection template
  - [x] 10.2.4 Add examples
- [x] 10.3 Implement plan parsing
  - [x] 10.3.1 Create `hiveterminal/agents/plan_parser.py`
  - [x] 10.3.2 Implement `parse_plan()` function
  - [x] 10.3.3 Extract file operations
  - [x] 10.3.4 Extract shell commands
  - [x] 10.3.5 Extract action order
  - [x] 10.3.6 Handle malformed plans
- [x] 10.4 Implement action execution
  - [x] 10.4.1 Create Action dataclass
  - [x] 10.4.2 Implement `execute_action()` method
  - [x] 10.4.3 Route to appropriate Vibe tools
  - [x] 10.4.4 Add error handling per action
  - [x] 10.4.5 Add progress tracking
- [x] 10.5 Create event types for spec mode
  - [x] 10.5.1 Create PlanGeneratedEvent
  - [x] 10.5.2 Create PlanApprovedEvent
  - [x] 10.5.3 Create PlanRejectedEvent
  - [x] 10.5.4 Create ActionStartEvent
  - [x] 10.5.5 Create ActionCompleteEvent
  - [x] 10.5.6 Create ActionErrorEvent
- [ ] 10.6 Test plan generation
- [ ] 10.7 Test plan parsing
- [ ] 10.8 Test action execution
- [ ] 10.9 Test error handling
- [ ] 10.10 Test file ingestion after execution

### 11. Mode Selection UI

- [x] 11.1 Create `hiveterminal/cli/mode_selection.py`
  - [x] 11.1.1 Implement `show_mode_selection()` function
  - [x] 11.1.2 Add Rich formatting for mode descriptions
  - [x] 11.1.3 Add conversational mode example
  - [x] 11.1.4 Add spec-first mode example
  - [x] 11.1.5 Add mode comparison
  - [x] 11.1.6 Implement user input prompt
  - [x] 11.1.7 Add input validation
- [ ] 11.2 Test mode selection UI
- [ ] 11.3 Test with different terminal sizes
- [ ] 11.4 Verify visual consistency with Vibe

### 12. CLI Integration

- [x] 12.1 Update `hiveterminal/cli/entrypoint.py`
  - [x] 12.1.1 Add `--mode` argument to parser
  - [x] 12.1.2 Add `--rebuild-memory` argument
  - [x] 12.1.3 Add `--memory-stats` argument
  - [x] 12.1.4 Update main() function
  - [x] 12.1.5 Add memory manager initialization
  - [x] 12.1.6 Add mode selection logic
  - [x] 12.1.7 Handle interactive mode selection
- [x] 12.2 Update `hiveterminal/cli/cli.py`
  - [x] 12.2.1 Add mode parameter to run_cli()
  - [x] 12.2.2 Add memory_manager parameter
  - [x] 12.2.3 Implement agent initialization based on mode
  - [x] 12.2.4 Add mode indicator in prompt
  - [x] 12.2.5 Implement `/mode` command for switching
- [ ] 12.3 Test CLI with --mode flag
- [ ] 12.4 Test CLI without mode flag (interactive selection)
- [ ] 12.5 Test mode switching with /mode command
- [ ] 12.6 Test memory commands

### 13. Mode Switching

- [-] 13.1 Implement runtime mode switching
  - [x] 13.1.1 Detect `/mode` command in user input
  - [x] 13.1.2 Show mode selection prompt
  - [ ] 13.1.3 Reinitialize agent with new mode
  - [ ] 13.1.4 Preserve conversation history
  - [x] 13.1.5 Preserve memory manager instance
- [x] 13.2 Add mode indicator to prompt
  - [x] 13.2.1 Show "[Conversational]" or "[Spec]" in dim text
  - [x] 13.2.2 Use Vibe's styling
- [ ] 13.3 Test mode switching
- [ ] 13.4 Test conversation history preservation
- [ ] 13.5 Test memory continuity across mode switches

---

## Phase 4: Testing and Polish (Week 7-8)

### 14. Unit Tests

- [ ] 14.1 Create test suite structure
  - [ ] 14.1.1 Create `tests/memory/` directory
  - [ ] 14.1.2 Create `tests/agents/` directory
  - [ ] 14.1.3 Create `tests/cli/` directory
- [ ] 14.2 Memory system tests
  - [ ] 14.2.1 Test MemoryManager initialization
  - [ ] 14.2.2 Test code chunking
  - [ ] 14.2.3 Test embedding generation
  - [ ] 14.2.4 Test storage and retrieval
  - [ ] 14.2.5 Test incremental updates
  - [ ] 14.2.6 Test database rebuild
- [ ] 14.3 Agent tests
  - [ ] 14.3.1 Test VibeAgentLoop context injection
  - [ ] 14.3.2 Test SpecAgentLoop plan generation
  - [ ] 14.3.3 Test plan parsing
  - [ ] 14.3.4 Test action execution
  - [ ] 14.3.5 Test error handling
- [ ] 14.4 CLI tests
  - [ ] 14.4.1 Test mode selection
  - [ ] 14.4.2 Test mode switching
  - [ ] 14.4.3 Test memory commands
  - [ ] 14.4.4 Test configuration loading
- [ ] 14.5 LiteLLM integration tests
  - [ ] 14.5.1 Test OpenAI provider
  - [ ] 14.5.2 Test Anthropic provider
  - [ ] 14.5.3 Test Ollama provider
  - [ ] 14.5.4 Test error handling

### 15. Integration Tests

- [ ] 15.1 End-to-end conversational mode test
- [ ] 15.2 End-to-end spec-first mode test
- [ ] 15.3 Test mode switching workflow
- [ ] 15.4 Test memory persistence across sessions
- [ ] 15.5 Test multi-provider switching
- [ ] 15.6 Test with real codebases
- [ ] 15.7 Test performance with large codebases
- [ ] 15.8 Test concurrent access to memory database

### 16. Documentation

- [ ] 16.1 Update README.md
  - [ ] 16.1.1 Add HiveTerminal overview
  - [ ] 16.1.2 Add installation instructions
  - [ ] 16.1.3 Add quick start guide
  - [ ] 16.1.4 Add mode selection guide
  - [ ] 16.1.5 Add memory system documentation
  - [ ] 16.1.6 Add configuration guide
  - [ ] 16.1.7 Add examples
- [ ] 16.2 Create ARCHITECTURE.md
  - [ ] 16.2.1 Document system architecture
  - [ ] 16.2.2 Document dual-mode design
  - [ ] 16.2.3 Document memory system
  - [ ] 16.2.4 Document differences from Vibe
- [ ] 16.3 Create CONTRIBUTING.md
- [ ] 16.4 Create API documentation
- [ ] 16.5 Create user guide
  - [ ] 16.5.1 When to use conversational mode
  - [ ] 16.5.2 When to use spec-first mode
  - [ ] 16.5.3 Memory system best practices
  - [ ] 16.5.4 Configuration examples
- [ ] 16.6 Add inline code documentation
- [ ] 16.7 Create migration guide from Vibe

### 17. Performance Optimization

- [ ] 17.1 Profile memory system performance
- [ ] 17.2 Optimize embedding generation
  - [ ] 17.2.1 Implement batch processing
  - [ ] 17.2.2 Add caching
  - [ ] 17.2.3 Add lazy loading
- [ ] 17.3 Optimize ChromaDB queries
  - [ ] 17.3.1 Add indexing
  - [ ] 17.3.2 Optimize similarity search
  - [ ] 17.3.3 Add query caching
- [ ] 17.4 Optimize code chunking
  - [ ] 17.4.1 Add parallel processing
  - [ ] 17.4.2 Optimize token counting
- [ ] 17.5 Profile agent loop performance
- [ ] 17.6 Optimize context injection
- [ ] 17.7 Measure and optimize startup time
- [ ] 17.8 Measure and optimize memory usage

### 18. Error Handling and Edge Cases

- [ ] 18.1 Handle missing API keys gracefully
- [ ] 18.2 Handle network errors
- [ ] 18.3 Handle corrupted memory database
- [ ] 18.4 Handle invalid configuration
- [ ] 18.5 Handle malformed plans
- [ ] 18.6 Handle file system errors
- [ ] 18.7 Handle large files
- [ ] 18.8 Handle binary files
- [ ] 18.9 Handle empty directories
- [ ] 18.10 Handle permission errors
- [ ] 18.11 Add comprehensive error messages
- [ ] 18.12 Add recovery suggestions

### 19. User Experience Polish

- [ ] 19.1 Verify visual consistency with Vibe
- [ ] 19.2 Test mode selection UX
- [ ] 19.3 Test mode switching UX
- [ ] 19.4 Add helpful error messages
- [ ] 19.5 Add progress indicators for long operations
- [ ] 19.6 Add confirmation prompts for destructive operations
- [ ] 19.7 Test with different terminal sizes
- [ ] 19.8 Test with different color schemes
- [ ] 19.9 Add keyboard shortcuts documentation
- [ ] 19.10 Test accessibility

### 20. Deployment Preparation

- [ ] 20.1 Create installation script
- [ ] 20.2 Test installation on macOS
- [ ] 20.3 Test installation on Linux
- [ ] 20.4 Create Docker image (optional)
- [ ] 20.5 Set up CI/CD pipeline
- [ ] 20.6 Create release checklist
- [ ] 20.7 Prepare release notes
- [ ] 20.8 Create demo video
- [ ] 20.9 Create example projects
- [ ] 20.10 Set up issue templates

---

## Optional Enhancements (Post-MVP)

### 21. Advanced Memory Features

- [ ]* 21.1 Implement memory compaction
- [ ]* 21.2 Add memory analytics dashboard
- [ ]* 21.3 Add memory export/import
- [ ]* 21.4 Add memory sharing via cloud
- [ ]* 21.5 Add memory versioning
- [ ]* 21.6 Add memory search UI

### 22. Advanced Spec Mode Features

- [ ]* 22.1 Add plan templates
- [ ]* 22.2 Add plan history
- [ ]* 22.3 Add plan comparison
- [ ]* 22.4 Add plan rollback
- [ ]* 22.5 Add plan scheduling
- [ ]* 22.6 Add plan collaboration

### 23. Additional Providers

- [ ]* 23.1 Add Google Gemini support
- [ ]* 23.2 Add Azure OpenAI support
- [ ]* 23.3 Add Cohere support
- [ ]* 23.4 Add local model support (llama.cpp)

### 24. IDE Integration

- [ ]* 24.1 Create VSCode extension
- [ ]* 24.2 Create JetBrains plugin
- [ ]* 24.3 Create Vim plugin
- [ ]* 24.4 Create Emacs integration

---

## Success Criteria

### Functional Requirements
- ✓ Dual-mode operation working (conversational and spec-first)
- ✓ Memory system functional (ingestion, retrieval, persistence)
- ✓ LiteLLM integration supporting OpenAI, Anthropic, Ollama
- ✓ Mode selection UI working
- ✓ Mode switching working
- ✓ All Vibe features preserved

### Performance Requirements
- ✓ Memory ingestion: >100 files/minute
- ✓ Context retrieval: <1 second
- ✓ Plan generation: <5 seconds
- ✓ Startup time: <3 seconds

### Quality Requirements
- ✓ All unit tests passing
- ✓ All integration tests passing
- ✓ Code coverage >80%
- ✓ No visual regressions from Vibe
- ✓ Documentation complete

### User Experience Requirements
- ✓ Mode selection clear and intuitive
- ✓ Examples helpful and accurate
- ✓ Error messages clear and actionable
- ✓ Visual consistency with Vibe maintained

---

## Notes

- Tasks marked with `*` are optional enhancements for post-MVP
- Each task should be tested before marking as complete
- Maintain compatibility with Vibe's existing features throughout
- Keep visual changes minimal - only add mode selection UI
- Document all changes from base Vibe
- Regular testing with real codebases recommended
