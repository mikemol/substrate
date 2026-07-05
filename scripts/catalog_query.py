#!/usr/bin/env python3
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
import os, sys, sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB   = os.path.join(ROOT, "catalog", "catalog.db")


def _con():
    if not os.path.exists(DB):
        sys.exit(f"catalog.db not found at {DB}\n  build it: scripts/gen_catalog.py (~2-3min)")
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)   # read-only
    con.row_factory = sqlite3.Row
    return con


def _rows(con, q, args=()):
    return con.execute(q, args).fetchall()


def _short(qn):
    return qn.rsplit(".", 1)[-1]


def cmd_summary(con, _args):
    ns   = _rows(con, "SELECT COUNT(*) c FROM structs")[0]["c"]
    nm   = _rows(con, "SELECT COUNT(DISTINCT module) c FROM structs")[0]["c"]
    ne   = _rows(con, "SELECT COUNT(*) c FROM edges")[0]["c"]
    namb = _rows(con, "SELECT COUNT(*) c FROM multiply_homed")[0]["c"]
    npar = _rows(con, "SELECT COUNT(*) c FROM shape_parallel")[0]["c"]
    print(f"catalog.db: {ns} structures across {nm} modules; {ne} refinement edges; "
          f"{namb} multiply-homed names; {npar} shape-parallel groups.")
    print("\nMost-reused primitives (in-degree):")
    for r in _rows(con, "SELECT qname, deg FROM in_degree ORDER BY deg DESC, qname LIMIT 12"):
        print(f"  {r['deg']:4}  {_short(r['qname']):24} {r['qname'].rsplit('.',1)[0]}")


def cmd_find(con, args):
    if not args:
        sys.exit("usage: catalog_query.py find <name-substring>")
    for r in _rows(con, "SELECT name, kind, module FROM structs WHERE name LIKE ? "
                        "ORDER BY name, module", (f"%{args[0]}%",)):
        print(f"  {r['kind']:6} {r['name']:24} {r['module']}")


def _resolve(con, ident):
    """Accept a full qname or a bare short name; return matching qnames."""
    if "." in ident:
        return [ident]
    return [r["qname"] for r in
            _rows(con, "SELECT qname FROM structs WHERE name = ? ORDER BY qname", (ident,))]


def cmd_refiners(con, args):
    if not args:
        sys.exit("usage: catalog_query.py refiners <name|qname>")
    for q in _resolve(con, args[0]):
        rs = _rows(con, "SELECT src FROM edges WHERE dst = ? ORDER BY src", (q,))
        print(f"{q}  ← refined by {len(rs)}:")
        for r in rs:
            print(f"    {r['src']}")


def cmd_builds_on(con, args):
    if not args:
        sys.exit("usage: catalog_query.py builds-on <name|qname>")
    for q in _resolve(con, args[0]):
        rs = _rows(con, "SELECT dst FROM edges WHERE src = ? ORDER BY dst", (q,))
        print(f"{q}  → builds on {len(rs)}:")
        for r in rs:
            print(f"    {r['dst']}")


def cmd_imports(con, args):
    if not args:
        sys.exit("usage: catalog_query.py imports <module>")
    m = args[0]
    rs = _rows(con, "SELECT dst FROM module_edges WHERE src = ? ORDER BY dst", (m,))
    print(f"{m}  → semantically depends on {len(rs)}:")
    for r in rs:
        print(f"    {r['dst']}")


def cmd_imported_by(con, args):
    if not args:
        sys.exit("usage: catalog_query.py imported-by <module>")
    m = args[0]
    rs = _rows(con, "SELECT src FROM module_edges WHERE dst = ? ORDER BY src", (m,))
    print(f"{m}  ← depended on by {len(rs)}:")
    for r in rs:
        print(f"    {r['src']}")


def cmd_homes(con, args):
    if not args:
        sys.exit("usage: catalog_query.py homes <name>")
    rs = _rows(con, "SELECT qname, kind, module, fp FROM structs WHERE name = ? ORDER BY module",
               (args[0],))
    if not rs:
        print(f"(no structure named {args[0]})")
    for r in rs:
        print(f"  {r['kind']:6} {r['module']:52} fp={r['fp']}")


def cmd_parallels(con, args):
    n = int(args[0]) if args else 25
    rs = _rows(con, "SELECT fp, names, structs FROM shape_parallel ORDER BY names DESC, fp LIMIT ?",
               (n,))
    for r in rs:
        kind, heads = r["fp"].split("|", 1)
        print(f"  [{r['names']}] {kind} {{{heads}}}")
        for s in r["structs"].split(","):
            print(f"        {s}")


def cmd_primitives(con, args):
    n = int(args[0]) if args else 25
    for r in _rows(con, "SELECT qname, deg FROM in_degree ORDER BY deg DESC, qname LIMIT ?", (n,)):
        print(f"  {r['deg']:4}  {_short(r['qname']):24} {r['qname'].rsplit('.',1)[0]}")


def cmd_sql(con, args):
    if not args:
        sys.exit('usage: catalog_query.py sql "SELECT ..."')
    q = args[0].strip()
    if not q.lower().startswith(("select", "with", "explain")):
        sys.exit("only read-only SELECT/WITH/EXPLAIN queries are allowed")
    rows = _rows(con, q)
    if rows:
        print("\t".join(rows[0].keys()))
        for r in rows:
            print("\t".join("" if r[k] is None else str(r[k]) for k in r.keys()))


CMDS = {"summary": cmd_summary, "find": cmd_find, "refiners": cmd_refiners,
        "builds-on": cmd_builds_on, "imports": cmd_imports, "imported-by": cmd_imported_by,
        "homes": cmd_homes, "parallels": cmd_parallels,
        "primitives": cmd_primitives, "sql": cmd_sql}

if __name__ == "__main__":
    argv = sys.argv[1:]
    cmd  = argv[0] if argv else "summary"
    if cmd not in CMDS:
        sys.exit(f"unknown command {cmd!r}; one of: {', '.join(CMDS)}")
    con = _con()
    try:
        CMDS[cmd](con, argv[1:])
    finally:
        con.close()
