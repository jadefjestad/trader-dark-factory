import pandas as pd
import pytest

from factory import execute, risk
from factory.data import synthetic

LIMITS = {"paper_only": True, "allow_short": False, "max_gross_exposure": 1.0, "max_position_weight": 0.15,
          "min_price": 5, "max_order_notional": 25000, "min_order_notional": 50, "max_orders_per_run": 60,
          "max_run_turnover": 1.0, "max_drawdown_halt": 0.2, "max_data_staleness_days": 4, "trading_enabled": True}


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


def test_plan_orders_sells_first_and_ignores_foreign_positions():
    orders = execute.plan_orders({"A": 0.1, "B": 0.0}, {"B": 10, "ZZZ": 5}, {"A": 100, "B": 50}, 100_000, 50)
    assert orders[0] == {"symbol": "B", "qty": 10, "side": "sell"}
    assert orders[1] == {"symbol": "A", "qty": 100, "side": "buy"}


class FakeBroker:
    def __init__(self, *a, **k):
        self.submitted = []

    def account(self):
        return {"account_number": "PA1", "status": "ACTIVE", "equity": "100000"}

    def portfolio_history(self):
        return {"equity": [100000]}

    def clock(self):
        return {"is_open": True}

    def open_orders(self):
        return []

    def calendar(self, start, end):
        return [{"date": d.strftime("%Y-%m-%d")} for d in pd.bdate_range(start, end)]

    def positions(self):
        return []

    def submit_order(self, *a):
        self.submitted.append(a)
        return {"id": "x"}


def _patch(monkeypatch, md):
    broker = FakeBroker()
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


def test_fresh_data_submits_orders(monkeypatch, tmp_path):
    syms = execute.config.universe()["symbols"]
    today = pd.Timestamp.now(tz="America/New_York").normalize().tz_localize(None)
    prev = pd.bdate_range(today - pd.Timedelta(days=10), today - pd.Timedelta(days=1))[-1]
    md = synthetic(syms, "2025-01-01", prev.strftime("%Y-%m-%d"))
    broker = _patch(monkeypatch, md)
    assert execute.main(["--out", str(tmp_path)]) == 0
    assert len(broker.submitted) == len(syms)
