#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `agda_error_class` - every branch, the trace, the accessors, and a differential.

THE LEAF PROBE IS THE FIXTURE'S KNOB. `leaves_of` is a dict lookup here, so the consumed-parent
branch is cased in every direction without a tree: one missing module with leaves; two where
only the SECOND has leaves (the origin's finditer lesson - a search-first reader would have
verdicted on the first); none with leaves. The production probe is cased separately over a
temporary tree so `leaves_on_disk` is a case, not an assumption.

THE DIFFERENTIAL LOADS `scratch/split_census.py` BY PATH and runs its `_classify` with its
`AG` pointed at the same temporary tree, so both readers see one filesystem; every fixture text
is compared on all three fields. Skipped, not failed, if the origin will not import here.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path
from typing import Protocol, cast

from substrate import agda_error_class as ec

_ORIGIN = Path(__file__).resolve().parent.parent / "scratch" / "split_census.py"

_FNF = (
    "Checking Substrate.X\nagda/Substrate/X.agda:3,1-40: error: [FileNotFound]\n"
    "Failed to find source of module {mod} in any of the following locations:\n"
)
_ONE = _FNF.format(mod="Substrate.Foundation.Vec")
_TWO = _FNF.format(mod="Substrate.Gone") + _FNF.format(mod="Substrate.Foundation.Vec")
_NONE = _FNF.format(mod="Substrate.Gone")
_NIS = (
    "Checking Substrate.Y\nagda/Substrate/Y.agda:9,5-8: error: [NotInScope]\n"
    "Not in scope:\n  foo at agda/Substrate/Y.agda:9,5-8\n"
)
_BARE = "Checking Substrate.Z\nerror: something the compiler did not bracket\n"
_FIXTURE = {
    "one": _ONE,
    "two": _TWO,
    "none": _NONE,
    "nis": _NIS,
    "bare": _BARE,
    "empty": "",
    "quiet": "Checking Substrate.Q\n",
}
# Which fixture modules have leaf directories, mirrored onto disk for the production probe.
_LEAVES = {"Substrate.Foundation.Vec": 3}

Cases = list[tuple[str, bool]]


def _leaves_of(module: str) -> int:
    """Return the fixture's leaf count for a module."""
    return _LEAVES.get(module, 0)


class _Origin(Protocol):
    AG: str

    def _classify(
        self, path: str, txt: str, trace: list[str] | None = None
    ) -> tuple[str, str, str | None]: ...


def _origin() -> _Origin | None:
    """Load `split_census.py` by PATH, or None when it is gone or will not import here."""
    if not _ORIGIN.exists():
        return None
    spec = importlib.util.spec_from_file_location("_split_census_origin", _ORIGIN)
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


def _branch_cases(cases: Cases) -> None:
    """Pin every branch of classify."""
    _check(cases, "empty text is clean", ok=ec.classify("", _leaves_of) == ("clean", "", None))
    _check(
        cases,
        "text with no error line is bare other with empty detail",
        ok=ec.classify("Checking Substrate.Q\n", _leaves_of) == ("other", "", None),
    )
    kind, mod, remedy = ec.classify(_ONE, _leaves_of)
    _check(
        cases,
        "a missing module WITH leaves is a consumed parent with the rewire remedy",
        ok=kind == "file-not-found"
        and mod == "Substrate.Foundation.Vec"
        and remedy is not None
        and "--rewire-only --apply" in remedy,
    )
    _check(
        cases,
        "two missing modules: the one WITH leaves wins even when reported second",
        ok=ec.classify(_TWO, _leaves_of)[1] == "Substrate.Foundation.Vec",
    )
    kind, mod, remedy = ec.classify(_NONE, _leaves_of)
    _check(
        cases,
        "a missing module with NO leaves is file-not-found, read-the-error remedy",
        ok=kind == "file-not-found"
        and mod == "Substrate.Gone"
        and remedy is not None
        and remedy.startswith("no leaf directory"),
    )
    kind, detail, remedy = ec.classify(_NIS, _leaves_of)
    _check(
        cases,
        "a bracketed kind is other:<Kind> with the first error line as detail",
        ok=kind == "other:NotInScope"
        and detail.startswith("agda/Substrate/Y.agda:9")
        and remedy is None,
    )
    _check(
        cases,
        "the refined class carries its measured remedy; the bare kind does not",
        ok="other:NotInScope:resolvable" in ec.CLASS_REMEDY
        and "other:NotInScope" not in ec.CLASS_REMEDY,
    )
    _check(
        cases, "an unbracketed error is bare other", ok=ec.classify(_BARE, _leaves_of)[0] == "other"
    )


