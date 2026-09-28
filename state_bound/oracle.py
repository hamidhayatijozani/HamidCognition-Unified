from __future__ import annotations
from dataclasses import dataclass
from threading import RLock
from typing import Callable
from .models import WorldState

@dataclass(frozen=True)
class OracleSnapshot:
    version:int
    world:WorldState

class StateOracle:
    """Append-only in-memory oracle for TA-001."""
    def __init__(self,initial_trajectory:dict,metadata:dict|None=None):
        self._lock=RLock(); self._version=1
        self._world=WorldState(self._version,dict(initial_trajectory),dict(metadata or {}))
    def latest(self)->OracleSnapshot:
        with self._lock: return OracleSnapshot(self._world.version,self._world)
    def append(self,trajectory:dict,metadata:dict|None=None)->OracleSnapshot:
        with self._lock:
            self._version+=1
            self._world=WorldState(self._version,dict(trajectory),dict(metadata or self._world.metadata))
            return OracleSnapshot(self._world.version,self._world)
    def execute_if_valid(self,*,authority,action:dict,subject:str,now_ns:int,verify:Callable,execute:Callable):
        """Atomically verify latest committed oracle state and run the prototype callback."""
        with self._lock:
            snapshot=OracleSnapshot(self._world.version,self._world)
            result=verify(authority,current_world=snapshot.world,current_action=action,subject=subject,now_ns=now_ns)
            if result.executable: execute(action,snapshot.world)
            return result
