from factory import config
from factory.stream.engine import StreamEngine


def test_stream_limits_exist_and_are_tighter_than_daily():
    lim = config.risk_limits()
    s = lim["stream"]
    assert s["max_gross_exposure"] <= lim["max_gross_exposure"]
    assert s["max_position_weight"] <= lim["max_position_weight"]
    assert 0 < s["max_daily_loss"] <= 0.02 and s["max_orders_per_minute"] <= 60
    h, m = map(int, s["flatten_at"].split(":"))
    assert (h, m) < (16, 0)


def test_engine_accepts_the_protected_stream_section():
    lim = config.risk_limits()
    StreamEngine(["AAPL"], 5, lambda md: {}, None, lim, lim["stream"], log=lambda r: None)
