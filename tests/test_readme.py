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


def test_fund_leaderboard_ranks_funded_accounts_and_counts_trades(tmp_path):
    class Up(Broker):
        def account(self):
            return {"equity": "105000", "last_equity": "104000", "cash": "0"}

    class Down(Broker):
        def portfolio_history(self):
            return {"equity": [110000, 101000]}

    class Broken:
        def account(self):
            raise RuntimeError("401")

    led = _ledger(tmp_path)
    (led / "executions" / "r2.json").write_text(json.dumps({
        "started_at": "2026-10-06T15:00:00+00:00", "fund": 4, "status": "submitted 1 orders", "submitted": [{"symbol": "KO"}]}))
    import pandas as pd
    closes = pd.Series([400.0, 404.0, 412.0, 416.0], index=pd.to_datetime(["2026-10-01", "2026-10-02", "2026-10-05", "2026-10-06"]))
    readme_prices = lambda sym, start: closes
    orig = readme.fund_section
    readme.fund_section = lambda runs, brokers: orig(runs, brokers, readme_prices)
    try:
        text = readme.section(led, Broker(), fund_brokers={1: Down(), 4: Up(), 6: Broken()})
    finally:
        readme.fund_section = orig
    rows = [line for line in text.splitlines() if line.startswith("| ") and "Darth" not in line[:4]]
    board = [r for r in rows if r.split("|")[1].strip().isdigit()]
    # best total first (SPY from the 2026-10-02 close: 404 -> 416 is +2.97%), then broken, then unfunded
    assert [r.split("|")[1].strip() for r in board][:4] == ["4", "10", "1", "6"]
    assert "| 10 | 🕷️ Spyder-man | SPY buy and hold since 2026-10-02 (benchmark) | $102,970 | +990 (+0.97%) | +2,970 (+2.97%) | n/a |" in board[1]
    assert "| 4 | 🛹 Marty McBuy |" in board[0] and "$105,000 | +1,000 (+0.96%) | +5,000 (+5.00%) | 1 |" in board[0]
    assert "(champion)" in board[2] and "-9,000 (-8.18%) | 2 |" in board[2]
    assert "unavailable (RuntimeError)" in board[3]
    assert sum("not funded yet" in r for r in board) == 6
