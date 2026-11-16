#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.stage_diff` — the reading a seam defect needs, pinned.

⚑⚑⚑ THE `lost_at` ARM IS THE ITEM, AND IT IS THE MEASUREMENT THAT SETTLED A REAL INCIDENT. A
codemod's transform passed 23/23 while thirteen real files failed: the transform ADDED an import
and a later `ruff --fix` stage REMOVED it as unused. End-to-end output could say only *"the import
is absent"*; the artefact simply never had it by the time anyone looked. Two turns went to
inference — both refuted — before a stage dump produced two lines that settled it:

    import after transform: True
    import after fix:       False

`lost_at(steps, needle)` is that reading, generalised: the stage where something went from present
to absent. Without it a reader bisects by hand or guesses.

⚑⚑ AND A STAGE THAT CHANGED THE ARTEFACT IS NOT THEREBY THE CULPRIT — a formatter SHOULD change
it. The census reports WHERE a change appeared so the question *"may this stage do that"* is asked
of the right stage; deciding it here would be the judgement a census must not make. The arms
assert that distinction directly: `changed_at` names every stage that touched the file, and
nothing marks any of them wrong.

⚑ THE DIFF IS BOUNDED PER STAGE, NOT OVERALL — pinned because a formatter that rewrites a whole
file would otherwise consume the budget and hide the one-line change a later stage made, which is
precisely the reading this instrument exists to produce.
"""

from __future__ import annotations

import sys

from substrate import stage_diff

# A source that each fixture stage rewrites in a known way.
_SOURCE = "alpha\nbeta\ngamma\n"

# What a stage may do to it.
_NEEDLE = "beta"

# The bound one arm asserts, and the line delta another does.
_LIMIT = 5
_ONE = 1


def _adds(text: str) -> str:
    """Return `text` with a marker line appended."""
    return text + "delta\n"


def _removes(text: str) -> str:
    """Return `text` without the needle line."""
    return "".join(line for line in text.splitlines(keepends=True) if _NEEDLE not in line)


def _identity(text: str) -> str:
    """Return `text` unchanged — a stage that legitimately does nothing."""
    return text


def _stages(*pairs: tuple[str, str]) -> list[stage_diff.Stage]:
    """Build stages from `(name, kind)` pairs, so each case reads as a pipeline."""
    how = {"adds": _adds, "removes": _removes, "identity": _identity}
    return [stage_diff.Stage(name=name, apply=how[kind]) for name, kind in pairs]


def every_stage_is_reported(out: list[str]) -> int:
    """Check the census has one row per stage, in order."""
    steps = stage_diff.run(_SOURCE, _stages(("first", "adds"), ("second", "identity")))
    if [step.name for step in steps] != ["first", "second"]:
        out.append(f"selftest: the stages are {[s.name for s in steps]!r}")
        return 1
    return 0


def a_stage_receives_the_previous_output(out: list[str]) -> int:
    """Check the artefact is THREADED, not re-read from the source.

    ⚑⚑ THE WHOLE POINT IS COMPOSITION. A census that handed each stage the original input would
    report what each does IN ISOLATION — which is exactly the reading a per-stage suite already
    gives, and exactly the one that missed the thirteen files.
    """
    steps = stage_diff.run(_SOURCE, _stages(("first", "adds"), ("second", "identity")))
    if steps[1].before != steps[0].after:
        out.append("selftest: the second stage did not receive the first's output")
        return 1
    return 0


def a_changing_stage_is_named(out: list[str]) -> int:
    """Check `changed_at` names the stage that altered the artefact."""
    steps = stage_diff.run(_SOURCE, _stages(("quiet", "identity"), ("noisy", "adds")))
    if stage_diff.changed_at(steps) != ("noisy",):
        out.append(f"selftest: changed_at is {stage_diff.changed_at(steps)!r}")
        return 1
    return 0


def an_unchanged_stage_is_not_named(out: list[str]) -> int:
    """Check a stage that does nothing is reported as unchanged, not omitted.

    ⚑ IT STILL GETS A ROW. A stage absent from the census is indistinguishable from one that did
    not run, which is the absence-versus-unmeasured collapse this repo names repeatedly.
    """
    steps = stage_diff.run(_SOURCE, _stages(("quiet", "identity")))
    if not steps:
        out.append("selftest: a no-op stage produced no row")
        return 1
    if steps[0].changed:
        out.append("selftest: a no-op stage was reported as changed")
        return 1
    return 0


def the_stage_that_removed_something_is_named(out: list[str]) -> int:
    """Check `lost_at` names the removing stage — THE THIRTEEN-FILE ARM.

    ⚑⚑⚑ THE READING THAT SETTLED A REAL INCIDENT. A transform added an import and a later fixer
    removed it; end-to-end the artefact simply never had it, and no output could say which stage
    was responsible. This is the question `record_migrate` could not answer about itself.
    """
    steps = stage_diff.run(_SOURCE, _stages(("keeps", "identity"), ("drops", "removes")))
    if stage_diff.lost_at(steps, _NEEDLE) != ("drops",):
        out.append(f"selftest: lost_at is {stage_diff.lost_at(steps, _NEEDLE)!r}")
        return 1
    return 0


def a_needle_never_present_is_not_reported_as_lost(out: list[str]) -> int:
    """Check absence throughout is not mistaken for removal.

    ⚑ NEVER-HAD-IT AND LOST-IT ARE DIFFERENT FINDINGS with different next actions — the first
    sends a reader to the producer, the second to the stage that took it away.
    """
    steps = stage_diff.run(_SOURCE, _stages(("drops", "removes")))
    if stage_diff.lost_at(steps, "nonesuch"):
        out.append("selftest: an absent needle was reported as lost")
        return 1
    return 0


def the_stage_that_added_something_is_named(out: list[str]) -> int:
    """Check `gained_at` names the adding stage — the other direction."""
    steps = stage_diff.run(_SOURCE, _stages(("adds", "adds")))
    if stage_diff.gained_at(steps, "delta") != ("adds",):
        out.append(f"selftest: gained_at is {stage_diff.gained_at(steps, 'delta')!r}")
        return 1
    return 0


def a_stage_reports_its_line_delta(out: list[str]) -> int:
    """Check the signed line change is available without reading the diff."""
    steps = stage_diff.run(_SOURCE, _stages(("adds", "adds"), ("drops", "removes")))
    if steps[0].delta != _ONE:
        out.append(f"selftest: an adding stage reports delta {steps[0].delta}")
        return 1
    if steps[1].delta != -_ONE:
        out.append(f"selftest: a removing stage reports delta {steps[1].delta}")
        return 1
    return 0


def a_diff_is_bounded_per_stage(out: list[str]) -> int:
    """Check one stage's diff cannot consume the whole report.

    ⚑ A FORMATTER THAT REWRITES EVERYTHING would otherwise hide the one-line change a later stage
    made — the reading this instrument exists to produce.
    """

    def _rewrites(text: str) -> str:
        del text
        return "".join(f"line {n}\n" for n in range(200))

    steps = stage_diff.run(_SOURCE, [stage_diff.Stage(name="rewrites", apply=_rewrites)])
    if len(steps[0].diff(limit=_LIMIT)) > _LIMIT:
        out.append(f"selftest: the diff is {len(steps[0].diff(limit=_LIMIT))} line(s)")
        return 1
    return 0


def the_holds_pair_shows_both_sides(out: list[str]) -> int:
    """Check `holds` reports input AND output presence — the pair that names a removal."""
    steps = stage_diff.run(_SOURCE, _stages(("drops", "removes")))
    was, now = steps[0].holds(_NEEDLE)
    if (was, now) != (stage_diff.PRESENT, stage_diff.ABSENT):
        out.append(f"selftest: holds reports ({was}, {now})")
        return 1
    return 0


def the_render_names_what_changed(out: list[str]) -> int:
    """Check the rendered census names the changing stage and refuses to call it wrong."""
    steps = stage_diff.run(_SOURCE, _stages(("quiet", "identity"), ("drops", "removes")))
    text = stage_diff.render(steps, needles=(_NEEDLE,))
    if "drops" not in text:
        out.append("selftest: the render does not name the changing stage")
        return 1
    # ⚑ ASSERTED ON A FRAGMENT THAT SURVIVES THE WRAP, AND IN THE CASE THE RENDERER USES. The
    # caveat spans a line break, so matching the whole sentence tests the LINE WIDTH rather than
    # the claim. ⚑⚑ AND THE FIRST FIX HERE WAS MADE ON A GUESS: I attributed the failure to the
    # wrap and shortened the needle, without reading the renderer — which emits `CULPRIT` in
    # CAPS. One `--source` call settled what two edits could not.
    if "CULPRIT" not in text:
        out.append("selftest: the render does not carry the not-a-verdict caveat")
        return 1
    return 0


def an_empty_pipeline_is_empty_not_an_error(out: list[str]) -> int:
    """Check zero stages yields zero rows rather than raising."""
    if stage_diff.run(_SOURCE, []):
        out.append("selftest: an empty pipeline produced rows")
        return 1
    return 0


_ARMS = (
    every_stage_is_reported,
    a_stage_receives_the_previous_output,
    a_changing_stage_is_named,
    an_unchanged_stage_is_not_named,
    the_stage_that_removed_something_is_named,
    a_needle_never_present_is_not_reported_as_lost,
    the_stage_that_added_something_is_named,
    a_stage_reports_its_line_delta,
    a_diff_is_bounded_per_stage,
    the_holds_pair_shows_both_sides,
    the_render_names_what_changed,
    an_empty_pipeline_is_empty_not_an_error,
)

_CASE_COUNT = 1 + 1 + 1 + 2 + 1 + 1 + 1 + 2 + 1 + 1 + 2 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"stage-diff selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"stage-diff selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
