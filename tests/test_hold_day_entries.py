from factory import execute


def test_hold_day_opens_small_new_positions():
    # a 2% target is inside the 3% drift tolerance but must still be bought when nothing is held
    orders = execute.plan_orders({"A": 0.02, "B": 0.10}, {"B": 100}, {"A": 100, "B": 100}, 100_000, 50, 0.03)
    assert orders == [{"symbol": "A", "qty": 20, "side": "buy"}]


def test_hold_day_closes_positions_targeted_at_zero():
    orders = execute.plan_orders({"A": 0.0}, {"A": 10}, {"A": 100}, 100_000, 50, 0.03)
    assert orders == [{"symbol": "A", "qty": 10, "side": "sell"}]
