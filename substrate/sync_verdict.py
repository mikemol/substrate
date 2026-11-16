# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Ask a census-sync gate for its verdict — the answer `commit_refusal` declines to fetch.

⚑⚑⚑ THE VERDICT EXISTS AND NOTHING WAS ASKING FOR IT. `commit_refusal` reports every
census-sync gate as UNMEASURABLE with the reason *"wired as `--check` — a census-sync gate
answers with its own exit code, not a key diff"*. Every word of that is true, and it names
the answer while declining to fetch it: the exit code IS the verdict, and no reader was
running these gates to collect it. Nine of the roster's gates are wired this way — measured
with `gate_status.py --list`, not counted from the reason column, because several of them
land in the write-guard bucket first and never reach the sync reason at all.

⚑⚑ AND THE ABSTENTION IS CORRECT FOR THE READER THAT MAKES IT. `commit_refusal`'s contract
is *execute no gate*, argued from a measured cost: `gate_status.py` runs the fleet SERIALLY
with a 600s per-gate timeout over a roster holding two gates past fifteen minutes, and a
bare run was measured past twenty-five. That argument is about the FLEET. A census-sync
`--check` is the bounded opposite — `toolmodes.py --check` measured at ~3s, read-only by
construction, because a drift gate's whole job is comparing a generated block against what
`--sync` would write. So this is not a loosening of that contract; it is a different
population with a different cost, and it gets its own reader rather than a flag on that one.

⚑ THE SELECTION IS `wired_mode`'s, NEVER A SECOND SPELLING. Which gates are census-sync is
already owned — `wired_mode.sync_flag` reads the hook's argv and its own docstring records
the three wrong diagnoses that came of keying on the script instead. Re-deriving that test
here would be a rival authority for exactly the relation that module exists to settle, and
`SYNC_FLAGS` would then have two homes.

⚑⚑ A GATE THAT WRITES ON A BARE RUN IS REFUSED BEFORE IT IS RUN, and the order is
load-bearing rather than tidy. `import_writes` is asked FIRST, so a gate whose `--check`
happens to regenerate its artifact is never invoked — `commit_refusal`'s own suite recorded
the live instance, where censusing `sppf_node_index.py` REGENERATED a markdown index while
the reader claimed to be read-only. A guard consulted after the run reports the write it
failed to prevent.

⚑⚑⚑ AND THE THIRD OUTCOME IS THE POINT, NOT A FALLBACK. A gate that times out, crashes, or
cannot be found is `UNREACHED` — not fresh, not drifted. Collapsing it into either direction
is the exact defect `commit_refusal`'s header refuses in three places: a false green banks a
verdict nobody measured, and a false red sends an operator to fix a gate that never ran.
`UNREACHED` carries the reason, so the row says which of the three happened.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass

from substrate import corpus, import_writes, label_lease, wired_mode

#: The gate's own `--check` exited 0 — its generated artifact matches what `--sync` would write.
FRESH = "FRESH"

#: The gate's own `--check` exited non-zero — the artifact has drifted and the gate would refuse.
DRIFTED = "DRIFTED"

#: The gate could not be asked at all. NOT a verdict about the tree.
UNREACHED = "UNREACHED"

