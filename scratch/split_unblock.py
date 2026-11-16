#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The BLOCKER-CHASE layer of the split pipeline: verify → diagnose → unblock.

⚑ A SEAM, NOT A NEW TOOL — AND DELIBERATELY NOT A CLI.  `split_pipeline.py` stays THE
supported entry point; these are reached through its `--verify`, `--diagnose`, `--why`
and `--unblock` modes, which is where the stage sequencing lives.  What is grouped here
is the layer that answers *does this file compile, whose fault is it, and what clears
it* — as against the driver's write-stages (split / prune / rewire / retire) and
`split_census`'s read of the build's own artifacts.

⚑ THE SELFTEST STILL REACHES THESE, AND THAT IS BY DESIGN.  Six cases in
`split_pipeline._selftest` call `inspect.getsource(unblock)` and assert the properties
that make the loop SAFE rather than merely automatic — that it checks `leaves_ready`
before rewiring, that a repeated blocker STALLS, that `max_rounds` is a runaway guard
and not a capability bound, that a descent re-enters rather than assuming.
`inspect.getsource` resolves through the function object, so it follows the def here;
the guards are unweakened by the move.  The `unblock(` reachability case reads the
DISPATCH source instead, which is why the dispatch block did not move.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scratch"))

AG = "agda"


def _driver():
    """The driver module, imported LATE.

    ⚑ THE CYCLE IS REAL AND THE LATE IMPORT IS THE POINT.  `unblock` repairs a link by
    calling `rewire_only`, which is a WRITE-stage and belongs to the driver; the driver
    in turn re-exports these read-side names.  Importing at module scope would close
    that loop at import time.  Resolving it per call keeps ONE implementation of the
    repair (the driver's) rather than a second copy here — a private twin of a write
    stage is exactly how two spellings of one relation start disagreeing.
    """
    import split_pipeline
    return split_pipeline


def isolate_check(leaf_path, mb=None):
    d = _driver()
    return d.isolate_check(leaf_path, d.DEFAULT_MB if mb is None else mb)


def blame(leaf_path, out):
    return _driver().blame(leaf_path, out)


def rewire_only(modname, apply=False):
    return _driver().rewire_only(modname, apply=apply)


def _classify(path, txt, trace=None):
    import split_census
    return split_census._classify(path, txt, trace=trace)


def verify(paths, jobs=None):
    """Typecheck each path and report ('clean'|'own'|'dependency', cited) per file.

    ⚑ EXISTS BECAUSE THE INVOCATION WAS BEING ASSEMBLED BY HAND EVERY TIME —
    `cd agda && membudget run 384 <label> -- agda --safe -i. <rel>` — which is four
    pieces of knowledge (the cwd, the memory lease, the label convention, the
    flags) living in a shell line instead of in the tool.  `isolate_check` already
    owns all four and `blame` already interprets the result; this joins them so
    "does this file compile, and whose fault is it" is ONE command.

    The distinction matters: during R9-VERIFY, 9 of 12 "failures" cited a
    DEPENDENCY, not the file under test.  Reading that as a 48% failure rate
    nearly caused a rollback of working code; the true leaf-own rate was ~19%.

    ⚑ PARALLEL, BECAUSE `membudget` IS ALREADY THE ARBITER AND THIS IGNORED IT
    (user, 2026-08-01: *"Is the census actually parallelized properly?"* — it was
    not).  The first version was a plain serial `for`: 1322 compiles, one `agda`
    process at a time, ~40 minutes.  That is not merely slow, it CONTRADICTS the
    repo's own build discipline — `membudget` exists so concurrent compiles
    self-throttle against a RAM semaphore, which is why the build oversubscribes
    the budget and lets the semaphore arbitrate.  (⚑ This cited CLAUDE.md's
    *"`make -j` with NO number is the right invocation"*; ⟡agda-jobs replaced the
    bare `-j` with a width from one authority — the RAM argument above is
    UNCHANGED and still the reason, but the invocation it justified is not the
    current one, so the citation is corrected rather than left pointing at
    superseded text.)  Each `isolate_check` is an
    independent subprocess with its own lease label and no shared state, so the
    only thing serialising them was this loop.

    Workers are deliberately MORE than the RAM budget allows to run at once: a
    blocked lease SLEEPS in `membudget` and wakes when one frees, so oversubscribing
    keeps the semaphore saturated rather than idling between compiles.  The cap is
    on THREADS (cheap, blocked in `subprocess.wait`), never on memory — memory is
    `membudget`'s job and duplicating that ceiling here would be two authorities for
    one limit.
    """
    from concurrent.futures import ThreadPoolExecutor
    if jobs is None:
        # oversubscribe deliberately: a blocked lease sleeps inside `membudget`
        # and wakes on release, so more threads than the RAM budget admits keeps
        # the semaphore saturated instead of idling between compiles.
        jobs = min(32, (os.cpu_count() or 4) * 2)

    def _one(p):
        rel = p[len(AG) + 1:] if p.startswith(AG + "/") else p
        rc, txt = isolate_check(p)
        return (p,) + blame(rel, txt if rc else "")

    if len(paths) < 2 or jobs == 1:
        return [_one(p) for p in paths]
    # ⚑ A LONG RUN THAT PRINTS NOTHING IS INDISTINGUISHABLE FROM A HUNG ONE.  The
    # serial version emitted its first line only at the end; two operators (me,
    # twice) killed or re-launched runs that were working.
    done, total = [0], len(paths)
    out = []
    with ThreadPoolExecutor(max_workers=jobs) as ex:
        for row in ex.map(_one, paths):
            out.append(row)
            done[0] += 1
            if done[0] % 100 == 0 or done[0] == total:
                print(f"   … {done[0]}/{total}", flush=True)
    return out


