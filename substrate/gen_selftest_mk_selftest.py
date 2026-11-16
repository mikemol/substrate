#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.gen_selftest_mk` — the renderer whose output RUNS every suite.

⚑⚑⚑ THE STAKES ARE WHY A PURE TEXT RENDERER IS WORTH PINNING AT ALL. This module decides nothing
and prints a makefile — but that makefile is how the whole selftest population executes, so a
malformed recipe does not fail loudly, it silently changes what runs. Two specific mistakes are
recorded in the module's own comments as HAVING BEEN MADE, and each is an arm here:

  · `mkdir -p` MUST PRECEDE THE WORK. A first draft emitted it after the suite, so a first run
    would touch a stamp into a directory that did not exist — failing on a CLEAN TREE, precisely
    the run nobody has tried. Reading the generated text caught it before running it did, which
    is exactly what these cases institutionalise.
  · THERE MUST BE NO `touch`. The stamp is written ONLY on `ok`, by `suite_run`. A `touch` in the
    recipe would stamp a FAILED run — marking the target satisfied so the next build skips the
    suite. That is a failure that silences itself, and it is the single worst thing this file
    could emit.

⚑⚑ THE ABSENCE ARMS NEED THE POSITIVE HALF BESIDE THEM. "No `touch` appears" is satisfied by an
empty string, so every no-X case here sits next to one asserting the recipe was actually rendered
— otherwise a renderer that produced nothing would read as maximally correct.

⚑⚑ AND THE ARMS ASSERT THE SHAPE OF A RECIPE, NEVER A PARTICULAR SUITE'S TEXT. The population
moves constantly; a case naming a real suite's label expires the day that suite is renamed. The
fixtures are synthetic labels, and the coverage arms assert only that the render covers whatever
population it was handed.

