# Python Skills Matrix (Optimal Baseline)

## 1) Core Language Mastery
- **Syntax & semantics:** data types, mutability, truthiness, slicing, unpacking, comprehensions.
- **Control flow:** loops, conditionals, iterators, generators, context managers.
- **Functions:** args/kwargs, decorators, closures, higher-order patterns.
- **OOP:** classes, inheritance, composition, dunder methods, dataclasses.
- **Typing:** type hints, `typing` module, protocols, generics, `mypy`-friendly design.
- **Error handling:** exception hierarchy, custom exceptions, robust failure modes.

## 2) Pythonic Design & Maintainability
- Write clear, small, testable functions with single responsibility.
- Prefer readability over cleverness (PEP 8 + practical consistency).
- Use idioms (`enumerate`, `zip`, `pathlib`, `collections`, `itertools`).
- Design modules/packages with stable public APIs.
- Apply SOLID pragmatically in Python contexts.

## 3) Tooling & Workflow
- **Environments:** `venv`, reproducible dependency management.
- **Packaging:** `pyproject.toml`, build backends, versioning, publishing basics.
- **Lint/format:** `ruff`/`flake8`, `black`, import sorting.
- **Type checking:** `mypy` or pyright in CI.
- **Debugging & profiling:** `pdb`, logging, `cProfile`, `timeit`, memory tools.
- **Automation:** Makefile/task runners, pre-commit hooks.

## 4) Testing & Quality
- **Unit/integration tests:** `pytest` fixtures, parametrization, mocks.
- **Test design:** boundary cases, property-style assertions, regression tests.
- **Coverage:** meaningful coverage with critical-path prioritization.
- **Quality gates:** lint + type + tests in CI before merge.

## 5) Data Structures, Algorithms, and Performance
- Complexity awareness for common operations.
- Correct choice of list/dict/set/tuple/deque/heap.
- Efficient I/O and streaming for large datasets.
- Vectorization and batching when appropriate.

## 6) Concurrency & Parallelism
- **Async I/O:** `asyncio`, tasks, cancellation, timeouts, backpressure.
- **Parallel CPU:** multiprocessing, process pools.
- **Threading:** safe usage for I/O-bound scenarios.
- Understand GIL implications and select model accordingly.

## 7) Data & Persistence
- SQL fundamentals and ORM/query-builder tradeoffs.
- Transaction handling, migrations, indexing basics.
- Serialization (`json`, `pydantic`, schema validation).
- Caching patterns and consistency considerations.

## 8) API and Service Development
- Build REST/async services (FastAPI/Flask/Django as context requires).
- Input validation, authn/authz basics, pagination, idempotency.
- Observability: structured logging, metrics, tracing hooks.
- Resilience: retries, circuit breakers, graceful degradation.

## 9) Security and Reliability
- Secrets handling and configuration hygiene.
- Dependency and supply-chain awareness.
- Safe file/network handling and input sanitization.
- Incident-ready logging and deterministic error responses.

## 10) Domain Specialization (Pick One or More)
- **Backend web:** APIs, queues, background jobs.
- **Data/ML:** pandas/polars, notebooks-to-production practices.
- **Automation/DevOps:** scripting, infra glue, CI/CD tooling.
- **Scientific computing:** NumPy/SciPy optimization patterns.

## 11) Collaboration Skills
- Code review quality (clarity, risk spotting, constructive feedback).
- Writing design notes and ADR-style decisions.
- Estimation, decomposition, and delivery predictability.

## 12) Practical Progression Roadmap
1. **Foundation (2–4 weeks):** core syntax, functions, OOP, error handling.
2. **Professional baseline (4–8 weeks):** packaging, testing, lint/type checks, CI.
3. **Production readiness (4–8 weeks):** APIs, persistence, observability, security.
4. **Specialization (ongoing):** pick one domain and build portfolio projects.

## 13) Definition of “Python-Proficient”
A Python-proficient engineer can design, implement, test, and operate maintainable Python services or applications with reliable quality gates (lint/type/tests), sound performance decisions, and clear team collaboration.
