#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""sppf_query.py — ⟡jea-pysim-query-db: jea_pysim's readouts, AS SQL over the resident SPPF.

The catalog_query analogue for the SPPF (scripts/sppf_db.py). jea_pysim computed support / fan-in /
shared-subtrees / extract-candidates / clusters as PYTHON graph-walks over an in-memory interner;
here each is a SELECT/JOIN/GROUP BY over the db that CONTAINS the SPPF. A new SPPF question is a
SELECT, not a new pass. (If a question needs Python, the SPPF model isn't expressive enough — the
same test the catalog uses.)

  support <unit>      support size + the head-op histogram of a unit's subterms   (was _support walk)
  fanin [k]           the most-shared nodes (fan-in = hash-cons corroboration)     (was I.fanin scan)
  extract [minunits]  subtrees shared by ≥ minunits distinct units (the apex)      (was the extract pass)
  clusters <unit> [t] units whose support overlaps <unit> by ≥ t fraction          (was the cluster pass)
  reuse [minunits]    consolidation candidates + the defCopy verdict (CONSOLIDATED/DUP/MIXED)
  sql "<query>"       arbitrary READ-ONLY SQL over the SPPF db

Every mode needs a tenant: pass --sandbox or --live (⟡tenant-mandatory; store.tenant refuses
an unstated one rather than picking, because a read against the wrong tenant returns plausible
rows nobody can distinguish).

⚑⚑ THIS TOOL OPENED `catalog/catalog.db` BY PATH UNTIL 2026-08-24, AND HAD BEEN BROKEN THE
WHOLE TIME SINCE THE POSTGRES PORT. Two independent faults, both measured (⟡sqlite-reroute):

  1. `query_builders` compiles postgres `%(name)s` placeholders, so EVERY builder-backed mode
     died on `sqlite3.OperationalError: near "%": syntax error`. `fanin 5` was the witness.
  2. `catalog.db` is a 334MB snapshot with an mtime FIVE DAYS BEFORE the port, holding exactly
     the ten event-tier tables and a ~40% subset of them (`terms` 12,252 vs 48,214 live;
     `core_fp` 1,961 vs 2,994). Nothing in it is unmigrated — postgres has all of it and more.

