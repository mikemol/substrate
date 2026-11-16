#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.worklist_engine`: locating, refusing, summarising — none of them spawn.

⚑⚑⚑ NOT ONE ARM RUNS THE ENGINE, AND THAT IS THE PROPERTY BEING DEMONSTRATED RATHER THAN A
LIMITATION BEING WORKED AROUND. The superseded module reads `PAPERKIT` and `PAPERKIT_TMPDIR` at
MODULE SCOPE, so its search path was frozen by whichever importer arrived first and no case could
vary it without reimporting — which is why the locate/refuse behaviour went unchecked for its whole
life. Every environment read here is a defaulted parameter, so both arms of every decision are
reachable offline, with no checkout present and no child process.

⚑⚑ THE REFUSAL ARM ASSERTS THE MESSAGE NAMES WHERE IT LOOKED, not merely that a miss was reported.
The two causes of a miss — nothing cloned, versus a `PAPERKIT` pointing somewhere stale — need
opposite fixes and are indistinguishable from a bare flag. A case checking only `found is False`
would pass on a refusal nobody can act on.

⚑⚑ THE SUMMARISER IS DRIVEN WITH A VERDICT THAT IS NOT THE LAST LINE. That is the exact defect
found in `gate_status.run_gate`, which kept `tail[-1]` while the ratchet family printed its hint
last — so a transcript whose verdict happens to end it would pass on a `tail`-based implementation
and prove nothing. The fixture deliberately puts working detail after the verdict.

⚑ THE SANDBOX ARM CHECKS THE NEGATIVE CASE TOO. Only Delta needs scratch; an implementation that
minted a temp directory for every entry point passes any arm that only watches Delta, and that
over-eager version is the one that actually shipped and filled the volume.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from mikemol.witness import witness_family

from substrate import suite_emit, worklist_engine, worklist_paths


def a_pinned_checkout_is_located_when_it_carries_the_marker(out: list[str]) -> int:
    """Check that a directory holding `paperkit/gate.py` is found, and reported as found.

    ⚑ THE MARKER IS WHAT MAKES A DIRECTORY A CHECKOUT, not its name. A locator keyed on the
    directory being called `paperkit` would accept an empty directory with the right name and then
    fail at spawn, which reports the wrong cause one step later.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "paperkit").mkdir()
        (root / worklist_engine.MARKER).write_text("", encoding="utf-8")
        got = worklist_engine.locate(pin=str(root))
        if got.root != root:
            out.append(f"selftest: a pinned checkout resolved to {got.root!r}")
            bad += 1
        if not got.found:
            out.append("selftest: a located checkout reports found=False")
            bad += 1
    return bad


def a_directory_without_the_marker_is_not_a_checkout(out: list[str]) -> int:
    """Check that an existing directory lacking `paperkit/gate.py` is rejected.

    ⚑ THE DISCRIMINATOR AGAINST A LOCATOR THAT ONLY TESTS `is_dir()`. A stale `PAPERKIT` usually
    points at a directory that still EXISTS — an old checkout, a renamed tree — so existence is
    precisely the test that cannot tell the failure case from the success one.
    """
    with tempfile.TemporaryDirectory() as tmp:
        got = worklist_engine.locate(pin=tmp, conventional="")
        if got.found:
            out.append(f"selftest: a directory with no marker was accepted as {got.root!r}")
            return 1
    return 0


def the_refusal_names_every_place_it_looked(out: list[str]) -> int:
    """Check that a miss reports the candidates tried and how to fix it.

    ⚑⚑ A BARE "NOT FOUND" IS UNACTIONABLE — see the module note. This asserts the CONTENT: the
    pinned path, the environment variable to set, and the conventional location all appear.
    """
    bad = 0
    got = worklist_engine.locate(pin="/nonexistent-pin-for-a-case", conventional="/nonexistent-alt")
    if got.found:
        out.append("selftest: two nonexistent candidates were reported as found")
        return 1
    why = got.why
    for needle in ("/nonexistent-pin-for-a-case", worklist_engine.PIN, "/nonexistent-alt"):
        if needle not in why:
            out.append(f"selftest: the refusal does not mention {needle!r}")
            bad += 1
    if got.tried != (Path("/nonexistent-pin-for-a-case"), Path("/nonexistent-alt")):
        out.append(f"selftest: the tried candidates are {got.tried!r}")
        bad += 1
    return bad


def a_located_engine_has_no_refusal_text(out: list[str]) -> int:
    """Check that `why` is empty when a checkout was found — the positive control.

    ⚑ WITHOUT THIS ARM, A `why` THAT ALWAYS RETURNED ITS MESSAGE would satisfy the refusal arm and
    report a working engine as broken. A diagnostic that reports offenders needs a case proving it
    can also report none.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "paperkit").mkdir()
        (root / worklist_engine.MARKER).write_text("", encoding="utf-8")
        got = worklist_engine.locate(pin=str(root))
        if got.why:
            out.append(f"selftest: a located engine still explains a miss: {got.why!r}")
            return 1
    return 0


