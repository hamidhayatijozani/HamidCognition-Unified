"""Fail closed when a protected FastAPI route lacks execution enforcement."""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [ROOT / "protected_tools", ROOT / "action_gate" / "protected_tools"]


def route_function(node: ast.AST) -> bool:
    return isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and any(
        isinstance(dec, ast.Call)
        and isinstance(dec.func, ast.Attribute)
        and dec.func.attr in {"get", "post", "put", "patch", "delete"}
        for dec in node.decorator_list
    )


def enforcement_dependency(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for default in list(node.args.defaults) + [x for x in node.args.kw_defaults if x is not None]:
        if isinstance(default, ast.Call) and isinstance(default.func, ast.Name) and default.func.id == "Depends":
            if any(isinstance(arg, ast.Name) and arg.id == "require_execution_authority" for arg in default.args):
                return True
    return False


def check(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError) as exc:
        return [f"{path}: cannot parse: {exc}"]

    failures: list[str] = []
    for node in ast.walk(tree):
        if route_function(node):
            assert isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            if not enforcement_dependency(node):
                failures.append(f"{path}:{node.lineno}: protected route lacks Depends(require_execution_authority)")
    return failures


def main() -> int:
    roots = [root for root in TARGETS if root.exists()]
    files = [path for root in roots for path in root.rglob("*.py") if path.name != "__init__.py"]
    if not files:
        print("ERROR: no protected-tool Python files found; enforcement coverage fails closed")
        return 1

    failures = [message for path in files for message in check(path)]
    if failures:
        print("\n".join(failures))
        return 1

    print(f"Enforcement coverage OK: {len(files)} protected-tool Python files scanned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
