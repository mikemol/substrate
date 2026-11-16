#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""What would refuse a commit right now, and why — WITHOUT attempting one.

⚑⚑⚑ THE STATE OF THE GATES IS DISCOVERED BY ATTEMPTING A COMMIT, WHICH IS THE WORST MOMENT TO
LEARN IT. Measured: nothing was committed across five working sessions while ~40 new modules
accumulated, and the roster carried pre-existing red BEFORE that work started. `gate_status.py`
already runs every hook-wired gate — but it runs them SERIALLY with a 600s per-gate timeout over
a roster containing two gates measured past fifteen minutes; a bare run measured here took over
twenty-five minutes to answer. This reader is the BOUNDED counterpart: it answers from each
authority's own declaration rather than by executing the fleet.

⚑⚑⚑ THREE DISTINCTIONS THIS REPORT REFUSES TO COLLAPSE, each one a recorded incident here, and
each one MEASURED as collapsed in the run-the-fleet reader.

  · **UNMEASURABLE is not CLEAN.** A gate that will not import has NO VERDICT. Four of the seven
    ratchet-family gates fail to load their SIBLINGS (`ratchet`, `buildtime`) while being present
    on disk and fine under the hook, which invokes them by script path with `scripts/` on
    `sys.path[0]`. Reporting those as passing banks a false green; reporting them as failing
    banks a false red. They are a third thing, and `ratchet_census` returns a REASON for every
    one, so this reader prints the reason rather than a verdict it does not have.
    ⚑ MEASURED, and not hypothetical: a full `gate_status.py` run rendered `tool unit tests` and
    `tool selftests` as `FAIL(1)` when both had died on `TypeError: may_write() takes 0
    positional arguments` — a BROKEN RUNNER, printed in the same column as genuine debt. An
    operator reading that row goes looking for test failures that were never measured.

  · **ABSENT BASELINE is not REGRESSION.** `type_gate` reads its NEW keys because
    `mypy_ratchet_baseline.txt` is EMPTY — the zero-tolerance setting, where every offender is a
    new key and nothing is grandfathered. That is a LEVEL, not a delta. A reader rendering it as
    a regression sends someone to fix a four-figure count of non-defects. ABSENT is the OPPOSITE
    failure: no file at all, so `set_ratchet` takes the record-and-pass branch and exits 0
    REGARDLESS of what it measured. `BaselineState` carries both properties as independent bits;
    this module asks the state rather than comparing its name, because every site that compared
    names got some case of it wrong.

  · **ADVISORY is not BLOCKING.** Two gates are invoked bare with `|| true`, deliberately outside
    the hook's `run()`, so they print and cannot refuse. Counting them as blockers overstates the
    debt; omitting them hides real findings.
    ⚑ AND THE INVERSE ERROR IS ALSO MEASURED: `gate_status.py` runs each gate through its HOOK
    ARGV, `|| true` included, so `def/proof separation` — a BLOCKING gate whose `|| true` sits
    outside `run` and cannot save it — printed PASS. The shell fragment that makes a gate LOOK
    advisory is not the thing that makes it advisory; only its position relative to `run` is.

⚑⚑ AND THE FOURTH DISTINCTION IS THE ONE THE OPERATOR ACTUALLY ASKED FOR: **WOULD-FIRE is not
WIRED.** Six gates sit inside `if` blocks guarded by a `git diff --cached` trigger, so with an
unstaged tree they do not run at all. A report listing them beside the unconditional gates
answers "what gates exist", not "what would refuse THIS commit" — different questions whenever
the index is not the worktree, which is precisely the situation that motivated this module.

⚑ IT EXECUTES NO GATE, AND THAT IS THE DESIGN, NOT A SHORTFALL. Running the fleet is
`gate_status.py`'s job and it does it correctly. Every figure here is read from a declaration:
the hook's own call sites (blocking/advisory/conditional), the staged index (does a trigger
fire), each gate's `census()` and `BASELINE` (measurable, over baseline), and
`gate_census.baseline_health()` (baseline state). A declaration read is bounded; a fleet run is
not, and an unbounded reader is one nobody consults before committing.

⚑ IT WRITES NOTHING AND RUNS NO GATE'S MAIN. `census()` is a pure read by contract, and
`SUBSTRATE_RATCHET_WRITE` is never set here — a reader that could lower a baseline would launder
a transient into a permanent grandfathering, which is the one thing worse than not reporting.

