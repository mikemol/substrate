#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `agda_blame` - the three verdicts, the clash shape, and a differential by path.

THE FIXTURE IS VERBATIM ERROR TEXT, shaped as agda prints it: an absolute path, a line and
column range, `error: [Kind]`, then the message. The dependency arm reproduces the recorded
R9 case (a leaf under test whose failure cites `F2/Vector.agda:167`); the own arm cites the
leaf itself; the no-file arm has `error` in it but names nothing, which is attributed to the
leaf conservatively. Both directions of the clean verdict are cased - empty output, and
non-empty output with neither a citation nor the word error - because a reader that returned
`clean` for everything would pass one and not the other.

THE DIFFERENTIAL LOADS `scratch/split_pipeline.py` BY PATH. It inserts its own directory on
`sys.path` at import and reaches scratch siblings and `agda_defs`; if that import fails on this
host the arms are SKIPPED, not failed - the origin's importability is the origin's business.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Protocol, cast

from substrate import agda_blame as ab

_ORIGIN = Path(__file__).resolve().parent.parent / "scratch" / "split_pipeline.py"
_LEAF = "agda/Substrate/Foundation/Fin/Op2.agda"

_DEP = (
    "/home/x/substrate/agda/Substrate/Foundation/F2/Vector.agda:167,3-9: error: "
    "[UnsolvedMetaVariables]\nUnsolved metas at the following locations:\n"
)
_OWN = (
    f"/home/x/substrate/{_LEAF}:12,1-8: error: [ClashingDefinition]\n"
    "Multiple definitions of _<_. Previous definition at\n"
    "  /home/x/substrate/agda/Substrate/Foundation/Nat/Lt.agda:5,1-4\n"
)
_NOFILE = "Checking Substrate.Foundation.Fin.Op2\nerror: something went wrong\n"
_QUIET = "Checking Substrate.Foundation.Fin.Op2\n"
_CLASH = (
    f"{_LEAF}:12,1-8: error: [ClashingDefinition]\n"
    "  Multiple definitions of _<_. Previous definition at\n"
    "  agda/Substrate/Foundation/Nat/Lt.agda:5,1-4\n"
)
_FIXTURE = {
    "dep": _DEP,
    "own": _OWN,
    "nofile": _NOFILE,
    "quiet": _QUIET,
    "empty": "",
    "clash": _CLASH,
}

Cases = list[tuple[str, bool]]


class _Origin(Protocol):
    def blame(self, leaf_path: str, out: str) -> tuple[str, str | None]: ...
    def _parse_clash(self, out: str) -> tuple[str, str, str] | None: ...


def _origin() -> _Origin | None:
    """Load `split_pipeline.py` by PATH, or None when it is gone or will not import here."""
    if not _ORIGIN.exists():
        return None
    spec = importlib.util.spec_from_file_location("_split_pipeline_origin", _ORIGIN)
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


def _blame_cases(cases: Cases) -> None:
    """Pin the three verdicts over the fixture."""
    kind, cited = ab.blame(_LEAF, _DEP)
    _check(
        cases,
        "a failure citing another file is a DEPENDENCY, and the file is returned",
        ok=kind == "dependency" and cited is not None and cited.endswith("F2/Vector.agda"),
    )
    kind, cited = ab.blame(_LEAF, _OWN)
    _check(
        cases,
        "a failure citing the leaf itself is OWN",
        ok=kind == "own" and cited is not None and cited.endswith(_LEAF),
    )
    _check(
        cases,
        "a leaf path with a ./ prefix still matches its citation",
        ok=ab.blame("./" + _LEAF, _OWN)[0] == "own",
    )
    _check(
        cases,
        "an error line citing no file is attributed to the leaf",
        ok=ab.blame(_LEAF, _NOFILE) == ("own", _LEAF),
    )
    _check(
        cases,
        "output with no citation and no error is clean",
        ok=ab.blame(_LEAF, _QUIET) == ("clean", None),
    )
    _check(cases, "empty output is clean", ok=ab.blame(_LEAF, "") == ("clean", None))


def _clash_cases(cases: Cases) -> None:
    """Pin the ClashingDefinition shape and that other errors read as None."""
    _check(
        cases,
        "a ClashingDefinition yields (consumer, name, previous)",
        ok=ab.parse_clash(_CLASH) == (_LEAF, "_<_", "agda/Substrate/Foundation/Nat/Lt.agda"),
    )
    _check(cases, "a non-clash error is None", ok=ab.parse_clash(_DEP) is None)
    _check(cases, "empty output is None", ok=ab.parse_clash("") is None)


def _differential_cases(cases: Cases) -> None:
    """Assert both readers agree with the origin over every fixture text, or skip."""
    o = _origin()
    if o is None:
        _check(cases, "differential: origin unavailable, skipped", ok=True)
        return
    for name, text in _FIXTURE.items():
        _check(
            cases, f"differential blame {name}", ok=ab.blame(_LEAF, text) == o.blame(_LEAF, text)
        )
        _check(
            cases,
            f"differential parse_clash {name}",
            ok=ab.parse_clash(text) == o._parse_clash(text),
        )  # noqa: SLF001 - the origin's spelling


def main() -> int:
    """Run every case; exit 1 if any failed."""
    cases: Cases = []
    _blame_cases(cases)
    _clash_cases(cases)
    _differential_cases(cases)
    failed = [name for name, ok in cases if not ok]
    for name in failed:
        sys.stdout.write(f"  FAIL  {name}\n")
    sys.stdout.write(f"agda_blame_selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
