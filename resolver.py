from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union
import unittest


Version = Tuple[int, int, int]
ConstraintRecord = Tuple[str, str]


@dataclass
class ResolveError:
    kind: str  # conflict | missing_package | circular_dependency
    message: str
    package: Optional[str] = None
    constraints: List[ConstraintRecord] = field(default_factory=list)
    dependency_chain: List[str] = field(default_factory=list)


@dataclass
class _State:
    constraints: Dict[str, List[ConstraintRecord]]
    selected: Dict[str, str]
    edges: Dict[str, set]


@dataclass
class _SearchResult:
    state: Optional[_State] = None
    error: Optional[ResolveError] = None


OPS = {
    "==": lambda a, b: a == b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
}


def _parse_version(version: str) -> Version:
    parts = version.split(".")
    if len(parts) not in (1, 2, 3):
        raise ValueError(f"Invalid version format: {version}")
    major = int(parts[0])
    minor = int(parts[1]) if len(parts) >= 2 else 0
    patch = int(parts[2]) if len(parts) == 3 else 0
    return major, minor, patch


def _parse_constraint(constraint: str) -> List[Tuple[str, Version]]:
    constraint = constraint.strip()
    if not constraint:
        return []

    out: List[Tuple[str, Version]] = []
    for part in constraint.split(","):
        part = part.strip()
        for op in (">=", "<=", "==", ">", "<"):
            if part.startswith(op):
                out.append((op, _parse_version(part[len(op) :])))
                break
        else:
            raise ValueError(f"Invalid constraint: {part}")
    return out


def _satisfies(version: str, constraints: List[str]) -> bool:
    v = _parse_version(version)
    for raw in constraints:
        for op, rhs in _parse_constraint(raw):
            if not OPS[op](v, rhs):
                return False
    return True


def _find_path(edges: Dict[str, set], start: str, target: str) -> Optional[List[str]]:
    stack: List[Tuple[str, List[str]]] = [(start, [start])]
    seen = set()
    while stack:
        node, path = stack.pop()
        if node == target:
            return path
        if node in seen:
            continue
        seen.add(node)
        for nxt in sorted(edges.get(node, set()), reverse=True):
            stack.append((nxt, path + [nxt]))
    return None


def _clone_state(state: _State) -> _State:
    return _State(
        constraints={k: list(v) for k, v in state.constraints.items()},
        selected=dict(state.selected),
        edges={k: set(v) for k, v in state.edges.items()},
    )


def resolve(
    packages: dict, requests: List[Tuple[str, Optional[str]]]
) -> Union[Dict[str, str], ResolveError]:
    state = _State(constraints={}, selected={}, edges={})

    for name, maybe_constraint in requests:
        state.constraints.setdefault(name, [])
        if maybe_constraint:
            state.constraints[name].append((maybe_constraint, "root request"))

    result = _search(packages, state)
    if result.error:
        return result.error

    assert result.state is not None
    return result.state.selected