#: The gate WAS asked, ran, and crossed `_TIMEOUT_S` before answering. NOT a verdict about the
#: tree either — but a different cause from `UNREACHED`, and the distinction is measured.
#:
#: ⚑⚑⚑ THE TWO WERE ONE STATE AND THAT PRODUCED A FALSE *NOT CLEAN*. `commit_refusal --sync`
#: reported the apex gate `no answer within 120s`, while `sync_verdict` run directly read it
#: FRESH at 46.0s and again at 46.4s — roughly a third of its own ceiling. The row rendered the
#: crossing identically to a gate that never started.
#:
#: ⚑⚑ AND TWO EXPLANATIONS FOR THE CROSSING HAVE NOW BEEN REFUTED IN TURN. *Contention* went
#: first: a quiet run still read 120.2s. *Serial position* went second: `--gate "apex gate"`
#: asks it as the ONLY gate and it still read 120.3s. What survives is that the gate's own cost
#: moves — it has answered in 46s and it has run past 300s invoked directly on this box, both
#: correctly. So a crossing is a reading of the GATE AND THE MOMENT together.
#:
#: ⚑ WHICH IS WHY `--gate <name>` EXISTS: a TIMED-OUT row is a prompt to ask that gate alone and
#: compare, not a verdict to act on. The difference between the two readings is the datum.
#:
#: ⚑⚑ A TIMEOUT IS A STATEMENT ABOUT THE MACHINE AND `UNREACHED` READS AS ONE ABOUT THE GATE.
#: The repo's standing rule is that wall time is not a measurement; this is that rule firing on a
#: drift check's own budget. A gate that never started, a gate that crashed, and a gate that ran
#: well within its ceiling on an idle box are three different things to do next, and collapsing
#: the third into the first sends a reader to fix a gate that is fine.
#:
#: ⚑ THE COST IS CARRIED, SO THE ROW CAN SAY SO. `seconds` is already set on the timeout path
#: (gate-F63's repair), and it is what separates *crossed the ceiling after real work* from
#: *never ran* — which is why this state is derivable rather than a fourth guess.
TIMED_OUT = "TIMED-OUT"

# ⚑⚑⚑ THE TIMING GATE IS CPU TIME; THE WALL CLOCK IS ONLY A HANG GUARD (ruled 2026-09-20, W8:
# *"Use cputime for your timing gate, not wall time."*). Every crossing this module recorded —
# 120.2s quiet, 120.3s asked alone, 46s a minute earlier — was a WALL reading, and wall time is
# the box plus the gate: a loaded machine manufactures a false TIMED-OUT about a gate whose own
# work has not changed. CPU seconds (`rusage` of the child, user + sys) are the gate's, so a gate
# is judged over its ceiling on what it COMPUTED, never on what it waited for.
#
# ⚑ THE WALL GUARD STILL EXISTS BECAUSE A HANG CONSUMES NO CPU. A gate blocked on a lock or a
# socket would never cross a CPU ceiling; the wall guard is a generous multiple of the ceiling
# so it fires on a hang and not on load, and a row that crosses it is TIMED-OUT with the CPU it
# had consumed beside the wall it waited — the two numbers a reader needs to tell the cases apart.
_CPU_CEILING_S = 120
_HANG_MULTIPLE = 4
_TIMEOUT_S = _CPU_CEILING_S * _HANG_MULTIPLE

# ⚑⚑⚑ THE CLASS IS NOT UNIFORMLY BOUNDED, AND I GENERALISED THAT FROM ONE MEMBER (gate-F63).
# `toolmodes --check` measures ~3s, and I carried that to the whole class as the argument for
# fetching these verdicts at all. MEASURED over the roster: ~42s in aggregate, of which
# `law_motif_apex --check` alone is ~32s with sys time dominating — it walks the Agda tree. The
# other ten total ~10s.
#
# ⚑⚑ SO A CALLER THAT MUST STAY BOUNDED NEEDS A BUDGET, NOT A PROMISE. `commit_refusal` exists
# because an unbounded reader is one nobody consults before committing; folding these in
# unconditionally would attack exactly that property. `budget_s` lets a caller spend what it can
# afford and get UNREACHED — the honest third outcome — for whatever did not fit, rather than
# choosing between a slow reader and a blind one.
#
# ⚑ AND UNREACHED-ON-BUDGET IS NOT A VERDICT ABOUT THE TREE. A gate skipped for cost is exactly
# as unmeasured as one that timed out, which is why it reuses the state rather than inventing a
# fourth: collapsing "we did not spend the time" into either direction is the defect this whole
# reader was built to refuse.
UNBUDGETED = "budget spent before this gate was asked — not measured, NOT clean"


