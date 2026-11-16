#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.suite_currency` — the verdicts, and the boundaries they print.

⚑⚑ THE LOAD-BEARING ARMS ARE THE VERDICT LINES, NOT THE EXIT CODES. Reading a program's status
via `echo $?` is the reasoning-not-codified shape: the code is for the hook, the SENTENCE is for
the reader — and a verdict that exits 1 while printing nothing actionable sends a reader hunting.

⚑ AND THE KIND MUST REACH THAT SENTENCE. "FAILED" sends a reader looking for a defect; `unfit`
sends them to the memory lease and `vacuous` to a suite that asserted nothing. Three different
next actions, one word until the kind became a column — and this is the projection an operator
actually reads.

⚑⚑ THE REACH READ'S BOUNDARY ARM IS THE OTHER HALF. Its two columns count DIFFERENT things and
their absolute values do not match, so printing them side by side INVITES the misreading. The
note has to be in the output, at the point of the misreading — a caveat in a docstring is the
shape that lets a wrong reading get banked.

⚑ AN ABSENT BASELINE IS NAMED, NOT SILENTLY EMPTY. ABSENT and EMPTY are opposite, and this repo
has measured a gate reading one as the other.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import suite_currency, suite_ledger


def _suites(root: Path, bodies: dict[str, str]) -> list[tuple[str, str]]:
    """Write fixture suites and return the `(label, path)` roster."""
    out: list[tuple[str, str]] = []
    for name, body in bodies.items():
        path = root / name
        path.write_text(body, encoding="utf-8")
        out.append((name, str(path)))
    return sorted(out)


def _ledger(suites: list[tuple[str, str]], kinds: dict[str, str], broken: set[str]) -> str:
    """Render a ledger for one run over these suites."""
    return suite_ledger.render(suites, (1, 1), kinds, broken)


def _text(lines: tuple[str, ...]) -> str:
    """Render a verdict's lines the way a reader sees them."""
    return "\n".join(lines)


def a_current_tree_says_so_and_exits_zero(out: list[str]) -> int:
    """Check an unedited tree reads CURRENT, in words and in the exit code."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        suites = _suites(Path(tmp), {"a.py": "x = 1\n"})
        got = suite_currency.currency(_ledger(suites, {"a.py": "ok"}, set()), suites)
        if got.code != 0 or "VERDICT: CURRENT" not in _text(got.lines):
            bad += 1
            out.append(f"selftest: a clean tree read {got.code} / {_text(got.lines)!r}")
    return bad


def an_edited_tree_says_stale_and_exits_one(out: list[str]) -> int:
    """Check an edited suite makes the verdict STALE, with the re-run instruction."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        suites = _suites(root, {"a.py": "x = 1\n"})
        body = _ledger(suites, {"a.py": "ok"}, set())
        (root / "a.py").write_text("x = 2\n", encoding="utf-8")
        got = suite_currency.currency(body, suites)
        text = _text(got.lines)
        if got.code != 1 or "VERDICT: STALE" not in text or "re-run" not in text:
            bad += 1
            out.append(f"selftest: an edited tree read {got.code} / {text!r}")
    return bad


def the_kind_reaches_the_verdict(out: list[str]) -> int:
    """Check a broken suite's KIND is printed, not collapsed to one word.

    ⚑ `unfit` SENDS A READER TO THE LEASE; a bare failure sends them to the code.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        suites = _suites(Path(tmp), {"a.py": "x = 1\n"})
        got = suite_currency.currency(_ledger(suites, {"a.py": "unfit"}, {"a.py"}), suites)
        text = _text(got.lines)
        if got.code != 1 or "UNFIT" not in text:
            bad += 1
            out.append(f"selftest: a lease-killed suite read {got.code} / {text!r}")
    return bad


def a_lease_kill_earns_its_hint(out: list[str]) -> int:
    """Check `unfit` is spelled out as NOT a test failure."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        suites = _suites(Path(tmp), {"a.py": "x = 1\n"})
        got = suite_currency.currency(_ledger(suites, {"a.py": "unfit"}, {"a.py"}), suites)
        if "LEASE finding" not in _text(got.lines):
            bad += 1
            out.append("selftest: an unfit verdict printed no lease hint")
    return bad


def a_removed_suite_says_gone(out: list[str]) -> int:
    """Check a recorded suite that is no longer one is named GONE, a state of its own."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        both = _suites(root, {"a.py": "x = 1\n", "b.py": "y = 1\n"})
        body = _ledger(both, {"a.py": "ok", "b.py": "ok"}, set())
        got = suite_currency.currency(body, [row for row in both if row[0] == "a.py"])
        if "GONE" not in _text(got.lines):
            bad += 1
            out.append(f"selftest: a removed suite produced no GONE row — {_text(got.lines)!r}")
    return bad


def the_reach_read_prints_its_lens_boundary(out: list[str]) -> int:
    """Check the two-column note is in the OUTPUT, not only in a docstring.

    ⚑ THE COLUMNS COUNT DIFFERENT THINGS. Printing them side by side invites the misreading,
    so the boundary is stated where the misreading happens.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        suites = _suites(root, {"a.py": "def _selftest():\n    check(1, 1)\n"})
        got = suite_currency.reach(suites, str(root / "absent.tsv"), "absent.tsv")
        text = _text(got.lines)
        if "different questions" not in text or "DELTAS" not in text:
            bad += 1
            out.append(f"selftest: the reach read stated no lens boundary — {text!r}")
    return bad


def an_absent_reach_baseline_is_named(out: list[str]) -> int:
    """Check no baseline reads as ABSENT rather than as an empty census.

    ⚑ ABSENT AND EMPTY ARE OPPOSITE, and this repo has measured a gate reading one as the
    other — reporting zero while asserting PASS over unrecorded findings.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        suites = _suites(root, {"a.py": "x = 1\n"})
        got = suite_currency.reach(suites, str(root / "absent.tsv"), "absent.tsv")
        if "no reach baseline" not in _text(got.lines):
            bad += 1
            out.append(f"selftest: an absent baseline was not named — {_text(got.lines)!r}")
    return bad


def the_reach_read_never_refuses(out: list[str]) -> int:
    """Check the reach read exits 0 — it is a DIAGNOSTIC, not a gate.

    ⚑ IT IS THE READ A RECORDER REACHES FOR WHEN THE GATE HAS ALREADY REFUSED. A diagnostic
    that also refuses gives a reader two failures to disentangle instead of one to read.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        suites = _suites(root, {"a.py": "x = 1\n"})
        got = suite_currency.reach(suites, str(root / "absent.tsv"), "absent.tsv")
        if got.code != 0:
            bad += 1
            out.append(f"selftest: the reach read exited {got.code}, not 0")
    return bad


def the_never_run_message_names_the_command(out: list[str]) -> int:
    """Check the no-record message tells a reader what to run."""
    bad = 0
    if "run_selftests" not in suite_currency.NEVER_RUN:
        bad += 1
        out.append(
            f"selftest: the never-run message names no command — {suite_currency.NEVER_RUN!r}"
        )
    return bad


_ARMS = (
    a_current_tree_says_so_and_exits_zero,
    an_edited_tree_says_stale_and_exits_one,
    the_kind_reaches_the_verdict,
    a_lease_kill_earns_its_hint,
    a_removed_suite_says_gone,
    the_reach_read_prints_its_lens_boundary,
    an_absent_reach_baseline_is_named,
    the_reach_read_never_refuses,
    the_never_run_message_names_the_command,
)

_CASE_COUNT = len(_ARMS)


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"suite-currency selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"suite-currency selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO DISCOVERY SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
