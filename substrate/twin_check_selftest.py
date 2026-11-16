#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.twin_check` — the guard standing in front of a DELETION.

⚑⚑⚑ THE ASYMMETRY IS THE WHOLE SUBJECT, AND IT IS WHY THE REFUSAL ARMS OUTNUMBER THE HAPPY ONE.
A false REMOVABLE loses a file; a false BLOCKED costs a reader one look. So the cases that matter
are the ones where a twin EXISTS and must still be refused — a drifted body, a missing twin — and
the discriminator is that `_normalise` must not launder a real difference into agreement.

⚑⚑ THE FIXTURES ARE PLANTED IN THE REAL TREE, at `scripts/` and `substrate/` under a name no
module uses, because `verdict` resolves against `corpus.ROOT` by construction — the same
constraint `record_migrate_selftest` records for the same path-keyed reason. Injecting a root
would test a parameter this module does not have. Every fixture is removed in `__exit__`, and the
planter REFUSES to write over an existing file rather than clobbering a real module.

⚑⚑ AND THE POPULATION ARMS ASSERT A SHAPE, NEVER A MEMBER. `PROMOTED` and `KEPT` name real
modules a later cleanup will delete; a case naming one expires the day it goes. What must hold is
that the two rosters are disjoint and that every roster entry gets a ranked verdict carrying its
reason — all of which survive the rosters changing.

⚑⚑ A ROSTER-IS-NON-EMPTY CASE WAS WRITTEN AND WITHDRAWN, BECAUSE IT CANNOT FAIL. `PROMOTED` is a
literal tuple, so mypy proves the empty branch unreachable and refuses the file — the type gate
saying, correctly, that the assertion is about the source text rather than about behaviour. **A
case that cannot fail is worse than an absent one**, so it is recorded here rather than written.

⚑ THE COUNT LINE IS AN ARM OF ITS OWN. `report` returns a blocked count that `main` turns into an
exit code, so a summary that miscounts turns a refusal into a silent success — the direction that
loses files. Both halves are pinned, because a constant zero passes the clean case alone.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from substrate import corpus, twin_check

if TYPE_CHECKING:
    from pathlib import Path

# What a planted twin pair holds. The import line is the one difference a promotion MUST
# introduce, so it is present in both halves in its own spelling.
_OLD_BODY = '"""A module."""\nfrom scripts import corpus\nVALUE = 1\n'
_NEW_BODY = '"""A module."""\nfrom substrate import corpus\nVALUE = 1\n'

# A body differing beyond its imports — the DRIFTED case.
_DRIFTED_BODY = '"""A module."""\nfrom substrate import corpus\nVALUE = 2\n'

# The fixture stem, chosen so no real module can collide with it.
_STEM = "twin_check_selftest_fixture"


class _Pair:
    """Plant an old/new module pair in the real tree, and remove it again.

    ⚑ IT REFUSES RATHER THAN OVERWRITES. A fixture that clobbered a real module would pass its
    own case and damage the tree; the planter checks first and raises if anything is there.
    """

    def __init__(self, old: str | None, new: str | None) -> None:
        """Record which halves to write."""
        self.old_path = corpus.ROOT / "scripts" / f"{_STEM}.py"
        self.new_path = corpus.ROOT / "substrate" / f"{_STEM}.py"
        self._old = old
        self._new = new

    def __enter__(self) -> tuple[Path, Path]:
        """Write the halves that were asked for and return both paths."""
        for path, body in ((self.old_path, self._old), (self.new_path, self._new)):
            if body is None:
                continue
            if path.exists():
                msg = f"fixture would clobber a real file at {path}"
                raise RuntimeError(msg)
            path.write_text(body, encoding="utf-8")
        return (self.old_path, self.new_path)

    def __exit__(self, *_exc: object) -> None:
        """Remove every half, whether or not the case passed."""
        self.old_path.unlink(missing_ok=True)
        self.new_path.unlink(missing_ok=True)


def an_identical_twin_is_removable(out: list[str]) -> int:
    """Check a correctly promoted module reads REMOVABLE — the happy path."""
    with _Pair(_OLD_BODY, _NEW_BODY):
        state, detail = twin_check.verdict(_STEM)
        if state != "REMOVABLE":
            out.append(f"selftest: an identical twin read {state}: {detail}")
            return 1
        if _STEM not in detail:
            out.append(f"selftest: the REMOVABLE detail does not name the twin: {detail}")
            return 1
    return 0


def a_drifted_body_is_refused(out: list[str]) -> int:
    """Check a twin differing beyond its imports BLOCKS — THE DISCRIMINATOR.

    ⚑⚑ WITHOUT THIS ARM A `_normalise` THAT ERASED EVERYTHING WOULD PASS. Same-name is not
    same-file: a stale half-copy has the right path and the wrong body, and reporting it
    REMOVABLE is the failure that loses the only remaining version.
    """
    with _Pair(_OLD_BODY, _DRIFTED_BODY):
        state, detail = twin_check.verdict(_STEM)
        if state != "DRIFTED":
            out.append(f"selftest: a drifted twin read {state}: {detail}")
            return 1
        if "DO NOT DELETE" not in detail:
            out.append(f"selftest: the DRIFTED detail does not refuse: {detail}")
            return 1
    return 0


