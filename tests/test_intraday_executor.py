import json

import pandas as pd
import pytest

from factory import config, funds, intraday
from factory.backtest import _flatten_intraday
from factory.data import DataError, synthetic

SYMS = config.universe()["symbols"]
REF = "strategies/candidates/intraday_hourly_reversal.py"
DAY = "2026-10-06"


def _fund(n=5, ref=REF):
    block = {"name": "intraday_hourly_reversal", "ref": ref, "timeframe": "15Min",
             "code_sha256": config.file_sha256(config.ROOT / ref), "experiment_id": "test", "params": None}
    return funds.Fund(n, "Test", "🧪", block)


class FakeBroker:
    def __init__(self, md, positions=None, equity=100_000, last_equity=100_000, close="16:00"):
        self.md, self.submitted, self.cancelled = md, [], 0
        self._positions = positions or []
        self.equity, self.last_equity = equity, last_equity
        self.close = pd.Timestamp(f"{DAY} {close}", tz="America/New_York")

    def account(self):
        return {"account_number": "PA5", "status": "ACTIVE", "equity": str(self.equity),
                "last_equity": str(self.last_equity), "cash": str(self.equity)}

    def portfolio_history(self):
        return {"equity": [100_000]}

    def clock(self):
        return {"is_open": True, "next_close": self.close.isoformat()}

    def open_orders(self):
        return []

    def cancel_open_orders(self):
        self.cancelled += 1

    def closed_orders(self, after):
        return []

    def positions(self):
        return self._positions

    def latest_trades(self, symbols, feed="iex"):
        now = pd.Timestamp.now(tz="UTC").isoformat()
        return {s: (float(self.md.close[s].dropna().iloc[-1]), now) for s in symbols}

    def submit_order(self, *a):
        self.submitted.append(a)
        return {"id": "x"}


def _md():
    return synthetic(SYMS, "2026-09-21", DAY, timeframe="15Min")


def _patch(monkeypatch, broker, md=None, fail_data=False):
    def load(*a, **k):
        if fail_data:
            raise DataError("feed down")
        return md
    monkeypatch.setattr(intraday, "PaperBroker", lambda *a, **k: broker)
    monkeypatch.setattr(intraday, "load_alpaca", load)
    monkeypatch.setattr(intraday, "wait_for_fills", lambda b: None)


def _now(hhmm):
    return pd.Timestamp(f"{DAY} {hhmm}:45", tz="America/New_York")


def test_completed_bars_drop_the_bar_in_progress_and_fill_short_gaps():
    md = _md()
    md.close.loc[pd.Timestamp(f"{DAY} 10:15", tz="America/New_York"), "AAPL"] = float("nan")
    out = intraday.completed_bars(md, _now("10:30"), 15, 2)
    assert out.index[-1] == pd.Timestamp(f"{DAY} 10:15", tz="America/New_York")
    assert not out.close.iloc[-1].isna().any()
    md.close.loc[pd.Timestamp(f"{DAY} 09:45", tz="America/New_York"):pd.Timestamp(f"{DAY} 10:15", tz="America/New_York"), "MSFT"] = float("nan")
    with pytest.raises(DataError):
        intraday.completed_bars(md, _now("10:30"), 15, 2)


def test_decision_bar_buys_the_strategy_targets(monkeypatch, tmp_path):
    md = _md()
    broker = FakeBroker(md)
    _patch(monkeypatch, broker, md)
    # 11:00 ET decision reads the 10:45 bar: bar 5 of the session, flat before the first 90-minute decision
    assert intraday.run_fund(_fund(), ("k", "s"), False, tmp_path, {}, _now("11:00")) == 0
    assert broker.submitted == []
    # 11:15 ET reads the 11:00 bar, bar 6: buy the five worst names of the last 90 minutes at 10% each
    assert intraday.run_fund(_fund(), ("k", "s"), False, tmp_path, {}, _now("11:15")) == 0
    assert len(broker.submitted) == 5 and all(o[2] == "buy" for o in broker.submitted)
    assert all(o[3].startswith("tdf-f5-202610061100-") for o in broker.submitted)


def test_end_of_session_flattens_without_needing_data(monkeypatch, tmp_path):
    md = _md()
    held = [{"symbol": "AAPL", "qty": "30", "current_price": str(float(md.close["AAPL"].iloc[-1]))}]
    broker = FakeBroker(md, positions=held)
    _patch(monkeypatch, broker, fail_data=True)
    assert intraday.run_fund(_fund(), ("k", "s"), False, tmp_path, {}, _now("15:45")) == 0
    assert broker.submitted and broker.submitted[0][:3] == ("AAPL", 30, "sell")
    rec = json.loads(next(tmp_path.glob("*.json")).read_text())
    assert "end of session" in rec["note"]


def test_early_close_moves_the_flatten_earlier(monkeypatch, tmp_path):
    md = _md()
    held = [{"symbol": "AAPL", "qty": "30", "current_price": str(float(md.close["AAPL"].iloc[-1]))}]
    broker = FakeBroker(md, positions=held, close="13:00")
    _patch(monkeypatch, broker, fail_data=True)
    assert intraday.run_fund(_fund(), ("k", "s"), False, tmp_path, {}, _now("12:45")) == 0
    assert broker.submitted[0][:3] == ("AAPL", 30, "sell")


