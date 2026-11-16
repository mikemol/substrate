#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# catalog_query.py — query the substrate's reuse catalog (Ⓓ.catalog-db).
#
# The relational store `catalog/catalog.db` (built by scripts/gen_catalog.py from the ONE shim
# decode pass — see scripts/reuse_catalog.py) holds the SAME facts the two markdown catalogs
# render, so a NEW discovery question is a SELECT rather than a new script. Tables: structs(qname,
# name, kind, module, fp), members(struct_qname, name, ord), refs(struct_qname, ref_qname),
# edges(src, dst). Views: in_degree, out_degree, multiply_homed, shape_parallel.
#
# This is the reuse-search discipline's INTERACTIVE endpoint — before building a new data/record,
# ask the DB whether it (or a same-shape sibling) already exists:
#
#   scripts/catalog_query.py                      # summary: counts + top reuse-primitives
#   scripts/catalog_query.py schema [substr]      # every table/view, its columns and row count —
#                                                 # ⚑ ASK THIS, do not trust the prose list below:
#                                                 # a hand-maintained roster of tables is a derived
#                                                 # view that goes stale the first time a projection
#                                                 # adds one.
#   scripts/catalog_query.py find V4              # structures whose NAME contains a substring
#   scripts/catalog_query.py refiners DivStr      # what is built on X (STRUCT edges INTO X) — by name or qname
#   scripts/catalog_query.py builds-on Wedge      # what X is built on (STRUCT edges OUT of X)
#   scripts/catalog_query.py imported-by Substrate.Foundation.Nat  # MODULES depending on a module
#   scripts/catalog_query.py imports Substrate.Algebra.Wedge       # a module's semantic dependencies
#   scripts/catalog_query.py homes Canonical      # a name's several homes (the ambiguity picker)
#   scripts/catalog_query.py parallels [N]        # same-shape / different-name candidates (top N by breadth)
#   scripts/catalog_query.py primitives [N]       # most-reused structures (in-degree ranking)
#   scripts/catalog_query.py sql "SELECT ..."     # arbitrary READ-ONLY SQL
#
# The DB is a derived, gitignored cache. If it is missing/stale, rebuild it:
#   scripts/gen_catalog.py           (~2-3min; regenerates both markdown catalogs AND the .db)
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "jea", "metalanguage"))
import store  # THE store authority: dsn, dialect, connect
import schema as _schema  # THE schema authority: relations/columns, upsert, DDL

# ⚑⚑ `DB` IS DELETED (⓺, 2026-08-11) AND IT HAD ZERO READERS — the thing it was kept for
# never happened. Its note read: *"was an independent derivation of the catalog path — one
# of EIGHT, and they did not agree; re-exported so the name still resolves for readers of
# this module."* `pycodemod --calls DB` on this file: one reference, the binding itself.
# A compatibility alias with no consumer is not compatibility, it is a live reference to a
# retired constant — which is exactly how this module would have kept a sqlite path
# reachable after the backend that read it was gone.


def _con():
    """A read-only connection to the ACTIVE store.

    ⚑ THE BACKEND IS NO LONGER SPELLED HERE. This opened a `file:…?mode=ro` sqlite URI
    directly, so it could not follow `SUBSTRATE_STORE` and would keep reading the OLD
    store after a migration — the silent-wrong-answer shape, since every query below
    would still return plausible rows.
    """
    return store.connect(mode="ro")


def _rows(con, q, args=()):
    """STREAM the result set.  A cursor IS the generator; do not materialize.

    ⚑ THIS WAS `.fetchall()`, AND THAT IS RAM-AS-STORAGE IN THE READER WHOSE
    WHOLE PURPOSE IS TO AVOID IT (user, 2026-08-05: *"This should be going into
    the sqlite3 db.  Then sqlite3 can stream to us.  We should not be using RAM
    as storage."*).  Every consumer below walks the result exactly once, so the
    list existed only to be iterated and dropped -- while a `SELECT` over the
    3.3GB catalog can return an arbitrarily large set.  `sqlite3.Cursor` is
    already an iterator over rows the engine produces on demand; returning it
    is strictly less machinery than wrapping it.

    ⚑ The one thing this costs: a caller may no longer `len()` the result or
    walk it twice.  That is the SAME constraint the figure-row fold just
    adopted, and it is the point -- a count falls out of the walk."""
    return con.execute(q, args)


def _one(con, q, args=()):
    """The single scalar row a COUNT-shaped query returns."""
    for r in con.execute(q, args):
        return r
    return None