def a_missing_twin_is_refused(out: list[str]) -> int:
    """Check an old file with nothing at the new path BLOCKS rather than reading clean."""
    with _Pair(_OLD_BODY, None):
        state, detail = twin_check.verdict(_STEM)
        if state != "NO TWIN":
            out.append(f"selftest: a module with no twin read {state}: {detail}")
            return 1
        if "DO NOT DELETE" not in detail:
            out.append(f"selftest: the NO TWIN detail does not refuse: {detail}")
            return 1
    return 0


def an_absent_old_file_is_gone_not_removable(out: list[str]) -> int:
    """Check nothing at the OLD path reads GONE — absent and removable are different facts.

    ⚑ REPORTING AN ALREADY-DELETED FILE AS REMOVABLE would make a second run claim work still
    to do, and a reader acting on it looks for a file that is not there.
    """
    with _Pair(None, _NEW_BODY):
        state, _detail = twin_check.verdict(_STEM)
        if state != "GONE":
            out.append(f"selftest: an already-removed module read {state}")
            return 1
    return 0


def the_import_rewiring_alone_is_not_drift(out: list[str]) -> int:
    """Check both import spellings are undone — a check that always fires teaches its neglect.

    ⚑ THE MODULE FORM AND THE FROM FORM ARE SEPARATE REPLACEMENTS. Undoing only one reports
    every module using the other as drifted, which is the always-red failure `_normalise` exists
    to avoid. Asserted through the public verdict, so the seam is exercised as a consumer sees
    it rather than by reaching for a private name.
    """
    for old, new in (
        ("from scripts import corpus\n", "from substrate import corpus\n"),
        ("from scripts.ratchet import x\n", "from substrate.ratchet import x\n"),
    ):
        with _Pair(old, new):
            state, detail = twin_check.verdict(_STEM)
            if state != "REMOVABLE":
                out.append(f"selftest: the rewiring {new!r} alone read {state}: {detail}")
                return 1
    return 0


def normalisation_does_not_launder_a_body_difference(out: list[str]) -> int:
    """Check the permissiveness is bounded to the two rewired spellings.

    ⚑ THE DRIFTED ARM ABOVE CHANGES A VALUE; this changes a line that LOOKS like the rewiring
    without being it, so a normaliser matching too loosely is caught separately from one that
    ignores bodies altogether.
    """
    with _Pair('"""A module."""\nimport scripts\n', '"""A module."""\nimport substrate\n'):
        state, _detail = twin_check.verdict(_STEM)
        if state != "DRIFTED":
            out.append(f"selftest: a bare `import` rename read {state}, not DRIFTED")
            return 1
    return 0


def a_kept_module_reads_kept_with_its_reason(out: list[str]) -> int:
    """Check a deliberate non-promotion is a ROW, not an absence.

    ⚑ THE PROPERTY, NOT A MEMBER. Every KEPT entry must render as KEEP and carry its recorded
    reason, so a reader cannot mistake a decision for an oversight — and this survives the
    roster changing, which naming one entry would not.
    """
    for name, reason in twin_check.KEPT.items():
        state, detail = twin_check.verdict(name)
        if state != "KEEP":
            out.append(f"selftest: kept module {name} read {state}")
            return 1
        if detail != reason:
            out.append(f"selftest: {name}'s verdict does not carry its recorded reason")
            return 1
        if not reason.strip():
            out.append(f"selftest: {name} is kept with an empty reason")
            return 1
    return 0


def a_kept_module_beats_its_own_files(out: list[str]) -> int:
    """Check KEPT is decided BEFORE the filesystem is consulted — the precedence arm.

    ⚑⚑ A DELIBERATE NON-PROMOTION MUST READ KEEP WHATEVER IS ON DISK. If the file check ran
    first, a kept module whose twin happens to exist would read REMOVABLE and be deleted — the
    exact loss the roster exists to prevent. The fixture plants a DRIFTED pair under a name
    added to the roster for this case, so a precedence slip shows as DRIFTED rather than KEEP.
    """
    kept = dict(twin_check.KEPT)
    twin_check.KEPT[_STEM] = "planted by the selftest to pin roster precedence"
    try:
        with _Pair(_OLD_BODY, _DRIFTED_BODY):
            state, detail = twin_check.verdict(_STEM)
            if state != "KEEP":
                out.append(f"selftest: a kept module was adjudicated from disk: {state}")
                return 1
            if detail != twin_check.KEPT[_STEM]:
                out.append(f"selftest: the KEEP detail is {detail!r}")
                return 1
    finally:
        twin_check.KEPT.clear()
        twin_check.KEPT.update(kept)
    return 0


