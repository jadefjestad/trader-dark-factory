import pandas as pd
import pytest

from factory import execute, risk
from factory.data import synthetic

LIMITS = {"paper_only": True, "allow_short": False, "max_gross_exposure": 1.0, "max_position_weight": 0.15,
          "min_price": 5, "max_order_notional": 25000, "min_order_notional": 50, "max_orders_per_run": 60,
          "max_run_turnover": 1.0, "max_drawdown_halt": 0.2, "max_data_staleness_days": 4, "trading_enabled": True,
          "cash_buffer": 0.02, "price_buffer": 0.03, "max_price_gap": 0.25, "max_quote_age_minutes": 30,
          "hold_rebalance_tolerance": 0.03}


def test_account_must_be_paper():
    with pytest.raises(risk.RiskError):
        risk.check_account({"account_number": "123", "status": "ACTIVE"}, LIMITS)
    risk.check_account({"account_number": "PA123", "status": "ACTIVE"}, LIMITS)


def test_targets_limits():
    with pytest.raises(risk.RiskError):
        risk.check_targets({"AAPL": 0.3}, ["AAPL"], LIMITS)
    with pytest.raises(risk.RiskError):
        risk.check_targets({"AAPL": -0.1}, ["AAPL"], LIMITS)
    with pytest.raises(risk.RiskError):
        risk.check_targets({"XYZ": 0.1}, ["AAPL"], LIMITS)


def test_drawdown_halt():
    with pytest.raises(risk.RiskError):
        risk.check_drawdown(70_000, [100_000, 90_000], LIMITS)


def test_plan_orders_sells_first():
    orders = execute.plan_orders({"A": 0.1, "B": 0.0}, {"B": 10}, {"A": 100, "B": 50}, 100_000, 50)
    assert orders[0] == {"symbol": "B", "qty": 10, "side": "sell"}
    assert orders[1] == {"symbol": "A", "qty": 100, "side": "buy"}


def test_plan_orders_tolerance_skips_small_drift():
    orders = execute.plan_orders({"A": 0.10, "B": 0.10}, {"A": 110, "B": 0}, {"A": 100, "B": 100}, 100_000, 50, 0.03)
    assert orders == [{"symbol": "B", "qty": 100, "side": "buy"}]


def test_decide_hold_and_nan():
    w = pd.DataFrame({"A": [0.1, float("nan")], "B": [0.0, float("nan")]})
    assert execute.decide(w, ["A", "B"]) == ({"A": 0.1, "B": 0.0}, True)
    with pytest.raises(risk.RiskError):
        execute.decide(pd.DataFrame({"A": [0.1], "B": [float("nan")]}), ["A", "B"])


@pytest.fixture(autouse=True)
def seed_champion(monkeypatch, tmp_path_factory):
    """Executor tests use the equal-weight baseline, whatever state/champion.json currently promotes."""
    import json
    p = tmp_path_factory.mktemp("seed") / "champion.json"   # not in tmp_path, where tests read run records
    p.write_text(json.dumps({"ref": "strategies.baselines.buy_hold:EqualWeightBuyHold",
                             "params": {"rebalance_every": 21}, "name": "equal_weight_buy_hold", "timeframe": "1Day"}))
    monkeypatch.setattr(execute, "CHAMPION", p)


class FakeBroker:
    def __init__(self, positions=None, fail_after=None, closes=None):
        self.submitted = []
        self._positions = positions or []
        self.fail_after = fail_after
        self.closes = closes or {}

    def account(self):
        return {"account_number": "PA1", "status": "ACTIVE", "equity": "100000", "cash": "100000"}

    def latest_trades(self, symbols, feed="iex"):
        now = pd.Timestamp.now(tz="UTC").isoformat()
        return {s: (self.closes[s], now) for s in symbols}

    def portfolio_history(self):
        return {"equity": [100000]}

    def clock(self):
        return {"is_open": True}

    def open_orders(self):
        return []

    def calendar(self, start, end):
        return [{"date": d.strftime("%Y-%m-%d")} for d in pd.bdate_range(start, end)]

    def positions(self):
        return self._positions

    def submit_order(self, *a):
        if self.fail_after is not None and len(self.submitted) >= self.fail_after:
            raise RuntimeError("connection reset")
        self.submitted.append(a)
        return {"id": "x"}


def _patch(monkeypatch, md, **kw):
    broker = FakeBroker(closes={s: float(md.close[s].iloc[-1]) for s in md.symbols}, **kw)
    monkeypatch.setattr(execute, "PaperBroker", lambda: broker)
    monkeypatch.setattr(execute, "load_alpaca", lambda *a, **k: md)
    return broker


def test_stale_data_places_no_orders(monkeypatch, tmp_path):
    syms = execute.config.universe()["symbols"]
    md = synthetic(syms, "2024-01-01", "2024-06-28")        # months old
    broker = _patch(monkeypatch, md)
    assert execute.main(["--out", str(tmp_path)]) == 2
    assert broker.submitted == []


def test_missing_symbol_places_no_orders(monkeypatch, tmp_path):
    syms = execute.config.universe()["symbols"]
    today = pd.Timestamp.now(tz="America/New_York").normalize().tz_localize(None)
    md = synthetic(syms[:-1], "2025-01-01", (today - pd.Timedelta(days=1)).strftime("%Y-%m-%d"))
    broker = _patch(monkeypatch, md)
    assert execute.main(["--out", str(tmp_path)]) == 2
    assert broker.submitted == []


def _fresh(syms):
    today = pd.Timestamp.now(tz="America/New_York").normalize().tz_localize(None)
    prev = pd.bdate_range(today - pd.Timedelta(days=10), today - pd.Timedelta(days=1))[-1]
    return synthetic(syms, "2025-01-01", prev.strftime("%Y-%m-%d"))


def test_fresh_data_submits_orders(monkeypatch, tmp_path):
    syms = execute.config.universe()["symbols"]
    broker = _patch(monkeypatch, _fresh(syms))
    assert execute.main(["--out", str(tmp_path)]) == 0
    assert len(broker.submitted) == len(syms)


def test_foreign_position_places_no_orders(monkeypatch, tmp_path):
    syms = execute.config.universe()["symbols"]
    broker = _patch(monkeypatch, _fresh(syms), positions=[{"symbol": "ZZZ", "qty": "5"}])
    assert execute.main(["--out", str(tmp_path)]) == 2
    assert broker.submitted == []


def test_partial_failure_keeps_submitted_orders(monkeypatch, tmp_path):
    import json
    syms = execute.config.universe()["symbols"]
    broker = _patch(monkeypatch, _fresh(syms), fail_after=3)
    assert execute.main(["--out", str(tmp_path)]) == 2
    rec = json.loads(next(tmp_path.glob("*.json")).read_text())
    assert len(rec["submitted"]) == 3 and rec["status"].startswith("STOPPED AFTER 3 ORDER(S)")
    assert "pending" in rec


def test_dry_run_when_market_closed_uses_last_trades(monkeypatch, tmp_path):
    import json
    syms = execute.config.universe()["symbols"]
    broker = _patch(monkeypatch, _fresh(syms))
    broker.clock = lambda: {"is_open": False}
    old = (pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=2)).isoformat()
    broker.latest_trades = lambda symbols, feed="iex": {s: (broker.closes[s], old) for s in symbols}
    assert execute.main(["--out", str(tmp_path), "--dry-run"]) == 0
    rec = json.loads(next(tmp_path.glob("*.json")).read_text())
    assert rec["status"].startswith("dry run") and len(rec["orders"]) == len(syms) and broker.submitted == []
