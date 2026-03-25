# CBSE Question Paper Generator - Coding Agent Guide

Guide for opencode coding agents working on this CBSE Question Paper Generator project.

## Build & Test Commands

**Run all tests:**
```bash
uv run pytest tests/ -v
```

**Run single test:**
```bash
uv run pytest tests/test_file.py::test_function_name -v
```

**Run domain-specific tests:**
```bash
./run_tests.sh [all|cache|question_generation|blueprint_validation|curriculum_search]
```

**Linting:**
```bash
uv run ruff check .
```

**Format code:**
```bash
uv run black . && uv run ruff check --fix .
```

**Type checking:**
```bash
uv run mypy .
```

**Run the application:**
```bash
uv run python src/run.py "Generate Class 10 Mathematics question paper"
```

## Code Style Guidelines

**Line Length:** 100 characters (enforced by black and ruff)

**Imports:**
- Order: stdlib → third-party → local
- Sorted alphabetically within each group
- Use absolute imports for local modules
- Example:
```python
import json
from pathlib import Path
from typing import Dict, Optional

from langchain_core.tools import tool

from src.config import settings
```

**Type Hints:**
- Required for all function parameters and return types
- Use `typing` module: `Dict`, `List`, `Optional`, `Any`
- Example: `def process_data(data: Dict[str, Any]) -> Optional[str]:`

**Naming Conventions:**
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Tool names: `snake_case_with_tool_suffix`

**Docstrings:**
- Google-style format
- Include Args and Returns sections
- First line should be a brief description

**Error Handling:**
- Use try/except with specific exceptions
- Provide descriptive error messages
- Return error info in dict format for tools
- Never silently swallow exceptions

**Tools Pattern:**
- One tool per file in `src/{module}/tool.py`
- Use `@tool` decorator from `langchain_core.tools`
- Return structured dict with success/error info
- Include type hints and docstrings

## Project Structure

```
src/
├── {module}/           # One directory per feature
│   └── tool.py         # Tool implementation
├── skills/             # Subagent skill definitions
│   └── {subagent}/
│       └── SKILL.md
├── config/            # Configuration
└── run.py             # Main entry point

tests/
├── test_{domain}/     # Domain-specific tests
└── conftest.py        # Shared fixtures
```

## Pre-commit Checklist

Before committing:
- [ ] Run linting: `uv run ruff check .`
- [ ] Run type check: `uv run mypy .`
- [ ] Verify no trailing whitespace
- [ ] Ensure docstrings are complete

## Common Tasks

**Add a new tool:**
1. Create `src/{module}/tool.py`
2. Implement using `@tool` decorator
3. Add tests in `tests/test_{module}/`
4. Run tests and linting

**Update an existing tool:**
1. Modify `src/{module}/tool.py`
2. Update corresponding tests
3. Run specific test: `uv run pytest tests/test_{module}/ -v`
4. Run full test suite before commit

**Add a new skill:**
1. Create `src/skills/{skill-name}/SKILL.md`
2. Follow agentskills.io specification format
3. Reference in appropriate subagent

## Environment

- Python: 3.11, 3.12, or 3.13
- Package manager: `uv`
- Virtual environment: `.venv/`
- Environment variables: `.env` (copy from `.env.example`)

## Important Notes

- **Do NOT commit** unless explicitly asked
- **Do NOT push** to remote unless explicitly asked
- **Always run tests** after making changes
- **Follow existing patterns** when adding new code
- **Check SKILL.md files** for subagent-specific requirements
- **Use uv** instead of pip for all package operations
