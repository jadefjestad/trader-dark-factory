import datetime as dt

import pandas as pd

from factory import intraday_probe as ip


def frame(sym, closes, vols, start="2026-10-01 09:30"):
    t = pd.date_range(start, periods=len(closes), freq="1min", tz="America/New_York")
    return pd.DataFrame({"symbol": sym, "t": t, "c": closes, "v": vols})


def test_compare_measures_share_coverage_and_gap():
    sip = frame("AAPL", [100.0, 100.0, 100.0, 100.0], [1000, 1000, 1000, 1000])
    iex = frame("AAPL", [100.01, 100.0], [30, 20])          # 2 of 4 minutes, one 1 bp off
    out = ip.compare_minute_bars(iex, sip, sessions=1)
    assert out["iex_volume_share"]["median"] == 0.0125
    assert abs(out["iex_minute_coverage"]["median"] - 2 / 390) < 1e-4
    assert abs(out["close_gap_bps_median"]["median"] - 0.5) < 1e-3


def test_compare_handles_symbol_missing_on_iex():
    out = ip.compare_minute_bars(frame("AAPL", [1.0], [0])[:0], frame("MSFT", [10.0], [5]), sessions=1)
    assert out["symbols"] == 1 and out["close_gap_bps_median"] is None


def test_recent_sessions_skips_weekends():
    assert ip.recent_sessions(dt.date(2026, 10, 5), 2) == [dt.date(2026, 10, 1), dt.date(2026, 10, 2)]


def test_probe_never_raises(monkeypatch):
    def boom(*a, **k):
        raise ConnectionError("no network")
    monkeypatch.setattr(ip, "_get", boom)
    monkeypatch.setenv("ALPACA_API_KEY_ID", "x")
    monkeypatch.setenv("ALPACA_API_SECRET_KEY", "y")
    monkeypatch.delenv("TIINGO_API_KEY", raising=False)
    monkeypatch.delenv("TWELVEDATA_API_KEY", raising=False)
    res = ip.probe(days=1)
    assert set(res) == {"feeds", "spreads", "limits", "third_party"}
    assert "error" in res["feeds"] and res["third_party"]["tiingo"].startswith("not configured")
