"""Load protected configuration and fingerprint it so results record exactly which rules applied."""
from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PROTECTED = ROOT / "protected"


def _load(name: str) -> dict:
    with open(PROTECTED / name) as f:
        return yaml.safe_load(f)


def universe() -> dict:
    return _load("universe.yaml")


def evaluation() -> dict:
    return _load("evaluation.yaml")


def risk_limits() -> dict:
    return _load("risk_limits.yaml")


def protected_fingerprint() -> str:
    h = hashlib.sha256()
    for p in sorted(PROTECTED.glob("*.yaml")):
        h.update(p.name.encode())
        h.update(p.read_bytes())
    return h.hexdigest()[:16]


def file_sha256(path: Path | str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
