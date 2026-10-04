import datetime as dt
import json

from factory import report


class Broker:
    def account(self):
        return {"equity": "101000", "last_equity": "100000", "cash": "5000"}

    def portfolio_history(self):
        return {"equity": [100000, 102000, 101000]}

    def positions(self):
        return [{"symbol": "AAPL"}]


def test_report_lists_recent_activity(tmp_path):
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    (tmp_path / "experiments").mkdir()
    (tmp_path / "executions").mkdir()
    (tmp_path / "experiments" / "index.jsonl").write_text(
        json.dumps({"strategy": "sma_trend", "evaluated_at": now, "passed_gates": True, "promote": False}) + "\n"
        + json.dumps({"strategy": "old", "evaluated_at": "2020-01-01T00:00:00+00:00", "promote": True}) + "\n")
    (tmp_path / "executions" / "index.jsonl").write_text(json.dumps({"started_at": now, "status": "submitted 3 orders"}) + "\n")
    text = report.build(tmp_path, Broker(), "| usage |")
    assert "sma_trend`: passed gates" in text and "`old`" not in text
    assert "submitted 3 orders" in text and "$101,000" in text and "+1.00%" in text and "| usage |" in text


def test_report_survives_broker_errors(tmp_path):
    class Bad:
        def account(self):
            raise RuntimeError("401")
    assert "could not read account" in report.build(tmp_path, Bad())


def test_execution_quality_signs_costs_against_us(tmp_path):
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    (tmp_path / "executions").mkdir()
    (tmp_path / "executions" / "run.json").write_text(json.dumps({
        "started_at": now, "prices": {"AAPL": 100.0, "MSFT": 200.0},
        "submitted": [{"client_order_id": "a", "symbol": "AAPL", "side": "buy"},
                      {"client_order_id": "m", "symbol": "MSFT", "side": "sell"}]}))

    class B(Broker):
        def closed_orders(self, after):
            return [{"client_order_id": "a", "filled_avg_price": "100.10"},   # paid 10 bps more
                    {"client_order_id": "m", "filled_avg_price": "199.60"},   # sold 20 bps lower
                    {"client_order_id": "other", "filled_avg_price": "1"}]
    line = report.execution_quality(tmp_path, B())[0]
    assert "2 fills" in line and "mean cost +15.0 bps" in line and "above the backtest assumption" in line
