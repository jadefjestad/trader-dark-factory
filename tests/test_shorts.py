import datetime as dt

import pandas as pd

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
