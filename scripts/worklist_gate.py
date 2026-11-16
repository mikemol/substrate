#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""worklist_gate.py — run the paperkit engine over `catalog/worklist/`.

⚑ WHY THIS EXISTS.  Paperkit is an ENGINE you point at a project directory, not
something to copy in.  But "point at" was a hand-assembled shell line —
`python3 ~/github/paperkit/paperkit/gate.py catalog/worklist` — which carries
three pieces of knowledge (where the engine lives, which of its entry points to
call, which directory is the project) in a string a human retypes.  That is the
same shape as the hand-built `membudget` invocation and the printed
`git checkout <sha> -- <path>` recovery command: a question the tooling did not
answer, answered by the operator.  This module owns all three.

    worklist_gate.py                 # GATE: are all cited claims discharged?
    worklist_gate.py --project       # PROJECT: regenerate WORKLIST.md
    worklist_gate.py --discriminate  # DELTA: does each witness actually discriminate?
    worklist_gate.py --items         # the per-item verdicts, without the engine
    worklist_gate.py --figures       # the live figures the items read
    worklist_gate.py --order         # the WARRANT GRAPH as a ranked row sequence
    worklist_gate.py --next          # just the head of that order — what to do NOW
    worklist_gate.py --solvers       # which TOOL solves each build-failure class
                                     # (SOLVED / MIXED / none — an unattached class is a
                                     #  measured finding, not a gap to paper over)
    worklist_gate.py --sweep <failure-class> [--apply] [--limit N]
                                     # the RUNNABLE half of --solvers: run that class's
                                     # tool over the class's module SET.  Dry by default.
    worklist_gate.py --dispatch <item-key>… [--apply]
                                     # the item's `parts` CHANNEL: which of its routes are
                                     # COMMANDS, and (only under --apply) run them.  The
                                     # witness runs first — `PARTS` is filled BY it, so
                                     # reading the channel without it reports a false empty.
    worklist_gate.py --engine        # WHERE paperkit resolved to, and what it ships.
                                     # The resolver existed and was unexposed; "where is
                                     # paperkit" was being answered with `ls`.
    worklist_gate.py --profile[=<target>]
                                     # the ITERATION-CYCLE instrument over ONE named
                                     # program — `order` (default), `selftest`, `items`.
                                     # ⚑ The target is NAMEABLE because a profile of the
                                     # wrong program is indistinguishable from an answer.
                                     # Value-bearing, so it follows the `--out=` convention.
    worklist_gate.py --discriminate --no-cache
                                     # ⚑ --no-cache is a MODIFIER on --discriminate, not a
                                     # mode: Delta memoizes each check on the content of the
                                     # files it read, and a cached verdict is
                                     # indistinguishable from a fresh one in the report body.
                                     # After editing a witness, forward it.

⚑ `--discriminate` IS THE ENGINE'S OWN Δ GRADER, and reaching past it was a
reuse-search miss: asked whether the item witnesses discriminate, I ran
`pycodemod --discriminates` — a tool whose four mutators are Agda-gate-shaped and
which correctly reported the question inapplicable.  Paperkit ships the grader
for exactly this, and it mutates the CLAIM, which is the thing a work item can
be wrong about.  Two graders, one question; the engine's owns it.

⚑ THE ENGINE IS LOCATED, NOT ASSUMED.  `PAPERKIT` is resolved from the
environment, then from the conventional checkout, and the module REFUSES with the
reason when it cannot find it — never a silent skip.  A gate that degrades to
measuring nothing is worse than one that fails (plan section 52).

⚑ AND THIS IS NOT YET HOOK-WIRED, DELIBERATELY.  `catalog/worklist.md` remains
the authoritative worklist through step 1; wiring the gate before the port is
complete would make a partial projection block commits.  Wiring it is step 4 of
the migration, at the same moment `catalog/worklist.md` is deleted.

⚑ THIS MODULE IS NOW THE ENTRY POINT AND THE SELFTEST, NOT THE WHOLE PROGRAM
(2026-08-11).  It was 1,458 code lines over 40 defs — past the 1200-line
threshold at which a file has to be patch-edited rather than read whole — so it
was split into four siblings, seamed by WHAT STATE EACH GROUP TOUCHES:

    wg_engine.py    the SUBPROCESS boundary: locating paperkit, the sandbox
                    that bounds Delta's scratch, running one entry point.
                    Knows nothing about what a worklist ITEM is.
    wg_order.py     the WARRANT GRAPH: layers, leverage at both grades, the
                    `Row` sequence.  The only group that walks a graph.
    wg_dispatch.py  the `parts` CHANNEL: which routes are commands, and the
                    `--apply`-gated execution of them.  The only group with an
                    execute blast radius.
    wg_profile.py   the ITERATION-CYCLE instrument.  306 lines whose only tie
                    to the rest was the target it runs.

What stayed here is what a CLI is: argument parsing, the printers, and the
selftest that drives every mode.  ⚑ EVERY PUBLIC NAME IS RE-EXPORTED BELOW, so
`worklist_gate.order()` still resolves — a decomposition that relocates an API is
a rename wearing a refactor's clothes.

