#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `agda_tree_state` - the stamp and the leaf census over a temporary tree.

THE TREE IS BUILT, NOT ASSUMED: three sources, one carrying the split marker in its head, one
carrying it only past the head window (so it must NOT count), a `.agdai` under `_build` that
must be invisible to both readers, and mtimes set explicitly so the newest is known. The
differential loads `scratch/split_census.py` by path and runs its `tree_stamp(root)` and
`leaves(root)` over the same tree; both take a root, so this is a real comparison. Skipped,
not failed, if the origin will not import here.

THE MTIME READER IS A PARAMETER, and one case hands the stamp a dict reader to show the
instrument is swappable - the property the bazel intake asked for across a repo boundary.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
from pathlib import Path
from typing import Protocol, cast

from substrate import agda_tree_state as ts

_ORIGIN = Path(__file__).resolve().parent.parent / "scratch" / "split_census.py"
_T0, _T1, _T2 = 1_000_000_000.0, 1_000_000_100.0, 1_000_000_200.0
_SOURCES = 3

Cases = list[tuple[str, bool]]


class _Origin(Protocol):
    def tree_stamp(self, root: str = "agda") -> str: ...
    def leaves(self, root: str = "agda") -> list[str]: ...


def _origin() -> _Origin | None:
    """Load `split_census.py` by PATH, or None when it is gone or will not import here."""
    if not _ORIGIN.exists():
        return None
    spec = importlib.util.spec_from_file_location("_split_census_origin_ts", _ORIGIN)
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


def _mirror(root: Path) -> None:
    """Lay the fixture tree: a leaf, a non-leaf, a late-marker file, and a _build artifact."""
    src = root / "Substrate"
    (src / "Deep").mkdir(parents=True)
    leaf = src / "Leaf.agda"
    leaf.write_text(f"-- {ts.MARKER}\nmodule Substrate.Leaf where\n", encoding="utf-8")
    plain = src / "Deep" / "Plain.agda"
    plain.write_text("module Substrate.Deep.Plain where\n", encoding="utf-8")
    late = src / "Late.agda"
    late.write_text("-- x\n" * (ts.HEAD_BYTES // 5 + 1) + f"-- {ts.MARKER}\n", encoding="utf-8")
    build = root / "_build" / "h" / "agda" / "Substrate"
    build.mkdir(parents=True)
    (build / "Leaf.agdai").write_text("", encoding="utf-8")
    (build / "Ghost.agda").write_text(f"-- {ts.MARKER}\n", encoding="utf-8")
    os.utime(leaf, (_T0, _T0))
    os.utime(plain, (_T2, _T2))
    os.utime(late, (_T1, _T1))


def _stamp_cases(cases: Cases, root: str) -> None:
    """Pin the stamp's count, its newest mtime, and the swappable reader."""
    _check(
        cases,
        "the stamp counts the sources outside _build and names the newest mtime",
        ok=ts.tree_stamp(root) == f"{_SOURCES}:{_T2:.0f}",
    )
    fake = {str(Path(root) / "Substrate" / "Leaf.agda"): 5.0}
    _check(
        cases,
        "the mtime reader is a parameter: unreadable files are skipped, not zeroed",
        ok=ts.tree_stamp(root, fake.get) == f"{_SOURCES}:5",
    )
    _check(
        cases,
        "an empty tree stamps as 0:0",
        ok=ts.tree_stamp(str(Path(root) / "Substrate" / "Deep" / "nowhere")) == "0:0",
    )


def _leaf_cases(cases: Cases, root: str) -> None:
    """Pin the leaf census: marker in the head only, _build invisible."""
    found = ts.leaves(root)
    _check(
        cases,
        "a file with the marker in its head is a leaf",
        ok=[Path(p).name for p in found] == ["Leaf.agda"],
    )
    _check(
        cases,
        "a marker past the head window does not count",
        ok=all(not p.endswith("Late.agda") for p in found),
    )
    _check(
        cases, "a marked .agda under _build is invisible", ok=all("_build" not in p for p in found)
    )


def _differential_cases(cases: Cases, root: str) -> None:
    """Assert both readers agree with the origin over the same tree, or skip."""
    o = _origin()
    if o is None:
        _check(cases, "differential: origin unavailable, skipped", ok=True)
        return
    _check(
        cases,
        "differential: tree_stamp agrees with the origin",
        ok=ts.tree_stamp(root) == o.tree_stamp(root),
    )
    _check(
        cases,
        "differential: leaves agrees with the origin",
        ok=sorted(map(str, ts.leaves(root))) == sorted(map(str, o.leaves(root))),
    )


def main() -> int:
    """Run every case; exit 1 if any failed."""
    cases: Cases = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "agda"
        _mirror(root)
        _stamp_cases(cases, str(root))
        _leaf_cases(cases, str(root))
        _differential_cases(cases, str(root))
    failed = [name for name, ok in cases if not ok]
    for name in failed:
        sys.stdout.write(f"  FAIL  {name}\n")
    sys.stdout.write(f"agda_tree_state_selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