def diagnose(path, trace=None):
    """(kind, detail, remedy) — WHAT is wrong with this file and WHAT repairs it.

    ⚑ THE JUDGEMENT BETWEEN `--why` AND THE REPAIR WAS MINE, TWICE, UNCODIFIED.
    Working the A4 blocker list, each file took THREE commands and a decision in
    the middle: `--why` to see the error, `resolve_notinscope` to find the real
    home, then `--rewire-only` — with me classifying "this is the consumed-parent
    class" in between.  That classification is a PREDICATE over the compiler's own
    output, so it belongs here (user, 2026-08-01: *"needing to run more than one
    tooling command indicates you're applying reasoning not codified"*).

    The consumed-parent class is the one that RECURS on every split (§13, §26, §46,
    §49): the parent was split into leaves, its importers were never rewired, and
    the module it names no longer exists.  The tell is `[FileNotFound]` on a
    `Substrate.*` module that HAS a leaf directory — and `rewire_only` is exactly
    its repair, so the remedy can be emitted as a runnable command rather than
    described.

    Returns ('clean'|'file-not-found'|'other', detail, remedy-or-None).
    """
    rc, txt = isolate_check(path)
    return _classify(path, txt if rc else "", trace=trace)


def leaves_ready(modname):
    """(ok, rows) — do this consumed parent's leaves COMPILE, before we rewire onto them?

    ⚑ C2's PRECONDITION, AND IT CHANGED THE ANSWER ON FIRST USE.  `diagnose`
    classifies `[FileNotFound]` as the consumed-parent class when the missing
    module HAS a leaf directory — but a directory's EXISTENCE is not its CONTENT
    (the same shape as `leaf_map` guarding on `os.path.isdir` and reading an EMPTY
    directory as "has leaves").  A split that was started and never finished
    leaves a directory of leaves that never compiled, and rewiring 20 consumers
    onto those trades one error for twenty.

    MEASURED, 2026-08-04: working the `Q.Reduction` blocker, the leaves came back
    `dependency`-blocked behind `Nat/GCD/ComputeTrace.agda` — NOT broken in
    themselves, but not yet a valid rewire target either.  Clearing the deeper
    root FIRST made them clean and the rewire correct.  Acting on the emitted
    remedy without this check would have cleared one error and re-exposed the same
    one, one layer down.

    ⚑ `dependency` IS NOT `own`, AND BOTH BLOCK THE REWIRE.  A leaf that fails on
    ITS OWN content needs repair (R12b's class); a leaf blocked behind something
    else needs that something else cleared first.  They want different work, so
    the rows are returned rather than collapsed to a bool — the caller decides,
    and `n of m` is preserved."""
    leaf_mods = _under(modname)
    if not leaf_mods:
        return False, []
    paths = []
    for m in leaf_mods:
        p = os.path.join("agda", *m.split(".")) + ".agda"
        if os.path.exists(p):
            paths.append(p)
    if not paths:
        return False, []
    rows = []
    for p in paths:
        rc, txt = isolate_check(p)
        verdict, cited = blame(p, txt if rc else "")
        rows.append((p, verdict, cited))
    return all(v == "clean" for _p, v, _c in rows), rows


