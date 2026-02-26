# Contributing to HiveTerminal

Thank you for your interest in contributing to HiveTerminal! This document outlines our Git workflow, branching strategy, and development practices.

## Git Workflow

HiveTerminal follows a feature branch workflow with pull requests for all changes.

### Branch Naming Conventions

Use descriptive branch names that follow these patterns:

- **Feature branches**: `feature/short-description`
  - Example: `feature/memory-caching`, `feature/plan-templates`
- **Bug fixes**: `fix/short-description`
  - Example: `fix/memory-leak`, `fix/plan-parsing-error`
- **Documentation**: `docs/short-description`
  - Example: `docs/api-reference`, `docs/installation-guide`
- **Refactoring**: `refactor/short-description`
  - Example: `refactor/agent-loop`, `refactor/config-loading`
- **Performance**: `perf/short-description`
  - Example: `perf/embedding-generation`, `perf/query-optimization`

### Development Workflow

1. **Create a branch** from `main` for your work:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** with clear, focused commits

3. **Test your changes** thoroughly:
   ```bash
   # Run tests
   pytest tests/
   
   # Test manually with both modes
   hive --mode vibe
   hive --mode spec
   ```

4. **Push your branch** to the remote repository:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a pull request** against `main` with a clear description

6. **Address review feedback** by pushing additional commits

7. **Merge** once approved (squash merge preferred for clean history)

## Commit Message Guidelines

Write clear, descriptive commit messages that explain **what** and **why**, not just **how**.

### Format

```
<type>: <short summary> (max 50 chars)

<optional detailed description>

<optional footer with issue references>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring without behavior changes
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (dependencies, build config, etc.)

### Examples

**Good commits:**
```
feat: add memory caching for embeddings

Implement LRU cache for frequently accessed embeddings to reduce
API calls and improve retrieval performance. Cache size configurable
via memory.cache_size config option.

Closes #42
```

```
fix: handle empty files in code chunker

The chunker was crashing on empty files. Now returns empty list
and logs a warning instead.

Fixes #58
```

**Bad commits:**
```
update code
fix bug
changes
```

## Code Review Process

All changes must go through code review before merging.

### For Authors

- Keep PRs focused and reasonably sized (< 500 lines when possible)
- Write a clear PR description explaining the changes
- Link related issues
- Ensure all tests pass
- Respond to feedback promptly
- Mark conversations as resolved once addressed

### For Reviewers

- Review within 2 business days when possible
- Be constructive and specific in feedback
- Test the changes locally if significant
- Approve when satisfied, or request changes with clear guidance
- Use "Comment" for minor suggestions, "Request Changes" for blocking issues

### Review Checklist

- [ ] Code follows project style and conventions
- [ ] Tests are included and passing
- [ ] Documentation is updated if needed
- [ ] No breaking changes (or properly documented)
- [ ] Performance impact considered
- [ ] Error handling is appropriate
- [ ] Visual consistency maintained (for UI changes)

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/HyphaeAI/HiveTerminal.git
   cd hiveterminal
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Mac/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Set up API keys:**
   ```bash
   export OPENAI_API_KEY="your-key-here"
   # or
   export ANTHROPIC_API_KEY="your-key-here"
   ```

5. **Run tests:**
   ```bash
   pytest tests/
   ```

## Testing Guidelines

- Write tests for all new features
- Maintain or improve code coverage
- Test both conversational and spec-first modes
- Test with multiple AI providers when relevant
- Include edge cases and error conditions

## Code Style

- Follow PEP 8 for Python code
- Use type hints for all function signatures
- Keep functions focused and reasonably sized
- Add docstrings for public APIs
- Use meaningful variable names
- Comment complex logic

## Questions?

If you have questions about contributing, feel free to:
- Open an issue for discussion
- Ask in pull request comments
- Check existing documentation

Thank you for contributing to HiveTerminal!
