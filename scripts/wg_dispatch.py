#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""wg_dispatch.py — the `parts` channel: which routes are commands, and running them.

⚑ THIS IS A SEAM, NOT A NEW LAYER.  Split out of `worklist_gate.py` (1,458 code
lines, over the 1200 threshold) on 2026-08-11.  The seam is chosen by WHAT STATE
THE GROUP TOUCHES: everything here reads the channels a witness FILLS (`PARTS`,
`WHY`) and, for `dispatch_parts`, ACTS on them by spawning other tools.  It is
the only group with a write/execute blast radius, which is precisely why it is
worth having its own file — the `--apply` guard and the runnability predicate
that gates it now sit together rather than being separated by 400 lines of
ordering code.

`solvers()` lives here for the same reason: it answers "which TOOL repairs this
failure class", which is the same question `part_is_runnable` asks one row down.

⚑ `worklist_gate.py` RE-EXPORTS EVERY NAME HERE.  The public surface did not
move — a caller still writes `worklist_gate.dispatch_parts(...)`.
"""

import os
import re
import subprocess
import sys

import wg_engine


def solvers(ledger=None):
    """{failure-class: {"tool": name|None, "n": modules, "sample": mod}}.

    ⚑ WHICH ITEM'S TOOL SOLVES THIS FAILURE CLASS — the question the DAG needed
    and nothing answered.  13 derived nodes carry 115 build failures and have
    ZERO edges, so the ordering ranks them at leverage 0 and `--next` reports a
    tie between two leverage-0 authored items instead.  "No solution matched"
    was a state I could only reach by reading, and a state nobody else could
    reach at all.

    ⚑ THE SIGNAL IS THE REMEDY `_classify` ALREADY EMITS, not the parts route.
    Every class's parts route names `split_pipeline --diagnose <mod>` — the
    DRIVER, which diagnoses rather than fixes, so routing on it would report
    one solver for everything.  `_classify`'s third element is the remedy, and
    it is emitted only where the classifier knows the repair.

    ⚑ MEASURED 2026-08-03, AND THE ANSWER IS MOSTLY `NONE`: 1 class of 13 has a
    tool (`file-not-found` → 42 modules → `--rewire-only`).  The other 12
    classes, 73 modules, emit no remedy.  That is not a gap in this query — it
    IS the finding: three quarters of the failing modules have no mechanised
    repair, which is what an unattached node in the DAG means and why declaring
    an `enables` edge for them would be fiction."""
    import re as _re

    led = ledger or os.path.join(wg_engine.ROOT, "agda", ".leaf-verify.tsv")
    sys.path.insert(0, os.path.join(wg_engine.ROOT, "scratch"))
    import split_pipeline as SP

    out = {}
    try:
        fh = open(led, encoding="utf-8")
    except OSError:
        return out
    with fh:
        for line in fh:
            if line.startswith("#"):
                continue
            p = line.rstrip("\n").split("\t")
            if len(p) < 2 or p[1] != "build-failed":
                continue
            log = os.path.join(
                wg_engine.ROOT,
                "agda",
                "_build",
                "2.8.0",
                "agda",
                p[0].replace(".agda", ".agdai.log"),
            )
            txt = ""
            if os.path.exists(log):
                txt = open(log, encoding="utf-8", errors="replace").read()
            kind, _detail, remedy = SP._classify(p[0], txt)
            # ⚑ ROUTE THROUGH THE FIGURE'S REFINEMENT — this called `_classify`
            # DIRECTLY, so when `figures._refine` split `NotInScope` into its
            # three verdicts the item roster gained three keys and THIS query
            # still reported the old single class.  Two derivations of one
            # relation, which is the defect this arc has paid for in four
            # `agda_files()` bodies and again here, in the same hour I named it.
            sys.path.insert(0, wg_engine.LIBRARY)
            import figures as _F

            kind = _F._refine(kind, p[0])
            # ⚑ THE REMEDY IS LOOKED UP ON THE REFINED KIND.  `_classify`
            # returns the unrefined one (it has no census context), so a
            # `CLASS_REMEDY` keyed on a refined class can only be resolved
            # HERE, after the split — otherwise the entry is unreachable and
            # the class reads as toolless, which is the inert-guard shape.
            remedy = remedy or SP.CLASS_REMEDY.get(kind)
            tool = None
            if remedy:
                m = _re.search(r"(?:scratch|scripts)/(\w+)\.py", remedy)
                tool = m.group(1) if m else remedy.split()[0]
            row = out.setdefault(kind, {"tool": tool, "n": 0, "sample": p[0], "by_tool": {}})
            row["n"] += 1
            row["by_tool"][tool] = row["by_tool"].get(tool, 0) + 1
            # ⚑ A CLASS WITH A MIXED VERDICT IS REPORTED AS UNSOLVED, not as
            # solved-by-the-first-one-seen.  A partially-mechanised class is
            # not mechanised.
            if row["tool"] != tool:
                row["tool"] = None
    # ⚑ AND `MIXED` IS KEPT, NOT COLLAPSED INTO `NONE` (user, 2026-08-03: a
    # partial verdict *"needs addressing... matched to an existing item or to
    # have a synthesized item made"*).  I named the collapse as a design choice
    # and stopped — but "some of this class is mechanised and some is not" is a
    # DIFFERENT finding from "nothing repairs this class", and it wants a
    # different item: extend the tool's coverage vs. build one.  Folding them
    # loses exactly the distinction that decides the work.
    for row in out.values():
        row["mixed"] = len(row["by_tool"]) > 1
    return out


def class_modules(kind, ledger=None):
    """Every build-failed module in ONE refined failure class.

    ⚑ `solvers()` COMPUTES THIS SET AND THROWS IT AWAY, keeping `n` and one
    `sample`.  So the census can say *"27 modules → split_pipeline"* and nothing
    can run the tool over those 27: the class→tool edge is measured and
    unrunnable, and the operator re-derives the population by hand.  That is the
    argmax-discard shape — a query that reports the SIZE of a set it had in hand
    and not the set.

    ⚑ IT REPEATS `solvers()`'s WALK RATHER THAN CACHING IT, deliberately.  The
    classification depends on the per-module logs, which a repair invalidates as
    it runs; a memo would hand the second half of a sweep a population computed
    before the first half changed it.  The walk is cheap (a log read per failed
    module); staleness here is not.
    """
    led = ledger or os.path.join(wg_engine.ROOT, "agda", ".leaf-verify.tsv")
    sys.path.insert(0, os.path.join(wg_engine.ROOT, "scratch"))
    import split_pipeline as SP

    sys.path.insert(0, wg_engine.LIBRARY)
    import figures as _F

    out = []
    try:
        fh = open(led, encoding="utf-8")
    except OSError:
        return out
    with fh:
        for line in fh:
            if line.startswith("#"):
                continue
            p = line.rstrip("\n").split("\t")
            if len(p) < 2 or p[1] != "build-failed":
                continue
            log = os.path.join(
                wg_engine.ROOT,
                "agda",
                "_build",
                "2.8.0",
                "agda",
                p[0].replace(".agda", ".agdai.log"),
            )
            txt = ""
            if os.path.exists(log):
                txt = open(log, encoding="utf-8", errors="replace").read()
            k, _detail, _remedy = SP._classify(p[0], txt)
            if _F._refine(k, p[0]) == kind:
                out.append(p[0])
    return out


def sweep(kind, apply=False, limit=None, ledger=None):
    """Run a failure class's ATTACHED tool over every module in that class.

    ⚑ THE MISSING HALF OF `solvers()` (Ⓒ35, 2026-08-17).  Two classes are
    SOLVED — `file-not-found` and `other:NotInScope:resolvable`, 40 of 102
    failing modules — and both were being worked one module at a time from a
    count the census printed.  Mechanising a per-module repair and leaving its
    POPULATION to a human is the reasoning-in-the-turn shape at the level above
    the tool: the judgement moved into `unblock`, the iteration did not.

    ⚑ IT REFUSES AN UNATTACHED OR MIXED CLASS RATHER THAN GUESSING.  `solvers()`
    reports `tool: None` for both "no tool" and "several tools disagree", and
    those want different work (build one vs. extend one) — running SOMETHING
    over either would invent an edge the census declined to declare.

    ⚑ AND THE DRIVER IS `unblock`, NOT THE REMEDY STRING.  `CLASS_REMEDY`'s
    entries are documentation naming a tool, with placeholders (`<build.log>`)
    that `part_is_runnable` already refuses to execute.  `unblock` is the
    codified loop over both solved classes — it re-diagnoses per round, descends
    into a chain, and STALLS on a repeated blocker.  Re-deriving a per-module
    invocation from the remedy text would be a second, dumber driver.

    Returns [(module, verdict, chain-length)] — the verdict is `unblock`'s own.
    """
    rows = solvers(ledger=ledger)
    row = rows.get(kind)
    if row is None:
        return None, "no such class in the current census"
    if row.get("mixed"):
        return None, (
            "class is MIXED (%s) — partially mechanised is not "
            "mechanised; extend the tool or split the class"
            % ", ".join(sorted(str(t) for t in row["by_tool"]))
        )
    if not row.get("tool"):
        return None, "class has no attached tool — building one is the work"
    mods = class_modules(kind, ledger=ledger)
    if limit:
        mods = mods[:limit]
    sys.path.insert(0, os.path.join(wg_engine.ROOT, "scratch"))
    import split_pipeline as SP

    out = []
    for m in mods:
        path = m if m.startswith("agda/") else os.path.join("agda", m)
        try:
            verdict, chain = SP.unblock(path, max_rounds=12, apply=apply)
        except Exception as e:
            # ⚑ A FAILED REPAIR IS A ROW, NEVER AN ABORT.  A sweep that dies on
            # module 3 of 27 leaves 24 unattempted and reports nothing about
            # them; the population is the point.
            verdict, chain = "FAILED %s" % type(e).__name__, []
        out.append((m, verdict, len(chain)))
        print(f"   {verdict:<16} {m}" + (f"  (+{len(chain)} link)" if chain else ""), flush=True)
    return out, None


RUNNABLE_PREFIX = ("python3 ", "make ", "scripts/", "scratch/")


def part_is_runnable(route):
    """Is this `parts` row's route a COMMAND, or prose describing the work?

    ⚑ MEASURED BEFORE ASSUMING, AND THE ASSUMPTION WAS WRONG.  The 13 census
    witnesses I wrote emit `python3 scratch/split_pipeline.py --diagnose <mod>`;
    `A5-using` emits `provider-cone 3180, 3180 exclusive`.  Across all 22
    items emitting parts: **53 command routes, 45 prose**.  A dispatcher that
    executed `route` would have worked on every row I had just written and
    failed on nearly half the corpus — the guard-from-the-instance defect,
    which this repo has recorded five times and which I would have committed
    while building the guard against it.

    ⚑ SO RUNNABILITY IS A PROPERTY OF THE ROW, decided here, and a prose route
    is NOT a defect: it is a description of work no single command performs.
    Reporting it as "unrunnable" would be the tally-without-denominator shape;
    it is reported as PROSE, which is what it is.

    ⚑ AND A PREFIX TEST ACCEPTS A TEMPLATE (measured 2026-08-04, on a route I
    had just introduced).  Routing derived-failure parts through `_classify`'s
    remedy surfaced `CLASS_REMEDY`'s entry verbatim — `python3
    scratch/fix_notinscope.py <build.log> --apply` — which passes the prefix
    and would have run `<build.log>` as a literal path under `--apply`, nine
    times.  That table's own comment says an entry is documentation EARNED BY A
    MEASUREMENT; it names the tool, it is not a filled command line.
    A placeholder is the row saying an argument is still unbound, so the row is
    PROSE by the same reasoning as a route no single command performs —
    decided here rather than by the dispatcher discovering it at runtime."""
    r = str(route)
    return r.startswith(RUNNABLE_PREFIX) and not re.search(r"<[^<>\s]+>", r)


def dispatch_parts(key, apply=False, limit=None):
    """Run an item's `parts` rows — the channel's FIRST consumer that acts.

    ⚑ `parts` WAS A DECLARED CHANNEL WITH A DISPLAY-ONLY CONSUMER (user,
    2026-08-03: *"Better to have something slightly wrong than something
    unbuilt."*).  Measured: `PARTS` had exactly two readers, both in this file,
    and both PRINT — grouped by route, formatted.  The rows carry routes that
    are runnable by construction and nothing ran them; a human read the line
    and retyped it.  `SIZES`, the sibling channel, IS consumed (it feeds the
    sort key), which is what made the asymmetry legible.

    ⚑ THIS IS THE SYNTHESIS STEP: a witness's rows are the NEXT witness's
    ARGUMENTS.  `_census_witness` is parameterised over an error class and
    emits one row per failing module; those module names are exactly what a
    per-module diagnosis takes.  That only works because every witness takes
    what it needs rather than closing over globals — `T25-parametric` read as
    hygiene and is in fact the precondition for this layering.

    ⚑ DRY RUN BY DEFAULT.  Every write tool in this repo gates on `--apply`,
    and the one that did not (`prune_imports`) cost an unintended 12-line
    deletion.  A dispatcher runs OTHER tools, so its blast radius is theirs."""
    rows = _item_parts(key)
    out = []
    for label, n, route in rows[:limit] if limit else rows:
        if not part_is_runnable(route):
            out.append((label, n, route, "prose", None))
            continue
        if not apply:
            out.append((label, n, route, "would-run", None))
            continue
        # ⚑ NO shell=True — the route is DATA from a witness, and a witness is
        # code this repo generates.  `shlex.split` keeps it an argv, so a route
        # can never become a shell injection surface as the channel widens.
        import shlex

        try:
            p = subprocess.run(
                shlex.split(route), capture_output=True, text=True, cwd=wg_engine.ROOT, timeout=300
            )
            tail = (p.stdout or p.stderr).strip().splitlines()
            out.append(
                (label, n, route, "ran rc=%d" % p.returncode, tail[-1][:120] if tail else "")
            )
        except Exception as e:
            # ⚑ A FAILED DISPATCH IS REPORTED, NEVER SWALLOWED.  A dispatcher
            # that hides an error reports the work as done.
            out.append((label, n, route, "FAILED %s" % type(e).__name__, str(e)[:120]))
    return out


def _item_parts(key):
    """The structured breakdown a witness returned, or [].

    ⚑ READ FROM `PARTS`, WHICH THE WITNESS FILLS -- never re-derived here.  The
    ordering must not recompute a partition the item already computed; that is
    two authorities for one relation, and the item owns its own shape."""
    sys.path.insert(0, wg_engine.LIBRARY)
    try:
        import items as I

        return I.PARTS.get(key, [])
    except Exception:
        return []


def _item_why(key):
    """The witness's own verdict sentence for `key`, or None.

    ⚑ `--next` NAMED AN ITEM AND MADE YOU RUN ITS WITNESS (user, 2026-08-05:
    *"`--next` should imply `--row` for the next (and runner-up) item"*).  It
    printed the key, the grades and the breakdown -- everything except WHY the
    item is open, which is the one thing an operator reads next.  So the honest
    use was two commands, `--next` then `items.py --row <key>`, with the second
    re-running a witness the ordering had ALREADY run to compute openness.
    Reasoning in the turn, and a redundant walk to boot.

    ⚑ AND THE VERDICT IS ALREADY IN HAND.  The ordering drains every witness;
    `_drain` returns the verdict row and `WHY` keeps it, exactly as `PARTS`
    keeps the breakdown.  This reads that -- it does not re-run anything."""
    sys.path.insert(0, wg_engine.LIBRARY)
    try:
        import items as I

        return I.WHY.get(key)
    except Exception:
        return None


def gates_reached(key, cone):
    """The hook-wired gates in an item's cone — the COMMIT-PATH evidence.

    ⚑ DEAD CAPABILITY AS OF 2026-08-11 — `--calls gates_reached` reports
    1 def, 0 calls, which is the `rewire_only` class this repo censuses.  It is
    CARRIED, not deleted: the reasoning below is the mechanized form of a
    tiebreak that was once performed by hand, and deleting it would return that
    judgement to the turn.  Wiring it is work, not a finding.

    ⚑ I ADJUDICATED A TIE BY READING TWO VERDICTS AND REASONING (user, and it
    is the shape corrected all session).  `G6` vs `T23-local`: same layer, same
    leverage, sizes 11 and 12 -- the ordering refused, correctly, and I broke it
    by hand on the grounds that *G6 blocks the commit and T23-local blocks
    nothing*.  That rationale is not taste and it is not prose: `gate_status`
    already parses `.githooks/pre-commit` for exactly the set of gates that
    stand between the tree and a commit.

    So the tiebreak reads it.  An item whose cone contains a hook-wired gate is
    on the commit path; one whose cone does not is tidying.  Both are real work
    and only the first has a deadline attached to it.

    ⚑ REPORTED, NOT AUTO-APPLIED.  A tie is an UNDISCHARGED CLAIM about the
    ordering (the standing rule), so this supplies the evidence a human uses to
    declare the edge -- it does not silently mint one.  An ordering that
    invents its own edges cannot be audited against the bib."""
    # ⚑ A REFUSAL NAMES ITS CAUSE.  My first cut swallowed every exception into
    # `None`, so the evidence line simply did not print and the tie looked
    # unmeasurable -- the guard-degrades-to-measuring-nothing class, in the
    # measurement built to stop me adjudicating by hand.
    sys.path.insert(0, os.path.join(wg_engine.ROOT, "scripts"))
    try:
        import gate_status

        rows = gate_status.gates()
    except Exception as e:
        return ["<gate_status unavailable: %s>" % type(e).__name__]
    # ⚑ AND THE SHAPE IS `(name, argv, conditional)`, WHICH I GUESSED WRONG.
    # My first cut read `g["path"]` -- an invented key, the eighth invented API
    # this session -- and the refusal I had just added is what named it.  The
    # script is inside `argv`; the docstring says so.
    # ⚑ THE SECOND FIELD IS A COMMAND STRING, NOT AN ARGV LIST -- three wrong
    # shapes in a row on ONE function (`g["path"]`, then `for a in argv`
    # iterating CHARACTERS, then stripping quotes off those characters), each
    # from guessing rather than reading `gates()`'s own `out.append((name,
    # rest.strip(), bool(indent)))`.  The refusal-names-its-cause line is what
    # made each attempt legible instead of silently empty; `--binding out` is
    # what finally answered it.
    wired = set()
    for _name, cmd, _cond in rows:
        for tok in str(cmd).replace('"', " ").replace("'", " ").split():
            if tok.endswith(".py"):
                wired.add(os.path.basename(tok))
    if not wired:
        return ["<no hook-wired gate parsed>"]
    sys.path.insert(0, wg_engine.LIBRARY)
    try:
        import items as I
    except Exception:
        return None
    # ⚑ A BUILD-LOG READER IS A BLOCKER SOURCE BY CONSTRUCTION, AND ASKING THE
    # ITEM GRAPH THROWS THAT AWAY (user, 2026-08-03: *"anything that generates
    # rows from reading build logs INTRINSICALLY surfaces rows which block make,
    # which intrinsically blocks the commit"*).
    #
    # The six `other:*` error classes tied at leverage -1 because this function
    # walked the cone hunting a `check_*.py` name and found none.  Every one of
    # them is a row minted from a FAILED TYPECHECK -- so each fails
    # `make -C agda -j`, which sets `fail=1` at `.githooks/pre-commit:311` and
    # refuses the commit.  The evidence was never missing; it was never asked for.
    #
    # ⚑ AND THE FIX IS NOT TO PARSE THE HOOK'S `make` LINE INTO `gate_status`.
    # That mints a SECOND, independently computed answer to "does this block the
    # commit" -- the derived-view divergence (§6) this arc has paid for four
    # times.  The build gate is not spelled as a `run` line (it must branch: on
    # success it stamps and regenerates the catalog), so `gates()` cannot see it
    # and SHOULD NOT be taught to: the provenance already carries the fact.
    #
    # `pycodemod.build_artifact_readers` classifies TOOLS, once, by whether the
    # artifact they read can contain a failure.  `.agdai.log` can; `.agdai` (a
    # compiled core) and `.agda-times.tsv` (membudget records only SUCCESSFUL
    # compiles) cannot.  Measured: 11 of 44 readers are failure-bearing, so the
    # distinction genuinely divides the population rather than admitting it whole.
    blocker_tools = set()
    try:
        sys.path.insert(0, os.path.join(wg_engine.ROOT, "scratch"))
        import pycodemod as _pc

        for rel, _arts, bearing in _pc.build_artifact_readers():
            if bearing in ("FAILURE", "BOTH"):
                blocker_tools.add(os.path.basename(rel))
    except Exception as e:
        # ⚑ A REFUSAL NAMES ITS CAUSE -- the same rule this function already
        # records for `gate_status`.  Degrading to "no evidence" would report a
        # measurable fact as unmeasurable, which is what -1 already did once.
        return ["<artifact provenance unavailable: %s>" % type(e).__name__]

    hit = set()
    for k in [key] + sorted(cone(key)):
        fn = I.ITEMS.get(k)
        if fn is None:
            continue
        src = ""
        try:
            import inspect

            src = inspect.getsource(fn)
        except Exception as e:
            # ⚑⚑ AN UNREADABLE WITNESS USED TO READ AS AN UNWIRED ONE.  `hit` is the
            # RETURNED verdict set, so `continue` on a source-read failure removes the
            # item from consideration and the caller sees exactly what it would see if
            # the item genuinely wired nothing.  A witness defined in a REPL, a C
            # extension, or a file moved since import all land here — and each reads as
            # a negative result rather than as an unanswerable question.
            #
            # ⚑ STILL CONTINUES — one unreadable witness must not abort the whole
            # dispatch — but the skip is now NAMED.  Found by `pycodemod --swallows`,
            # which flags a discard whose work feeds a returned value.
            print(
                "wg_dispatch: cannot read source of %r (%s) — EXCLUDED from the "
                "wired-witness scan; this is a fact about the READ, not evidence "
                "the item wires nothing" % (k, type(e).__name__),
                file=__import__("sys").stderr,
            )
            continue
        for g in wired:
            if g and g in src:
                hit.add(g)
        # a witness that runs a failure-bearing reader is on the commit path via
        # the full build, whose failure is `make`'s and therefore the hook's
        for t in blocker_tools:
            if t in src:
                hit.add("make -C agda -j (via %s)" % t)
    return sorted(hit)
