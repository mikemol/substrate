#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.md_write` — the argv contract of a bounded section write.

⚑⚑⚑ THE OPERAND-COUNT CASE IS THE ONE THAT ALREADY FIRED. The first cut read operands as
"every argv entry without a leading `--`", which counts a flag's VALUE as an operand: a correct
invocation carrying `--body-file <path>` presents three, and was refused for having three. The
defect is invisible to a test that only exercises the happy path with no valued flags, and it
made the tool unusable on its first real call. A flag's value is CONSUMED by the flag.

⚑⚑ THE `--exact` CASE PINS THE WHOLE REASON THIS MODULE EXISTS. The capability lives in
`md_spans`, but its only other CLI (`scratch/mdstruct.py`) is frozen under the per-file gate, so
without a route here a heading contained in another is permanently unaddressable. A test that
only checked substring matching would pass on a build where `--exact` was silently dropped.

⚑ INTENT MUST BE STATED, so BOTH the neither-flag and both-flags invocations refuse. A tool that
defaults one way silently does nothing when you meant to write, or silently writes when you meant
to look; only a case that fires on each half keeps that from regressing to a default.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import md_write

# ⚑ THE TITLE CONTAINS THE SUBSECTION'S WHOLE HEADING — the containment shape that makes
# substring matching insufficient rather than merely imprecise.
_FIXTURE = """# Ⓝ31 residue — gates and budgets

intro line

## Residue

existing body
"""


def _doc(d: str) -> Path:
    """Write the fixture document and return its path."""
    path = Path(d) / "doc.md"
    path.write_text(_FIXTURE, encoding="utf-8")
    return path


def _body(d: str) -> Path:
    """Write a body file and return its path."""
    path = Path(d) / "body.md"
    path.write_text("appended line\n", encoding="utf-8")
    return path


def a_valued_flag_is_not_an_operand(out: list[str]) -> int:
    """Check `--body-file <path>` does not count its value toward the operand budget."""
    with tempfile.TemporaryDirectory() as d:
        doc, body = _doc(d), _body(d)
        code = md_write.main([str(doc), "Residue", "--body-file", str(body), "--exact", "--apply"])
        if code:
            out.append(f"selftest: a correct invocation was refused with exit {code}")
            return 1
        if "appended line" not in doc.read_text(encoding="utf-8"):
            out.append("selftest: the write reported success and changed nothing")
            return 1
    return 0


def exact_reaches_a_contained_heading(out: list[str]) -> int:
    """Check `--exact` resolves a heading wholly contained in the document title.

    ⚑ WITHOUT THE FLAG THIS SAME CALL MUST REFUSE — the arm below is its discriminator.
    """
    with tempfile.TemporaryDirectory() as d:
        doc, body = _doc(d), _body(d)
        code = md_write.main(
            [str(doc), "Residue", "--body-file", str(body), "--exact", "--dry-run"]
        )
    if code:
        out.append(f"selftest: --exact failed to resolve a contained heading (exit {code})")
        return 1
    return 0


def without_exact_the_same_heading_refuses(out: list[str]) -> int:
    """Check the DISCRIMINATOR: substring matching really cannot name that section.

    ⚑ IF THIS ARM PASSED WITHOUT `--exact`, the arm above would prove nothing — it would be
    green on a build where the flag was ignored entirely.
    """
    with tempfile.TemporaryDirectory() as d:
        doc, body = _doc(d), _body(d)
        code = md_write.main([str(doc), "Residue", "--body-file", str(body), "--dry-run"])
    if code == 0:
        out.append("selftest: an ambiguous heading resolved without --exact")
        return 1
    return 0


def a_dry_run_writes_nothing(out: list[str]) -> int:
    """Check `--dry-run` leaves the document byte-identical."""
    with tempfile.TemporaryDirectory() as d:
        doc, body = _doc(d), _body(d)
        before = doc.read_text(encoding="utf-8")
        md_write.main([str(doc), "Residue", "--body-file", str(body), "--exact", "--dry-run"])
        if doc.read_text(encoding="utf-8") != before:
            out.append("selftest: a dry run modified the document")
            return 1
    return 0


def intent_must_be_stated(out: list[str]) -> int:
    """Check BOTH neither-flag and both-flags refuse, rather than defaulting either way."""
    with tempfile.TemporaryDirectory() as d:
        doc, body = _doc(d), _body(d)
        base = [str(doc), "Residue", "--body-file", str(body), "--exact"]
        for extra, label in (([], "neither"), (["--apply", "--dry-run"], "both")):
            if md_write.main(base + extra) == 0:
                out.append(f"selftest: {label} of --apply/--dry-run was accepted")
                return 1
    return 0


def a_missing_heading_refuses(out: list[str]) -> int:
    """Check a heading matching nothing exits non-zero rather than writing."""
    with tempfile.TemporaryDirectory() as d:
        doc, body = _doc(d), _body(d)
        before = doc.read_text(encoding="utf-8")
        code = md_write.main([str(doc), "no-such-heading", "--body-file", str(body), "--apply"])
        if code == 0 or doc.read_text(encoding="utf-8") != before:
            out.append("selftest: a missing heading did not refuse cleanly")
            return 1
    return 0


_ARMS = (
    a_valued_flag_is_not_an_operand,
    exact_reaches_a_contained_heading,
    without_exact_the_same_heading_refuses,
    a_dry_run_writes_nothing,
    intent_must_be_stated,
    a_missing_heading_refuses,
)

# ⚑ DERIVED FROM `_ARMS`, NEVER TYPED. A hand-kept count is a second roster beside the real one
# and drifts in both directions; `md_spans_selftest` reported `6/6` while running eight arms.
_CASE_COUNT = len(_ARMS)


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"md-write selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"md-write selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
