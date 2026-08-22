"""The surface, the refusal, and the ways a caller can get it wrong."""
import numpy as np
import pandas as pd
import pytest

from fieldvalue import SingleNumberRefused, surface


def toy(n=4000, seed=5, overlap=0.6):
    rng = np.random.default_rng(seed)
    Kb, Kg, Kf = 4, 6, 40
    b = rng.integers(0, Kb, n)
    f = rng.integers(0, Kf, n)
    gmap = rng.integers(0, Kg, Kf)
    g = np.where(rng.random(n) < 0.75, gmap[f], rng.integers(0, Kg, n))
    eb, ef, eg = (rng.normal(0, .8, Kb), rng.normal(0, 1.6, Kf),
                  rng.normal(0, 1.6, Kg))
    eta = eb[b] + (1 - overlap) * ef[f] + overlap * eg[g] - .4
    y = (rng.random(n) < 1 / (1 + np.exp(-eta))).astype(int)
    X = pd.DataFrame(dict(b=b.astype(str), g=g.astype(str), f=f.astype(str),
                          t=np.arange(n)))
    return X, y


BASE = {"B0": ["b"], "B0+g": ["b", "g"]}


def test_surface_returns_a_frame_with_every_axis():
    X, y = toy()
    s = surface(X, y, "f", BASE, thresholds=(0.2, 0.4), population=(1.0, 0.5),
                order="t")
    F = s.to_frame()
    for c in ("baseline_pair", "metric", "threshold", "population", "regime",
              "V_lo", "V_hi", "R"):
        assert c in F.columns
    assert F.metric.nunique() >= 5           # four scalar metrics + net benefit
    assert set(F.population) == {1.0, 0.5}


def test_the_package_refuses_to_emit_one_number():
    X, y = toy()
    s = surface(X, y, "f", BASE, thresholds=(), population=(1.0,))
    with pytest.raises(SingleNumberRefused) as e:
        float(s)
    assert "four arguments" in str(e.value)
    with pytest.raises(SingleNumberRefused):
        s.headline()


def test_at_forces_the_caller_to_name_a_cell():
    X, y = toy()
    s = surface(X, y, "f", BASE, thresholds=(0.3,), population=(1.0,))
    row = s.at(metric="auc", population=1.0)
    assert np.isfinite(row.V_lo)
    with pytest.raises(KeyError):
        s.at(metric="not_a_metric")


def test_spread_reports_all_four_axes():
    X, y = toy()
    s = surface(X, y, "f", BASE, thresholds=(0.2, 0.3, 0.4),
                population=(1.0, 0.75, 0.5), order="t")
    sp = s.spread()
    assert set(sp.axis) == {"baseline", "metric", "threshold", "population"}
    assert (sp.cells > 0).all()


def test_a_feature_cannot_be_incremental_over_itself():
    X, y = toy()
    with pytest.raises(ValueError):
        surface(X, y, "f", {"bad": ["b", "f"]})


def test_missing_columns_are_named():
    X, y = toy()
    with pytest.raises(KeyError):
        surface(X, y, "f", {"B0": ["b", "nope"]})
    with pytest.raises(KeyError):
        surface(X, y, "not_a_column", BASE)


def test_no_order_column_produces_a_note_rather_than_silence():
    X, y = toy()
    s = surface(X.drop(columns=["t"]), y, "f", BASE, thresholds=(),
                population=(1.0,))
    assert any("leaks the future" in n for n in s.notes)


def test_population_masking_actually_degrades_the_register():
    X, y = toy()
    s = surface(X, y, "f", BASE, thresholds=(), population=(1.0, 0.5),
                regimes=("rare-first",), order="t")
    F = s.to_frame()
    assert F[F.population == 1.0].populated.iloc[0] == pytest.approx(1.0)
    assert F[F.population == 0.5].populated.iloc[0] < 0.7


def test_report_prints_the_minimum_reportable_form():
    import io
    X, y = toy()
    s = surface(X, y, "f", BASE, thresholds=(0.3,), population=(1.0,))
    buf = io.StringIO()
    s.report(stream=buf)
    txt = buf.getvalue()
    assert "AS A SURFACE" in txt
    assert "minimum reportable form" in txt
    for axis in ("baseline", "metric", "threshold", "population"):
        assert axis in txt


def test_plot_reads_every_value_from_the_frame(tmp_path):
    X, y = toy()
    s = surface(X, y, "f", BASE, thresholds=(), population=(1.0,))
    p = tmp_path / "fig.png"
    s.plot(path=str(p))
    assert p.exists() and p.stat().st_size > 1000


def test_a_ratio_with_a_non_positive_denominator_is_blank_not_printed():
    """R must be NaN where V(f | B_lo) <= 0, and the note must say so."""
    rng = np.random.default_rng(1)
    n = 3000
    X = pd.DataFrame(dict(b=rng.integers(0, 3, n).astype(str),
                          g=rng.integers(0, 3, n).astype(str),
                          f=rng.integers(0, 50, n).astype(str)))
    y = (rng.random(n) < 0.4).astype(int)      # f carries nothing
    s = surface(X, y, "f", BASE, thresholds=(), population=(1.0,))
    F = s.to_frame()
    assert F.R.isna().any()
    assert any("crosses zero" in nte for nte in s.notes)


def test_more_baselines_give_more_reductions():
    X, y = toy()
    s2 = surface(X, y, "f", {"B0": ["b"], "B1": ["b", "g"]}, thresholds=(),
                 population=(1.0,))
    s3 = surface(X, y, "f", {"E": [], "B0": ["b"], "B1": ["b", "g"]},
                 thresholds=(), population=(1.0,))
    assert s3.to_frame().baseline_pair.nunique() == 3     # 3 choose 2
    assert s2.to_frame().baseline_pair.nunique() == 1
