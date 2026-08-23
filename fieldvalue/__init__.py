"""fieldvalue -- report what a recorded field is worth as a surface, not a number.

    from fieldvalue import surface

    s = surface(X, y, feature="ci_name",
                baselines={"intake": INTAKE, "intake+group": INTAKE + ["group"]},
                metrics=["auc", "ap", "brier_skill", "nagelkerke"],
                thresholds=np.arange(0.05, 0.80, 0.025),
                population=[1.0, 0.75, 0.50, 0.25],
                seed=20260819)
    s.report()      # the minimum reportable form, as text
    s.to_frame()    # the surface as a tidy DataFrame
    s.plot()        # the signature figure

`float(s)` raises.  That is the point: the incremental value of a field is a
function of the baseline, the metric, the operating point and the register's
population, and a library that returned one number would be arguing against
the standard it exists to implement.
"""
from .core import (DEFAULT_METRICS, DEFAULT_POPULATION, DEFAULT_THRESHOLDS,
                   SingleNumberRefused, Surface, surface)
from .metrics import (METRICS, RANK_BASED, auc, average_precision, brier,
                      brier_skill, expected_cost_saving, nagelkerke,
                      net_benefit)
from .report import decompose, regions, regret, robustness, summary

__version__ = "0.2.0"
__all__ = ["surface", "Surface", "SingleNumberRefused", "METRICS",
           "RANK_BASED", "DEFAULT_METRICS", "DEFAULT_THRESHOLDS",
           "DEFAULT_POPULATION", "auc", "average_precision", "brier",
           "brier_skill", "nagelkerke", "net_benefit",
           "expected_cost_saving", "decompose", "regions", "regret",
           "robustness", "summary", "__version__"]
