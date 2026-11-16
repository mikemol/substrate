#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""check_clause_audit.py — every NAME in an import clause must BIND something.

⛔ TWO VERDICTS, TWO GATE SHAPES, because the two failure directions are not the
same KIND of problem and must not be gated as one number.

**NONEXPORT is a HARD GATE AT ZERO.** The target does not export the name. Agda
reports this as a WARNING (`ModuleDoesntExport`), the name silently binds
NOTHING, and the build fails at the far-away USE site as `NotInScope`. That
distance is the whole hazard: the error names a file that is correct, and the
cause sits in a clause somewhere else.

⚑ FIVE MEASURED INSTANCES, FOUR FOUND BY A COMPILE RATHER THAN A CENSUS, and all
five the exhaust of ONE process — a ban sweep that removed a banned construct
without rewiring the consumers that reached names through it:

  * `S5Verdict` forwarded Nat and List but NOT Eq, so fourteen consumers wrote
    `using (_≡_; refl; …; ℕ; zero; suc)` and silently bound the ℕ half only —
    the Eq half bound nothing AND shadowed the real providers.  `fix_notinscope`
    reverted five times against it before the cause was found.
  * `RuleAction.Compose` asked `V4Compose` for `_∘V_` after a sweep stripped the
    `renaming` that was that module's entire content.
  * `GValueLSpace.Properties` and `.LogSumExp` asked for `ExpLogCodec` after its
    `public` forward was retired.
  * `IntParityBridge` asked `Z.Arithmetic` for `_+ℤ_`/`_*ℤ_`/`_⊖_`, which had
    moved to `Z.Add`/`Z.Mul`.
  * `Semiring.Instances.Z` — the same dissolved conduit, found BY the census.

The tree is at ZERO today (all five repaired by hand), which is exactly when a
hard gate is cheap to install and the only time it is honest to install one.

**UNUSED is a PAYDOWN-ONLY RATCHET**, not a hard gate. The target DOES export the
name and the file never mentions it: a dead clause entry. That is debt, not
breakage — but it is debt that MISREPRESENTS THE COST OF PAYDOWN. A clause naming
twelve things where two are live looks like a twelve-name rewire and is a
two-name one, so the dead entries make retiring the clause look more expensive
than it is. Census it, never grow it.

⚑ BOTH VERDICTS ARE COMPUTED BY `agda_defs.clause_audit()`, WHICH IS THE
AUTHORITY — this file adds a gate shape and nothing else. Re-deriving the census
here would be the shared-name-not-shared-authority defect this repo censuses
(`agda_files()` once existed as four bodies under one name, two feeding gates).

