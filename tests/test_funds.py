"""Paper funds: config, keys, and per-fund fail-closed execution."""
import json

import pandas as pd
import pytest
import yaml

from factory import execute, funds
from factory.data import synthetic
from tests.test_risk_and_execute import FakeBroker

NAMES = ["The Empire Strikes Black", "Darth Trader", "Back to the Futures", "Marty McBuy", "Wizard of Odds",
         "Jon Dough", "Live Long and Profit", "Game of Loans", "Frodough Baggins"]


def test_config_has_the_nine_funds_and_valid_strategies():
    fs = funds.load()
    assert [f.number for f in fs] == list(range(1, 10))
    assert [f.name for f in fs] == NAMES
    assert all(f.emoji for f in fs)
    for f in fs:
        s = funds.strategy(f)   # raises on a missing file or hash mismatch
        assert s["name"] and s["ref"]


def test_credentials_fall_back_to_the_original_account_for_fund_1_only():
    env = {"ALPACA_API_KEY_ID": "a", "ALPACA_API_SECRET_KEY": "b", "ALPACA_FUND_3_KEY_ID": "c"}
    assert funds.credentials(1, env) == ("a", "b")
    assert funds.credentials(2, env) is None
    assert funds.credentials(3, env) is None   # half a key pair is no key pair
    env["ALPACA_FUND_3_SECRET_KEY"] = "d"
    assert funds.credentials(3, env) == ("c", "d")
    assert funds.credentials(1, {**env, "ALPACA_FUND_1_KEY_ID": "e", "ALPACA_FUND_1_SECRET_KEY": "f"}) == ("e", "f")


def test_bad_fund_numbers_are_rejected(tmp_path):
    p = tmp_path / "funds.yaml"
    p.write_text("funds:\n  10:\n    name: x\n    emoji: y\n    strategy: champion\n")
    with pytest.raises(funds.FundError):
        funds.load(p)


def _fresh(syms, bars=400):
    today = pd.Timestamp.now(tz="America/New_York").normalize().tz_localize(None)
    prev = pd.bdate_range(today - pd.Timedelta(days=10), today - pd.Timedelta(days=1))[-1]
    return synthetic(syms, (prev - pd.tseries.offsets.BDay(bars)).strftime("%Y-%m-%d"), prev.strftime("%Y-%m-%d"))


def _setup(monkeypatch, tmp_path, keyed: dict, assignments: dict | None = None):
    """keyed: {fund number: FakeBroker}. Only those funds get keys."""
    for n in range(1, 10):
        for part in ("KEY_ID", "SECRET_KEY"):
            monkeypatch.delenv(f"ALPACA_FUND_{n}_{part}", raising=False)
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    for n in keyed:
        monkeypatch.setenv(f"ALPACA_FUND_{n}_KEY_ID", f"k{n}")
        monkeypatch.setenv(f"ALPACA_FUND_{n}_SECRET_KEY", f"s{n}")
    monkeypatch.setattr(execute, "PaperBroker", lambda key, secret: keyed[int(key[1:])])
    if assignments:
        p = tmp_path / "funds.yaml"
        p.write_text(yaml.safe_dump({"funds": {n: {"name": f"f{n}", "emoji": "x", "strategy": s}
                                               for n, s in assignments.items()}}))
        real = funds.load
        monkeypatch.setattr(funds, "load", lambda path=None: real(p))


def _broker(md, number="PA1", **kw):
    b = FakeBroker(closes={s: float(md.close[s].iloc[-1]) for s in md.symbols}, **kw)
    b.account = lambda: {"account_number": number, "status": "ACTIVE", "equity": "100000", "cash": "100000"}
    return b


EW = {"name": "equal_weight_buy_hold", "ref": "strategies.baselines.buy_hold:EqualWeightBuyHold",
      "params": {"rebalance_every": 21}, "timeframe": "1Day"}


def test_one_funds_failure_does_not_stop_another(monkeypatch, tmp_path):
    syms = execute.config.universe()["symbols"]
    md = _fresh(syms)
    monkeypatch.setattr(execute, "load_alpaca", lambda *a, **k: md)
    good, bad = _broker(md, "PA1"), _broker(md, "PA2")
    bad.account = lambda: (_ for _ in ()).throw(RuntimeError("401 unauthorized"))
    _setup(monkeypatch, tmp_path, {2: bad, 5: good}, {2: EW, 5: EW, 7: EW})
    out = tmp_path / "out"
    assert execute.main(["--out", str(out)]) == 2          # fails visibly
    assert len(good.submitted) == len(syms) and bad.submitted == []
    recs = {json.loads(f.read_text())["fund"]: json.loads(f.read_text()) for f in out.glob("*.json")}
    assert set(recs) == {2, 5}                             # fund 7 has no keys: skipped, nothing recorded
    assert recs[2]["status"].startswith("NO ORDERS") and recs[5]["status"] == f"submitted {len(syms)} orders"
    assert all(o["client_order_id"].startswith("tdf-f5-") for o in recs[5]["submitted"])


def test_two_funds_on_one_account_refuse(monkeypatch, tmp_path):
    syms = execute.config.universe()["symbols"]
    md = _fresh(syms)
    monkeypatch.setattr(execute, "load_alpaca", lambda *a, **k: md)
    shared = _broker(md, "PA9")
    _setup(monkeypatch, tmp_path, {3: shared, 4: shared}, {3: EW, 4: EW})
    assert execute.main(["--out", str(tmp_path / "out")]) == 2
    assert len(shared.submitted) == len(syms)              # fund 3 traded once; fund 4 refused


def test_no_keys_anywhere_fails_visibly(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path, {})
    assert execute.main(["--out", str(tmp_path / "out")]) == 2


@pytest.mark.parametrize("fund", funds.load(), ids=lambda f: f"fund{f.number}")
def test_every_assigned_strategy_runs_through_the_executor(monkeypatch, tmp_path, fund):
    syms = execute.config.universe()["symbols"]
    _, meta = execute.load_strategy(fund)
    md = _fresh(syms, int(meta["lookback"] * 1.5) + 30)
    monkeypatch.setattr(execute, "load_alpaca", lambda *a, **k: md)
    real = execute.extras.attach   # synthetic stand-ins for the SEC and news panels
    monkeypatch.setattr(execute.extras, "attach", lambda m, names, source: real(m, names, "synthetic"))
    b = _broker(md)
    _setup(monkeypatch, tmp_path, {fund.number: b})
    assert execute.main(["--out", str(tmp_path / "out"), "--fund", str(fund.number), "--dry-run"]) == 0
    rec = json.loads(next((tmp_path / "out").glob("*.json")).read_text())
    assert rec["status"].startswith(("dry run", "no decision yet")), rec["status"]
