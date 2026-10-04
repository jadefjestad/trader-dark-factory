import pandas as pd
import pytest

from factory import extras, runner
from factory.data import DataError, synthetic

STRAT = '''
from strategies.base import Strategy


class EchoNews(Strategy):
    name = "echo_news"
    lookback = 5
    extra_data = ("news_count",)

    def target_weights(self, md):
        n = md.extra["news_count"]
        return n.div(n.sum(axis=1).where(lambda s: s > 0), axis=0).fillna(0.0)
'''


def test_panel_reaches_strategy_and_slices_with_rows(tmp_path, monkeypatch):
    md = extras.attach(synthetic(["AAPL", "MSFT"], start="2024-01-01", end="2024-03-01"), ["news_count"], "synthetic")
    f = tmp_path / "echo_news.py"
    f.write_text(STRAT)
    ref = str(f)
    assert runner.describe(ref)["extra_data"] == ["news_count"]
    full, part = runner.run(ref, md, [{}, {"rows": 20, "start": 5}])
    n = md.extra["news_count"]
    expect = n.div(n.sum(axis=1).where(lambda s: s > 0), axis=0).fillna(0.0)
    pd.testing.assert_frame_equal(full, expect, check_freq=False)
    pd.testing.assert_frame_equal(part, expect.iloc[5:20], check_freq=False)


def test_select_and_slice_keep_panels():
    md = extras.attach(synthetic(["AAPL", "MSFT", "SPY"], start="2024-01-01", end="2024-02-01"), ["news_count"], "synthetic")
    sub = md.select(["AAPL"]).slice(None, "2024-01-15")
    assert list(sub.extra["news_count"].columns) == ["AAPL"]
    assert sub.extra["news_count"].index.equals(sub.index)


def test_unknown_panel_fails_closed():
    md = synthetic(["AAPL"], start="2024-01-01", end="2024-02-01")
    with pytest.raises(DataError):
        extras.attach(md, ["tweets"], "synthetic")
