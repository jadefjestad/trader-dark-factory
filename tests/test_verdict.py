import json
import subprocess
import sys
from pathlib import Path

from factory import evaluate

ROOT = Path(__file__).resolve().parent.parent


def _verdict(tmp, head):
    (tmp / "head.json").write_text(json.dumps(head))
    return subprocess.run([sys.executable, str(ROOT / "scripts" / "pr_verdict.py"), "--results", str(tmp / "results"),
                           "--head-champion", str(tmp / "head.json"), "--base-champion", str(ROOT / "state" / "champion.json"),
                           "--out", str(tmp / "v.md")], capture_output=True, text=True).returncode


def test_champion_change_requires_matching_promote(tmp_path):
    r = evaluate.evaluate("strategies/candidates/example_momentum_trend.py", "synthetic", "x", include_baselines=False)
    (tmp_path / "results").mkdir()
    s = r["strategy"]
    champ = {k: s[k] for k in ("ref", "params", "code_sha256", "timeframe")}
    (tmp_path / "results" / "x.json").write_text(json.dumps(r, default=str))
    (tmp_path / "results" / "x.md").write_text("md")
    assert _verdict(tmp_path, champ) == 1                       # synthetic run never promotes
    r["promote"] = True
    (tmp_path / "results" / "x.json").write_text(json.dumps(r, default=str))
    assert _verdict(tmp_path, champ) == 0
    assert _verdict(tmp_path, {**champ, "params": {**s["params"], "top_n": 3}}) == 1
