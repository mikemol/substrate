# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""WHEN a guard FIRES, not where it is WRITTEN — the execution-order reading.

⚑⚑⚑ THE CENSUS THAT COULD NOT SEE THE ONLY DISTINCTION THAT MATTERS (Ⓐ48
⟡guard-placement-predicate).  `pycodemod --guarded guard` classifies a call by SOURCE
POSITION: a call not lexically inside an `if` is reported `top`.  Measured 2026-08-25
it reports **41 `top` sites**, and a prior agent measured that **ZERO of them refuse a
bare invocation** — because 30 of the 41 are the `_snapshot_once(path)` idiom, a
first-write-only helper whose body runs at the first PENDING WRITE.  A read-only mode,
a dry run that restores, or a `nothing droppable` run never reaches it.

**The position where a guard is WRITTEN is not the point where it FIRES.**  Source
position is the holder; execution order is the worker.  A census keyed on the holder
scores a first-write guard and an entry guard identically, and `--guarded`'s own
docstring is correct that its conditions are *source text, never reachability* — the
defect is not in that mode, it is that nothing answered the other question.

⚑⚑ THREE SPELLINGS ALREADY PARTITION THIS SPACE AND THIS IS DELIBERATELY NOT A FOURTH.

    pycodemod --guarded guard          WHERE the call sits lexically (source position)
    check_snapshot_guard.intent_census WHETHER the tool names the contract at all
                                       (a per-tool substring disjunction over
                                       `mutating_argv` / `intent=` / `require_at_entry`)
    edit_snapshot.require_at_entry     the RUNTIME authority — the guard itself

This module answers the question none of the three asks: **on a bare invocation, is the
contract reached before any mode dispatch?**  It consumes `--guarded`'s own visitor
output (`KwIndex.conds` / `.contexts`, gathered in the same scan) rather than
re-walking, and it does not restate `intent_census`'s membership test — that census
asks *is the contract named*, this one asks *is it reached*, and a tool can pass either
while failing the other.