def the_two_rosters_are_disjoint(out: list[str]) -> int:
    """Check nothing is both promoted and deliberately kept — a shape, not a member."""
    overlap = sorted(set(twin_check.PROMOTED) & set(twin_check.KEPT))
    if overlap:
        out.append(f"selftest: modules are both promoted and kept: {overlap!r}")
        return 1
    return 0


def refusals_sort_before_clean_rows(out: list[str]) -> int:
    """Check a BLOCKED row is printed first, so a reader meets it before the summary."""
    with _Pair(_OLD_BODY, None):
        lines, _blocked = twin_check.report((*twin_check.KEPT, _STEM))
        if "NO TWIN" not in lines[0]:
            out.append(f"selftest: the first row is not the refusal: {lines[0]!r}")
            return 1
    return 0


def the_summary_counts_what_the_rows_say(out: list[str]) -> int:
    """Check the count line and the blocked return agree with the rendered verdicts.

    ⚑⚑ THE COUNT IS WHAT `main` TURNS INTO AN EXIT CODE. A summary undercounting blocked rows
    exits 0 over a report that refuses, which is a refusal that silences itself.
    """
    with _Pair(_OLD_BODY, _DRIFTED_BODY):
        lines, blocked = twin_check.report((_STEM,))
        if blocked != 1:
            out.append(f"selftest: one drifted module counted as {blocked} blocked")
            return 1
        summary = next((ln for ln in lines if ln.startswith("twin-check:")), "")
        if "1 BLOCKED" not in summary:
            out.append(f"selftest: the summary is {summary!r}")
            return 1
        if not any("no verified twin" in ln for ln in lines):
            out.append("selftest: a blocked report omits the warning about deleting it")
            return 1
    return 0


def a_clean_report_counts_no_blocked(out: list[str]) -> int:
    """Check the blocked count is not a constant — the other half of the count arm."""
    with _Pair(_OLD_BODY, _NEW_BODY):
        lines, blocked = twin_check.report((_STEM,))
        if blocked:
            out.append(f"selftest: a removable module counted as {blocked} blocked")
            return 1
        if any("no verified twin" in ln for ln in lines):
            out.append("selftest: a clean report carries the blocked warning anyway")
            return 1
        summary = next((ln for ln in lines if ln.startswith("twin-check:")), "")
        if "1 removable" not in summary:
            out.append(f"selftest: the clean summary is {summary!r}")
            return 1
    return 0


def the_live_report_covers_both_rosters(out: list[str]) -> int:
    """Check the default population is promoted PLUS kept, and every module gets a row.

    ⚑ A REPORT LISTING ONLY REMOVABLE FILES would make a deliberate non-promotion look like an
    oversight. This asserts the row count rather than any module's verdict, so it survives the
    tree's actual state changing under it.
    """
    names = (*twin_check.PROMOTED, *twin_check.KEPT)
    lines, _blocked = twin_check.report(names)
    if len(lines) < len(names) + 1:
        out.append(f"selftest: {len(names)} module(s) produced {len(lines)} line(s)")
        return 1
    for name in names:
        if not any(name in ln for ln in lines):
            out.append(f"selftest: {name} has no row in the live report")
            return 1
    return 0


def every_live_verdict_is_a_declared_state(out: list[str]) -> int:
    """Check no module produces a state outside the ordering.

    ⚑ THE RANKING DEFAULTS AN UNKNOWN STATE TO THE REFUSAL POSITION, which is the safe
    direction and also a silent one — a typo'd state would sort among the refusals rather than
    announce itself. So the states are checked against the roster directly.
    """
    declared = set(twin_check._ORDER)  # noqa: SLF001 — the ordering roster under test
    for name in (*twin_check.PROMOTED, *twin_check.KEPT):
        state, _detail = twin_check.verdict(name)
        if state not in declared:
            out.append(f"selftest: {name} produced an unranked state {state!r}")
            return 1
    return 0


_ARMS = (
    an_identical_twin_is_removable,
    a_drifted_body_is_refused,
    a_missing_twin_is_refused,
    an_absent_old_file_is_gone_not_removable,
    the_import_rewiring_alone_is_not_drift,
    normalisation_does_not_launder_a_body_difference,
    a_kept_module_reads_kept_with_its_reason,
    a_kept_module_beats_its_own_files,
    the_two_rosters_are_disjoint,
    refusals_sort_before_clean_rows,
    the_summary_counts_what_the_rows_say,
    a_clean_report_counts_no_blocked,
    the_live_report_covers_both_rosters,
    every_live_verdict_is_a_declared_state,
)

_CASE_COUNT = 2 + 2 + 2 + 1 + 2 + 1 + 3 + 2 + 1 + 1 + 3 + 3 + 2 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"twin-check selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"twin-check selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
