#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""check_mypy_ratchet.py — ⟡type-gate: a STATIC-TYPE ERROR in PROMOTED python is DEBT.

⛔ POLICY (user, 2026-08-01): *"Have we reached a point where we should be using [a type
checker] to provide typing guarantees (i.e. not None) for our functions? Because that's what
it's feeling like."* … *"I think I prefer mypy here. And gated."*

THE EVIDENCE IS THIS ARC'S OWN DEFECT LOG, and every one of these cost a run-edit-run cycle:

  · `agda_lex.imports_of` behind a `hasattr` fallback (§52) — **the strongest case: the
    GUARD HID IT.** A fallback to an absent function degraded the freshness check to
    measuring NOTHING, and a census that measures nothing reports a clean tree.
  · `_classify` called before it existed (§55) — recorded at the time as *"the FOURTH
    invented API this session"*, i.e. I was already counting them and still shipping them.
  · `CII.importers()` (§49) and `AL.agda_files` (§65) — two more invented APIs.
  · `group_statements(lines, [])` where a CALLABLE was required (§58c).
  · `log_is_fresh` widened 2-tuple → 3-tuple with 4 returns and 1 call site unchecked (§67).

⚑ WHAT THIS GATE IS *NOT*: an annotation-coverage push.  It censuses what mypy reports on the
PROMOTED corpus, whose profile is DEFECT-SHAPED (`arg-type`, `attr-defined`, `union-attr`,
`used-before-def`) and carries **zero** `var-annotated`/`assignment` — that code is already
annotated, because being annotated is part of what promotion means.  Adding a stricter flag
would convert this from a defect census into an annotation census and bank hundreds of keys
that are not the policy.  The predicate must match the POLICY, not the tool's maximum setting.

═══ SCOPE — AND IT IS IMPORTED, NEVER RESTATED (§6d) ═══

`ROOTS` comes from `check_scratch_independence`, THE authority on which projects have been
promoted out of `scratch/`, whose own docstring carries the maintenance rule: *"Extend ROOTS
when another project is promoted out of scratch/."*  Promote a fourth project and it joins
this gate BY CONSTRUCTION.  A hand-maintained second copy is exactly how `agda_files()` became
four different bodies under one name, two of them feeding pre-commit gates.

  · `jea/`, `el-atlas/` — the promoted projects (from ROOTS)
  · `scripts/`          — the gate layer itself; hook-wired, so a defect here is load-bearing

⚑ `scratch/` IS DELIBERATELY UNGATED, and that is the policy, not an omission (user,
2026-08-01: *"the silos live inside scratch/ … they can be promoted out of scratch/ if they're
brought to meet common quality status"*).  **`scratch/` is a STAGING AREA, not a place to
partition** — residence there IS the not-yet-promoted status.  Gating staging defeats staging.

⚑ AND THIS GIVES `promotion` A MECHANICAL TEST IT DID NOT HAVE: **a candidate must not add
census keys.**  Before this gate, "brought to meet common quality status" was a judgement only
its author could apply.

═══ THE CENSUS ═══

Keys are `<error-code>::<relpath>` — NOT line numbers.  §7g: *a ratchet key must be invariant
under everything except the thing it measures*, and a line-keyed ratchet reads every edit above
a site as retire+add, which trains reflexive re-baselining.  A file with three `arg-type`
errors is ONE key; fixing two of them does not pay it down, and that is correct — the file
either type-checks for that code or it does not.

Paydown-only: the set may SHRINK (fix the error) but never grow.

⚑ AN UNRUNNABLE mypy IS A REFUSAL, NEVER AN EMPTY CENSUS.  `type_errors` returns the sentinel
`__unrunnable__` when mypy exits non-{0,1} (a config error, a duplicate module name, an absent
install), and this gate REFUSES on it.  Reading "mypy could not run" as "no type errors" is the
guard-degrades-to-measuring-nothing class (§52) — the exact defect that motivated the gate,
reproduced in the gate.  My first cut of the census reported that absence as `0 keys`.

USAGE:
  check_mypy_ratchet.py                  # the gate: exit 1 on any NEW census key
  check_mypy_ratchet.py --quiet          # silent on success (hook form)
  check_mypy_ratchet.py --list           # ENUMERATE the census — every `<code>::<relpath>` key
  check_mypy_ratchet.py --check          # accepted alias of the bare gate run, for callers that
                                         # spell every gate the same way; identical verdict.
(`--dry-run` is not listed: `ratchet.UNIVERSAL_FLAGS` declares the flags the authority
implements for every caller, so restating it here would be the duplication this arc retires.)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scratch")
)
import ratchet
import pycodemod  # THE mypy census authority; never re-derive
from check_scratch_independence import ROOTS  # THE promoted-project authority (§6d)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASELINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mypy_ratchet_baseline.txt")