@dataclass(frozen=True, slots=True)
class Sync:
    """One census-sync gate, and what its own `--check` answered."""

    name: str
    script: str
    flag: str
    state: str
    detail: str
    # ⚑⚑ THE COST IS CARRIED PER GATE BECAUSE THE CLASS IS NOT UNIFORMLY BOUNDED (gate-F63), and
    # an aggregate cannot say which member to look at. Two ticks were spent re-deriving that
    # `law_motif_apex --check` is ~30s of a ~42s total (gate-F65); the reader should say so.
    # ⚑ 0.0 FOR A GATE THAT WAS NOT ASKED, which is honest rather than missing: no time was
    # spent on it. The state already says why it was not asked.
    seconds: float = 0.0
    # ⚑ CPU SECONDS THE GATE ITSELF SPENT (user + sys of the child), the number the timing gate
    # is judged on; `seconds` above is the wall it waited, kept because their DIFFERENCE is the
    # load the box added. Both zero for a gate that was not asked.
    cpu_s: float = 0.0

    @property
    def over_ceiling(self) -> bool:
        """Whether this gate's own work crossed the CPU ceiling — a fact about the GATE."""
        return self.cpu_s > _CPU_CEILING_S

    @property
    def refuses(self) -> bool:
        """Whether this gate would refuse a commit.

        ⚑ `UNREACHED` IS NOT A REFUSAL, for the same reason `UNMEASURABLE` is not in the reader
        this one extends: nobody measured it. It is also not clean, which is why it counts on
        its own line rather than folding into either total.
        """
        return self.state == DRIFTED


# ⚑ THE OPENING OF THE TIMEOUT REASON, NAMED SO THE WRITER AND THE READER SHARE ONE SPELLING.
# `ask` discriminates TIMED-OUT from UNREACHED by this prefix, and a message assembled at the
# raise site with the test written separately is the census-keyed-on-one-spelling defect at
# arm's length — two copies of one string, drifting the first time either is reworded.
_CROSSED = "no answer within"


# ⚑ ONE HOME FOR THE CPU READER. `label_lease` owns the cost ledger this reading belongs beside
# (W3 sized the lease for time from it; W8 sizes it for work); a second `getrusage` here would
# be the two-emitter shape CLAUDE.md records against `membudget_otlp.emit` / `_emit_one`.
child_cpu = label_lease.child_cpu


