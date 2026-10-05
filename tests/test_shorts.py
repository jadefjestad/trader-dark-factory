import datetime as dt

import pandas as pd
import pytest

from factory import shorts

SAMPLE = """Date|Symbol|ShortVolume|ShortExemptVolume|TotalVolume|Market
20261001|AAPL|4000|10|10000|B,Q,N
20261001|MSFT|1500|0|5000|B,Q,N
20261001|ZERO|0|0|0|Q
3
"""


def test_parse_daily_drops_trailer_and_empty_rows():
    rows = shorts.parse_daily(SAMPLE)
    assert list(rows["symbol"]) == ["AAPL", "MSFT"]
    assert rows["date"].iloc[0] == pd.Timestamp("2026-10-01")
    assert rows["short_volume"].iloc[0] == 4000 and rows["total_volume"].iloc[0] == 10000


def test_daily_file_is_usable_only_from_the_next_bar():
    idx = pd.bdate_range("2026-09-30", "2026-10-06")
    panel = shorts.short_volume_ratio_panel(shorts.parse_daily(SAMPLE), idx, ["AAPL", "MSFT", "KO"])
    assert panel.loc[:"2026-10-01"].isna().all().all()        # not on the trade date itself
    assert panel.loc["2026-10-02", "AAPL"] == 0.4 and panel.loc["2026-10-06", "MSFT"] == 0.3
    assert panel["KO"].isna().all()


def test_friday_file_waits_for_monday():
    rows = shorts.parse_daily(SAMPLE.replace("20261001", "20261002"))
    panel = shorts.short_volume_ratio_panel(rows, pd.bdate_range("2026-10-01", "2026-10-06"), ["AAPL"])
    assert pd.isna(panel.loc["2026-10-02", "AAPL"]) and panel.loc["2026-10-05", "AAPL"] == 0.4


def test_short_interest_waits_for_publication():
    # settled Sep 15, published ~7 business days later: usable from the business day after that
    assert shorts.available_from(pd.Series([pd.Timestamp("2026-09-15")]), shorts.PUBLICATION_LAG_BDAYS)[0] \
        == pd.Timestamp("2026-09-25")


def test_probe_never_raises(monkeypatch):
    def boom(*a, **k):
        raise ConnectionError("no network")
    monkeypatch.setattr(shorts, "_get", boom)
    monkeypatch.setattr(shorts, "_post", boom)
    res = shorts.probe()
    assert set(res) == {"regsho_daily", "short_interest"} and all("error" in v for v in res.values())


def test_last_weekday_skips_weekend():
    assert shorts.last_weekday(dt.date(2026, 10, 5)) == dt.date(2026, 10, 2)


class _Resp:
    def __init__(self, status, text=""):
        self.status_code, self.text = status, text


def test_fetch_days_skips_holidays_and_filters_symbols(monkeypatch):
    monkeypatch.setattr(shorts.time, "sleep", lambda s: None)
    days = [dt.date(2026, 9, d) for d in range(1, 31) if dt.date(2026, 9, d).weekday() < 5]
    def get(url):
        return _Resp(404) if "20260907" in url else _Resp(200, SAMPLE.replace("20261001", url[-12:-4]))
    monkeypatch.setattr(shorts, "_get", get)
    rows = shorts.fetch_days(days, ["AAPL"])
    assert set(rows["symbol"]) == {"AAPL"} and len(rows) == len(days) - 1


def test_fetch_days_fails_closed_when_many_missing(monkeypatch):
    monkeypatch.setattr(shorts.time, "sleep", lambda s: None)
    monkeypatch.setattr(shorts, "_get", lambda url: _Resp(403))
    try:
        shorts.fetch_days([dt.date(2026, 9, 1), dt.date(2026, 9, 2)], ["AAPL"])
    except shorts.DataError:
        return
    raise AssertionError("expected DataError")


def test_load_caches_complete_years(monkeypatch, tmp_path):
    monkeypatch.setattr(shorts, "CACHE_DIR", tmp_path)
    calls = []
    def fake(days, symbols, pause=0.2):
        calls.append(len(days))
        return shorts.parse_daily(SAMPLE.replace("20261001", "20220103"))
    monkeypatch.setattr(shorts, "fetch_days", fake)
    a = shorts.load(["AAPL"], "2022-01-01", "2022-12-31")
    b = shorts.load(["AAPL"], "2022-01-01", "2022-12-31")
    assert len(calls) == 1 and (tmp_path / "shorts_2022.csv.gz").exists() and len(a) == len(b) == 2