⚑ AND THE CENSUS DELIBERATELY DOES NOT EXCUSE `private`.  A first cut swept
`mutual|private|abstract|nested-module` into UNKNOWN and emptied both verdicts
tree-wide.  `private` is BANNED (see `check_private_ratchet.py`) for the same
reason re-exports are: it blocks a name that would otherwise leak, so its
presence is evidence something upstream over-exports.  Excusing it here would
make THIS gate launder what THAT ratchet is paying down — two gates on one
construct pulling opposite ways.
"""

import os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scratch")
)
import ratchet
import agda_defs  # THE clause-audit authority; never re-derive

BASELINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clause_unused_baseline.txt")


_ROWS = None


def rows():
    """`clause_audit()` ONCE per process, memoized.

    ⚑ THE AUDIT WAS RUNNING TWICE PER GATE INVOCATION (found 2026-08-25). `census()`
    and `nonexports()` each called `agda_defs.clause_audit()`, and `main()` calls both —
    so every commit paid the full scan twice. That scan is the expensive one in this
    gate by a wide margin: it builds `def_index()`, `def_index_modules()` and
    `reexport_index()`, then globs and comment-masks every module under
    `agda/Substrate/**` (thousands of files). The selftest called it a THIRD time.
    Nothing was wrong with either function in isolation, which is why it survived —
    the duplication is only visible where the two are composed.

    ⚑ THE COST WAS INVISIBLE BECAUSE THE GATE IS SILENT. `--quiet` prints nothing until
    the whole audit finishes, so a doubled runtime reads as one slow gate rather than
    two, and an operator measured it at >600s with zero output and could not tell
    whether it was progressing, wedged, or looping. `--progress` (below) exists so that
    question is answerable without a stopwatch — a duration is a measurement, "no output"
    is not.

    Memoized rather than threaded through as a parameter so the selftest — which
    legitimately wants the rows and both partitions — pays the scan once as well.
    """
    global _ROWS
    if _ROWS is None:
        _ROWS = agda_defs.clause_audit(on_module=_reporter())
    return _ROWS


#: Modules between progress lines. ⚑ NOT 1: a flushed write per file over thousands of
#: files is thousands of syscalls for a reader who only needs to see the number MOVE.
#: NOT 1000 either — the two phases would emit ~3 lines each and a stall inside a
#: chunk would still be a minutes-long silence. 100 puts a line roughly every few
#: seconds at the measured rate, which is the interval at which "it is advancing" is
#: actually observable to a person watching.
PROGRESS_EVERY = 100


def _reporter():
    """The `on_module` callback for `--progress`, or None. ⚑⚑ Ⓝ24.

    ⚑⚑⚑ 94% CPU PROVES THE PROCESS IS EXECUTING, NEVER THAT IT IS ADVANCING, AND THAT
    DISTINCTION COST THIS GATE A 2061-SECOND RUN. It was killed at ~34 minutes on the
    reasoning *"if it's not emitting progress, kill it, because we can't tell if it's
    hung or not"* — which is correct: an infinite loop also burns 94%. The start banner
    `--progress` already printed proved LIVENESS and nothing more, so after one line a
    long scan and a spin were the same observation. This is the original ten-bytes-of-
    silence defect one level up, and it is why the gate has never been observed to
    finish: not because it cannot, but because waiting could never be justified.

    ⚑ RENDERING LIVES HERE, NOT IN THE AUTHORITY. `agda_defs.clause_audit` reports
    `(phase, done, total)` and chooses no stream and no wording — so a second consumer
    wanting a span or a TUI is not fighting a print statement compiled into the shared
    layer.

    ⚑ STDERR, because this gate's STDOUT IS ITS VERDICT and the pre-commit hook tees
    that into the commit message. Progress on stdout would land in commit messages.

    ⚑ AND THE PHASE IS NAMED. The scan makes TWO passes over the same file list, so a
    counter that silently restarts at zero reads as a regression — or worse, as a loop.
    Naming `mask` and `scan` makes the reset legible as the second phase beginning.
    """
    if "--progress" not in sys.argv:
        return None

    def _report(phase, done, total):
        # ⚑ THE LAST FILE ALWAYS PRINTS, not only every Nth. Otherwise the final line
        # is `3400/3457` and a reader cannot tell a completed phase from one that died
        # 57 files short — which is precisely the ambiguity this callback exists to
        # remove, reintroduced by the sampling that makes it cheap.
        if done % PROGRESS_EVERY and done != total:
            return
        print(f"clause-audit: [{phase}] {done}/{total} module(s)", file=sys.stderr, flush=True)

    return _report


def census(_rows=None):
    """{`<module>:<line>::<target>::<name>`} for every UNUSED clause entry.

    Keyed on all four parts because none alone is stable: a module has many
    clauses, a target appears in many modules, and a name repeats across both.
    The LINE is included so a moved clause reads as paydown-plus-new-debt rather
    than silently swapping one key for another.
    """
    return {
        f"{m}:{ln}::{t}::{nm}"
        for m, ln, t, nm, v in (rows() if _rows is None else _rows)
        if v == "UNUSED"
    }


def nonexports(_rows=None):
    """Rows for the HARD half — a name its target does not export."""
    return [
        (m, ln, t, nm)
        for m, ln, t, nm, v in (rows() if _rows is None else _rows)
        if v == "NONEXPORT"
    ]


def main():
    if (
        rc := ratchet.check_argv(
            sys.argv, {"--quiet", "--list", "--selftest", "--progress"}, "check_clause_audit.py"
        )
    ) is not None:
        return rc
    quiet = "--quiet" in sys.argv
    # ⚑ A DURATION IS A MEASUREMENT; "NO OUTPUT" IS NOT.  This gate does one long
    # opaque call, so without this it is indistinguishable from a hang — which is
    # exactly how it was read.  `--progress` reports to STDERR (the gate's stdout is
    # its verdict, and the hook tees it into the commit message) both that the scan
    # STARTED and how long it took, so "slow" and "wedged" become different
    # observations.  Off by default: the pre-commit path stays quiet.
    progress = "--progress" in sys.argv
    t0 = time.monotonic()
    if progress:
        print(
            "clause-audit: scanning every import clause under agda/Substrate/** "
            "(def-index + re-export index + per-module comment mask)…",
            file=sys.stderr,
            flush=True,
        )

    # ⚑ ONE SCAN, BOTH VERDICTS.  See `rows()` — these two partitions used to drive
    # two full scans.
    all_rows = rows()
    if progress:
        n_un = sum(1 for r in all_rows if r[4] == "UNUSED")
        n_nx = sum(1 for r in all_rows if r[4] == "NONEXPORT")
        n_uk = sum(1 for r in all_rows if r[4] == "UNKNOWN")
        print(
            f"clause-audit: scan complete in {time.monotonic() - t0:.1f}s — "
            f"{len(all_rows)} clause name(s): {n_nx} NONEXPORT, {n_un} UNUSED, "
            f"{n_uk} UNKNOWN (UNKNOWN is neither gated nor censused)",
            file=sys.stderr,
            flush=True,
        )

    # ⚑ THE HARD GATE RUNS FIRST AND IS NOT A RATCHET.  A latent build failure is
    # not debt to be capped at its current level — it is a break that has not
    # surfaced yet, so the only correct baseline is zero.
    bad = nonexports(all_rows)
    if bad:
        print(f"clause-audit: {len(bad)} clause name(s) NAME A NON-EXPORT")
        for m, ln, t, nm in bad:
            print(f"   {m}:{ln}\t{t}\t{nm}")
        print(
            "A `using`/`renaming` naming something its target does not export "
            "is only a WARNING in agda: the"
        )
        print(
            "name binds NOTHING and the build fails at the USE site, elsewhere. "
            "Bind the name at its real"
        )
        print(
            "home (`agda_defs <name>` resolves it) — do not delete the use site, "
            "and do not add an exemption."
        )
        return 1
    if not quiet:
        print("clause-audit: 0 non-export clause names (hard gate)")

    return ratchet.set_ratchet(
        census(all_rows),
        BASELINE,
        "clause-unused",
        quiet,
        list_keys="--list" in sys.argv,
        noun="dead clause entry/entries (exported, never used)",
        refuse_hint="A clause entry naming something the file never uses is dead "
        "weight that makes the clause look load-bearing. REMOVE the "
        "entry (or drop the whole clause — the ban wants it gone "
        "anyway); do not add an exemption.",
    )


def _selftest():
    """Counted from len(cases)."""
    cases = []

    def check(name, got, want):
        cases.append((name, got == want, got, want))

    # ⚑ THE GATE MUST DELEGATE, NOT RE-DERIVE.  The defect this guards against is
    # a second census under a shared name drifting from the first — measured in
    # this repo as `agda_files()` existing as four bodies, two feeding gates.
    # ⚑ THE SCAN IS COUNTED, NOT JUST REUSED.  The duplication this guards against was
    # invisible for as long as it existed because both callers were individually
    # correct; only the COMPOSITION was wrong.  A property that is expensive and
    # invisible needs a case, or the next refactor reintroduces it — so wrap the
    # authority and assert the call COUNT, which is the quantity that actually
    # regressed. (`_ROWS` is reset so this measures a cold run, not the memo.)
    global _ROWS
    _ROWS = None
    _real, calls = agda_defs.clause_audit, []

    # ⚑⚑ THE STUB MIRRORS THE AUTHORITY'S SIGNATURE, AND OMITTING THAT BROKE THE SUITE
    # (Ⓝ24, measured immediately). `clause_audit` gained an optional `on_module=`; this
    # double still took none, so the first `rows()` raised `TypeError: _counted() got an
    # unexpected keyword argument`. That is the ⟡fix-owes-callers class caught by a case
    # instead of by the census — a widened signature whose CALLER-SHAPED DOUBLE was not
    # updated with it. `**kw` rather than a named parameter: the double's job is to count
    # calls, not to re-declare an interface it would then have to track.
    def _counted(*a, **kw):
        calls.append(1)
        return _real(*a, **kw)

    agda_defs.clause_audit = _counted
    try:
        all_rows = rows()
        census(all_rows)
        nonexports(all_rows)
        rows()  # a second consumer must hit the memo, not the scan
    finally:
        agda_defs.clause_audit = _real
    check("the full clause scan runs EXACTLY ONCE per process", len(calls), 1)

    check(
        "the census delegates to the agda_defs authority", all(len(r) == 5 for r in all_rows), True
    )
    check(
        "...and partitions cleanly by verdict",
        {r[4] for r in all_rows} - {"NONEXPORT", "UNUSED", "UNKNOWN"},
        set(),
    )

    # ⚑ UNKNOWN IS NEITHER GATED NOR CENSUSED.  It means the provision set is
    # genuinely open (a re-exporter, or `mutual`/`abstract` the column-0 index
    # cannot see), which is a fact about the METHOD.  Banking it as debt would
    # put keys in a paydown-only baseline that can never legitimately be paid.
    keys = census(all_rows)
    check("UNKNOWN rows are not banked as debt", any("::" in k for k in keys) or not keys, True)
    check(
        "the ratchet census holds only UNUSED",
        len(keys),
        len([r for r in all_rows if r[4] == "UNUSED"]),
    )

    # ⚑ THE HARD HALF IS SEPARATE FROM THE RATCHET, and that separation is the
    # point: a latent build failure must not be capped at its current level.
    check(
        "the hard gate reads only NONEXPORT",
        len(nonexports(all_rows)),
        len([r for r in all_rows if r[4] == "NONEXPORT"]),
    )

    # keys must carry all four parts — a two-part key collides across clauses in
    # one module and would make a real regression read as no change.
    check(
        "every census key carries module:line::target::name",
        all(k.count("::") == 2 and ":" in k.split("::")[0] for k in keys),
        True,
    )

    fails = [c for c in cases if not c[1]]
    for name, _ok, got, want in fails:
        print(f"FAIL {name}: got {got}, want {want}")
    if fails:
        return 1
    print(f"check_clause_audit selftest: {len(cases)}/{len(cases)} OK")
    return 0


if __name__ == "__main__":
    sys.exit(_selftest() if "--selftest" in sys.argv else main())
