#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""catalog_db.py — the SINGLE shared home for the catalog.db path + a read-only connection.

⟡py-lift-catalogdb (⟡gates-query-sppf S0): the `catalog/catalog.db` path literal + a per-script connect
helper were re-rolled in ~9 places with DIVERGENT policy (bare connect vs `mode=ro` vs `row_factory`). This
consolidates them so every gate/tool opens the DB the same way and no gate re-derives from source what the
interned SPPF already materializes:

    from catalog_db import CATALOG_DB, connect
    import query_builders as QB
    con = connect()                       # read-only, Row factory
    for row in QB.run(con, "unit_cod"):   # ⟡qinfra: named query, no SQLAlchemy at runtime
        ...

`run` (the compile+execute helper from query_builders) is re-exported so a gate needs one import. A
`sqlite3.Row` factory is set unconditionally — it supports BOTH `row["col"]` and positional unpacking
(`a, b = row`), so it is a drop-in for the existing bare-connect positional consumers.
"""

import glob
import os
import sys
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import store  # THE store authority: dsn, dialect, connect
import schema as _schema  # THE schema authority: rows/scalar/ph, upsert, DDL


def _core_root():
    """The `.agdai` root — RESOLVED, never spelled.

    ⚑ MY FIRST CUT HARDCODED `agda/_build/2.8.0/agda`, which is a version
    literal that rots silently at the next Agda upgrade: the glob would find
    ZERO cores, the set-difference would be empty, and the guard would report
    COMPLETE on a corpus it could not see.  A completeness check that passes
    because it looked in the wrong directory is the exact failure it exists to
    catch, one layer out.  `sppf_db.substrate_core_root` is the authority the
    Set₁ gate already resolves through (`set1_ratchet_cores.py:163`)."""
    scripts = os.path.join(REPO, "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import sppf_db

    return sppf_db.substrate_core_root(os.path.join(REPO, "agda"))


_BUILD_HINT = (
    "  build it: python3 scripts/gen_catalog.py   "
    '(or the projection alone: python3 scripts/sppf_db.py "")'
)


def completeness(con=None, core_root=None):
    """{"on_disk": n, "ingested": n, "missing": [core_id …]} — is the census TOTAL?

    ⚑ AN UNDECODABLE CORE IS INDISTINGUISHABLE FROM AN ABSENT ONE, and that is
    a storage-layer fact, not a staleness one.  `sppf_db._decode_insert_core`
    writes `core_fp` on the SUCCESS path only (`scripts/sppf_db.py:230`), so a
    core the shim cannot decode contributes no rows AND no ledger entry.  It
    then reads exactly like a core that was never on disk.

    ⚑ MEASURED 2026-08-03: 3131 cores on disk, 2991 in `core_fp`, 140 missing —
    while EVERY naive freshness proxy reported FRESH (no `.agdai` newer than the
    DB, no source newer, schema version current, `meta.failed = 0`).  So the
    mtime ledger is CORRECT and the corpus is INCOMPLETE, and mtime cannot
    express the difference.  A footprint or census computed here would have
    silently omitted 4.5% of the tree, concentrated in `Algebra` (98) and
    `Groups` (19) — the areas under active edit.

    ⚑ AND THE TWO EXISTING MEASUREMENTS DISAGREE: `meta.failed` reads 0 because
    it counts the CATALOG tier's walk failures, a separate decode path from the
    SPPF tier's.  This set-difference is the one to trust — it compares the
    ledger against a live disk glob rather than incrementing a counter — but
    both are reported by `--completeness` rather than one being silently picked.

    ⚑ NOT A TIMESTAMP CHECK, BY CONSTRUCTION.  Comparing the DB's mtime to the
    tree's answers "was this rebuilt recently", which is the question that
    already returns FRESH on an incomplete DB.  The population is DISCOVERED
    from the disk glob every call, so a core added tomorrow is in the denominator
    with no edit here — the same reason `worklist_gate.reads` had to stop
    spying a hardcoded five-name list."""
    own = con is None
    if own:
        con = connect()
    root = core_root or _core_root()
    try:
        # ⚑ THE CORE_ID IS `_content_addr._b64`, THE SHARED PRIMITIVE — never a
        # local `base64.b64encode`.  I wrote the inline form first; it is
        # byte-identical TODAY, and that is exactly how `agda_files()` became
        # four bodies under one name.  A guard keyed by a private re-derivation
        # of someone else's identity function silently stops matching the
        # moment the authority changes.
        sys.path.insert(0, os.path.join(REPO, "scripts"))
        from _content_addr import _b64

        on_disk = {}
        for p in glob.iglob(os.path.join(root, "**", "*.agdai"), recursive=True):
            rel = os.path.relpath(p, root)
            on_disk[_b64(rel)] = rel
        # ⚑ WAS `except sqlite3.Error: ingested = set()` — "no core_fp at all: nothing
        # ingested". That tolerance is SQLITE REASONING, and `schema_rows.schema_version`
        # already records why it cannot be carried over: POSTGRES ABORTS THE WHOLE
        # TRANSACTION on any error, so catching one does not undo it — every later
        # statement fails with `InFailedSqlTransaction` naming neither the read nor the
        # table. Ask the CATALOGUE whether the relation exists, then read it.
        ingested = (
            {r["core_id"] for r in _schema.rows(con, "SELECT core_id FROM core_fp")}
            if "core_fp" in _schema.relations(con)
            else set()
        )
        missing = sorted(on_disk[c] for c in (set(on_disk) - ingested))
        return {"on_disk": len(on_disk), "ingested": len(ingested), "missing": missing}
    finally:
        if own:
            con.close()


def orphan_cores(core_root=None, src_root=None, con=None):
    """Every `.agdai` whose `.agda` is GONE — `[(relstem, decodes, ingested)]`.

    ⚑ TWO INDEPENDENT FACTS PER ROW, BECAUSE ONE FLAG HID THE DANGEROUS CASE.
    My first cut carried only `decodes` and reported **85 undecodable / 0
    decodable**, against a research agent's **35 / 50**.  Neither was wrong —
    they measured different things, and the disagreement was the finding:

      * `decodes`  — can the shim read this core TODAY?  (measured live)
      * `ingested` — is it in `core_fp`, i.e. did the DB already absorb it?

    Measured on `Foundation/Nat`, `Foundation/Sum`, `Algebra/Quotient`:
    **ingested = True, decodes = False.**  They were ingested when their
    dependencies were intact and stopped decoding as the tree moved.  Reporting
    one flag collapsed that into a plain "undecodable" and lost it.

    ⚑ AND `ingested AND source-gone` IS THE WORST CELL IN THE TABLE.  Those
    cores are NOT missing from the DB — their rows are LIVE in `unit_obs`,
    `edges`, `structs`, feeding every reuse query — and they describe modules
    whose sources no longer exist.  `--completeness` cannot see them (it reports
    what is ABSENT from `core_fp`; these are present), and `finalize_db`'s prune
    keys on disk-absence (`sppf_db.py:277`), which they fail too.  A retired
    definition indistinguishable from a live one is exactly the silent-wrong-row
    this session has been chasing at every layer.

    ⚑ A CENSUS, NOT A SWEEP (user, 2026-08-03: *"Not a sweep, a census."*).  I
    was about to add a standalone entry to `split_pipeline.sweep_orphan_agdai`
    — the DELETING verb — with a dry-run in front of it.  That inverts the
    order this repo has paid for repeatedly: a dry-run shows what one
    invocation WOULD do, while a census materializes the POPULATION, which is
    the thing a gate can ratchet, an item can be sized against, and a reader can
    audit without trusting the tool that would act on it.  The sweep stays where
    it is; this is what tells you whether to run it.

    ⚑ AND IT IS THE POPULATION `classify_missing` CANNOT SEE.  That predicate
    starts from the MISSING set, so it reports only source-gone cores ABSENT
    from `core_fp` — measured 35.  The true figure is **85**, and the extra 50
    are the ingested ones: present in the DB, contributing rows, sources gone.

    ⚑ NOT PROOF OF RETIREMENT.  A core here has no source TODAY; whether that
    is a retirement, a rename, or an accident is a separate question this does
    not answer.  Two cores (`Algebra/F2`, `Algebra/F2/Linear`) show a recent
    commit with no `--diff-filter=D` line — the signature of a RENAME, whose
    core is not residue.  Report the population; let the caller adjudicate."""
    root = core_root or _core_root()
    src = src_root or os.path.join(REPO, "agda", "Substrate")
    sys.path.insert(0, os.path.join(REPO, "scripts"))
    from _content_addr import _b64

    # ⚑⚑ THE `os.path.exists(CATALOG_DB)` GATE WAS AN INVERTED CENSUS WAITING TO HAPPEN,
    # AND SQLITE'S REMOVAL IS WHAT MADE IT FIRE (⓺, 2026-08-11). It read
    # `if con is None and os.path.exists(CATALOG_DB): con, own = connect(), True` — a
    # FILESYSTEM test gating a connection that had already been ported to postgres. With
    # the sqlite file deleted the test is False, `con` stays None, `ing` becomes the empty
    # set, and EVERY core reports `ingested=False` — silently inverting the exact cell
    # this function's docstring calls the most consequential one. No error, no empty
    # result: a full table of confident wrong answers.
    #
    # ⚑ A PRECONDITION MUST BE ASKED OF THE THING IT GUARDS. The guard was "does the store
    # exist" spelled as "does this path exist", which stopped being the same question the
    # moment the store stopped being a file. `connect()` resolves the store; if it cannot,
    # that is a connection error and belongs to the caller, not a silent empty set.
    own = False
    if con is None:
        con, own = connect(), True
    ing = {r["core_id"] for r in _schema.rows(con, "SELECT core_id FROM core_fp")}
    if own:
        con.close()
    out = []
    for p in sorted(glob.iglob(os.path.join(root, "**", "*.agdai"), recursive=True)):
        stem = os.path.relpath(p, root)[: -len(".agdai")]
        if os.path.exists(os.path.join(src, stem + ".agda")):
            continue
        # ⚑ DECODABILITY IS MEASURED, NOT INFERRED FROM THE MISSING SET.  Asking
        # the shim directly is what separates the 35 already reported from the
        # 50 that no instrument was looking at.
        try:
            sys.path.insert(0, HERE)
            import jea_agdai

            decodes = jea_agdai.decode_core(p) is not None
        except Exception:
            decodes = None  # unmeasured, never silently False
        out.append((stem, decodes, _b64(stem + ".agdai") in ing))
    return out


def classify_missing(con=None, core_root=None, ledger=None, src_root=None):
    """Each undecodable core, TYPED — `{class: [relpath …]}`, five classes.

    ⚑ 140 UNDECODABLE CORES ARE NOT ONE ITEM (user, 2026-08-03: *"it's not 1
    item or 2, it's 140 virtual items"*).  I asked whether they were the same
    population as the 121 build failures — a one-or-two question — and the
    measurement refuted the framing rather than answering it.  Crossed against
    `.leaf-verify.tsv`: **blocked 74, clean 46, build-failed 15, absent from the
    ledger 5.**  So "the 140 are downstream of the build failures, a rebuild
    unblocks them" is wrong for a third of them, and my rebuild advice would
    have left those forever.

    ⚑ AND THE FIFTH CLASS HAS NO SOURCE AT ALL.  `Algebra/F2.agda` (consumed by
    its own split) and `Algebra/F2/Linear.agda` (retired) are GONE, while their
    `.agdai` remain.  They can never decode and a rebuild will never touch them:
    `make` builds what a source demands, and no source demands these.
    `sppf_db.finalize_db` prunes cores absent from DISK — these are present on
    disk; it is the SOURCE that vanished, and nothing checks that relation.
    An orphan is the one class whose route is a DELETE, so collapsing it into
    "rebuild" is not a rounding error, it is the wrong verb.

    ⚑ THE CLASSES ARE ROUTES, WHICH IS WHY THIS IS NOT A TALLY.  Each row is a
    virtual item carrying what to DO — and `orphan`/`blocked`/`build-failed`
    have three different answers.  `unexplained` is deliberately NOT folded into
    a neighbour: it is the honest name for 46 cores that compiled clean and
    still will not decode, and naming it as a gap is what keeps it from reading
    as covered."""
    st = completeness(con, core_root)
    # ⚑ A PARAMETER, NOT A PATCHED GLOBAL.  My first cases monkey-patched `REPO`
    # to redirect this and it silently did not take (the value is read here, at
    # call time), so BOTH fixtures classified as orphan and the case failed for
    # a reason that was not the code's.  A test that has to reach inside the
    # module to steer it is testing the reach, not the predicate.
    src_root = src_root or os.path.join(REPO, "agda", "Substrate")

    verdict = {}
    led = ledger or os.path.join(REPO, "agda", ".leaf-verify.tsv")
    try:
        with open(led, encoding="utf-8") as fh:
            for ln in fh:
                if ln.startswith("#"):
                    continue
                p = ln.rstrip("\n").split("\t")
                if len(p) < 2:
                    continue
                rel = p[0]
                if rel.startswith("Substrate" + os.sep):
                    rel = rel[len("Substrate") + 1 :]
                if rel.endswith(".agda"):
                    rel = rel[:-5]
                verdict[rel] = p[1]
    except OSError:
        verdict = {}  # no census yet: everything lands in `uncensused`

    out = {}
    for rel in st["missing"]:
        stem = rel[:-6] if rel.endswith(".agdai") else rel
        # ⚑ SOURCE-ABSENT IS CHECKED FIRST, because it OVERRIDES the census: an
        # orphan's last census row describes a module that no longer exists, so
        # reading `clean` off it would certify a source that is gone.
        if not os.path.exists(os.path.join(src_root, stem + ".agda")):
            out.setdefault("orphan", []).append(stem)
            continue
        v = verdict.get(stem)
        if v is None:
            out.setdefault("uncensused", []).append(stem)
        elif v in ("blocked", "build-failed", "dependency"):
            out.setdefault(v, []).append(stem)
        else:
            out.setdefault("unexplained", []).append(stem)
    return {k: sorted(v) for k, v in out.items()}


# ⚑ THE ROUTE IS PART OF THE ROW, not prose beside it.  A class whose remedy
# lives in a comment is a class the next reader re-derives; `PARTS` rows are
# `(label, n, route)` precisely so the worklist can print what to run.
MISSING_ROUTE = {
    "orphan": "rm the .agdai — the source is GONE; no rebuild can produce it",
    "build-failed": "fix the module: split_pipeline.py --diagnose <mod>",
    "blocked": "fix its blocker first: split_pipeline.py --diagnose --blockers",
    "dependency": "fix the cited dependency, then re-verify",
    "uncensused": "no census row — run the build census before classifying",
    "unexplained": "COMPILED CLEAN YET UNDECODABLE — no mechanism known; "
    "diagnose the CORE, not the module",
}


def assert_complete(con=None, core_root=None, quiet=False):
    """Refuse an INCOMPLETE census. Returns the completeness dict, or exits 1.

    ⚑ THE GUARD EXISTED AND WAS SCOPED TO ONE CALLER.
    `scripts/set1_ratchet_cores.py:75-82` has done exactly this set-difference
    since it was written, under the rule *an incomplete census is not a low
    count*.  Every OTHER consumer reached the DB through `connect()`, which
    checked only `os.path.exists` — so nine tools inherited none of it.  Lifting
    it here is not a new policy; it is the existing policy reaching the layer
    where consumers actually arrive.

    ⚑ IT IS OPT-IN, DELIBERATELY.  Wiring it into `connect()` itself would make
    every read pay a full-corpus glob, and would refuse tools whose question is
    genuinely per-core (an ingest, a targeted projection).  A caller asking a
    question ABOUT THE POPULATION calls this; a caller asking about one row does
    not.  What must never happen is a population question inheriting silence."""
    st = completeness(con, core_root)
    if st["missing"]:
        n, tot = len(st["missing"]), st["on_disk"]
        sys.stderr.write(f"catalog.db: {n} of {tot} cores UNDECODABLE — census INCOMPLETE.\n")
        for rel in st["missing"][:3]:
            sys.stderr.write(f"  {rel}\n")
        if n > 3:
            sys.stderr.write(f"  … and {n - 3} more (--completeness lists all)\n")
        sys.stderr.write(
            "  An incomplete census is not a low count. A core that fails to\n"
            "  decode writes no core_fp row, so it reads as absent rather than\n"
            "  as broken. Rebuild (`make -C agda -j` then gen_catalog.py); do\n"
            "  not certify a figure computed over the remainder.\n"
        )
        sys.exit(1)
    if not quiet:
        print(f"catalog.db: complete — {st['ingested']} of {st['on_disk']} cores.")
    return st


def connect(mode="ro", *, require=True):
    """Open the ACTIVE store. Delegates to the store authority.

    mode='ro'  (default) → read-only where the backend can express one
    mode='rw'            → read-write (the projection/builders that write)
    require=True         → exit with the build hint if a sqlite store is absent

    ⚑ THIS FUNCTION HAD ZERO EXTERNAL CALLERS (measured 2026-08-06, `pycodemod --calls`),
    while ~56 `sqlite3.connect` sites across the tree opened their own connections. A
    chokepoint nobody routes through is not a chokepoint — it is a fifth spelling. So it
    now DELEGATES rather than duplicating: the body was a byte-for-byte twin of
    `catalog_query._con` plus a mode flag, and keeping two of those was how the backend
    came to be spelled in eight places.

    Kept as a name because this module's own callers use it; it is a re-export, not an
    authority.
    """
    return store.connect(mode=mode, require=require)


# Re-export the compile+execute helper so a gate imports one module. Best-effort: query_builders is a
# sibling in jea/metalanguage; add HERE to the path so the import resolves regardless of the caller's cwd.
if HERE not in sys.path:
    sys.path.insert(0, HERE)
try:
    from query_builders import run  # noqa: F401
except Exception:  # pragma: no cover — callers can import query_builders directly if this fails
    run = None


def _selftest():
    """⚑ THE CASES DRIVE `completeness` OVER A TEMP ROOT, never a re-implemented
    predicate.  A case that recomputes the set-difference itself would pass
    while the function stayed broken — the defect this repo has now recorded in
    `check_snapshot_guard`, the 6c `expectedFailure`, and `check_rederive_ratchet`."""
    import sqlite3 as _s
    import tempfile

    cases = []

    def check(label, got, want):
        cases.append((label, got == want, got, want))

    sys.path.insert(0, os.path.join(REPO, "scripts"))
    from _content_addr import _b64

    root = tempfile.mkdtemp()
    for rel in ("A/One.agdai", "A/Two.agdai", "B/Three.agdai"):
        os.makedirs(os.path.join(root, os.path.dirname(rel)), exist_ok=True)
        open(os.path.join(root, rel), "w").close()

    # ⚑⚑ THE FIXTURE MOVED FROM `:memory:` SQLITE TO THE SANDBOX TENANT (⓺, 2026-08-11),
    # AND IT HAD TO. The reason these cases wanted a private database is unchanged — they
    # test `completeness` against a `core_fp` whose contents they CONTROL, and pointing
    # them at the live store would test the corpus instead. What changed is that
    # `completeness` now asks `schema.relations()`, which reads `information_schema`; a
    # sqlite connection answers "no such table" and the whole suite went SILENT.
    #
    # ⚑ `store.sandbox_connect` IS THE `:memory:` REPLACEMENT, AND IT ALREADY EXISTED FOR
    # THIS. Its docstring: *"a SECOND database whose whole purpose is being mutated by
    # measurement"*, and `sandbox_reset`'s: *"a probe whose verdicts depend on its own
    # history is not a probe."* The old fixture got that property free (a fresh `:memory:`
    # database is empty by construction); `reset=True` is what buys it back.
    #
    # ⚑ AND THE RETIRED `ph(2, "sqlite")` PIN IS WHY THE SUITE CAUGHT THIS AT ALL. That
    # argument existed to work around `ph()` dispatching on the AMBIENT backend, so
    # removing the parameter turned this line into a `TypeError` — loud, at the one site
    # that had encoded the defect as a workaround. Had `ph()` merely IGNORED the argument,
    # this fixture would have kept running and failed later, in `relations()`, with an
    # error naming neither.
    #
    # ⚑ THE BARE CASE RUNS FIRST NOW, AND THE ORDER IS LOAD-BEARING. It needs a store with
    # NO `core_fp` at all; under `:memory:` that was a second connection, but two
    # `sandbox_connect(reset=True)` calls would each wipe the other's tables. One
    # connection, emptied once, exercised bare-then-populated.
    con = _schema.sandbox_fixture("catalog_db")

    # ⚑ NO core_fp TABLE AT ALL ⇒ nothing ingested, every core missing —
    # never a crash, and never a silent pass.
    # ⚑ THE TABLE IS DROPPED EXPLICITLY RATHER THAN LEFT UNCREATED. `sandbox_fixture`
    # leaves the tenant in the DECLARED shape (see its note — a shared tenant must not be
    # emptied for the next suite), so "no core_fp" is now a state this case has to make
    # rather than inherit. Saying it out loud is better anyway: the fixture and the
    # assertion are the same sentence.
    _schema.execute(con, "DROP TABLE IF EXISTS core_fp CASCADE")
    check("a DB with no core_fp reports all missing", len(completeness(con, root)["missing"]), 3)

    # ⚑ REBUILT FROM THE DECLARATION, NOT HAND-SPELLED. The retired fixture wrote
    # `CREATE TABLE core_fp (core_id TEXT PRIMARY KEY, mtime INT)` — two columns, while
    # the model declares three (`producer` scopes the prune). A fixture carrying its own
    # copy of a table shape is the drift `upsert` reads the arity off the declaration to
    # prevent, reproduced inside the guard.
    _schema.apply(con, only="event")
    _schema.upsert(con, "core_fp", [(_b64(r), 0, "agdai") for r in ("A/One.agdai", "A/Two.agdai")])

    st = completeness(con, root)
    check("counts the DISK population", st["on_disk"], 3)
    check("counts the INGESTED population", st["ingested"], 2)
    # ⚑ THE LOAD-BEARING CASE: an undecodable core writes no core_fp row, so it
    # is INDISTINGUISHABLE from absent unless the disk is the denominator.
    check("names the core with no core_fp row", st["missing"], ["B/Three.agdai"])

    # a complete DB reports empty — the branch that must not be unreachable
    _schema.upsert(con, "core_fp", [(_b64("B/Three.agdai"), 0, "agdai")])
    check("complete ⇒ no missing", completeness(con, root)["missing"], [])

    # ⚑ AN EMPTY ROOT MUST NOT READ AS COMPLETE.  My first `_core_root` spelled
    # the Agda version literally; when that path rots the glob finds nothing,
    # the set-difference is empty, and the guard certifies a corpus it never
    # looked at.  `on_disk == 0` is the discriminator.
    empty = tempfile.mkdtemp()
    st0 = completeness(con, empty)
    check("an empty root reports 0 on disk (not 'complete')", st0["on_disk"], 0)

    # ── classify_missing ────────────────────────────────────────────────
    # ⚑ THE ORDER OF THE PREDICATES IS THE FINDING, so a case pins it.  Reading
    # the census verdict FIRST types an orphan by a row describing a module that
    # no longer exists — which is how I measured `unexplained` at 46 when it is
    # 11, and `orphan` at 2 when it is 35.  Source-absence OVERRIDES the census.
    croot = tempfile.mkdtemp()
    sroot = os.path.join(croot, "src", "Substrate")
    os.makedirs(os.path.join(sroot, "A"), exist_ok=True)
    for rel in ("A/Live.agdai", "A/Gone.agdai"):
        os.makedirs(os.path.join(croot, os.path.dirname(rel)), exist_ok=True)
        open(os.path.join(croot, rel), "w").close()
    open(os.path.join(sroot, "A", "Live.agda"), "w").close()  # Gone.agda: absent

    led = os.path.join(croot, "led.tsv")
    with open(led, "w") as fh:
        fh.write("#stamp\t0\n")
        fh.write("Substrate/A/Live.agda\tclean\n")
        fh.write("Substrate/A/Gone.agda\tclean\n")  # a row for a deleted module

    # ⚑ THE SECOND `:memory:` FIXTURE, SAME MOVE, SAME REASON — an EMPTY `core_fp` (the
    # table exists, no rows), which is a different fact from the table being absent and is
    # exactly what makes both cores "missing". `con` is already populated by the cases
    # above, so this needs its own empty table rather than reusing it.
    _schema.execute(con, "DELETE FROM core_fp")
    cl = classify_missing(con, croot, ledger=led, src_root=sroot)
    check(
        "a source-absent core is an ORPHAN, not its stale census row", cl.get("orphan"), ["A/Gone"]
    )
    check("a clean-but-undecodable core stays UNEXPLAINED", cl.get("unexplained"), ["A/Live"])
    # ⚑ EVERY CLASS CARRIES A ROUTE — a row the worklist cannot act on is a tally.
    check("every emitted class has a route", sorted(set(cl) - set(MISSING_ROUTE)), [])

    # ── orphan_cores ────────────────────────────────────────────────────
    # ⚑ THE DECODABLE ORPHAN IS THE CASE THAT MATTERS.  `classify_missing`
    # cannot see it by construction (it starts from the missing set), and it is
    # the worse half: it contributes rows indistinguishable from live ones.
    # ⚑ THE FIXTURE MUST SET UP THE CELL IT ASSERTS.  My first cut asserted
    # `A/Gone` was INGESTED against a core_fp that only ever held Live/Two — a
    # case demanding a state it never created, which fails while saying nothing
    # about the code.  Insert it here, explicitly, so the assertion is about
    # the predicate.
    # ⚑ `INSERT OR REPLACE` WAS SQLITE-ONLY AND `upsert(on_conflict="replace")` ALREADY
    # OWNS THE PORTABLE FORM — postgres spells it `ON CONFLICT (pk) DO UPDATE`, and
    # `upsert` reads both the column list and the conflict target off the declaration
    # rather than a hand-typed `(?,?)`. Used here rather than a hand-written `ON CONFLICT`
    # for the reason its own docstring gives: one capability had 21 spellings, and a
    # fixture typing its own would be the 22nd.
    _schema.upsert(con, "core_fp", [(_b64("A/Gone.agdai"), 0, "agdai")], on_conflict="replace")
    orph = orphan_cores(croot, sroot, con=con)
    check(
        "censuses the orphan regardless of decodability",
        sorted(s for s, _d, _i in orph),
        ["A/Gone"],
    )
    check("a core WITH a source is not an orphan", [s for s, _d, _i in orph if s == "A/Live"], [])
    # ⚑ THE CELL THAT RESOLVED THE 85/0-vs-35/50 DISAGREEMENT: source-gone AND
    # present in core_fp.  Its rows are live in the DB; nothing prunes them,
    # because every existing prune keys on the core being absent from DISK.
    check(
        "an orphan already in core_fp is flagged INGESTED",
        [(s, i) for s, _d, i in orph],
        [("A/Gone", True)],
    )

    con.close()
    ok = sum(1 for _n, g, _a, _b in cases if g)
    for n, g, got, want in cases:
        if not g:
            print("  FAIL %s: got %r want %r" % (n, got, want))
    print("catalog_db selftest: %d/%d" % (ok, len(cases)))
    return ok == len(cases)


# selftest-tenant: sandbox
# ⚑ ⟡tenant-pragma — `run_selftests._tenant` reads this and appends the flag. `store.tenant`
# exits 2 on an unstated tenant since ⟡tenant-mandatory (2026-08-24); SANDBOX because a suite
# that reaches the LIVE store can corrupt the corpus it exists to check.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if _selftest() else 1)
    if "--orphans" in sys.argv:
        rows = orphan_cores()
        # ⚑ THE TWO FLAGS ARE REPORTED SEPARATELY, because collapsing them is
        # what made two correct measurements (85/0 and 35/50) look like a
        # contradiction.  `ingested` is the one with live consequences.
        ingested = [s for s, _d, i in rows if i]
        absent = [s for s, _d, i in rows if not i]
        unk = [s for s, d, _i in rows if d is None]
        print(f"orphan cores (.agdai with no .agda): {len(rows)}")
        print(
            f"  {len(ingested):>3} INGESTED  — ⚠ rows are LIVE in the DB "
            f"(unit_obs/edges/structs) for modules whose source is GONE;"
        )
        print(
            f"           --completeness cannot see these (they are PRESENT "
            f"in core_fp), and finalize_db's"
        )
        print(f"           prune keys on disk-absence, which they also fail.")
        print(
            f"  {len(absent):>3} absent    — not in core_fp; these are the "
            f"ones --completeness reports"
        )
        if unk:
            print(f"  {len(unk):>3} unmeasured — the decode probe itself failed")
        print(
            "  route: scratch/split_pipeline.py sweep_orphan_agdai() removes "
            "the FILE (stage 8 of --apply today);"
        )
        print(
            "         the ingested rows also need a DB prune — no tool does "
            "that today (finalize_db keys on disk)."
        )
        print(
            "  ⚑ a source-gone core is not PROOF of retirement — a RENAME "
            "looks identical here. Adjudicate before removing."
        )
        if "-v" in sys.argv or "--verbose" in sys.argv:
            for s, d, i in rows:
                print(
                    f"      {'INGESTED' if i else 'absent':<9}"
                    f"{'decodes' if d else 'undec' if d is False else '?':<8} {s}"
                )
        else:
            print("  (-v lists every core)")
        sys.exit(1 if rows else 0)

    if "--completeness" in sys.argv:
        st = completeness()
        print(
            f"catalog.db: {st['ingested']} of {st['on_disk']} cores ingested; "
            f"{len(st['missing'])} MISSING"
        )
        # ⚑ REPORT THE POPULATION, NOT THE TALLY — and report BOTH disagreeing
        # measurements rather than picking.  `meta.failed` counts the CATALOG
        # tier's walk failures, a different decode path from the SPPF tier's,
        # and on 2026-08-03 it read 0 against 140 missing.  The set-difference
        # is the one to trust (a live disk glob vs the ledger); the counter is
        # shown so the disagreement stays visible instead of being resolved
        # silently in favour of whichever is quoted.
        # ⚑ SAME `sqlite3.Error` TOLERANCE AS ABOVE, SAME REPLACEMENT: ask the catalogue
        # first rather than catching a postgres error that has already poisoned the
        # transaction. The `(absent)` branch still exists — it now means the ROW is
        # missing, which is a different fact from the RELATION being missing, and the two
        # were previously collapsed into one `except`.
        _v = (
            _schema.scalar(connect(), "SELECT value FROM meta WHERE key='failed'")
            if "meta" in _schema.relations(connect())
            else None
        )
        print(
            f"  meta.failed (catalog-tier walk) = "
            f"{_v if _v is not None else '(absent)'}"
            + (
                "   ⚠ DISAGREES with the set-difference above"
                if st["missing"] and _v is not None and str(_v) == "0"
                else ""
            )
        )
        # ⚑ THE CLASSES ARE THE REPORT, because 140 rows under one heading read
        # as one problem with one remedy — and they are five problems whose
        # verbs differ (rm / fix / wait / census / unknown).
        cl = classify_missing()
        for k in sorted(cl, key=lambda k: -len(cl[k])):
            print(f"  {k:<13} {len(cl[k]):>3}   {MISSING_ROUTE[k]}")
            if "-v" in sys.argv or "--verbose" in sys.argv:
                for rel in cl[k]:
                    print(f"      {rel}")
        if not any("-v" in a or "--verbose" in a for a in sys.argv):
            print("  (-v lists every core under its class)")
        sys.exit(1 if st["missing"] else 0)
    # Smoke test: open the DB and run one builder, proving the path/connect/run wiring.
    import query_builders as QB

    con = connect()
    n = next(iter(QB.run(con, "core_count")), None)
    # ⚑ NAMES THE TENANT, NOT A PATH. `CATALOG_DB` printed a filesystem location that
    # stopped existing; `store.dsn()` is the authority's own answer to "what did I open".
    print(f"catalog_db: OK — {store.dsn()['dbname']}")
    print(f"  q_core_count → {tuple(n) if n is not None else None}")
    con.close()