def the_pin_is_preferred_over_the_conventional_location(out: list[str]) -> int:
    """Check that an explicit pin wins when both candidates carry the marker.

    ⚑ THE WHOLE REASON THE PIN EXISTS is selecting a different engine version without editing the
    file. An implementation that searched the conventional location first would silently ignore the
    pin whenever a default checkout also existed — which is the common case, so the bug would be
    invisible exactly where it matters.
    """
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        pinned, other = base / "pinned", base / "other"
        for root in (pinned, other):
            (root / "paperkit").mkdir(parents=True)
            (root / worklist_engine.MARKER).write_text("", encoding="utf-8")
        got = worklist_engine.locate(pin=str(pinned), conventional=str(other))
        if got.root != pinned:
            out.append(f"selftest: the pin lost to the conventional location ({got.root!r})")
            return 1
    return 0


def a_refused_run_reports_cannot_measure_rather_than_success(out: list[str]) -> int:
    """Check that running without an engine yields the refusal code, not a clean exit.

    ⚑⚑ AN UNMEASURABLE CHECK THAT EXITS 0 IS INDISTINGUISHABLE FROM A PASSING ONE, and this repo
    reads a green gate as a fact about the tree. So the absent-engine case gets its own code, and
    the transcript carries the reason rather than being empty.
    """
    missing = worklist_engine.Located(root=None, tried=(Path("/nowhere"),))
    got = worklist_engine.run(worklist_engine.Invocation(entry="gate.py"), located=missing)
    bad = 0
    if got.code != worklist_engine.CANNOT_MEASURE:
        out.append(f"selftest: a refused run exited {got.code}")
        bad += 1
    if got.located:
        out.append("selftest: a refused run reports the engine as located")
        bad += 1
    if "/nowhere" not in got.text:
        out.append("selftest: a refused run does not carry the reason")
        bad += 1
    return bad


def only_the_grading_entry_point_is_sandboxed(out: list[str]) -> int:
    """Check that Delta needs scratch and the reporting entry points do not.

    ⚑⚑ THE OVER-EAGER VERSION IS THE ONE THAT SHIPPED AND FILLED THE VOLUME. It redirected TMPDIR
    for every entry and created the directory eagerly, so `--figures` and `--items` — which spawn
    nothing — still minted a scratch dir. Watching only Delta would pass on exactly that.
    """
    bad = 0
    if not worklist_engine.Invocation(entry="discriminate.py").sandboxed:
        out.append("selftest: the grading entry point is not sandboxed")
        bad += 1
    for entry in ("gate.py", "figures.py", "items.py"):
        if worklist_engine.Invocation(entry=entry).sandboxed:
            out.append(f"selftest: {entry} was sandboxed and needs no scratch")
            bad += 1
    return bad


