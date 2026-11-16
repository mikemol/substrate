#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The H4 conductance-circuit roofline - a lift's cost as a circuit, never a flat scalar.

THE FIRST CUT OF THE DRAIN'S THIRD FILE (`jea/metalanguage/sql_lift.py:371-498`, W4 tick 29).
L7 MEASURED the flat `gain = 2.5 * k` heuristic WRONG: the same `WITH RECURSIVE` reachability lift
is 275x on a small on-demand closure and 0.7x - a LOSS - on the full-graph closure. A verdict that
FLIPS with the workload N cannot be expressed by a size-independent constant. Here a cost is a SUM
of a launch term and a work/parallelism term, and which dominates is an OUTPUT of the sum;
conductance is 1/cost; a pipeline's conductance is the series/parallel FOLD of its stages; and a
lift is steered by a Wheatstone bridge - the signed difference of two conductances. The 275x/0.7x
crossover is a bridge NULL of that fold at the estimated N, not a constant anyone typed.

THE TWO CIRCUIT FOLDS ARE TRANSCRIBED FROM `jea/jea_circuit.py`, AND THAT IS A RE-DERIVATION TO
RECORD, NOT HIDE. `series_schur` (`:68`, the Kron step `a*b/(a+b)`) and `parallel` (`:63`, KCL
addition) are one-liners over a carrier with `add`/`mul`/`div`, and `jea_circuit` is reachable
only through a `sys.path` insert - the origin's own line 368. A clean module cannot import it, so
the kernel is carried here as a `Carrier` Protocol plus the two combines. The differential suite
loads the origin BY PATH and asserts both folds agree, which is what makes this a promotion rather
than a fork (the `climode` precedent).

THE HONEST BOUNDARY IS THE ORIGIN'S, KEPT VERBATIM: the FORM is structural (launch + work/P); the
residual is the two L7 anchors CALIBRATED ONCE - a model fit to a measurement, not a proof. A
mis-specified term self-reveals as a mispredicted crossover, which is exactly what the suite pins.

THE INPUT IS A HEAD SEQUENCE AND A BREADTH, NOT A `RelTerm`. The origin's `roofline(rt)` reads
`rt.heads` and `len(rt.sites)` and nothing else; taking those two directly keeps this module free
of the term class, which is cut 2's business. The origin's dict keys (`k`, `gain`, `i_eager`,
`i_fused`, `score`, ...) are preserved because `report()` reads them.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol, TypedDict

# The L7 measurement the eager side is calibrated to (byte-exact 59794 in the origin's record).
SPEEDUP_SMALL = 275.0
SPEEDUP_FULL = 0.7
N_SMALL = 1.0
N_FULL = 1000.0
# Default estimated closure/result cardinality when the caller has not measured one (L5 does).
N_ESTIMATE_ENV = "SQL_LIFT_N"
N_ESTIMATE_DEFAULT = 100.0
# SWAR width: the N-wide set-at-a-time operating point's parallelism.
SWAR_WIDTH = 64.0


class Carrier(Protocol):
    """The arithmetic a circuit folds over - `jea_circuit.Carrier`'s surface."""

    @property
    def zero(self) -> float:
        """Return the additive identity."""
        ...

    def add(self, a: float, b: float) -> float:
        """Return a + b."""
        ...

    def mul(self, a: float, b: float) -> float:
        """Return a * b."""
        ...

    def div(self, a: float, b: float) -> float:
        """Return a / b, or the carrier's answer for a zero divisor."""
        ...


class FloatCarrier:
    """Plain floats, with division by zero reading as zero conductance."""

    @property
    def zero(self) -> float:
        """Return 0.0."""
        return 0.0

    def add(self, a: float, b: float) -> float:
        """Return a + b."""
        return a + b

    def mul(self, a: float, b: float) -> float:
        """Return a * b."""
        return a * b

    def div(self, a: float, b: float) -> float:
        """Return a / b, or 0.0 when b is zero."""
        return a / b if b != 0 else 0.0


FLOAT = FloatCarrier()


def series_schur(c: Carrier, a: float, b: float) -> float:
    """Schur-eliminate the shared node of a two-edge series path: a*b/(a+b), the Kron step."""
    return c.div(c.mul(a, b), c.add(a, b))


def parallel(c: Carrier, a: float, b: float) -> float:
    """Add parallel conductances (KCL at the shared node)."""
    return c.add(a, b)


def series_fold(c: Carrier, gs: list[float]) -> float:
    """Fold a SERIES pipeline of stage conductances - costs add, so they combine harmonically."""
    it = iter(gs)
    acc = next(it)
    for g in it:
        acc = series_schur(c, acc, g)
    return acc