⚑⚑⚑ AND "IT ONLY IMPORTS" IS NOT THE SAME AS "IT DOES NOT WRITE" — MEASURED IN THIS MODULE'S OWN
SUITE. Censusing a gate IMPORTS it, and `sppf_node_index.py` has its whole body at module level
with a final `else:` that writes, so the first live run of this reader REGENERATED
`scratch/sppf_collision_index.md` while claiming to be read-only. `import_writes` is asked
BEFORE the census — never after, which would report the write it failed to prevent.

⚑ EVERY READ OF A GATE MODULE IS AN UNTYPED BOUNDARY, narrowed AT THE SEAM as `ratchet_census`
does it. A gate is an arbitrary module; letting an unchecked attribute read carry `Any` into the
comparison that decides whether a commit is refused would put the least-checked value in the
most load-bearing position in this file. Every crossing goes through `call_rows`, `field`,
`entry` or `flag` — each returning a concrete type or nothing.

⚑⚑ THE ROSTER (`Gate`, `hook_gates`, and the untyped-boundary readers it needs) LIVES IN
`hook_roster` since 2026-09-24, re-exported here unchanged. It moved to cut the one live import
cycle: `sync_verdict` needed the roster and this module needs `sync_verdict`.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass

from substrate import corpus, import_writes, ratchet_census
from substrate.hook_roster import Gate, authority, call_rows, field, hook_gates

# ⚑ RE-EXPORTED: suites and `wired_mode_selftest` read these through this module.
__all__ = [
    "AT_BASELINE",
    "OVER",
    "SYNC_STATE",
    "UNMEASURABLE",
    "VACUOUS",
    "Gate",
    "Verdict",
    "authority",
    "call_rows",
    "field",
    "fires",
    "hook_gates",
    "main",
    "mark",
    "render",
    "verdict",
    "writes_on_import",
]

# The states a gate can be in. ⚑ DECLARED, so the renderer and the counters cannot disagree
# about which of them means "this refuses".
OVER = "OVER"
UNMEASURABLE = "UNMEASURABLE"
VACUOUS = "VACUOUS"
AT_BASELINE = "at baseline"


@dataclass(frozen=True, slots=True)
class Verdict:
    """One gate's standing: whether it can refuse, whether it was readable, and what it holds."""

    name: str
    script: str
    blocking: bool
    conditional: bool
    fires: bool
    state: str
    detail: str

    @property
    def refuses(self) -> bool:
        """Report whether THIS gate would refuse THIS commit.

        ⚑ THE THREE CONJUNCTS ARE ALL LOAD-BEARING, and dropping any one produces a report this
        module exists to prevent. Not blocking -> it prints and exits 0 whatever it found. Not
        firing -> its trigger does not match the staged index, so it never runs. Not OVER -> it
        holds nothing new. An UNMEASURABLE gate is NOT `refuses`, because nobody measured it —
        and it is not clean either, which is why it is counted on its own line.
        """
        return self.blocking and self.fires and self.state == OVER


def flag(obj: object, attr: str) -> bool:
    """Return one boolean property of an untyped value, defaulting to False.

    ⚑ `getattr` RETURNS `Any`, AND THIS IS THE PROPERTY THAT DECIDES WHETHER A DEFECT IS
    REPORTED. Narrowing it here keeps the one attribute read that matters from carrying `Any`
    into the merge that could otherwise hide a vacuous green behind a healthy sibling.
    """
    got: object = getattr(obj, attr, False)
    return got is True


def sample(key: str, width: int = 60) -> str:
    """Return a census key short enough to illustrate a verdict rather than bury it.

    ⚑⚑ A CENSUS KEY IS ONLY USUALLY A SHORT OPAQUE STRING, and the exception destroyed the
    report. `toolmodes` keys on a whole parsed mode-table, so one `e.g.` rendered as nineteen
    thousand characters of nested dicts and the verdict table vanished under it. An example
    that buries the thing it illustrates is worse than no example.

    ⚑ TRUNCATED, NOT DROPPED. The key is what an operator greps for next, so the head of it is
    the useful part; the ellipsis says explicitly that there is more rather than implying the
    key really ends there.
    """
    flat = " ".join(key.split())
    return flat if len(flat) <= width else flat[:width] + "…"


def writes_on_import(script: str) -> str:
    """Return why censusing this gate would WRITE, or the empty string when it is safe to read.

    ⚑ THE JUDGEMENT LIVES IN `import_writes`, EXTRACTED AT THE PER-FILE GATE'S OWN INSTRUCTION:
    the guard needs `importlib`/`sys` at module scope, which this file could not absorb in one
    edit. A gate that keeps firing is saying the UNIT is wrong, and here it was right.
    """
    return import_writes.why_not_import(script)


