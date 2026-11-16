# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.sync_verdict` — the third outcome, and the write guard's order.

⚑⚑⚑ THE LOAD-BEARING CASE IS THAT `UNREACHED` IS NOT A REFUSAL. This reader exists because
`commit_refusal` refuses to collapse UNMEASURABLE into clean, and a reader that fetched the
verdict but then folded its own failures into FRESH or DRIFTED would reintroduce exactly the
collapse it was built to close — one level down, and with more authority, because this one
claims to have ASKED.

⚑⚑ AND THE WRITE GUARD'S ORDER IS CASED, not assumed. `commit_refusal` recorded a live
incident where reading `sppf_node_index.py` regenerated a markdown index while the reader
claimed to be read-only. A guard consulted after the run reports the write it failed to
prevent, so the case asserts a writing gate is never invoked at all.

⚑ THE SELECTION IS DELEGATED AND THE CASE SAYS SO. `wired_mode` owns which invocations are
census-sync, and its own docstring records three wrong diagnoses from keying on the script
instead. A case here that re-derived the test would pin a second spelling in place.
"""

from __future__ import annotations

from substrate import sync_verdict


def _selection_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for which invocations this reader will ask at all."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ⚑ A NON-SYNC GATE IS NOT THIS READER'S SUBJECT, and returning None rather than a verdict
    # is what keeps it out of the counts. A ratchet gate answers with a key diff and
    # `ratchet_census` already owns that; producing a row here would be two readers reporting
    # one gate under two contracts.
    check(
        "a ratchet gate is not asked",
        passed=sync_verdict.ask(
            "ban ratchet",
            "scripts/check_ban_ratchet.py",
            'python3 "$ROOT/scripts/check_ban_ratchet.py" --quiet',
        )
        is None,
    )

    check(
        "and neither is a bare invocation",
        passed=sync_verdict.ask(
            "decl-site shape tags",
            "scripts/decl_shape_tag.py",
            'python3 "$ROOT/scripts/decl_shape_tag.py"',
        )
        is None,
    )

    # ⚑⚑ BOTH SYNC SPELLINGS ARE ASKED. `--check` and `--check-census` are separate flags in
    # `wired_mode.SYNC_FLAGS`, and a reader matching only the first would silently drop the
    # sql census — a population gap reported as an empty result.
    got = sync_verdict.ask(
        "sql census in sync",
        "jea/metalanguage/sql_lift.py",
        'python3 "$ROOT/jea/metalanguage/sql_lift.py" --check-census',
    )
    check("a --check-census gate IS asked", passed=got is not None)
    check(
        "and the row records which flag was wired",
        passed=got is not None and got.flag == "--check-census",
    )

    return out


def _outcome_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the three states and what each means for a commit."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    def row(state: str) -> sync_verdict.Sync:
        return sync_verdict.Sync(name="n", script="s.py", flag="--check", state=state, detail="d")

    # ⚑⚑⚑ THE COLLAPSE THIS READER EXISTS TO REFUSE. An unreached gate has no verdict; calling
    # it a refusal sends an operator to fix a gate that never ran, and calling it fresh banks a
    # green nobody measured. Both directions are asserted, because a case checking only one
    # passes against a reader that always returns the other.
    check("a DRIFTED gate refuses", passed=row(sync_verdict.DRIFTED).refuses)
    check("a FRESH gate does not", passed=not row(sync_verdict.FRESH).refuses)
    check(
        "and an UNREACHED gate does NOT refuse either",
        passed=not row(sync_verdict.UNREACHED).refuses,
    )

    # ⚑ THE WRITE GUARD FIRES BEFORE THE RUN, so a writing gate is UNREACHED rather than
    # carrying whatever exit code it would have produced after mutating the tree.
    writing = sync_verdict.ask(
        "shape-node index current",
        "scripts/sppf_node_index.py",
        'python3 "$ROOT/scripts/sppf_node_index.py" --check',
    )
    check(
        "a gate that writes on a bare run is not invoked",
        passed=writing is not None and writing.state == sync_verdict.UNREACHED,
    )
    check(
        "and the row says it was NOT asked",
        passed=writing is not None and "not asked" in writing.detail,
    )

    # ⚑ A MISSING SCRIPT IS UNREACHED, NEVER A VERDICT. A reader that let a nonexistent path
    # read as a failing gate would report its own spelling error as tree debt.
    absent = sync_verdict.ask(
        "nope",
        "scripts/no_such_gate_at_all.py",
        'python3 "$ROOT/scripts/no_such_gate_at_all.py" --check',
    )
    check(
        "an absent gate is UNREACHED",
        passed=absent is not None and absent.state == sync_verdict.UNREACHED,
    )

    # ⚑⚑⚑ AND A TIMEOUT IS A DIFFERENT CAUSE UNDER THE SAME NON-VERDICT, WHICH IS WHY IT HAS ITS
    # OWN STATE. `commit_refusal --sync` reported the apex gate `no answer within 120s` while
    # `sync_verdict` run directly read it FRESH at 46.0s and again at 46.4s — stable, roughly a
    # third of its ceiling. The crossing happened under contention, and one state rendered it
    # identically to a gate that never started, so the row said *not clean* about a fresh gate.
    #
    # ⚑⚑ THE DISCRIMINATION IS ASSERTED AT THE SEAM RATHER THAN BY TIMING ONE OUT. Driving a real
    # timeout costs `_TIMEOUT_S` per run — the ceiling exists precisely so nothing waits that
    # long, and a suite that spent it would be the slowest case in the tree to assert one branch.
    # What is actually under test is that `ask` keys on the reason `_run` emits, so the arm pins
    # the two spellings against each other.
    # ⚑⚑⚑ THE ROUTING IS NOW DRIVABLE, AND IT WAS NOT (gate-G362). Inlined in `ask`, the
    # TIMED-OUT branch needed a real `_TIMEOUT_S` wait or an OS launch failure to reach — a
    # missing script is NEITHER, since python starts and exits non-zero — so replacing the
    # discriminator with a constant left this suite at full marks and the arm written as a
    # negative control measured a path that never reached the branch. `state_of` takes the same
    # decision as plain arguments, so all four states are one call each.
    #
    # ⚑⚑ ALL FOUR ARE ASSERTED, because each pair is a way to be wrong that the others hide. A
    # router collapsing the two `None` causes passes every exit-code case; one collapsing the
    # exit codes passes every `None` case.
    crossed = f"{sync_verdict._CROSSED} 480s wall (the hang guard) having spent 0.0s CPU"  # noqa: SLF001
    check(
        "a None code whose reason names the crossing is TIMED-OUT",
        passed=sync_verdict.state_of(None, crossed) == sync_verdict.TIMED_OUT,
    )

    # ⚑⚑⚑ THE TIMING GATE IS CPU, THE WALL IS A HANG GUARD (ruled 2026-09-20, W8). A gate that
    # waited past the old 120s on a loaded box while computing for 40s is FRESH and under its
    # ceiling; one that computed for 130s is over its ceiling whatever the wall read. Both
    # directions are asserted, and the wall figure is deliberately the SAME in each so a reader
    # keyed on wall could not pass the pair.
    quick = sync_verdict.Sync(
        name="n",
        script="s.py",
        flag="--check",
        state=sync_verdict.FRESH,
        detail="d",
        seconds=125.0,
        cpu_s=40.0,
    )
    heavy = sync_verdict.Sync(
        name="n",
        script="s.py",
        flag="--check",
        state=sync_verdict.FRESH,
        detail="d",
        seconds=125.0,
        cpu_s=130.0,
    )
    check(
        "a gate under the CPU ceiling is not over it, whatever the wall read",
        passed=not quick.over_ceiling,
    )
    check("and a gate over the CPU ceiling is, at the same wall reading", passed=heavy.over_ceiling)
    check(
        "the wall hang guard is a multiple of the CPU ceiling, never the ceiling itself",
        passed=sync_verdict._TIMEOUT_S > sync_verdict._CPU_CEILING_S,
    )  # noqa: SLF001
    # ⚑ THE CPU READER IS LIVE, NOT A STUB: a real child that burns CPU moves the counter.
    before = sync_verdict.child_cpu()
    code, _said, cpu = sync_verdict._run(  # noqa: SLF001
        ["python3", "-c", "sum(i * i for i in range(3_000_000))"]
    )
    check(
        "a child's CPU is measured as a positive delta on a completed run",
        passed=code == 0 and cpu > 0.0 and sync_verdict.child_cpu() >= before + cpu,
    )
    check(
        "and a None code from a launch failure is UNREACHED, not a timeout",
        passed=sync_verdict.state_of(None, "could not run: boom") == sync_verdict.UNREACHED,
    )
    check("a zero exit is FRESH", passed=sync_verdict.state_of(0, "ok") == sync_verdict.FRESH)
    check(
        "and a non-zero exit is DRIFTED",
        passed=sync_verdict.state_of(1, "stale") == sync_verdict.DRIFTED,
    )

    check(
        "a TIMED-OUT gate does NOT refuse, the same as UNREACHED",
        passed=not row(sync_verdict.TIMED_OUT).refuses,
    )
    # ⚑ AND IT IS A DISTINCT STATE, not an alias — an arm asserting only the non-refusal above
    # would pass against a TIMED_OUT that WAS UNREACHED, which is exactly the collapse repaired.
    check(
        "and it is distinct from UNREACHED rather than an alias for it",
        passed=sync_verdict.TIMED_OUT != sync_verdict.UNREACHED,
    )

    return out


def _render_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for what the report puts on the page."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    rows = [
        sync_verdict.Sync(
            name="a", script="a.py", flag="--check", state=sync_verdict.FRESH, detail="fresh"
        ),
        sync_verdict.Sync(
            name="b", script="b.py", flag="--check", state=sync_verdict.DRIFTED, detail="drifted"
        ),
        sync_verdict.Sync(
            name="c",
            script="c.py",
            flag="--check",
            state=sync_verdict.UNREACHED,
            detail="not asked — writes",
        ),
    ]
    text = sync_verdict.render(rows)

    # ⚑⚑ THREE COUNTS ON THREE LINES. Summing them yields one number wrong in three directions,
    # and one number is what a reader quotes.
    check("the report counts drifted separately", passed="1 DRIFTED" in text)
    check("and fresh separately", passed="1 FRESH" in text)
    check("and unreached separately", passed="1 UNREACHED" in text)
    check("and says unreached is NOT clean", passed="NOT clean" in text)

    # ⚑⚑ THE COST COLUMN IS RENDERED, because the class is not uniformly bounded (gate-F63) and
    # an aggregate cannot name the expensive member. Two ticks were spent re-deriving that one
    # gate is ~30s of a ~42s total (gate-F65); a reader that drops the column sends the next
    # person to derive it a third time.
    priced = sync_verdict.render(
        [
            sync_verdict.Sync(
                name="slow",
                script="s.py",
                flag="--check",
                state=sync_verdict.FRESH,
                detail="ok",
                seconds=31.7,
            )
        ]
    )
    check("the report prices each gate", passed="31.7s" in priced)
    # ⚑ AND A GATE THAT WAS NOT ASKED PRICES AT ZERO rather than blank — no time WAS spent, and
    # a missing figure would read as unmeasured cost rather than as no cost.
    check("an unasked gate prices at zero", passed="0.0s" in text)

    # ⚑ AN EMPTY ROSTER IS A FACT ABOUT THE READER. Rendering an all-zero table would report a
    # roster-parsing failure as a tree with no sync gates.
    check(
        "an empty result reports on the READER, not the gates",
        passed="fact about the ROSTER READER" in sync_verdict.render([]),
    )

    return out


def _budget_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the survey budget — gate-F63.

    ⚑⚑⚑ THE BUDGET EXISTS BECAUSE I GENERALISED A BOUND FROM ONE MEMBER. `toolmodes --check`
    measures ~3s and I carried that to the whole census-sync class; the aggregate is ~42s, of
    which `law_motif_apex --check` alone is ~32s. So bounded-ness belongs to a gate, not to the
    class, and a caller that must stay bounded needs to be able to stop.

    ⚑⚑ BOTH DIRECTIONS, or the case is satisfied by a reader that skips everything. A zero
    budget must ask NOTHING and still report every gate; no budget must ask them all. An arm
    checking only the first passes against a survey that never runs a gate at all.

    ⚑ AND A SKIPPED GATE IS UNREACHED, NEVER FRESH. Not spending the time is exactly as
    unmeasured as a timeout — collapsing it toward clean would put a false green in the reader
    built to refuse exactly that.
    """
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    starved = sync_verdict.survey(budget_s=0.0)

    check("a zero budget still reports every sync gate", passed=len(starved) > 0)
    check("and asks none of them", passed=all(r.state == sync_verdict.UNREACHED for r in starved))
    check(
        "naming the budget as the reason",
        passed=all(r.detail == sync_verdict.UNBUDGETED for r in starved),
    )
    # ⚑ A STARVED SURVEY MUST NOT REFUSE A COMMIT. Reporting an unasked gate as refusing would
    # send an operator to fix a gate nobody ran — the false-red half of the same collapse.
    check("and refuses nothing", passed=not any(r.refuses for r in starved))

    # ⚑ THE OTHER DIRECTION IS THE CONTROL: with no budget the reader reaches gates the starved
    # run could not, so the skip is the budget's doing rather than the reader's.
    full = sync_verdict.survey()
    check("an unbudgeted survey covers the same roster", passed=len(full) == len(starved))
    check(
        "and actually asks some of them",
        passed=any(r.state != sync_verdict.UNREACHED for r in full),
    )

    # ⚑⚑ THE FLAG IS PARSED, AND A MALFORMED VALUE IS NO BUDGET RATHER THAN ZERO. Reading
    # `--budget banana` as 0.0 would starve the survey and report every gate UNREACHED — a
    # typo rendered as a tree-wide absence of measurement.
    check(
        "a budget flag is read from argv", passed=sync_verdict.budget_of(["--budget", "8"]) == 8.0
    )  # noqa: PLR2004
    check("no flag means no bound", passed=sync_verdict.budget_of([]) is None)
    check(
        "a malformed budget is NO budget, not zero",
        passed=sync_verdict.budget_of(["--budget", "banana"]) is None,
    )
    check(
        "and a flag with no value is no budget either",
        passed=sync_verdict.budget_of(["--budget"]) is None,
    )

    # ⚑⚑ `--gate` IS READ THE SAME WAY AND REFUSES THE SAME DEGENERATE INPUT. A `--gate` with no
    # operand read as `""` would match no roster row and report the gate as ABSENT — a spelling
    # error rendered as a fact about the roster, which is the collapse `budget_of` already
    # refuses for a malformed number. ⚑ AND A FOLLOWING FLAG IS NOT A NAME: `--gate --budget 8`
    # must not ask about a gate called `--budget`.
    check(
        "a gate name is read from argv",
        passed=sync_verdict.gate_of(["--gate", "apex gate"]) == "apex gate",
    )
    check("no flag means the whole survey", passed=sync_verdict.gate_of([]) is None)
    check(
        "a flag with no operand is no request, not an empty name",
        passed=sync_verdict.gate_of(["--gate"]) is None,
    )
    check(
        "and a following flag is not mistaken for a name",
        passed=sync_verdict.gate_of(["--gate", "--budget", "8"]) is None,
    )

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _selection_cases() + _outcome_cases() + _render_cases() + _budget_cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"sync-verdict selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