def an_unsandboxed_entry_creates_no_scratch_tree(out: list[str]) -> int:
    """Check that entering the sandbox for a reporting entry point makes no directory.

    ⚑ THIS IS THE ARM THAT WATCHES THE FILESYSTEM RATHER THAN THE PREDICATE. `sandboxed` could be
    correct while the context manager created the tree anyway — the predicate and the effect are
    separate claims, and it was the effect that filled the disk.
    """
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "scratch-that-should-not-appear"
        request = worklist_engine.Invocation(entry="gate.py", scratch=base)
        with worklist_engine.sandbox(request):
            pass
        if base.exists():
            out.append("selftest: an unsandboxed entry created a scratch tree")
            return 1
    return 0


def a_sandboxed_run_removes_its_scratch_tree_on_the_way_out(out: list[str]) -> int:
    """Check that the sandbox redirects TMPDIR and tears the tree down afterwards.

    ⚑⚑ NOTHING WAS DELETING IT BETWEEN RUNS, AND THAT IS WHY THE VOLUME FILLED TWICE. Delta copies
    the project once per mutated input, so the tree grows with (project size x input count). The
    arm asserts both halves: the child is pointed at the tree, and the tree is gone at the end.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "scratch"
        request = worklist_engine.Invocation(entry="discriminate.py", scratch=base)
        with worklist_engine.sandbox(request, keep=False) as env:
            made = Path(env["TMPDIR"])
            if not made.is_dir():
                out.append("selftest: the sandbox did not create the tree it pointed TMPDIR at")
                bad += 1
            if base not in made.parents:
                out.append(f"selftest: the sandbox made {made!r} outside the chosen scratch root")
                bad += 1
        if made.exists():
            out.append("selftest: the sandbox tree survived the context")
            bad += 1
    return bad


def the_verdict_lines_are_selected_not_the_tail(out: list[str]) -> int:
    """Check that the summariser picks engine-tagged lines wherever they sit.

    ⚑⚑ THE FIXTURE PUTS WORKING DETAIL AFTER THE VERDICT ON PURPOSE — see the module note. A
    `tail[-1]` implementation returns the trailing detail and drops the verdict entirely, which is
    the defect this replaced; a transcript ending in its verdict could not tell the two apart.
    """
    transcript = (
        "working detail nobody needs\n"
        f"{worklist_engine.VERDICT_PREFIX}gate: 3 of 4 items warranted\n"
        "trailing hint printed last\n"
        f"{worklist_engine.VERDICT_PREFIX}gate: REFUSED\n"
        "more trailing detail\n"
    )
    got = worklist_engine.verdicts(transcript)
    expected = (
        f"{worklist_engine.VERDICT_PREFIX}gate: 3 of 4 items warranted\n"
        f"{worklist_engine.VERDICT_PREFIX}gate: REFUSED"
    )
    if got != expected:
        out.append(f"selftest: the summariser returned {got!r}")
        return 1
    return 0


def a_transcript_with_no_verdict_summarises_to_nothing(out: list[str]) -> int:
    """Check that working detail alone yields an empty summary — the negative control.

    ⚑ WITHOUT THIS, A SUMMARISER THAT RETURNED ITS INPUT UNCHANGED would pass the selection arm on
    a transcript that happened to be all verdicts. An empty result here is the fact that the prefix
    is actually being tested.
    """
    got = worklist_engine.verdicts("nothing tagged here\nnor here\n")
    if got:
        out.append(f"selftest: an untagged transcript summarised to {got!r}")
        return 1
    return 0


def emitting_to_a_file_writes_it_and_reports_where(out: list[str]) -> int:
    """Check that a named destination is written, newline-terminated, and named back.

    ⚑ THE REPORT WAS BEING PRODUCED CORRECTLY WHILE THE SPOOL COULD NOT HOLD IT, so the tool looked
    broken when the volume was. Naming the destination is the repair, and the caller needs the
    path back to tell the next command where to read.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "report.txt"
        said = worklist_engine.emit("a body with no trailing newline", out=target)
        if target.read_text(encoding="utf-8") != "a body with no trailing newline\n":
            out.append("selftest: the emitted file is not newline-terminated")
            bad += 1
        if str(target) not in said:
            out.append(f"selftest: emit did not name its destination: {said!r}")
            bad += 1
    return bad