def _run(argv: list[str]) -> tuple[int | None, str, float]:
    """Run a gate's own check; return `(exit code, first meaningful line, CPU seconds)`.

    ⚑ A `None` CODE MEANS THE GATE WAS NEVER ASKED — a timeout, a missing interpreter, a
    crash before it could answer. That is distinct from any exit code it might have returned,
    and the caller renders it as `UNREACHED` rather than guessing a direction.

    ⚑ THE CPU FIGURE IS CARRIED ON EVERY PATH, the timeout one included: a gate killed at the
    wall guard having burned the whole guard in CPU is a runaway, and one killed having burned
    none is a hang. The reason line says which, because the state alone cannot.
    """
    before = child_cpu()
    try:
        got = subprocess.run(
            argv,
            cwd=corpus.ROOT,
            capture_output=True,  # noqa: S603
            text=True,
            timeout=_TIMEOUT_S,
            check=False,
        )
    except subprocess.TimeoutExpired:
        cpu = child_cpu() - before
        return (
            None,
            (
                f"{_CROSSED} {_TIMEOUT_S}s wall (the hang guard, {_HANG_MULTIPLE}x the "
                f"{_CPU_CEILING_S}s CPU ceiling) having spent {cpu:.1f}s CPU"
            ),
            cpu,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return None, f"could not run: {exc}", child_cpu() - before
    cpu = child_cpu() - before
    said = (got.stdout or "") + (got.stderr or "")
    lines = [ln.strip() for ln in said.splitlines() if ln.strip()]
    return got.returncode, lines[0] if lines else "(said nothing)", cpu


def state_of(code: int | None, said: str) -> str:
    """Return the state a `_run` outcome means — the four-way choice, as a pure function.

    ⚑⚑⚑ EXTRACTED SO IT CAN BE DRIVEN AT ALL (gate-G362). Inlined in `ask`, the TIMED-OUT branch
    was reachable only by spending `_TIMEOUT_S` or by an OS launch failure — a missing script is
    NEITHER, since python starts and exits non-zero — so no cheap input drove it, replacing the
    discriminator with a constant left the suite at full marks, and an arm written as a negative
    control measured a path that never reached the branch. **Every input to this decision was
    already a plain value**; only its position hid it.

    ⚑⚑ THE REASON IS THE DISCRIMINATOR, NOT THE CLOCK. A crash after real work also spends
    seconds, so elapsed time cannot separate *crossed the ceiling* from *never started* —
    `_run` already tells them apart in the text it returns, and `_CROSSED` is the one spelling
    both sides share.

    ⚑ NO TIMING AND NO SUBPROCESS HERE, DELIBERATELY. `ask` keeps both, because what it owns is
    the invocation and what this owns is the reading. A function that did either could not be
    called with arguments, which is the whole point of the extraction.
    """
    if code is None:
        return TIMED_OUT if said.startswith(_CROSSED) else UNREACHED
    return FRESH if code == 0 else DRIFTED


def ask(name: str, script: str, argv: str) -> Sync | None:
    """Return what one gate's census-sync check answers, or None when it is not a sync gate.

    ⚑ THE WRITE GUARD RUNS BEFORE THE GATE DOES. A `--check` that regenerates its own artifact
    would be a reader mutating the tree it reports on, which is the live incident
    `commit_refusal`'s header records against `sppf_node_index.py`.
    """
    flag = wired_mode.sync_flag(argv)
    if not flag:
        return None

    writing = import_writes.why_not_import(script)
    if writing:
        return Sync(
            name=name, script=script, flag=flag, state=UNREACHED, detail=f"not asked — {writing}"
        )

    import time  # noqa: PLC0415

    began = time.monotonic()
    code, said, cpu = _run(["python3", str(corpus.ROOT / script), flag])
    spent = time.monotonic() - began
    # ⚑ THE FOUR-WAY CHOICE IS `state_of`'s, and this function does not repeat it. Two spellings
    # of one decision is the shape that lets a reader's verdict drift from its own test.
    return Sync(
        name=name,
        script=script,
        flag=flag,
        state=state_of(code, said),
        detail=said,
        seconds=spent,
        cpu_s=cpu,
    )


def render(rows: list[Sync]) -> str:
    """Render the sync gates' own verdicts, each state counted separately.

    ⚑⚑ THREE COUNTS, NEVER SUMMED. A drifted gate refuses, a fresh one does not, and an
    unreached one has no verdict at all — one number would be wrong in three directions, and a
    single number is what a reader quotes.
    """
    if not rows:
        return (
            "sync-verdict: no census-sync gate found in the hook roster — a fact about "
            "the ROSTER READER, not about the gates\n"
        )
    # ⚑ THE COST COLUMN NAMES THE EXPENSIVE MEMBER, which is the fact a caller needs to size a
    # budget and the one two ticks were spent re-deriving (gate-F63, gate-F65).
    # ⚑ TWO CLOCKS PER ROW: wall is what the survey waited, CPU is what the gate computed. A gate
    # over the CPU ceiling is marked on ITS row — that is the timing gate — where a wall crossing
    # is only ever the hang guard (ruled 2026-09-20, W8).
    mark = f"  ⚑ over the {_CPU_CEILING_S}s CPU ceiling"
    out = [
        f"  {r.state:<10} {r.seconds:>6.1f}s wall {r.cpu_s:>6.1f}s cpu  {r.name:<32} "
        f"{r.detail}{mark if r.over_ceiling else ''}"
        for r in rows
    ]
    drifted = [r for r in rows if r.state == DRIFTED]
    fresh = [r for r in rows if r.state == FRESH]
    unreached = [r for r in rows if r.state == UNREACHED]
    slow = [r for r in rows if r.state == TIMED_OUT]
    heavy = [r for r in rows if r.over_ceiling]
    out.extend(
        [
            "",
            f"sync-verdict: {len(rows)} census-sync gate(s) asked their own check",
            f"  {len(drifted)} DRIFTED — would refuse this commit",
            f"  {len(fresh)} FRESH — the generated block matches what --sync would write",
            f"  {len(unreached)} UNREACHED — no verdict, NOT clean",
            f"  {len(slow)} TIMED-OUT — crossed the {_TIMEOUT_S}s wall hang guard; CPU is on the row",
            f"  {len(heavy)} over the {_CPU_CEILING_S}s CPU ceiling — the gate's OWN cost, timing gate",
            "   ⚑ WALL IS THE BOX PLUS THE GATE; CPU IS THE GATE. The apex gate read 46s and 120s",
            "     wall for the same work — compare the cpu column across runs, not the wall one.",
            "   ⚑ these are the gates `commit_refusal` reports UNMEASURABLE: its contract is to",
            "     execute no gate, and a census-sync check is the bounded exception it names.",
        ]
    )
    return "\n".join(out) + "\n"


def survey(budget_s: float | None = None) -> list[Sync]:
    """Ask every census-sync gate in the hook roster for its own verdict.

    ⚑ THE ROSTER IS `gate_status`'s, PARSED FROM THE HOOK. Restating which gates exist would be
    the hand-kept-copy defect this repo files most often, and `commit_refusal.hook_gates`
    already records why that reader owns the parse — including its refusal on a hook that does
    not parse as shell, so a truncated roster is an error rather than a short list.

    ⚑⚑ `budget_s` GATES WHETHER THE NEXT GATE IS STARTED — it does NOT cap the wall time, and
    the difference is measured rather than theoretical. Under `--budget 8` the run took ~37s,
    because the ~32s apex gate began while the budget still had room and then ran to
    completion. A caller gets "stop starting new work after N seconds", which bounds the TAIL
    beyond one gate and cannot bound one gate that is already running; the wall hang guard
    `_TIMEOUT_S` is the only per-gate kill, and the CPU ceiling is a judgement, not a kill.
    Every gate not started is UNREACHED with the reason — the same state as a
    timeout, deliberately, since both mean nobody measured it.

    ⚑ THE WEAKER GUARANTEE IS STILL THE USEFUL ONE, given gate-F63: the class is not uniformly
    bounded and the caller cannot know which member is expensive, so "do not begin anything
    new" is exactly the decision a bounded caller can actually make. Promising a wall-clock cap
    here would be a claim this loop cannot keep.

    ⚑ THE ROSTER ORDER IS THE HOOK'S, so a budget spends on the gates the hook runs first
    rather than on whichever happens to be cheapest. Reordering to fit more in would make the
    report's coverage depend on cost rather than on what the commit actually faces.

    ⚑ THE ROSTER COMES FROM `hook_roster`, NOT `commit_refusal` (2026-09-24): reading it off
    `commit_refusal` closed the one live import cycle, since that module consults this one.
    `time` is local because the per-file gate enforces import-with-use in ONE write, and it is
    used only here.
    """
    import time  # noqa: PLC0415

    from substrate import hook_roster  # noqa: PLC0415

    started = time.monotonic()
    out: list[Sync] = []
    for gate in hook_roster.hook_gates():
        flag = wired_mode.sync_flag(gate.argv)
        if not flag:
            continue
        if budget_s is not None and time.monotonic() - started >= budget_s:
            out.append(
                Sync(
                    name=gate.name,
                    script=gate.script,
                    flag=flag,
                    state=UNREACHED,
                    detail=UNBUDGETED,
                )
            )
            continue
        got = ask(gate.name, gate.script, gate.argv)
        if got is not None:
            out.append(got)
    return out


def budget_of(argv: list[str]) -> float | None:
    """Return the `--budget <seconds>` a caller asked for, or None for no bound.

    ⚑ A MALFORMED BUDGET IS NO BUDGET, NEVER ZERO. Reading `--budget banana` as 0 would starve
    the survey and report every gate UNREACHED — a spelling error rendered as a tree-wide
    absence of measurement, which is the method-as-substrate collapse this reader exists against.
    """
    if "--budget" not in argv:
        return None
    rest = argv[argv.index("--budget") + 1 :]
    if not rest:
        return None
    try:
        return float(rest[0])
    except ValueError:
        return None


def gate_of(argv: list[str]) -> str | None:
    """Return the gate NAME a caller asked about with `--gate`, or None for the whole survey.

    ⚑ A `--gate` WITH NO OPERAND IS NO REQUEST, NEVER AN EMPTY NAME. Reading it as `""` would
    match no roster row and report the gate as absent — a spelling error rendered as a fact
    about the roster, the same collapse `budget_of` refuses for a malformed budget.
    """
    if "--gate" not in argv:
        return None
    rest = argv[argv.index("--gate") + 1 :]
    return rest[0] if rest and not rest[0].startswith("-") else None


def one(name: str) -> tuple[Sync | None, str]:
    """Return one gate's verdict by NAME, or say why the roster could not answer.

    ⚑⚑⚑ THIS IS THE INSTRUMENT THE BOUND'S OWN QUESTION NEEDS (gate-G364). Three readings show
    the apex gate at 46.0s, 120.9s and 120.2s — the same gate, moving with its POSITION in a
    serial survey — while running it alone answers fine. Comparing *alone* against *tenth of
    eleven* is the measurement that would say whether accumulated process state is the cause,
    and until now `ask` was public with no caller, so that comparison had no instrument.

    ⚑⚑ THE ROSTER IS `hook_gates()`'s, MATCHED ON THE NAME IT ALREADY CARRIES. Taking a script
    path instead would make this a second authority on which invocations are census-sync, which
    `wired_mode.sync_flag` owns and `ask` already consults — and that module's docstring records
    three wrong diagnoses from keying on the script.

    ⚑ AN UNKNOWN NAME IS A REFUSAL NAMING THE ROSTER, not an empty result. A census that
    answered nothing for a typo would report the caller's spelling as a fact about the tree.
    """
    from substrate import hook_roster  # noqa: PLC0415

    for gate in hook_roster.hook_gates():
        if gate.name != name:
            continue
        got = ask(gate.name, gate.script, gate.argv)
        if got is None:
            return None, f"{name!r} is in the roster but is not a census-sync gate"
        return got, ""
    known = sorted(g.name for g in hook_roster.hook_gates())
    return None, f"no gate named {name!r} — the roster holds {', '.join(known)}"


def main(out: list[str], argv: list[str] | None = None) -> int:
    """Report what every census-sync gate answers about itself.

    ⚑ `--budget <s>` BOUNDS THE RUN for a caller that cannot spend the full cost — see
    gate-F63: the class is not uniformly bounded, and one member is most of the total.

    ⚑⚑ `--gate <name>` ASKS ONE GATE ALONE, which is a DIFFERENT measurement rather than a
    cheaper one. A gate's cost here is not independent of where it sits in the survey
    (gate-G364), so timing it by itself and timing it in place are two readings whose
    DIFFERENCE is the finding — and a mode that only did the second could not produce it.
    """
    got = argv or []
    name = gate_of(got)
    if name is not None:
        row, why = one(name)
        out.append(render([row]) if row is not None else f"  {why}\n")
        return 0 if row is None or not row.refuses else 1
    rows = survey(budget_of(got))
    out.append(render(rows))
    return 1 if any(r.refuses for r in rows) else 0


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        from substrate import sync_verdict_selftest

        raise SystemExit(0 if sync_verdict_selftest.selftest() else 1)

    _lines: list[str] = []
    _code = main(_lines, sys.argv[1:])
    sys.stdout.write("".join(_lines))
    raise SystemExit(_code)
