#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `sql_circuit` - the origin's H4 pins, plus a differential against `jea_circuit`.

THE NINE H4 CASES ARE THE ORIGIN'S OWN (`sql_lift._selftest_h4`), reproduced rather than
paraphrased: the L7 crossover must fall out of the fold as a bridge NULL between the two measured
workloads, the speedups at each anchor must reproduce the measurement, the sign must flip across
the null, and a losing lift must SINK under a signed score. A cut that quietly changes one of
those is a rewrite wearing a refactor's clothes.

THE DIFFERENTIAL LOADS `jea/jea_circuit.py` BY PATH, never by name - importing it as
`jea_circuit` needs the `sys.path` insert the cut removes, so a by-name check would depend on the
defect it verifies the fix for. It asserts the two transcribed combines agree with the origin's
over a fixed grid, and is SKIPPED (not failed) once the origin is gone.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Protocol, cast

from substrate import sql_circuit as sc

_ORIGIN = Path(__file__).resolve().parent.parent / "jea" / "jea_circuit.py"
_REACH = ("Closure",)
_GRID = [(1.0, 2.0), (0.5, 0.25), (3.0, 3.0), (1e-3, 1e3)]
_SPEEDUP_TOL_SMALL = 1.0
_SPEEDUP_TOL_FULL = 0.05
_NULL_TOL = 1e-6
_FOLD_TOL = 1e-12

Cases = list[tuple[str, bool]]


class _Combine(Protocol):
    def __call__(self, c: sc.Carrier, a: float, b: float) -> float: ...


class _Origin(Protocol):
    """The two combines this module transcribed."""

    @property
    def parallel(self) -> _Combine: ...
    @property
    def series_schur(self) -> _Combine: ...


def _origin() -> _Origin | None:
    """Load `jea/jea_circuit.py` by PATH, or None when it is gone."""
    if not _ORIGIN.exists():
        return None
    spec = importlib.util.spec_from_file_location("_jea_circuit_origin", _ORIGIN)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return cast("_Origin", module)


def _check(cases: Cases, name: str, *, ok: bool) -> None:
    """Append one verdict to the run."""
    cases.append((name, ok))


def _h4_cases(cases: Cases) -> None:
    """Pin the origin's nine H4 verifications over the L7 reachability lift."""
    ns, nf = sc.MEAS.n_small, sc.MEAS.n_full
    rs, rf = sc.roofline(_REACH, n=ns), sc.roofline(_REACH, n=nf)
    _check(cases, "small-N: the lift wins", ok=rs["bridge"] > 0 and rs["regime"] == "lift")
    _check(
        cases,
        "small-N speedup reproduces ~275x",
        ok=abs(rs["speedup"] - sc.MEAS.spd_small) < _SPEEDUP_TOL_SMALL,
    )
    _check(cases, "full-N: eager wins", ok=rf["bridge"] < 0 and rf["regime"] == "eager")
    _check(
        cases,
        "full-N speedup reproduces ~0.7x",
        ok=abs(rf["speedup"] - sc.MEAS.spd_full) < _SPEEDUP_TOL_FULL,
    )
    nstar = sc.crossover(_REACH, ns, nf)
    _check(
        cases,
        "the bridge NULL lies strictly between the two workloads",
        ok=ns < nstar < nf and abs(sc.bridge(_REACH, nstar)) < _NULL_TOL,
    )
    _check(
        cases,
        "the sign FLIPS across the null",
        ok=sc.bridge(_REACH, nstar * 0.5) > 0 > sc.bridge(_REACH, nstar * 2.0),
    )
    _check(cases, "the verdict is workload-relative", ok=(rs["bridge"] > 0) != (rf["bridge"] > 0))
    _check(
        cases,
        "a losing lift SINKS at full N (signed score, breadth 2)",
        ok=sc.roofline(_REACH, 2, n=nf)["score"] < 0 < sc.roofline(_REACH, 2, n=ns)["score"],
    )
    _check(
        cases,
        "N-wide SWAR beats eager at full N",
        ok=sc.pipeline_g(_REACH, "swar", nf) > sc.pipeline_g(_REACH, "eager", nf),
    )


def _shape_cases(cases: Cases) -> None:
    """Pin the readout shape the origin's report() reads, and the Scan-only degenerate case."""
    r = sc.roofline(("Scan",), n=10.0)
    _check(cases, "Scan alone is not a materialized stage (k = 0)", ok=r["k"] == 0)
    _check(cases, "gain is the workload-relative speedup", ok=r["gain"] == r["speedup"])
    _check(
        cases,
        "i_eager/i_fused are the two conductances",
        ok=r["i_eager"] == r["G_eager"] and r["i_fused"] == r["G_cte"],
    )
    _check(
        cases,
        "N defaults to the estimate when unset",
        ok=sc.roofline(_REACH)["N"] == sc.n_estimate(),
    )
    _check(cases, "a zero divisor reads as zero conductance", ok=sc.FLOAT.div(1.0, 0.0) == 0.0)


def _differential_cases(cases: Cases) -> None:
    """Assert the transcribed combines agree with `jea_circuit`'s, or skip when it is gone."""
    o = _origin()
    if o is None:
        _check(cases, "differential: origin retired, skipped", ok=True)
        return
    for a, b in _GRID:
        _check(
            cases,
            f"series_schur agrees with the origin at ({a}, {b})",
            ok=abs(sc.series_schur(sc.FLOAT, a, b) - o.series_schur(sc.FLOAT, a, b)) < _FOLD_TOL,
        )
        _check(
            cases,
            f"parallel agrees with the origin at ({a}, {b})",
            ok=abs(sc.parallel(sc.FLOAT, a, b) - o.parallel(sc.FLOAT, a, b)) < _FOLD_TOL,
        )


def main() -> int:
    """Run every case; exit 1 if any failed."""
    cases: Cases = []
    _h4_cases(cases)
    _shape_cases(cases)
    _differential_cases(cases)
    failed = [name for name, ok in cases if not ok]
    for name in failed:
        sys.stdout.write(f"  FAIL  {name}\n")
    sys.stdout.write(f"sql_circuit_selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