def triggers() -> list[str]:
    """Return the conditional gates' staged-path trigger regexes, verbatim from the hook."""
    return [str(t) for t in call_rows(authority("gate_census"), "triggers")]


def staged() -> list[str]:
    """Return the staged paths — the index, which is what a trigger actually matches.

    ⚑⚑ THE INDEX, NOT THE WORKTREE, AND THE DIFFERENCE IS THE WHOLE QUESTION. The hook's
    conditional gates test `git diff --cached`, so forty modified files that were never `git
    add`ed fire NOTHING. A reader answering from the worktree would report six extra gates as
    live and send the operator to pay down debt no commit would have hit — a fact about the
    working tree, reported as a fact about the commit.
    """
    got = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],  # noqa: S607
        cwd=corpus.ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return [line for line in got.stdout.splitlines() if line.strip()]


def fires(patterns: list[str], paths: list[str]) -> bool:
    """Report whether any staged path matches any conditional trigger."""
    return any(re.search(p, path) for p in patterns for path in paths)


def baseline_states() -> dict[str, str]:
    """Return `script -> baseline state name`, delegating to the health reader."""
    out: dict[str, str] = {}
    for row in call_rows(authority("gate_census"), "baseline_health"):
        rel, state = field(row, 0), field(row, 2)
        if rel is None or state is None:
            continue
        # ⚑ A SCRIPT MAY OWN SEVERAL BASELINES (`check_snapshot_guard` owns three), and a DEFECT
        # must not be masked by a healthy sibling. `is_defect` wins the merge, so a gate with one
        # ABSENT baseline reports ABSENT however many `ok` ones sit beside it — a merge taking
        # the last row would hide the vacuous green behind whichever row happened to sort later.
        if str(rel) in out and not flag(state, "is_defect"):
            continue
        out[str(rel)] = str(state)
    return out


def verdict(gate: Gate, *, will_fire: bool, baselines: dict[str, str]) -> Verdict:
    """Return one gate's standing, asking each authority rather than executing the gate.

    ⚑⚑ AN ABSENT BASELINE IS REPORTED BEFORE THE CENSUS IS CONSULTED, because it makes the census
    IRRELEVANT: the gate exits 0 whatever it measured. Reading such a gate's census and reporting
    "at baseline" would be literally true and deeply misleading — the verdict is not that the
    tree is clean, it is that the gate cannot say.
    """

    def stand(state: str, detail: str) -> Verdict:
        return Verdict(
            name=gate.name,
            script=gate.script,
            blocking=gate.blocking,
            conditional=gate.conditional,
            fires=will_fire,
            state=state,
            detail=detail,
        )

    if baselines.get(gate.script) == "ABSENT":
        return stand(VACUOUS, "no baseline file — exits 0 REGARDLESS of what it measured")

    # ⚑ ASKED BEFORE THE CENSUS, because the census is what would perform the import. A guard
    # consulted afterwards would report the write it failed to prevent.
    writing = writes_on_import(gate.script)
    if writing:
        return stand(UNMEASURABLE, writing)

    # ⚑⚑⚑ A SCRIPT IS NOT A GATE, AND CENSUSING ONE AS THE OTHER PRODUCED A REFUSING ROW FOR
    # THREE TICKS (gate-G26, gate-G28). A census-sync gate's verdict IS its own exit code — it
    # holds no baseline, and the key set a census would find belongs to whatever OTHER mechanism
    # happens to share the file. Asked here, beside the write guard, because both answer one
    # question: is a census the right instrument for this gate. Neither is a claim about the tree.
    # ⚑⚑ THE ROW SAYS UNMEASURABLE RATHER THAN CLEAN, which is the distinction this module's own
    # header refuses to collapse. This reader has no verdict for such a gate, and reporting one
    # would put a false green exactly where the false red used to be.
    # ⚑ IMPORTED LOCALLY BECAUSE THE PER-FILE GATE ENFORCES IMPORT-WITH-USE IN ONE WRITE, and
    # this file is too large to rewrite whole without retyping code this edit never read.
    from substrate import wired_mode  # noqa: PLC0415

    unkeyed: str = wired_mode.why_not_census(gate.argv)
    if unkeyed:
        return stand(UNMEASURABLE, unkeyed)

    got, why = ratchet_census.census(gate.script.rsplit("/", 1)[-1])
    if got is None:
        return stand(UNMEASURABLE, why or "no reason given")
    if not got.over:
        return stand(AT_BASELINE, f"{got.held} held")

    # ⚑⚑ THE ZERO-TOLERANCE READING IS NAMED AS A LEVEL, NOT A DELTA. With an EMPTY baseline
    # every key is new BY CONSTRUCTION, so a four-figure "added" is the SIZE OF THE POPULATION,
    # not evidence that four figures' worth of things regressed. Rendering the two identically
    # is what would send an operator to fix a number that was never a defect count — and they
    # are indistinguishable from the census alone, which is why the baseline STATE reaches here.
    level = baselines.get(gate.script) == "EMPTY"
    detail = (
        f"{got.over} of {got.held} held — ZERO-TOLERANCE baseline: a LEVEL, not a regression"
        if level
        else f"{got.over} added of {got.held} held"
    )
    # ⚑ THE SAMPLE KEY IS TRUNCATED — see `sample`: one census keys on a whole parsed
    # mode-table, and rendering it whole buried the verdict table it was illustrating.
    return stand(OVER, f"{detail}  e.g. {sample(got.added[0])}")