⚑ WHAT IT CANNOT DECIDE — stated at the verdict, not only here, because `harness-rooted`
shipped honest by doing exactly that.  See `UNDECIDABLE`.
"""

import os
import sys

import _pycodemod_core
from _pycodemod_query import KwIndex, scan

ROOT = _pycodemod_core.ROOT

# ⚑ THE ENTRY-FORM SPELLINGS.  A call to any of these is the contract being demanded at
# the INVOCATION.  This is `intent_census`'s recognition list MINUS `intent=` and
# `mutating_argv`: those two state intent AT A DECISION, which is strictly later than
# entry, and folding them in here would collapse the very distinction this module exists
# to draw.  Named rather than substring-matched for the reason that census records — the
# three are not interchangeable, they differ in WHERE.
ENTRY_FORMS = ("require_at_entry", "require_explicit_mutation")

# ⚑⚑ THE SNAPSHOT FORMS — a SEPARATE call with a SEPARATE placement from the intent
# gate, and NOTHING BINDS THE TWO.  That decoupling is the recurrence vector the operator
# named: a tool can state intent at entry and snapshot at the write, or state intent and
# never snapshot at all, and `intent_census` scores both as compliant because it asks
# only whether the contract is NAMED.
SNAPSHOT_FORMS = ("guard", "_snapshot_once")

# ⚑⚑⚑ THE THIRD AXIS: A SNAPSHOT IS A FILESYSTEM ACT.  It copies files aside; it cannot
# capture a postgres mutation.  So "snapshot taken" on a store-writing tool is a FALSE
# ASSURANCE — strictly worse than no signal, because the operator reads it as recoverable
# and it is not.  These are the call names that mean "this tool's writes land in the
# store", derived from the schema layer rather than from a filename convention: the
# authority is `schema_rows.upsert` (1 def, 50 call sites) and the DDL/transaction verbs
# around it.
STORE_WRITE_FORMS = ("upsert", "executemany", "commit", "reclaim", "drop_relation")

# ⚑ WHAT A STORE WRITER IS TOLD INSTEAD, and it is named rather than left as a hole.
# The store's protection is NOT a snapshot: it is `--dry-run` plus the transaction
# boundary.  Saying "snapshot not applicable" alone would leave a reader assuming
# nothing protects it; naming the substitute is the difference between a scope
# qualifier and a gap.
STORE_SUBSTITUTE = ("snapshot NOT APPLICABLE (writes land in the store, not the "
                    "filesystem) — its protection is --dry-run + the transaction "
                    "boundary, NOT a file copy")

# ⚑ THE FIRST-WRITE IDIOM.  `_snapshot_once` is 30 defs / 30 calls across the corpus
# (`pycodemod --calls _snapshot_once`), each a per-tool helper that snapshots on its
# first call and returns early after.  Its body is reached only once a write is pending,
# which is precisely the placement Ⓐ44 measured as the defect.
FIRST_WRITE_FORMS = ("_snapshot_once",)

UNDECIDABLE = (
    "a guard reached through a helper TWO HOPS deep (this follows one hop: the "
    "enclosing def, called from `__main__`)",
    "a guard behind a RUNTIME-COMPUTED condition (`if mode == argv[1]`) — the "
    "condition is source text here, as it is in `--guarded`",
    "a guard reached only via an import side effect or a decorator-registered path",
    "whether a tool that never writes on ANY path NEEDS one — the contract has no "
    "read-path exemption, so this reports placement, never necessity",
)


def _entry_span(src):
    """(start_line, end_line) of the `if __name__ == "__main__"` block, or None.

    ⚑ TEXTUAL ON PURPOSE, AND BOUNDED.  The block's TEST is the one condition in this
    corpus that is not a mode branch — it is the module's entry point — so it must not
    be counted as a guarding `if`.  Recovering it from the CST would mean a second walk
    for one line number; the spelling is fixed by Python itself.
    """
    lines = src.splitlines()
    start = None
    indent = 0
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        if start is None:
            if s.startswith("if __name__") and "__main__" in s:
                start = i
                indent = len(ln) - len(ln.lstrip())
            continue
        if s and not ln.startswith(" " * (indent + 1)):
            return (start, i - 1)
    return (start, len(lines)) if start else None


def _dispatch_conds(conds, entry_test):
    """The conditions that make a call CONDITIONAL for this reading.

    ⚑ THE `__main__` TEST IS NOT A GUARD.  `--guarded` correctly reports it (it is an
    `if`), and reading it as one would score every entry-guarded tool as conditional —
    the inverted verdict.  Everything else on the stack IS a dispatch branch: a mode
    test, an `if apply:`, an `if rest:`.
    """
    return [c for c in conds if c != entry_test]


def placement(paths=None):
    """{relpath: (verdict, witness)} — WHEN each tool's mutation guard fires.

    Four verdicts, and the split between the first two is the whole point:

      entry        an ENTRY_FORM call reached unconditionally on a bare invocation —
                   either at module scope inside `if __name__`, or in a def called
                   unconditionally from there.  This REFUSES a bare invocation.
      dispatched   an ENTRY_FORM call that sits under a dispatch condition, so some
                   mode reaches the tool's body without it.  Written, not fired.
      first-write  the guard is consulted only at a pending write (`_snapshot_once`,
                   or a call under `if apply:`).  This is the 30-site population
                   `--guarded` reports as `top` and scores identically to `entry`.
      unguarded    no recognised form is called at all.

    ⚑ THE VERDICT IS PER TOOL, NOT PER CALL SITE, and the reason is `intent_census`'s:
    a tool legitimately calls the entry form once and `_snapshot_once` at every write,
    and a per-site census would report the paid-down tool as an offender.  The STRONGEST
    verdict a tool earns is the one reported; the witness names the site that earned it.

    ⚑ ONE BODY, SHARED WITH THE SNAPSHOT AXIS.  `_verdict_for` is the engine; this and
    `disagreement()` differ only in WHICH guard family they ask about.  Two bodies would
    drift, and a disagreement census over two drifting predicates would report its own
    skew as the tools' skew.
    """
    return _verdict_for(list(paths or _pycodemod_core.py_files()),
                        ENTRY_FORMS, FIRST_WRITE_FORMS)


def _called_unconditionally(population, path, fname, span):
    """Is `fname` called from the entry block with nothing on the condition stack?

    ⚑ SCOPED TO THE DEFINING FILE.  A cross-module entry point is a different question
    and this returns False for it rather than guessing — an over-report of `dispatched`
    is the conservative direction (it names work that may not exist; the inverse would
    certify a tool that does not refuse).
    """
    if not span:
        return False
    seen = KwIndex()
    rows = [r for r in scan([path], fname, kwseen=seen) if r[1] == "call"]
    src = open(path, encoding="utf-8", errors="replace").read()
    first = src.splitlines()[span[0] - 1].strip()
    entry_test = first[3:].rstrip(":").strip() if first.startswith("if ") else None
    for p, _k, _n, line in rows:
        if not (span[0] <= line <= span[1]):
            continue
        if not _dispatch_conds(seen.conds.get((p, line), []), entry_test):
            return True
    return False


def _verdict_for(population, forms, first_write_forms=()):
    """{relpath: (verdict, witness)} for ONE guard family — the shared engine.

    ⚑ FACTORED OUT RATHER THAN COPIED so the intent axis and the snapshot axis are
    measured by the SAME predicate.  Two bodies would drift, and a disagreement census
    built on two drifting predicates reports its own skew as the tools' skew.
    """
    out = {}
    rank = {"entry": 3, "dispatched": 2, "first-write": 1}
    for form in tuple(forms) + tuple(first_write_forms):
        seen = KwIndex()
        rows = [r for r in scan(population, form, kwseen=seen) if r[1] == "call"]
        for p, _k, _n, line in rows:
            rel = os.path.relpath(p, ROOT)
            try:
                src = open(p, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            span = _entry_span(src)
            entry_test = None
            if span:
                first = src.splitlines()[span[0] - 1].strip()
                entry_test = (first[3:].rstrip(":").strip()
                              if first.startswith("if ") else None)
            conds = _dispatch_conds(seen.conds.get((p, line), []), entry_test)
            ctx = seen.contexts.get((p, line), "<module>")
            if form in first_write_forms:
                verdict = "first-write"
            elif conds:
                verdict = "dispatched"
            elif ctx != "<module>":
                # ⚑ ONE HOP, AND THE BOUND IS STATED RATHER THAN HIDDEN.  A guard inside
                # a def fires at entry only if that def is itself called unconditionally
                # from the entry block.  Following further would need a call graph this
                # module deliberately does not rebuild (`callgraph` exists; the two-hop
                # case is in UNDECIDABLE).
                verdict = "entry" if _called_unconditionally(
                    population, p, ctx, span) else "dispatched"
            elif span is None:
                # ⚑⚑ NO `__main__` BLOCK MEANS THE SCRIPT BODY *IS* THE ENTRY POINT, and
                # reading its absence as "not at entry" was a FALSE POSITIVE this census
                # produced on its first run: `unseal_defs.py:45` calls `require_at_entry`
                # at module scope with no `__main__` block at all, and its own ⚑ comment
                # records that placement as the Ⓐ44 paydown.  The predicate scored the
                # STRONGEST form as debt — `census-keyed-on-one-spelling` in the shape
                # `intent_census` records, reproduced one layer out.  A module-scope call
                # under no dispatch condition runs on import AND on invocation; that is
                # entry by construction, whether or not the file spells the idiom.
                verdict = "entry"
            else:
                verdict = "entry" if span[0] <= line <= span[1] else "dispatched"
            prev = out.get(rel)
            if prev is None or rank[verdict] > rank[prev[0]]:
                out[rel] = (verdict, f"{form} at :{line}")
    return out


def writes_store(path):
    """(bool, witness) — do this tool's writes land in the STORE rather than in files?

    ⚑ STRUCTURAL, NOT BY FILENAME.  `jea/metalanguage/**` is a directory convention and
    conventions drift; the fact is whether the tool CALLS a store-write verb.  Derived
    from `STORE_WRITE_FORMS`, whose authority is `schema_rows.upsert` and the
    transaction verbs around it.

    ⚑ A TOOL CAN BE BOTH, and this reports the store side as PRESENT rather than as a
    classification — `sppf_decode` writes cores AND upserts rows.  A tool that is both
    needs a snapshot for its files AND is unprotected for its rows, so collapsing it to
    one bucket would hide half the answer.
    """
    try:
        src = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return False, "unreadable"
    seen = KwIndex()
    for form in STORE_WRITE_FORMS:
        if form not in src:
            continue
        rows = [r for r in scan([path], form, kwseen=seen) if r[1] == "call"]
        # ⚑ A FIXTURE CALL IS NOT A WRITE PATH — same discriminator the near-miss
        # census needed, and for the same reason: `schema_selftest` calls `upsert`
        # 24 times against a throwaway tenant.
        live = [r for r in rows
                if "selftest" not in (seen.contexts.get((r[0], r[3]), "") or "").lower()]
        if live:
            return True, f"{form} at :{live[0][3]}"
    return False, ""


def _binds_snapshot_at_entry(population):
    """{relpath: witness} for the BOUND form — the snapshot taken BY the intent call.

    ⚑⚑⚑ THIS EXISTS BECAUSE THE FIX FOR `SPLIT` WAS INVISIBLE TO THE CENSUS THAT FOUND
    IT.  `require_at_entry(label, paths=...)` delegates to `guard` past the intent
    check (see `edit_snapshot.require_at_entry`), so stating `--apply` IS taking the
    snapshot — one act, one placement.  But the delegation happens INSIDE
    `edit_snapshot`, so the calling tool contains NO `guard`/`_snapshot_once` call at
    all, and `_verdict_for` scored the correctly-bound shape `snapshot=absent`.

    ⚑⚑ SO THE CENSUS HAD NO VOCABULARY FOR ITS OWN REMEDY, and the two failures are
    MIRRORS.  Before the fix a split tool read GREEN to `intent_census` (the contract is
    named) while being unprotected; after the fix it read RED here (no snapshot call is
    visible) while being protected.  Both are the same error — SOURCE POSITION reported
    where the question is about EXECUTION — and shipping the paydown without this would
    have converted eight false GREENs into eight false REDs, leaving no instrument that
    could confirm the repair.

    ⚑ THE DISCRIMINATOR IS THE `paths=` KEYWORD, NOT THE CALL NAME.  `require_at_entry`
    WITHOUT `paths` still checks intent and still delegates to `guard`, but hands it an
    empty path tuple — which snapshots TRACKED content (whole-worktree `git stash
    create`) while copying NO untracked file, because `_copy_untracked(paths)` is the
    only mechanism that reaches them.  The untracked half is precisely the population
    most likely to need recovering (measured: 63 untracked pipeline tools, every
    destructive one among them). So `paths=` present is reported as `entry`, and its
    ABSENCE is reported as `entry-nopaths` rather than folded into either verdict.
    """
    out = {}
    seen = KwIndex()
    rows = [r for r in scan(population, "require_at_entry", kwseen=seen)
            if r[1] == "call"]
    for p, _k, _n, line in rows:
        rel = os.path.relpath(p, ROOT)
        kws = seen.get((p, line), set()) or set()
        # ⚑ `edit_snapshot.py` DEFINES the delegation; a call there is the fixture/
        # dispatch, not a tool binding its own snapshot. Excluded so the authority
        # does not appear in a census of its own adopters.
        if rel.endswith("edit_snapshot.py"):
            continue
        witness = f"require_at_entry(paths=) at :{line}"
        if "paths" in kws:
            out[rel] = ("entry", witness)
        elif rel not in out:
            out[rel] = ("entry-nopaths", f"require_at_entry at :{line} (no paths=)")
    return out


def disagreement(paths=None):
    """The DANGEROUS SHAPE: intent stated at entry, snapshot taken at the write.

    ⚑⚑⚑ THIS IS THE CENSUS THE OPERATOR'S PARENTHETICAL ASKS FOR.  A tool in this state
    looks COMPLIANT to `check_snapshot_guard.intent_census` (the contract is named) and
    is UNPROTECTED in practice (a read-only mode, a restoring dry run, or a run that
    finds nothing to change never reaches the snapshot).  Neither existing census can
    see it, because each reads ONE of the two guards and nothing reads the RELATION —
    `the-fact-may-be-an-edge-not-a-property`, in the mutation family.

    ⚑ AND THE STORE AXIS CHANGES THE VERDICT, NOT JUST THE COMMENTARY.  For a
    store-writing tool a snapshot-at-the-write is not a weaker protection than
    snapshot-at-entry — it is NO protection either way, so reporting it as a placement
    defect would send a reader to move a call that cannot help.  Those rows report
    `store` and carry `STORE_SUBSTITUTE`.
    """
    population = list(paths or _pycodemod_core.py_files())
    intent = _verdict_for(population, ENTRY_FORMS)
    snap = _verdict_for(population, (), SNAPSHOT_FORMS)
    # ⚑⚑ THE BOUND FORM IS AN ARGUMENT, NOT A SECOND CALL, so it cannot come from
    # `_verdict_for` (which scans for call NAMES).  `require_at_entry(paths=...)` takes
    # the snapshot by delegating to `guard` inside `edit_snapshot`, leaving no snapshot
    # call in the tool itself — the shape `_binds_snapshot_at_entry` recognises.  It
    # OVERRIDES the scanned verdict rather than merging with it: a tool that binds at
    # entry AND still carries a write-site call is bound (the write-site call is then
    # redundant, not a defect), and reporting it as SPLIT would send a reader to
    # "fix" the one placement that is already correct.
    bound = _binds_snapshot_at_entry(population)
    rows = {}
    for rel in sorted(set(intent) | set(snap) | set(bound)):
        i = intent.get(rel, ("absent", ""))
        s = bound.get(rel) or snap.get(rel, ("absent", ""))
        if s[0] == "entry-nopaths":
            # ⚑ NOT COLLAPSED INTO `entry`.  The intent gate is bound, but the untracked
            # half of the snapshot is not reached — a real and NARROWER gap than SPLIT,
            # and naming it separately is what keeps it from being banked as done.
            s = ("entry-nopaths", s[1])
        store, swit = writes_store(os.path.join(ROOT, rel))
        if store:
            kind = "store"
        elif i[0] == "entry" and s[0] in ("first-write", "dispatched"):
            kind = "SPLIT"
        elif i[0] == "entry" and s[0] == "absent":
            kind = "intent-only"
        elif i[0] == "absent" and s[0] != "absent":
            kind = "snapshot-only"
        elif i[0] == "entry" and s[0] == "entry":
            kind = "bound"
        elif i[0] == "entry" and s[0] == "entry-nopaths":
            kind = "bound-nopaths"
        else:
            kind = "unbound"
        rows[rel] = (kind, i, s, swit)
    return rows


def print_disagreement(paths=None):
    """The disagreement census, with the store rows told what they get INSTEAD."""
    rows = disagreement(paths)
    order = ["SPLIT", "intent-only", "snapshot-only", "unbound", "bound-nopaths",
             "store", "bound"]
    byk = {}
    for rel, v in rows.items():
        byk.setdefault(v[0], []).append((rel, v))
    for k in order:
        for rel, (_k, i, s, swit) in sorted(byk.get(k, [])):
            extra = f"  [{swit}]" if k == "store" and swit else ""
            print(f"{k:<14} {rel}   intent={i[0]} ({i[1] or '—'})  "
                  f"snapshot={s[0]} ({s[1] or '—'}){extra}")
    counts = " / ".join(f"{len(byk.get(k, []))} {k}" for k in order if byk.get(k))
    print(f"disagreement: {len(rows)} tool(s) — {counts}")
    if byk.get("SPLIT"):
        print("   ⚑⚑ SPLIT is the DANGEROUS SHAPE: intent is stated at entry (so")
        print("      `intent_census` scores it compliant) while the snapshot is taken")
        print("      only at a pending write — a read-only mode, a restoring dry run,")
        print("      or a `nothing to change` run is UNPROTECTED.")
        print("      → bind them: take the snapshot AT the intent statement.")
    if byk.get("bound-nopaths"):
        print(f"   ⚑ {len(byk['bound-nopaths'])} tool(s) bind the snapshot to the intent "
              f"statement but pass NO `paths=`.")
        print("      The intent gate and the snapshot are one act (the SPLIT is closed),")
        print("      and TRACKED content is covered — `snapshot()` is whole-worktree.")
        print("      What is NOT covered is the UNTRACKED half: `_copy_untracked(paths)`")
        print("      is the only mechanism that reaches it, and it iterates `paths`.")
        print("      → pass the tool's target paths to `require_at_entry(paths=...)`.")
    if byk.get("store"):
        print(f"   ⚑ {len(byk['store'])} STORE-writing tool(s): {STORE_SUBSTITUTE}")
        print("      Reporting a snapshot placement defect on these would send a reader")
        print("      to move a call that cannot help. A snapshot is a FILESYSTEM act.")
    print("   ⚑ WHAT THIS CANNOT DECIDE:")
    for u in UNDECIDABLE:
        print(f"       · {u}")
    print("       · whether a tool that is BOTH a file and a store writer has its FILE "
          "writes covered — it reports `store`, which is the stronger warning")
    return rows


def print_placement(paths=None):
    """The census, grouped by verdict, with the undecidable set stated at the verdict."""
    rows = placement(paths)
    order = ["unguarded", "first-write", "dispatched", "entry"]
    byv = {}
    for rel, (v, w) in rows.items():
        byv.setdefault(v, []).append((rel, w))
    for v in order:
        for rel, w in sorted(byv.get(v, [])):
            print(f"{v:<12} {rel}  ({w})")
    tot = len(rows)
    counts = " / ".join(f"{len(byv.get(v, []))} {v}" for v in order if byv.get(v))
    print(f"placement: {tot} tool(s) call a recognised mutation-guard form — {counts}")
    print("   ⚑ EXECUTION ORDER, not source position — `--guarded guard` answers the")
    print("     other axis and scores `entry` and `first-write` identically.")
    print("   ⚑ WHAT THIS CANNOT DECIDE:")
    for u in UNDECIDABLE:
        print(f"       · {u}")
    return rows


def _cases():
    """Guards for the mechanism.  Called from `_pycodemod_selftest`."""
    import tempfile
    fails = []

    def case(name, src, want):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "t.py")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(src)
        got = placement([p])
        v = got.get(os.path.relpath(p, ROOT), ("unguarded", ""))[0]
        if v != want:
            fails.append(f"{name}: want {want}, got {v}")

    # ⚑ THE CASE THAT SEPARATES THE TWO — both are `top` to `--guarded`.
    case("entry-at-module-scope",
         'if __name__ == "__main__":\n    require_at_entry("t")\n    go()\n', "entry")
    case("first-write-helper",
         'def _snapshot_once(p):\n    pass\ndef go():\n    _snapshot_once("x")\n', "first-write")
    case("dispatched-under-mode",
         'if __name__ == "__main__":\n    if "--apply" in sys.argv:\n'
         '        require_at_entry("t")\n', "dispatched")
    case("entry-one-hop",
         'def main():\n    require_at_entry("t")\n'
         'if __name__ == "__main__":\n    main()\n', "entry")
    # ⚑ THE FALSE POSITIVE THE FIRST LIVE RUN PRODUCED — `unseal_defs.py` has no
    # `__main__` block, so the script body is the entry point.  Scored `dispatched`
    # (debt) until the `span is None` branch existed.
    case("no-main-block-module-scope",
         'import sys\nrequire_at_entry("t")\npath = sys.argv[1]\n', "entry")
    case("hop-under-condition",
         'def main():\n    require_at_entry("t")\n'
         'if __name__ == "__main__":\n    if x:\n        main()\n', "dispatched")
    return fails


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _f = _cases()
        for _m in _f:
            print(f"FAIL {_m}")
        print(f"placement selftest: {6 - len(_f)}/6 case(s) pass")
        sys.exit(1 if _f else 0)
    _rest = [a for a in sys.argv[1:] if not a.startswith("-")]
    print_placement(_pycodemod_core.py_files(*_rest) if _rest else None)
