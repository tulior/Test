---
name: python-dependency-resolver
description: Design, implement, and validate Python package dependency resolvers (version solving, constraint propagation, backtracking, lockfile generation, and conflict diagnostics). Use when building or improving tools like pip/poetry/uv-style resolvers, debugging unsatisfiable dependency sets, or adding reproducible resolution workflows.
---

# Python Dependency Resolver Skill

Use this skill to build or improve a Python package dependency resolver that is correct, explainable, and reproducible.

## 1) Define Resolution Contract First
- Specify target semantics before coding:
  - Inputs: root requirements, constraints, index metadata, environment markers, extras, python version, platform tags.
  - Outputs: resolved set (or UNSAT), lock data, and human-readable explanation.
  - Invariants: every selected version satisfies all active constraints and markers.
- Choose strategy explicitly:
  - Default: complete backtracking resolver with pruning and deterministic tie-breaking.
  - Optional: SAT/SMT encoding if ecosystem scale or feature set demands it.
- Freeze deterministic rules:
  - Stable package ordering.
  - Stable candidate ordering.
  - Repeatable outcome for identical inputs.

## 2) Model the Problem Precisely
- Represent dependency state with immutable records where possible:
  - `Requirement(name, specifier, markers, extras, source)`
  - `Candidate(name, version, dependencies, yanked, requires_python)`
  - `Assignment(name -> candidate)`
- Normalize package names (PEP 503 style) and specifiers once at ingestion.
- Evaluate markers against an explicit environment object, not ambient process state.
- Separate hard constraints (must satisfy) from preferences (latest, non-yanked, wheel-first).

## 3) Implement Core Solving Loop
- Maintain three structures:
  - Decision stack (selected candidates and decision level).
  - Pending requirements queue.
  - Constraint store by package.
- Resolution loop:
  1. Propagate newly added requirements into constraint store.
  2. Detect immediate conflicts (empty candidate domain).
  3. Pick next undecided package using fail-first heuristic (smallest viable domain).
  4. Try candidates in deterministic preference order.
  5. On conflict, backtrack to latest decision level with unexplored candidates.
- Record conflict causes as structured reason chains to produce actionable diagnostics.

## 4) Pruning and Performance Rules
- Prune aggressively but soundly:
  - Exclude candidates failing specifier/marker/python checks early.
  - Use yanked releases only as last resort unless explicitly requested.
  - Memoize incompatibility checks `(package, version, constraint-set hash)`.
- Cache index lookups and metadata parsing.
- Batch network requests where protocol supports it.
- Enforce bounded retries and timeouts for remote sources.

## 5) Conflict Explanation Requirements
- When UNSAT, return:
  - Minimal conflicting requirement chain if available.
  - Concrete package/version constraints that clash.
  - Suggested user actions (relax pin, drop extra, change python version).
- Never emit only “resolution failed”; always include at least one concrete contradiction.

## 6) Lockfile and Reproducibility
- Generate lock output with:
  - Exact version pins.
  - Source/index provenance.
  - Hashes/checksums when available.
  - Marker-conditional entries as needed.
- Support update policies:
  - Full refresh.
  - Targeted package update with transitive minimization.
- Guarantee that install from lock re-validates hashes and markers.

## 7) Testing Standard (Required)
- Add tests for:
  - Simple satisfiable graphs.
  - Diamond dependencies.
  - Extras and environment markers.
  - Requires-Python incompatibilities.
  - Yanked/pre-release handling.
  - Unsatisfiable cases with explanation assertions.
- Add property-style checks where feasible:
  - Every resolved candidate satisfies accumulated constraints.
  - Determinism across repeated runs.
- Add regression tests for every discovered resolver bug.

## 8) Implementation Checklist
- Keep resolver core isolated from transport/index adapters.
- Expose pure function entrypoint for testability:
  - `resolve(requirements, environment, provider, policy) -> ResolutionResult`
- Include structured logging hooks by decision level.
- Measure:
  - Solve time distribution.
  - Backtrack count.
  - Metadata fetch count/cache hit rate.

## 9) Preferred Default Heuristics
- Prefer installed/locked candidate first when policy is “minimal change”.
- Otherwise prefer newest non-yanked stable release.
- Defer prereleases unless root requirement or policy opts in.
- Break ties lexicographically by normalized name then version ordering for determinism.

## 10) Anti-Patterns to Avoid
- Read environment markers from global interpreter state during solving.
- Mix I/O and solving logic in the same unit.
- Use non-deterministic iteration over dict/set when choosing decisions.
- Drop conflict context during backtracking.
- Emit lockfiles without provenance or integrity data.

## 11) Minimal Delivery Template
When asked to implement a resolver feature, produce:
1. Brief contract statement (inputs, outputs, invariants).
2. Data model changes.
3. Solver algorithm change (with backtracking/conflict impact).
4. Test additions (SAT + UNSAT path).
5. Performance impact note.
