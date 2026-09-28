"""BESAZ integration map: awareness governs existing product subsystems."""
from __future__ import annotations
from dataclasses import dataclass
from .awareness_components import canonical_contracts
from .awareness_registry import AwarenessRegistry
from .awareness_policy import authorize, Authorization

@dataclass(frozen=True)
class IntegrationBinding:
    component_id: str
    subsystem: str
    role: str
    evidence_required: bool = True

BESAZ_BINDINGS=(
    IntegrationBinding("GOVERNANCE","Action Gate + Z-FREEZE-LOCK","authority, safety and freeze policy"),
    IntegrationBinding("COGNITION","Strategic Intelligence OS","coordinate knowledge models"),
    IntegrationBinding("SELF-MODEL","Strategic Intelligence Self Model","capability ledger and maturity evidence"),
    IntegrationBinding("CREATOR-CONTEXT","Strategic Intelligence Creator Model","explicit goals, constraints and decisions"),
    IntegrationBinding("MARKET-INTELLIGENCE","Market Intelligence","dated sources, signals and counter-evidence"),
    IntegrationBinding("REASONING","Evidence-bound reasoning","separate facts, assumptions and inference"),
    IntegrationBinding("EXECUTION","Idea-to-Sale OS","bounded execution of product and commercial workflows"),
    IntegrationBinding("PROMPTS","Prompt assets","run contracted prompt operations"),
    IntegrationBinding("MODULES","Application modules","run deterministic modules"),
    IntegrationBinding("TOOLS","External adapters","invoke only authorized interfaces"),
    IntegrationBinding("WORKFLOWS","Workflow orchestration","advance only across explicit gates"),
    IntegrationBinding("FEEDBACK","Evidence Pipeline","verify and record outcomes"),
    IntegrationBinding("VERIFICATION","Release verification","bind claims to tests and artifacts"),
    IntegrationBinding("MEMORY","Provenance records","persist verified state"),
    IntegrationBinding("LEARNING","Learning loop","propose updates only from verified outcomes"),
)

def build_besaz_registry() -> AwarenessRegistry:
    return AwarenessRegistry(canonical_contracts())

def binding_for(component_id: str) -> IntegrationBinding:
    return next(b for b in BESAZ_BINDINGS if b.component_id==component_id)

def authorize_need(registry: AwarenessRegistry, component_id: str, action: str, approval: bool=False) -> Authorization:
    return authorize(registry.component(component_id), action, approval)

def system_health(registry: AwarenessRegistry) -> dict:
    return {"project":"BESAZ","components":registry.health(),"bindings":len(BESAZ_BINDINGS)}
