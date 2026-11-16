#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.pid_ownership`: one discriminator per kind, plus its two boundaries.

⚑⚑ EVERY ARM DRIVES A SYNTHETIC MODULE, NOT A LIVE FILE. Arms naming live files have expired four
times in this arc: a case asserting `scripts/check_claims.py` is REACHED is a case about today's
tree, and it turns red the day somebody converts it — which is the day the census is WORKING. The
property under test is the CLASSIFICATION, so every fixture is a source string written here to
carry exactly one shape.

⚑⚑⚑ AND EVERY ARM IS A DISCRIMINATOR, WHICH IS WHAT SEPARATES THIS FROM A SUITE THAT PASSES ON A
BROKEN READER. Each positive arm ("this shape is UNREACHED") is paired with the negative a
predicate always answering yes would fail — `a_center_reaching_module_is_not_on_the_work_list` is
the arm a reader flagging everything would fail, and `a_bare_module_claims_nothing` is the arm a
reader keyed on the `sys` import would fail. Named as premises of their positives rather than
argued in a paragraph nobody can check.

⚑ THE ENTRY ARM IS THE ONE THAT PINS THE EXEMPTION. A `__main__` guard reading `sys.argv` is the
one legitimate PID claim, and a census without that arm would be indistinguishable from one that
simply never looks at guards — it would report the same numbers for the wrong reason.
"""

from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from mikemol.witness import witness_family

from substrate import pid_ownership, suite_emit

# A module that hands its guard's argv to a `main` reaching the center. ⚑ THE SHAPE THE RULING
# ASKS FOR, and the negative control for every arm below.
_REACHED = """
import sys
from substrate.ratchet_flags import check_argv

def main(argv):
    rc = check_argv(argv, ("--quiet",), "t")
    return 0 if rc is None else rc

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
"""

# A module whose `main` parses flags by hand and never reaches the center — the work list's shape.
_UNREACHED = """
import sys

def main(argv):
    quiet = "--quiet" in argv
    return 0 if quiet else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
"""

# A module whose CAPABILITY reads the global directly — the argv half of the ruling with no entry
# point behind it. ⚑ `report` is not the guard's callee, which is exactly what makes it captive.
_CAPTIVE = """
import sys

def report():
    return "--quiet" in sys.argv

def main(argv):
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
"""

# A library — no guard at all — that ends the process. The lifetime half, with no defence.
_FATAL = """
import sys

def load(path):
    if not path:
        sys.exit(2)
    return path
"""

# A guard handing argv to a callee that neither reads it nor reaches the center — the legitimate
# claim, and the boundary the work list is measured from.
_ENTRY = """
import sys

def run(flags):
    return 0

if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
"""

# A library claiming neither the arguments nor the lifetime — the arm a reader flagging everything
# with a `sys` import would fail.
_CLEAR = """
import sys

def width(text):
    return len(text) + sys.maxsize * 0
"""

# A dispatch guard calling a builtin beside its real handoff. ⚑ THE REGRESSION FIXTURE for the
# defect measured on this census's own first run — see `_delegates`.
_BUILTIN_IN_GUARD = """
import sys

def report():
    return "--quiet" in sys.argv

def main(argv):
    return 0

if __name__ == "__main__":
    print("banner")
    sys.exit(main(sys.argv[1:]))
"""

# The key this suite reports under. ⚑ THE REPO-RELATIVE PATH, which is what the discovery
# convention labels a suite with and therefore what the runner's ledger is keyed on.
_KEY = "substrate/pid_ownership_selftest.py"


def _read(source: str, name: str = "fixture.py") -> str:
    """Return the kind `pid_ownership` assigns to one synthetic module."""
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / name
        path.write_text(source, encoding="utf-8")
        row = pid_ownership.read_one(path, name)
        return "UNPARSED" if row is None else row.kind


def _check(out: list[str], source: str, want: str, *, name: str = "fixture.py") -> int:
    """Assert one fixture's kind, appending the disagreement when it differs."""
    got = _read(source, name)
    if got != want:
        out.append(f"selftest: {name} classified {got!r}, want {want!r}")
        return 1
    return 0


