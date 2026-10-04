"""Static checks and loading for agent-written candidate strategies.

Candidates live in strategies/candidates/<name>.py and may import only numpy, pandas, math,
statistics and strategies.base. No file, network, process or dynamic-code access.
"""
from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

ALLOWED_IMPORTS = {"numpy", "pandas", "math", "statistics", "strategies.base", "__future__"}
BANNED_NAMES = {
    "open", "exec", "eval", "compile", "__import__", "getattr", "setattr", "delattr", "globals",
    "locals", "vars", "input", "breakpoint", "exit", "quit", "memoryview",
}
BANNED_ATTRS = {"read_csv", "read_parquet", "read_json", "read_html", "read_sql", "to_csv", "to_parquet",
                "to_pickle", "read_pickle", "to_json", "to_sql", "load", "save", "savez", "fromfile", "tofile",
                "system", "popen"}


class CandidateRejected(ValueError):
    pass


def check_source(src: str) -> None:
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name not in ALLOWED_IMPORTS:
                    raise CandidateRejected(f"import not allowed: {a.name}")
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "") not in ALLOWED_IMPORTS or node.level:
                raise CandidateRejected(f"import not allowed: {node.module}")
        elif isinstance(node, ast.Name) and node.id in BANNED_NAMES:
            raise CandidateRejected(f"name not allowed: {node.id}")
        elif isinstance(node, ast.Attribute):
            if node.attr.startswith("__") or node.attr in BANNED_ATTRS:
                raise CandidateRejected(f"attribute not allowed: {node.attr}")
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            raise CandidateRejected("global/nonlocal not allowed")


def load_candidate(path: Path | str):
    """Return the single Strategy subclass defined in a candidate file."""
    path = Path(path)
    check_source(path.read_text())
    spec = importlib.util.spec_from_file_location(f"candidate_{path.stem}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    from strategies.base import Strategy
    found = [v for v in vars(mod).values() if isinstance(v, type) and issubclass(v, Strategy) and v is not Strategy
             and v.__module__ == mod.__name__]
    if len(found) != 1:
        raise CandidateRejected(f"expected exactly one Strategy subclass in {path.name}, found {len(found)}")
    return found[0]


def load_ref(ref: str):
    """Load 'module.path:ClassName' (baselines) or a candidate file path."""
    if ref.endswith(".py"):
        return load_candidate(ref)
    mod, _, cls = ref.partition(":")
    return getattr(importlib.import_module(mod), cls)