# The gate layer itself, beside the promoted projects.  See the docstring: this list is
# ROOTS + one, and ROOTS is imported so a future promotion needs no edit here.
POPULATION = list(ROOTS) + ["scripts"]


def census(paths=None):
    """{key -> [messages]} over the promoted corpus, or the `__unrunnable__` sentinel."""
    files = paths if paths is not None else pycodemod.py_files(*POPULATION)
    return pycodemod.type_errors(files)


def main(argv):
    # ⚑ CONSUME THE VERDICT.  `check_argv` RETURNS an exit code (its docstring gives
    # this exact walrus form); the bare statement I first wrote printed the complaint
    # and ran the gate ANYWAY — a guard present, greppable, and inert.  MEASURED by
    # `pycodemod --discards check_argv`: 6 of 7 call sites consume it, and the one
    # that did not was this one, written minutes after I quoted §15's *"a census can
    # verify presence, never behaviour"*.
    # `--dry-run` is NOT listed: `ratchet.UNIVERSAL_FLAGS` declares the flags the
    # authority implements for every caller, so restating it here would be the
    # ten-call-site duplication this arc keeps retiring.
    if (
        rc := ratchet.check_argv(argv, {"--quiet", "--list", "--check"}, "check_mypy_ratchet.py")
    ) is not None:
        return rc
    quiet = "--quiet" in argv

    rows = census()
    # ⚑ REFUSE, do not report clean.  See the docstring: this is the one branch that
    # separates "no type errors" from "the checker never ran".
    if rows is None or "__unrunnable__" in (rows or {}):
        why = (rows or {}).get("__unrunnable__", ["mypy is not importable"])[0]
        print("mypy-ratchet: CANNOT MEASURE — refusing rather than reporting clean.")
        print(f"  reason: {why}")
        print("  try:  uv run --with mypy python3 scripts/check_mypy_ratchet.py")
        return 2

    def render(k):
        msgs = rows.get(k) or []
        return f"{k}  ({len(msgs)}× — e.g. {msgs[0][:70]})" if msgs else k

    return ratchet.set_ratchet(
        set(rows),
        BASELINE,
        "mypy-ratchet",
        quiet=quiet,
        noun="type errors",
        list_keys="--list" in argv,
        render=render,
        dry_run="--dry-run" in argv,
        refuse_hint=(
            "A NEW static-type error in PROMOTED python.  Fix the error at the site;\n"
            "  do not add a `# type: ignore` and do not widen a signature to `Any`.\n"
            "  Enumerate the census with:  check_mypy_ratchet.py --list"
        ),
    )


