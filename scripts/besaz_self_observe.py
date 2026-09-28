import json
from pathlib import Path
from src.besaz_self_observer import observe

out=Path("data/awareness/self-observation.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(observe(), ensure_ascii=False, indent=2, sort_keys=True)+"\n", encoding="utf-8")
print(out)
