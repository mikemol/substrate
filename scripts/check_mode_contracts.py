#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""check_mode_contracts.py — a CLI mode's declaration and its dispatch are TWO
SPELLINGS; ratchet the disagreement down.

⚑⚑ WHY THIS GATE EXISTS, AND IT IS THE `census-keyed-on-one-spelling` SHAPE.  A tool
declares its modes in a roster (`MODES = {"--flag": Mode(...)}`) and dispatches them in
`_dispatch` (`if "--flag" in sys.argv:`).  Nothing compared the two, so both directions
drifted silently:

  * DISPATCHED, UNDECLARED — a mode that runs with UNDECLARED ARITY.  The entry point
    reads operand arity from the roster, so an absent row means the arg-stripper guesses:
    `--key --archive f.py` CRASHED because `--key`'s operand was bound as a tarball path.
    Measured 2026-08-19: 25 of 57 modes in `pycodemod.py` alone, several whose usage text
    exists ONLY as a runtime `print` inside their own branch — help reachable exclusively
    by getting the call wrong.
  * DECLARED, NEVER DISPATCHED — a promise the CLI does not keep, and the more dangerous
    direction: a phantom row still feeds arity resolution and can bind a real operand as
    a flag's argument.

⚑ THE READER ALREADY EXISTED AND WAS GATED BY NOTHING.  `pycodemod --check-contracts`
(`scan_contract`) has reported both directions plus the `scans=True` conformance check
for days; `--calls` put it at 0 call sites, reachable only from its own CLI.  A red
verdict nobody runs is not a gate — which is the whole reason this file is a four-line
wrapper rather than a new analysis.  The authority stays in the tool that owns the
artifact kind; this only makes it BITE.

CENSUS (materialized from the tree, not a frozen list): the SET of keys
`<tool>::<flag>::<kind>` for every roster/dispatch disagreement and every unhonoured
behavioural contract.  This set is DEBT — it may only be PAID DOWN (declare the mode,
delete the phantom row, honour the contract), never grown.  A paydown auto-lowers the
baseline.  RATCHET semantics + I/O are the shared `scripts/ratchet.py`.

⚑ A BASELINE, NOT A CLEAN ZERO, AND DELIBERATELY SO.  `pycodemod` is at 6 — the
⟡mode-dual-role set, six flags that are BOTH a declared modifier (`OPT_OPERANDS`, operand
read by `argopt` and stripped from `args`) AND a dispatch branch (operand read
positionally from `args[0]`).  Conflating those two kinds "broke every query mode for ten
minutes" per `_dispatch`'s own record, so they are a genuine unresolved design question,
not an unpaid row.  Grandfathering them is what lets the gate refuse the NEXT one today
instead of after that question is settled (`policy_is_a_ratchet_over_census`).

Blocking gate. Exit 0 = clean, 1 = a new disagreement appeared.
Usage: check_mode_contracts.py [--quiet] [--list] [--where] [--selftest]

