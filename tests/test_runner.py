import uuid
from pathlib import Path

import pytest

from factory import runner
from factory.data import synthetic

CAND = Path(__file__).resolve().parent.parent / "strategies" / "candidates"


@pytest.fixture
def candidate():
    paths = []

    def make(body):
        p = CAND / f"_test_{uuid.uuid4().hex[:8]}.py"
        p.write_text("from strategies.base import Strategy\n\n\nclass T(Strategy):\n    name = 't'\n    lookback = 1\n"
                     "    params = {}\n\n    def target_weights(self, md):\n" + body)
        paths.append(p)
        return f"strategies/candidates/{p.name}"
    yield make
    for p in paths:
        p.unlink()


def test_candidate_cannot_mutate_parent_data(candidate):
    ref = candidate("        md.open.iloc[:, :] = 1.0\n        return md.close * 0\n")
    md = synthetic(["A", "B"], "2021-01-01", "2021-03-01")
    before = md.open.copy()
    runner.run(ref, md, [{}])
    assert md.open.equals(before)


def test_hanging_candidate_times_out(candidate):
    ref = candidate("        while True:\n            pass\n")
    md = synthetic(["A"], "2021-01-01", "2021-02-01")
    with pytest.raises(runner.StrategyError, match="exceeded"):
        runner.run(ref, md, [{}], timeout=3)


def test_unsafe_candidate_rejected_in_child(candidate):
    ref = candidate("        import os\n        return md.close * 0\n")
    with pytest.raises(runner.StrategyError, match="import not allowed"):
        runner.describe(ref)


def test_truncated_jobs_return_matching_shapes():
    md = synthetic(["A", "B"], "2021-01-01", "2021-06-01")
    full, part = runner.run("strategies.baselines.sma_trend:SmaTrend", md, [{}, {"rows": 50}])
    assert full.shape == (len(md.index), 2) and part.shape == (50, 2)
