"""Hard invariants from Jade's founding goal. Agent branches may not modify or delete this file
(scripts/guard.py); add new invariant tests in a new file instead."""
import importlib.util
import subprocess
from pathlib import Path

import pandas as pd
import pytest

from factory import broker, execute, invariants, risk
from tests.test_risk_and_execute import LIMITS, _fresh, _patch

ROOT = Path(__file__).resolve().parent.parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


guard = _load("guard_inv", "scripts/guard.py")
rule_log = _load("rule_log_inv", "scripts/rule_log.py")


# --- paper trading only ---------------------------------------------------------------------------
def test_no_live_endpoint_anywhere():
    assert guard.check_live_endpoints() == []


def test_broker_only_knows_the_paper_endpoint(monkeypatch):
    assert broker.PAPER_URL == invariants.PAPER_URL == "https://paper-api.alpaca.markets"
    monkeypatch.setenv("APCA_API_KEY_ID", "k")
    monkeypatch.setenv("APCA_API_SECRET_KEY", "s")
    monkeypatch.setenv("APCA_API_BASE_URL", "https://example.com")
    with pytest.raises(broker.BrokerError):
        broker.PaperBroker()


@pytest.mark.parametrize("limits,acct", [({}, "PA1"), ({"paper_only": False}, "PA1"),
                                         ({"paper_only": "true"}, "PA1"), ({"paper_only": True}, "123")])
def test_paper_required_regardless_of_rules(limits, acct):
    with pytest.raises(RuntimeError):
        invariants.require_paper(limits, acct)
    with pytest.raises(risk.RiskError):
        risk.check_account({"account_number": acct, "status": "ACTIVE"}, {**LIMITS, **limits} if limits else {})


# --- no orders on data, auth or validation failure ------------------------------------------------
def _syms():
    return execute.config.universe()["symbols"]


def test_stale_data_places_no_orders(monkeypatch, tmp_path):
    from factory.data import synthetic
    b = _patch(monkeypatch, synthetic(_syms(), "2024-01-01", "2024-06-28"))
    assert execute.main(["--out", str(tmp_path)]) != 0 and b.submitted == []


def test_auth_failure_places_no_orders(monkeypatch, tmp_path):
    def boom():
        raise broker.BrokerError("401 unauthorized")
    monkeypatch.setattr(execute, "PaperBroker", boom)
    monkeypatch.setattr(execute, "load_alpaca", lambda *a, **k: _fresh(_syms()))
    assert execute.main(["--out", str(tmp_path)]) != 0


def test_validation_failure_places_no_orders(monkeypatch, tmp_path):
    md = _fresh(_syms())
    b = _patch(monkeypatch, md)
    monkeypatch.setattr(execute, "decide", lambda *a, **k: (_ for _ in ()).throw(risk.RiskError("bad weights")))
    assert execute.main(["--out", str(tmp_path)]) != 0 and b.submitted == []


def test_non_paper_account_places_no_orders(monkeypatch, tmp_path):
    b = _patch(monkeypatch, _fresh(_syms()))
    monkeypatch.setattr(b, "account", lambda: {"account_number": "999", "status": "ACTIVE",
                                               "equity": "100000", "cash": "100000"})
    assert execute.main(["--out", str(tmp_path)]) != 0 and b.submitted == []


# --- failed experiments retained; invariants and rule changes guarded -----------------------------
@pytest.fixture
def repo(tmp_path, monkeypatch):
    def run(*a):
        subprocess.run(["git", *a], cwd=tmp_path, check=True, capture_output=True)
    run("init", "-q", "-b", "main")
    run("config", "user.email", "t@t"); run("config", "user.name", "t")
    for p in ["scripts/guard.py", "strategies/candidates/old.py", "protected/risk_limits.yaml",
              "factory/invariants.py", "tests/test_invariants.py"]:
        (tmp_path / p).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / p).write_text("max_gross_exposure: 1.0\n" if p.endswith(".yaml") else "x = 1\n")
    run("add", "-A"); run("commit", "-qm", "base")
    run("checkout", "-qb", "claude/x")
    monkeypatch.setattr(guard, "ROOT", tmp_path)
    monkeypatch.setattr(rule_log, "ROOT", tmp_path)
    return tmp_path, run


def test_candidate_files_are_immutable(repo):
    root, run = repo
    (root / "strategies/candidates/old.py").unlink()
    run("commit", "-qam", "delete")
    assert any("immutable" in e for e in guard.check_branch("main", "claude/x"))


@pytest.mark.parametrize("path", invariants.INVARIANT_FILES)
def test_agent_cannot_edit_invariants(repo, path):
    root, run = repo
    (root / path).write_text("x = 2\n")
    run("commit", "-qam", "edit")
    assert any("hard invariant" in e for e in guard.check_branch("main", "claude/x"))


def test_rule_change_needs_reason_and_is_logged(repo, monkeypatch):
    root, run = repo
    (root / "protected/risk_limits.yaml").write_text("max_gross_exposure: 0.8\n")
    run("commit", "-qam", "lower gross\n\nReason: drawdowns too deep")
    monkeypatch.setenv("GUARD_PR_BODY", "no reason here")
    assert any("Reason:" in e for e in guard.check_branch("main", "claude/x"))
    monkeypatch.setenv("GUARD_PR_BODY", "Reason: drawdowns too deep")
    assert guard.check_branch("main", "claude/x") == []
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    rec = rule_log.build("main", "claude/x")
    assert rec["reason"] == "drawdowns too deep"
    assert rec["files"] == [{"file": "protected/risk_limits.yaml", "change": "M",
                             "values": [{"key": "max_gross_exposure", "before": 1.0, "after": 0.8}]}]