def _search(packages: dict, state: _State) -> _SearchResult:
    for pkg, records in state.constraints.items():
        if pkg in state.selected:
            selected_ver = state.selected[pkg]
            reqs = [c for c, _ in records]
            if not _satisfies(selected_ver, reqs):
                return _SearchResult(
                    error=ResolveError(
                        kind="conflict",
                        message=f"Selected version {pkg}=={selected_ver} violates constraints.",
                        package=pkg,
                        constraints=records,
                    )
                )

    undecided = [pkg for pkg in state.constraints if pkg not in state.selected]
    if not undecided:
        return _SearchResult(state=state)

    best_pkg = None
    best_domain: Optional[List[str]] = None

    for pkg in sorted(undecided):
        if pkg not in packages:
            return _SearchResult(
                error=ResolveError(
                    kind="missing_package",
                    message=f"Package '{pkg}' was required but is not available.",
                    package=pkg,
                    constraints=state.constraints.get(pkg, []),
                )
            )

        all_constraints = [c for c, _ in state.constraints[pkg]]
        domain = [
            v
            for v in sorted(packages[pkg].keys(), key=_parse_version, reverse=True)
            if _satisfies(v, all_constraints)
        ]

        if not domain:
            return _SearchResult(
                error=ResolveError(
                    kind="conflict",
                    message=f"No versions of '{pkg}' satisfy all constraints.",
                    package=pkg,
                    constraints=state.constraints[pkg],
                )
            )

        if best_domain is None or len(domain) < len(best_domain) or (
            len(domain) == len(best_domain) and pkg < best_pkg
        ):
            best_pkg = pkg
            best_domain = domain

    assert best_pkg is not None and best_domain is not None

    last_error: Optional[ResolveError] = None

    for version in best_domain:
        next_state = _clone_state(state)
        next_state.selected[best_pkg] = version

        dependencies = packages[best_pkg][version].get("dependencies", [])

        dep_error: Optional[ResolveError] = None
        for dep_name, dep_constraint in dependencies:
            next_state.constraints.setdefault(dep_name, [])
            next_state.constraints[dep_name].append(
                (dep_constraint, f"{best_pkg}=={version}")
            )

            next_state.edges.setdefault(best_pkg, set())
            next_state.edges.setdefault(dep_name, set())

            path_back = _find_path(next_state.edges, dep_name, best_pkg)
            if path_back is not None:
                cycle = [best_pkg] + path_back
                dep_error = ResolveError(
                    kind="circular_dependency",
                    message="Circular dependency detected.",
                    package=dep_name,
                    dependency_chain=cycle,
                )
                break

            next_state.edges[best_pkg].add(dep_name)

        if dep_error:
            last_error = dep_error
            continue

        recursive = _search(packages, next_state)
        if recursive.state is not None:
            return recursive
        last_error = recursive.error

    return _SearchResult(error=last_error)


class ResolverTests(unittest.TestCase):
    def test_happy_path_prefers_highest(self):
        packages = {
            "A": {
                "1.0.0": {"dependencies": [("B", ">=1.0")]},
            },
            "B": {
                "1.0.0": {"dependencies": []},
                "1.2.0": {"dependencies": []},
                "2.0.0": {"dependencies": []},
            },
        }

        out = resolve(packages, [("A", None), ("B", "<2")])
        self.assertEqual(out, {"A": "1.0.0", "B": "1.2.0"})

    def test_version_conflict(self):
        packages = {
            "A": {
                "1.0.0": {"dependencies": [("B", "==1.0.0")]},
            },
            "C": {
                "1.0.0": {"dependencies": [("B", "==2.0.0")]},
            },
            "B": {
                "1.0.0": {"dependencies": []},
                "2.0.0": {"dependencies": []},
            },
        }

        out = resolve(packages, [("A", None), ("C", None)])
        self.assertIsInstance(out, ResolveError)
        assert isinstance(out, ResolveError)
        self.assertEqual(out.kind, "conflict")
        self.assertEqual(out.package, "B")

    def test_missing_dependency(self):
        packages = {
            "A": {
                "1.0.0": {"dependencies": [("B", ">=1.0.0")]},
            }
        }

        out = resolve(packages, [("A", None)])
        self.assertIsInstance(out, ResolveError)
        assert isinstance(out, ResolveError)
        self.assertEqual(out.kind, "missing_package")
        self.assertEqual(out.package, "B")

    def test_circular_dependency(self):
        packages = {
            "A": {
                "1.0.0": {"dependencies": [("B", ">=1.0.0")]},
            },
            "B": {
                "1.0.0": {"dependencies": [("A", ">=1.0.0")]},
            },
        }

        out = resolve(packages, [("A", None)])
        self.assertIsInstance(out, ResolveError)
        assert isinstance(out, ResolveError)
        self.assertEqual(out.kind, "circular_dependency")
        self.assertGreaterEqual(len(out.dependency_chain), 3)

    def test_diamond_conflict(self):
        packages = {
            "A": {
                "1.0.0": {"dependencies": [("B", ">=1.0.0"), ("C", ">=1.0.0")]},
            },
            "B": {
                "1.0.0": {"dependencies": [("D", "==1.0.0")]},
            },
            "C": {
                "1.0.0": {"dependencies": [("D", "==2.0.0")]},
            },
            "D": {
                "1.0.0": {"dependencies": []},
                "2.0.0": {"dependencies": []},
            },
        }

        out = resolve(packages, [("A", None)])
        self.assertIsInstance(out, ResolveError)
        assert isinstance(out, ResolveError)
        self.assertEqual(out.kind, "conflict")
        self.assertEqual(out.package, "D")


if __name__ == "__main__":
    unittest.main()
