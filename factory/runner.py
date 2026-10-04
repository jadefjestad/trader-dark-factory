"""Run strategy code in a separate, credential-free process.

The evaluator and executor never import strategy modules themselves. They hand the market data to a
child process (optionally as an unprivileged OS user, set FACTORY_SANDBOX_USER), which returns only
numeric weight arrays. The child gets a private copy of the code and data in a temp directory, an empty
environment, and a timeout, so a strategy cannot read secrets, mutate the data the evaluator scores,
or write results the parent trusts.

Child mode:  python -m factory.runner <workdir> <ref>
"""
from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from factory.config import ROOT
from factory.data import FIELDS, MarketData

DEFAULT_TIMEOUT_S = 600


class StrategyError(RuntimeError):
    pass


# ---------------------------------------------------------------- parent side

def _write_inputs(work: Path, md: MarketData | None, jobs: list[dict]) -> None:
    code = work / "code"
    for pkg in ("factory", "strategies"):
        shutil.copytree(ROOT / pkg, code / pkg, ignore=shutil.ignore_patterns("__pycache__"), symlinks=False)
    (work / "jobs.json").write_text(json.dumps(jobs))
    if md is not None:
        idx = pd.DatetimeIndex(md.index)
        tz = str(idx.tz) if idx.tz is not None else ""
        ns = (idx.tz_convert("UTC").tz_localize(None) if tz else idx).as_unit("ns").asi8
        arrays = {f: getattr(md, f).reindex(columns=md.symbols).to_numpy(dtype=float) for f in FIELDS}
        np.savez(work / "data.npz", index=ns, **arrays,
                 meta=np.frombuffer(json.dumps({"symbols": md.symbols, "tz": tz, "timeframe": md.timeframe,
                                                 "source": md.source}).encode(), dtype=np.uint8))
    for p in [work, *work.rglob("*")]:
        p.chmod(0o755 if p.is_dir() else 0o644)


def _invoke(ref: str, md: MarketData | None, jobs: list[dict], timeout: int) -> dict:
    with tempfile.TemporaryDirectory(prefix="tdf-run-") as tmp:
        work = Path(tmp)
        _write_inputs(work, md, jobs)
        child = [sys.executable, "-m", "factory.runner", str(work), ref]
        # the child sees its private code copy plus the interpreter's library paths, never the repo itself
        libs = [p for p in sys.path if p and Path(p).resolve() != ROOT and Path(p).exists()]
        pypath = os.pathsep.join([str(work / "code"), *libs])
        env = ["env", "-i", "PATH=/usr/bin:/bin", f"PYTHONPATH={pypath}", f"HOME={work}",
               "PYTHONDONTWRITEBYTECODE=1", "MPLCONFIGDIR=" + str(work)]
        user = os.environ.get("FACTORY_SANDBOX_USER")
        cmd = (["sudo", "-n", "-u", user] if user else []) + env + child
        try:
            p = subprocess.run(cmd, cwd=work / "code", capture_output=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            raise StrategyError(f"{ref} exceeded {timeout}s")
        if p.returncode != 0:
            raise StrategyError(f"{ref} failed: {p.stderr.decode(errors='replace')[-1500:]}")
        with np.load(io.BytesIO(p.stdout), allow_pickle=False) as z:
            return {k: z[k] for k in z.files}


def describe(ref: str, timeout: int = 120) -> dict:
    """Name, timeframe, lookback and default params of a strategy, read in the child process."""
    out = _invoke(ref, None, [], timeout)
    return json.loads(out["meta"].tobytes().decode())


def run(ref: str, md: MarketData, jobs: list[dict], timeout: int = DEFAULT_TIMEOUT_S) -> list[pd.DataFrame]:
    """jobs: [{"params": {...} or None, "rows": n or None}] -> one weights frame per job (rows = first n bars)."""
    out = _invoke(ref, md, jobs, timeout)
    frames = []
    for i, job in enumerate(jobs):
        n = job.get("rows") or len(md.index)
        a = out[f"w{i}"]
        if a.shape != (n, len(md.symbols)):
            raise StrategyError(f"{ref} returned shape {a.shape}, expected {(n, len(md.symbols))}")
        frames.append(pd.DataFrame(a, index=md.index[:n], columns=md.symbols))
    return frames


# ---------------------------------------------------------------- child side

def _child(work: Path, ref: str) -> None:
    from factory.sandbox import load_ref

    cls = load_ref(ref)
    jobs = json.loads((work / "jobs.json").read_text())
    meta = {"name": cls.name, "timeframe": cls.timeframe, "lookback": int(cls.lookback), "params": dict(cls.params)}
    out = {"meta": np.frombuffer(json.dumps(meta).encode(), dtype=np.uint8)}
    if jobs:
        with np.load(work / "data.npz", allow_pickle=False) as z:
            m = json.loads(z["meta"].tobytes().decode())
            idx = pd.DatetimeIndex(z["index"])
            if m["tz"]:
                idx = idx.tz_localize("UTC").tz_convert(m["tz"])
            raw = {f: z[f] for f in FIELDS}
        for i, job in enumerate(jobs):
            n = job.get("rows") or len(idx)
            md = MarketData(*(pd.DataFrame(raw[f][:n].copy(), index=idx[:n], columns=m["symbols"]) for f in FIELDS),
                            timeframe=m["timeframe"], source=m["source"])
            s = cls(**(job.get("params") or {}))
            w = s.target_weights(md)
            if not isinstance(w, pd.DataFrame):
                raise TypeError("target_weights must return a DataFrame")
            w = w.reindex(index=md.index, columns=m["symbols"]).astype(float)
            out[f"w{i}"] = w.to_numpy()
    buf = io.BytesIO()
    np.savez(buf, **out)
    sys.stdout.buffer.write(buf.getvalue())


if __name__ == "__main__":
    _child(Path(sys.argv[1]), sys.argv[2])
