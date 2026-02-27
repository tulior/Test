---
name: python-development
description: Use this skill when creating, reviewing, or improving Python code, projects, and engineering workflows with production-grade quality standards.
---

# Python Development Skill

Apply this skill when the user requests Python implementation, refactoring, architecture guidance, debugging, or project setup.

## Outcomes
- Correct, readable, and maintainable Python code.
- Reproducible project setup.
- Quality gates: lint, type checks, and tests.
- Clear handoff notes for users/reviewers.

## Workflow

1. **Scope the task first**
   - Identify runtime constraints (Python version, framework, deployment target).
   - Confirm whether the request is script-level, package-level, or service-level.

2. **Choose implementation shape**
   - Prefer small, composable functions with explicit inputs/outputs.
   - Use `dataclass`/typed objects when domain data has structure.
   - Keep I/O at boundaries; keep core logic side-effect-light.

3. **Apply Python quality defaults**
   - Formatting/linting: `black` + `ruff` (or repo-standard tools).
   - Type safety: annotate public functions and complex internals.
   - Error handling: raise specific exceptions with actionable messages.

4. **Test intentionally**
   - Add/adjust `pytest` tests for new behavior and regressions.
   - Cover happy path + boundary + failure modes.
   - Mock only external boundaries (network, filesystem, clocks, randomness).

5. **Performance and reliability checks (as needed)**
   - For hotspots: profile before optimizing (`cProfile`, `timeit`).
   - For I/O-heavy flows: consider async or batching.
   - For CPU-heavy flows: consider multiprocessing/vectorization.

6. **Delivery checklist**
   - Code passes lint/type/tests.
   - Public interfaces are documented with concise docstrings.
   - Final summary includes changed files and validation commands.

## Design Rules
- Prefer clarity over clever one-liners.
- Use `pathlib` instead of raw path strings when possible.
- Keep functions focused; split when branching/complexity grows.
- Avoid hidden global state.
- Use dependency injection for external services to improve testability.

## Quick Patterns

### Function template
```python
def transform_records(records: list[dict[str, str]]) -> list[dict[str, str]]:
    """Normalize and validate incoming records."""
    if not records:
        return []
    return [normalize_record(r) for r in records]
```

### Error pattern
```python
class ConfigurationError(ValueError):
    """Raised when required application configuration is missing."""
```

### Test pattern
```python
def test_transform_records_empty_returns_empty_list() -> None:
    assert transform_records([]) == []
```

## When to escalate structure
- Introduce package modules when a single file exceeds clear ownership.
- Introduce service/repository layers when business rules and persistence intertwine.
- Introduce `pyproject.toml` tooling config when repeated command flags appear.