def cmd_schema(con, args):
    """Every table and view in the store, with its columns and row count.

    ⚑ BUILT BECAUSE "WHAT IS ALREADY IN HERE" HAD NO COMMAND (2026-08-05).  The
    header comment lists tables and views in PROSE -- a derived view of the
    schema, maintained by hand, and therefore stale the moment a projection
    adds a table.  Routing a census INTO this store is exactly when that
    question gets asked, and the answer was a `.schema` at a sqlite3 shell,
    i.e. reaching past the tool that owns the artifact."""
    # ⚑ `sqlite_master` AND `PRAGMA table_info` ARE BOTH SQLITE-ONLY — postgres has
    # neither, so this listing was a hard porting stop rather than a stylistic one.
    # `schema.relations` and `schema.columns_of` answer the same two questions from
    # whichever catalogue the active backend has.
    want = args[0] if args else None
    rel = _schema.relations(con)
    n = 0
    for name in sorted(rel, key=lambda x: (rel[x], x)):
        if want and want.lower() not in name.lower():
            continue
        n += 1
        cols = ", ".join(_schema.columns_of(con, name))
        cnt = _one(con, "SELECT COUNT(*) c FROM %s" % name)
        print("  %-5s %-24s %8d  (%s)" % (rel[name], name, cnt["c"], cols))
    # ⚑ `n of m`, ALWAYS -- an empty listing must not read as an empty store.
    print("%d of %d relation(s)" % (n, len(rel)))


def _short(qn):
    return qn.rsplit(".", 1)[-1]


def cmd_summary(con, _args):
    # ⚑ `_one`, NOT `_rows(...)[0]` -- a cursor has no positional access, which
    # is the whole reason it streams.  A COUNT query returns one row; asking for
    # it by name says so, where `[0]` said "materialize and index".
    ns = _one(con, "SELECT COUNT(*) c FROM structs")["c"]
    nm = _one(con, "SELECT COUNT(DISTINCT module) c FROM structs")["c"]
    ne = _one(con, "SELECT COUNT(*) c FROM edges")["c"]
    namb = _one(con, "SELECT COUNT(*) c FROM multiply_homed")["c"]
    npar = _one(con, "SELECT COUNT(*) c FROM shape_parallel")["c"]
    print(
        f"catalog.db: {ns} structures across {nm} modules; {ne} refinement edges; "
        f"{namb} multiply-homed names; {npar} shape-parallel groups."
    )
    print("\nMost-reused primitives (in-degree):")
    for r in _rows(con, "SELECT qname, deg FROM in_degree ORDER BY deg DESC, qname LIMIT 12"):
        print(f"  {r['deg']:4}  {_short(r['qname']):24} {r['qname'].rsplit('.', 1)[0]}")


def cmd_find(con, args):
    if not args:
        sys.exit("usage: catalog_query.py find <name-substring>")
    for r in _rows(
        con,
        "SELECT name, kind, module FROM structs WHERE name LIKE ? ORDER BY name, module",
        (f"%{args[0]}%",),
    ):
        print(f"  {r['kind']:6} {r['name']:24} {r['module']}")


def _resolve(con, ident):
    """Accept a full qname or a bare short name; return matching qnames.

    ⚑⚑ THE SIX `?` PLACEHOLDERS IN THIS FILE WERE THE SAME DEFECT AS `demand_imports`, AND
    THE SUITE COULD NOT SEE THEM (⓺, 2026-08-11). `catalog_query --selftest` reads 7/7
    while every one of these commands would raise `ProgrammingError: the query has 0
    placeholders but 1 parameters were passed` against psycopg — because the cases cover
    the parsing and rendering, and no case drives a PARAMETERISED read. A green suite over
    a module whose every parameterised query is broken is the sharpest possible statement
    of what a suite measures.

    ⚑ FOUND BY ASKING FOR THE LITERAL, NOT BY REVIEW. `pycodemod --literal '= ?'` over the
    tree returns them as `arg`-role string literals; the ⚑ commentary that explains the
    paramstyle is excluded by construction, because a comment is not a literal.
    """
    if "." in ident:
        return [ident]
    return [
        r["qname"]
        for r in _rows(
            con, "SELECT qname FROM structs WHERE name = %s ORDER BY qname" % _schema.ph(), (ident,)
        )
    ]