def test_daily_loss_stop_flattens_and_stays_flat(monkeypatch, tmp_path):
    md = _md()
    held = [{"symbol": "MSFT", "qty": "10", "current_price": str(float(md.close["MSFT"].iloc[-1]))}]
    broker = FakeBroker(md, positions=held, equity=96_000, last_equity=100_000)
    _patch(monkeypatch, broker, md)
    shared = {}
    assert intraday.run_fund(_fund(), ("k", "s"), False, tmp_path, shared, _now("11:15")) == 0
    assert broker.submitted == [("MSFT", 10, "sell", broker.submitted[0][3])]
    broker._positions, broker.equity = [], 99_000          # recovered, but the stop holds for the day
    assert intraday.run_fund(_fund(), ("k", "s"), False, tmp_path, shared, _now("11:30")) == 0
    assert len(broker.submitted) == 1


def test_stale_or_missing_data_places_no_orders(monkeypatch, tmp_path):
    md = _md().slice(None, pd.Timestamp(f"{DAY} 10:00", tz="America/New_York"))   # feed stopped at 10:15
    broker = FakeBroker(md)
    _patch(monkeypatch, broker, md)
    assert intraday.run_fund(_fund(), ("k", "s"), False, tmp_path, {}, _now("11:15")) == 2
    _patch(monkeypatch, broker, fail_data=True)
    assert intraday.run_fund(_fund(), ("k", "s"), False, tmp_path, {}, _now("11:15")) == 2
    assert broker.submitted == []
    recs = [json.loads(p.read_text()) for p in tmp_path.glob("*.json")]
    assert all(r["status"].startswith("NO ORDERS") for r in recs)


def test_hash_mismatch_places_no_orders(monkeypatch, tmp_path):
    md = _md()
    broker = FakeBroker(md)
    _patch(monkeypatch, broker, md)
    f = _fund()
    bad = funds.Fund(f.number, f.name, f.emoji, {**f.strategy, "code_sha256": "0" * 64})
    assert intraday.run_fund(bad, ("k", "s"), False, tmp_path, {}, _now("11:15")) == 2
    assert broker.submitted == []


def test_live_flatten_matches_the_backtester():
    """Decisions the backtester zeroes are exactly those the executor makes flat."""
    md = _md().slice(pd.Timestamp(DAY, tz="America/New_York"), None)
    w = pd.DataFrame(0.1, index=md.index, columns=md.symbols)
    zeroed = (_flatten_intraday(w).sum(axis=1) == 0)
    close = pd.Timestamp(f"{DAY} 16:00", tz="America/New_York")
    bar = pd.Timedelta(minutes=15)
    live = pd.Series([b + bar * 2 >= close for b in md.index], index=md.index)
    assert (zeroed == live).all()


def test_daily_executor_leaves_intraday_funds_alone(tmp_path):
    daily = funds.Fund(4, "D", "📈", {"name": "x", "ref": "y", "timeframe": "1Day"})
    assert funds.timeframe_of(_fund()) == "15Min" and funds.timeframe_of(daily) == "1Day"
    assert funds.timeframe_of(funds.Fund(1, "C", "💀", "champion")) == "1Day"


def test_next_decision_waits_for_the_bar_to_complete():
    t = pd.Timestamp(f"{DAY} 10:14:10", tz="America/New_York")
    assert intraday.next_decision(t, 15, 45) == pd.Timestamp(f"{DAY} 10:15:45", tz="America/New_York")
    t = pd.Timestamp(f"{DAY} 10:15:20", tz="America/New_York")
    assert intraday.next_decision(t, 15, 45) == pd.Timestamp(f"{DAY} 10:15:45", tz="America/New_York")


@pytest.mark.parametrize("fund", [f for f in funds.load() if not f.benchmark and funds.timeframe_of(f) != "1Day"],
                         ids=lambda f: f"fund{f.number}")
def test_every_assigned_intraday_strategy_runs_through_the_intraday_executor(monkeypatch, tmp_path, fund):
    md = _md()
    for hhmm in ("10:00", "11:15", "13:00", "15:45"):
        broker = FakeBroker(md)
        _patch(monkeypatch, broker, md)
        assert intraday.run_fund(fund, ("k", "s"), True, tmp_path, {}, _now(hhmm)) == 0


def test_daily_executor_skips_intraday_funds():
    from factory import execute
    daily = [f.number for f in funds.load() if not f.benchmark and funds.timeframe_of(f, execute.CHAMPION) == "1Day"]
    assert set(daily) | {f.number for f in intraday.intraday_funds()} == {f.number for f in funds.load() if not f.benchmark}


def test_closed_market_dry_run_previews_on_the_last_bars(monkeypatch, tmp_path):
    md = _md().slice(None, pd.Timestamp(f"{DAY} 11:00", tz="America/New_York"))
    broker = FakeBroker(md)
    broker.clock = lambda: {"is_open": False, "next_close": "2026-10-07T16:00:00-04:00"}
    _patch(monkeypatch, broker, md)
    assert intraday.run_fund(_fund(), ("k", "s"), True, tmp_path, {}, _now("19:00")) == 0
    rec = json.loads(next(tmp_path.glob("*.json")).read_text())
    assert rec["status"].startswith("dry run") and len(rec["orders"]) == 5 and broker.submitted == []
    # a real run on stale bars still refuses
    broker.clock = lambda: {"is_open": True, "next_close": "2026-10-06T16:00:00-04:00"}
    assert intraday.run_fund(_fund(), ("k", "s"), False, tmp_path, {}, _now("14:00")) == 2