def _under(modname):
    """Every module under `modname.` — the leaf set, read from the tree."""
    base = os.path.join("agda", *modname.split(os.extsep if False else "."))
    out = []
    if not os.path.isdir(base):
        return out
    for dirpath, _dirs, files in os.walk(base):
        for fn in sorted(files):
            if fn.endswith(".agda"):
                rel = os.path.relpath(os.path.join(dirpath, fn), "agda")
                out.append(rel[: -len(".agda")].replace(os.sep, "."))
    return sorted(out)


def _repair_notinscope(path):
    """Supply a `[NotInScope]` name's definer, via `fix_notinscope`.  Returns the
    number of imports added (0 = nothing the index could supply, or a refusal).

    ⚑ THE INPUT IS A FRESH COMPILE, NOT THE PERSISTED LOG.  `fix_notinscope` takes a
    BUILD LOG, and §52 measured 1770 of 2810 per-module logs stale — inside a repair
    loop a stale log would name a name the previous round already fixed, and the loop
    would 'repair' it forever.  `isolate_check` is the same compile `diagnose` runs,
    so the log handed over describes the tree as it is right now.

    ⚑ THE TEMPFILE IS NOT A CACHE.  It exists for one call because the delegate's
    interface is a path; writing it under the build tree would make it look like a
    build artifact and invite a later reader to trust its age.
    """
    import re as _re
    import subprocess
    import tempfile
    _rc, txt = isolate_check(path)
    if not txt:
        return 0
    with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False,
                                     encoding="utf-8") as fh:
        fh.write(txt)
        log = fh.name
    try:
        r = subprocess.run(["python3", "scratch/fix_notinscope.py", log, "--apply"],
                           capture_output=True, text=True, cwd=ROOT)
        out = (r.stdout or "") + (r.stderr or "")
        for ln in out.split("\n"):
            if ln.strip():
                print(f"     {ln.rstrip()}")
        # ⚑ COUNT THE `ADD` LINES THE TOOL EMITS, MINUS THE ONES IT REVERTED.  My
        # first cut regex-matched a summary count (`(\d+) added|kept|import`) that
        # `fix_notinscope` never prints — so a run that DID repair reported
        # `0 link(s) repaired` and the loop treated a success as a dead end.
        # A parse of an output shape the delegate does not produce is the
        # docstring-as-evidence error one layer down: I read the tool's prose for
        # its interface instead of its emission.
        added = len(_re.findall(r"^\s*ADD\s", out, _re.M))
        reverted = len(_re.findall(r"^\s*REVERTED", out, _re.M))
        return max(0, added - reverted)
    finally:
        os.unlink(log)


def _repair_noparse(path):
    """Repair a FIXITY-collision `[NoParseForApplication]`, via `fix_noparse`.

    ⚑⚑ THE REMEDY WAS ATTACHED TO A CLASS IT COULD NOT REACH.  `fix_noparse`
    classifies from a LOG FILE, and the only paths to it were the persisted
    `agda/_build` logs — which §52 measured 1770-of-2810 stale.  So the tool
    reported `0 of 9 repaired` against a tree whose live compile carried the
    error, `unblock` returned `other:NoParseForApplication` as not-its-class,
    and the site was fixed by hand.  Three times in two days.

    ⚑ THE FIX IS THE ONE `_repair_notinscope` ALREADY MADE, one class over: hand
    the delegate the compile `diagnose` JUST RAN, not the build's memory of an
    older tree.  Same tempfile-for-one-call shape, same reason — the delegate's
    interface is a path, and writing it under `_build` would make it look like a
    build artifact and invite a later reader to trust its age.
    """
    import tempfile
    _rc, txt = isolate_check(path)
    if not txt:
        return 0
    sys.path.insert(0, os.path.join(ROOT, "scratch"))
    import fix_noparse as FNP
    with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False,
                                     encoding="utf-8") as fh:
        fh.write(txt)
        log = fh.name
    try:
        rows = FNP.classify(log)
        # ⚑ ONLY THE `fixity` VERDICT IS OURS.  A genuine precedence error is
        # REFUSED by the classifier, and repairing it would change what the term
        # MEANS — the refusal is the tool's, and this must not route around it.
        return FNP.repair(rows, apply=True)
    finally:
        os.unlink(log)


