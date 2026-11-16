#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `rewire_ready` - the four measured targets, the orderings, and the compile gate.

THE FIXTURE IS THE ORIGIN'S OWN MEASUREMENT (2026-08-17): four targets that shared one remedy
string and needed four different actions. Each is a manifest text shaped as `rewire_to_leaves
--manifest --dry-run` prints it, and the case asserts the verdict's FIRST line - the one a
reader acts on. The orderings are cased as positions: the arity verdict precedes the compile
result, and a surviving `public` re-export precedes it too.

NO DIFFERENTIAL AGAINST THE ORIGIN'S `ready_verdict`: it runs a subprocess and isolate-compiles
agda, so a by-path call would be a build, not a comparison. The pure piece it exposes is the
manifest regex, and `parse_manifest` is pinned on the same texts the origin was measured on.
"""

from __future__ import annotations

import sys

from substrate import rewire_ready as rr

_VEC = "  12 names / 7 leaves -> WOULD rewire 42 importers\n"
_NAT = (
    "  9 names / 13 leaves -> WOULD rewire 3 importers\n"
    "  ⚠ UNMAPPED in agda/Substrate/Foundation/Fin/Op2.agda: ['suc-injective']\n"
)
_GUNIT = (
    "  4 names / 2 leaves -> WOULD rewire 0 importers\n"
    "  ⚠ UNMAPPED in agda/A.agda: ['x']\n  ⚠ UNMAPPED in agda/B.agda: ['y', 'z']\n"
)
_F2 = "  0 names / 0 leaves -> WOULD rewire 0 importers\n"
_GARBLED = "rewire_to_leaves: refused\n"
_REEX: rr.Reexport = (
    "Substrate.WitnessTower.FaceSetStabilizes",
    75,
    "Substrate.WitnessTower.SimplicialBoundary",
    "open import …SimplicialBoundary public using (delAt)",
    "open-applied",
)
_ROOT = "/home/x/substrate"
_ROWS: tuple[rr.LeafRow, ...] = (
    (f"{_ROOT}/agda/A.agda", "clean", None),
    (f"{_ROOT}/agda/B.agda", "own", f"{_ROOT}/agda/B.agda"),
)
_VEC_LEAVES = 7
_VEC_IMPORTERS = 42
_NAT_IMPORTERS = 3
_GUNIT_UNMAPPED = 2
_OVER_CAP = 369

Cases = list[tuple[str, bool]]


def _check(cases: Cases, name: str, *, ok: bool) -> None:
    """Append one verdict to the run."""
    cases.append((name, ok))


def _lines(leaves: int, txt: str, **kw: object) -> list[str]:
    """Render a verdict over a manifest text with the given extra inputs."""
    return rr.verdict(rr.Inputs(leaves, rr.parse_manifest(txt), **kw))  # type: ignore[arg-type]


def _manifest_cases(cases: Cases) -> None:
    """Pin parse_manifest over the four measured texts and a garbled one."""
    _check(
        cases,
        "Vec.Properties: 42 importers, nothing unmapped",
        ok=rr.parse_manifest(_VEC) == rr.Manifest(_VEC_IMPORTERS, ()),
    )
    nat = rr.parse_manifest(_NAT)
    _check(
        cases,
        "Foundation.Nat: 3 importers with one UNMAPPED site",
        ok=nat.importers == _NAT_IMPORTERS
        and len(nat.unmapped) == 1
        and nat.unmapped[0][1] == "['suc-injective']",
    )
    want = rr.Manifest(0, (("agda/A.agda", "['x']"), ("agda/B.agda", "['y', 'z']")))
    _check(
        cases,
        "GUnit.Base: 0 importers with two UNMAPPED sites",
        ok=rr.parse_manifest(_GUNIT) == want,
    )
    _check(cases, "Algebra.F2: 0 of 0", ok=rr.parse_manifest(_F2).importers == 0)
    _check(
        cases,
        "a garbled manifest reads as an unknown reach, not zero",
        ok=rr.parse_manifest(_GARBLED).importers is None,
    )


def _verdict_cases(cases: Cases) -> None:
    """Pin the first line of each of the four targets' verdicts, and the no-leaf-set refusal."""
    _check(
        cases,
        "Vec.Properties reads as a rewire of 42",
        ok=_lines(_VEC_LEAVES, _VEC)[0] == "ready: → would rewire 42 importer(s)",
    )
    lines = _lines(13, _NAT)
    _check(
        cases,
        "Foundation.Nat names its UNMAPPED site and says those importers are untouched",
        ok=any("UNMAPPED ['suc-injective']" in ln for ln in lines)
        and any("left UNTOUCHED" in ln for ln in lines),
    )
    lines = _lines(2, _GUNIT)
    _check(
        cases,
        "GUnit.Base is a NO-OP that names both UNMAPPED sites",
        ok=lines[0].startswith("ready: ✗ NO-OP")
        and sum("UNMAPPED [" in ln for ln in lines) == _GUNIT_UNMAPPED,
    )
    _check(
        cases,
        "Algebra.F2 with no leaf set does not apply",
        ok=_lines(0, _F2)[0].startswith("ready: ✗ NO LEAF SET"),
    )
    _check(
        cases,
        "an unreadable reach is reported as a question, not a verdict",
        ok=_lines(3, _GARBLED)[0].startswith("ready: ?"),
    )


