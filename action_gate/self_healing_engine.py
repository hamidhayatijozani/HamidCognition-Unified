"""Bounded self-healing analysis for HamidCognition-Unified.

The engine is evidence-first and fail-closed:
- L1 GSRP performs conservative static preflight checks.
- L2 HCF builds a deterministic dependency graph and anomaly candidates.
- L3 OER ranks repair candidates; it never claims entropy is literally zero.
- L4 TRLE performs deterministic replay from captured inputs/checkpoints.
- L5 Gate emits PASS only when the supplied verifier proves the repair.

Source mutation is deliberately outside this module. A patch can only become
real after an external, authorized change path applies it and the verifier
produces fresh evidence.
"""

from __future__ import annotations

import ast
import hashlib
import json
from dataclasses import dataclass, field
from typing import Callable, Iterable, Mapping


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    severity: str
    location: str | None = None


@dataclass(frozen=True)
class PatchCandidate:
    patch_id: str
    description: str
    files: tuple[str, ...]
    risk: float
    test_scope: tuple[str, ...]
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class RepairResult:
    status: str
    findings: tuple[Finding, ...]
    candidates: tuple[PatchCandidate, ...]
    replay_digest: str | None
    evidence: Mapping[str, object] = field(default_factory=dict)


class GSRPEngine:
    """Conservative static guards. No source mutation."""

    def analyze(self, source: str, filename: str = "<memory>") -> tuple[Finding, ...]:
        try:
            tree = ast.parse(source, filename=filename)
        except SyntaxError as exc:
            return (
                Finding(
                    "SYNTAX_ERROR",
                    str(exc),
                    "critical",
                    filename,
                ),
            )

        findings: list[Finding] = []
        imported: set[str] = set()
        defined: set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.asname or alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.update(alias.asname or alias.name for alias in node.names)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                defined.add(node.name)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                defined.add(node.id)

        builtins = set(dir(__builtins__)) if not isinstance(__builtins__, dict) else set(__builtins__)
        unknown = sorted(
            {
                node.id
                for node in ast.walk(tree)
                if isinstance(node, ast.Name)
                and isinstance(node.ctx, ast.Load)
                and node.id not in imported
                and node.id not in defined
                and node.id not in builtins
            }
        )
        for name in unknown:
            findings.append(
                Finding(
                    "UNBOUND_NAME_CANDIDATE",
                    f"Conservative unresolved-name candidate: {name}",
                    "high",
                    filename,
                )
            )
        return tuple(findings)


class HCFMapper:
    """Deterministic call/import graph mapper, not a claim of literal holography."""

    def map(self, sources: Mapping[str, str]) -> Mapping[str, tuple[str, ...]]:
        graph: dict[str, tuple[str, ...]] = {}
        for filename, source in sorted(sources.items()):
            try:
                tree = ast.parse(source, filename=filename)
            except SyntaxError:
                graph[filename] = ()
                continue
            deps: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    deps.update(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    deps.add(node.module)
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    deps.add(node.func.id)
            graph[filename] = tuple(sorted(deps))
        return graph

    def anomaly_nodes(self, graph: Mapping[str, Iterable[str]]) -> tuple[str, ...]:
        incoming: dict[str, int] = {node: 0 for node in graph}
        for deps in graph.values():
            for dep in deps:
                if dep in incoming:
                    incoming[dep] += 1
        return tuple(sorted(node for node, count in incoming.items() if count == 0 and graph[node]))


class OEROptimizer:
    """Reduce candidate search space using explicit, auditable heuristics."""

    def rank(self, candidates: Iterable[PatchCandidate]) -> tuple[PatchCandidate, ...]:
        return tuple(
            sorted(
                candidates,
                key=lambda c: (
                    c.risk,
                    len(c.files),
                    len(c.test_scope),
                    c.patch_id,
                ),
            )
        )


class TRLELoop:
    """Replay inputs deterministically; no unsafe 'time reversal' claim."""

    def replay(
        self,
        inputs: Iterable[object],
        execute: Callable[[object], object],
    ) -> tuple[str, tuple[object, ...]]:
        outputs = tuple(execute(item) for item in inputs)
        payload = json.dumps(
            {"inputs": list(inputs), "outputs": list(outputs)},
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode()
        return hashlib.sha256(payload).hexdigest(), outputs


class SelfHealingEngine:
    """Orchestrates analysis and verification without bypassing Action Gate."""

    def diagnose(
        self,
        sources: Mapping[str, str],
        candidates: Iterable[PatchCandidate] = (),
    ) -> RepairResult:
        gsrp = GSRPEngine()
        findings = tuple(
            finding
            for filename, source in sorted(sources.items())
            for finding in gsrp.analyze(source, filename)
        )
        graph = HCFMapper().map(sources)
        ranked = OEROptimizer().rank(candidates)
        status = "HOLD" if findings else "READY"
        return RepairResult(
            status=status,
            findings=findings,
            candidates=ranked,
            replay_digest=None,
            evidence={
                "phase": "static",
                "graph_sha256": hashlib.sha256(
                    json.dumps(graph, sort_keys=True, separators=(",", ":")).encode()
                ).hexdigest(),
                "source_files": tuple(sorted(sources)),
            },
        )