def survey() -> list[Verdict]:
    """Return a verdict for every hook-wired gate, in hook order."""
    paths, pats, baselines = staged(), triggers(), baseline_states()
    live = fires(pats, paths)
    return [
        verdict(g, will_fire=live if g.conditional else True, baselines=baselines)
        for g in hook_gates()
    ]


#: How a census-sync gate's own answer becomes one of this reader's states.
#:
#: ⚑⚑⚑ AT MODULE SCOPE SO A CASE CAN ASSERT IT, and that is not a style preference. Written as a
#: local inside `fold_sync` the mapping was unreachable from any test, so the arm that matters
#: most — a DRIFTED gate must become a REFUSAL — could only be checked by running the real
#: survey, which no suite here can afford (a prior arm was killed at 143 doing exactly that).
#: A rule nothing can assert is a rule that drifts.
#:
#: ⚑⚑ DRIFTED -> OVER because that gate refuses; FRESH -> AT_BASELINE because it holds nothing
#: new; UNREACHED -> UNMEASURABLE because a gate skipped for budget, or refused by the write
#: guard, is exactly as unmeasured as one nobody asked. Promoting that last one to clean is the
#: false green this whole module exists to refuse.
#:
#: ⚑ SPELLED WITH LITERALS RATHER THAN READ FROM `sync_verdict`, which predates the cycle cut
#: (the roster now lives in `hook_roster`). The suite asserts the two agree, so the duplication
#: is checked rather than trusted.
#:
#: ⚑⚑ TIMED-OUT MAPS TO UNMEASURABLE TOO, AND THAT IS NOT A COLLAPSE. This reader has three
#: states and the distinction the fourth carries lives in the DETAIL, which travels with the row
#: — so a reader sees `crossed 120s` rather than `could not run`, without this module growing a
#: state it has no other use for. The split exists in `sync_verdict` because that is where the
#: cause is known.
SYNC_STATE: dict[str, str] = {
    "DRIFTED": OVER,
    "FRESH": AT_BASELINE,
    "UNREACHED": UNMEASURABLE,
    "TIMED-OUT": UNMEASURABLE,
}


def fold_sync(rows: list[Verdict], budget_s: float | None = None) -> list[Verdict]:
    """Replace each census-sync gate's UNMEASURABLE row with the verdict it will actually give.

    ⚑⚑⚑ THE ROWS THIS REPLACES SAY THE ANSWER EXISTS AND DECLINE TO FETCH IT. `wired_mode`'s
    reason — *a census-sync gate answers with its own exit code* — is true, and for five ticks
    nothing anywhere was collecting that exit code, so a genuinely REFUSING gate sat inside the
    UNMEASURABLE block unreported (gate-F61). This is that repair, and it is OPT-IN because the
    cost is real: gate-F63 measured the class at ~42s, of which ONE member is ~32s.

    ⚑⚑ SO THE DEFAULT MUST NOT CHANGE. `commit_refusal` exists because an unbounded reader is
    one nobody consults before committing — its header argues exactly that, from a measured
    twenty-five-minute fleet run. A fold that made the default slow would trade a blind reader
    for an unused one, which is worse: the blind reader at least gets read.

    ⚑ THE MAPPING IS THREE-WAY AND KEEPS EVERY DISTINCTION THIS MODULE OWNS. DRIFTED becomes
    OVER, because that gate refuses. FRESH becomes AT_BASELINE, because it holds nothing new.
    UNREACHED STAYS UNMEASURABLE — a gate skipped for budget or refused by the write guard is
    exactly as unmeasured as before, and promoting it to clean would put a false green where
    the reader's whole purpose is refusing one.
    """
    from substrate import sync_verdict  # noqa: PLC0415

    asked = {got.name: got for got in sync_verdict.survey(budget_s)}
    if not asked:
        return rows

    out: list[Verdict] = []
    for row in rows:
        got = asked.get(row.name)
        if got is None:
            out.append(row)
            continue
        out.append(
            Verdict(
                name=row.name,
                script=row.script,
                blocking=row.blocking,
                conditional=row.conditional,
                fires=row.fires,
                state=SYNC_STATE[got.state],
                detail=got.detail,
            )
        )
    return out


