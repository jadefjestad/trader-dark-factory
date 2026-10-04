import datetime as dt

from factory.stream.bars import BarBuilder
from factory.stream.feed import FeedGuard
from factory.stream.throttle import OrderThrottle, client_order_id

T0 = dt.datetime(2026, 10, 5, 10, 0, 0)


def at(s):
    return T0 + dt.timedelta(seconds=s)


def test_bars_are_never_emitted_early_and_carry_available_at():
    b = BarBuilder(["AAPL"], 5)
    b.on_trade("AAPL", 100.0, 10, at(0.5))
    b.on_trade("AAPL", 101.0, 5, at(3))
    assert b.close_until(at(4.9)) == []
    [bar] = b.close_until(at(5.2))
    assert (bar.open, bar.high, bar.low, bar.close, bar.volume) == (100.0, 101.0, 100.0, 101.0, 15)
    assert bar.end == at(5) and bar.available_at == at(5.2) and bar.filled


def test_quiet_interval_repeats_close_unfilled_and_late_prints_are_ignored():
    b = BarBuilder(["AAPL"], 5)
    b.on_trade("AAPL", 100.0, 10, at(1))
    b.close_until(at(5))
    b.on_trade("AAPL", 999.0, 1, at(4))           # belongs to an emitted bar: dropped
    [quiet] = b.close_until(at(10))
    assert quiet.close == 100.0 and quiet.volume == 0 and not quiet.filled


def test_trades_in_two_intervals_before_close_keep_both_bars():
    b = BarBuilder(["AAPL"], 5)
    b.on_trade("AAPL", 100.0, 1, at(1))
    b.on_trade("AAPL", 102.0, 1, at(6))
    bars = b.close_until(at(10))
    assert [x.close for x in bars] == [100.0, 102.0]


def test_feed_guard_rejects_bad_data_and_reports_staleness():
    g = FeedGuard(["AAPL", "MSFT"], max_symbol_gap_s=30, max_feed_gap_s=10)
    assert g.feed_stale(at(0))
    assert g.accept_trade("AAPL", 100.0, 5, at(0))
    assert not g.accept_trade("AAPL", 120.0, 5, at(1))      # 20% jump
    assert not g.accept_trade("AAPL", -1.0, 5, at(1))
    assert not g.accept_quote("AAPL", 100.0, 100.0, at(1))  # locked
    assert not g.accept_trade("TSLA", 100.0, 5, at(1))      # not in universe
    assert g.stale_symbols(at(5)) == {"MSFT"}
    assert g.feed_stale(at(11)) and g.stale_symbols(at(11)) == {"AAPL", "MSFT"}


def test_throttle_enforces_spacing_budget_and_daily_cap():
    th = OrderThrottle(per_minute=2, per_day=3, min_seconds_per_symbol=30)
    assert th.allow("AAPL", at(0))[0]
    assert th.allow("AAPL", at(10)) == (False, "symbol traded too recently")
    assert th.allow("MSFT", at(10))[0]
    assert th.allow("NVDA", at(11)) == (False, "per-minute order budget")
    assert th.allow("NVDA", at(45))[0]                         # refilled
    assert th.allow("KO", at(200)) == (False, "daily order cap")
    assert th.allow("KO", at(200) + dt.timedelta(days=1))[0]


def test_client_order_ids_are_deterministic():
    assert client_order_id(dt.date(2026, 10, 5), 7) == "stream-20261005-00007"