So the file was neither a live store nor a fallback: it was a stale partial snapshot that no
working code path could read. Rerouting through `store.tenant` REPAIRS ALREADY-BROKEN MODES; it
migrates no data, because there is none here to migrate (`sql-F26`/`sql-F27`).
"""

import sys, os

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "jea", "metalanguage"
    ),
)
import query_builders as QB  # ⟡query-rawtocore: single-source Core builders (run = execute)
import store as _store  # ⟡tenant-mandatory: the tenant is NAMED, never defaulted


def _con():
    # ⚑ ARGV-DRIVEN, NOT `require=`. gate-F24's test is whether the tenant is the OPERATOR'S to
    # pick, and here it is: both tenants are real stores holding the same declared relations, and
    # asking the SPPF a question of one or the other is exactly the choice this tool exists to
    # serve. `require=` is for a caller whose tenant is fixed by what it IS (a fixture, or a mode
    # meaningless against one tenant) — a pragma or a pin here would misdescribe.
    #
    # ⚑ THE SANDBOX ARM RETURNS HONEST EMPTIES, AND THAT IS NOT A REASON TO PIN LIVE. Measured
    # 2026-08-24: sandbox holds 0 of 28 declared relations, live holds 26. An empty answer from a
    # named tenant is a fact; a silently-live answer to an unstated one is the defect (`sql-F2`).
    return _store.tenant(mode="ro", label="sppf_query")


# ⚑ `.fetchone()` WAS A SQLITE-CURSOR IDIOM AND `QB.run` NEVER RETURNED A CURSOR HERE.
# query_builders.run NORMALISES its result to a LIST of name-keyed rows (`_rows_of`), precisely
# because a psycopg dict_row cursor unpacks to COLUMN NAMES — the silent-shape defect its own
# comment records. Three call sites in this file called `.fetchone()` on that list. `_one` is the
# one spelling of "first row or None"; a scalar read then indexes it by NAME, not position.
def _one(rows):
    return rows[0] if rows else None


def _uid(c, name):
    r = _one(QB.run(c, "uid", name=name, likep="%." + name))
    return r["unit_id"] if r else None


def cmd_support(c, a):
    uid = _uid(c, a[0])
    if uid is None:
        sys.exit(f"no unit matching {a[0]!r}")
    n = _one(QB.run(c, "support_count", uid=uid))["k"]
    print(f"support: {n} interned subterm nodes")
    for r in QB.run(c, "support_hist", uid=uid):
        print(f"   {r['k']:4d}  {r['head'][:60]}")


def cmd_fanin(c, a):
    k = int(a[0]) if a else 15
    for r in QB.run(c, "fanin", lim=k):
        print(f"  fan-in {r['fanin']:5d}  node {str(r['node_id'])[:10]:>10}  {r['head'][:55]}")


def cmd_extract(c, a):
    # the parametric-helper apex: a subtree shared across ≥ minunits DISTINCT units — a GROUP BY.
    m = int(a[0]) if a else 3
    for r in QB.run(c, "extract", m=m):
        print(f"  in {r['units']:4d} units  node {str(r['node_id'])[:10]:>10}  {r['head'][:50]}")


def cmd_clusters(c, a):
    uid = _uid(c, a[0])
    if uid is None:
        sys.exit(f"no unit matching {a[0]!r}")
    thr = float(a[1]) if len(a) > 1 else 0.6
    sz = _one(QB.run(c, "support_count", uid=uid))["k"]
    # coherent fraction = |shared| / |support(u)| — a JOIN + GROUP BY, not a pairwise Python pass.
    for r in QB.run(c, "clusters_overlap", sz=sz, uid=uid, thr=thr):
        print(f"   {r['shared'] * 1.0 / sz:.2f}  ({r['shared']}/{sz})  {r['name'].split('.')[-1]}")


def has_copy(c):
    """is the defCopy provenance column present on `_unit` in THIS tenant?

    ⚑ STILL A PROBE, NOT A CONSTANT, THOUGH `copy` IS NOW DECLARED. Under postgres the column
    is part of the schema declaration, so the honest answer is almost always True — but a tenant
    that has never been established holds NO `_unit` at all (measured: sandbox is 0 of 28
    relations), and a hardcoded True would send `reuse_rows_copy` at a relation that is absent.
    Asking the engine keeps 'the column is missing' and 'the relation is missing' distinguishable.

    ⚑ `PRAGMA table_info` WAS THE SQLITE FORM AND IS GONE. `schema.columns_of` is the existing
    engine-catalogue reader (`schema.py --columns` is its CLI) — reused rather than re-derived.
    """
    import schema as _schema

    return "copy" in _schema.columns_of(c, "_unit")


def reuse_rows(c, min_units=3, limit=None):
    """Consolidation candidates AS ONE query (no re-intern): composite subtrees shared by ≥min_units
    DISTINCT units, each with the defCopy verdict — all instances are module-instantiation copies ⇒
    CONSOLIDATED; none are ⇒ genuine DUP (independent originals sharing structure = the target); else
    MIXED. copies is NULL and verdict '?' if the db predates the copy column."""
    # single-source: two static named variants (⟡qinfra ⟡q-reuse-rows-copy/-nocopy); lim=-1 ≡ no limit.
    out = []
    name = "reuse_rows_copy" if has_copy(c) else "reuse_rows_nocopy"
    for r in QB.run(c, name, min_units=min_units, lim=(-1 if limit is None else int(limit))):
        cc = r["copies"]
        verdict = (
            "?"
            if cc is None
            else "CONSOLIDATED"
            if cc == r["units"]
            else "DUP"
            if cc == 0
            else "MIXED"
        )
        out.append(
            {
                "node_id": r["node_id"],
                "head": r["head"] or "?",
                "units": r["units"],
                "copies": cc,
                "verdict": verdict,
            }
        )
    return out


def cmd_reuse(c, a):
    m = int(a[0]) if a else 3
    if not has_copy(c):
        print(
            "  ⚠ this tenant has no defCopy provenance on `_unit` (the column, or the relation "
            'itself, is absent) — establish/ingest it (python3 scripts/sppf_db.py "") for the '
            "consolidated-vs-dup verdict; showing counts only.\n"
        )
    for r in reuse_rows(c, m, limit=25):
        mark = {"CONSOLIDATED": "✓", "DUP": "✗", "MIXED": "·"}.get(r["verdict"], "?")
        cp = "" if r["copies"] is None else f" ({r['copies']}/{r['units']} copies)"
        print(f"  {mark} {r['verdict']:12s} {r['units']:4d} units{cp}  {r['head'][:44]}")


def cmd_sql(c, a):
    # ⚑ ROWS ARE DICTS NOW, NOT TUPLES. `store.connect` sets psycopg's `dict_row` factory, so
    # iterating a row yields its COLUMN NAMES under the old `str(x) for x in row`. Print values.
    for row in c.execute(a[0]):
        print("  " + " | ".join(str(v) for v in row.values()))


CMDS = {
    "support": cmd_support,
    "fanin": cmd_fanin,
    "extract": cmd_extract,
    "clusters": cmd_clusters,
    "reuse": cmd_reuse,
    "sql": cmd_sql,
}

if __name__ == "__main__":
    # ⚑ THE TENANT FLAGS ARE NOT OPERANDS. `store.tenant` reads them off `sys.argv` itself, so
    # they may appear anywhere; strip them here so `fanin --live 5` binds 5 as the limit rather
    # than trying `--live` as a count. Filtering by the resolver's OWN roster (`store.TENANT_FLAGS`)
    # keeps the two spellings from drifting apart — the census-keyed-on-one-spelling shape.
    _rest = [a for a in sys.argv[1:] if a not in _store.TENANT_FLAGS]
    if not _rest or _rest[0] not in CMDS:
        sys.exit(f"usage: sppf_query.py <{'|'.join(CMDS)}> [args] (--sandbox|--live)")
    c = _con()
    CMDS[_rest[0]](c, _rest[1:])
