import pandas as pd

from factory import extras, macro
from factory.data import synthetic


def test_panel_uses_only_values_dated_before_the_bar():
    raw = pd.DataFrame({"T10Y2Y": [1.0, 2.0, None, 4.0]},
                       index=pd.to_datetime(["2024-03-06", "2024-03-07", "2024-03-08", "2024-03-11"]))
    idx = pd.DatetimeIndex(pd.to_datetime(["2024-03-07", "2024-03-08", "2024-03-11", "2024-03-12"]))
    p = macro.panel(raw, idx)
    # Thu sees Wed, Fri sees Thu, Mon sees Fri (missing, so Thu forward-filled), Tue sees Mon
    assert p["T10Y2Y"].tolist() == [1.0, 2.0, 2.0, 4.0]


def test_macro_panel_survives_symbol_selection():
    md = extras.attach(synthetic(["AAPL", "MSFT", "SPY"], start="2024-01-01", end="2024-02-01"),
                       ["macro", "news_count"], "synthetic")
    sub = md.select(["AAPL", "MSFT"])
    assert list(sub.extra["macro"].columns) == list(macro.SERIES)
    assert list(sub.extra["news_count"].columns) == ["AAPL", "MSFT"]