def unblock(path, max_rounds=None, apply=False):
    """Follow a `[FileNotFound]` CHAIN to its root, repairing each link.

    ⚑ MECHANIZED AFTER RUNNING IT BY HAND FOUR TIMES (user, 2026-08-04: *"You've
    got a repeatable process. Repeatable means mechanizable. Fix the tooling."*).
    Clearing ONE blocker took: `--diagnose` to classify, `--verify` on the leaves
    to check the target is sound, `--rewire-only --apply` to repair, then
    `--diagnose` again on the original file to see what surfaced.  Four commands
    and a judgement, repeated per link — which is the reasoning-not-codified shape
    the standing rule forbids, committed while working a worklist item about it.

    ⚑ A BLOCKER LIST MAY BE A CHAIN, AND MEASURING IT ONE HOP AT A TIME IS WHAT
    MADE IT EXPENSIVE.  §51 recorded that two of two worked blockers each cleared
    their own error and revealed a DEEPER one; §46's `F2/Vector` → `Universal` and
    §51's `V4-Coxeter` → `Coxeter/Core` are the same shape.  Measured here on the
    g-value chain: `Q.Reduce` → `Q.Reduction` → `ComputeTrace` → `Nat.WellFounded`,
    then two more links above it.  So the loop is the unit of work, not the hop.

    ⚑ TERMINATION IS BY STRICT PROGRESS, NOT A ROUND CAP.  Each round must either
    clear the file or name a DIFFERENT blocker than last round; a repeated blocker
    means the repair did not take, and continuing would spin.  `max_rounds` exists
    only as a runaway guard for a cycle the predicate cannot see — the same
    distinction `agda_lex.head_span` settled (a TERMINATION bound is fine; a
    CAPABILITY bound silently truncates).

    Returns (verdict, chain) where chain is the ordered list of roots repaired."""
    chain, seen = [], set()
    rounds = 0
    while True:
        rounds += 1
        if max_rounds is not None and rounds > max_rounds:
            return "runaway", chain
        kind, detail, _remedy = diagnose(path)
        if kind == "clean":
            return "clean", chain
        if kind.startswith("other:NotInScope"):
            # ⚑⚑ THE SECOND CLASS THE CHAIN ACTUALLY CONTAINS, AND WALKING IT BY
            # HAND IS WHAT THIS LOOP EXISTS TO STOP.  MEASURED 2026-08-17: an
            # eight-link chain (`NilpotentLogExpBridge` → `DLogHom` →
            # `FromCommRing` → `Graded` → `Nth` → `Conv` → `Distrib` → `Scalar`)
            # was cleared one hop at a time — `--why`, read, repair, `--why` again
            # — because this branch returned the moment the class was not
            # `file-not-found`.  A decomposition retires a barrel and BOTH classes
            # follow: the consumer that imported the barrel gets `[FileNotFound]`,
            # the consumer that reached a NAME through it gets `[NotInScope]`.
            # One cause, two error shapes, and the loop covered one.
            #
            # ⚑ IT DELEGATES RATHER THAN RE-DERIVING.  `fix_notinscope` is the
            # mechanical repair: look the name up in the definition index, add the
            # BARE import of its definer (ban-compliant), and REFUSE when several
            # definers exist rather than guess which the file meant.
            #
            # ⚑ AND ITS REVERT IS IN-MEMORY, WHICH IS WHY IT IS SAFE IN A LOOP.
            # `fix_notinscope.py:191` holds `before = src` before writing and
            # restores it at `:197` — no git, no staging area, no snapshot
            # ordering to get wrong, and per-file, so a chain that repairs three
            # links and reverts the fourth keeps the three.  The revert fires only
            # on `not ok and name in out`: a DIFFERENT error after the import means
            # the import helped and is KEPT (`:213`).  It is not "revert unless
            # perfect", it is "revert only if this name is still unbound".
            #
            # ⚑ AND IT DIAGNOSES ON THE WAY OUT: a correct import that still leaves
            # the name unbound means a stale `using` is shadowing it, which it
            # names (`fix_stale_using`) rather than leaving a bare revert for the
            # next reader to re-derive — measured on `SBoxTable`/`∧-elimˡ`.
            #
            # ⚑ AND IT NEEDS THE FILE'S OWN LOG, not the tree's.  `fix_notinscope`
            # reads a BUILD LOG; the per-module log may be stale (§52 measured
            # 1770 of 2810), so the fresh compile `diagnose` just ran is the
            # honest input — captured here rather than re-derived.
            if not apply:
                print(f"   → {os.path.basename(path)}: [NotInScope] {detail[:60]}")
                print("     (dry run — pass --apply to repair)")
                return "would-repair", chain
            if detail in seen:
                return "stalled", chain
            seen.add(detail)
            n = _repair_notinscope(path)
            if n == 0:
                # nothing the index could supply: a genuinely missing definition,
                # or an ambiguity the tool refused. Both want a human.
                return kind, chain
            print(f"   ✓ {os.path.basename(path)}: {n} import(s) supplied")
            chain.append(f"{path} [NotInScope]")
            continue
        if kind.startswith("other:NoParseForApplication"):
            # ⚑⚑ THE THIRD CLASS A RENAME LEAVES BEHIND, and the loop covered two.
            # A tree-wide `rename_at_source` that matches a bare token can hit a
            # PREFIX operator sharing the spelling of a binary one, and the site
            # then fails to PARSE rather than failing to resolve — so neither the
            # `file-not-found` arm nor the `NotInScope` arm sees it.  MEASURED
            # 2026-08-17/18: `Z/Properties/Add`, `MulFull` (twice), `Q/Field`,
            # `R/Trace/Properties` — each fixed by hand while a tool that
            # classifies the class sat one call away.
            #
            # ⚑ IT DELEGATES, AND THE DELEGATE'S REFUSAL STANDS.  `fix_noparse`
            # repairs only an infix operator with NO left operand; a genuine
            # precedence error is reported and left alone.
            if not apply:
                print(f"   → {os.path.basename(path)}: [NoParseForApplication] "
                      f"{detail[:60]}")
                print("     (dry run — pass --apply to repair)")
                return "would-repair", chain
            if detail in seen:
                return "stalled", chain
            seen.add(detail)
            n = _repair_noparse(path)
            if n == 0:
                # a precedence error the classifier refused, or nothing on the
                # reported line matched — both want a human.
                return kind, chain
            print(f"   ✓ {os.path.basename(path)}: {n} fixity site(s) repaired")
            chain.append(f"{path} [NoParseForApplication]")
            continue
        if kind != "file-not-found":
            # ⚑ NOT OUR CLASS — say so rather than guessing a remedy.  A
            # NoParse/UnequalTerms failure wants a different tool entirely (or a
            # human), and emitting a rewire for it is how A4-FNF's population got
            # overstated.
            return kind, chain
        if detail in seen:
            # The same blocker twice: the repair did not take.  Stopping here is
            # the honest outcome; looping would spin on a fixed point that is not
            # a success.
            return "stalled", chain
        seen.add(detail)
        ok, rows = leaves_ready(detail)
        if not ok:
            # ⚑ A BLOCKED LEAF IS NOT NECESSARILY A TERMINAL STATE — and my first
            # version treated it as one.  MEASURED: the loop stopped at
            # `Z.Coprime` reporting `own` on `CofactorCoprime.agda`, which reads
            # as "this leaf is broken, hand it to R12b".  It was not: the leaf's
            # own failure was ANOTHER `[FileNotFound]` on a consumed parent
            # (`Nat.GCD.GcdPos`), i.e. THE SAME CLASS THIS LOOP ALREADY REPAIRS.
            # Pointing `--unblock` at the leaf by hand cleared it in one hop.
            #
            # `blame()` attributes a `[FileNotFound]` to the file HOLDING the
            # import, so an unrepaired consumed parent surfaces as `own` on its
            # importer — which is correct attribution and a misleading CLASS
            # signal.  So the verdict is not the classifier; `diagnose` is.
            # Recursing here is what makes the loop find the ROOT rather than the
            # nearest broken file.
            deeper = []
            for p, verdict, _cited in rows:
                if verdict == "clean":
                    continue
                k, _d, _r = diagnose(p)
                if k == "file-not-found":
                    deeper.append(p)
            if deeper:
                print(f"   ↓ {detail}: {len(deeper)} leaf/leaves blocked by the "
                      f"SAME class — descending")
                for p in deeper:
                    v, sub = unblock(p, max_rounds=max_rounds, apply=apply)
                    chain.extend(sub)
                    if v not in ("clean", "would-repair"):
                        return v, chain
                # ⚑ RE-ENTER RATHER THAN ASSUME.  The descent may or may not have
                # made these leaves a valid target; only re-running the check says
                # so, and `seen` still guards against a repeat.
                seen.discard(detail)
                continue
            # ⚑ GENUINELY NOT OUR CLASS.  A leaf failing on its OWN content is
            # R12b's repair (re-emission), not a rewire — report WHICH and stop
            # rather than guess a remedy.
            print(f"   ✗ {detail}: leaves not ready — rewiring here would trade "
                  f"one error for many")
            for p, verdict, cited in rows:
                if verdict != "clean":
                    print(f"      {verdict:<10} {p}"
                          + (f"   cites {cited}" if cited else ""))
            return "leaves-blocked", chain
        print(f"   → {detail}: {len(rows)} leaf/leaves clean; rewiring")
        if not apply:
            print("     (dry run — pass --apply to repair)")
            return "would-repair", chain + [detail]
        rc = rewire_only(detail, apply=True)
        if rc != 0:
            return "rewire-failed", chain
        chain.append(detail)