def parallel_fold(c: Carrier, gs: list[float]) -> float:
    """Fold PARALLEL branches - their conductances add."""
    acc = c.zero
    for g in gs:
        acc = parallel(c, acc, g)
    return acc


@dataclass(frozen=True)
class Measurement:
    """The two L7 anchors: a speedup at a small workload and one at a full workload."""

    spd_small: float = SPEEDUP_SMALL
    spd_full: float = SPEEDUP_FULL
    n_small: float = N_SMALL
    n_full: float = N_FULL


MEAS = Measurement()


def calibrate_eager(m: Measurement = MEAS, lc: float = 1.0, sc: float = 1.0) -> tuple[float, float]:
    """Fit eager's (launch, slope) so cost_eager/cost_cte hits BOTH anchors; N* is derived."""
    b_s = m.spd_small * (lc + sc * m.n_small)
    b_f = m.spd_full * (lc + sc * m.n_full)
    se = (b_f - b_s) / (m.n_full - m.n_small)
    return b_s - se * m.n_small, se


_LE, _SE = calibrate_eager()

# (launch, work, parallelism) per operating point; slope = work / parallelism.
OPS: dict[str, tuple[float, float, float]] = {
    "eager": (_LE, _SE, 1.0),
    "cte": (1.0, 1.0, 1.0),
    "swar": (1.0, 1.0, SWAR_WIDTH),
}


def n_estimate() -> float:
    """Return the estimated workload: `SQL_LIFT_N` if set, else the default."""
    return float(os.environ.get(N_ESTIMATE_ENV, str(N_ESTIMATE_DEFAULT)))


def op_cost(op: str, n: float) -> float:
    """Return launch + work*N/P for one operating point - BOTH terms, the regime an output."""
    launch, work, par = OPS[op]
    return launch + (work * n) / par


def op_g(op: str, n: float) -> float:
    """Return the conductance 1/cost of one operating point at workload N."""
    return FLOAT.div(1.0, op_cost(op, n))


def pipeline_g(heads: tuple[str, ...], op: str, n: float, branches: int = 1) -> float:
    """Return a pipeline's conductance: series over heads, a Closure fanning out in parallel."""
    gs: list[float] = []
    for h in heads:
        if h == "Scan":
            continue
        if h == "Closure":
            gs.append(parallel_fold(FLOAT, [op_g(op, n)] * max(1, branches)))
        else:
            gs.append(op_g(op, n))
    if not gs:
        gs = [op_g(op, n)]
    return series_fold(FLOAT, gs)


def bridge(
    heads: tuple[str, ...], n: float, lifted: str = "cte", eager: str = "eager", branches: int = 1
) -> float:
    """Return the Wheatstone bridge: >0 the lift wins, <0 eager wins, 0 the crossover."""
    return pipeline_g(heads, lifted, n, branches) - pipeline_g(heads, eager, n, 1)


class Roofline(TypedDict):
    """The H4 readout - keys preserved for the origin's `report()`."""

    k: int
    N: float
    G_eager: float
    G_cte: float
    G_swar: float
    bridge: float
    speedup: float
    gain: float
    regime: str
    i_eager: float
    i_fused: float
    score: float


def roofline(
    heads: tuple[str, ...], breadth: int = 0, n: float | None = None, branches: int = 1
) -> Roofline:
    """Return the signed conductance advantage of lifting `heads` at workload N, times breadth."""
    if n is None:
        n = n_estimate()
    k = len([h for h in heads if h != "Scan"])
    g_e = pipeline_g(heads, "eager", n, 1)
    g_c = pipeline_g(heads, "cte", n, branches)
    g_s = pipeline_g(heads, "swar", n, branches)
    br = g_c - g_e
    spd = (g_c / g_e) if g_e > 0 else float("inf")
    return Roofline(
        k=k,
        N=n,
        G_eager=g_e,
        G_cte=g_c,
        G_swar=g_s,
        bridge=br,
        speedup=spd,
        gain=spd,
        regime="lift" if br > 0 else "eager",
        i_eager=g_e,
        i_fused=g_c,
        score=br * max(1, breadth),
    )


def crossover(heads: tuple[str, ...], lo: float, hi: float, steps: int = 60) -> float:
    """Return the bridge NULL between two workloads by bisection - the crossover as an OUTPUT."""
    for _ in range(steps):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if bridge(heads, mid) > 0 else (lo, mid)
    return 0.5 * (lo + hi)