⚑ `--selftest` EXISTS AS OF 2026-08-24 AND DID NOT BEFORE (gate-F7, ⟡selftest-record).
This gate ratchets other tools' declarations against their dispatch and had no declaration
of its own, so the standing instruction *"run the selftest after you change it"* was a
NON-COMMAND against this very file — the flag refused as unknown.
"""

import os
import sys

import ratchet

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASELINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mode_contracts_baseline.txt")

#: Tools whose mode roster is the `Mode(...)` shape and can therefore be checked.
#: ⚑ NOT A FROZEN ROSTER OF TOOLS — it is the population that has ADOPTED the standard,
#: and it grows as ⟡mode-standardize converts each one.  A tool absent here is not
#: exempt; it has no roster to check yet, which is a DIFFERENT state from checked-clean
#: and is why this list is explicit rather than a glob that would silently report 0.
#: (relpath, module, roster attribute) for every tool that has adopted the shape.
#: ⚑ ⟡mode-generic-contract CLOSED THE COVERAGE GAP THIS LIST USED TO RECORD.  Until the
#: reader was lifted into `climode.contract_rows`, only `pycodemod` could be checked — it
#: owned the one `scan_contract`, whose branch regex was that file's shape.  A roster
#: converted anywhere else was STANDARDISED but not CHECKED, contributing zero keys and
#: rendering exactly like a clean one.  Now the reader takes the roster as a parameter, so
#: adopting the shape and being held to it are the same act.
ADOPTED = (
    ("scratch/pycodemod.py", "pycodemod", "MODES"),
    ("jea/metalanguage/schema.py", "schema", "MODES"),
    ("jea/metalanguage/lifecycle.py", "lifecycle", "MODES"),
    ("jea/metalanguage/reconstruct.py", "reconstruct", "MODES"),
    ("jea/metalanguage/jea_pydecode.py", "jea_pydecode", "MODES"),
    # ⚑ Ⓢ1e — the first tool with NO prior roster: its modes lived only in a docstring,
    # and five dispatched in no usage line at all. Authored from the branches, not lifted.
    ("scratch/mdstruct.py", "mdstruct", "MODES"),
    # ⚑ the Agda-source authority: 23 modes had curated usage, 14 dispatched in none.
    # Its write set was derived from `--guarded guard` ⋈ `--binding apply`, never names.
    ("scratch/agda_defs.py", "agda_defs", "MODES"),
    # ⚑ Ⓟ5 ⟡procstruct-roster — the process census (⟡process-hygiene). Adopted the shape
    # at authorship rather than by conversion, so it lands here contributing zero keys;
    # that is the point of the explicit tuple — a glob could not tell "clean" from
    # "never checked", and this row is what makes the clean reading a CHECKED one.
    ("scratch/procstruct.py", "procstruct", "MODES"),
)


def census():
    """{tool::flag::kind} — every roster/dispatch disagreement across adopted tools.

    ⚑ THE VERDICT IS THE OWNING TOOL'S, RE-DERIVED PER RUN.  This does not reimplement
    `scan_contract`; it imports it.  A second analysis here would be the roster-beside-a-
    roster shape the toolkit exists to retire, and it would drift from the one the tool's
    own `--check-contracts` prints.
    """
    import climode

    keys = set()
    sys.path.insert(0, os.path.join(ROOT, "scratch"))
    sys.path.insert(0, os.path.join(ROOT, "jea", "metalanguage"))
    for rel, modname, attr in ADOPTED:
        src = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        roster = getattr(__import__(modname), attr)
        for flag, ok, why in climode.contract_rows(src, roster):
            if ok:
                continue
            keys.add("%s::%s::%s" % (rel, flag, kind_of(ok, why)))
    return keys


def cmd_where():
    """Print each finding's BRANCH LOCATION — the line a paydown must open.

    ⚑⚑ WRITTEN BECAUSE I GUESSED FOUR CALLEE NAMES IN A ROW TRYING TO FIND THEM BY HAND.
    The gate names WHICH modes disagree and says nothing about WHERE, so paying one down
    meant hunting the branch with `--literal` / `--guarded` probes against names I did not
    know existed — `--literal "--establish"` kept matching the file PATH, `--guarded
    require_indexes` returned 0 of 0. Four calls, no location, and every one of them was
    judgement happening in the turn.

    ⚑ AND THE ANSWER WAS ALREADY COMPUTED. `climode.branch_bounds` derives exactly this to
    do its own work and threw it away. A census that reports a defect without exposing the
    structure needed to fix it leaves the paydown to be re-derived by hand, differently,
    every time — the same reason `pycodemod --layout` exists beside `--size`.
    """
    import climode

    sys.path.insert(0, os.path.join(ROOT, "scratch"))
    sys.path.insert(0, os.path.join(ROOT, "jea", "metalanguage"))
    n = 0
    for rel, modname, attr in ADOPTED:
        src = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        roster = getattr(__import__(modname), attr)
        bounds = climode.branch_bounds(src)
        rows = [(f, why) for f, ok, why in climode.contract_rows(src, roster) if not ok]
        if not rows:
            continue
        print("── %s" % rel)
        for flag, why in rows:
            at = bounds.get(flag)
            # ⚑ A MISSING BOUND IS ITS OWN FACT — a phantom row has no branch to open, and
            # printing a blank line number would read as line 0 rather than "nowhere".
            where = "%s:%d" % (rel, at[0] + 1) if at else "(no branch — declared only)"
            print("   %-14s %-42s %s" % (flag, where, why[:60]))
            n += 1
    print("%d finding(s) located across %d adopted roster(s)" % (n, len(ADOPTED)))
    return 0


def kind_of(ok, why):
    """The census key's KIND from one `contract_rows` verdict — the classifier, LIFTED.

    ⚑⚑ IT WAS AN INLINE CHAIN INSIDE `census()`, i.e. UNREACHABLE FROM A CASE — the exact
    shape `run_selftests.verdict_kind` records about itself (*"it is a function so a case
    can reach it"*) and the same one that let `rename_at_source` ship a live write-path bug
    through a green run. This decides which bucket every debt key lands in, keyed on
    SUBSTRINGS of another module's message text, and nothing could drive it.

    ⚑ AND THE SUBSTRINGS ARE A CROSS-MODULE COUPLING NOBODY DECLARED. `climode.contract_rows`
    owns the wording; this reads it. Reword a message there and every key here silently
    becomes `contract`, which auto-lowers one bucket and grows another — a baseline that
    moves without the tree moving. The cases below pin the four phrases against the live
    messages, so a reword FAILS here instead of quietly re-bucketing the census.
    """
    # ⚑ `ok is None` IS *UNKNOWN*, NOT PASS — an unlocatable branch is a fact about the
    # reader, and banking it as clean is the confident-zero shape `scan_contract`'s own
    # docstring refuses. Both are debt here.
    return (
        "unknown"
        if ok is None
        else "undeclared"
        if "absent from the roster" in why
        else "phantom"
        if "never dispatched" in why
        else "silent-write"
        if "silent default" in why
        else "contract"
    )


def _selftest():
    """The guarded cases.

    ⚑⚑⚑ THIS GATE HAD NO SUITE AT ALL, AND THAT MADE A STANDING INSTRUCTION A NON-COMMAND
    (gate-F7, ⟡selftest-record). "Run the selftest after you change it" was issued for this
    file this session and `check_mode_contracts.py --selftest` REFUSES as an unknown flag —
    so a gate that ratchets other tools' declarations against their dispatch had no
    declaration of its own, and its classifier was untestable by construction.
    """
    import climode

    cases, ok_n = [], 0

    def check(name, got, want):
        nonlocal ok_n
        cases.append(name)
        if got == want:
            ok_n += 1
        else:
            print(f"  FAIL {name}: got {got!r} want {want!r}")

    # ── kind_of: the four buckets, against the LIVE message text ────────────────
    # ⚑ EACH `want` IS DRIVEN THROUGH `climode.contract_rows` RATHER THAN A PASTED STRING.
    # A case asserting `kind_of(False, "absent from the roster") == "undeclared"` tests only
    # that I can retype my own substring; it passes forever while the real message drifts
    # out from under it. Generating the message from the authority is what makes a reword
    # fail HERE instead of silently re-bucketing the census.
    _und = climode.contract_rows('if "--w" in sys.argv:\n    go()\n', {})
    check(
        "a DISPATCHED-undeclared verdict buckets as `undeclared`",
        {kind_of(o, w) for _f, o, w in _und},
        {"undeclared"},
    )
    _phan = climode.contract_rows("x = 1\n", {"--gone": climode.Mode()})
    check(
        "a DECLARED-never-dispatched verdict buckets as `phantom`",
        {kind_of(o, w) for _f, o, w in _phan},
        {"phantom"},
    )
    _sil = climode.contract_rows(
        'if "--w" in sys.argv:\n    write()\n', {"--w": climode.Mode(writes=("store",))}
    )
    check(
        "a silent-default writer buckets as `silent-write`",
        {kind_of(o, w) for _f, o, w in _sil},
        {"silent-write"},
    )
    # ⚑⚑ ONE FLAG YIELDS TWO ROWS HERE, AND MY FIRST CASE ASSERTED ONE — measured on the
    # first run of this suite. An undispatched `scans=True` mode is BOTH `unknown` (the
    # reader could not locate its branch) and `phantom` (declared, never dispatched): two
    # true findings about one flag, and the census keys them separately BY DESIGN, since
    # `tool::flag::kind` includes the kind. `climode._selftest` records the same trap one
    # layer down (*"one flag can yield several rows... my first cut used a dict
    # comprehension, so the LAST row silently won"*), and I walked into it from the other
    # side by asserting the set was a singleton.
    _unk = climode.contract_rows("x = 1\n", {"--nowhere": climode.Mode(scans=True)})
    check(
        "an UNKNOWN branch buckets as `unknown`, never as clean",
        "unknown" in {kind_of(o, w) for _f, o, w in _unk},
        True,
    )
    check(
        "...and the same flag ALSO keys as a phantom — two true findings, two keys",
        {kind_of(o, w) for _f, o, w in _unk},
        {"unknown", "phantom"},
    )
    # ⚑ THE FALLBACK MUST BE REACHABLE AND MUST NOT SWALLOW THE OTHERS. A classifier whose
    # last arm catches everything would still pass the four cases above if the arms were
    # reordered wrongly — this pins the residue explicitly.
    check(
        "an unrecognised message falls back to `contract`",
        kind_of(False, "declares scans=True but never calls _report_skipped("),
        "contract",
    )

    # ── the census: shape, and that it reports its own boundary ────────────────
    # ⚑ A GREEN GATE MUST NOT IMPLY COVERAGE IT DOES NOT HAVE. `ADOPTED` is the population
    # that CAN be checked; a tool absent from it is not exempt, it is unreadable — and the
    # two render identically at a zero.
    check(
        "every adopted entry is a (relpath, module, attr) triple",
        all(len(e) == 3 for e in ADOPTED),
        True,
    )
    check(
        "...and every relpath exists",
        [r for r, _m, _a in ADOPTED if not os.path.exists(os.path.join(ROOT, r))],
        [],
    )
    _keys = census()
    check(
        "the census returns a SET (a count cannot catch swap-gaming)", isinstance(_keys, set), True
    )
    # ⚑ EVERY KEY IS `tool::flag::kind`, and the kind is one the reader knows. A key whose
    # kind fell out of the classifier's vocabulary would ratchet as a NEW key forever.
    _KINDS = {"unknown", "undeclared", "phantom", "silent-write", "contract"}
    check(
        "every census key is tool::flag::kind with a known kind",
        {k.split("::")[2] for k in _keys} - _KINDS,
        set(),
    )
    check(
        "...and every key names an ADOPTED tool",
        {k.split("::")[0] for k in _keys} - {r for r, _m, _a in ADOPTED},
        set(),
    )

    # ⚑ THE GATE IS WIRED TO THE RATCHET, not merely described. A census computed and never
    # handed to `set_ratchet` is the `rewire_only` shape — the docstring would read as a
    # policy while nothing gated.
    import inspect as _insp

    _msrc = _insp.getsource(main)
    check(
        "main() runs the census through the paydown ratchet",
        "set_ratchet(" in _msrc and "census()" in _msrc,
        True,
    )
    check("...and against THIS gate's baseline", "BASELINE" in _msrc, True)
    # ⚑ AND `census()` USES THE LIFTED CLASSIFIER rather than a second copy of it. The whole
    # reason `kind_of` exists is that the chain was unreachable from a case — leaving a copy
    # inline would mean the cases test a function the gate does not call.
    check(
        "census() routes through kind_of, not an inline copy",
        "kind_of(" in _insp.getsource(census),
        True,
    )

    _R = ok_n == len(cases)
    print(f"selftest: {ok_n}/{len(cases)}")
    return _R


def main():
    if (
        rc := ratchet.check_argv(
            sys.argv, {"--quiet", "--list", "--where", "--selftest"}, "check_mode_contracts.py"
        )
    ) is not None:
        return rc
    if "--where" in sys.argv:
        return cmd_where()
    quiet = "--quiet" in sys.argv
    # ⚑ A GREEN GATE MUST NOT IMPLY COVERAGE IT DOES NOT HAVE. `census-green-is-a-fact-
    # about-the-census`: a converted-but-unchecked roster contributes zero keys, which
    # renders exactly like a checked-clean one. Naming the population keeps "the gate
    # found nothing" apart from "the gate cannot see it yet".
    if not quiet:
        print(
            "   %d adopted roster(s) checked: %s"
            % (len(ADOPTED), ", ".join(r for r, _m, _a in ADOPTED))
        )
    return ratchet.set_ratchet(
        census(),
        BASELINE,
        "mode-contracts",
        quiet,
        list_keys="--list" in sys.argv,
        noun="mode roster/dispatch disagreement(s)",
        refuse_hint="Declare the mode in MODES (`pycodemod --declare-modes` emits the "
        "skeleton with arity already derived), delete the phantom row, or "
        "honour the contract the roster claims — do NOT widen the baseline.",
    )


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if _selftest() else 1)
    sys.exit(main())
