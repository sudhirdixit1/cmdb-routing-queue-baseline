# fieldvalue

**Report what a recorded field is worth as a surface, not a number.**

A claim that a field is "worth +0.08 AUC" is a claim about four things that are
almost never stated: which already-recorded fields the comparison is allowed to
contain (the **baseline**), how performance is measured (the **metric**), where
on the operating range it is read (the **operating point**), and how complete
the register the field reads from is (the **population**). `fieldvalue`
computes the value over all four and **refuses to collapse it to one number**.

```python
from fieldvalue import surface

s = surface(
    X, y,
    feature="ci_name",
    baselines={"intake": INTAKE, "intake+group": INTAKE + ["group"]},
    metrics=["auc", "ap", "brier_skill", "nagelkerke"],
    thresholds=np.arange(0.05, 0.80, 0.025),
    population=[1.0, 0.75, 0.50, 0.25],
    order="opened_at",          # split by time; a random split leaks the future
    seed=20260819,
)

s.report()      # the minimum reportable form, as text
s.to_frame()    # the surface, tidy
s.spread()      # how much each axis moves the answer
s.plot()        # the signature figure
float(s)        # raises SingleNumberRefused, and says why
```

From the command line:

```
python -m fieldvalue --data incidents.csv --target reassigned \
    --feature ci_name \
    --baseline intake:category,impact,urgency,priority \
    --baseline "intake+group:category,impact,urgency,priority,group" \
    --order opened_at --out surface.csv --figure surface.png
```

## The estimand

For a feature $f$, a baseline set $B$, a metric $m$ and an operating point
$\theta$,

$$V(f \mid B, m, \theta) = m(B \cup \{f\}, \theta) - m(B, \theta)$$

and for two nested baselines $B_0 \subset B_1$, the **admissibility
reduction**

$$R(f \mid B_0, B_1, m, \theta) = 1 - \frac{V(f \mid B_1, m, \theta)}{V(f \mid B_0, m, \theta)}$$

`R` is left blank wherever $V(f \mid B_0) \le 0$. A ratio whose denominator
crosses zero is not a quantity, and the package says so in its notes rather
than printing one.

## What is in the box

| module | what it does |
|---|---|
| `fieldvalue.metrics` | AUC, average precision, Brier, Brier skill, Nagelkerke $R^2$, net benefit, expected cost saving — **implemented in numpy**, not delegated |
| `fieldvalue.core` | the estimator (one-hot + logistic), the population masking, the surface, the refusal |
| `fieldvalue.cli` | `python -m fieldvalue` |
| `fieldvalue.tests` | 91 tests, including the accompanying paper's three propositions |

**The metrics are implemented from scratch on purpose.** The paper that ships
with this package re-derives its own headline through `fieldvalue` and asserts
agreement with its analysis pipeline
(`scripts/r46_tool_agreement.py`: 20 of 20 quantities agree to 2.2e-16). That
check is worth something only if the two paths are genuinely different.
`tests/test_metrics.py` asserts agreement with scikit-learn to 1e-12, so the
independence costs no correctness. What is **not** independent: scikit-learn's
`OneHotEncoder` and `LogisticRegression`, which both paths call.

## The refusal

`float(s)` and `s.headline()` raise `SingleNumberRefused`. This is not a
defensive check; it is the standard, encoded. If you need one cell, name it:

```python
s.at(baseline="intake -> intake+group", metric="auc", population=1.0)
```

which forces the caller to say which cell they are standing in.

## Install

```
pip install -e .            # from the repository root
pip install -e ".[plot,test]"
python -m pytest fieldvalue
```

Dependencies: numpy, pandas, scikit-learn. `matplotlib` only for `.plot()`,
imported lazily.

## A worked example

`examples/worked_example.py` runs the whole thing on UCI Adult
(`doi:10.24432/C5XW20`) — a public dataset that is **not** one of the paper's
event logs — asking what `occupation` is worth. Against the fields that come
free with the sampling frame the reduction is $+0.75$; against those plus
education and hours it is $+0.20$. Same data, same feature, same metric: the
baseline alone moves the answer by three quarters of its own size.

## Licence

MIT.
