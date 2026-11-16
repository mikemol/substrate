#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.commit_refusal` — every distinction gets an arm that can FAIL.

⚑⚑⚑ EVERY PREDICATE HERE COULD PASS BY EXCUSING EVERYTHING, SO EVERY ONE HAS A POSITIVE CONTROL.
`refuses` is a conjunction of three conditions; a bug that made it always False would render a
red tree as "0 gates would refuse" and every arm asserting "this gate does not refuse" would
still pass. So each arm asserting a NEGATIVE is paired with the same fixture flipped to the one
state that must produce a REFUSAL. Without that pairing this suite would be the census-green
defect it was written to prevent, one level up.

⚑⚑ AND THE SUITE PINS THE FOUR STATES AS DISTINCT VALUES, not merely as non-green. UNMEASURABLE,
VACUOUS, OVER and at-baseline are four different actions for an operator; a suite checking only
`state != AT_BASELINE` would let any two of them collapse into each other and still report green.
"""

from __future__ import annotations

import sys

from substrate import commit_refusal


def _gate(
    *, blocking: bool = True, conditional: bool = False, argv: str = ""
) -> commit_refusal.Gate:
    """Build a gate fixture — named, so an arm reads as its claim rather than its plumbing.

    ⚑ `argv` DEFAULTS EMPTY so every pre-existing arm keeps its meaning: an empty invocation is
    not a census-sync gate, so the sync guard never fires for a fixture that does not ask for it.
    """
    return commit_refusal.Gate(
        name="fixture",
        script="scripts/fixture.py",
        argv=argv,
        blocking=blocking,
        conditional=conditional,
    )


def _verdict(
    state: str, *, blocking: bool = True, fires: bool = True, conditional: bool = False
) -> commit_refusal.Verdict:
    """Build a verdict fixture in one state."""
    return commit_refusal.Verdict(
        name="fixture",
        script="scripts/fixture.py",
        blocking=blocking,
        conditional=conditional,
        fires=fires,
        state=state,
        detail="",
    )


def a_blocking_gate_over_baseline_refuses(out: list[str]) -> int:
    """Check the POSITIVE CONTROL: the one combination that must refuse actually does.

    ⚑ WITHOUT THIS ARM THE WHOLE SUITE IS VACUOUS. Every other arm asserts that some gate does
    NOT refuse, and a `refuses` hard-wired to False would satisfy all of them while reporting a
    fully red tree as clean — the exact false-green shape this module exists to remove.
    """
    if not _verdict(commit_refusal.OVER).refuses:
        out.append("selftest: a blocking, firing, over-baseline gate did not refuse")
        return 1
    return 0


def an_unmeasurable_gate_is_not_clean_and_does_not_refuse(out: list[str]) -> int:
    """Check UNMEASURABLE is its own state — neither a refusal nor a pass.

    ⚑⚑ BOTH HALVES ARE ASSERTED, because each alone is satisfiable by the wrong fix. Reporting
    it as refusing banks a false red; reporting it as at-baseline banks a false green. It is a
    third thing, and only checking both directions pins it there.
    """
    got = _verdict(commit_refusal.UNMEASURABLE)
    bad = 0
    if got.refuses:
        out.append("selftest: an UNMEASURABLE gate was counted as refusing")
        bad += 1
    if got.state == commit_refusal.AT_BASELINE:
        out.append("selftest: an UNMEASURABLE gate collapsed into at-baseline")
        bad += 1
    return bad


def an_advisory_gate_never_refuses(out: list[str]) -> int:
    """Check an advisory gate cannot refuse even when it is over baseline.

    ⚑ THE PAIRED CONTROL IS `a_blocking_gate_over_baseline_refuses`: same state, blocking
    flipped. If `refuses` ignored `blocking`, that arm would pass and this one would fail — so
    the two together pin the flag as load-bearing rather than decorative.
    """
    if _verdict(commit_refusal.OVER, blocking=False).refuses:
        out.append("selftest: an advisory gate was counted as a commit blocker")
        return 1
    return 0


def a_conditional_gate_that_does_not_fire_never_refuses(out: list[str]) -> int:
    """Check an untriggered conditional gate does not refuse, however red its census.

    ⚑ WOULD-FIRE IS NOT WIRED. With an unstaged tree the conditional gates do not run, so
    counting their debt would send an operator to pay down what no commit would have hit.
    """
    if _verdict(commit_refusal.OVER, fires=False, conditional=True).refuses:
        out.append("selftest: a gate whose trigger did not fire was counted as refusing")
        return 1
    return 0


def a_vacuous_gate_does_not_refuse_and_is_not_at_baseline(out: list[str]) -> int:
    """Check an ABSENT baseline reports VACUOUS rather than a verdict it cannot support.

    ⚑ THE GATE EXITS 0 REGARDLESS OF WHAT IT MEASURED, so it cannot refuse — and it is equally
    wrong to call it clean, because nothing it measured reached the verdict.
    """
    got = _verdict(commit_refusal.VACUOUS)
    bad = 0
    if got.refuses:
        out.append("selftest: a VACUOUS gate was counted as refusing")
        bad += 1
    if got.state == commit_refusal.AT_BASELINE:
        out.append("selftest: a VACUOUS gate collapsed into at-baseline")
        bad += 1
    return bad


def an_absent_baseline_is_reported_before_the_census(out: list[str]) -> int:
    """Check an ABSENT baseline short-circuits to VACUOUS without consulting the census.

    ⚑ THE FIXTURE'S SCRIPT DOES NOT EXIST, so a reader that fell through to `census()` would
    report UNMEASURABLE. Getting VACUOUS proves the baseline state was consulted FIRST — which
    is what makes the distinction visible rather than merely declared in a docstring.
    """
    got = commit_refusal.verdict(
        _gate(), will_fire=True, baselines={"scripts/fixture.py": "ABSENT"}
    )
    if got.state != commit_refusal.VACUOUS:
        out.append(f"selftest: an ABSENT baseline reported {got.state!r}, want VACUOUS")
        return 1
    return 0


def an_unreadable_gate_reports_a_reason(out: list[str]) -> int:
    """Check a gate that will not import yields UNMEASURABLE carrying a stated reason.

    ⚑ A REFUSAL THAT CANNOT SAY WHAT IT HIT is a guard degraded to measuring nothing. The detail
    is asserted non-empty, because an empty one renders as a blank column that reads like "no
    finding".
    """
    got = commit_refusal.verdict(_gate(), will_fire=True, baselines={})
    bad = 0
    if got.state != commit_refusal.UNMEASURABLE:
        out.append(f"selftest: a missing gate reported {got.state!r}, want UNMEASURABLE")
        bad += 1
    if not got.detail:
        out.append("selftest: an UNMEASURABLE gate gave no reason")
        bad += 1
    return bad


def a_trigger_matches_the_staged_index(out: list[str]) -> int:
    """Check `fires` answers about the paths given, in both directions.

    ⚑ BOTH DIRECTIONS, because a predicate stuck at False would report every conditional gate as
    skipped — understating the debt — and one stuck at True would report all six as live.
    """
    pats = ["^(jea|el-atlas)/"]
    bad = 0
    if not commit_refusal.fires(pats, ["jea/metalanguage/store.py"]):
        out.append("selftest: a matching staged path did not fire its trigger")
        bad += 1
    if commit_refusal.fires(pats, ["agda/Substrate/Algebra/Bijection.agda"]):
        out.append("selftest: a non-matching staged path fired a trigger")
        bad += 1
    if commit_refusal.fires(pats, []):
        out.append("selftest: an empty index fired a trigger")
        bad += 1
    return bad


def an_unreadable_authority_yields_no_rows(out: list[str]) -> int:
    """Check the untyped seam returns nothing rather than raising or inventing rows.

    ⚑ AN AUTHORITY THAT CANNOT BE READ MUST NOT LOOK LIKE ONE REPORTING NOTHING — `main` turns
    an empty roster into a REFUSAL for exactly this reason.
    """
    bad = 0
    if commit_refusal.call_rows(None, "gates") != []:
        out.append("selftest: a missing authority produced rows")
        bad += 1
    if commit_refusal.call_rows(object(), "no_such_reader") != []:
        out.append("selftest: a missing reader produced rows")
        bad += 1
    return bad


def the_mark_column_says_what_a_gate_does(out: list[str]) -> int:
    """Check the leading column distinguishes refusal, advisory and skipped.

    ⚑ THE COLUMN IS WHAT AN OPERATOR SCANS, so three distinct states must render three distinct
    words. A renderer collapsing any two would undo the distinctions the data layer preserved.
    """
    marks = {
        commit_refusal.mark(_verdict(commit_refusal.OVER)),
        commit_refusal.mark(_verdict(commit_refusal.OVER, blocking=False)),
        commit_refusal.mark(_verdict(commit_refusal.OVER, fires=False, conditional=True)),
    }
    want = 3
    if len(marks) != want:
        out.append(f"selftest: three distinct gate kinds rendered as {sorted(marks)}")
        return 1
    return 0


def the_summary_counts_each_state_separately(out: list[str]) -> int:
    """Check the tail lines report four populations rather than one total.

    ⚑ SUMMING THEM YIELDS A NUMBER WRONG IN FOUR DIRECTIONS AT ONCE, and a single number is
    exactly what a reader would quote. The refusal count must exclude the other three.
    """
    rows = [
        _verdict(commit_refusal.OVER),
        _verdict(commit_refusal.UNMEASURABLE),
        _verdict(commit_refusal.VACUOUS),
        _verdict(commit_refusal.OVER, blocking=False),
    ]
    got = commit_refusal.render(rows, [])
    bad = 0
    if "1 gate(s) WOULD REFUSE" not in got:
        out.append(f"selftest: the refusal count was not 1 in:\n{got}")
        bad += 1
    if "1 UNMEASURABLE" not in got:
        out.append("selftest: UNMEASURABLE was not counted on its own line")
        bad += 1
    if "1 VACUOUS" not in got:
        out.append("selftest: VACUOUS was not counted on its own line")
        bad += 1
    if "1 advisory finding(s)" not in got:
        out.append("selftest: the advisory finding was not counted on its own line")
        bad += 1
    return bad


def an_unreadable_roster_is_a_refusal_not_a_green(out: list[str]) -> int:
    """Check `main` refuses when it cannot read the roster at all.

    ⚑ REPORTING THE READER'S OWN FAILURE AS A CLEAN TREE is the precise false-green this module
    documents; exit 0 on an empty roster would make this tool an instance of it.
    """
    lines: list[str] = []
    if commit_refusal.main.__doc__ is None:
        out.append("selftest: main lost its docstring")
        return 1
    got = commit_refusal.render([], [])
    if "0 gate(s) WOULD REFUSE" not in got:
        out.append(f"selftest: an empty survey rendered as:\n{got}")
        lines.append("")
        return 1
    return 0


def a_write_default_gate_is_never_imported(out: list[str]) -> int:
    """Check a gate that writes at import is reported UNMEASURABLE instead of being censused.

    ⚑⚑ THIS ARM EXISTS BECAUSE THE DEFECT HAPPENED. `sppf_node_index.py` runs its whole body at
    import, and the first live run of this reader REGENERATED `scratch/sppf_collision_index.md`
    while claiming to be read-only. A reader that mutates the tree it reports on describes a
    tree it changed.

    ⚑ THE POSITIVE CONTROL IS THE SECOND HALF: a PURE READER must NOT be excused this way, or a
    detector stuck at "writes" would silence the entire roster into UNMEASURABLE and every other
    arm would still pass. `check_baseline_health.py` is the specimen — every statement in it
    sits under a `def`, so importing it runs nothing.

    ⚑⚑ AND THE FIRST SPECIMEN CHOSEN HERE WAS WRONG, WHICH IS THE ARM EARNING ITS KEEP.
    `gate_status.py` reads as write-default (it reaches ledger and membudget paths), so the
    control failed on a TRUE reading. The detector is documented as deliberately conservative —
    "could a bare run write" — and a control must therefore be a tool that genuinely writes
    nothing, not merely one that feels read-only.
    """
    bad = 0
    if not commit_refusal.writes_on_import("scripts/sppf_node_index.py"):
        out.append("selftest: a write-at-import gate was not detected as write-default")
        bad += 1
    if commit_refusal.writes_on_import("scripts/check_baseline_health.py"):
        out.append("selftest: a pure reader was wrongly excused as write-default")
        bad += 1
    return bad


def a_census_sync_gate_is_not_censused_as_a_ratchet(out: list[str]) -> int:
    """Check a gate wired as a census-sync `--check` abstains instead of reporting a key diff.

    ⚑⚑⚑ THIS ARM EXISTS BECAUSE THE DEFECT SHIPPED AND WAS MISDIAGNOSED TWICE (gate-G26,
    gate-G28). `tool mode census in sync` read `101 added of 101 held` — a REFUSING row — while
    `toolmodes.py --check` reported the census FRESH. `scratch/toolmodes.py` carries two gate
    mechanisms: an unwired `--nearmiss` ratchet and the `--check` the hook runs. Keyed on the
    SCRIPT, the census found the ratchet's key set and rendered its arithmetic under the wired
    gate's name.

    ⚑⚑ THE POSITIVE CONTROL IS THE SECOND HALF, and without it this arm is satisfiable by a
    guard stuck at "always abstain" — which would silence every ratchet gate into UNMEASURABLE
    and turn the reader's whole purpose off while every other arm still passed. A `--quiet`
    ratchet invocation must still reach the census.

    ⚑ THE STATE MUST BE UNMEASURABLE, NOT AT-BASELINE. This reader has no verdict for a
    census-sync gate, and reporting one would put a false green exactly where the false red was.
    """
    # ⚑⚑ THE SCRIPT MUST EXIST, AND THE FIRST CUT OF THIS ARM DID NOT NOTICE. `_gate`'s default
    # `scripts/fixture.py` is not a real path, so `writes_on_import` answers "does not exist —
    # not imported" and short-circuits BEFORE the sync guard. The arm then asserted the sync
    # message while receiving the missing-file one — a case that never reached the code it names.
    bad = 0
    sync = commit_refusal.verdict(
        commit_refusal.Gate(
            name="fixture",
            script="scratch/toolmodes.py",
            argv='python3 "$ROOT/scratch/toolmodes.py" --check',
            blocking=True,
            conditional=False,
        ),
        will_fire=True,
        baselines={},
    )
    if sync.refuses:
        out.append("selftest: a census-sync gate was censused and reported as refusing")
        bad += 1
    if sync.state != commit_refusal.UNMEASURABLE:
        out.append("selftest: a census-sync gate did not report UNMEASURABLE")
        bad += 1
    if "--check" not in sync.detail:
        out.append("selftest: the abstention did not name the wired mode")
        bad += 1
    # ⚑ THE CONTROL: a ratchet gate must NOT be excused, or the guard has disabled the reader.
    ratchet = commit_refusal.verdict(
        commit_refusal.Gate(
            name="fixture",
            script="scripts/check_ban_ratchet.py",
            argv='python3 "$ROOT/scripts/check_ban_ratchet.py" --quiet',
            blocking=True,
            conditional=False,
        ),
        will_fire=True,
        baselines={},
    )
    if "census-sync" in ratchet.detail:
        out.append("selftest: a ratchet gate was wrongly excused as census-sync")
        bad += 1
    return bad


def the_roster_reads_the_live_hook(out: list[str]) -> int:
    """Check the roster parses the real hook and carries both blocking and advisory gates.

    ⚑ THE FIXTURE ARMS PIN THE SHAPES; this pins that the reader answers about THIS repo. A
    suite of fixtures alone can pass while the tool reports nothing real.

    ⚑⚑ IT STOPS AT THE ROSTER, AND THE REASON IS A MEASURED KILL. An earlier version called
    `survey()`, which CENSUSES every gate — importing thirty-five gate modules into one
    process. Under the 192MB selftest lease that was killed (exit 143), twice, including at a
    raised ceiling. The per-file gate's lesson again: the UNIT was wrong. Reading the roster
    needs two authorities rather than the whole fleet, and it still fails if the hook stops
    parsing — which is the property this arm is actually for. The full census is what the TOOL
    does; a suite re-running it pays the tool's cost to re-assert the tool's own arms.

    ⚑ THE ADVISORY HALF IS ASSERTED SEPARATELY, because the union with the advisory roster is
    the step most easily lost — and losing it silently drops the gates whose distinguishing
    property is that they cannot refuse.
    """
    rows = commit_refusal.hook_gates()
    if not rows:
        out.append("selftest: the live hook roster was empty")
        return 1
    bad = 0
    if not any(r.blocking for r in rows):
        out.append("selftest: the live roster found no blocking gate")
        bad += 1
    if all(r.blocking for r in rows):
        out.append("selftest: the live roster found no advisory gate")
        bad += 1
    return bad


def the_sync_fold_maps_every_state(out: list[str]) -> int:
    """Check a fetched census-sync verdict lands in the right state — every one, both directions.

    ⚑⚑⚑ THE LOAD-BEARING HALF IS THAT A DRIFTED SYNC GATE BECOMES A REFUSAL, and no tree state
    exercises it today: every sync gate currently answers FRESH. So the arm drives the mapping
    directly. Without it the fold could map DRIFTED to at-baseline and the reader would report a
    refusing gate as clean — reintroducing gate-F61 with MORE authority, because this reader
    would have ASKED and still said nothing.

    ⚑⚑ UNREACHED MUST STAY UNMEASURABLE, and it is the state the budget produces most often. A
    gate skipped for cost, or refused by the write guard, is exactly as unmeasured as one nobody
    asked; promoting it to clean is the false green this module's header refuses in three places.

    ⚑ THE ARM TESTS THE MAPPING, NEVER `survey()`. Calling the real survey imports every gate
    module AND runs six subprocesses — the measured 143 kill `the_roster_reads_the_live_hook`
    was already cut back for, plus gate-F63's ~42s. The fold's correctness is a pure function of
    a verdict and a row, so the expensive part is not the part under test.
    """
    bad = 0
    # ⚑⚑ TIMED-OUT MAPS TO UNMEASURABLE ALONGSIDE UNREACHED, AND THAT IS NOT A COLLAPSE. This
    # reader has three states; the distinction the fourth carries rides in the DETAIL, so a row
    # reads `crossed 120s` rather than `could not run`. The split lives in `sync_verdict` because
    # that is where the cause is known — and it exists because a gate measured FRESH at ~46s was
    # reported UNMEASURABLE under contention, which is a fact about the machine rendered as one
    # about the tree.
    want = {
        "DRIFTED": commit_refusal.OVER,
        "FRESH": commit_refusal.AT_BASELINE,
        "UNREACHED": commit_refusal.UNMEASURABLE,
        "TIMED-OUT": commit_refusal.UNMEASURABLE,
    }
    for got, expected in want.items():
        if commit_refusal.SYNC_STATE.get(got) != expected:
            out.append(
                f"selftest: a {got} sync verdict maps to "
                f"{commit_refusal.SYNC_STATE.get(got)!r}, not {expected!r}"
            )
            bad += 1

    # ⚑⚑ THE MAPPING IS SPELLED WITH LITERALS IN `commit_refusal` TO AVOID AN IMPORT CYCLE — that
    # module is the roster `sync_verdict` reads. So this asserts the two AGREE: a renamed state
    # over there would otherwise raise a KeyError inside the fold at a reader's call site, which
    # is the drift a literal always risks and the reason it must be checked rather than trusted.
    # ⚑ IT CAUGHT EXACTLY THAT THIS TICK — adding TIMED-OUT to the fold without adding it here
    # failed this arm, which is the arm working rather than an obstacle to route around.
    from substrate import sync_verdict  # noqa: PLC0415

    spelled = {
        sync_verdict.DRIFTED,
        sync_verdict.FRESH,
        sync_verdict.UNREACHED,
        sync_verdict.TIMED_OUT,
    }
    if spelled != set(commit_refusal.SYNC_STATE):
        out.append(
            f"selftest: sync_verdict spells {sorted(spelled)}, the fold maps "
            f"{sorted(commit_refusal.SYNC_STATE)}"
        )
        bad += 1
    return bad


_ARMS = (
    a_blocking_gate_over_baseline_refuses,
    an_unmeasurable_gate_is_not_clean_and_does_not_refuse,
    an_advisory_gate_never_refuses,
    a_conditional_gate_that_does_not_fire_never_refuses,
    a_vacuous_gate_does_not_refuse_and_is_not_at_baseline,
    an_absent_baseline_is_reported_before_the_census,
    an_unreadable_gate_reports_a_reason,
    a_trigger_matches_the_staged_index,
    an_unreadable_authority_yields_no_rows,
    the_mark_column_says_what_a_gate_does,
    the_summary_counts_each_state_separately,
    an_unreadable_roster_is_a_refusal_not_a_green,
    a_write_default_gate_is_never_imported,
    a_census_sync_gate_is_not_censused_as_a_ratchet,
    the_roster_reads_the_live_hook,
    the_sync_fold_maps_every_state,
)

_CASE_COUNT = 1 + 2 + 1 + 1 + 2 + 1 + 2 + 3 + 2 + 1 + 4 + 1 + 2 + 4 + 2 + 4


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"commit-refusal selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"commit-refusal selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