def _ordering_cases(cases: Cases) -> None:
    """Pin the two load-bearing orderings and the compile gate."""
    lines = _lines(_VEC_LEAVES, _VEC, reexports=(_REEX,), compiled=(False, _ROWS), root=_ROOT)
    i_reex = next(i for i, ln in enumerate(lines) if "re-export(s) TARGET" in ln)
    i_comp = next(i for i, ln in enumerate(lines) if ln.startswith("    leaves:"))
    _check(
        cases,
        "arity first, re-exports before the compile result",
        ok=lines[0].startswith("ready: →") and i_reex < i_comp,
    )
    _check(
        cases,
        "the re-export line names the site and its kind",
        ok=any("FaceSetStabilizes:75  [open-applied]" in ln for ln in lines),
    )
    _check(
        cases,
        "a NOT-clean compile names the bad leaf relative to the root",
        ok=any(ln.strip() == "own          agda/B.agda" for ln in lines)
        and "1 of 2 NOT clean" in lines[i_comp],
    )
    _check(
        cases,
        "a clean compile reports the row count",
        ok=_lines(_VEC_LEAVES, _VEC, compiled=(True, _ROWS))[-1] == "    leaves: ✓ 2 compile",
    )
    over = rr.Inputs(_OVER_CAP, rr.parse_manifest(_VEC), compiled=(True, _ROWS))
    _check(
        cases,
        "over the cap the verdict SAYS it did not compile-check, and ignores any rows",
        ok=rr.verdict(over)[-1].startswith("    leaves: 369 > cap 24")
        and not rr.needs_compile(over),
    )
    _check(
        cases,
        "needs_compile: a NO-OP never asks for the compile",
        ok=not rr.needs_compile(rr.Inputs(2, rr.parse_manifest(_GUNIT))),
    )
    _check(
        cases,
        "needs_compile: an in-cap rewire with reach does",
        ok=rr.needs_compile(rr.Inputs(_VEC_LEAVES, rr.parse_manifest(_VEC))),
    )
    _check(
        cases,
        "a NO-OP verdict stops before the compile section even with rows supplied",
        ok=not any(
            ln.startswith("    leaves:") for ln in _lines(2, _GUNIT, compiled=(True, _ROWS))
        ),
    )


def main() -> int:
    """Run every case; exit 1 if any failed."""
    cases: Cases = []
    _manifest_cases(cases)
    _verdict_cases(cases)
    _ordering_cases(cases)
    failed = [name for name, ok in cases if not ok]
    for name in failed:
        sys.stdout.write(f"  FAIL  {name}\n")
    sys.stdout.write(f"rewire_ready_selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
