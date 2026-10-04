"""The promoted champion in state/champion.json must run end to end through the executor."""
import pandas as pd

from factory import execute
from factory.data import synthetic
from tests.test_risk_and_execute import _patch


def test_current_champion_places_orders(monkeypatch, tmp_path):
    syms = execute.config.universe()["symbols"]
    _, meta = execute.load_champion()
    today = pd.Timestamp.now(tz="America/New_York").normalize().tz_localize(None)
    prev = pd.bdate_range(today - pd.Timedelta(days=10), today - pd.Timedelta(days=1))[-1]
    start = prev - pd.tseries.offsets.BDay(int(meta["lookback"] * 1.5) + 30)
    md = synthetic(syms, start.strftime("%Y-%m-%d"), prev.strftime("%Y-%m-%d"))
    broker = _patch(monkeypatch, md)
    assert execute.main(["--out", str(tmp_path)]) == 0
    assert broker.submitted, "champion produced no orders from a flat account"
