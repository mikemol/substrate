#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `key_partition` - the kind and identity partitions of a ratchet's added keys.

THE REFUSALS ARE CASED BEFORE THE PARTITIONS: an undeclared schema and a 2-field schema both
return `(None, why)`, because the origin's first cut reported a 2-field gate as "35 kind(s), each
x1" and that false shape is the defect this module exists to refuse. Then the kind partition
over a 3-field fixture (largest first, ties by label, a malformed key in its own bucket, the
sample the smallest key), and the identity partition within one kind (the path dropped, other
kinds excluded, malformed keys skipped) - including on a reversed-path schema, where the
identity is the field that is NOT the path.

THE DIFFERENTIAL IS BY PATH against `figures.added_kinds` / `figures.kind_concentration` over a
LIVE gate (`check_ban_ratchet.py`, the arity-3 case), driven with `ratchet_census.census`'s
added keys - skipped, not failed, when figures will not import or the gate cannot be censused,
and it says how many added keys it covered.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Protocol, cast

from substrate import key_partition as kp
from substrate import key_spec, ratchet_census

_ROOT = Path(__file__).resolve().parent.parent
_LIVE_GATE = "check_ban_ratchet.py"

Cases = list[tuple[str, bool]]
Rows = list[tuple[str, int, str]]


class _Figures(Protocol):
    def added_kinds(self, name: str) -> tuple[Rows | None, str | None]: ...
    def kind_concentration(self, name: str, kind: str) -> tuple[Rows | None, str | None]: ...


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


_BAN = key_spec.KeySpec(gate="ban", baseline="", sep="::", path_field=0, arity=3, noun="")
_PUBLIC = key_spec.KeySpec(gate="public", baseline="", sep="::", path_field=0, arity=2, noun="")
_REV = key_spec.KeySpec(gate="sumtype", baseline="", sep="::", path_field=1, arity=2, noun="")
_KEYS = [
    "a/X.agda::M::using",
    "a/Y.agda::M::using",
    "b/Z.agda::N::as",
    "a/X.agda::N::using",
    "broken",
    "c/W.agda::N::renaming",
]


def _refusal_cases(cases: Cases) -> None:
    """Pin the two refusals, on both partitions."""
    undeclared = "no gate_keys.SCHEMA entry -- the key's fields are undeclared"
    _check(
        cases,
        "by_kind refuses an undeclared schema",
        ok=kp.by_kind(_KEYS, None) == (None, undeclared),
    )
    rows, why = kp.by_kind(["p::n"], _PUBLIC)
    _check(
        cases,
        "by_kind refuses a 2-field schema and names the shape",
        ok=rows is None and why == "keys are 2-field (path::name) -- no kind field to partition by",
    )
    _check(
        cases,
        "concentration refuses an undeclared schema",
        ok=kp.concentration(_KEYS, None, "using")[0] is None,
    )


def _kind_cases(cases: Cases) -> None:
    """Pin the kind partition over the fixture."""
    rows, why = kp.by_kind(_KEYS, _BAN)
    _check(
        cases,
        "by_kind partitions on the trailing field, largest first, ties by label",
        ok=why is None
        and rows
        == [
            ("using", 3, "a/X.agda::M::using"),
            ("(malformed)", 1, "broken"),
            ("as", 1, "b/Z.agda::N::as"),
            ("renaming", 1, "c/W.agda::N::renaming"),
        ],
    )
    _check(
        cases,
        "an empty key set is an empty partition, not a refusal",
        ok=kp.by_kind([], _BAN) == ([], None),
    )


def _concentration_cases(cases: Cases) -> None:
    """Pin the identity partition within one kind."""
    rows, why = kp.concentration(_KEYS, _BAN, "using")
    _check(
        cases,
        "concentration drops the path, keeps the other kinds out, skips malformed",
        ok=why is None
        and rows == [("M::using", 2, "a/X.agda::M::using"), ("N::using", 1, "a/X.agda::N::using")],
    )
    _check(
        cases,
        "a kind with no keys concentrates nowhere",
        ok=kp.concentration(_KEYS, _BAN, "nope") == ([], None),
    )
    rows, _why = kp.concentration(["Name::a/P.agda", "Name::a/Q.agda", "Other::a/P.agda"], _REV, "")
    _check(
        cases,
        "on a reversed-path 2-field schema the identity is field 0, kind ignored",
        ok=rows == [("Name", 2, "Name::a/P.agda"), ("Other", 1, "Other::a/P.agda")],
    )


def _differential_cases(cases: Cases) -> None:
    """Agree with figures over a live arity-3 gate, when both sides can read it."""
    fig = _load("_figures_origin", _ROOT / "catalog" / "library" / "figures.py")
    got, _why = ratchet_census.census(_LIVE_GATE)
    if fig is None or got is None:
        _check(cases, "differential: figures or the live gate unavailable, skipped", ok=True)
        return
    f = cast("_Figures", fig)
    spec = key_spec.spec_for(_LIVE_GATE)
    # Say what the differential covered: a passing case with an unread denominator is a zero
    # that gets banked as coverage.
    sys.stdout.write(f"  differential over {_LIVE_GATE}: {len(got.added)} added key(s)\n")
    mine = kp.by_kind(got.added, spec)
    theirs = f.added_kinds(_LIVE_GATE)
    _check(
        cases,
        f"differential: added_kinds agrees over {len(got.added)} added key(s)",
        ok=mine == theirs,
    )
    kind = mine[0][0][0] if mine[0] else "using"
    _check(
        cases,
        f"differential: kind_concentration agrees on the largest kind ({kind})",
        ok=kp.concentration(got.added, spec, kind) == f.kind_concentration(_LIVE_GATE, kind),
    )


def main() -> int:
    """Run every case; exit 1 if any failed."""
    cases: Cases = []
    _refusal_cases(cases)
    _kind_cases(cases)
    _concentration_cases(cases)
    _differential_cases(cases)
    failed = [name for name, ok in cases if not ok]
    for name in failed:
        sys.stdout.write(f"  FAIL  {name}\n")
    sys.stdout.write(f"key_partition_selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