def a_center_reaching_module_is_not_on_the_work_list(out: list[str]) -> int:
    """Check that a module already calling `check_argv` reads REACHED and is not work.

    ⚑⚑ THE POSITIVE CONTROL FOR THE WHOLE CENSUS. Every other arm asserts that some shape IS a
    claim, and a reader that flagged every module in the corpus would satisfy them all — while
    handing an operator a work list identical to the population. This is the arm that fails on
    that reader.
    """
    bad = _check(out, _REACHED, pid_ownership.REACHED)
    if pid_ownership.REACHED in pid_ownership.WORK:
        out.append("selftest: REACHED was placed on the work list")
        bad += 1
    return bad


def a_hand_parsing_entry_callee_is_the_work_list(out: list[str]) -> int:
    """Check that a `main` parsing flags itself reads UNREACHED and IS work.

    ⚑ BOTH HALVES. Classifying it correctly and then leaving it off the work list would produce a
    census that is right and useless — the kind is only load-bearing if it reaches the output an
    operator acts on.
    """
    bad = _check(out, _UNREACHED, pid_ownership.UNREACHED)
    if pid_ownership.UNREACHED not in pid_ownership.WORK:
        out.append("selftest: UNREACHED is not on the work list")
        bad += 1
    return bad


def a_capability_reading_the_global_is_captive(out: list[str]) -> int:
    """Check that a non-callee function reading `sys.argv` reads CAPTIVE, not UNREACHED.

    ⚑⚑ THE TWO ARE THE SAME SYNTAX AND DIFFERENT WORK, which is the reason the kind exists. An
    UNREACHED `main` needs its parsing swapped for a `check_argv` call; a CAPTIVE function needs a
    PARAMETER it does not have, so the fix changes its signature and every call site. Folding them
    would hand an operator one list requiring two unrelated edits.
    """
    return _check(out, _CAPTIVE, pid_ownership.CAPTIVE)


def a_builtin_in_the_guard_does_not_excuse_a_captive(out: list[str]) -> int:
    """Check that a `print` beside the handoff does not suppress the CAPTIVE finding.

    ⚑⚑⚑ THE REGRESSION ARM, AND THE DEFECT IT PINS WAS THIS CENSUS'S OWN. The first cut collected
    every bare-name call under a guard as a "callee" — `print`, `len`, `sorted` — and `callees` is
    what EXCUSES a function from CAPTIVE. So a module whose guard happened to call a builtin could
    silently exempt a real finding, through a detail line nobody would read as load-bearing. The
    fixture is the CAPTIVE module with one `print` added: it must still read CAPTIVE.
    """
    return _check(out, _BUILTIN_IN_GUARD, pid_ownership.CAPTIVE)


def a_library_that_exits_is_fatal(out: list[str]) -> int:
    """Check that `sys.exit` in a module with no guard reads FATAL.

    ⚑ THE KIND WITH NO LEGITIMATE INSTANCE. A guard can justify a `sys.exit`; a module that is only
    ever imported cannot, because no caller handed it the process. This arm is what stops the
    lifetime half of the ruling being collapsed into the argv half.
    """
    return _check(out, _FATAL, pid_ownership.FATAL)


def a_main_guard_may_claim_its_own_argv(out: list[str]) -> int:
    """Check that a guard reading argv reads ENTRY, and that ENTRY is not work.

    ⚑⚑ THIS IS THE EXEMPTION, MADE CHECKABLE. The ruling's own text names the guard as the one
    place a process may claim argv; a census that flagged it would be arguing with the ruling it
    implements, and one that never looked at guards would report identical numbers for the wrong
    reason. Both halves are asserted so the exemption cannot be satisfied by absence.
    """
    bad = _check(out, _ENTRY, pid_ownership.ENTRY)
    if pid_ownership.ENTRY in pid_ownership.WORK:
        out.append("selftest: a __main__ guard's own argv claim was put on the work list")
        bad += 1
    return bad


