"""A strategy must produce the same signal from only `lookback` bars (what factory.execute fetches)
as from the full history; otherwise it would trade differently live than in its backtest."""
import uuid
from pathlib import Path

import pytest

from factory import evaluate, runner
from factory.data import synthetic

CAND = Path(__file__).resolve().parent.parent / "strategies" / "candidates"


@pytest.fixture
def make():
    paths = []

    def _make(lookback):
        p = CAND / f"_test_{uuid.uuid4().hex[:8]}.py"
        p.write_text("from strategies.base import Strategy, equal_weight\n\n\nclass T(Strategy):\n"
                     f"    name = 't'\n    lookback = {lookback}\n    params = {{}}\n\n"
                     "    def target_weights(self, md):\n"
                     "        c = md.close\n"
                     "        return equal_weight(c > c.rolling(100).mean(), slots=10)\n")
        paths.append(p)
        return f"strategies/candidates/{p.name}"
    yield _make
    for p in paths:
        p.unlink()


def _windows_match(ref, lookback):
    md = synthetic(["A", "B", "C"], "2020-01-01", "2021-06-30")
    cuts = [200, 250, 300]
    frames = runner.run(ref, md, [{}] + [{"rows": c + 1, "start": max(0, c + 1 - lookback)} for c in cuts])
    for c, f in zip(cuts, frames[1:]):
        assert f.index[-1] == md.index[c]
    return evaluate.causality_mismatches(frames[0], dict(zip(cuts, frames[1:])))


def test_short_lookback_is_caught(make):
    assert _windows_match(make(30), 30)


def test_sufficient_lookback_passes(make):
    assert _windows_match(make(120), 120) == []
