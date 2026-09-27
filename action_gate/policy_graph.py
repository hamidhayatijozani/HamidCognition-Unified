from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from enterprise_models import EnterpriseArchitectureError


@dataclass(frozen=True)
class PolicyGraph:
    """Deterministic authorization graph used at the enforcement boundary."""
    edges: frozenset[tuple[str, str, str]]

    @classmethod
    def from_edges(cls, edges: Iterable[tuple[str, str, str]]) -> "PolicyGraph":
        return cls(frozenset((str(a), str(b), str(c)) for a, b, c in edges))

    def _has(self, source: str, relation: str, target: str) -> bool:
        return (source, relation, target) in self.edges

    def validate(self, *, tenant_id: str, agent_id: str, policy_id: str,
                 tool_id: str, authority_id: str) -> tuple[str, ...]:
        checks = (
            (f"tenant:{tenant_id}", "governs", f"policy:{policy_id}", "tenant_policy_edge_missing"),
            (f"agent:{agent_id}", "uses", f"policy:{policy_id}", "agent_policy_edge_missing"),
            (f"policy:{policy_id}", "binds", f"tool:{tool_id}", "policy_tool_edge_missing"),
            (f"policy:{policy_id}", "issues", f"authority:{authority_id}", "policy_authority_edge_missing"),
        )
        for source, relation, target, error in checks:
            if not self._has(source, relation, target):
                raise EnterpriseArchitectureError(error)
        return tuple(f"{source} -[{relation}]-> {target}" for source, relation, target, _ in checks)