def a_bare_module_claims_nothing(out: list[str]) -> int:
    """Check that a library touching `sys` but not argv or exit reads CLEAR.

    ⚑ THE SECOND NEGATIVE CONTROL, and it is not redundant with the REACHED arm. A reader keyed on
    the `sys` IMPORT rather than on the argv read would pass that one and fail this — and importing
    `sys` is near-universal in this corpus, so that reader would report almost the whole tree.
    """
    return _check(out, _CLEAR, pid_ownership.CLEAR)


def a_suite_is_held_out_of_the_work_list(out: list[str]) -> int:
    """Check that a `*_selftest.py` reads SUITE even when its body is the UNREACHED shape.

    ⚑⚑ THE ENTANGLEMENT ARM, AND THE FIXTURE IS DELIBERATELY THE WORK-LIST BODY. A suite reads argv
    to honour the discovery literal, and the pytest migration retires that reader wholesale — so a
    row converted here would be deleted there. Driving it with the exact source that reads
    UNREACHED under any other name proves the hold-out is keyed on the SUFFIX, not on suites
    happening to be written differently.
    """
    bad = _check(out, _UNREACHED, pid_ownership.SUITE, name="thing_selftest.py")
    if pid_ownership.SUITE in pid_ownership.WORK:
        out.append("selftest: a suite was put on this item's work list")
        bad += 1
    return bad


def the_render_states_both_boundaries(out: list[str]) -> int:
    """Check that the output carries the predicate's blind spots AND the walk's exclusions.

    ⚑⚑ TWO DIFFERENT BOUNDARIES, AND A CENSUS NEEDS BOTH. `unresolved` names what the predicate
    could not DECIDE about a file it read; `walk_scope` names what the walk never REACHED. A reader
    given one of them cannot tell a small work list from a narrow instrument, which is the
    `report presence, never absence` failure at the level of this tool's own output.
    """
    bad = 0
    rows = (
        pid_ownership.Claim("a.py", pid_ownership.UNREACHED, "x"),
        pid_ownership.Claim("b_selftest.py", pid_ownership.SUITE, "y"),
    )
    body = pid_ownership.render(rows)
    for shape in ("one-hop", "dynamic-dispatch", "suite-entanglement"):
        if shape not in body:
            out.append(f"selftest: the render does not name the {shape!r} blind spot")
            bad += 1
    if "the walk did NOT look at" not in body:
        out.append("selftest: the render does not carry the walk's own boundary")
        bad += 1
    if "a.py" not in body:
        out.append("selftest: the render does not name the work-list row")
        bad += 1
    return bad


def the_suite_boundary_appears_only_when_suites_do(out: list[str]) -> int:
    """Check that `unresolved` adds the entanglement note only when a suite is present.

    ⚑ A DISCLOSURE THAT FIRES WHEN THERE IS NOTHING TO DISCLOSE TEACHES A READER TO SKIP IT — the
    lesson `walk_scope`'s empty-root arm records, applied to the other boundary. A census over a
    directory with no suites must not claim an overlap it does not have.
    """
    bad = 0
    without = pid_ownership.unresolved((pid_ownership.Claim("a.py", pid_ownership.CLEAR, "x"),))
    if any("suite-entanglement" in s for s in without):
        out.append("selftest: the suite boundary was stated where no suite exists")
        bad += 1
    with_suite = pid_ownership.unresolved(
        (pid_ownership.Claim("b_selftest.py", pid_ownership.SUITE, "y"),)
    )
    if not any("suite-entanglement" in s for s in with_suite):
        out.append("selftest: the suite boundary was omitted where a suite exists")
        bad += 1
    return bad


def every_kind_reaches_the_denominator(out: list[str]) -> int:
    """Check that each kind the classifier can emit is carried by `KINDS` and carries a reason.

    ⚑⚑ THE ARM THAT CATCHES A KIND ADDED AND FORGOTTEN. A kind emitted by `read_one` but missing
    from `KINDS` vanishes from the render's denominator, so the totals stop summing to the
    population and nothing says so — a census silently under-reporting itself. Asserting the
    round-trip is cheaper than a reader noticing the arithmetic.
    """
    bad = 0
    emitted = {
        pid_ownership.REACHED,
        pid_ownership.UNREACHED,
        pid_ownership.CAPTIVE,
        pid_ownership.FATAL,
        pid_ownership.ENTRY,
        pid_ownership.CLEAR,
        pid_ownership.SUITE,
    }
    missing = emitted - set(pid_ownership.KINDS)
    if missing:
        out.append(f"selftest: kind(s) {sorted(missing)} are emitted but absent from KINDS")
        bad += 1
    unreasoned = [k for k in pid_ownership.KINDS if not pid_ownership.Claim("x", k, "y").why]
    if unreasoned:
        out.append(f"selftest: kind(s) {unreasoned} carry no reason")
        bad += 1
    return bad


