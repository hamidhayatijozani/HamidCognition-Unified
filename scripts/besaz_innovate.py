"""Generate a bounded BESAZ innovation report from the canonical architecture."""
import json
from pathlib import Path

from src.besaz_innovation_engine import innovation_report
from src.awareness_components import canonical_contracts

OUT = Path("data/awareness/innovation-report.json")


def main() -> None:
    contracts = canonical_contracts()
    components = [
        {
            "component_id": c.component_id,
            "maturity": c.maturity.value,
            "evidence_refs": list(c.evidence_refs),
            "capabilities": list(c.capabilities),
        }
        for c in contracts
    ]
    report = innovation_report(components)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
