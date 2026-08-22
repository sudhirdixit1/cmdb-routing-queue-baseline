"""Every metric here is implemented from scratch, so every metric here is
tested against scikit-learn's.  Agreement to 1e-12 is what makes the
independence in `scripts/r46_tool_agreement.py` free rather than expensive.
"""
import numpy as np
import pytest
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

from fieldvalue import metrics as M

SEEDS = range(12)


def _draw(rng, n=800, ties=False, prev=0.3):
    y = (rng.random(n) < prev).astype(int)
    s = rng.random(n) * 0.6 + 0.2 * y
    if ties:
        s = np.round(s, 1)          # heavy tie blocks, on purpose
    if len(np.unique(y)) < 2:
        y[0], y[1] = 0, 1
    return s, y


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("ties", [False, True])
def test_auc_matches_sklearn(seed, ties):
    s, y = _draw(np.random.default_rng(seed), ties=ties)
    assert abs(M.auc(s, y) - roc_auc_score(y, s)) < 1e-12


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("ties", [False, True])
def test_average_precision_matches_sklearn(seed, ties):
    s, y = _draw(np.random.default_rng(seed), ties=ties)
    assert abs(M.average_precision(s, y)
               - average_precision_score(y, s)) < 1e-12


@pytest.mark.parametrize("seed", SEEDS)
def test_brier_matches_sklearn(seed):
    s, y = _draw(np.random.default_rng(seed))
    assert abs(M.brier(s, y) - brier_score_loss(y, s)) < 1e-12


def test_auc_is_half_for_a_constant_score():
    y = np.r_[np.ones(30, int), np.zeros(70, int)]
    assert M.auc(np.full(100, 0.4), y) == pytest.approx(0.5)


def test_auc_is_one_for_perfect_separation():
    y = np.r_[np.ones(30, int), np.zeros(70, int)]
    s = np.r_[np.full(30, 0.9), np.full(70, 0.1)]
    assert M.auc(s, y) == pytest.approx(1.0)


def test_average_precision_is_prevalence_for_a_constant_score():
    y = np.r_[np.ones(25, int), np.zeros(75, int)]
    assert M.average_precision(np.full(100, 0.5), y) == pytest.approx(0.25)


def test_net_benefit_needs_a_threshold_inside_the_unit_interval():
    y = np.r_[np.ones(10, int), np.zeros(10, int)]
    s = np.linspace(0, 1, 20)
    for bad in (0.0, 1.0, -0.1, 1.4):
        with pytest.raises(ValueError):
            M.net_benefit(s, y, bad)


def test_expected_cost_saving_is_net_benefit_at_the_bayes_threshold():
    """The paper's instrument matrix proves the identity; this asserts it."""
    rng = np.random.default_rng(3)
    s, y = _draw(rng)
    for r in (1.0, 2.0, 3.0, 5.0, 10.0):
        assert (M.expected_cost_saving(s, y, r)
                == pytest.approx(r * M.net_benefit(s, y, 1.0 / (1.0 + r)),
                                 abs=1e-12))


def test_labels_must_be_binary():
    with pytest.raises(ValueError):
        M.auc(np.array([0.1, 0.2, 0.3]), np.array([0, 1, 2]))


def test_shape_mismatch_is_an_error():
    with pytest.raises(ValueError):
        M.auc(np.array([0.1, 0.2]), np.array([0, 1, 1]))
