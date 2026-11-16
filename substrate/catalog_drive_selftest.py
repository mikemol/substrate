#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.catalog_drive`: the driver sequences, validates first, and injects.

⚑⚑⚑ EVERY ARM RUNS WITH NO STORE, NO CORES AND NO POSTGRES, AND THAT IS THE WHOLE CLAIM. The
driver this supersedes cannot be driven at all without the `.agdai` tree built and a projection
connected, because its only entry point opens both before reaching any decision. Recording each
step as a call into a list is what makes the ORDER — the part that is actually the capability —
assertable, and it is assertable precisely because the steps arrive as arguments.

⚑⚑ THE VALIDATE-BEFORE-BUILD ARM IS THE ONE WITH TEETH, AND IT IS A NEGATIVE OBSERVATION. It
asserts the builder was NOT called when a target is mistyped. A driver that validated after
building would satisfy every other arm here while spending the two-minute walk to report a fact
it held before starting — and the failure would be invisible in the output, since the refusal
still arrives.

⚑ THE SKIP IS CHECKED AS AN ABSENT CALL, not as an absent message. A builder that ran and printed
nothing would pass a message-only check while doing the expensive work the flag exists to avoid,
which is the same absent-versus-broken collapse the drained module's `reuse_db` once made by
testing a file's existence in place of a store question.

