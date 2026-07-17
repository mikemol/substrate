#!/usr/bin/env python3
"""catalog_db.py — the SINGLE shared home for the catalog.db path + a read-only connection.

⟡py-lift-catalogdb (⟡gates-query-sppf S0): the `catalog/catalog.db` path literal + a per-script connect
helper were re-rolled in ~9 places with DIVERGENT policy (bare connect vs `mode=ro` vs `row_factory`). This
consolidates them so every gate/tool opens the DB the same way and no gate re-derives from source what the
interned SPPF already materializes:

    from catalog_db import CATALOG_DB, connect
    import query_builders as QB
    con = connect()                       # read-only, Row factory
    for row in QB.run(con, QB.q_unit_cod()):
        ...

`run` (the compile+execute helper from query_builders) is re-exported so a gate needs one import. A
`sqlite3.Row` factory is set unconditionally — it supports BOTH `row["col"]` and positional unpacking
(`a, b = row`), so it is a drop-in for the existing bare-connect positional consumers.
"""
import os
import sys
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
CATALOG_DB = os.path.join(REPO, "catalog", "catalog.db")

_BUILD_HINT = ("  build it: python3 scripts/gen_catalog.py   "
               "(or the projection alone: python3 scripts/sppf_db.py \"\")")


def connect(mode="ro", *, require=True):
    """Open catalog.db.

    mode='ro'  (default) → read-only URI connection (gates/tools that only query).
    mode='rw'            → read-write connection (the projection/builders that write).
    require=True         → exit with the build hint if the DB is absent (matches catalog_query._con).

    A `sqlite3.Row` factory is set either way.
    """
    if require and not os.path.exists(CATALOG_DB):
        sys.exit(f"catalog.db not found at {CATALOG_DB}\n{_BUILD_HINT}")
    if mode == "ro":
        con = sqlite3.connect(f"file:{CATALOG_DB}?mode=ro", uri=True)
    else:
        con = sqlite3.connect(CATALOG_DB)
    con.row_factory = sqlite3.Row
    return con


# Re-export the compile+execute helper so a gate imports one module. Best-effort: query_builders is a
# sibling in jea/metalanguage; add HERE to the path so the import resolves regardless of the caller's cwd.
if HERE not in sys.path:
    sys.path.insert(0, HERE)
try:
    from query_builders import run  # noqa: F401
except Exception:  # pragma: no cover — callers can import query_builders directly if this fails
    run = None


if __name__ == "__main__":
    # Smoke test: open the DB and run one builder, proving the path/connect/run wiring.
    import query_builders as QB
    con = connect()
    n = next(iter(QB.run(con, QB.q_core_count())), None)
    print(f"catalog_db: OK — {CATALOG_DB}")
    print(f"  q_core_count → {tuple(n) if n is not None else None}")
    con.close()
