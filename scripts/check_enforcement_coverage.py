"""Fail closed when a production protected-tool endpoint lacks enforcement.

Protected tool source files are discovered under protected_tools/ and
action_gate/protected_tools/. A public FastAPI route in those locations must
declare require_execution_authority as a dependency.
"""
from __future__ import annotations

import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [ROOT / "protected_tools", ROOT / "action_gate" / "protected_tools"]


def is_protected_path(path: Path) -> bool:
    return any(path.is_relative_to(t) for t in TARGETS if t.exists())


def has_enforcement(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    source = ast.unparse(node)
    return "require_execution_authority" in source or "enforce_execution_authority" in source


def check(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError) as exc:
        return [f"{path}: cannot parse: {exc}"]
    failures = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            route = any(
                isinstance(dec, ast.Call)
                and isinstance(dec.func, ast.Attribute)
                and dec.func.attr in {"get", "post", "put", "patch", "delete"}
                for dec in node.decorator_list
            )
            if route and not has_enforcement(node):
                failures.append(f"{path}:{node.lineno}: protected route lacks execution enforcement")
    return failures


def main() -> int:
    files = [p for root in TARGETS if root.exists() for p in root.rglob("*.py")]
    failures = [msg for p in files for msg in check(p)]
    if failures:
        print("\n".join(failures))
        return 1
    print(f"Enforcement coverage OK: {len(files)} protected-tool Python files scanned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
