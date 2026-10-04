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
    "locals", "vars", "input", "breakpoint", "exit", "quit", "memoryview", "__builtins__", "help",
}
# File, process and code-evaluation entry points in numpy/pandas. Checked on attribute access AND on
# `from x import name`. This is a lint for honest mistakes, not the security boundary: candidate code
# only ever runs in factory/runner.py's credential-free child process.
BANNED_ATTRS = {
    "save", "savez", "savez_compressed", "savetxt", "load", "loadtxt", "genfromtxt", "fromfile", "tofile",
    "fromregex", "memmap", "DataSource", "lib", "ctypeslib", "f2py", "testing",
    "to_csv", "to_parquet", "to_pickle", "to_json", "to_sql", "to_excel", "to_hdf", "to_feather", "to_stata",
    "to_html", "to_latex", "to_markdown", "to_clipboard", "to_xml", "to_orc", "ExcelWriter", "HDFStore",
    "eval", "query", "system", "popen", "io", "api",
}


def _banned_attr(name: str) -> bool:
    return name.startswith("_") or name.startswith("read_") or name in BANNED_ATTRS


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
            for a in node.names:
                if a.name == "*" or _banned_attr(a.name):
                    raise CandidateRejected(f"import not allowed: {node.module}.{a.name}")
        elif isinstance(node, ast.Name) and node.id in BANNED_NAMES:
            raise CandidateRejected(f"name not allowed: {node.id}")
        elif isinstance(node, ast.Attribute):
            if _banned_attr(node.attr):
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