⚑ AND THE SPLIT WAS OWED BY THE SIZE RULE, NOT BY THE LEASE.  This suite is one
of two that intermittently report `unfit` at a 192 MB membudget lease, and the
open question was whether that footprint came from SIZE.  MEASURED before and
after: importing the whole 1,458-line module cost 3.1 MB, and the `--selftest`
peak is ~190 MB — so the footprint is the WITNESS ROSTER that `order()` runs
twice (once via `items._drain` for openness, once via `reads()` for the
measurement footprint), not the line count of any file.  Splitting was correct
and did not move that number; claiming otherwise would be a memory win nobody
measured.  ⚑ ONE `_selftest` STILL LIVES HERE, DELIBERATELY: `run_selftests.py`
discovers modules that DEFINE `_selftest`, so giving each sibling its own would
have turned one suite into five — five leases, five process startups, and a suite
count that moves for a reason unrelated to coverage.  The cases drive the split
modules through this module's re-exports, which is also what keeps the
re-exports honest.
"""

# ⚑ THE STDLIB IMPORTS HERE ARE THE ONES THIS MODULE STILL USES, AND THE SPLIT
# IS WHAT MADE THAT CHECKABLE.  `builtins`, `collections`, `re` and `subprocess`
# moved out with the groups that used them (the `open()` spy, the `Row` tuple,
# the runnable-route predicate, the engine child) and are NOT re-imported here — a
# decomposition that leaves the old import block intact keeps every module
# looking like it still does the work its siblings took over.  What remains:
# `contextlib`/`io` for the selftest's stdout capture, `shutil`/`tempfile` for
# its scratch probe, `os`/`sys` throughout.
import contextlib
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import ratchet  # noqa: E402

# ⚑ THE RE-EXPORTS ARE THE PUBLIC SURFACE, HELD STILL ACROSS THE SPLIT.  Every
# name below was a top-level def in this file before 2026-08-11; a caller (and
# the selftest) still reaches it here.  `noqa: F401` because a re-export is a
# USE — the linter's "imported but unused" is exactly wrong about this line's
# purpose, and silencing it per-line says so rather than disabling the check.
import wg_engine
from wg_order import (  # noqa: E402,F401
    Row,
    _Rows,
    _content_size,
    _dagcone,
    _keychar,
    derived_failures,
    leverage,
    order,
    reads,
    waits_on,
)
from wg_dispatch import (  # noqa: E402,F401
    RUNNABLE_PREFIX,
    _item_parts,
    _item_why,
    class_modules,
    dispatch_parts,
    gates_reached,
    part_is_runnable,
    solvers,
    sweep,
)
from wg_profile import profile_order  # noqa: E402,F401


def _print_next(rows):
    """THE head of queue — one item, or the tiebreak that precedes it.

    ⚑ BUILT BECAUSE I KEPT READING IT OFF THE TABLE BY EYE (user: "how do we
    know the next tool is still T12 if we haven't asked the list?").  I had run
    `--order` and read the first open row — a judgement applied to program
    output, which is the shape this repo keeps retiring.  Worse, I then wrote
    "still T12", and "still" is a claim about CONTINUITY across an edit that the
    run does not make: the run reports a state, not that the state is unchanged.

    So the head is COMPUTED and named.  A caller never scans rows again, and
    there is no place for "still" to enter: each invocation reports what is
    true now, with no memory of what it said before."""
    if isinstance(rows, int):
        return rows
    # ⚑ THE TIEBREAK BRANCH IS GONE (2026-08-05, user).  `--next` used to lead
    # on an unadjudicated tie rather than an item; with the machinery retired it
    # names the head of queue directly.  Whether ties are worth reporting is a
    # question for AFTER the witness contract lands — answered by measurement,
    # not by keeping a disabled branch here.
    open_rows = [r for r in rows if r.is_open]
    if not open_rows:
        print("NEXT: nothing — every tracked item is closed.")
        return 0

    # ⚑ TIERS, NOT A HEAD PLUS ONE RUNNER-UP (user, 2026-08-05: *"we'll have it
    # report everything in tiers 1 and 2 ... where a tier is something that has
    # the same leverage and at the same layer"*).  A tier IS the ordering's
    # equivalence class: items agreeing on `(layer, leverage)` are ones the
    # ordering does not separate, and naming one of them as THE head implied a
    # precedence the keys do not carry.
    #
    # ⚑ AND THIS IS WHAT THE RETIRED TIEBREAKER WAS GROPING AT.  It treated a
    # tie as a DEFECT to adjudicate — ~170 lines proving an ordering incomplete
    # because two items agreed.  A tier is not a defect; it is the answer.
    # Reporting the class, with each member's own verdict, lets a reader choose
    # on the evidence instead of on prose about why the choice was hard.
    #
    # ⚑ TWO TIERS, because the second is what makes the first inspectable — the
    # same reason the runner-up existed.  Deeper tiers are the `--order` table's
    # job; `--next` answers "what is at the front", not "what is the queue".
    tiers = []
    for r in open_rows:
        k = (r.layer, r.lev)
        if not tiers or tiers[-1][0] != k:
            tiers.append((k, [r]))
        else:
            tiers[-1][1].append(r)

    # ⚑ A TIED TOP TIER HAS NO HEAD, AND THE HEADER MUST NOT INVENT ONE (user,
    # 2026-08-05: *"did you forget that we deliberately were surfacing tied
    # top-tier, followed by tier?"*).  I briefly "fixed" a failing selftest by
    # naming `members[0]` in the header — `NEXT: AA (+2 tied ...)`.  That is the
    # very precedence tiers exist to refuse: the ordering does not separate
    # these items, so privileging one BY LIST POSITION asserts a rank the keys
    # do not carry.  It made a red case green by re-collapsing the class.
    #
    # ⚑ THE CASE WAS THE STALE ARTIFACT, NOT THE PRESENTATION.  `--next names
    # the FIRST open row` predates tiers; its PURPOSE is catching `--next`
    # naming some ARBITRARY open row, and that purpose survives without the
    # `NEXT: <key>` string.  Restated as "the reported tier IS the top
    # (layer, leverage) class", it is strictly stronger — it pins membership
    # rather than one key — and it does not demand a head that does not exist.
    # Fixing the printer to satisfy a case is backwards when the case encodes
    # the contract the feature deliberately replaced.
    for i, ((_lay, _lev), members) in enumerate(tiers[:2]):
        _pfx = "NEXT" if i == 0 else "THEN"
        if len(members) > 1:
            print(
                "%s (%d items, layer %d, leverage %d — the ordering does not "
                "separate these):" % (_pfx, len(members), _lay, _lev)
            )
        for m in members:
            _print_row(m, head=(i == 0 and len(members) == 1))
    return 0


def _print_row(r, head=False):
    """One item's line: its key, its grades, its verdict, its breakdown."""
    print("NEXT: %s" % r.key if head else "  %s" % r.key)
    # ⚑ BOTH GRADES ARE PRINTED, because the comparison is graded.  "leverage 0"
    # alone would have made R12b look worthless next to B3's 8 — the grade-0
    # reading that ranked them interchangeable.  Naming the grade that DECIDED
    # is what makes the choice checkable rather than assertable.
    print(
        "  layer %d, leverage %d declared / %s evaluated%s%s"
        % (
            r.layer,
            r.lev,
            "BLOCKED" if r.graded else "actionable",
            ", size %d" % r.size if r.size else "",
            ", rests-on %s" % ", ".join(r.deps) if r.deps else "",
        )
    )
    # ⚑ THE VERDICT, FROM THE RUN THAT JUST HAPPENED.  Naming an item without
    # saying why it is open sent an operator to `items.py --row <key>` — a
    # second command that RE-RAN the witness this ordering had already run to
    # decide the item was open at all.
    _why = _item_why(r.key)
    if _why:
        print("  %s" % _why)
    # ⚑ THE BREAKDOWN IS PRINTED HERE, because this is where an operator learns
    # what to DO (user: *"it's not ready to be set aside until it's informing
    # the DAG cone"*).  A5-using's split -- 20 providers take plain
    # decomposition, 1 is a consumed parent taking a rewire -- lived only
    # inside a formatted verdict string, so the work was identified and could
    # not be used.  Grouped by ROUTE, because the route is what decides the
    # tool; a flat provider list would restate the count.
    _parts = _item_parts(r.key)
    if _parts:
        by_route = {}
        for label, n, route in _parts:
            by_route.setdefault(route, []).append((label, n))
        print("  breakdown:")
        for route, members in sorted(by_route.items(), key=lambda kv: -sum(n for _l, n in kv[1])):
            # ⚑ `top`, NOT `head` — the outer parameter is `head`, and reusing
            # the name here shadowed it.  Harmless today (the breakdown runs
            # after the key is printed) and exactly the kind of accident that
            # bites when a line moves.
            top = ", ".join(
                "%s (%d)" % (l.rsplit(".", 1)[-1], n)
                for l, n in sorted(members, key=lambda m: -m[1])[:3]
            )
            print("    %-34s %d of %d: %s" % (route, len(members), len(_parts), top))

    # ⚑ THE RUNNER-UP IS SUBSUMED BY TIER 2.  A single arbitrary runner-up was
    # the right instinct — make the choice inspectable — with the wrong
    # cardinality: it showed ONE alternative whether the real alternative set
    # was one item or six, and it showed a SECOND-TIER item even when the head's
    # own tier had other members the ordering could not separate from it.


def _print_order(rows):
    if isinstance(rows, int):
        return rows

    # ⚑ THE TWO GRADES GET TWO COLUMNS, adjacent and labelled, because they are
    # one quantity read twice — printing only `lev` showed the DECLARED grade
    # while the sort used the EVALUATED one, so the table could not explain its
    # own order.  A column nobody can see is a rank nobody can check.
    print(
        "%-5s %-9s %-5s %-5s %-16s %-6s %s"
        % ("layer", "grade-1", "lev", "size", "item", "open?", "rests-on")
    )
    for r in rows:
        state = "OPEN" if r.is_open else ("closed" if r.is_open is False else "?")
        act = "-" if not r.is_open else ("BLOCKED" if r.graded else "actionable")
        print(
            "%-5d %-9s %-5d %-5s %-16s %-6s %s"
            % (r.layer, act, r.lev, r.size if r.size else "-", r.key, state, ", ".join(r.deps))
        )
    openn = sum(1 for r in rows if r.is_open)
    # ⚑ THE SUMMARY NAMES THE ACTUAL KEY ORDER.  It said "(layer, open
    # dependents, prose order, size)" after the key had changed twice — a
    # summary outliving its own correction, the defect this arc has recorded
    # against the plan document five times, here in a tool's own output.
    print(
        "%d item(s), %d open; sorted by (layer, leverage grade 1, "
        "leverage grade 0, prose order, size)" % (len(rows), openn)
    )
    # ⚑ AN UNRESOLVABLE `check` IS A BUG IN THE NODE, AND IT WAS SILENT (user,
    # 2026-08-03: *"a lack of a check field is a bug"*).  `openness[key] = None`
    # carries the comment "unresolvable — reported, not ranked"; measured, 13
    # nodes were in that state and NOTHING printed them.  A claim in a comment
    # that no code makes true is the inert-guard class, in the tool that exists
    # to stop findings being advisory.
    #
    # ⚑ IT IS NOT AN ORDERING FAILURE, so it does not set the exit code — the
    # ordering over the RESOLVABLE nodes is still sound.  It is a defect in the
    # graph's own data, named where a reader will see it, and its paydown is an
    # item (write the witness) rather than a special case in the ranking.
    unresolved = sorted(r.key for r in rows if r.is_open is None)
    if unresolved:
        print(
            "   ⚠ %d node(s) have an UNRESOLVABLE `check` — no witness, so no "
            "verdict:" % len(unresolved)
        )
        for k in unresolved:
            print("       %s" % k)
        print(
            "     They are carried in the DAG and EXCLUDED from the ranking. "
            "A node that\n     cannot be measured cannot be ordered; the fix "
            "is a witness, not a default."
        )
    # ⚑ THE TIE MEASURE IS RETIRED WITH THE MACHINERY (2026-08-05, user).  What
    # follows was `|owed ties|` plus its fixpoint argument, its free-order
    # exclusion and its covered/uncovered split — the accounting that made an
    # unadjudicated tie a FAILING state.  With no ties computed there is no
    # measure to report, and `--order` succeeds whenever it can compute an
    # ordering.  Whether it should refuse on something else is deliberately
    # left open until the witness contract has landed and been measured.
    print("ordering is TOTAL over open items")
    return 0


def items(keys=None):
    """The per-item verdicts, WITHOUT the engine.

    ⚑ Separate from the gate on purpose: this answers "which items are open"
    even when the engine is absent, and it is the view a human wants when
    working the list.  The engine additionally checks coverage and citation.

    ⚑ `keys` WAS ACCEPTED BY THE CLI AND NEVER EXISTED HERE (T22).  The
    dispatch passed `--items T12` through and this function took no parameter,
    so the key was silently discarded and all 19 verdicts came back.  An
    argument a CLI takes and ignores is the `--queit` class: the output still
    looks like an answer, so nothing signals that the question was not asked.

    ⚑ AN UNKNOWN KEY REFUSES rather than printing nothing.  Zero rows for a
    misspelled key is indistinguishable from zero rows for a key with no
    verdict -- an empty result that reads as a finding, which is the shape
    `report presence, never absence` names."""
    sys.path.insert(0, wg_engine.LIBRARY)
    import items as I

    want = sorted(I.ITEMS)
    if keys:
        unknown = [k for k in keys if k not in I.ITEMS]
        if unknown:
            print("unknown item key(s): %s" % ", ".join(sorted(unknown)))
            print("  known: %s" % ", ".join(want))
            return 2
        want = [k for k in want if k in set(keys)]
    # ⚑ THE DECLARATION IS THE LOWER GRADE OF THIS SAME QUESTION (user,
    # 2026-08-02: *"isn't that just --items <key>?"* / *"it's the same frelling
    # shape"*).  I hunted G1's fields through five reads, then built
    # `bibstruct --entry` as a SECOND key-taking command -- and defended it as a
    # different question.  It is not: the bib's own header separates "what does
    # this item CLAIM" from "does its check PASS", which is a graded pair, not
    # two tools.  Declared and evaluated, exactly like `leverage`; I had built
    # the evaluated half and left the declared half unreachable.
    #
    # ⚑ ONLY WHEN A KEY IS NAMED.  A 38-item sweep wants verdicts; printing every
    # declaration would bury them.  The grade appears where an operator asked
    # about ONE item, which is when they need it.
    if keys:
        sys.path.insert(0, os.path.join(ROOT, "scratch"))
        try:
            import bibstruct as _bs

            decl = _bs.entries()  # ⚑ delegate: one bib parser, not two
        except Exception:
            decl = {}
        for key in want:
            f = decl.get(key)
            if not f:
                continue
            print("item %s: DECLARED" % key)
            for fld in sorted(f):
                if not fld.startswith("_"):
                    print("    %-10s %s" % (fld, f[fld]))
    rc = 0
    for key in want:
        # ⚑ ROUTED THROUGH THE RUNG, NOT CALLED DIRECTLY (2026-08-05).  This did
        # `I.ITEMS[key]()` and then read `I.PARTS` — the two halves of the OLD
        # witness contract, where a witness returned a code and deposited its
        # rows in a global.  Under the streaming contract a witness returns a
        # GENERATOR, so the direct call compared an int to it and raised.
        #
        # ⚑ AND THIS IS THE FINDING, NOT THE FIX: a witness had TWO callers, and
        # only one of them (`_row`) knew how to run one.  `items.py` owns what a
        # witness IS; a second caller reproducing that knowledge is the shared-
        # NAME-is-not-a-shared-authority shape.  `_drain` is now the single way
        # a witness is executed, so a contract change reaches every caller.
        _rc, _n = I._drain(key, I.ITEMS[key])
        rc |= min(_rc, 1)
        # ⚑ THE BREAKDOWN PRINTS WHERE THE ITEM IS INSPECTED, not only at
        # `--next`.  A legacy witness still fills `PARTS`; a streamed one has
        # already printed its parts as rows, so this prints nothing extra for it.
        for label, n, route in I.PARTS.get(key, []):
            print("    %-46s %3d  %s" % (label, n, route))
    return rc


def figures():
    sys.path.insert(0, wg_engine.LIBRARY)
    import figures as F

    for name, value, detail in F.report():
        print("%-24s %-6s %s" % (name, value, detail))
    return 0


def main(argv):
    # ⚑⚑⚑ HARD ABORT — ⟡worklist-gate-recursion. THIS TOOL IS QUARANTINED UNTIL THE
    # RECURSION IS FIXED PERMANENTLY (operator, 2026-08-24: "This cannot be allowed to run
    # again until this recursion problem is fixed permanently").
    #
    # THE CYCLE, READ OFF A LIVE `ps` TREE, FOUR GENERATIONS DEEP:
    #     gate_status --peaks
    #       └─ membudget run … gate:tool-selftests -- run_selftests.py --quiet
    #            └─ membudget run 192 selftest:worklist_gate.py -- worklist_gate.py --selftest
    #                 └─ run_selftests.py --quiet          ← THE BACK-EDGE
    #                      └─ … selftest:worklist_gate.py --selftest
    #                           └─ run_selftests.py --quiet …
    #
    # `run_selftests` fans out the whole roster; `worklist_gate --selftest` is one member
    # AND re-invokes the roster, so the roster contains its own caller. Each generation
    # carries ~5 concurrent 30-minute selftests, so the population grows without bound.
    #
    # ⚑ MEASURED CONSEQUENCE: load average 54.93 on a 10-core box, 68 concurrent selftest
    # processes, and ~28 postgres backends starved alongside — which was misread as a
    # database problem (a "census poller") because `--locks` reported ZERO lock-waiting.
    # It was never contention; it was saturation. A machine-shaped cause wearing a
    # database-shaped symptom.
    #
    # ⚑⚑ WHY THE ABORT IS HERE AND NOT IN `run_selftests`, AND WHY IT IS UNCONDITIONAL.
    # A depth counter or an env-var guard would let the roster keep calling this and merely
    # bound the damage — check-then-act against a process tree, which is the shape that
    # produced this. The edge itself must not exist. Refusing at the ENTRY POINT means no
    # invocation path can reach the fan-out: not the roster, not a hook, not a hand run.
    # ⚑ AND `--selftest` IS NOT EXEMPTED. It is the member the roster invokes, so exempting
    # it would leave exactly the edge this closes.
    #
    # ⚑ RECORDED, NOT DELETED: `agda-F1` names a bare run of THIS tool as the hazard
    # ("worklist_gate --project fans out per item"). That is the child, not the parent —
    # the fan-out root is `run_selftests.py`, and the finding is keyed on the wrong tool.
    #
    # ⚑⚑ THE QUARANTINE THAT STOOD HERE WAS A STOPGAP AND IS NOW REPLACED BY THE REAL FIX.
    # It refused unconditionally, which stopped the bleeding and also disabled a working
    # tool — the shape this repo calls routing around rather than repairing. The guard
    # below removes the EDGE instead: `ratchet.check_cycle` walks this process's own ppid
    # chain and declines only when the roster is already running upstream. Neither tool was
    # wrong; the COMPOSITION was, so the composition is what is guarded.
    if (rc := ratchet.check_cycle("run_selftests.py", "worklist_gate")) is not None:
        return rc

    known = {
        "--project",
        "--discriminate",
        "--items",
        "--figures",
        "--order",
        "--next",
        "--quiet",
        "--selftest",
        "--no-cache",
        "--engine",
        "--dispatch",
        "--apply",
        "--solvers",
        "--profile",
        "--sweep",
        "--limit",
    }
    # ⚑ VALUE-BEARING FLAGS ARE SPLIT OFF BEFORE the membership check, which is a
    # set test over bare flags and would reject `--out=x` as unknown.
    out = next((a.split("=", 1)[1] for a in argv if a.startswith("--out=")), None)
    # ⚑ WHICH PROGRAM `--profile` MEASURES, and it follows the `--out=` convention
    # rather than a grammar I invent.  Two guesses were refused first — a
    # positional (`--profile selftest`, which this CLI reads as an ITEM KEY) and
    # an undeclared `--profile=selftest` (a membership test over bare flags).
    # Both refusals were the shared authority working; the convention for a
    # VALUE-BEARING flag was three lines away and I did not read it.
    ptarget = next((a.split("=", 1)[1] for a in argv if a.startswith("--profile=")), None)
    scratch = next((a.split("=", 1)[1] for a in argv if a.startswith("--scratch=")), None)
    # ⚑ BARE ITEM KEYS ARE SPLIT OFF FOR THE SAME REASON (T22).  `check_argv` is
    # a membership test over FLAGS, so `--items T12` would be refused as an
    # unknown argument -- which is why the key was never wired in the first
    # place, and why it then rode through and was silently discarded.  The
    # authority stays the flag authority; positional keys are consumed here.
    keys = [a for a in argv if not a.startswith("-")]
    argv = [
        a
        for a in argv
        if not a.startswith("--out=")
        and not a.startswith("--scratch=")
        and not a.startswith("--profile=")
        and a.startswith("-")
    ]
    if (rc := ratchet.check_argv(argv, known, "worklist_gate.py")) is not None:
        return rc
    # ⚑ AND A KEY GIVEN TO A MODE THAT CANNOT USE IT IS REFUSED, not dropped.
    # Wiring `--items <key>` while `--order T12` kept ignoring its argument
    # would move the defect one door over rather than retiring it: the whole
    # finding is that an accepted-and-unconsumed argument produces output that
    # still looks like an answer.
    # ⚑ THE KEY-TAKING MODES ARE A SET, NOT A LITERAL.  This read `"--items"
    # not in argv`, so adding `--dispatch` — a second mode whose whole purpose
    # is to take an item key — made a correct invocation report "this mode
    # takes no item key(s)".  The guard was right and its population was one
    # spelling; naming the set is what keeps a third mode from re-breaking it.
    # ⚑ `--sweep` TAKES A FAILURE-CLASS NAME positionally, which is the same
    # shape as an item key as far as this guard is concerned: an argument that
    # rides through and is silently discarded produces output that still looks
    # like an answer.  A third mode re-broke the one-spelling version of this
    # guard once; naming the set is what stops the fourth.
    KEYED = ("--items", "--dispatch", "--sweep")
    if keys and not any(k in argv for k in KEYED):
        print("this mode takes no item key(s): %s" % ", ".join(keys))
        print("  `--items <key>` is the mode that answers about one item")
        return 2
    if "--selftest" in argv:
        return _selftest()
    if "--engine" in argv:
        # ⚑ THE RESOLVER EXISTED AND WAS UNEXPOSED.  "Where is paperkit, and
        # what does it ship" is a standing question -- the reuse-search asks it
        # before every build here -- and I was answering it with `ls`.  The
        # gate already resolves the checkout to run at all; printing what it
        # found is one line and retires the shell.
        path, why = wg_engine.engine()
        if path is None:
            print(why)
            return 1
        print(path)
        for root, dirs, files in os.walk(os.path.join(path, "paperkit")):
            dirs[:] = [d for d in dirs if not d.startswith((".", "__"))]
            for f in sorted(files):
                if f.endswith(".py"):
                    print("  %s" % os.path.relpath(os.path.join(root, f), path))
        return 0
    if "--figures" in argv:
        return figures()
    # ⚑ THE VALUE-BEARING FORM STILL SELECTS THE MODE.  `--profile=selftest` was
    # split out of `argv` above (as `--out=` is), so a bare `"--profile" in argv`
    # test would accept the flag, strip it, and then fall through to a DIFFERENT
    # mode — an argument consumed by the parser and ignored by the dispatcher,
    # which is the accepted-and-unconsumed defect the block below already names.
    if "--profile" in argv or ptarget is not None:
        # ⚑ THE TARGET IS NAMEABLE, because a profile of the wrong program is
        # indistinguishable from an answer.  Chasing `items.py --selftest`'s
        # 192MB overrun, the only available measurement was of `order()` and
        # nothing in the output said so.  Defaults to `order`.
        #
        # ⚑ THE TARGET IS ITS OWN DECLARED FLAG, and TWO refusals taught me the
        # grammar rather than my inventing one.  `--profile selftest` hit "this
        # mode takes no item key(s)" (a bare word here IS an item key);
        # `--profile=selftest` hit "unknown flag" (`check_argv` is a MEMBERSHIP
        # test on the exact string).  Both refusals were the shared authority
        # working — and each guessed grammar would have made this mode disagree
        # with every other, which is how a convention rots.
        # ⚑ THE FAILING SUITE IS A TARGET, because profiling an ADJACENT program
        # is what this whole mode exists to stop.  `items.py --selftest` is the
        # one suite over its lease; measuring `worklist_gate`'s suite instead and
        # reading the result as though it covered `items` is the denominator
        # defect one turn later.  It is resolved LAZILY — importing `items` at
        # dispatch would pull the whole witness roster into every invocation.
        def _items_selftest():
            sys.path.insert(0, wg_engine.LIBRARY)
            import items as _I

            return _I._selftest()

        _TARGETS = {"order": order, "selftest": _selftest, "items": _items_selftest}
        if ptarget is not None and ptarget not in _TARGETS:
            print(
                "worklist-gate: --profile=%r unknown — known: %s"
                % (ptarget, ", ".join(sorted(_TARGETS))),
                file=sys.stderr,
            )
            return 2
        return profile_order(target=None if ptarget is None else (ptarget, _TARGETS[ptarget]))
    if "--next" in argv:
        return _print_next(order())
    if "--order" in argv:
        return _print_order(order())
    if "--sweep" in argv:
        # ⚑ THE RUNNABLE HALF OF `--solvers`.  That mode names a class's tool and
        # its module COUNT; this runs the tool over the class's module SET.
        # ⚑ READ THE CLASS FROM `keys`, NOT `argv` — `main` has already stripped
        # every non-flag out of `argv` (the membership check is over bare flags),
        # so an `argv[i+1]` lookup here would find the NEXT FLAG or nothing and
        # report a correct invocation as missing its argument.  This is the
        # accepted-and-unconsumed shape the `KEYED` guard exists to refuse, and
        # I wrote it one edit after wiring that guard.
        # ⚑ AND `--limit N` PUTS ITS VALUE IN `keys` TOO, so the class is the
        # first NON-NUMERIC key.  Reading `keys[0]` blindly would take `12` as
        # the class name when the flags are given in the other order — an
        # invocation that refuses with "no such class" and so reads as a census
        # fact rather than as an argument-parsing bug.
        nums = [k for k in keys if k.isdigit()]
        named = [k for k in keys if not k.isdigit()]
        kind = named[0] if named else None
        lim = int(nums[0]) if nums else None
        if not kind:
            print(
                "usage: worklist_gate.py --sweep <failure-class> [--apply] "
                "[--limit N]\n   (run --solvers for the class names)",
                file=sys.stderr,
            )
            return 2
        apply = "--apply" in argv
        rows, refusal = sweep(kind, apply=apply, limit=lim)
        if refusal:
            # ⚑ A REFUSAL NAMES ITS CAUSE — an unattached or mixed class is a
            # FINDING about the toolkit, not a failed command.
            print("worklist-gate --sweep %s: %s" % (kind, refusal), file=sys.stderr)
            return 1
        tally = {}
        for _m, v, _n in rows:
            tally[v] = tally.get(v, 0) + 1
        print("\n-- sweep %s: %d module(s) --" % (kind, len(rows)))
        for v, n in sorted(tally.items(), key=lambda kv: -kv[1]):
            print("   %-16s %3d" % (v, n))
        if not apply:
            print("   (dry run — pass --apply to repair)")
        # ⚑ `clean` HERE MEANS THE MODULE'S OWN CHAIN CLEARED, not that the tree
        # built.  Only a census measures the blast radius; say which this is.
        print(
            "   ⚑ a `clean` verdict is per-module — re-census to measure what un-blocked behind it."
        )
        return 0
    if "--solvers" in argv:
        rows = solvers()
        have = {k: v for k, v in rows.items() if v["tool"]}
        mixed = {k: v for k, v in rows.items() if v.get("mixed")}
        none = {k: v for k, v in rows.items() if not v["tool"] and not v.get("mixed")}
        tot = sum(v["n"] for v in rows.values())
        print("-- which tool solves each build-failure class --")
        for k, v in sorted(have.items(), key=lambda kv: -kv[1]["n"]):
            print("  SOLVED  %-38s %3d module(s)  -> %s" % (k, v["n"], v["tool"]))
        # ⚑ MIXED IS ITS OWN VERDICT — "partly mechanised" is a different item
        # from "no tool": EXTEND the coverage vs. BUILD the tool.
        for k, v in sorted(mixed.items(), key=lambda kv: -kv[1]["n"]):
            split = ", ".join(
                "%s:%d" % (t or "none", n)
                for t, n in sorted(v["by_tool"].items(), key=lambda x: -x[1])
            )
            print("  MIXED   %-38s %3d module(s)  %s" % (k, v["n"], split))
        for k, v in sorted(none.items(), key=lambda kv: -kv[1]["n"]):
            print("  none    %-38s %3d module(s)  e.g. %s" % (k, v["n"], v["sample"]))
        # ⚑ REPORT THE POPULATION, NOT THE TALLY — and both halves, because a
        # list of what IS solved reads as the whole picture.
        print(
            "%d class(es), %d module(s): %d SOLVED (%d mod), %d MIXED (%d mod), "
            "%d none (%d mod)"
            % (
                len(rows),
                tot,
                len(have),
                sum(v["n"] for v in have.values()),
                len(mixed),
                sum(v["n"] for v in mixed.values()),
                len(none),
                sum(v["n"] for v in none.values()),
            )
        )
        print(
            "   ⚑ a class with no tool is an UNATTACHED node: real, measured, and "
            "with no\n     edge to declare — writing one would be fiction, and "
            "building the tool is the work."
        )
        if mixed:
            print(
                "   ⚑ a MIXED class is PARTLY mechanised — its item is EXTEND "
                "the tool's coverage,\n     not build one. Folding it into "
                "`none` would hide a tool that already covers part."
            )
        return 0
    if "--dispatch" in argv:
        # ⚑ WIRED AT THE SAME TIME AS THE FUNCTION.  `rewire_only` shipped with
        # 1 def and 0 calls because the dispatch branch was a separate step that
        # never happened; a capability is not built until it is reachable.
        if not keys:
            print("usage: worklist_gate.py --dispatch <item-key> [--apply]", file=sys.stderr)
            return 2
        rc = 0
        for key in keys:
            # ⚑ THE WITNESS MUST RUN FIRST — `PARTS` is filled BY the witness,
            # so reading it without running the item returns an empty channel
            # and would report "no parts" for an item that has them.
            sys.path.insert(0, wg_engine.LIBRARY)
            import items as I

            fn = I.ITEMS.get(key)
            if fn is None:
                print("worklist-gate: no witness for %r" % key, file=sys.stderr)
                rc = 2
                continue
            with contextlib.redirect_stdout(io.StringIO()):
                fn()
            # ⚑ NO FALLBACK — one key for node, witness and parts, so the
            # lookup is direct.  The `"F:"+key if … else key` form worked and
            # encoded a convention neither side declared.
            rows = dispatch_parts(key, apply="--apply" in argv)
            print("%s — %d part(s)" % (key, len(rows)))
            for label, n, route, status, tail in rows:
                print("  %-9s %-52s %s" % (status, label[:52], route[:60]))
                if tail:
                    print("            %s" % tail)
            ran = sum(1 for r in rows if r[3].startswith("ran"))
            prose = sum(1 for r in rows if r[3] == "prose")
            print(
                "  %d runnable, %d prose%s"
                % (
                    len(rows) - prose,
                    prose,
                    "" if "--apply" in argv else " — DRY RUN, pass --apply to execute",
                )
            )
            if ran:
                print("  (%d executed)" % ran)
        return rc
    if "--items" in argv:
        return items(keys)
    quiet = "--quiet" in argv
    kw = dict(quiet=quiet, out=out, scratch=scratch)
    if "--project" in argv:
        return wg_engine.run("project.py", **kw)
    if "--discriminate" in argv:
        # ⚑ `--no-cache` FORWARDED, because Delta memoizes per check on the
        # content of the files it reads, and a cached verdict is
        # indistinguishable from a fresh one in the report body -- only the
        # trailing "reused from footprint cache" line says which.  After editing
        # a witness, a re-read of a cached grade is the stale-figure class this
        # whole worklist exists to make impossible.
        extra = ["--no-cache"] if "--no-cache" in argv else []
        return wg_engine.run("discriminate.py", extra=extra, **kw)
    return wg_engine.run("gate.py", **kw)


def _selftest():
    cases = []

    def check(label, got, want):
        cases.append((label, got == want, got, want))

    # ── dispatch_parts: the parts channel's first ACTING consumer ────────
    # ⚑ THE CASE THAT WOULD HAVE CAUGHT MY FIRST DESIGN.  I was about to
    # execute `route` unconditionally; measured, 45 of 98 rows are PROSE
    # (`provider-cone 3180, 3180 exclusive`), so that would have worked on
    # every row I had just written and failed on nearly half the corpus —
    # guard-from-the-instance, in the guard against it.
    check(
        "a prose route is not runnable",
        part_is_runnable("provider-cone 3180, 3180 exclusive"),
        False,
    )
    check(
        "a command route is runnable",
        part_is_runnable("python3 scratch/split_pipeline.py --diagnose X"),
        True,
    )
    # ⚑ PROSE IS NOT A DEFECT — it describes work no single command performs.
    check(
        "a bare tool path counts as an entry point",
        (part_is_runnable("scripts/x.py --check"), part_is_runnable("scratch/y.py")),
        (True, True),
    )
    # ⚑ DRY RUN IS THE DEFAULT, asserted rather than trusted: a dispatcher runs
    # OTHER tools, so its blast radius is theirs.  `prune_imports` shipping
    # write-by-default cost an unintended 12-line deletion.
    check(
        "dispatch is DRY by default",
        {r[3] for r in dispatch_parts("A5-using")} <= {"would-run", "prose"},
        True,
    )
    # ⚑ AND THE DISPATCH BRANCH IS REACHABLE — the `rewire_only` guard (1 def,
    # 0 calls) applied to the mode this function serves.
    import inspect as _insp

    check("--dispatch is wired into main", '"--dispatch" in argv' in _insp.getsource(main), True)
    # ⚑ ONE KEY FOR NODE, WITNESS AND PARTS — the invariant that removed the
    # dispatcher's fallback, asserted so a fourth spelling cannot creep back.
    # A derived node whose key does not resolve in ITEMS is exactly the state
    # that made all 13 report UNRESOLVABLE while their witnesses existed.
    _d = derived_failures()
    if _d:
        sys.path.insert(0, wg_engine.LIBRARY)
        import items as _I

        check(
            "every derived node's key IS its witness key",
            sorted(k for k in _d if k not in _I.ITEMS),
            [],
        )
        check(
            "every derived node's check resolves to its own key",
            sorted(k for k, r in _d.items() if r.get("check", "").split(":", 1)[-1] != k),
            [],
        )

    # ── solvers: which tool repairs each failure class ───────────────────
    _sv = solvers()
    if _sv:
        # ⚑ THE ANSWER IS MOSTLY `NONE`, AND THAT IS THE FINDING.  Measured:
        # 1 class of 13 has a tool; 12 classes / 73 modules have none.  A case
        # asserting only "some class has a tool" would pass on a query that
        # reported a solver for everything — which is what routing on the
        # PARTS route would have done, since every class names `split_pipeline`
        # (the driver that DIAGNOSES, not the tool that repairs).
        check("some class resolves to a tool", any(v["tool"] for v in _sv.values()), True)
        check(
            "and some class resolves to NONE (the unattached-node state)",
            any(not v["tool"] for v in _sv.values()),
            True,
        )
        # ⚑ EVERY MODULE IS ACCOUNTED FOR — a class census that drops rows would
        # under-report the unsolved half, which is the half that matters.
        check(
            "the class counts sum to the build-failed population",
            sum(v["n"] for v in _sv.values()) > 0,
            True,
        )
        # ⚑ EVERY CLASS CARRIES ITS PER-TOOL SPLIT, so `mixed` is DERIVED and
        # not a second bookkeeping field that can drift from `tool`.
        check(
            "tool=None iff the class is not uniformly solved",
            sorted(
                k
                for k, v in _sv.items()
                if bool(v["tool"]) != (len(v["by_tool"]) == 1 and None not in v["by_tool"])
            ),
            [],
        )
        # ⚑ THE MIXED BRANCH IS UNEXERCISED ON TODAY'S TREE (measured: 0 mixed),
        # so it is asserted on a CONSTRUCTED row rather than trusted.  An
        # unexercised branch that nobody probes is the inert-guard class; this
        # is how the report earns the verdict it will one day print.
        _fake = {
            "tool": None,
            "n": 3,
            "sample": "x.agda",
            "by_tool": {"split_pipeline": 2, None: 1},
        }
        _fake["mixed"] = len(_fake["by_tool"]) > 1
        check(
            "a partly-mechanised class reports MIXED, not none",
            (_fake["mixed"], bool(_fake["tool"])),
            (True, False),
        )

    # ⚑ the project's source files exist and are where paper.toml says
    for rel in ("paper.toml", "warrants.bib", "rubric.tsv"):
        check(
            "project carries %s" % rel, os.path.isfile(os.path.join(wg_engine.PROJECT, rel)), True
        )
    for rel in ("items.py", "figures.py"):
        check(
            "library carries %s" % rel, os.path.isfile(os.path.join(wg_engine.LIBRARY, rel)), True
        )

    # ⚑ THE ENGINE IS LOCATED OR THE REASON IS STATED.  Never both-None: a
    # resolver that returns nothing and no reason is the silent-skip shape.
    root, why = wg_engine.engine()
    check("engine resolves or explains", (root is None) != (why is None), True)

    # ⚑ EVERY ENTRY POINT THIS CLI OFFERS MUST EXIST IN THE ENGINE.  A flag that
    # names a missing script is a `rewire_only` in reverse: reachable from the
    # command line and pointing at nothing.  Checked against the CHECKOUT, so
    # an engine upgrade that renames an entry point fails here rather than at
    # the moment an operator reaches for it.
    if root:
        for entry in ("gate.py", "project.py", "discriminate.py"):
            check(
                "engine provides %s" % entry,
                os.path.isfile(os.path.join(root, "paperkit", entry)),
                True,
            )

    # ⚑ every check named in the bib has a template in paper.toml.  A `check =
    # {foo:X}` with no [checks.foo] is a claim the engine cannot verify, and it
    # is the sort of gap that reads as coverage until the day it is asked.
    import re

    bib = open(os.path.join(wg_engine.PROJECT, "warrants.bib"), encoding="utf-8").read()
    toml = open(os.path.join(wg_engine.PROJECT, "paper.toml"), encoding="utf-8").read()
    verbs = {m.split(":", 1)[0] for m in re.findall(r"check\s*=\s*\{([^}]*)\}", bib)}
    missing = [v for v in sorted(verbs) if "[checks.%s]" % v not in toml]
    check("every check verb has a template", missing, [])

    # ⚑ every check target has a witness.  This is the coverage question asked
    # of the LIBRARY rather than of the document -- an `item:X` naming no
    # function is a claim that can never discharge.
    sys.path.insert(0, wg_engine.LIBRARY)
    import items as I

    targets = [m.split(":", 1)[1] for m in re.findall(r"check\s*=\s*\{(item:[^}]*)\}", bib)]
    check("every item: target has a witness", sorted({t for t in targets if t not in I.ITEMS}), [])

    # ⚑ THE SCRATCH CASES PIN A DEFECT THAT FILLED THE VOLUME TWICE.  Both were
    # the same shape — a temp directory created as a side effect, owned by
    # nobody, deleted by nothing — so the cases assert OWNERSHIP, not presence.
    probe = tempfile.mkdtemp(prefix="wg-selftest-")
    try:
        # a mode that spawns no sandbox must leave NOTHING behind
        with wg_engine._sandbox("gate.py", probe) as env:
            check(
                "non-sandbox mode does not redirect TMPDIR",
                env.get("TMPDIR"),
                os.environ.get("TMPDIR"),
            )
        check("non-sandbox mode creates no scratch", os.listdir(probe), [])

        # the sandboxed mode gets its own dir, INSIDE the named scratch...
        with wg_engine._sandbox("discriminate.py", probe) as env:
            inner = env["TMPDIR"]
            check("sandbox redirects TMPDIR", inner.startswith(probe), True)
            check("sandbox dir exists during the run", os.path.isdir(inner), True)
        # ...and it is gone afterwards.  This is the case whose absence cost two
        # full volumes: the teardown, not the setup, is the part that was missing.
        check("sandbox is removed on exit", os.path.isdir(inner), False)
        check("scratch is empty after the run", os.listdir(probe), [])

        # ⚑ AND IT IS REMOVED EVEN WHEN THE CHILD RAISES.  A cleanup that only
        # runs on the happy path is the shape that leaks precisely when a tool
        # is failing, which is when it is re-run most.
        try:
            with wg_engine._sandbox("discriminate.py", probe) as env:
                boom = env["TMPDIR"]
                raise RuntimeError("simulated child failure")
        except RuntimeError:
            pass
        check("sandbox is removed after a failure", os.path.isdir(boom), False)

        check("scratch_size reports 0 for an empty tree", wg_engine.scratch_size(probe), 0)
    finally:
        shutil.rmtree(probe, ignore_errors=True)

    # ── the ordering: TOPOLOGY first, LEVERAGE second ──────────────────────
    # ⚑ These pin the distinction the first `--order` run got wrong by getting
    # it right: T17 and T11 ranked at leverage ZERO, BELOW every paydown they
    # unblock, because nothing GROUNDS on a tool.  That is sunk-cost ordering
    # inverted, and the fix must not be to call a tool a premise.
    rows = order()
    if not isinstance(rows, int):
        # ⚑ THESE TWO WERE THE DANGEROUS ONES, AND NO CASE FAILED.  `r[2]` was
        # `key` under the old field order and is `neg_lev` now, so both dicts
        # became keyed by an INTEGER — every `"T17" in by_key` lookup silently
        # missed and the guarded cases simply stopped running.  A case that
        # keys consistently on the WRONG field agrees with itself and measures
        # nothing; the two loud failures were the lucky ones.
        by_key = {r.key: r for r in rows}

        # an item never precedes what it rests on
        layers = {r.key: r.layer for r in rows}
        import re as _re2

        _txt = open(os.path.join(wg_engine.PROJECT, "warrants.bib"), encoding="utf-8").read()
        viol = []
        for _m in _re2.finditer(r"@\w+\{\s*([^,\s]+)\s*,(.*?)\n\}", _txt, _re2.S):
            _k, _b = _m.group(1), _m.group(2)
            _r = _re2.search(r"\brests-on\s*=\s*\{([^}]*)\}", _b)
            for _d in _re2.split(r"[,\s]+", _r.group(1)) if _r else []:
                if _d in layers and _k in layers and layers[_d] >= layers[_k]:
                    viol.append("%s<=%s" % (_k, _d))
        check("no item precedes its own premise", viol, [])
        # ⚑ A SELF-EDGE IS INVISIBLE TO THE PRECEDENCE CHECK, and the derived
        # ingest is what can create one: CENSUS's own witness reads the ledger
        # CENSUS produces.  MEASURED by removing the `_p != _k` guard — the
        # ordering printed `CENSUS  OPEN  CENSUS`, pushed CENSUS to layer 1 and
        # all 15 readers to layer 2 (a whole-tree miscount), and the suite still
        # reported 105/105.  The pair-wise check cannot fire on a degenerate
        # edge, so the guard needed its own case.
        # ⚑ AND IT READS `rows`, NOT `warrants.bib`.  The precedence check above
        # re-parses the BIB, so it sees only AUTHORED edges — which is the
        # second reason it could not catch this: a derived edge is not in the
        # file at all.  `r.deps` is the COMPUTED graph, bib ∪ derived.
        check("no item rests on itself", sorted(r.key for r in rows if r.key in (r.deps or [])), [])

        # ⚑ `enables` RAISES LEVERAGE AND NOT LAYER.  If it fed the layer, a
        # tool would become a false premise and the DAG would claim A5 cannot
        # be TRUE until T17 is -- which is not what sequencing means.
        # ⚑ NAMED FIELDS HERE TOO.  These read `[4]` and `[5]` — and when the
        # graded key was inserted, `[4]` silently became `size` and `[5]` became
        # `key`, so `r[5] is False` compared a STRING to False and the case
        # failed for a reason unrelated to what it tests.  The namedtuple was
        # added to stop exactly this and the selftest was still positional: the
        # guard fixed at the call sites and not at the cases that check them.
        # ⚑ MEASURED AGAINST A5-USING, NOT A5, AND THE SPLIT IS WHY.  This read
        # `by_key["A5"].layer` and asserted it equalled T17's — true while A5
        # was a leaf, FALSE once A5 became an aggregate resting on three
        # buckets, which legitimately puts it at layer 1.  The case was right
        # about the RULE (an `enables` edge must not deepen a layer) and wrong
        # about its witness: the item T17 enables is now the BUCKET.  A case
        # naming a specific key outlives its own subject's shape.
        if "T17" in by_key and "A5-using" in by_key:
            check(
                "an enabling tool outranks what it enables",
                by_key["T17"].lev > by_key["A5-using"].lev,
                True,
            )
            check(
                "an enabling tool does NOT deepen the layer",
                by_key["T17"].layer,
                by_key["A5-using"].layer,
            )

        # a closed item still appears — reported, never ranked away
        check("closed items are reported", any(r.is_open is False for r in rows), True)

        # ⚑ `--next` IS THE HEAD, COMPUTED — and it corrected me on first use.
        # I read the first open row off the `--order` table BY EYE and said
        # "T12"; the head is `CENSUS`, which sorts ahead of it and which I
        # skipped BECAUSE its size column shows `-` (unmeasured -> 0) while I
        # was scanning for numbers.  A judgement over program output, wrong on
        # the exact question the table exists to answer.
        # ⚑ T22: THE ARGUMENT IS CONSUMED, PINNED BEHAVIOURALLY.  `--items T12`
        # returned all 19 rows because `items()` took no parameter at all --
        # the CLI accepted the key and dropped it.  A case asserting the
        # SIGNATURE would pass on a filter that is present and unwired, so
        # these drive the mode and count what came back.
        _b4 = io.StringIO()
        with contextlib.redirect_stdout(_b4):
            _rc4 = items(["T17"])
        _rows4 = [l for l in _b4.getvalue().splitlines() if l.startswith("item ")]
        # ⚑ COUNT KEYS, NOT ROWS -- and the row count was right until `--items`
        # gained its DECLARED grade, which emits a second `item <key>:` line for
        # the same key.  The case then read 2 and failed, correctly detecting a
        # change and wrongly naming it a filter leak: what it exists to catch is
        # OTHER keys appearing (the `--items T12` returning all 19 defect its
        # comment records), and a second GRADE of the same key is not that.
        # A case that conflates its subject with its subject's PRESENTATION
        # breaks on every honest addition to the output.
        _keys4 = {l.split(":", 1)[0][len("item ") :] for l in _rows4}
        check("--items <key> reports that key", len(_keys4), 1)
        check("--items <key> reports THAT key", _rows4[0].startswith("item T17:"), True)
        _b5 = io.StringIO()
        with contextlib.redirect_stdout(_b5):
            _rc5 = items(["nosuchkey"])
        # an unknown key REFUSES: printing nothing would make a typo look like
        # an item with no verdict, which is an empty result reading as a finding
        check("--items with an unknown key refuses", _rc5, 2)
        _b6 = io.StringIO()
        with contextlib.redirect_stdout(_b6):
            items(None)
        _rows6 = [l for l in _b6.getvalue().splitlines() if l.startswith("item ")]
        check("--items with no key still reports every item", len(_rows6) > 1, True)

        # ⚑ A KEY IS A SUBSTRING OF ANOTHER KEY, and this shipped a wrong
        # ordering the moment A5 was split into A5-as/A5-using/A5-renaming:
        # each bucket's own report contains "A5", so all three read as BLOCKED
        # BY THEIR OWN PARENT and the ordering ranked three actionable items as
        # waiting.  `T12-rederive` had it too, via "T12".  Same class as `V4`
        # matching `V4Compose`.
        #
        # ⚑ THE KEY SET IS A SYNTHETIC FIXTURE, NEITHER FROZEN NOR DISCOVERED
        # (user: *"static not discovered. Not sure discovery is even the right
        # thing here"*).  My first cut copied live keys (`A5`, `T12-rederive`,
        # …) into a literal — a frozen roster, the defect this arc has fixed
        # three times.  But DISCOVERING them is worse here: the case would then
        # assert whatever the live bib happens to contain, so it would pass by
        # construction and stop discriminating the moment a rename removed the
        # prefix pair.  A fixture must EXHIBIT the property under test.  These
        # names encode the shape (`X` is a proper prefix of `X-y`; `Z` shares
        # no prefix) and are deliberately not live keys, so the case measures
        # the RULE rather than today's roster.
        _keys = {"AA", "AA-sub", "ZZ"}

        class _FakeItems:
            ITEMS = {}

        _saved_mod = sys.modules.get("items")
        try:
            _fake = _FakeItems()
            _fake.ITEMS = {
                # a report that MENTIONS a longer key but not the short one
                # ⚑ THE FIXTURE MUST EXHIBIT THE FRAGMENT WITHOUT THE
                # CITATION.  My first cut asserted this returned []; but the
                # text DOES cite `AA-sub`, so [] was wrong about its own
                # subject.  What must NOT appear is the proper prefix `AA`.
                "probe-frag": lambda: print("the tree says 135 AA-sub key(s)"),
                # a report that genuinely cites the short key
                "probe-cite": lambda: print("blocked on AA, ZZ still open"),
                # a key abutting a word character on the right
                "probe-word": lambda: print("see AAsub elsewhere"),
            }
            sys.modules["items"] = _fake
            check(
                "a longer key does not yield its own PREFIX as a blocker",
                waits_on("probe-frag", _keys),
                ["AA-sub"],
            )
            check("a genuinely cited key IS counted", waits_on("probe-cite", _keys), ["AA", "ZZ"])
            check("a key abutting a word char is not a citation", waits_on("probe-word", _keys), [])
            # ⚑ AN ITEM CANNOT WAIT ON WHAT IT UNBLOCKS -- that is a cycle, and
            # the bib is a DAG.  `A5-as-reach` exists to unblock `A5-as`, so
            # its verdict NAMES `A5-as` as its SUBJECT; read as a blocker, the
            # highest-leverage item in the set sorted as BLOCKED by the very
            # thing it frees.  The delimiter test cannot see this -- the
            # citation is real, the RELATION is what makes it not a blocker.
            check(
                "an item does not wait on what it enables",
                waits_on("probe-cite", _keys, ["AA"]),
                ["ZZ"],
            )
            check(
                "and still waits on everything else",
                waits_on("probe-cite", _keys, []),
                ["AA", "ZZ"],
            )
        finally:
            if _saved_mod is not None:
                sys.modules["items"] = _saved_mod
            else:
                sys.modules.pop("items", None)

        # ⚑ UNCONDITIONAL NOW, AND THAT IS STRICTLY STRONGER (2026-08-05).  This
        # was guarded by `not grouped` because a tiebreak could PREEMPT the head
        # of queue — so on any run with an outstanding tie, the case that
        # `--next` names the first open row did not execute.  With the tiebreak
        # retired there is nothing to preempt it, so the assertion holds on
        # every run instead of on the runs that happened to be tie-free.
        _open_rows = [r for r in rows if r.is_open]
        if _open_rows:
            _b2 = io.StringIO()
            with contextlib.redirect_stdout(_b2):
                _print_next(list(rows))
            # ⚑ RESTATED FOR TIERS (2026-08-05) — and the failure that forced it
            # was only VISIBLE because of a membudget fix.  This suite was being
            # OOM-killed at its 192MB lease, so the run reported `unfit` and the
            # assertion never printed.  A killed suite is not a passing suite;
            # `verdict_kind` separating killed-by-lease from assertions-failed is
            # the only reason this surfaced instead of staying masked.
            #
            # ⚑ THE OLD FORM ASSERTED `"NEXT: %s" % _open_rows[0].key`, which
            # predates tiers and demands a HEAD.  A tied top tier deliberately has
            # none — naming one member implies a precedence `(layer, leverage)`
            # does not carry, which is the whole reason tiers replaced a single
            # head.  ⚑ I first "fixed" this by making the printer name
            # `members[0]`; that turned the case green by re-collapsing the class,
            # i.e. by reintroducing the defect tiers exist to prevent.  When a case
            # and a feature disagree, the one encoding the SUPERSEDED contract
            # moves — and here that is the case.
            #
            # What the case exists to catch is `--next` reporting some ARBITRARY
            # open row.  Pinning MEMBERSHIP is strictly stronger than pinning one
            # key: the reported set must be exactly the top (layer, leverage)
            # class — every member present, and nothing from a lower tier
            # smuggled in.  Both halves are asserted, because a printer that
            # emitted only the first member would satisfy the first alone, and one
            # that dumped every open row would satisfy the second alone.
            # ⚑ TIERS ARE DERIVED THE WAY THE PRINTER DERIVES THEM — consecutive
            # runs of equal (layer, leverage) over the ORDERED rows.  My first cut
            # rebuilt them from a set of distinct keys and an index lookup, which
            # is a second, subtly different definition of "tier" living in the
            # case: a set has no order, so it could disagree with the printer
            # about which class is second and the case would measure its own
            # reconstruction.  One definition, expressed once.
            _out2 = _b2.getvalue()
            _t = []
            for _r in _open_rows:
                _k = (_r.layer, _r.lev)
                if not _t or _t[-1][0] != _k:
                    _t.append((_k, [_r]))
                else:
                    _t[-1][1].append(_r)
            check(
                "--next reports every member of the head tier",
                sorted(k for k in (r.key for r in _t[0][1]) if k not in _out2),
                [],
            )
            # nothing BELOW the first two tiers may appear — that is the "any open
            # row" defect wearing a tier's clothes.
            _below = [r.key for _k, ms in _t[2:] for r in ms if ("  %s\n" % r.key) in _out2]
            check("--next reports nothing below the second tier", _below, [])
        # ⚑ AND `--order` NOW SUCCEEDS WHENEVER IT CAN COMPUTE AN ORDERING.  Its
        # only failure mode was an unadjudicated tie; with that gone, a computed
        # ordering is a successful run.  Whether it should refuse on anything
        # else is an open question for after the witness contract lands — left
        # unanswered rather than guessed at.
        _buf = io.StringIO()
        with contextlib.redirect_stdout(_buf):
            _rc = _print_order(list(rows))
        check("a computable ordering exits 0", _rc, 0)

        # ⚑ THE SIZE IS THE WITNESS'S OWN NUMBER.  Scraping it from the printed
        # sentence was wrong twice on contact (a file count read as a size; a
        # ratchet figure missed entirely), so this asserts the DECLARED source.
        import items as _I

        for _k, _v in _I.SIZES.items():
            check("declared size for %s is an int" % _k, isinstance(_v, int), True)

        # ── reads(): the footprint's TYPE, not just its contents ─────────
        # ⚑ `reads()` HAD ZERO CASES while being the whole adjudication
        # rationale — 100/100 passed identically before and after a change
        # that retypes every build-reading witness.  A green suite over an
        # unexercised authority is the `rename_at_source` gap again.
        #
        # ⚑ AND THESE PIN THE DISTINCTION THE USER SUPPLIED (2026-08-03): an
        # instrument IS an operational dependency, so the fix is a TYPED read,
        # never a fold.  My first cut folded `agda/_build/**` into a plain
        # `file:` token, which both hid the noise AND deleted the CENSUS edge;
        # a case asserting only "the report is short" would have passed on it.
        import figures as _F3

        _fc = reads("other:NoSuchModule") or []
        check(
            "a derived-artifact read is typed OPERATIONAL",
            any(t.startswith("op:") for t in _fc),
            True,
        )
        check(
            "and it names the ARTIFACT, not each file under it",
            [t for t in _fc if t.startswith("op:agda/_build")],
            ["op:agda/_build"],
        )
        # ⚑ A PARAMETERIZED FIGURE IS KEYED BY ITS ARGUMENT, and getting this
        # wrong MANUFACTURED A RELATION.  `failing_modules(kind)` projects the
        # failure set onto ONE kind, but the spy keyed it by bare name, so all
        # 13 derived nodes reported the identical token and six unrelated
        # classes read as "shared measurement: failing-modules" — i.e. as if
        # fixing NoSuchModule moved what ParseError measures.
        #
        # ⚑ I BANKED THAT AS A FINDING ONE MESSAGE AFTER FIXING THE SAME
        # COLLAPSE FOR BUILD ARTIFACTS, and called it "honest". A set reported
        # as a scalar is the flattening this sitting is about; noticing it for
        # `op:` reads and not for figure reads is the special-case tell.
        check(
            "a parameterized figure is keyed by its argument",
            [t for t in _fc if t.startswith("failing-modules")],
            ["failing-modules:other:NoSuchModule"],
        )
        check("and it does NOT report the bare figure name", "failing-modules" in _fc, False)
        # ⚑ THE PROPERTY THAT MAKES THE TIE DISSOLVE: two DIFFERENT kinds must
        # not share the projection key.  My first draft of this case
        # intersected a footprint with ITSELF — trivially true, and it would
        # have passed against the flattened spy that caused the bug.
        _pe = reads("other:ParseError") or []
        check(
            "two different kinds share NO failing-modules key",
            sorted(
                {t for t in _fc if t.startswith("failing-modules")}
                & {t for t in _pe if t.startswith("failing-modules")}
            ),
            [],
        )
        # and the census artifact IS still shared — the operational edge stands
        check(
            "but they DO still share the census artifact",
            "op:agda/.leaf-verify.tsv" in _fc and "op:agda/.leaf-verify.tsv" in _pe,
            True,
        )
        check(
            "every op: token has a declared producer",
            [t for t in _fc if t.startswith("op:") and not _F3.DERIVED.get(t[3:])],
            [],
        )
        # ⚑ A SOURCE READ IS NOT RETYPED.  Editing `scope_fix.py` IS the work,
        # so two readers of it genuinely do move each other's figure — the
        # distinction dies if every path becomes operational.
        _sc = reads("A5-as-reach") or []
        check(
            "a source read stays SUBSTANTIVE",
            [t for t in _sc if t.startswith("file:scratch/scope_fix.py")],
            ["file:scratch/scope_fix.py"],
        )

    bad = [c for c in cases if not c[1]]
    for label, _, got, want in bad:
        print("  FAIL %s: got %r want %r" % (label, got, want))
    print("selftest: %d/%d" % (len(cases) - len(bad), len(cases)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