# ⚑ THE COUNT COMES OUT OF THE WALK, NOT A SECOND PASS.  These five commands
# each read `rs = _rows(...)`, printed `len(rs)`, then iterated `rs` -- so the
# result set had to be a LIST purely to be measured before it was rendered.
# Under a streaming cursor the count is just the loop variable, and the header
# moves below the rows (which is also more honest: the total is known when the
# walk finishes, not before it starts).
def _edges(con, q, arg, head, col):
    # ⚑ THE HEADER MOVED BELOW THE ROWS, AND BUFFERING TO KEEP IT ON TOP WOULD
    # HAVE RE-INTRODUCED THE CONTAINER.  My first cut collected the lines into a
    # list so the count could print first -- which is the materialization this
    # change exists to remove, restored for cosmetics.  A total is knowable only
    # when the walk ends; printing it there is what the stream can honestly say.
    n = 0
    for r in _rows(con, q, (arg,)):
        n += 1
        print("    %s" % r[col])
    print(head % (arg, n))


def cmd_refiners(con, args):
    if not args:
        sys.exit("usage: catalog_query.py refiners <name|qname>")
    for q in _resolve(con, args[0]):
        _edges(
            con,
            "SELECT src FROM edges WHERE dst = %s ORDER BY src" % _schema.ph(),
            q,
            "%s  ← refined by %d:",
            "src",
        )


def cmd_builds_on(con, args):
    if not args:
        sys.exit("usage: catalog_query.py builds-on <name|qname>")
    for q in _resolve(con, args[0]):
        _edges(
            con,
            "SELECT dst FROM edges WHERE src = %s ORDER BY dst" % _schema.ph(),
            q,
            "%s  → builds on %d:",
            "dst",
        )


def cmd_imports(con, args):
    if not args:
        sys.exit("usage: catalog_query.py imports <module>")
    _edges(
        con,
        "SELECT dst FROM module_edges WHERE src = %s ORDER BY dst" % _schema.ph(),
        args[0],
        "%s  → semantically depends on %d:",
        "dst",
    )


def cmd_imported_by(con, args):
    if not args:
        sys.exit("usage: catalog_query.py imported-by <module>")
    _edges(
        con,
        "SELECT src FROM module_edges WHERE dst = %s ORDER BY src" % _schema.ph(),
        args[0],
        "%s  ← depended on by %d:",
        "src",
    )


def cmd_homes(con, args):
    if not args:
        sys.exit("usage: catalog_query.py homes <name>")
    n = 0
    for r in _rows(
        con,
        "SELECT qname, kind, module, fp FROM structs WHERE name = %s "
        "ORDER BY module" % _schema.ph(),
        (args[0],),
    ):
        n += 1
        print(f"  {r['kind']:6} {r['module']:52} fp={r['fp']}")
    # ⚑ `if not rs` became a COUNT AFTER THE WALK.  Emptiness is a property the
    # stream reports when it ends, not one you can test before reading it.
    if not n:
        print(f"(no structure named {args[0]})")


def cmd_parallels(con, args):
    n = int(args[0]) if args else 25
    for r in _rows(
        con, "SELECT fp, names, structs FROM shape_parallel ORDER BY names DESC, fp LIMIT ?", (n,)
    ):
        kind, heads = r["fp"].split("|", 1)
        print(f"  [{r['names']}] {kind} {{{heads}}}")
        for s in r["structs"].split(","):
            print(f"        {s}")


def cmd_primitives(con, args):
    n = int(args[0]) if args else 25
    for r in _rows(con, "SELECT qname, deg FROM in_degree ORDER BY deg DESC, qname LIMIT ?", (n,)):
        print(f"  {r['deg']:4}  {_short(r['qname']):24} {r['qname'].rsplit('.', 1)[0]}")


def cmd_sql(con, args):
    if not args:
        sys.exit('usage: catalog_query.py sql "SELECT ..."')
    q = args[0].strip()
    if not q.lower().startswith(("select", "with", "explain")):
        sys.exit("only read-only SELECT/WITH/EXPLAIN queries are allowed")
    # ⚑ THIS READ `rows[0].keys()` AND THEN RE-WALKED `rows` — which under a
    # streaming cursor prints the header and SILENTLY DROPS THE FIRST ROW,
    # because the header read already consumed it.  A materialized list hid
    # that: indexing and iterating a list are independent, indexing and
    # iterating a stream are not.  The header now comes from the first row as
    # it passes, so nothing is consumed twice and nothing is lost.
    n = 0
    for r in _rows(con, q):
        if not n:
            print("\t".join(r.keys()))
        n += 1
        print("\t".join("" if r[k] is None else str(r[k]) for k in r.keys()))
    # ⚑ `n of m` has no denominator for arbitrary SQL — the population IS the
    # query.  Reporting the count still separates "no matching rows" from "the
    # query never ran", which an empty print does not.
    print("%d row(s)" % n)


