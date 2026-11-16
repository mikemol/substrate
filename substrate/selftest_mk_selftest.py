#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.selftest_mk` — a check that cannot FAIL is not a check.

⚑⚑⚑ THE NEGATIVE CONTROL IS THE ITEM, AND ITS ABSENCE IS THE WHOLE INCIDENT. A session added a
suite, ran `gen_selftest_mk.py --check`, read exit 0, and reported the roster current. That
module is a pure RENDERER with no `main` and no CLI: it accepts any flag and exits 0 having done
nothing. Discovery found 236 suites, `Selftest.mk` declared 235, and the new suite never ran.
**A flag a program does not implement is byte-identical to one it satisfies** — both exit 0 and
print nothing.

⚑⚑ SO EVERY ARM HERE THAT ASSERTS A PASS IS PAIRED WITH ONE THAT FORCES A REFUSAL. Verifying
`--check` returns 0 on a current roster proves nothing on its own: that is exactly what the
non-existent mode did. What separates a working check from an absent one is that the working one
goes RED when the artefact moves.

⚑ AND THIS MODULE ALSO EXISTED WITHOUT CASES. `selftest_mk.py`'s `--selftest` returned a bare
`0` so discovery would see it — the `silent` verdict `suite_run`'s own docstring records catching
in ITSELF, and the fix it prescribes is delegation to a sibling rather than a vacuous success.
"""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
from pathlib import Path

from substrate import selftest_mk

# A rendered roster in the shape the generator emits — two targets, recipe bodies included, so
# the target reader is exercised against real surrounding text rather than bare lines.
_BODY = """# GENERATED
BUILD := _build/selftest

all: $(BUILD)/a__x.py.ran $(BUILD)/b__y.py.ran

$(BUILD)/a__x.py.ran: a/x.py
\t@mkdir -p $(dir $@)
\t@$(MEMBUDGET) run auto selftest:x.py -- $(PY) -m substrate.suite_run a/x.py $@ a/x.py