def emitting_without_a_destination_returns_the_body(out: list[str]) -> int:
    """Check that an unnamed destination hands the text back rather than printing it.

    ⚑ THE TRANSCRIPT IS A VALUE, NOT A SIDE EFFECT. Returning it is what lets a caller choose where
    it goes; a version that printed would make this arm assert on captured stdout, which is the
    coupling the module removed.
    """
    got = worklist_engine.emit("already terminated\n")
    if got != "already terminated\n":
        out.append(f"selftest: emit returned {got!r}")
        return 1
    return 0


def an_invocation_defaults_to_the_live_project(out: list[str]) -> int:
    """Check that an unset project resolves to the worklist and an explicit one is honoured.

    ⚑ THE INJECTED HALF IS WHAT MAKES THIS SUITE POSSIBLE. A module hardcoding its project could
    only ever be checked against the live tree, so the arm drives a foreign path and asserts it is
    used rather than ignored.
    """
    bad = 0
    if worklist_engine.Invocation(entry="gate.py").where() != worklist_paths.PROJECT:
        out.append("selftest: an unset project does not resolve to the live worklist")
        bad += 1
    foreign = Path("/nonexistent-project-for-a-case")
    if worklist_engine.Invocation(entry="gate.py", project=foreign).where() != foreign:
        out.append("selftest: an explicit project was ignored")
        bad += 1
    return bad


def the_child_environment_pins_the_located_engine(out: list[str]) -> int:
    """Check that a located engine is exported to the child, and a miss changes nothing.

    ⚑ THE ENVIRONMENT A CHILD IS HANDED IS A DECISION WORTH ASSERTING ON ITS OWN. Folding it into
    `run` would make it observable only by spawning — the coupling that left the superseded
    module's behaviour unpinned.
    """
    bad = 0
    found = worklist_engine.Located(root=Path("/some/checkout"), tried=())
    if worklist_engine.environment(found, env={}).get(worklist_engine.PIN) != "/some/checkout":
        out.append("selftest: a located engine is not exported to the child")
        bad += 1
    missing = worklist_engine.Located(root=None, tried=())
    if worklist_engine.PIN in worklist_engine.environment(missing, env={}):
        out.append("selftest: an unlocated engine still exported a pin")
        bad += 1
    return bad


def the_scratch_root_prefers_an_explicit_override(out: list[str]) -> int:
    """Check that a named scratch wins, and the default sits under the repository root.

    ⚑ PLACEMENT IS SOMETHING THE CALLER MAY NEED TO CONTROL, in the same spirit as `AGDA_MB`
    pinning a membudget lease. A tool whose only answer is "wherever the environment pointed"
    cannot be aimed — and on this box the default it inherited was a small shared tmpfs.
    """
    bad = 0
    chosen = Path("/an/explicit/scratch")
    if worklist_engine.scratch_root(chosen) != chosen:
        out.append("selftest: an explicit scratch root was ignored")
        bad += 1
    default = worklist_engine.scratch_root()
    if worklist_paths.ROOT not in default.parents and default.parent != worklist_paths.ROOT:
        out.append(f"selftest: the default scratch root is {default!r}, not under the tree")
        bad += 1
    return bad