def _selftest():
    """⚑ THIS MODULE HAD NO SUITE, so `run_selftests` could not see it at all —
    a reader of the 3.3GB store, invisible rather than failing.  The cases drive
    the STREAMING contract, because that is what just changed and what a future
    edit would silently undo by re-introducing a `.fetchall()`.

    Uses an in-memory scratch db, NOT `catalog.db`: a case that depends on the
    live store's contents fails for the wrong reason when the store moves, and
    the contract under test is about cursors, not about this repo's data."""
    # ⚑ THE SHARED HELPER, NOT A 56TH COPY (2026-08-05).  `--rivals check`
    # measured **55 defs, 55 reimplementing, 0 delegating** — one name, fifty
    # bodies, no authority, in the machinery that verifies everything else.  The
    # CALL SITES are untouched: they were already uniform, and rewriting the
    # uniform part is not where the duplication lives.
    sys.path.insert(0, os.path.join(ROOT, "scratch"))
    import rungs

    check = rungs.Cases(key="scripts/catalog_query.py")

    # ⚑ THE FIXTURE STAYS SQLITE ON PURPOSE, and it is not an oversight that it does
    # not follow `SUBSTRATE_STORE`. These cases test the ROW READER (`_rows` streams;
    # `cmd_sql` does not eat row one) against a table whose contents they control. An
    # in-memory database is the only way to make that controlled; pointing them at the
    # live store would test the store instead, and would fail on an empty one.
    # The import is LOCAL because the module no longer talks sqlite anywhere else —
    # a top-level import would read as "this tool is a sqlite tool", which is the fact
    # the store authority just retired.
    import sqlite3

    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.execute("CREATE TABLE t (a, b)")
    con.executemany("INSERT INTO t VALUES (?,?)", [(1, "x"), (2, "y"), (3, "z")])

    # ⚑ THE ROW READER STREAMS.  A list would satisfy every other case here;
    # only asking whether it is its own iterator tells a cursor from a list.
    rs = _rows(con, "SELECT a FROM t ORDER BY a")
    check("_rows returns a stream, not a container", iter(rs) is rs, True)

    # ⚑ THE DEFECT `cmd_sql` HAD: read the header off row one, then walk —
    # which under a cursor CONSUMES that row.  Pins the fold that fixed it.
    seen, hdr = [], None
    for r in _rows(con, "SELECT a, b FROM t ORDER BY a"):
        if hdr is None:
            hdr = list(r.keys())
        seen.append(r["a"])
    check("header off row one does not eat it", seen, [1, 2, 3])
    check("header names the columns", hdr, ["a", "b"])

    # ⚑ AND THE SHAPE THAT WOULD HAVE BROKEN: consuming a row for the header
    # BEFORE the loop drops it.  Demonstrates the bug is real, not hypothetical.
    cur = _rows(con, "SELECT a FROM t ORDER BY a")
    _ = next(iter(cur)).keys()
    check("a pre-consumed header LOSES row one", [r["a"] for r in cur], [2, 3])

    # `_one` takes the single row a COUNT returns, without materializing.
    check("_one reads a scalar row", _one(con, "SELECT COUNT(*) c FROM t")["c"], 3)
    check("_one on an empty set is None", _one(con, "SELECT a FROM t WHERE a > 99"), None)

    # ⚑ A COUNT AFTER THE WALK IS THE ONLY HONEST ONE — `cmd_homes` tested
    # `if not rs` BEFORE iterating, which a stream cannot answer.
    n = 0
    for _r in _rows(con, "SELECT a FROM t WHERE a > 99"):
        n += 1
    check("emptiness is known when the walk ends", n, 0)

    con.close()

    # ── ⟡catalog-query-green-selftest — THE CASE THIS SUITE DID NOT HAVE ──────────────
    # ⚑⚑ EVERY CASE ABOVE PASSES AGAINST AN IN-MEMORY FIXTURE WHILE 9 OF 11 COMMANDS
    # RAISE AGAINST THE LIVE STORE. That is not a flaw in the fixture — the streaming
    # contract genuinely needs controlled data, and pointing those cases at the store
    # would test the store. The flaw is that NOTHING here asked the one question the
    # fixture structurally cannot: **do the relations these commands name exist in the
    # store this tool connects to?**
    #
    # MEASURED 2026-08-20: `_con()` correctly follows `SUBSTRATE_STORE` to postgres (its
    # docstring records that half of the migration, and why). The queries did not follow:
    # `summary` runs `SELECT COUNT(*) FROM structs` and raises `UndefinedTable`; `find`
    # raises too.
    #
    # ⚑⚑⚑ AND THE NEXT SENTENCE HERE WAS WRONG — IT READ *"`structs`/`edges`/`module_edges`/
    # `in_degree` live only in the SQLite `catalog.db`"*, and they do not live there either
    # (`sql-F26`, `sql-F27`, 2026-08-24). `catalog.db` was opened and enumerated: it holds ten
    # tables (`core_fp`, `edge`, `event`, `obs`, `path_seg`, `path_text`, `schema_version`,
    # `terms`, `unit_member`, `unit_obs`), ALL of which postgres already has, and NONE of the
    # four this tool names. It is a stale pre-migration snapshot of the event tier, not the
    # home of these relations.
    #
    # ⚑⚑ SO THE VERDICT IS NOT "MIGRATED AWAY", IT IS **NEVER WRITTEN ANYWHERE**. The catalog
    # tier has no home at all: `reuse_catalog._db_tier_unported` raises `SystemExit` naming the
    # eight tables, and the one writer (`DbBuilder.write`) sits behind that refusal. The repair
    # is to DECLARE the tier in `schema_decl.py`, after which the already-compiled builders
    # (`q_indegree_top`, `q_edges_dst_distinct`, the `view.*` family) light up unchanged —
    # `query_defs --touching structs` already reports 7 readers and 0 writers.
    #
    # ⚑ THIS CASE IS THEREFORE CORRECT AND MUST STAY RED. 4-of-4 absent in BOTH tenants is
    # exactly what an unmigrated tier looks like; a green here would mean the check stopped
    # asking. `run_selftests` records it as 7/8 WITH a record, which is the honest state.
    #
    # ⚑ So `run_selftests` read this module GREEN while its first command was broken —
    # `census-green-is-a-fact-about-the-census`, and the module's own docstring already
    # records this exact shape happening once before: *"A green suite over a module whose
    # every parameterised query is broken is the sharpest possible statement of what a
    # suite measures."* Same defect, one migration later.
    #
    # This case is a REACHABILITY check, not a data check: it asserts the relations are
    # PRESENT, never what they contain — so it stays honest on an empty store and fails
    # exactly when a reader has outlived its data.
    _named = {"structs", "edges", "module_edges", "in_degree"}
    try:
        _c = _con()
    except Exception as e:  # no store configured → declared skip
        check(f"⚑ store unreachable ({type(e).__name__}) — reachability UNMEASURED", True, True)
    else:
        try:
            _have = set(_schema.relations(_c))
        finally:
            try:
                _c.close()
            except Exception:
                pass
        check(
            "the relations this tool's commands name exist in the store it connects to",
            sorted(_named - _have),
            [],
        )

    # ⚑ `N/M` IS THE COUNT OF THE WALK, and a zero denominator REFUSES — both
    # were reimplemented per suite, and `spool` shipped 8 unrun assertions
    # behind a `0/0` that read as green.
    return check.report() == 0


