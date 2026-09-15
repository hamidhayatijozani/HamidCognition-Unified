#!/usr/bin/env python3
"""
HamidCognition Unified — Contradiction Ledger

This module maintains an executable record of contradictions discovered during
research. Contradictions are NOT bugs to hide; they are research observations.

A contradiction blocks promotion to VERIFIED/CANONICAL status until resolved
through one of:
  1. Root cause discovered and corrected
  2. False alarm (original observation was incorrect)
  3. Documented acceptable behavior (semantics justify divergence)
  4. Accepted limitation (trade-off decision)

This replaces hiding issues; we make them structural.
"""

import json
import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime


class ContradictionStatus(Enum):
    """Status of a contradiction record."""
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED_ACCEPTED = "resolved_accepted"
    RESOLVED_FIXED = "resolved_fixed"
    FALSE_ALARM = "false_alarm"
    DEFERRED = "deferred"


class ContradictionSeverity(Enum):
    """Impact on canonicalization/verification."""
    CRITICAL = "critical"  # Blocks any promotion
    MAJOR = "major"  # Blocks VERIFIED; prevents canonical equivalence
    MINOR = "minor"  # Blocks perfect equivalence; acceptable in variants
    DOCUMENTATION = "documentation"  # Metadata mismatch, no behavioral impact