$(BUILD)/b__y.py.ran: b/y.py
\t@mkdir -p $(dir $@)
\t@$(MEMBUDGET) run auto selftest:y.py -- $(PY) -m substrate.suite_run b/y.py $@ b/y.py
"""

# The recipe block a fixture drops to simulate a suite that is discovered but not declared.
_DROPPED = (
    "$(BUILD)/b__y.py.ran: b/y.py\n"
    "\t@mkdir -p $(dir $@)\n"
    "\t@$(MEMBUDGET) run auto selftest:y.py -- $(PY) -m substrate.suite_run "
    "b/y.py $@ b/y.py\n"
)

# What the two declared targets are.
_TARGETS = ("$(BUILD)/a__x.py.ran", "$(BUILD)/b__y.py.ran")

# How many targets that body declares.
_TARGET_COUNT = 2


def _written(where: str, text: str) -> Path:
    """Write a fixture roster the way the writer does — body plus one trailing newline."""
    path = Path(where) / selftest_mk.TARGET
    path.write_text(text, encoding="utf-8")
    return path


def a_current_roster_passes(out: list[str]) -> int:
    """Check an unchanged file is accepted."""
    with tempfile.TemporaryDirectory() as where:
        got = selftest_mk.check(_BODY, _written(where, _BODY + "\n"))
    if got != 0:
        out.append(f"selftest: a current roster was refused ({got})")
        return 1
    return 0


def an_added_suite_is_refused(out: list[str]) -> int:
    """Check a discovered-but-undeclared suite REFUSES — THE INCIDENT, EXACTLY.

    ⚑⚑⚑ THIS IS THE ARM THAT WOULD HAVE CAUGHT IT. The committed file is missing a target the
    renderer now produces, which is the 235-vs-236 state precisely: the suite exists, discovery
    finds it, and `make` would never run it.
    """
    with tempfile.TemporaryDirectory() as where:
        got = selftest_mk.check(
            _BODY, _written(where, _BODY.replace(_DROPPED, "") + "\n"), quiet=True
        )
    if got == 0:
        out.append("selftest: a roster missing a discovered suite was accepted")
        return 1
    return 0


def a_dropped_suite_is_refused(out: list[str]) -> int:
    """Check a declared-but-undiscovered target REFUSES — the OTHER direction.

    ⚑⚑ THE TWO DIRECTIONS ARE DIFFERENT REPAIRS AND MUST BOTH FIRE. Added means regenerate;
    dropped means a PREDICATE changed and a suite stopped being recognised — the under-admitting
    failure `suite_discovery`'s own docstring records four times, whose cost is invisible because
    a missing suite vanishes into a smaller green total.
    """
    with tempfile.TemporaryDirectory() as where:
        got = selftest_mk.check(
            _BODY, _written(where, _BODY + "$(BUILD)/c__z.py.ran: c/z.py\n"), quiet=True
        )
    if got == 0:
        out.append("selftest: a roster declaring an undiscovered target was accepted")
        return 1
    return 0


def a_changed_recipe_is_refused(out: list[str]) -> int:
    """Check a same-set body difference still refuses.

    ⚑ A COUNT MATCHING IS THE WORST CASE. Two rosters of N with one recipe rewritten — a
    different lease, a different claim tag — are identical by number and different in what they
    run. The rendered text is the artefact, so the text is what is compared.
    """
    changed = _BODY.replace("run auto selftest:x.py", "run 192 selftest:x.py")
    with tempfile.TemporaryDirectory() as where:
        got = selftest_mk.check(_BODY, _written(where, changed + "\n"), quiet=True)
    if got == 0:
        out.append("selftest: a roster with a rewritten recipe was accepted")
        return 1
    return 0


def an_absent_roster_is_stale_not_a_crash(out: list[str]) -> int:
    """Check a missing file refuses rather than raising.

    ⚑ A FRESH CHECKOUT HAS NO `Selftest.mk`, and the remedy is the same as for a stale one. A
    check that raised here would fail the gate with a traceback instead of an instruction.
    """
    with tempfile.TemporaryDirectory() as where:
        got = selftest_mk.check(_BODY, Path(where) / "absent.mk", quiet=True)
    if got == 0:
        out.append("selftest: an absent roster was accepted")
        return 1
    return 0


def a_refusal_names_the_remedy(out: list[str]) -> int:
    """Check the diagnostic tells a reader what to DO, not merely that something is wrong.

    ⚑⚑⚑ AND THIS IS THE ARM THAT KEEPS `quiet` HONEST. Every other refusal case passes
    `quiet=True` so fixture diagnostics do not read as a broken roster in a build log — but a
    flag that silenced EVERY message would be indistinguishable from a check that emits none,
    and no case would notice. This one captures stderr and asserts the CONTENT, so the
    reader-facing half stays exercised.

    ⚑ A GATE THAT SAYS "STALE" AND STOPS makes every reader re-derive the fix. The refusal must
    name the generator and, because the two directions are different repairs, say which target
    moved and which way.
    """
    said = io.StringIO()
    with tempfile.TemporaryDirectory() as where, contextlib.redirect_stderr(said):
        selftest_mk.check(_BODY, _written(where, _BODY.replace(_DROPPED, "") + "\n"))
    text = said.getvalue()

    if "selftest_mk.py" not in text:
        out.append(f"selftest: the refusal does not name the generator: {text!r}")
        return 1
    if "would not run" not in text:
        out.append(f"selftest: the refusal does not say the suite would not run: {text!r}")
        return 1
    return 0


def the_targets_are_read_from_rendered_text(out: list[str]) -> int:
    """Check the target reader sees what `make` sees.

    ⚑ RECIPE LINES AND THE `all:` LINE MUST NOT COUNT. A reader keying on `.ran` alone would
    take the `all:` aggregate and every stamp mentioned in it, reporting a roster far larger
    than the one declared.
    """
    got = selftest_mk.targets(_BODY)
    if got != _TARGETS:
        out.append(f"selftest: the targets read as {got!r}")
        return 1
    if len(got) != _TARGET_COUNT:
        out.append(f"selftest: {len(got)} target(s) read, expected {_TARGET_COUNT}")
        return 1
    return 0


def the_artefact_is_tracked(out: list[str]) -> int:
    """Check the generated roster is IN THE INDEX — gate-F62.

    ⚑⚑⚑ EVERY ARM ABOVE TESTS THE COMPARISON AND NONE TESTS WHETHER THERE IS ANYTHING TO
    COMPARE AGAINST. `Selftest.mk` had never been tracked — `git log` on the path returned
    nothing while `git check-ignore` exited 1, so it was neither committed nor deliberately
    ignored — and the gate that requires it fresh therefore refuses on every checkout. The
    absent-file arm proves the check REPORTS that state; it cannot notice that the state is
    permanent, because a tempdir fixture always has whatever file the case wrote.

    ⚑⚑ SO THE SUBJECT IS THE REPOSITORY, NOT THE RENDERER, and that is why no fixture can
    stand in. A generated artefact a blocking gate reads must be committed or every paydown
    is discarded with the working tree — which is what makes this a case rather than a note.

    ⚑ IT ASSERTS TRACKED, NEVER FRESH. Freshness is `--check`'s job and it moves with every
    added suite; a case pinning it here would go red on ordinary work and teach a reader to
    ignore this file. Tracked-ness only changes when someone removes the artefact.
    """
    import subprocess  # noqa: PLC0415

    from substrate import corpus  # noqa: PLC0415

    got = subprocess.run(  # noqa: S603
        ["git", "ls-files", "--error-unmatch", selftest_mk.TARGET],  # noqa: S607
        cwd=corpus.ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if got.returncode != 0:
        out.append(
            f"selftest: {selftest_mk.TARGET} is not tracked — the gate that requires it "
            f"fresh cannot pass on a checkout (gate-F62)"
        )
        return 1
    return 0


_ARMS = (
    a_current_roster_passes,
    an_added_suite_is_refused,
    a_dropped_suite_is_refused,
    a_changed_recipe_is_refused,
    an_absent_roster_is_stale_not_a_crash,
    a_refusal_names_the_remedy,
    the_targets_are_read_from_rendered_text,
    the_artefact_is_tracked,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 1 + 2 + 2 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"selftest-mk selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"selftest-mk selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