def test_synthetic_panel_attaches_through_extras():
    from factory import extras
    from factory.data import synthetic
    md = extras.attach(synthetic(["AAA", "BBB"], start="2024-01-01", end="2024-03-01"), ["short_volume_ratio"], "synthetic")
    p = md.extra["short_volume_ratio"]
    assert p.shape == md.close.shape and p.notna().all().all() and ((p >= 0) & (p <= 1)).all().all()


def test_real_panel_fails_closed_without_a_latest_value(monkeypatch):
    monkeypatch.setattr(shorts, "load", lambda *a, **k: shorts.parse_daily(SAMPLE))
    idx = pd.bdate_range("2026-09-01", "2026-09-30")          # before the only file: nothing usable
    try:
        shorts.panel(idx, ["AAPL"], "alpaca")
    except shorts.DataError:
        return
    raise AssertionError("expected DataError")


SI_RECS = [
    {"symbolCode": "AAPL", "settlementDate": "2026-09-15", "daysToCoverQuantity": 1.5},
    {"symbolCode": "AAPL", "settlementDate": "2026-08-31", "daysToCoverQuantity": 2.0},
    {"symbolCode": "AAPL", "settlementDate": "2026-09-15", "daysToCoverQuantity": 1.7},   # revision wins
    {"symbolCode": "MSFT", "settlementDate": "2026-09-15", "daysToCoverQuantity": None},
]


def test_parse_short_interest_sorts_and_keeps_revisions():
    rows = shorts.parse_short_interest(SI_RECS)
    assert list(rows["days_to_cover"]) == [2.0, 1.7] and set(rows["symbol"]) == {"AAPL"}


def test_days_to_cover_waits_for_publication_lag():
    rows = shorts.parse_short_interest(SI_RECS)
    idx = pd.bdate_range("2026-09-01", "2026-10-02")
    p = shorts.days_to_cover_panel(rows, idx, ["AAPL", "MSFT"])
    # 2026-08-31 settles; +7 bdays = 2026-09-09, usable from 2026-09-10
    assert pd.isna(p.loc["2026-09-09", "AAPL"]) and p.loc["2026-09-10", "AAPL"] == 2.0
    # 2026-09-15 settles; +7 bdays = 2026-09-24, usable from 2026-09-25
    assert p.loc["2026-09-24", "AAPL"] == 2.0 and p.loc["2026-09-25", "AAPL"] == 1.7
    assert p["MSFT"].isna().all()


def test_short_interest_fails_closed(monkeypatch, tmp_path):
    monkeypatch.setattr(shorts, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(shorts.time, "sleep", lambda s: None)
    monkeypatch.setattr(shorts, "_post", lambda *a, **k: _Resp(400))
    with pytest.raises(shorts.DataError):
        shorts.short_interest_panel(pd.bdate_range("2026-09-01", "2026-10-02"), ["AAPL"], "alpaca")


def test_short_interest_stale_fails_closed(monkeypatch):
    monkeypatch.setattr(shorts, "load_short_interest", lambda s: shorts.parse_short_interest(SI_RECS))
    with pytest.raises(shorts.DataError):
        shorts.short_interest_panel(pd.bdate_range("2026-11-01", "2026-12-31"), ["AAPL"], "alpaca")
    p = shorts.short_interest_panel(pd.bdate_range("2026-09-01", "2026-10-02"), ["AAPL"], "alpaca")
    assert p.iloc[-1, 0] == 1.7


def test_short_interest_synthetic_panel():
    from factory import extras
    from factory.data import synthetic
    md = extras.attach(synthetic(["AAA", "BBB"], start="2024-01-01", end="2024-06-01"), ["short_interest_days"], "synthetic")
    p = md.extra["short_interest_days"]
    assert p.shape[1] == 2 and p.notna().all().all() and (p > 0).all().all()
    assert p["AAA"].nunique() > 5          # steps twice a month, not daily noise
