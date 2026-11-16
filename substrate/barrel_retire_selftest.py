#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `barrel_retire` and `agda_tree_state.modules_under` - cut 11's two halves.

THE RETIRE VERDICT IS DRIVEN OVER SUPPLIED FACTS, one case per branch in the origin's order:
already retired (refresh still owed), live references (the rewire remedy named), no leaf
directory, an empty one (a directory's existence is not its content), coverage not consulted,
a barrel that still owns a name (the real-module refusal), and the delete. The listing caps
are cased so a long hit list elides rather than floods.

`modules_under` IS DIFFERENCED BY PATH against `split_unblock._under`, which walks a
RELATIVE `agda/` - so the suite changes into a temporary root for that arm and changes back
in a `finally`, because a cwd left changed would make every later case read the wrong tree.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
from pathlib import Path
from typing import Protocol, cast

from substrate import agda_tree_state as ts
from substrate import barrel_retire as br

_ORIGIN = Path(__file__).resolve().parent.parent / "scratch" / "split_unblock.py"
_MOD = "Substrate.Foundation.Sum"
_REL = "agda/Substrate/Foundation/Sum.agda"
_HITS: tuple[br.Hit, ...] = tuple(
    (f"agda/Substrate/C{i}.agda", 3, "open", f"open import {_MOD}\n") for i in range(25)
)

Cases = list[tuple[str, bool]]


class _Origin(Protocol):
    def _under(self, modname: str) -> list[str]: ...


def _origin() -> _Origin | None:
    """Load `split_unblock.py` by PATH, or None when it is gone or will not import here."""
    if not _ORIGIN.exists():
        return None
    spec = importlib.util.spec_from_file_location("_split_unblock_origin", _ORIGIN)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except ImportError:
        return None
    return cast("_Origin", module)


def _check(cases: Cases, name: str, *, ok: bool) -> None:
    """Append one verdict to the run."""
    cases.append((name, ok))


def _verdict_cases(cases: Cases) -> None:
    """Pin every branch of the retire decision."""
    v = br.verdict(_MOD, _REL, br.Inputs(exists=False))
    _check(
        cases,
        "an absent barrel is already-retired, and still owes the refresh",
        ok=v.action == br.ALREADY_RETIRED and "already retired" in v.lines[0],
    )
    v = br.verdict(_MOD, _REL, br.Inputs(exists=True, hits=_HITS))
    _check(
        cases,
        "live references refuse, list 20, elide the rest, and name the rewire remedy",
        ok=v.action == br.REFUSE
        and v.lines[0].startswith("✗ 25 LIVE")
        and v.lines[-1] == "   … 5 more"
        and v.remedy is not None
        and "--rewire-only --apply" in v.remedy,
    )
    v = br.verdict(_MOD, _REL, br.Inputs(exists=True, has_leaf_dir=False))
    _check(
        cases,
        "no leaf directory: not a consumed barrel",
        ok=v.action == br.REFUSE and "does not exist" in v.lines[0],
    )
    v = br.verdict(_MOD, _REL, br.Inputs(exists=True, has_leaf_dir=True, leaves=()))
    _check(
        cases,
        "an EMPTY leaf directory is an abandoned split, not a barrel",
        ok=v.action == br.REFUSE and "is EMPTY" in v.lines[0],
    )
    v = br.verdict(_MOD, _REL, br.Inputs(exists=True, has_leaf_dir=True, leaves=("Inl",)))
    _check(
        cases,
        "coverage not consulted refuses rather than assuming",
        ok=v.action == br.REFUSE and "not consulted" in v.lines[0],
    )
    owning = br.Inputs(
        exists=True,
        has_leaf_dir=True,
        leaves=("Inl",),
        occupied=("module", tuple(f"n{i}" for i in range(12))),
    )
    v = br.verdict(_MOD, _REL, owning)
    _check(
        cases,
        "a barrel that still owns names is a REAL MODULE: refused, 10 names listed",
        ok=v.action == br.REFUSE
        and "still OWNS 12" in v.lines[0]
        and sum(ln.startswith("     n") for ln in v.lines) == br.NAME_CAP,
    )
    dead = br.Inputs(exists=True, has_leaf_dir=True, leaves=("Inl", "Inr"), occupied=("barrel", ()))
    v = br.verdict(_MOD, _REL, dead)
    _check(
        cases,
        "zero references and full coverage: delete, both checks named",
        ok=v.action == br.DELETE and len(v.lines) == 2 and "2 leaves" in v.lines[1],
    )  # noqa: PLR2004 - two check lines


def _under_cases(cases: Cases, root: Path) -> None:
    """Pin modules_under over a temp tree, then difference it against the origin from that cwd."""
    agda = root / "agda"
    _check(
        cases,
        "modules_under lists the leaves as dotted modules, sorted",
        ok=ts.modules_under(str(agda), "Substrate.Foundation.Sum")
        == ["Substrate.Foundation.Sum.Inl", "Substrate.Foundation.Sum.Inr"],
    )
    _check(
        cases,
        "modules_under is empty for a prefix with no directory",
        ok=ts.modules_under(str(agda), "Substrate.Nope") == [],
    )
    o = _origin()
    if o is None:
        _check(cases, "differential: origin unavailable, skipped", ok=True)
        return
    before = Path.cwd()
    try:
        os.chdir(root)
        theirs = o._under("Substrate.Foundation.Sum")  # noqa: SLF001 - the origin's spelling
    finally:
        os.chdir(before)
    _check(
        cases,
        "differential: modules_under agrees with the origin's _under",
        ok=theirs == ts.modules_under(str(agda), "Substrate.Foundation.Sum"),
    )


def _mirror(root: Path) -> None:
    """Lay a consumed parent with two leaves."""
    d = root / "agda" / "Substrate" / "Foundation" / "Sum"
    d.mkdir(parents=True)
    for leaf in ("Inr", "Inl"):
        (d / f"{leaf}.agda").write_text("", encoding="utf-8")
    (root / "agda" / "Substrate" / "Foundation" / "Sum.agda").write_text("", encoding="utf-8")


def main() -> int:
    """Run every case; exit 1 if any failed."""
    cases: Cases = []
    _verdict_cases(cases)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _mirror(root)
        _under_cases(cases, root)
    failed = [name for name, ok in cases if not ok]
    for name in failed:
        sys.stdout.write(f"  FAIL  {name}\n")
    sys.stdout.write(f"barrel_retire_selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
