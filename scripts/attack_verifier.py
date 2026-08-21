"""Corruption suite for verify_paper.py.

Run as a regression test.  Each entry perturbs the paper in a way an earlier
version of the verifier failed to catch, then asserts the verifier now fails.

!! DO NOT EDIT THE MANUSCRIPT WHILE THIS IS RUNNING. !!  This script copies
paper/iaai27_empty_cmdb.tex to paper/.tex.bak, rewrites the manuscript once
per corruption, and restores the backup in a `finally` block.  Any edit made
to the manuscript while it runs is silently reverted at the end, and any
build or verification started while it runs may be reading a CORRUPTED file
and reporting on that.  Both happened during round sixteen.  If you see
paper/.tex.bak on disk, this script is either running or was killed
mid-flight; in the latter case restore from it before doing anything else.
Whitespace in the search strings is normalised, because LaTeX wraps lines and
a naive replace silently no-ops -- which produced a false "PASSED" in an
earlier run of this suite and briefly looked like a verifier hole.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEX = ROOT / "paper" / "iaai27_empty_cmdb.tex"
BAK = ROOT / "paper" / ".tex.bak"

CORRUPTIONS = [
    ("sign flip, headline gain", "& $+0.183$ [", "& $-0.183$ ["),
    ("sign flip, group-unique",
     "and $+0.002$ once the item is present",
     "and $-0.002$ once the item is present"),
    ("swap table-1 AUCs", "intake only & 0.562 & 0.746", "intake only & 0.644 & 0.746"),
    ("swap train/test n", "$31{,}818$ training and", "$13{,}637$ training and"),
    ("swap mirror pair", "retains $91\\%$ of the group's", "retains $41\\%$ of the group's"),
    ("corrupt scope top-64", "$64$ recover $88\\%$", "$64$ recover $68\\%$"),
    ("corrupt scope top-8", "top $8$ recover $56\\%$", "top $8$ recover $26\\%$"),
    ("corrupt design range", "ranges $+0.067$ to", "ranges $+0.087$ to"),
    ("corrupt queue-unique CI", "$[+0.0001,+0.0034]$", "$[+0.0010,+0.0034]$"),
    ("corrupt null", "$-0.0009 \\pm 0.0005$", "$-0.0019 \\pm 0.0005$"),
    ("corrupt cohort figure", "$92.56\\%$", "$95.56\\%$"),
    ("break a tabular row",
     "adversarial: negatives first & $+608$ & $+104$ & $5.8$ \\\\",
     "adversarial: negatives first & $+608$ & $+104$ & $5.8$ \\"),
    ("fabricated literal", "before funding anything.",
     "before funding anything, across $737$ sites."),
    # -- second task (r9).  A new claim gets the same treatment as an old one.
    ("swap the reopen gain pair",
     "worth $+0.083$ against the intake block and $+0.055$",
     "worth $+0.055$ against the intake block and $+0.083$"),
    ("inflate reopen shrinkage", "a reduction of $33\\%$", "a reduction of $53\\%$"),
    ("corrupt long-handling gain", "on long handling, $+0.118$ and $+0.078$",
     "on long handling, $+0.148$ and $+0.078$"),
    ("corrupt reopen positives", "failure mode: $2{,}096$ incidents",
     "failure mode: $3{,}096$ incidents"),
    ("overstate target independence",
     "correlating with reassignment at $+0.14$",
     "correlating with reassignment at $+0.04$"),
    ("overstate reopen evidence", "stand only $5.5$ and $4.2$ pooled",
     "stand only $25.5$ and $4.2$ pooled"),
    # The split-point ranges are replaced by bootstrap intervals on the
    # SHRINKAGE, which is what showed the replication claim overrunning its
    # evidence on the near-independent target.
    ("narrow the reopening shrinkage interval away from zero",
     "$[-1,60]$ on reopening", "$[11,60]$ on reopening"),

    # -- r10, estimator families.  The point of these rows is that the effect
    #    is not an artifact of one estimator, so an inflated range or a hidden
    #    encoder null is exactly the corruption that would matter.
    ("swap the estimator range endpoints",
     "the first rung ranges $+0.173$ to $+0.184$",
     "the first rung ranges $+0.184$ to $+0.173$"),
    ("hide the boosting encoder null",
     "$+0.0042 \\pm 0.0020$", "$+0.0002 \\pm 0.0020$"),
    # This one is a real defect that shipped: HANDOFF quoted the max_bins
    # PARAMETER (256) where r5_binning computes 137 distinct bins.
    ("restore the wrong bin count", "into $137$ bins", "into $256$ bins"),

    # -- r11, the operational translation.
    # -- ROUND SIXTEEN.  The capacity table is withdrawn (section 8.1), so
    #    the five corruptions that lived on it are replaced by five on the
    #    evidence that withdrew it.  A withdrawal is a claim and gets the
    #    same treatment as the claim it replaced.
    ("swap the tie table's two arms",
     "one & $+271$ & $+63$ & $4.3$", "one & $+63$ & $+271$ & $4.3$"),
    ("corrupt the adversarial arm",
     "negatives first & $+608$", "negatives first & $+908$"),
    ("flip the sign the withdrawal turns on",
     "each tie & $-26$ & $+24$", "each tie & $+26$ & $+24$"),
    ("inflate the net-benefit replacement factor",
     "overstates its value there by a factor of\n$1.07$",
     "overstates its value there by a factor of\n$4.07$"),
    ("corrupt the abstract's replacement factor",
     "overstates the item's value by $1.07$ at",
     "overstates the item's value by $4.07$ at"),
    # The real defect was subtler than a fabricated digit: the abstract kept
    # the DISCREDITED single-tie-break-draw estimate while the table moved to
    # the median.  Both were "true" of some computation; only one is the
    # paper's.  This is the corruption that actually shipped.
    # The real defect this class describes -- an abstract keeping a figure
    # the body has retracted -- is now available in a sharper form: state
    # the WITHDRAWN factor as if it still stood.
    ("restore the withdrawn factor as a live claim in the abstract",
     "an operational overstatement we had reported as a factor of\n$4.3$ at "
     "a fixed review capacity does not survive",
     "omitting the free field credits the CMDB with $4.3$ times as many "
     "additional catches"),
    ("understate the AUC ratio the replacement is compared with",
     "smaller than the ratio of\n$1.8$", "smaller than the ratio of\n$1.1$"),
    ("swap the threshold ladder pair",
     "gives $+0.131$ and $+0.068$", "gives $+0.068$ and $+0.131$"),
    # Range endpoints floor and ceil; narrowing either makes the stated
    # range untrue, which ck_bound now catches.
    ("narrow the threshold shrinkage band",
     "between $43\\%$ and $49\\%$", "between $44\\%$ and $48\\%$"),

    # -- r12/r13, the queue's shape and the model-free mechanism.  The
    #    balanced-accuracy figure is the one that keeps the mechanism claim
    #    honest, so removing it is the most damaging single edit available.
    ("overstate what the item tells you about the group",
     "carries $60.4\\%$ of the opening group's",
     "carries $90.4\\%$ of the opening group's"),
    ("understate the field's concentration",
     "largest group holds $62.1\\%$", "largest group holds $22.1\\%$"),
    ("swap the two shares that show the field is an actor stamp",
     "$67.0\\%$ of \\texttt{Open} rows but only $18.4\\%$",
     "$18.4\\%$ of \\texttt{Open} rows but only $67.0\\%$"),
    ("overstate what one bit recovers",
     "recovers $61\\%$ of the group's baseline gain",
     "recovers $91\\%$ of the group's baseline gain"),

    # -- r14, scoping.  The across-split band is what stops a single split's
    #    curve being read as an estimate, so shrinking it is the attack.
    ("shrink the scoping band",
     "range over $52$--$58\\%$, $81$--$93\\%$",
     "range over $55$--$57\\%$, $87$--$89\\%$"),
    ("corrupt the across-split spread",
     "across-split spread is $9$ points", "across-split spread is $2$ points"),
    ("corrupt scoping without the group", "--- $89\\%$ at $k=64$",
     "--- $69\\%$ at $k=64$"),

    # -- r15.  The single-organisation justification rests on this rate: if it
    #    were 20% rather than 0.2%, a second organisation would be available
    #    and "constraint rather than choice" would be false.
    # -- r16.  The field re-characterisation is the correction that cost the
    #    paper its title.  Each of the three structural facts is attacked,
    #    because reversing any one of them restores the wrong reading.
    ("hide that Open rows are less diverse than Assignment rows",
     "rows carry $218$", "rows carry $18$"),
    ("reverse the agreement with the first Assignment",
     "activity for just $15.1\\%$", "activity for just $85.1\\%$"),
    ("shrink the delay that makes real routing inadmissible",
     "a median of $46$ minutes later", "a median of $4$ minutes later"),
    ("corrupt the count of incidents with no Assignment at all",
     "$7{,}878$ of $45{,}455$", "$1{,}878$ of $45{,}455$"),
    ("understate the drift in the free field",
     "falls from $49$ to $32$", "falls from $49$ to $42$"),

    # -- r17.  The rebuilt floor corrects a null that could not fail;
    #    understating it would restore the withdrawn 89-point margin.

    # -- the widest capacity's interval includes zero, which is why the paper
    #    quotes the 5% figure instead.  Hiding that is the attack.
    ("hide that net benefit goes negative", "$-16.1$ [$-23.0,-8.9$] & $+84.1$",
     "$+16.1$ [$8.9,23.0$] & $+84.1$"),
    # -- round three.  Each of these is a control a referee had to compute
    #    because the paper had not, so each gets its own corruption.
    ("understate what admitting the service component costs",
     "takes the measured value to $+0.023$",
     "takes the measured value to $+0.093$"),
    ("overstate how much hour and day of week move it",
     "from $+0.103$ to $+0.099$", "from $+0.103$ to $+0.049$"),
    ("hide that the routing-blind floor beats the real leg",
     "partition of items retains \\emph{more}, $56\\%$",
     "partition of items retains less, $16\\%$"),
    # Deleting this caveat would restore an ordering that holds by
    # construction: at one cell per item the null IS the real leg.
    ("misstate the capacity table's bootstrap draws",
     "re-ranked in each draw and use $400$",
     "re-ranked in each draw and use $4000$"),
    # -- round four.
    ("delete the engagement with the free-field objection",
     "The opening group may be free only because a human at the desk",
     "The opening group is free because nobody at the desk"),
    ("reuse bootstrap notation for the across-split spread",
     "These are min--max spreads over a design choice, not bootstrap",
     "These are 95% bootstrap intervals, like every other"),
    ("restore over-precise z statistics",
     "roughly $28$ and\n$17$ standard deviations",
     "roughly $28.1$ and\n$17.4$ standard deviations"),
    ("narrow the primary-target shrinkage interval",
     "$[40,48]$ on reassignment", "$[41,47]$ on reassignment"),
    # -- round five.  The Limitations sentence carried the EXCLUDED reverse
    #    leg as a transferable claim through four revisions.  It has no
    #    numeral, so only a phrase check catches it -- and a residue guard
    #    now bans the retracted wording outright.
    ("restore the reversed mechanism direction in Limitations",
     "the mechanism runs from item to group",
     "the mechanism is the item column proxying for the opening group"),
    ("overstate the union of the two edited-field rates",
     "reassigned at $0.66$ and those whose Urgency was edited at $0.67$",
     "reassigned at $0.76$ and those whose Urgency was edited at $0.67$"),
    ("drop the rule that stops a ratio being quoted across zero",
     "because a ratio whose denominator is crossing zero is not a\nquantity",
     "because the figure is not informative there"),
    ("broaden the interval claim back over rungs we do not measure",
     "the interval on\neach $+$group rung excludes zero",
     "every interval excludes zero, on\neach rung"),
    # -- round six.  The title asserted the mechanism leg section 5 excludes;
    #    the tail gloss was unevidenced; the naive baseline's rank degeneracy
    #    partly drives the headline factor and went unreported.
    ("restore the unevidenced 'own work' gloss",
     "calling them teams opening their own work would be another",
     "they are teams opening their own work, which would be another"),
    ("hide the naive baseline's rank degeneracy",
     "emit only $23$ distinct scores", "emit $2{,}300$ distinct scores"),
    ("overstate how often the tail opener does its own work",
     "later work rows only $59.1\\%$", "later work rows only $95.1\\%$"),
    # -- round seven.
    ("restore the range that excludes its own maximum",
     "first rung ranges $+0.173$ to $+0.184$",
     "first rung ranges $+0.173$ to $+0.183$"),
    ("reinstate the censored range built from single-incident months",
     "are reassigned at $81.2\\%$ against $40.0\\%$",
     "show reassignment rates of $76$--$100\\%$ against"),
    ("hide the criterion asymmetry",
     "$2{,}060$ of $2{,}554$ training items also map to a single opening",
     "few training items map to a single opening"),
    ("claim a principled threshold the paper does not have",
     "We know of no principled threshold that admits the group and",
     "A principled threshold admits the group and"),
    ("reintroduce the disowned tail gloss into the mechanism section",
     "the contrast doing most of the work is the central desk against\neverything else",
     "the contrast doing most of the work is a specialist team opening\nits own work"),
    ("promote the cross-target ordering to a prediction",
     "rather than predicted by it: the mechanism says nothing about how",
     "and predicted by it: the mechanism says exactly how"),
    # -- round eight.
    ("hide that reopening's shrinkage is unresolved",
     "is \\emph{not} resolvably different from zero",
     "is resolvably different from zero"),
    ("overstate the reopening significance",
     "($P \\le 0$ is $0.03$)", "($P \\le 0$ is $0.00$)"),
    ("drop the right-censoring sensitivity",
     "The extract is\nright-censored too", "The extract is\nnot censored at the end"),
    ("widen the right-censoring band",
     "moves between $42\\%$ and\n$45\\%$", "moves between $12\\%$ and\n$75\\%$"),
    ("restore the estate framing of a training-split statistic",
     "generate $30.2\\%$ of training incidents",
     "generate $30.2\\%$ of incidents"),
    ("restore the false claim about where draw counts are recorded",
     "the count set by cost and recorded in the code that produces each",
     "recorded beside each figure in the result files"),

    # ================= round fifteen: the second organisation ============
    ("corrupt the second log's item count",
     "attribute with $704$ distinct values", "attribute with $904$ distinct values"),
    ("corrupt the second log's trace count",
     "on all $7{,}554$ traces", "on all $7{,}054$ traces"),
    ("corrupt the volvo first rung",
     "the same ladder gives $+0.238$", "the same ladder gives $+0.338$"),
    ("corrupt the volvo reduction",
     "a reduction of $61.3\\%$ $[54,68]$", "a reduction of $71.3\\%$ $[54,68]$"),
    ("narrow the volvo interval inward",
     "a reduction of $61.3\\%$ $[54,68]$", "a reduction of $61.3\\%$ $[55,67]$"),
    ("flip the volvo coupling caveat to favour us",
     "should be read as an upper bound rather than",
     "should be read as a lower bound rather than"),
    ("delete the volvo coupling caveat entirely",
     "and the Volvo\nreduction should be read as an upper bound rather than "
     "as a second draw from\nthe same distribution.", ""),
    # ================= round fifteen: the design space ===================
    ("corrupt the design-space maximum",
     "runs $\\mathbf{36.1\\%}$ to $\\mathbf{48.3\\%}$",
     "runs $\\mathbf{36.1\\%}$ to $\\mathbf{45.3\\%}$"),
    ("raise the design-space floor to protect the title",
     "runs $\\mathbf{36.1\\%}$ to $\\mathbf{48.3\\%}$",
     "runs $\\mathbf{40.1\\%}$ to $\\mathbf{48.3\\%}$"),
    ("delete the admission that the low end is nearer a third",
     "At the low end of the design space it is closer to a third.", ""),
    # ================= round fifteen: the withdrawn mechanism legs =======
    ("corrupt the floor at matched granularity",
     "the floor retains $87.5\\% \\pm 3.6\\%$", "the floor retains $67.5\\% \\pm 3.6\\%$"),
    ("corrupt the z that fails the bar",
     "a margin of $3.5$ points at\n$z=0.9$", "a margin of $3.5$ points at\n$z=2.9$"),
    ("un-withdraw the margin",
     "We therefore withdraw the\nmargin.", "We therefore retain the\nmargin."),
    ("corrupt the entropy ratio behind the tautology",
     "that ratio is $3.09$", "that ratio is $2.09$"),
    ("corrupt the mutual information",
     "share\n$1.47$ bits of mutual information", "share\n$2.47$ bits of mutual information"),
    ("re-assert the direction the identity forbids",
     "its \\emph{direction} is not measurable this way",
     "its \\emph{direction} is measurable this way"),
    # ================= round fifteen: the new disclosures ================
    ("corrupt the impact-urgency cell count",
     "$19$ occupied cells", "$21$ occupied cells"),
    ("corrupt the per-item lookup AUC",
     "scores $0.744$, against", "scores $0.844$, against"),
    ("corrupt the service-component gain",
     "Service Component WBS (aff) & $256$   & 0.722 & $+0.078$",
     "Service Component WBS (aff) & $256$   & 0.722 & $+0.098$"),
    ("corrupt the marginal over the service component",
     "marginal over the service component & --- & --- & $+0.023$",
     "marginal over the service component & --- & --- & $+0.073$"),
    # ===== the whitelist channel: three fabrications an audit landed =====
    ("fabricate a multi-organisation replication",
     "and the ordering never\nreverses.",
     "and the ordering never\nreverses, replicated across $7$ further organisations."),
    ("fabricate a confidence level",
     "and the ordering never\nreverses.",
     "and the ordering never\nreverses, at $95\\%$ confidence on every rung."),
    ("fabricate independent extracts",
     "and the ordering never\nreverses.",
     "and the ordering never\nreverses, confirmed on $10$ independent extracts."),

    # ===== ROUND SIXTEEN =================================================
    # Section 8 was rebuilt and sections 4, 5 and 6 gained new controls.
    # Every new claim gets a corruption, and so does every new WITHDRAWAL:
    # a retraction that can be quietly softened is not a retraction.

    # -- 8.1, the tie census that justifies the withdrawal
    ("understate the share of the naive top-5% that is a tie",
     "$635$ --- $93.1\\%$ of\nthe review budget",
     "$635$ --- $43.1\\%$ of\nthe review budget"),
    ("corrupt the tied block's own outcome rate",
     "that block is\nreassigned at $0.534$", "that block is\nreassigned at $0.734$"),
    ("hide that the naive baseline's own top is worse than guessing",
     "its cut contain $9$ reassignment-bound incidents, a rate below the "
     "base rate", "its cut contain $409$ reassignment-bound incidents"),
    ("swap the honest baseline's tie structure",
     "with $590$ of $682$ ranked strictly above the cut and only $92$",
     "with $92$ of $682$ ranked strictly above the cut and only $590$"),
    ("inflate the oracle-policy honest arm",
     "including the oracle\n($+24$ $[+9,+40]$)",
     "including the oracle\n($+94$ $[+9,+40]$)"),
    ("delete the sentence that states the withdrawal",
     "A\nquantity whose sign is set by how a coin lands inside a "
     "$1{,}944$-row block\nis not a measurement of information, and we "
     "withdraw it.",
     "The reported figure is the expectation under a random tie-break."),
    # -- 8.1, the repair that cannot work
    ("claim the encoding repair worked",
     "the\ncomposite encoding emits $19$ distinct scores, fewer than the "
     "one-hot\nmodel's, not more",
     "the\ncomposite encoding emits $190$ distinct scores, more than the "
     "one-hot\nmodel's"),
    ("inflate the intake block's cardinality",
     "The four\nintake fields take $23$ distinct combinations",
     "The four\nintake fields take $203$ distinct combinations"),

    # -- 8.2, the decision curve
    ("corrupt the increment at the threshold that carries the claim",
     "it adds $86.9$ reassignment-bound incidents",
     "it adds $186.9$ reassignment-bound incidents"),
    ("swap the two arms at the threshold the claim is made at",
     "arrivals over the\ngroup-aware baseline and $92.8$ over the intake "
     "block",
     "arrivals over the\ngroup-aware baseline and $32.8$ over the intake "
     "block"),
    ("widen the region where the increment is resolved",
     "contiguous run from $0.100$ to $0.425$",
     "contiguous run from $0.100$ to $0.825$"),
    ("swap a net-benefit table row's two arms",
     "$0.30$ & $+64.9$ [$59.8,70.2$] & $+69.9$ [$64.7,74.8$]",
     "$0.30$ & $+69.9$ [$59.8,70.2$] & $+64.9$ [$64.7,74.8$]"),
    ("flip the sign of the negative region",
     "reaching $-16.1$ $[-23.0,-8.9]$ per\nthousand",
     "reaching $+16.1$ $[+8.9,+23.0]$ per\nthousand"),
    ("delete the admission that the item can be worth nothing",
     "adding item identity\nto a model that already knows the opening group "
     "makes the desk worse off",
     "the increment is not resolvable at that threshold"),
    ("corrupt the calibration slope that identifies the weak arm",
     "run $1.391$, $1.185$ and $1.040$", "run $0.391$, $1.185$ and $1.040$"),
    ("corrupt a Brier score", "$0.232$ for the intake block",
     "$0.132$ for the intake block"),

    # -- section 4, the congestion control and the central desk
    ("weaken the congestion control",
     "measured value from $+0.103$ to $+0.100$",
     "measured value from $+0.103$ to $+0.060$"),
    ("corrupt the congestion-adjusted reduction",
     "the reduction from $43.7\\%$ to $45.7\\%$ $[41,50]$",
     "the reduction from $43.7\\%$ to $65.7\\%$ $[41,50]$"),
    ("claim the free features carry signal on their own",
     "the same four features score\n$0.497$",
     "the same four features score\n$0.697$"),
    ("flip the direction that answers the tautology objection",
     "It reassigns \\emph{less}: $0.309$ against $0.603$",
     "It reassigns \\emph{more}: $0.603$ against $0.309$"),
    ("corrupt the central-desk contrast's interval",
     "a difference of $-0.294$\n$[-0.315,-0.275]$",
     "a difference of $-0.294$\n$[-0.515,-0.275]$"),
    ("overstate what the free field predicts on its own",
     "applied as a lookup with no model, scores\n$0.642$",
     "applied as a lookup with no model, scores\n$0.942$"),

    # -- section 5, the determinism argument that draws the admission line
    ("corrupt the field the admissibility argument does not dispose of",
     "it varies on $58$ of $2{,}929$ items, carrying $8.7\\%$ of",
     "it varies on $580$ of $2{,}929$ items, carrying $8.7\\%$ of"),
    ("swap the two incident-mass figures that place the line",
     "carrying $8.7\\%$ of\nincidents, where the opening group varies on "
     "$565$ items carrying $92.5\\%$",
     "carrying $92.5\\%$ of\nincidents, where the opening group varies on "
     "$565$ items carrying $8.7\\%$"),
    ("assert determinism the data does not support",
     "Neither varies on a single one of the\n$2{,}929$ items",
     "Neither varies on more than three of the\n$2{,}929$ items"),

    # -- section 6, the two-rung encoder null
    ("hide the intake-rung encoder residual",
     "returns\n$+0.0002 \\pm 0.0015$ and $-0.0036 \\pm 0.0025$",
     "returns\n$+0.0002 \\pm 0.0015$ and $-0.0006 \\pm 0.0025$"),
    ("reverse the direction of the encoder correction",
     "from\n$47.1\\%$ to $50.5\\%$ under boosting",
     "from\n$47.1\\%$ to $40.5\\%$ under boosting"),
    ("understate the size of the correction",
     "worth at\nmost $3.4$ percentage points", "worth at\nmost $0.4$ percentage points"),

    # -- the corrections list itself
    ("restore the old count of corrections",
     "Eight errors of our own are reported", "Six errors of our own are reported"),
    ("soften the withdrawal in the corrections list",
     "moves the naive arm from $-26$ to $+608$. We\nwithdraw the factor",
     "moves the naive arm from $-26$ to $+608$. We\nqualify the factor"),

    # -- restatements, which is where a retracted figure survives
    ("corrupt the abstract's lookup result",
     "of any kind --- scores $0.744$ against the full model's $0.748$",
     "of any kind --- scores $0.844$ against the full model's $0.748$"),
    ("corrupt the conclusion's marginal",
     "with instance identity adding\n$+0.023$ over it",
     "with instance identity adding\n$+0.123$ over it"),
    ("fabricate a third organisation in the conclusion",
     "the\npattern replicates on a second organisation.",
     "the\npattern replicates on a second organisation, and on $3$ others."),
    # ===== reversals of words, every number left correct =================
    ("flip the free-field reading from a lower to an upper bound",
     "our $+0.103$ is a lower bound", "our $+0.103$ is an upper bound"),
    ("reverse the diversity argument",
     "cannot be less diverse than the teams", "cannot be more diverse than the teams"),
    ("delete the exclusion of the reverse leg",
     "The leg is floor-dominated and we exclude it.", ""),
    ("assert leakage in the encoders",
     "Encoders and rankings are fit on training data only",
     "Encoders and rankings are fit on all data"),
    ("assert leakage in the target encoder",
     "fitted on training only, out-of-fold", "fitted on all rows, in-fold"),
    ("promote a trend to a resolved series",
     "so only the trend is claimed", "so each step is individually resolved"),
    ("admit the field the paper excludes",
     "We exclude it as near-deterministic in the item",
     "We admit it as near-deterministic in the item"),
    ("turn the target back into an error",
     "which is routine handling and not error",
     "which is misrouting error and not routine handling"),
    ("pick the reading the paper refuses to pick",
     "so we choose none of them", "so we choose the second"),
    ("delete the causation disclaimer",
     "Nor do we claim\na direction of causation:", "The item drives who logs the ticket:"),
    ("turn the motivation into a saving",
     "we use this to motivate the task, not as a recoverable saving",
     "we use this to motivate the task, and as a recoverable saving"),
    ("promote the proxy to a direct measure",
     "Reassignment is a proxy for misrouting",
     "Reassignment is a direct measure of misrouting"),
    ("loosen the group's unique contribution",
     "under $0.01$ AUC and not resolvable more finely",
     "over $0.01$ AUC and not resolvable more finely"),
    ("swap the open and assignment group counts",
     "rows carry $50$ distinct groups where the \\texttt{Assignment}\nrows carry $218$",
     "rows carry $218$ distinct groups where the \\texttt{Assignment}\nrows carry $50$"),
    ("soften the asymmetry's withdrawal",
     "We withdraw the asymmetry and the directional claim it supported.",
     "We qualify the asymmetry and the directional claim it supported."),
    ("soften a correction that carries no number",
     "It is the group that logged the incident",
     "It is best described as the group that logged the incident"),
    ("soften the correction about the dataset claim",
     "which we had presented as a constraint rather than a choice. It was"
     " a choice.",
     "which was a reasonable reading at the time."),
    ("soften the recalibration's outcome",
     "applied to test, with no test outcome entering it. No conclusion"
     " below changes.",
     "applied to test, with no test outcome entering it. Most conclusions"
     " below are unchanged."),
    ("delete the concession that the oracle bound is asymmetric",
     "A contrast whose magnitude is governed by the size of one arm's tie"
     " block, rather than by what either arm knows, is measuring the block.",
     "The oracle policy is the fairer of the two bounds."),
    ("corrupt the interval-discipline restatement",
     "elsewhere refuses to resolve $+0.0017$ past two decimals",
     "elsewhere refuses to resolve $+0.0117$ past two decimals"),
    ("swap the item vocabulary counts",
     "across $2{,}929$ items, $2{,}554$\nseen in training",
     "across $2{,}554$ items, $2{,}929$\nseen in training"),

]


def flat(s):
    return re.sub(r"\s+", " ", s)


def apply(src, old, new):
    """Replace ignoring how LaTeX happened to wrap the line."""
    f_src, f_old = flat(src), flat(old)
    i = f_src.find(f_old)
    if i < 0:
        return None
    # walk the original string counting non-space characters to find the span
    def span(target_idx):
        seen = j = 0
        while j < len(src):
            if not src[j].isspace():
                if seen == target_idx:
                    return j
                seen += 1
            elif j and not src[j - 1].isspace():
                seen += 1
            j += 1
        return len(src)
    nonspace_before = len(flat(f_src[:i]).replace(" ", ""))
    # simpler: rebuild by regex allowing arbitrary whitespace between tokens
    pat = r"\s+".join(re.escape(t) for t in old.split())
    m = re.search(pat, src)
    if not m:
        return None
    return src[:m.start()] + new + src[m.end():]


def run():
    return subprocess.run([sys.executable, str(ROOT / "scripts" / "verify_paper.py")],
                          capture_output=True, text=True).returncode


shutil.copy(TEX, BAK)
caught = missed = skipped = 0
try:
    for name, old, new in CORRUPTIONS:
        src = BAK.read_text(encoding="utf-8")
        out = apply(src, old, new)
        if out is None or out == src:
            print(f"  SKIP     {name}  (pattern not found -- test is stale)")
            skipped += 1
            continue
        TEX.write_text(out, encoding="utf-8")
        if run() != 0:
            print(f"  caught   {name}")
            caught += 1
        else:
            print(f"  MISSED   {name}")
            missed += 1
finally:
    shutil.copy(BAK, TEX)
    BAK.unlink()

print(f"\n{caught} caught, {missed} missed, {skipped} skipped "
      f"of {len(CORRUPTIONS)}")
sys.exit(1 if (missed or skipped) else 0)
