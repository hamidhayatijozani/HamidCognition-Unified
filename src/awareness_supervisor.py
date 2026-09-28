"""Top-level supervisor for bounded awareness components."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from .awareness_registry import AwarenessRegistry, SupervisorDecision

@dataclass(frozen=True)
class SupervisorEvent:
    component_id: str
    kind: str
    detail: str

class AwarenessSupervisor:
    def __init__(self, registry: AwarenessRegistry):
        self.registry=registry
        self.events:list[SupervisorEvent]=[]

    def inspect(self)->dict:
        health=self.registry.health()
        self.events.append(SupervisorEvent("ROOT","INSPECT",f"{len(health)} components inspected"))
        return health

    def process(self, component_id:str, observer:Callable, need_detector:Callable):
        component=self.registry.component(component_id)
        component._observer=observer
        observations=component.observe()
        needs=component.detect_need(need_detector)
        decisions=[self.registry.route_need(component_id,n) for n in needs]
        for d in decisions:
            self.events.append(SupervisorEvent(d.component_id,"ROUTE",f"{d.action}:{d.mode}:{d.reason}"))
        return {"observations":observations,"needs":needs,"decisions":[d.__dict__ for d in decisions]}

    def event_log(self):
        return [e.__dict__ for e in self.events]
