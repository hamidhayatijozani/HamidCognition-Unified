#!/usr/bin/env python3
"""Executable contradiction ledger for research evidence."""
import json, sys
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime

class ContradictionStatus(Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED_ACCEPTED = "resolved_accepted"
    RESOLVED_FIXED = "resolved_fixed"
    FALSE_ALARM = "false_alarm"
    FALSIFIED = "falsified"
    DEFERRED = "deferred"

class ContradictionSeverity(Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    DOCUMENTATION = "documentation"

@dataclass
class Contradiction:
    id: str
    title: str
    discovered_in: str
    discovered_date: str
    severity: str
    description: str
    observed_behavior: str
    expected_behavior: str
    affected_components: List[str] = field(default_factory=list)
    affected_variants: List[str] = field(default_factory=list)
    status: str = "open"
    resolution_notes: Optional[str] = None
    resolved_date: Optional[str] = None
    blocking_issues: List[int] = field(default_factory=list)
    test_artifact: Optional[str] = None

class ContradictionLedger:
    PROMOTION_BLOCKERS = {"open", "investigating"}
    CRITICAL_BLOCKAGE = {"critical", "major"}
    def __init__(self, path: str = "RESEARCH/contradictions.json"):
        self.path = Path(path); self.contradictions: Dict[str, Contradiction] = {}; self._load()
    def _load(self):
        if not self.path.exists(): return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            for entry in data.get("contradictions", []): self.contradictions[entry["id"]] = Contradiction(**entry)
        except Exception as e: print(f"Warning: could not load contradictions: {e}")
    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({"generated": datetime.utcnow().isoformat(), "contradictions": [asdict(c) for c in self.contradictions.values()]}, indent=2), encoding="utf-8")
    def add(self, contradiction: Contradiction):
        if contradiction.id in self.contradictions: raise ValueError(f"Contradiction {contradiction.id} already exists")
        self.contradictions[contradiction.id] = contradiction; self.save()
    def update(self, contradiction_id: str, **updates):
        if contradiction_id not in self.contradictions: raise ValueError(f"Contradiction {contradiction_id} not found")
        c = self.contradictions[contradiction_id]
        for key, value in updates.items():
            if hasattr(c, key): setattr(c, key, value)
        self.save()
    def get_blocking_contradictions(self):
        return [c for c in self.contradictions.values() if c.status in self.PROMOTION_BLOCKERS and c.severity in self.CRITICAL_BLOCKAGE]
    def can_promote_to_verified(self, component_id: str):
        blocking = [c.id for c in self.contradictions.values() if c.status in self.PROMOTION_BLOCKERS and c.severity in self.CRITICAL_BLOCKAGE and component_id in c.affected_components]
        return len(blocking) == 0, blocking
    def validate(self):
        errors=[]; ids=set()
        for c in self.contradictions.values():
            if not c.id or c.id in ids: errors.append(f"invalid_or_duplicate_id:{c.id}")
            ids.add(c.id)
            if c.status in self.PROMOTION_BLOCKERS and not c.description: errors.append(f"open_contradiction_missing_description:{c.id}")
            if c.status in self.PROMOTION_BLOCKERS and c.severity in self.CRITICAL_BLOCKAGE and not c.affected_components: errors.append(f"blocking_contradiction_missing_components:{c.id}")
        return len(errors) == 0, errors
    def report(self, format="text"):
        valid, errors = self.validate(); blocking = self.get_blocking_contradictions()
        if format == "json": return json.dumps({"valid":valid,"validation_errors":errors,"contradictions":[asdict(c) for c in self.contradictions.values()],"blocking_count":len(blocking)}, indent=2)
        lines=["="*80,"HAMIDCOGNITION UNIFIED — CONTRADICTION LEDGER",f"Generated: {datetime.utcnow().isoformat()}",f"Status: {'VALID' if valid else 'INVALID'}","="*80,""]
        if errors:
            lines += ["VALIDATION ERRORS:"] + [f"  ✗ {e}" for e in errors] + [""]
        if blocking:
            lines += [f"BLOCKING CONTRADICTIONS ({len(blocking)}):","-"*80]
            for c in sorted(blocking,key=lambda x:x.severity):
                lines += [f"\n  {c.id} [{c.severity.upper()}]",f"    Title: {c.title}",f"    Discovered in: {c.discovered_in}",f"    Affects: {', '.join(c.affected_components)}",f"    {c.description}"]
        else: lines.append("✓ No blocking contradictions")
        lines += ["\n"+"="*80,f"Total contradictions: {len(self.contradictions)}",f"Blocking: {len(blocking)}","="*80]
        return "\n".join(lines)

def check_promotion_gate(component_id, ledger=None):
    if ledger is None: ledger=ContradictionLedger()
    return ledger.can_promote_to_verified(component_id)[0]

def main(argv=None):
    argv=sys.argv[1:] if argv is None else argv
    ledger=ContradictionLedger()
    if not argv: print(ledger.report()); return 0
    cmd=argv[0]
    if cmd == "validate":
        valid, errors=ledger.validate(); print(json.dumps({"valid":valid,"errors":errors},indent=2)); return 0 if valid else 1
    if cmd == "report": print(ledger.report(argv[1] if len(argv)>1 else "text")); return 0
    if cmd == "check-gate":
        if len(argv)<2: print("Usage: check-gate <component_id>"); return 1
        can, blockers=ledger.can_promote_to_verified(argv[1]); result={"component":argv[1],"can_promote":can};
        if not can: result["blockers"]=blockers
        print(json.dumps(result,indent=2)); return 0 if can else 1
    print(f"Unknown command: {cmd}\nAvailable: validate, report, check-gate <component_id>"); return 1

if __name__ == "__main__": raise SystemExit(main())
