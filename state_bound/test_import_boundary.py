import ast
from pathlib import Path


def test_reaction_layer_cannot_import_action_gate():
    root = Path(__file__).parent
    forbidden = {"action_gate", "action_gate.app", "action_gate.security_authority"}
    for path in root.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = {alias.name for alias in node.names}
                assert not forbidden.intersection(imported), f"{path} imports forbidden Action Gate module"
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                assert module not in forbidden and not module.startswith("action_gate."), (
                    f"{path} imports forbidden Action Gate module {module}"
                )