@dataclass
class Contradiction:
    """Single contradiction record."""
    id: str
    title: str
    discovered_in: str  # Experiment ID (e.g., "EXP-001")
    discovered_date: str  # ISO 8601
    severity: str  # "critical", "major", "minor", "documentation"
    
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
    """Executable ledger of unresolved contradictions."""
    
    PROMOTION_BLOCKERS = {"open", "investigating"}
    CRITICAL_BLOCKAGE = {"critical", "major"}
    
    def __init__(self, path: str = "RESEARCH/contradictions.json"):
        self.path = Path(path)
        self.contradictions: Dict[str, Contradiction] = {}
        self._load()
    
    def _load(self):
        """Load persisted contradictions from JSON."""
        if not self.path.exists():
            return
        
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            for entry in data.get("contradictions", []):
                c = Contradiction(**entry)
                self.contradictions[c.id] = c
        except Exception as e:
            print(f"Warning: could not load contradictions: {e}")
    
    def save(self):
        """Persist ledger to JSON."""
        data = {
            "generated": datetime.utcnow().isoformat(),
            "contradictions": [asdict(c) for c in self.contradictions.values()],
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    def add(self, contradiction: Contradiction):
        """Record a new contradiction."""
        if contradiction.id in self.contradictions:
            raise ValueError(f"Contradiction {contradiction.id} already exists")
        self.contradictions[contradiction.id] = contradiction
        self.save()
    
    def update(self, contradiction_id: str, **updates):
        """Update contradiction status."""
        if contradiction_id not in self.contradictions:
            raise ValueError(f"Contradiction {contradiction_id} not found")
        
        c = self.contradictions[contradiction_id]
        for key, value in updates.items():
            if hasattr(c, key):
                setattr(c, key, value)
        
        self.save()
    
    def get_blocking_contradictions(self) -> List[Contradiction]:
        """Return open contradictions that block promotion."""
        return [
            c for c in self.contradictions.values()
            if c.status in self.PROMOTION_BLOCKERS
            and c.severity in self.CRITICAL_BLOCKAGE
        ]
    
    def can_promote_to_verified(self, component_id: str) -> tuple:
        """
        Check if component can be promoted to VERIFIED status.
        
        Returns:
            (can_promote: bool, blocking_contradiction_ids: list)
        """
        blocking = [
            c.id for c in self.contradictions.values()
            if c.status in self.PROMOTION_BLOCKERS
            and c.severity in self.CRITICAL_BLOCKAGE
            and component_id in c.affected_components
        ]
        return len(blocking) == 0, blocking
    
    def validate(self) -> tuple:
        """
        Validate ledger integrity.
        
        Returns:
            (is_valid: bool, errors: list)
        """
        errors = []
        ids = set()
        
        for c in self.contradictions.values():
            if not c.id or c.id in ids:
                errors.append(f"invalid_or_duplicate_id:{c.id}")
            ids.add(c.id)
            
            if c.status in self.PROMOTION_BLOCKERS and not c.description:
                errors.append(f"open_contradiction_missing_description:{c.id}")
            
            if c.status in self.PROMOTION_BLOCKERS and c.severity in self.CRITICAL_BLOCKAGE:
                if not c.affected_components:
                    errors.append(f"blocking_contradiction_missing_components:{c.id}")
        
        return len(errors) == 0, errors
    
    def report(self, format: str = "text") -> str:
        """Generate report of contradiction status."""
        is_valid, validation_errors = self.validate()
        
        if format == "json":
            return json.dumps({
                "valid": is_valid,
                "validation_errors": validation_errors,
                "contradictions": [asdict(c) for c in self.contradictions.values()],
                "blocking_count": len(self.get_blocking_contradictions()),
            }, indent=2)
        
        # Text format
        lines = [
            "=" * 80,
            "HAMIDCOGNITION UNIFIED — CONTRADICTION LEDGER",
            f"Generated: {datetime.utcnow().isoformat()}",
            f"Status: {'VALID' if is_valid else 'INVALID'}",
            "=" * 80,
            "",
        ]
        
        if validation_errors:
            lines.append("VALIDATION ERRORS:")
            for err in validation_errors:
                lines.append(f"  ✗ {err}")
            lines.append("")
        
        blocking = self.get_blocking_contradictions()
        
        if blocking:
            lines.append(f"BLOCKING CONTRADICTIONS ({len(blocking)}):")
            lines.append("-" * 80)
            for c in sorted(blocking, key=lambda x: x.severity):
                lines.append(f"\n  {c.id} [{c.severity.upper()}]")
                lines.append(f"    Title: {c.title}")
                lines.append(f"    Discovered in: {c.discovered_in}")
                if c.affected_components:
                    lines.append(f"    Affects: {', '.join(c.affected_components)}")
                if c.affected_variants:
                    lines.append(f"    Variants: {', '.join(c.affected_variants)}")
                lines.append(f"    {c.description}")
                if c.blocking_issues:
                    lines.append(f"    GitHub: {', '.join(f'#{i}' for i in c.blocking_issues)}")
        else:
            lines.append("✓ No blocking contradictions")
        
        lines.append("\n" + "=" * 80)
        lines.append(f"Total contradictions: {len(self.contradictions)}")
        lines.append(f"Blocking: {len(blocking)}")
        lines.append("=" * 80)
        
        return "\n".join(lines)


# ============================================================================
# PROMOTION GATE: Block verification if contradictions unresolved
# ============================================================================

def check_promotion_gate(component_id: str, ledger: Optional[ContradictionLedger] = None) -> bool:
    """
    Prevents promotion of component unless all contradictions are resolved.
    
    Args:
        component_id: HC-001, HC-008, etc.
        ledger: ContradictionLedger instance
    
    Returns:
        True if safe to promote, False otherwise
    """
    if ledger is None:
        ledger = ContradictionLedger()
    
    can_promote, blockers = ledger.can_promote_to_verified(component_id)
    return can_promote


def main(argv=None):
    """CLI interface for contradiction ledger."""
    if argv is None:
        argv = sys.argv[1:]
    
    if not argv:
        ledger = ContradictionLedger()
        print(ledger.report())
        return 0
    
    cmd = argv[0]
    
    if cmd == "validate":
        ledger = ContradictionLedger()
        is_valid, errors = ledger.validate()
        print(json.dumps({"valid": is_valid, "errors": errors}, indent=2))
        return 0 if is_valid else 1
    
    elif cmd == "report":
        ledger = ContradictionLedger()
        fmt = argv[1] if len(argv) > 1 else "text"
        print(ledger.report(format=fmt))
        return 0
    
    elif cmd == "check-gate":
        if len(argv) < 2:
            print("Usage: check-gate <component_id>")
            return 1
        component_id = argv[1]
        ledger = ContradictionLedger()
        can_promote = check_promotion_gate(component_id, ledger)
        result = {"component": component_id, "can_promote": can_promote}
        if not can_promote:
            _, blockers = ledger.can_promote_to_verified(component_id)
            result["blockers"] = blockers
        print(json.dumps(result, indent=2))
        return 0 if can_promote else 1
    
    else:
        print(f"Unknown command: {cmd}")
        print("Available: validate, report, check-gate <component_id>")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
