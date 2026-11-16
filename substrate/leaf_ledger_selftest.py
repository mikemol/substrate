#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `leaf_ledger` - the one spelling of the leaf-verify census file.

THE ROUND-TRIP IS THE LOAD-BEARING CASE: what `write` emits, `read` returns, stamp and rows alike,
with an empty `cited` surviving as ''. The padding case pins the origin readers' tolerance of a
short row; the stamp cases pin the three states a ledger can be in (absent, present without a
stamp, stamped). `is_current` is driven in both directions.

TWO DIFFERENTIALS BY PATH, over the LIVE ledger when it exists: `figures.census_stamp` against
`stamp_of`, and `figures.census_is_current` against `is_current` over the tree's stamp now -
skipped, not failed, when `figures` will not import here (it inserts scratch/ onto sys.path at
load and reaches the split_pipeline driver). And the `split_pipeline` shim's `_read_ledger`
against `read`, over the same live file.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path
from typing import Protocol, cast

from substrate import agda_tree_state, leaf_ledger

_ROOT = Path(__file__).resolve().parent.parent
_FIGURES = _ROOT / "catalog" / "library" / "figures.py"
_DRIVER = _ROOT / "scratch" / "split_pipeline.py"

Cases = list[tuple[str, bool]]


class _Figures(Protocol):
    def census_stamp(self) -> str | None: ...
    def census_is_current(self) -> tuple[bool, str]: ...


class _Driver(Protocol):
    def _read_ledger(self) -> tuple[str, list[tuple[str, str, str]]]: ...


def _load(name: str, path: Path) -> object | None:
    """Load a module by PATH, or None when it is gone or will not import here."""
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (ImportError, OSError, RuntimeError):
        return None
    return module


def _check(cases: Cases, name: str, *, ok: bool) -> None:
    """Append one verdict to the run."""
    cases.append((name, ok))


def _format_cases(cases: Cases, root: Path) -> None:
    """Pin the round-trip, the padding, and the three stamp states."""
    p = root / "l.tsv"
    rows = [
        ("a/B.agda", "clean", ""),
        ("a/C.agda", "dependency", "a/B.agda"),
        ("a/D.agda", "own", None),
    ]
    _check(cases, "write reports success", ok=leaf_ledger.write(p, "3:1.5", rows))
    stamp, back = leaf_ledger.read(p)
    _check(cases, "the round-trip returns the stamp", ok=stamp == "3:1.5")
    _check(
        cases,
        "the round-trip returns every row, None cited as ''",
        ok=back
        == [
            ("a/B.agda", "clean", ""),
            ("a/C.agda", "dependency", "a/B.agda"),
            ("a/D.agda", "own", ""),
        ],
    )
    _check(cases, "stamp_of reads the same stamp", ok=leaf_ledger.stamp_of(p) == "3:1.5")
    short = root / "short.tsv"
    short.write_text("x.agda\tclean\ny.agda\n\n", encoding="utf-8")
    _check(
        cases,
        "a short row is padded, a blank line skipped, and no stamp reads as None",
        ok=leaf_ledger.read(short) == (None, [("x.agda", "clean", ""), ("y.agda", "", "")]),
    )
    _check(
        cases, "stamp_of is None for an unstamped ledger", ok=leaf_ledger.stamp_of(short) is None
    )
    _check(
        cases,
        "stamp_of is None for an absent ledger",
        ok=leaf_ledger.stamp_of(root / "nope.tsv") is None,
    )
    _check(
        cases,
        "a write into a missing directory reports failure, not a verdict",
        ok=leaf_ledger.write(root / "no" / "dir" / "l.tsv", "1:1", []) is False,
    )


def _current_cases(cases: Cases) -> None:
    """Drive is_current through its three verdicts."""
    _check(
        cases,
        "absent ledger: not current, says the census never ran",
        ok=leaf_ledger.is_current(None, "1:1")
        == (False, "no leaf-verify ledger on disk -- the census has never run"),
    )
    ok, why = leaf_ledger.is_current("1:1", "2:2")
    _check(
        cases,
        "a moved tree: STALE, both stamps named",
        ok=not ok and "recorded 1:1, tree is 2:2" in why,
    )
    _check(
        cases,
        "a matching stamp is current",
        ok=leaf_ledger.is_current("1:1", "1:1") == (True, "ledger stamp 1:1 matches the tree"),
    )


def _log_cases(cases: Cases) -> None:
    """log_for is a lookup keyed on the module name."""
    idx = {"Substrate.A.B": "/b/Substrate/A/B.agdai.log"}
    _check(
        cases,
        "log_for resolves an agda-relative source through the index",
        ok=leaf_ledger.log_for("Substrate/A/B.agda", idx) == "/b/Substrate/A/B.agdai.log",
    )
    _check(
        cases,
        "log_for is None for a module the build never logged",
        ok=leaf_ledger.log_for("Substrate/A/C.agda", idx) is None,
    )


def _differential_cases(cases: Cases) -> None:
    """Agree with the two origin readers over the live ledger, when both are reachable."""
    live = _ROOT / leaf_ledger.LEDGER
    if not live.exists():
        _check(cases, "differential: no live ledger, skipped", ok=True)
        return
    stamp, rows = leaf_ledger.read(live)
    fig = _load("_figures_origin", _FIGURES)
    if fig is None:
        _check(cases, "differential (figures): origin unavailable, skipped", ok=True)
    else:
        f = cast("_Figures", fig)
        _check(
            cases,
            "differential: figures.census_stamp agrees with stamp_of",
            ok=f.census_stamp() == leaf_ledger.stamp_of(live),
        )
        now = agda_tree_state.tree_stamp(str(_ROOT / "agda"))
        _check(
            cases,
            "differential: figures.census_is_current agrees with is_current",
            ok=f.census_is_current() == leaf_ledger.is_current(stamp, now),
        )
    drv = _load("_driver_origin", _DRIVER)
    if drv is None:
        _check(cases, "differential (driver): shim unavailable, skipped", ok=True)
        return
    d = cast("_Driver", drv)
    d_stamp, d_rows = d._read_ledger()  # noqa: SLF001 - the shim's spelling
    _check(
        cases,
        "differential: the driver's _read_ledger agrees with read",
        ok=(d_stamp or None) == stamp and d_rows == rows,
    )


def main() -> int:
    """Run every case; exit 1 if any failed."""
    cases: Cases = []
    with tempfile.TemporaryDirectory() as tmp:
        _format_cases(cases, Path(tmp))
    _current_cases(cases)
    _log_cases(cases)
    _differential_cases(cases)
    failed = [name for name, ok in cases if not ok]
    for name in failed:
        sys.stdout.write(f"  FAIL  {name}\n")
    sys.stdout.write(f"leaf_ledger_selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