def _trace_cases(cases: Cases) -> None:
    """Pin that the predicate explains itself when asked, and is silent when not."""
    trace: list[str] = []
    ec.classify(_TWO, _leaves_of, trace)
    _check(
        cases,
        "the trace records the match count, each module's leaves, and the decision",
        ok=trace[0] == "[FileNotFound] matches: 2"
        and any("leaves=3" in t for t in trace)
        and trace[-1].startswith("→ consumed-parent"),
    )
    _check(
        cases,
        "no trace list, no side effect",
        ok=ec.classify(_NIS, _leaves_of) == ec.classify(_NIS, _leaves_of, None),
    )


def _accessor_cases(cases: Cases) -> None:
    """Pin other_kind and is_other across the prefix partition."""
    _check(
        cases,
        "other_kind reads the class off a prefixed kind",
        ok=ec.other_kind("other:NotInScope:resolvable") == "NotInScope:resolvable",
    )
    _check(
        cases,
        "other_kind is None for bare other and for non-other kinds",
        ok=ec.other_kind("other") is None and ec.other_kind("file-not-found") is None,
    )
    _check(
        cases,
        "is_other holds for bare and prefixed, not for file-not-found or clean",
        ok=ec.is_other("other")
        and ec.is_other("other:X")
        and not ec.is_other("file-not-found")
        and not ec.is_other("clean"),
    )


def _disk_cases(cases: Cases, tree: Path) -> None:
    """Pin the production probe over a temporary tree mirroring the fixture."""
    probe = ec.leaves_on_disk(tree)
    _check(
        cases,
        "leaves_on_disk counts the .agda files where the module would live",
        ok=probe("Substrate.Foundation.Vec") == _LEAVES["Substrate.Foundation.Vec"],
    )
    _check(
        cases, "leaves_on_disk is 0 for a module with no directory", ok=probe("Substrate.Gone") == 0
    )


def _differential_cases(cases: Cases, tree: Path) -> None:
    """Assert classify agrees with the origin's _classify over one filesystem, or skip."""
    o = _origin()
    if o is None:
        _check(cases, "differential: origin unavailable, skipped", ok=True)
        return
    o.AG = str(tree / ec.AGDA_DIR)
    probe = ec.leaves_on_disk(tree)
    for name, text in _FIXTURE.items():
        _check(
            cases,
            f"differential {name}",
            ok=ec.classify(text, probe) == o._classify("x.agda", text),
        )  # noqa: SLF001 - the origin's spelling


def _mirror(tree: Path) -> None:
    """Lay the fixture's leaf directories on disk."""
    for mod, n in _LEAVES.items():
        d = tree / ec.AGDA_DIR / mod.replace(".", "/")
        d.mkdir(parents=True)
        for i in range(n):
            (d / f"Leaf{i}.agda").write_text("", encoding="utf-8")


def main() -> int:
    """Run every case; exit 1 if any failed."""
    cases: Cases = []
    _branch_cases(cases)
    _trace_cases(cases)
    _accessor_cases(cases)
    with tempfile.TemporaryDirectory() as tmp:
        tree = Path(tmp)
        _mirror(tree)
        _disk_cases(cases, tree)
        _differential_cases(cases, tree)
    failed = [name for name, ok in cases if not ok]
    for name in failed:
        sys.stdout.write(f"  FAIL  {name}\n")
    sys.stdout.write(f"agda_error_class_selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
