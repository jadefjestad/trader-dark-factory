import json

from factory import readme


class Broker:
    def account(self):
        return {"equity": "101000", "last_equity": "100500", "cash": "2000"}

    def portfolio_history(self):
        return {"equity": [100000, 100500, 101000]}

    def positions(self):
        return [{"symbol": "KO", "qty": "110", "market_value": "7000", "unrealized_pl": "-12.5"}]


def _ledger(tmp_path):
    (tmp_path / "experiments").mkdir()
    (tmp_path / "executions").mkdir()
    m = {"in_sample": {"sharpe": 1.0}, "validation": {"sharpe": 0.5, "max_drawdown": 0.1, "annual_turnover": 2.0},
         "holdout": {"sharpe": 1.2}}
    (tmp_path / "experiments" / "a.json").write_text(json.dumps({
        "strategy": {"name": "idea", "timeframe": "1Day"}, "data": {"source": "alpaca:sip"}, "metrics": m,
        "evaluated_at": "2026-10-04T00:00:00+00:00", "passed_gates": False,
        "gates": [{"gate": "turnover", "passed": False}, {"gate": "executable_timeframe", "passed": False, "promotion_only": True}]}))
    (tmp_path / "experiments" / "b.json").write_text(json.dumps({
        "strategy": {"name": "smoke", "timeframe": "1Day"}, "data": {"source": "synthetic"}, "metrics": m}))
    (tmp_path / "executions" / "r1.json").write_text(json.dumps({
        "started_at": "2026-10-05T15:00:00+00:00", "status": "submitted 2 orders",
        "submitted": [{"symbol": "KO"}, {"symbol": "XOM"}]}))
    return tmp_path


def test_section_reports_trades_pnl_holdings_and_experiments(tmp_path):
    text = readme.section(_ledger(tmp_path), Broker())
    assert "**2** on 1 trading day(s)" in text and "submitted 2 orders" in text
    assert "+500 (+0.50%)" in text and "+1,000 (+1.00%) since $100,000" in text
    assert "| KO | 110 | $7,000 | -12 |" in text
    assert "| `idea` | 1Day | rejected (turnover) | 1.00 | 0.50 | ~1.2 | 10% | 2.0 |" in text
    assert "smoke" not in text   # synthetic runs are not results


def test_section_without_trades_or_broker_says_so(tmp_path):
    (tmp_path / "experiments").mkdir()
    text = readme.section(tmp_path, None)
    assert "**0**" in text and "No paper trades yet" in text and "not checked" in text


def test_broker_failure_still_builds(tmp_path):
    class Bad:
        def account(self):
            raise RuntimeError("401")
    assert "Could not read the paper account" in readme.section(_ledger(tmp_path), Bad())


def test_splice_only_touches_the_block():
    doc = f"intro\n{readme.RESULTS_START}\nold\n{readme.RESULTS_END}\noutro\n"
    out = readme.splice(doc, f"{readme.RESULTS_START}\nnew\n{readme.RESULTS_END}")
    assert out == f"intro\n{readme.RESULTS_START}\nnew\n{readme.RESULTS_END}\noutro\n"


def test_main_appends_a_block_to_a_file_without_markers(tmp_path):
    out = tmp_path / "RESULTS.md"
    out.write_text("# Results page\n")
    (tmp_path / "experiments").mkdir()
    readme.main(["--ledger", str(tmp_path), "--readme", str(out), "--no-broker"])
    text = out.read_text()
    assert text.startswith("# Results page") and readme.RESULTS_START in text and text.rstrip().endswith(readme.RESULTS_END)