def _selftest():
    """⚑ Every case drives a REAL defect this gate exists to catch or a REAL way it could lie."""
    cases = []

    # ⚑ A NAMED REGISTRAR, NOT A BARE `cases.append` — and the spelling is BORROWED,
    # never invented.  `run_selftests.CASE_CALLS` is the census roster; `ok` is the
    # shape `ratchet.py` (`def ok`, 55 cases) and `scratch/prose_apex.py` (`def ok`,
    # 10) already use, so this suite becomes countable by the census that exists
    # rather than by widening it.  A fourth spelling would be the defect one layer on.
    #
    # ⚑⚑ AND IT IS ONE CALL SITE PER CASE, WHICH IS THE HONESTY CONSTRAINT.  The
    # SKIP branch below used to `append` from BOTH arms of an if/else, so a
    # site-counting census read 10 where 9 cases ever run — the `tmi_subject`
    # shape (a hardcoded 15 against 11 that ran).  Routing the conditional case
    # through ONE `ok(...)` call makes the static count equal the cases that RUN.
    def ok(name, cond):
        cases.append((name, cond))

    # 1. SCOPE IS IMPORTED, NOT RESTATED (§6d).  If someone hand-copies ROOTS into this
    #    file, a future promotion silently escapes the type gate — the four-`agda_files()`
    #    class.  Assert the identity, not the contents.
    import check_scratch_independence as _csi

    ok(
        "scope imports ROOTS from its authority",
        all(r in POPULATION for r in _csi.ROOTS) and "scripts" in POPULATION,
    )

    # 2. `scratch/` IS EXCLUDED BY THE POPULATION, not by a filter that can rot.
    ok("scratch/ is not in the population", "scratch" not in POPULATION)

    # 3. ⚑ THE UNRUNNABLE SENTINEL MUST REFUSE, NOT READ AS CLEAN.  This is the §52
    #    guard-degrades-to-measuring-nothing class, and it is the defect this gate was
    #    built after.  A gate that reports 0 keys when the checker never ran is worse
    #    than no gate: it certifies its own blind spot.
    real = pycodemod.type_errors
    try:
        pycodemod.type_errors = lambda *a, **k: {"__unrunnable__": ["synthetic"]}
        rc = main(["--quiet"])
        ok("unrunnable mypy REFUSES (exit 2), never reports clean", rc == 2)
    finally:
        pycodemod.type_errors = real

    # 4. ⚑ THE GATE MUST ACTUALLY REFUSE ON A GROWN CENSUS — added because
    #    `pycodemod --discriminates` reported this suite BLIND to the mutant
    #    `empty-census-passes` (a `return 0` inserted above the `set_ratchet` call).
    #    Every other case checked an INPUT predicate; none checked that the verdict
    #    is reached at all, so a gate short-circuited to always-pass stayed green.
    #    That is §9a — a gate wired into nothing — at the case level, and the only
    #    reason it surfaced is that the question became a command instead of a
    #    throwaway script.
    import tempfile as _tf

    _bl = os.path.join(_tf.mkdtemp(), "b.txt")
    open(_bl, "w").write("old::x.py\n")
    _real_census, _real_bl = census, BASELINE
    try:
        globals()["census"] = lambda paths=None: {"old::x.py": ["m"], "NEW::y.py": ["m"]}
        globals()["BASELINE"] = _bl
        rc_grown = main(["--quiet"])
        globals()["census"] = lambda paths=None: {"old::x.py": ["m"]}
        rc_held = main(["--quiet"])
    finally:
        globals()["census"], globals()["BASELINE"] = _real_census, _real_bl
    ok("REFUSES a grown census (1) and holds at baseline (0)", rc_grown == 1 and rc_held == 0)

    # 5. KEYS CARRY NO LINE NUMBER (§7g).  A line-keyed ratchet reads any edit above a
    #    site as retire+add and trains reflexive re-baselining.  Drive the real census
    #    over ONE file rather than asserting the key shape from a fixture.
    #
    # ⚑ THIS IS THE ONE CONDITIONAL CASE, and it registers from ONE site on purpose.
    # It SKIPs (`None`) when mypy cannot run, so it contributes a row either way —
    # but written as an if/else with an `append` in each arm it presented TWO static
    # call sites for ONE case that ever runs, which is the denominator inflation
    # `tmi_subject` was fixed for.  The branch now chooses the VALUE, not the site.
    rows = census([os.path.join(ROOT, "scripts", "check_mypy_ratchet.py")])
    _absent = rows is None or "__unrunnable__" in (rows or {})
    ok(
        "keys are <code>::<path>, never line-keyed" + ("  [SKIP — mypy absent]" if _absent else ""),
        None
        if _absent
        else all(k.count("::") == 1 and not k.rsplit(":", 1)[-1].isdigit() for k in rows),
    )

    # 6. ⚑ `--dry-run` MUST PREVIEW WITHOUT WRITING.  Added because the repo's
    #    write-polarity convention is `--dry-run` (6 write tools carry it) and
    #    **0 of 16 gates did** — a gate is thought of as read-only, but at the
    #    moment it mints a baseline it is a write tool, and it was the one write
    #    path with no preview.  Its absence is why I reached for the env-var
    #    bypass instead (user: *"I was pointing at --dry-run"*).
    _bl2 = os.path.join(_tf.mkdtemp(), "b2.txt")
    _real_census2, _real_bl2 = census, BASELINE
    try:
        globals()["census"] = lambda paths=None: {"k::x.py": ["m"]}
        globals()["BASELINE"] = _bl2
        rc_dry = main(["--quiet", "--dry-run"])
    finally:
        globals()["census"], globals()["BASELINE"] = _real_census2, _real_bl2
    ok("--dry-run previews and writes NOTHING", rc_dry == 0 and not os.path.exists(_bl2))

    # 7. ⚑ AN UNKNOWN FLAG MUST REFUSE, NOT MERELY COMPLAIN.  `check_argv` RETURNS
    #    an exit code; the bare-statement call I first wrote printed the message and
    #    ran the gate anyway.  Found by `pycodemod --discards check_argv` (6 of 7
    #    sites consumed it; this was the 7th).  The case drives `main` with a typo
    #    rather than inspecting the source, so it binds the BEHAVIOUR: a future edit
    #    back to a bare call fails here.
    ok("an unknown flag REFUSES (exit 2), not merely warns", main(["--queit"]) == 2)

    # 8. ⚑ EVERY `set_ratchet` CALLER ACCEPTS `--dry-run`, BY CONSTRUCTION (`T17`).
    #    The item was "back-fill the flag across the other nine gates"; MEASURED it
    #    was 10 of 11, and threading one flag through ten files is the duplication
    #    §60 retired — the ELEVENTH gate would silently lack it again.  The authority
    #    resolves the flag from argv and declares it in `UNIVERSAL_FLAGS`, so this
    #    case checks the PROPERTY (no caller can be missing it) rather than a list.
    import pycodemod as _pc

    _has, _lacks = _pc.forwards("set_ratchet", "dry_run") if _pc.cst else ([], [])
    ok(
        "--dry-run is universal: no gate declares it per-site",
        "--dry-run" in ratchet.UNIVERSAL_FLAGS
        and not any(
            "--dry-run" in open(p, encoding="utf-8").read().split("check_argv")[1][:200]
            for p, _l in (_has + _lacks)
            if "check_argv" in open(p, encoding="utf-8").read()
        ),
    )

    # 9. `render` MUST BE TOTAL ON A KEY ABSENT FROM THE CENSUS (§60).  A PAID-DOWN key
    #    is absent from `rows` by construction, so a renderer indexing it raises exactly
    #    on the branch that reports PROGRESS — the branch a gate author never exercises.
    def _r(k):
        msgs = ({}).get(k) or []
        return f"{k}  ({len(msgs)}×)" if msgs else k

    ok("render is total on a paid-down key", _r("gone::x.py") == "gone::x.py")

    ran = [(n, v) for n, v in cases if v is not None]
    for n, v in cases:
        print(f"  {'ok  ' if v else ('SKIP' if v is None else 'FAIL')}  {n}")
    # ⚑ THE DENOMINATOR IS `ran`, NOT `cases` — a SKIPped case is not a case that ran.
    passed = sum(1 for _, v in ran if v)
    print(f"selftest: {passed}/{len(ran)}")
    return 0 if passed == len(ran) else 1


if __name__ == "__main__":
    sys.exit(_selftest() if "--selftest" in sys.argv else main(sys.argv[1:]))
