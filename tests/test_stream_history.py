import datetime as dt

import pandas as pd
import pytest

from factory.stream import history

T0 = "2026-10-02T13:30:00"


def _trades():
    body = {"trades": {"AAPL": [{"t": f"{T0}.100Z", "p": 100.0, "s": 10},
                                {"t": f"{T0}.900Z", "p": 101.0, "s": 5},
                                {"t": "2026-10-02T13:30:04.999Z", "p": 99.0, "s": 1},
                                {"t": "2026-10-02T13:30:11Z", "p": 102.0, "s": 2}],
                       "MSFT": [{"t": f"{T0}.500Z", "p": 400.0, "s": 3}]}}
    return history.parse("trades", body)


def _quotes():
    body = {"quotes": {"AAPL": [{"t": f"{T0}.050Z", "bp": 99.9, "ap": 100.1, "bs": 1, "as": 2},
                                {"t": "2026-10-02T13:30:05Z", "bp": 98.0, "ap": 98.2, "bs": 1, "as": 1}]}}
    return history.parse("quotes", body)


def test_parse_shapes_and_types():
    t, q = _trades(), _quotes()
    assert list(t.columns) == history.TRADE_COLUMNS and len(t) == 5 and str(t["time"].dt.tz) == "UTC"
    assert list(q.columns) == ["time", "symbol", "bid", "ask", "bid_size", "ask_size"] and q["ask_size"].iloc[0] == 2.0


def test_seconds_bars_label_by_end_and_fill_gaps():
    b = history.seconds_bars(_trades(), _quotes(), 5)
    e1 = pd.Timestamp("2026-10-02 13:30:05", tz="UTC")
    assert b["open"].loc[e1, "AAPL"] == 100.0 and b["high"].loc[e1, "AAPL"] == 101.0
    assert b["close"].loc[e1, "AAPL"] == 99.0 and b["volume"].loc[e1, "AAPL"] == 16
    e2 = e1 + pd.Timedelta(seconds=5)       # no AAPL trade: previous close, zero volume
    assert b["close"].loc[e2, "AAPL"] == 99.0 and b["volume"].loc[e2, "AAPL"] == 0
    assert b["bid"].loc[e1, "AAPL"] == 99.9 and b["bid"].loc[e2, "AAPL"] == 98.0


def test_a_print_at_the_bar_end_belongs_to_the_next_bar():
    # leakage test: nothing stamped at or after a bar's end may change that bar
    base = history.seconds_bars(_trades(), _quotes(), 5)
    late = pd.DataFrame([{"time": pd.Timestamp("2026-10-02 13:30:05", tz="UTC"), "symbol": "AAPL",
                          "price": 500.0, "size": 1000.0}])
    more = history.seconds_bars(pd.concat([_trades(), late], ignore_index=True), _quotes(), 5)
    e1 = pd.Timestamp("2026-10-02 13:30:05", tz="UTC")
    for k in ("open", "high", "low", "close", "volume"):
        assert more[k].loc[e1, "AAPL"] == base[k].loc[e1, "AAPL"]
    assert more["close"].loc[e1 + pd.Timedelta(seconds=5), "AAPL"] == 500.0


def test_bad_bar_length():
    with pytest.raises(ValueError):
        history.seconds_bars(_trades(), None, 7)


class _Resp:
    def __init__(self, status, body=None):
        self.status_code, self._body = status, body or {}

    def json(self):
        return self._body


def test_fetch_follows_pages_and_caches_completed_days(monkeypatch, tmp_path):
    monkeypatch.setattr(history, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(history, "_alpaca_headers", lambda: {})
    monkeypatch.setattr(history.time, "sleep", lambda s: None)
    pages = [{"trades": {"AAPL": [{"t": f"{T0}.1Z", "p": 1, "s": 1}]}, "next_page_token": "x"},
             {"trades": {"AAPL": [{"t": f"{T0}.2Z", "p": 2, "s": 1}]}, "next_page_token": None}]
    calls = []

    def get(url, params, headers):
        calls.append(dict(params))
        return _Resp(200, pages[len(calls) - 1])
    monkeypatch.setattr(history, "_get", get)
    df = history.load_day("trades", ["AAPL"], dt.date(2026, 10, 2))
    assert list(df["price"]) == [1.0, 2.0] and calls[1]["page_token"] == "x"
    again = history.load_day("trades", ["AAPL"], dt.date(2026, 10, 2))
    assert len(calls) == 2 and list(again["price"]) == [1.0, 2.0]


def test_fetch_fails_closed(monkeypatch, tmp_path):
    monkeypatch.setattr(history, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(history, "_alpaca_headers", lambda: {})
    monkeypatch.setattr(history.time, "sleep", lambda s: None)
    monkeypatch.setattr(history, "_get", lambda *a, **k: _Resp(401))
    with pytest.raises(history.DataError):
        history.load_day("quotes", ["AAPL"], dt.date(2026, 10, 2))
