# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.glob_portable` — three disagreements, each with its portable twin.

⚑⚑⚑ EVERY REFUSAL ARM NEEDS A PORTABLE ARM BESIDE IT. A check that refused every pattern would
satisfy all three defect cases and be useless, so each is paired with a pattern that must pass —
and the pairs are chosen to differ in exactly the feature under test.

⚑⚑ THE ZERO-SEGMENT ARM IS THE ONE THAT SHIPPED A DEFECT. `**/` cannot match zero segments in
either matcher, so every depth-0 path is dropped and the smaller result reads as a smaller corpus.
Six modules went missing that way, and the arm exists because nothing about the output said so.

⚑ THE CHECK IS A PURE FUNCTION OF THE PATTERN, so these cases need no corpus at all — which is
precisely the property that makes the refusal deterministic rather than a fact about what happens
to be on disk. The listing arms use a temporary tree only because listing is about the filesystem.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import glob_portable as gp


def _segment_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for `**` used inside a segment."""
    out: list[tuple[str, bool]] = []

    found = gp.ambiguity("src**/x.py")
    out.append(
        (f"`**` inside a segment is refused: {found.why() if found else None}", found is not None)
    )
    out.append(
        (
            f"and the reason names the segment: {found.reason if found else ''}",
            found is not None and "src**" in found.reason,
        )
    )

    # ⚑ THE PORTABLE TWIN. A WHOLE-segment `**` is exactly what both matchers agree on.
    out.append(
        (f"a whole-segment `**` is fine: {gp.ambiguity('src/**')}", gp.ambiguity("src/**") is None)
    )
    return out


def _zero_segment_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the drop that looked like a smaller corpus.

    ⚑⚑ THIS IS THE SHIPPED DEFECT. `src/**/x.py` matches nothing at depth zero, so `src/x.py` is
    dropped — silently, because a shorter list reads as a smaller tree rather than a broken query.
    """
    out: list[tuple[str, bool]] = []

    found = gp.ambiguity("src/**/deep.py")
    out.append(
        (f"a non-final `**` is refused: {found.why() if found else None}", found is not None)
    )
    out.append(
        (
            f"and the reason names the zero-segment drop: {found.reason if found else ''}",
            found is not None and "ZERO segments" in found.reason,
        )
    )
    out.append(
        (
            f"and the remedy is depth-agnostic: {found.remedy if found else ''}",
            found is not None and "src/**" in found.remedy,
        )
    )

    # ⚑ THE PORTABLE TWIN — trailing `**`, which both matchers read the same way.
    out.append(
        (f"a trailing `**` is fine: {gp.ambiguity('src/**')}", gp.ambiguity("src/**") is None)
    )
    return out


def _crossing_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for a bare wildcard that crosses `/` under one matcher."""
    out: list[tuple[str, bool]] = []

    found = gp.ambiguity("src/*.py")
    out.append(
        (
            f"a multi-segment bare star is refused: {found.why() if found else None}",
            found is not None,
        )
    )
    out.append(
        (
            f"and the reason names the crossing: {found.reason if found else ''}",
            found is not None and "cross" in found.reason,
        )
    )

    # ⚑⚑ THE PORTABLE TWIN, AND IT IS THE SUBTLE ONE. A SINGLE-segment pattern has no directory
    # context to cross into, so the disagreement cannot arise — refusing it would make the check
    # fire on patterns that are already safe.
    out.append(
        (f"a single-segment star is fine: {gp.ambiguity('*.py')}", gp.ambiguity("*.py") is None)
    )
    out.append(
        (
            f"and a literal multi-segment path is fine: {gp.ambiguity('src/x.py')}",
            gp.ambiguity("src/x.py") is None,
        )
    )
    return out


def _order_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the reporting order when a pattern has two defects.

    ⚑ A PATTERN WITH BOTH IS FIXED AT THE SEGMENT END. Reporting the zero-segment defect first
    would send a reader to the wrong part of the pattern, and they would fix the half that was not
    blocking them.
    """
    out: list[tuple[str, bool]] = []
    found = gp.ambiguity("src**/**/x.py")

    out.append(
        (
            f"the segment defect is reported first: {found.reason if found else ''}",
            found is not None and "WHOLE segment" in found.reason,
        )
    )
    return out


def _listing_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the listing itself, against a real tree."""
    out: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "src").mkdir()
        (root / "src" / "deep").mkdir()
        (root / "src" / "shallow.py").write_text("x", encoding="utf-8")
        (root / "src" / "deep" / "buried.py").write_text("y", encoding="utf-8")

        found = gp.listdir("src/**", root)
        out.append(
            (
                f"a portable pattern lists both depths: {found}",
                "src/shallow.py" in found and "src/deep/buried.py" in found,
            )
        )
        out.append((f"and the result is sorted: {found}", found == sorted(found)))
        out.append(
            (
                f"and the paths are root-relative: {found[0]}",
                not any(p.startswith("/") for p in found),
            )
        )

        # ⚑⚑ THE REFUSAL FIRES ON THE WORKING TREE TOO, where the pattern happens to be exact.
        # A check that only fired on the lossy source would let the trap be armed by a caller who
        # never touched it — which is how the drop shipped.
        try:
            gp.listdir("src/*.py", root)
        except gp.AmbiguousPatternError as exc:
            out.append((f"an ambiguous pattern is refused on disk: {str(exc)[:40]}", True))
        else:
            out.append(("an ambiguous pattern is refused on disk", False))

        # ⚑ AND OPTING OUT LISTS IT — the escape works, and it is a caller ESTABLISHING one source
        # rather than making the pattern portable.
        lax = gp.listdir("src/*.py", root, strict=False)
        out.append((f"and strict=False lists it anyway: {lax}", lax == ["src/shallow.py"]))
        # ⚑⚑ AND THE LAX LISTING IS THE LOSSY ONE — it finds the shallow file and NOT the buried
        # one, which is the disagreement the refusal was warning about, made visible.
        out.append(
            (f"and the lax listing drops the deeper file: {lax}", "src/deep/buried.py" not in lax)
        )

        empty = gp.listdir("nothing/**", root)
        out.append((f"a pattern matching nothing yields nothing: {empty}", empty == []))
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _segment_cases()
        + _zero_segment_cases()
        + _crossing_cases()
        + _order_cases()
        + _listing_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"glob-portable selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