CMDS = {
    "summary": cmd_summary,
    "schema": cmd_schema,
    "find": cmd_find,
    "refiners": cmd_refiners,
    "builds-on": cmd_builds_on,
    "imports": cmd_imports,
    "imported-by": cmd_imported_by,
    "homes": cmd_homes,
    "parallels": cmd_parallels,
    "primitives": cmd_primitives,
    "sql": cmd_sql,
}

# selftest-tenant: sandbox
# ⚑ ⟡tenant-pragma — `run_selftests._tenant` reads this and appends the flag. `store.tenant`
# exits 2 on an unstated tenant since ⟡tenant-mandatory (2026-08-24); SANDBOX, which agrees
# with the dispatch note below: the suite must not need the live store to exist.
# ⚑ THIS SUITE IS SEPARATELY RED — 7/8 WITH a record, a real pre-existing defect surfaced by
# the tenant census and NOT caused by it (⟡catalog-query-defect). Declaring the tenant does
# not repair it, and a green here would be the thing to distrust.
if __name__ == "__main__":
    argv = sys.argv[1:]
    # ⚑ DISPATCHED BEFORE `_con()` — the suite must not need the 3.3GB store to
    # exist.  A selftest that exits on "catalog.db not found" is a suite that
    # only runs on a machine that has already built the artifact.
    if argv and argv[0] == "--selftest":
        sys.exit(0 if _selftest() else 1)
    cmd = argv[0] if argv else "summary"
    if cmd not in CMDS:
        sys.exit(f"unknown command {cmd!r}; one of: {', '.join(CMDS)}")
    con = _con()
    try:
        CMDS[cmd](con, argv[1:])
    finally:
        con.close()
