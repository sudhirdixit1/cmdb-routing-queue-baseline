"""Tests for the four reporting objects.

Each test states the property in its name and asserts it on a constructed
surface whose answer is known by hand, so a failure names the broken property
rather than a number.
"""
import numpy as np
import pandas as pd
import pytest

from fieldvalue import decompose, regions, regret, robustness, summary


def grid(values, axes=("baseline_pair", "metric")):
    """A tidy frame over a full factorial with the given cell values."""
    rows = []
    k = 0
    for a in ("B0->B1", "B0->B2"):
        for m in ("auc", "ap", "brier_skill"):
            rows.append(dict(baseline_pair=a, metric=m, population=1.0,
                             regime="full", V=values[k]))
            k += 1
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- decompose
def test_decompose_attributes_all_variance_to_the_axis_that_carries_it():
    #  V depends only on the metric: the three metric levels differ, the two
    #  baseline levels do not.
    f = grid([1.0, 2.0, 3.0, 1.0, 2.0, 3.0])
    d = decompose(f).set_index("axis")
    assert d.loc["metric", "S"] == pytest.approx(1.0)
    assert d.loc["baseline_pair", "S"] == pytest.approx(0.0, abs=1e-12)


def test_decompose_indices_lie_in_the_unit_interval():
    rng = np.random.default_rng(0)
    f = grid(list(rng.normal(0, 1, 6)))
    d = decompose(f)
    assert ((d.S >= -1e-9) & (d.S <= 1 + 1e-9)).all()
    assert ((d.S_total >= -1e-9) & (d.S_total <= 1 + 1e-9)).all()


def test_decompose_total_is_at_least_first_order():
    rng = np.random.default_rng(1)
    f = grid(list(rng.normal(0, 1, 6)))
    d = decompose(f)
    assert (d.S_total >= d.S - 1e-9).all()


def test_decompose_finds_interaction_where_there_is_one():
    #  a pure interaction: the metric's effect reverses with the baseline, so
    #  neither main effect explains anything and the total indices do.
    f = grid([1.0, 0.0, -1.0, -1.0, 0.0, 1.0])
    d = decompose(f).set_index("axis")
    assert d.loc["metric", "S"] == pytest.approx(0.0, abs=1e-12)
    assert d.loc["baseline_pair", "S"] == pytest.approx(0.0, abs=1e-12)
    assert d.loc["metric", "interaction"] > 0.5


def test_decompose_on_a_constant_surface_is_not_a_crash():
    f = grid([2.0] * 6)
    d = decompose(f)
    assert d.S.isna().all() or (d.S == 0).all()


# ------------------------------------------------------------------ regions
def test_regions_labels_by_the_interval_not_the_point_estimate():
    f = grid([0.1] * 6)
    f["lo"] = [-0.2, 0.05, -0.2, 0.05, -0.2, 0.05]
    f["hi"] = 0.4
    lab = list(regions(f).label)
    assert lab == ["unresolved", "beneficial"] * 3


def test_regions_calls_a_cell_harmful_only_when_the_upper_bound_is_negative():
    f = grid([-0.1] * 6)
    f["lo"] = -0.4
    f["hi"] = [-0.05, 0.2] * 3
    lab = list(regions(f).label)
    assert lab == ["harmful", "unresolved"] * 3


def test_regions_without_intervals_says_so_rather_than_guessing():
    f = grid([0.1] * 6)
    assert set(regions(f).label) == {"positive-point-estimate"}
    assert "no intervals supplied" in robustness(f).region.iloc[0]


# --------------------------------------------------------------- robustness
def test_rho_is_one_exactly_when_every_cell_is_beneficial():
    f = grid([0.2] * 6)
    f["lo"], f["hi"] = 0.1, 0.3
    r = robustness(f)
    assert r.rho.iloc[0] == pytest.approx(1.0)
    assert r.region.iloc[0] == "uniformly beneficial"


def test_rho_is_minus_one_when_every_cell_is_harmful():
    f = grid([-0.2] * 6)
    f["lo"], f["hi"] = -0.3, -0.1
    r = robustness(f)
    assert r.rho.iloc[0] == pytest.approx(-1.0)
    assert r.region.iloc[0] == "harmful"


def test_a_surface_with_both_signs_resolved_is_sign_changing():
    f = grid([0.2, 0.2, 0.2, -0.2, -0.2, -0.2])
    f["lo"] = [0.1, 0.1, 0.1, -0.3, -0.3, -0.3]
    f["hi"] = [0.3, 0.3, 0.3, -0.1, -0.1, -0.1]
    assert robustness(f).region.iloc[0] == "sign-changing"


def test_exclusion_removes_the_implausible_rung_from_the_region():
    f = grid([0.2, 0.2, 0.2, -0.2, -0.2, -0.2])
    f["lo"] = [0.1, 0.1, 0.1, -0.3, -0.3, -0.3]
    f["hi"] = [0.3, 0.3, 0.3, -0.1, -0.1, -0.1]
    r = robustness(f, exclude=("B0->B2",))
    assert r.region.iloc[0] == "uniformly beneficial"
    assert r.n_cells.iloc[0] == 3


# ------------------------------------------------------------------- regret
def test_misreport_is_zero_when_every_cell_agrees_in_sign():
    f = grid([0.2] * 6)
    assert (regret(f).misreport == 0).all()


def test_misreport_is_the_share_of_the_other_sign():
    f = grid([0.2, 0.2, 0.2, 0.2, -0.2, -0.2])
    g = regret(f)
    #  four positives, two negatives: a positive report misleads a third of
    #  readers, a negative report misleads two thirds.
    assert g[g.V > 0].misreport.iloc[0] == pytest.approx(2 / 6)
    assert g[g.V < 0].misreport.iloc[0] == pytest.approx(4 / 6)


def test_regret_is_zero_where_nothing_is_forgone_or_destroyed():
    f = grid([0.2] * 6)
    #  every cell is beneficial, so a positive report destroys nothing
    assert regret(f).regret.max() == pytest.approx(0.0)


def test_summary_returns_the_three_objects_and_never_a_scalar():
    f = grid([0.2, 0.1, -0.1, 0.3, 0.0, -0.2])
    f["lo"], f["hi"] = f.V - 0.05, f.V + 0.05
    s = summary(f)
    assert set(s) == {"decomposition", "robustness", "regret"}
    for v in s.values():
        assert isinstance(v, pd.DataFrame)
