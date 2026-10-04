import numpy as np
import pandas as pd

from factory import metrics


def test_more_trials_lower_the_probability():
    r = pd.Series(np.random.default_rng(3).normal(0.0006, 0.01, 500))
    one = metrics.deflated_sharpe(r, 1)["probability"]
    many = metrics.deflated_sharpe(r, 50)["probability"]
    assert 0 < many < one <= 1


def test_noise_is_not_significant_after_many_trials():
    r = pd.Series(np.random.default_rng(5).normal(0.0, 0.01, 500))
    assert metrics.deflated_sharpe(r, 30)["probability"] < 0.5


def test_short_series_gives_no_answer():
    assert metrics.deflated_sharpe(pd.Series([0.01, -0.01]), 5)["probability"] is None