FAMILY = witness_family.of(
    key="pid_ownership",
    apex="a module's relationship to the argv center is readable as a kind that names a next "
    "action — the work list, the exemption, the already-done, and the population another "
    "item owns — with both of the census's boundaries stated in its own output",
    subject="the claims `substrate.pid_ownership` assigns to a module over `sys.argv`/`sys.exit`",
    members=(
        witness_family.Member(
            name="a_center_reaching_module_is_not_on_the_work_list",
            claim="a module already calling check_argv reads REACHED and is not work",
            cases=2,
        ),
        witness_family.Member(
            name="a_hand_parsing_entry_callee_is_the_work_list",
            claim="a main parsing flags itself reads UNREACHED and reaches the work list",
            cases=2,
            premises=("a_center_reaching_module_is_not_on_the_work_list",),
        ),
        witness_family.Member(
            name="a_capability_reading_the_global_is_captive",
            claim="a non-callee function reading sys.argv reads CAPTIVE, not UNREACHED",
            premises=("a_center_reaching_module_is_not_on_the_work_list",),
        ),
        witness_family.Member(
            name="a_builtin_in_the_guard_does_not_excuse_a_captive",
            claim="a print beside the handoff does not suppress the CAPTIVE finding",
            premises=("a_capability_reading_the_global_is_captive",),
        ),
        witness_family.Member(
            name="a_library_that_exits_is_fatal",
            claim="sys.exit in a module with no __main__ guard reads FATAL",
            premises=("a_center_reaching_module_is_not_on_the_work_list",),
        ),
        witness_family.Member(
            name="a_main_guard_may_claim_its_own_argv",
            claim="a guard reading argv reads ENTRY and is exempt from the work list",
            cases=2,
        ),
        witness_family.Member(
            name="a_bare_module_claims_nothing",
            claim="a library touching sys but not argv or exit reads CLEAR",
        ),
        witness_family.Member(
            name="a_suite_is_held_out_of_the_work_list",
            claim="a *_selftest.py reads SUITE even carrying the UNREACHED body",
            cases=2,
        ),
        witness_family.Member(
            name="the_render_states_both_boundaries",
            claim="the output carries the predicate's blind spots and the walk's exclusions",
            cases=5,
        ),
        witness_family.Member(
            name="the_suite_boundary_appears_only_when_suites_do",
            claim="the entanglement note is stated only when a suite is in the population",
            cases=2,
        ),
        witness_family.Member(
            name="every_kind_reaches_the_denominator",
            claim="each kind the classifier emits is carried by KINDS and carries a reason",
            cases=2,
        ),
    ),
)

_ARMS = (
    a_center_reaching_module_is_not_on_the_work_list,
    a_hand_parsing_entry_callee_is_the_work_list,
    a_capability_reading_the_global_is_captive,
    a_builtin_in_the_guard_does_not_excuse_a_captive,
    a_library_that_exits_is_fatal,
    a_main_guard_may_claim_its_own_argv,
    a_bare_module_claims_nothing,
    a_suite_is_held_out_of_the_work_list,
    the_render_states_both_boundaries,
    the_suite_boundary_appears_only_when_suites_do,
    every_kind_reaches_the_denominator,
)

# ⚑ DERIVED FROM THE FAMILY, NOT HAND-SUMMED — a total that moved while only names changed is a
# dropped or invented assertion.
_CASE_COUNT = FAMILY.count


def selftest() -> int:
    """Run every arm, report by TYPED RECORD, and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(_KEY, _CASE_COUNT - failures, _CASE_COUNT)


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
