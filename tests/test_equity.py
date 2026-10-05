"""Fund equity snapshots and the README performance chart."""
import datetime as dt
import json
import xml.etree.ElementTree as ET

from factory import equity, funds


class B:
    def __init__(self, eq, open_=True):
        self.eq, self.open_ = eq, open_

    def clock(self):
        return {"is_open": self.open_}

    def account(self):
        if self.eq is None:
            raise RuntimeError("401")
        return {"equity": str(self.eq)}

    def latest_trades(self, syms):
        return {s: (600.0, "t") for s in syms}


def test_snapshot_records_each_fund_and_spy_and_isolates_errors():
    fs = funds.load()
    rec = equity.snapshot(fs, {1: B(100500), 4: B(None)})
    assert rec["funds"]["1"] == {"equity": 100500.0, "strategy": funds.strategy(fs[0])["name"]}
    assert "error" in rec["funds"]["4"] and "2" not in rec["funds"]
    assert rec["funds"]["10"]["price"] == 600.0
    assert equity.snapshot(fs, {1: B(1, open_=False)}) is None   # market closed: nothing recorded
    assert equity.snapshot(fs, {}) is None


def _recs():
    t = dt.datetime(2026, 10, 5, 14, 45, tzinfo=dt.timezone.utc)
    out = []
    for i, (a, s, p) in enumerate([(100000, "x", 600), (101000, "x", 606), (99000, "y", 612)]):
        out.append({"taken_at": (t + dt.timedelta(hours=2 * i)).isoformat(),
                    "funds": {"1": {"equity": a, "strategy": s}, "10": {"price": p, "strategy": "SPY benchmark"},
                              "2": {"error": "401"}}})
    return out


def test_series_indexes_to_first_reading_and_finds_strategy_changes():
    lines, changes = equity.series(_recs())
    assert [round(p, 4) for _, p in lines[1]] == [0.0, 0.01, -0.01]
    assert [round(p, 4) for _, p in lines[10]] == [0.0, 0.01, 0.02]
    assert 2 not in lines
    assert changes == [{"fund": 1, "index": 2, "pct": lines[1][2][1], "taken_at": _recs()[2]["taken_at"], "from": "x", "to": "y"}]


def test_svg_is_valid_and_highlights_the_benchmark(tmp_path):
    doc = equity.svg(_recs(), funds.load())
    root = ET.fromstring(doc)
    ns = "{http://www.w3.org/2000/svg}"
    assert len(root.findall(f"{ns}path[@class='b']")) == 1          # one thick benchmark line
    assert len(root.findall(f"{ns}path[@class='l']")) == 1
    assert len(root.findall(f"{ns}circle")) == 2                    # one change marker + legend key
    assert "Spyder-man (benchmark)" in doc and "prefers-color-scheme: dark" in doc
    ET.fromstring(equity.svg([], funds.load()))                     # empty window still renders


def test_load_keeps_the_last_90_days(tmp_path):
    (tmp_path / "equity").mkdir()
    now = dt.datetime(2026, 12, 31, tzinfo=dt.timezone.utc)
    for i, days in enumerate((1, 89, 91)):
        (tmp_path / "equity" / f"{i}.json").write_text(json.dumps(
            {"taken_at": (now - dt.timedelta(days=days)).isoformat(), "funds": {}}))
    assert len(equity.load(tmp_path, now)) == 2