def mark(got: Verdict) -> str:
    """Return the leading column: what this gate DOES to a commit, not what it found."""
    if got.refuses:
        return "REFUSES"
    if not got.blocking:
        return "advisory"
    return "skipped" if not got.fires else "-"


def render(rows: list[Verdict], paths: list[str]) -> str:
    """Render the survey, keeping every distinction on its own line."""
    out = [
        f"  {len(paths)} path(s) staged"
        + ("" if paths else "  — no conditional gate fires on an empty index")
    ]
    out.extend(f"  {mark(got):<9} {got.state:<13} {got.name:<32} {got.detail}" for got in rows)

    refusing = [r for r in rows if r.refuses]
    unmeasured = [r for r in rows if r.state == UNMEASURABLE]
    vacuous = [r for r in rows if r.state == VACUOUS]
    findings = [r for r in rows if not r.blocking and r.state == OVER]
    skipped = [r for r in rows if r.conditional and not r.fires]

    # ⚑⚑ EACH TAIL LINE IS A SEPARATE COUNT, NEVER FOLDED INTO THE REFUSAL TOTAL. An unmeasurable
    # gate has no verdict, a vacuous one cannot render one, an advisory finding cannot refuse,
    # and a skipped gate did not run. Summing them yields one number that is wrong in four
    # different directions at once — and a single number is exactly what a reader would quote.
    out.extend(
        [
            "",
            f"  {len(refusing)} gate(s) WOULD REFUSE this commit",
            f"  {len(unmeasured)} UNMEASURABLE — no verdict, NOT clean",
            f"  {len(vacuous)} VACUOUS — absent baseline, exits 0 regardless",
            f"  {len(findings)} advisory finding(s) — real, but cannot refuse",
            f"  {len(skipped)} conditional gate(s) not triggered by the staged index",
        ]
    )
    return "\n".join(out)


def main(out: list[str], argv: list[str] | None = None) -> int:
    """Report what would refuse a commit right now.

    ⚑ `--sync` FETCHES THE CENSUS-SYNC VERDICTS this reader otherwise declines to collect, at a
    measured cost (gate-F63). OPT-IN, because the default must stay fast enough to be consulted;
    `--budget <s>` bounds what it spends and reports the rest UNMEASURABLE, unchanged.
    """
    got = argv or []
    rows = survey()
    if not rows:
        # ⚑ AN UNREADABLE ROSTER IS A REFUSAL, NEVER A GREEN. Returning 0 here would report the
        # reader's own failure as a clean tree — the exact false-green this module documents.
        out.append("  commit-refusal: the hook roster could not be read — NOT a clean tree")
        return 1
    if "--sync" in got:
        from substrate import sync_verdict  # noqa: PLC0415

        rows = fold_sync(rows, sync_verdict.budget_of(got))
    out.append(render(rows, staged()))
    return 1 if any(r.refuses for r in rows) else 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS MODULE (⟡selftest-discovery), and it
# DELEGATES rather than exiting 0 — a no-op guard reports nothing, which the outcome classifier
# calls `silent`.
if __name__ == "__main__":
    import sys

    from substrate import quiet_read

    if "--selftest" in sys.argv:
        from substrate import commit_refusal_selftest

        sys.exit(commit_refusal_selftest.selftest())

    # ⚑ THE AUTHORITIES NARRATE WHILE THEY WORK, and censusing them means importing and calling
    # them — so the twelve-line verdict table arrived under nineteen thousand characters of
    # someone else's scan output. The chatter is captured rather than discarded: an authority's
    # genuine error must not vanish into a quieter report.
    _lines: list[str] = []
    _code, _noise = quiet_read.quietly(lambda: main(_lines, sys.argv[1:]))
    sys.stdout.write("\n".join(_lines) + "\n")
    if "--noise" in sys.argv and _noise:
        sys.stdout.write("\n--- what the authorities printed while being read ---\n" + _noise)
    sys.exit(_code)