⚑ NO ARM ASSERTS WHAT A RENDERER PRODUCES. The renderer bodies stay in `scripts/reuse_catalog.py`
with the store machinery they need; this module owns the sequence, and a case reaching for a real
catalog would be testing the half that was deliberately left behind.
"""

from __future__ import annotations

import sys

from mikemol.witness import witness_family

from substrate import catalog_drive, catalog_targets, suite_emit


class _Recorder:
    """A step that records the targets it was asked to render, and a builder that records its run.

    ⚑ ONE OBJECT HOLDS BOTH so an arm can assert their RELATIVE order, which is the sequencing
    claim. Two independent spies would each record faithfully and lose exactly the fact that
    distinguishes build-then-render from render-then-build.
    """

    def __init__(self) -> None:
        self.calls: list[str] = []

    def build(self) -> list[str]:
        """Stand in for the projection build, recording that it ran."""
        self.calls.append("build")
        return ["built"]

    def step(self, target: str) -> str:
        """Stand in for one render, recording which target it was handed."""
        self.calls.append(target)
        return f"rendered {target}"


def the_build_runs_before_every_render(out: list[str]) -> int:
    """Check that the injected build runs first, then each target in declared order.

    ⚑ THE ORDER IS THE CAPABILITY. Rendering before the store is built would render whatever the
    previous run left behind and report success — a stale catalog produced silently, which is the
    failure the drained module's own `--render-only` warning describes.
    """
    rec = _Recorder()
    msgs = catalog_drive.generate(catalog_targets.DEFAULT, build=rec.build, step=rec.step)
    bad = 0
    expected = ["build", *catalog_targets.DEFAULT]
    if rec.calls != expected:
        out.append(f"selftest: the driver called {rec.calls!r}, not {expected!r}")
        bad += 1
    if msgs[0] != "built":
        out.append("selftest: the build's summary is not first in the returned messages")
        bad += 1
    if len(msgs) != len(expected):
        out.append(f"selftest: {len(msgs)} summaries for {len(expected)} steps")
        bad += 1
    return bad


def omitting_the_builder_skips_the_build(out: list[str]) -> int:
    """Check that passing no builder renders without building.

    ⚑⚑ THIS IS CHECKED AS AN ABSENT CALL, NOT AN ABSENT MESSAGE. A builder that ran and returned
    nothing would pass a message-only check while doing the expensive work the skip exists to
    avoid — absent read as broken, at the step rather than the census.
    """
    rec = _Recorder()
    msgs = catalog_drive.generate((catalog_targets.INDEX,), step=rec.step)
    bad = 0
    if "build" in rec.calls:
        out.append("selftest: the build ran although no builder was passed")
        bad += 1
    if rec.calls != [catalog_targets.INDEX]:
        out.append(f"selftest: the skipped-build path called {rec.calls!r}")
        bad += 1
    if msgs != ["rendered index"]:
        out.append(f"selftest: the skipped-build path returned {msgs!r}")
        bad += 1
    return bad


def an_unknown_target_refuses_before_the_build_runs(out: list[str]) -> int:
    """Check that a mistyped target refuses without spending the build.

    ⚑⚑ THE NEGATIVE OBSERVATION IS THE POINT. A driver validating after the build satisfies every
    other arm here while spending the expensive half to report a fact it already held, and the
    refusal still arrives so the output looks identical. Asserting the builder did NOT run is the
    only way that difference is visible.
    """
    rec = _Recorder()
    bad = 0
    try:
        catalog_drive.generate(("sitmap",), build=rec.build, step=rec.step)
    except ValueError:
        pass
    else:
        out.append("selftest: an unknown target was ACCEPTED by the driver")
        bad += 1
    if rec.calls:
        out.append(f"selftest: the driver did work before refusing: {rec.calls!r}")
        bad += 1
    return bad


def a_subset_request_renders_only_that_subset(out: list[str]) -> int:
    """Check that asking for one target invokes the step once.

    ⚑ WITHOUT THIS, A DRIVER IGNORING ITS TARGETS AND ALWAYS RENDERING EVERYTHING would pass the
    ordering arm. Two of the three consumers ask for exactly one catalog, so this is the majority
    invocation rather than an edge case.
    """
    bad = 0
    for one in catalog_targets.DEFAULT:
        rec = _Recorder()
        catalog_drive.generate((one,), step=rec.step)
        if rec.calls != [one]:
            out.append(f"selftest: requesting {one!r} called {rec.calls!r}")
            bad += 1
    return bad


def render_plans_before_invoking_any_step(out: list[str]) -> int:
    """Check that `render` refuses a bad target without invoking the step for the good ones.

    ⚑ THE SUPERSEDED LOOP INDEXES ITS RENDERER TABLE INSIDE THE ITERATION, so a bad fifth target
    is discovered only after four catalogs have been written — work that must then be judged as
    partial rather than simply not done. Refusing with nothing written is the repair.
    """
    rec = _Recorder()
    bad = 0
    try:
        catalog_drive.render((catalog_targets.INDEX, "usge"), rec.step)
    except ValueError:
        pass
    else:
        out.append("selftest: render ACCEPTED an unknown target")
        bad += 1
    if rec.calls:
        out.append(f"selftest: render invoked steps before refusing: {rec.calls!r}")
        bad += 1
    return bad


def the_driver_renders_in_declared_order_not_request_order(out: list[str]) -> int:
    """Check that a backwards request is still rendered in the declared order.

    ⚑ WITHOUT THIS ARM A DRIVER PASSING ARGV STRAIGHT THROUGH would satisfy the sequencing case,
    which drives targets already in order. The reversed request is what separates "the plan is
    consulted" from "the plan happens to agree".
    """
    rec = _Recorder()
    catalog_drive.generate(tuple(reversed(catalog_targets.DEFAULT)), step=rec.step)
    if rec.calls != list(catalog_targets.DEFAULT):
        out.append(f"selftest: a reversed request rendered as {rec.calls!r}")
        return 1
    return 0


def a_step_that_refuses_propagates_rather_than_being_swallowed(out: list[str]) -> int:
    """Check that a refusing step's exception reaches the caller.

    ⚑⚑ THE DRAINED MODULE'S TIER REFUSAL IS A `SystemExit`, and it exists because the unported
    path once wrote a complete answer to a store nobody read and reported success. A driver that
    caught a step's refusal and continued would restore exactly that: catalogs reported rendered
    while one of them was not.
    """

    def refusing(_target: str) -> str:
        msg = "the tier is unported"
        raise SystemExit(msg)

    try:
        catalog_drive.generate((catalog_targets.INDEX,), step=refusing)
    except SystemExit:
        return 0
    out.append("selftest: a refusing step was SWALLOWED by the driver")
    return 1


FAMILY = witness_family.of(
    key="catalog_drive",
    apex="the driver validates its targets before spending the build, runs the injected build "
    "once ahead of every render, renders exactly the requested subset in declared order, "
    "skips the build when none is injected, and lets a refusing step propagate",
    subject="the sequence `substrate.catalog_drive` imposes, driven offline with recorded steps",
    members=(
        witness_family.Member(
            name="the_build_runs_before_every_render",
            claim="the injected build runs first, then each target in declared order",
            cases=3,
        ),
        witness_family.Member(
            name="omitting_the_builder_skips_the_build",
            claim="passing no builder renders without building",
            cases=3,
        ),
        witness_family.Member(
            name="an_unknown_target_refuses_before_the_build_runs",
            claim="a mistyped target refuses without spending the build",
            cases=2,
        ),
        witness_family.Member(
            name="a_subset_request_renders_only_that_subset",
            claim="asking for one target invokes the step once",
            cases=5,
        ),
        witness_family.Member(
            name="render_plans_before_invoking_any_step",
            claim="a bad target refuses with no step invoked for the good ones",
            cases=2,
        ),
        witness_family.Member(
            name="the_driver_renders_in_declared_order_not_request_order",
            claim="a backwards request is still rendered in the declared order",
            premises=("the_build_runs_before_every_render",),
        ),
        witness_family.Member(
            name="a_step_that_refuses_propagates_rather_than_being_swallowed",
            claim="a refusing step's exception reaches the caller",
        ),
    ),
)

_ARMS = (
    the_build_runs_before_every_render,
    omitting_the_builder_skips_the_build,
    an_unknown_target_refuses_before_the_build_runs,
    a_subset_request_renders_only_that_subset,
    render_plans_before_invoking_any_step,
    the_driver_renders_in_declared_order_not_request_order,
    a_step_that_refuses_propagates_rather_than_being_swallowed,
)

_CASE_COUNT = FAMILY.count

_SELF_KEY = "substrate/catalog_drive_selftest.py"


def selftest() -> int:
    """Run every arm, report by typed record, and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(_SELF_KEY, _CASE_COUNT - failures, _CASE_COUNT)


if __name__ == "__main__":
    raise SystemExit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