FAMILY = witness_family.of(
    key="worklist_engine",
    apex="the engine boundary locates a checkout by its marker rather than its name, refuses by "
    "naming every place it looked instead of reporting clean, sandboxes only the entry point "
    "that needs scratch and removes that tree on the way out, and selects the engine's "
    "verdict lines wherever they sit rather than keeping the tail",
    subject="the subprocess boundary `substrate.worklist_engine` owns, exercised without spawning",
    members=(
        witness_family.Member(
            name="a_pinned_checkout_is_located_when_it_carries_the_marker",
            claim="a directory holding the marker is found and reported as found",
            cases=2,
        ),
        witness_family.Member(
            name="a_directory_without_the_marker_is_not_a_checkout",
            claim="an existing directory lacking the marker is rejected",
        ),
        witness_family.Member(
            name="the_refusal_names_every_place_it_looked",
            claim="a miss reports the candidates tried and how to fix it",
            cases=4,
        ),
        witness_family.Member(
            name="a_located_engine_has_no_refusal_text",
            claim="the refusal explanation is empty when a checkout was found",
            premises=("the_refusal_names_every_place_it_looked",),
        ),
        witness_family.Member(
            name="the_pin_is_preferred_over_the_conventional_location",
            claim="an explicit pin wins when both candidates carry the marker",
        ),
        witness_family.Member(
            name="a_refused_run_reports_cannot_measure_rather_than_success",
            claim="running without an engine yields the refusal code and carries the reason",
            cases=3,
        ),
        witness_family.Member(
            name="only_the_grading_entry_point_is_sandboxed",
            claim="the grading entry needs scratch and the reporting entries do not",
            cases=4,
        ),
        witness_family.Member(
            name="an_unsandboxed_entry_creates_no_scratch_tree",
            claim="entering the sandbox for a reporting entry makes no directory",
            premises=("only_the_grading_entry_point_is_sandboxed",),
        ),
        witness_family.Member(
            name="a_sandboxed_run_removes_its_scratch_tree_on_the_way_out",
            claim="the sandbox redirects TMPDIR into the chosen root and tears the tree down",
            cases=3,
        ),
        witness_family.Member(
            name="the_verdict_lines_are_selected_not_the_tail",
            claim="engine-tagged lines are picked wherever they sit in the transcript",
        ),
        witness_family.Member(
            name="a_transcript_with_no_verdict_summarises_to_nothing",
            claim="working detail alone yields an empty summary",
            premises=("the_verdict_lines_are_selected_not_the_tail",),
        ),
        witness_family.Member(
            name="emitting_to_a_file_writes_it_and_reports_where",
            claim="a named destination is written, newline-terminated, and named back",
            cases=2,
        ),
        witness_family.Member(
            name="emitting_without_a_destination_returns_the_body",
            claim="an unnamed destination hands the text back rather than printing it",
        ),
        witness_family.Member(
            name="an_invocation_defaults_to_the_live_project",
            claim="an unset project resolves to the worklist and an explicit one is honoured",
            cases=2,
        ),
        witness_family.Member(
            name="the_child_environment_pins_the_located_engine",
            claim="a located engine is exported to the child and a miss changes nothing",
            cases=2,
        ),
        witness_family.Member(
            name="the_scratch_root_prefers_an_explicit_override",
            claim="a named scratch wins and the default sits under the repository root",
            cases=2,
        ),
    ),
)

_ARMS = (
    a_pinned_checkout_is_located_when_it_carries_the_marker,
    a_directory_without_the_marker_is_not_a_checkout,
    the_refusal_names_every_place_it_looked,
    a_located_engine_has_no_refusal_text,
    the_pin_is_preferred_over_the_conventional_location,
    a_refused_run_reports_cannot_measure_rather_than_success,
    only_the_grading_entry_point_is_sandboxed,
    an_unsandboxed_entry_creates_no_scratch_tree,
    a_sandboxed_run_removes_its_scratch_tree_on_the_way_out,
    the_verdict_lines_are_selected_not_the_tail,
    a_transcript_with_no_verdict_summarises_to_nothing,
    emitting_to_a_file_writes_it_and_reports_where,
    emitting_without_a_destination_returns_the_body,
    an_invocation_defaults_to_the_live_project,
    the_child_environment_pins_the_located_engine,
    the_scratch_root_prefers_an_explicit_override,
)

_CASE_COUNT = FAMILY.count

_SELF_KEY = "substrate/worklist_engine_selftest.py"


def selftest() -> int:
    """Run every arm, report by typed record, and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(_SELF_KEY, _CASE_COUNT - failures, _CASE_COUNT)


if __name__ == "__main__":
    raise SystemExit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