⚑ THE LEASE IS `auto` AND THAT IS PINNED AS A PROPERTY. A hardcoded figure collapses every
workload onto one number, over-sized for the median and under-sized for the tail at once — the
same reasoning the Agda build records. What the case checks is that no literal size reaches the
recipe, not that the word `auto` appears in a particular column.
"""

from __future__ import annotations

import sys

from substrate import corpus, gen_selftest_mk, suite_claims

# A synthetic population — labels no real suite carries, so no case expires on a rename.
_SUITES = [
    ("alpha/one", str(corpus.ROOT / "substrate" / "alpha_selftest.py")),
    ("beta/two", str(corpus.ROOT / "substrate" / "beta_selftest.py")),
]

# The path the single-recipe arms render against.
_PATH = str(corpus.ROOT / "substrate" / "alpha_selftest.py")

# Neither reaching a store nor fanning out — the plain classification.
_NONE: frozenset[str] = frozenset()


def _recipe() -> list[str]:
    """Render one recipe under the plain classification."""
    return gen_selftest_mk.recipe("alpha/one", _PATH, _NONE, _NONE)


def _text() -> str:
    """Render the whole makefile over the synthetic population."""
    return gen_selftest_mk.text(_SUITES, _NONE, _NONE)


def a_recipe_declares_its_stamp_against_its_source(out: list[str]) -> int:
    """Check the target is the STAMP and the prerequisite is the suite's own file.

    ⚑ THIS IS WHAT MAKES THE BUILD A DAG RATHER THAN A FAN OF PHONY TARGETS. A selftest
    produces no file, so the stamp is the artefact — and a suite re-runs when its SOURCE is
    newer, which is incremental in the honest sense.
    """
    lines = _recipe()
    if not lines:
        out.append("selftest: the recipe rendered nothing")
        return 1
    rule = lines[0]
    if ":" not in rule:
        out.append(f"selftest: the first line is not a rule: {rule!r}")
        return 1
    target, _sep, prereq = rule.partition(":")
    if target.strip() != gen_selftest_mk.stamp("alpha/one"):
        out.append(f"selftest: the target is {target.strip()!r}, not the stamp")
        return 1
    if not prereq.strip().endswith("alpha_selftest.py"):
        out.append(f"selftest: the prerequisite is {prereq.strip()!r}, not the source")
        return 1
    return 0


def the_prerequisite_is_repo_relative(out: list[str]) -> int:
    """Check the source is named relative to the root, so the makefile moves with the tree."""
    rule = _recipe()[0]
    _target, _sep, prereq = rule.partition(":")
    if str(corpus.ROOT) in prereq:
        out.append(f"selftest: the prerequisite carries an absolute path: {prereq.strip()!r}")
        return 1
    return 0


def a_stamp_path_cannot_collide_across_directories(out: list[str]) -> int:
    """Check a label's separators are flattened, so two suites cannot share one stamp.

    ⚑⚑ TWO LABELS DIFFERING ONLY IN DIRECTORY would otherwise write the same stamp file, and
    the second suite would read as already-built. A collision here does not fail — it SKIPS,
    which is the silent direction.
    """
    first = gen_selftest_mk.stamp("a/thing")
    second = gen_selftest_mk.stamp("b/thing")
    if first == second:
        out.append(f"selftest: two labels share the stamp {first!r}")
        return 1
    if "/" in first.removeprefix("$(BUILD)/"):
        out.append(f"selftest: the stamp keeps a path separator: {first!r}")
        return 1
    return 0


def the_directory_is_made_before_the_work(out: list[str]) -> int:
    """Check `mkdir -p` precedes the suite — THE RECORDED FIRST-RUN DEFECT.

    ⚑⚑⚑ A FIRST DRAFT EMITTED IT AFTER THE SUITE, so a first run would touch a stamp into a
    directory that did not exist — failing on a CLEAN TREE, precisely the run nobody has tried.
    Ordering is the whole assertion; both lines being present is not enough.
    """
    lines = _recipe()
    made = next((i for i, ln in enumerate(lines) if "mkdir" in ln), None)
    ran = next((i for i, ln in enumerate(lines) if "suite_run" in ln), None)
    if made is None:
        out.append("selftest: the recipe never creates the stamp directory")
        return 1
    if ran is None:
        out.append("selftest: the recipe never runs the suite")
        return 1
    if made > ran:
        out.append("selftest: the directory is created AFTER the suite runs")
        return 1
    return 0


def the_recipe_never_touches_its_own_stamp(out: list[str]) -> int:
    """Check no `touch` appears — THE FAILURE THAT WOULD SILENCE ITSELF.

    ⚑⚑⚑ THE STAMP IS WRITTEN ONLY ON `ok`, BY THE WRAPPER. A `touch` here would stamp a FAILED
    run, marking the target satisfied so the next build skips the suite entirely. `make` knows
    pass/fail, but `suite_outcome` names seven kinds and `vacuous` is decided WITHOUT consulting
    the exit code — so a suite can assert nothing and still exit success.

    ⚑ THE POSITIVE HALF IS BESIDE IT because an empty recipe also contains no `touch`.
    """
    lines = _recipe()
    if not any("suite_run" in ln for ln in lines):
        out.append("selftest: the recipe does not run the suite, so `no touch` asserts nothing")
        return 1
    offending = [ln for ln in lines if "touch" in ln]
    if offending:
        out.append(f"selftest: the recipe touches its stamp: {offending!r}")
        return 1
    return 0


def the_suite_runs_through_the_wrapper_that_owns_the_stamp(out: list[str]) -> int:
    """Check the suite is invoked via `suite_run` with the stamp and label handed to it.

    ⚑ THE WRAPPER WRITES THE STAMP, so it must RECEIVE the stamp path. A recipe invoking the
    suite directly would run the cases and record nothing.

    ⚑⚑ AND THE STAMP ARRIVES AS `$@`, NOT AS A REPEATED LITERAL — a first draft of this case
    asserted the literal and went red against a CORRECT recipe. Make's automatic variable IS
    the target, so the recipe cannot disagree with its own rule; spelling the path twice could.
    The case now pins the stronger property it found rather than the weaker one it assumed.
    """
    ran = next((ln for ln in _recipe() if "suite_run" in ln), "")
    if "$@" not in ran:
        out.append(f"selftest: the wrapper is not handed the target stamp: {ran!r}")
        return 1
    if gen_selftest_mk.stamp("alpha/one") in ran:
        out.append(f"selftest: the stamp is re-spelled rather than taken from `$@`: {ran!r}")
        return 1
    if not ran.rstrip().endswith("alpha/one"):
        out.append(f"selftest: the wrapper is not handed the label: {ran!r}")
        return 1
    return 0


def every_recipe_line_after_the_rule_is_tab_indented(out: list[str]) -> int:
    """Check the recipe body uses tabs — a makefile indented with spaces does not run.

    ⚑ THIS IS THE ONE SYNTAX ERROR A RENDERER CAN MAKE THAT NO READING CATCHES, because a
    space-indented recipe LOOKS right and make refuses it with a message about separators.
    """
    body = [ln for ln in _recipe()[1:] if ln]
    if not body:
        out.append("selftest: the recipe has no body")
        return 1
    for line in body:
        if not line.startswith("\t"):
            out.append(f"selftest: a recipe line is not tab-indented: {line!r}")
            return 1
    return 0


def the_lease_is_not_a_hardcoded_size(out: list[str]) -> int:
    """Check the recipe leases `auto` rather than a number — a property, not a spelling.

    ⚑ A HARDCODED FIGURE COLLAPSES EVERY WORKLOAD ONTO ONE NUMBER, over-sized for the median
    and under-sized for the tail at the same time. `auto` keys on the label and reads that
    suite's own recorded peaks.
    """
    if gen_selftest_mk.LEASE != "auto":
        out.append(f"selftest: the lease is the literal {gen_selftest_mk.LEASE!r}")
        return 1
    ran = next((ln for ln in _recipe() if "suite_run" in ln), "")
    if f"run {gen_selftest_mk.LEASE} " not in ran:
        out.append(f"selftest: the recipe does not lease through membudget: {ran!r}")
        return 1
    return 0


def the_membudget_label_comes_from_the_claims_authority(out: list[str]) -> int:
    """Check the tag is what `suite_claims` decides, not a name this module invents.

    ⚑⚑ THIS MODULE RENDERS; IT DECIDES NOTHING. The exclusion policy is `suite_claims`, and a
    first cut held all four responsibilities — threading ONE parameter through it took six
    refused edits, the gate saying the unit was wrong. A tag computed here would put the policy
    back inside the renderer where nothing could change it independently.
    """
    expected = suite_claims.label_for("alpha/one", _PATH, _NONE, _NONE)
    ran = next((ln for ln in _recipe() if "suite_run" in ln), "")
    if f" {expected} " not in ran:
        out.append(f"selftest: the recipe's tag is not the claims authority's: {ran!r}")
        return 1
    return 0


def a_classified_suite_is_tagged_differently_from_a_plain_one(out: list[str]) -> int:
    """Check the classification actually reaches the tag — THE DISCRIMINATOR.

    ⚑⚑ WITHOUT THIS, A RENDERER IGNORING `reaching` AND `fanout` ENTIRELY passes the arm above,
    because both would agree on the plain label. What must hold is that the two populations
    produce DIFFERENT recipes — otherwise the exclusion policy is threaded through and dropped.
    """
    plain = gen_selftest_mk.recipe("alpha/one", _PATH, _NONE, _NONE)
    reaching = gen_selftest_mk.recipe("alpha/one", _PATH, frozenset({_PATH}), _NONE)
    fanning = gen_selftest_mk.recipe("alpha/one", _PATH, _NONE, frozenset({_PATH}))
    if plain == reaching and plain == fanning:
        out.append(
            "selftest: neither classification changes the recipe — the policy is "
            "threaded through and dropped"
        )
        return 1
    return 0


def the_generated_file_says_it_is_generated(out: list[str]) -> int:
    """Check the marker heads the file, so no reader hand-edits it."""
    text = _text()
    if not text.startswith(gen_selftest_mk.MARKER):
        out.append("selftest: the marker does not head the generated file")
        return 1
    if "do not edit" not in gen_selftest_mk.MARKER:
        out.append(f"selftest: the marker does not refuse edits: {gen_selftest_mk.MARKER!r}")
        return 1
    return 0


def the_all_target_names_every_stamp(out: list[str]) -> int:
    """Check `all` depends on one stamp per suite — a shape over whatever population arrives."""
    line = next((ln for ln in _text().splitlines() if ln.startswith("all:")), "")
    for label, _path in _SUITES:
        if gen_selftest_mk.stamp(label) not in line:
            out.append(f"selftest: `all` omits the stamp for {label!r}")
            return 1
    return 0


def every_suite_gets_a_rule(out: list[str]) -> int:
    """Check the render covers the whole population it was handed, not the first member."""
    text = _text()
    for label, _path in _SUITES:
        if f"{gen_selftest_mk.stamp(label)}:" not in text:
            out.append(f"selftest: no rule was rendered for {label!r}")
            return 1
    return 0


def an_empty_population_still_renders_a_usable_makefile(out: list[str]) -> int:
    """Check nothing to run yields a valid file rather than a broken `all`."""
    text = gen_selftest_mk.text([], _NONE, _NONE)
    if not text.startswith(gen_selftest_mk.MARKER):
        out.append("selftest: an empty population lost the marker")
        return 1
    if "all:" not in text:
        out.append("selftest: an empty population has no `all` target")
        return 1
    return 0


def clean_removes_stamps_and_never_source(out: list[str]) -> int:
    """Check `clean` reaches only the build directory — it is total and cannot touch a suite.

    ⚑ A STAMP IS THE ONLY THING THIS BUILD CREATES, so `clean` removing `$(BUILD)` is complete.
    A removal naming anything else would be reaching for files it did not make.
    """
    removals = [ln for ln in _text().splitlines() if "rm " in ln]
    if not removals:
        out.append("selftest: there is no clean recipe")
        return 1
    for line in removals:
        if "$(BUILD)" not in line:
            out.append(f"selftest: a removal reaches outside the build dir: {line!r}")
            return 1
    return 0


def the_phony_targets_are_declared(out: list[str]) -> int:
    """Check `all`, `clean` and `list` are PHONY, so a same-named file cannot shadow them."""
    phony = next((ln for ln in _text().splitlines() if ln.startswith(".PHONY:")), "")
    for name in ("all", "clean", "list"):
        if name not in phony:
            out.append(f"selftest: {name} is not declared phony: {phony!r}")
            return 1
    return 0


def the_membudget_path_is_absolute(out: list[str]) -> int:
    """Check the wrapper is named by absolute path — the makefile cannot rely on PATH."""
    line = next((ln for ln in _text().splitlines() if ln.startswith("MEMBUDGET :=")), "")
    if str(corpus.ROOT) not in line:
        out.append(f"selftest: membudget is not resolved absolutely: {line!r}")
        return 1
    return 0


def the_list_target_names_every_suite(out: list[str]) -> int:
    """Check `list` enumerates the population, so a reader can see what would run."""
    body = _text().partition("list:")[2]
    for label, _path in _SUITES:
        if label not in body:
            out.append(f"selftest: `list` omits {label!r}")
            return 1
    return 0


_ARMS = (
    a_recipe_declares_its_stamp_against_its_source,
    the_prerequisite_is_repo_relative,
    a_stamp_path_cannot_collide_across_directories,
    the_directory_is_made_before_the_work,
    the_recipe_never_touches_its_own_stamp,
    the_suite_runs_through_the_wrapper_that_owns_the_stamp,
    every_recipe_line_after_the_rule_is_tab_indented,
    the_lease_is_not_a_hardcoded_size,
    the_membudget_label_comes_from_the_claims_authority,
    a_classified_suite_is_tagged_differently_from_a_plain_one,
    the_generated_file_says_it_is_generated,
    the_all_target_names_every_stamp,
    every_suite_gets_a_rule,
    an_empty_population_still_renders_a_usable_makefile,
    clean_removes_stamps_and_never_source,
    the_phony_targets_are_declared,
    the_membudget_path_is_absolute,
    the_list_target_names_every_suite,
)

_CASE_COUNT = 4 + 1 + 2 + 3 + 2 + 3 + 2 + 2 + 1 + 1 + 2 + 2 + 2 + 2 + 2 + 3 + 1 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"gen-selftest-mk selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"gen-selftest-mk selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
