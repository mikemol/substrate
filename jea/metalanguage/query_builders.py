#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""query_builders.py — ⟡qinfra: the cached RUNTIME. Imports NO SQLAlchemy: executes precompiled SQL from the
generated `query_sql.py` by NAME. The compiler + the builder definitions live in the sibling `query_defs.py`;
regenerate the cache with `python3 query_defs.py --compile` (drift-gated by `--check`).

    import query_builders as QB
    QB.run(con, "unit_cod")                 # named: fast path — no SQLAlchemy import
    QB.run(con, "fanin", lim=20)            # named + params (merged over the builder's baked literal defaults)

Why: `import query_defs` costs ~0.4s (SQLAlchemy's SQL-compilation layer). The hot paths — sppf_db
`--ingest-core`, the pre-commit gates — only READ, so they `import query_builders` and pay ~nothing. The
runtime `run` merges the caller's params over the builder's compiled defaults (baked string/int literals like
COALESCE's `''`/`0`), replaying exactly what query_defs.run would have compiled — byte-equivalent results.

Back-compat: `run(con, <Core stmt>, **params)` (a non-str first arg) lazy-imports query_defs and compiles —
the dynamic path (a query whose TEXT genuinely varies), which pays SQLAlchemy only there.
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)


# ⚑ THE CACHE IS PER-BACKEND, AND THIS LINE WAS HARDCODED TO SQLITE'S. I added
# `query_sql_postgres.py` when the dialect became selectable and never wired the RUNTIME
# to pick it — so under `SUBSTRATE_STORE=postgres` every named query executed SQLITE SQL
# (`:named` params, sqlite quoting) against psycopg.
#
# ⚑ AND IT FAILED SILENTLY, WHICH IS THE WORST PART. The ingest exited 0 and reported
# "1 packings, 0 units, 0 shared subtrees" from 185 cores: the event tier wrote 18,334
# rows correctly, then `project_sppf` read them back through these builders, got nothing,
# and projected nothing. No exception, no warning — a successful-looking run that
# produced an empty projection. Measured: 172 cores / 6,387 events / 419 unit_obs in the
# store, 0 units in the projection.
#
# ⚑ THE FALLBACK IS DELIBERATE AND NARROW: postgres falls back to the sqlite cache only
# if its own is missing, and says so on stderr. Falling back SILENTLY is what this bug
# was; failing outright would break a checkout that has not run `--compile` yet.
# ⚑ AND IT RECURRED, BECAUSE THE DEFAULT MOVED AND THIS SECOND READER DID NOT (2026-08-07).
# The line below read `_os.environ.get("SUBSTRATE_STORE", "sqlite")` — a COPY of the
# authority's default rather than a call to it. When `store.backend()` flipped its default to
# postgres (the live store now holds 23 of 23 relations against sqlite's 10), this module kept
# answering "sqlite", so the connection spoke postgres while the query cache served sqlite SQL.
# MEASURED: `sppf_db --ingest-core` → `psycopg.errors.SyntaxError: syntax error at or near ":"`
# on `WHERE core_fp.core_id = :core_id`.
#
# ⚑ THE COMMENT DIRECTLY ABOVE ALREADY RECORDS THIS EXACT CLASS BEING FIXED ONCE. That fix
# made the cache per-backend; it left the SELECTOR as a duplicated literal, so the defect had
# somewhere to come back to. A shared NAME is not a shared authority — and neither is a shared
# DEFAULT. `pycodemod --forwards backend SUBSTRATE_STORE`: 31 sites route through
# `store.backend()`, this was the one outlier.
#
# ⚑ THE "STAY IMPORT-CHEAP" REASON FOR THE OUTLIER DOES NOT HOLD, and I checked rather than
# assumed. This module avoids `query_defs` because that costs ~0.4s of SQLAlchemy — but
# `store` imports only `os` and `sys` at module level (SQLAlchemy is lazy, inside functions),
# so routing through the authority costs nothing. The outlier bought no speed.
def _cache_backend():
    """Which per-backend SQL cache this process must load — THE authority's answer.

    ⚑ A FUNCTION, NOT A LINE INSIDE `_load_sql`, SO A CASE CAN DRIVE IT. The defect was
    unreachable from any test: the resolution ran once at import, so nothing could ask "does
    this agree with the store?" without re-importing the module. Lifting it is what makes the
    agreement assertable at all.
    """
    import store as _store  # os+sys only at import time; SQLAlchemy is lazy inside

    return _store.backend()  # never a second copy of its default


def _load_sql():
    """The ONE compiled cache. No fallback — see below.

    ⚑⚑ THE FALLBACK IS DELETED, AND ITS OWN NOTE IS WHY (⓺, 2026-08-11). It read:
    *"postgres falls back to the sqlite cache only if its own is missing, and says so on
    stderr. Failing SILENTLY is what this bug was; failing outright would break a
    checkout that has not run `--compile` yet."* Both halves of that reasoning have
    expired. There is no sqlite cache to fall back TO — `query_sql.py` is removed — and
    the thing it was protecting (a checkout mid-migration) is precisely the state that
    must now fail loudly, because the only SQL it could serve is a paramstyle psycopg
    refuses.

    ⚑ AND THE `except Exception: return {}` TAIL WENT WITH IT, WHICH IS THE SHARPER
    HALF. An empty cache is not an absent one: every `run(con, name)` then raises
    `KeyError: no compiled query` — a message naming the QUERY, four frames from the
    real cause, which is that the file was never generated. Letting the ImportError
    stand names the file.
    """
    from query_sql_postgres import SQL as _S  # {name: (sql, defaults)} — --compile

    return _S


SQL = _load_sql()


def _rows_of(cur):
    """Materialise a cursor's rows as name-keyed tuples, on either driver.

    ⚑ NOT A GENERATOR, DELIBERATELY. Callers here do `{(c, l): e for c, l, e in
    QB.run(...)}`, `list(...)`, `.fetchone()` and sometimes two passes — a lazy wrapper
    would break the ones that re-read, and this runtime's job is compatibility, not
    streaming. `schema.rows` is the streaming contract for new code.
    """
    import schema as _schema

    desc = getattr(cur, "description", None)
    names = tuple(d[0] for d in desc) if desc else ()
    out = []
    for r in cur:
        if isinstance(r, dict):
            out.append(_schema.Row(tuple(r.keys()), list(r.values())))
        else:
            out.append(_schema.Row(names, list(r)))
    return out


def sql(name, /, **params):
    """`(sql_text, params)` for a compiled builder — WITHOUT executing it.

    ⚑ FOR THE CALLER THAT MUST WRAP A BUILDER IN DDL. `pack_core_sql` materialises the height map
    once per core as `CREATE TEMP TABLE … AS <builder>`; `run` cannot serve that, because the
    statement is not the builder — the builder is its TAIL. Without this the only routes were
    reaching into `SQL[name]` from another module (a second reader of the cache's shape) or
    re-spelling the query by hand (a fourth parser of the thing `query_defs` exists to
    single-source). Both are shapes this tree has paid for.

    ⚑ THE PARAM MERGE IS `run`'s, NOT A COPY — same `dict(defaults)` then `update`, so a caller
    cannot get a different binding here than it would get by executing. Two spellings of one
    merge is how a compiled default and a runtime default drift apart silently.
    """
    try:
        text, defaults = SQL[name]
    except KeyError:
        raise KeyError(
            f"query_builders: no compiled query {name!r}; the builder set changed — "
            f"regenerate via `python3 jea/metalanguage/query_defs.py --compile`"
        ) from None
    p = dict(defaults)
    p.update(params)
    return text, p


def run(con, name, /, **params):
    """Execute a compiled read-query by NAME on the existing connection (no engine churn, column order
    preserved for Row/positional reads). A non-str `name` is a Core stmt → lazy-compile via query_defs.

    `con`/`name` are POSITIONAL-ONLY (the `/`) so a builder bindparam literally named `name` — q_uid,
    table_exists, object_type — routes to **params instead of colliding with this positional.

    ⚑ `con.execute(...)` IS SQLITE-ONLY: psycopg puts `execute` on a CURSOR, not the
    connection. Every named query in the ingest path runs through here, so this one line
    decided whether the projection could read anything at all."""
    if isinstance(name, str):
        try:
            sql, defaults = SQL[name]
        except KeyError:
            raise KeyError(
                f"query_builders: no compiled query {name!r}; the builder set changed — regenerate "
                f"query_sql.py via `python3 jea/metalanguage/query_defs.py --compile`"
            ) from None
        p = dict(defaults)
        p.update(params)
        cur = con.cursor() if not hasattr(con, "execute") else con
        res = cur.execute(sql, p)
        # ⚑ A psycopg CURSOR WITH `dict_row` YIELDS DICTS, AND ITERATING A DICT YIELDS ITS
        # KEYS. Every consumer here unpacks positionally — `{(c, l): e for c, l, e in
        # QB.run(con, "obs_all")}` — so under postgres each row unpacked to the COLUMN
        # NAMES: the `obs` dict came out with exactly ONE entry, keyed
        # `('core_id', 'local_id')`. MEASURED: 18,334 rows in, 1 dict entry out.
        #
        # ⚑ AND IT FAILED SILENTLY THROUGH TWO FULL INGESTS. No exception — the
        # projection simply had nothing to project, reported "1 packings, 0 units", and
        # exited 0. The reads were fine (`event_head` returns all 6,387 rows); what was
        # wrong was the SHAPE of each row, which no count could reveal.
        #
        # `schema.rows` already normalises this to a name-keyed tuple subclass, but it is
        # a generator and these callers index/iterate freely — so normalise here, at the
        # runtime every named query flows through.
        return _rows_of(res if res is not None else cur)
    from query_defs import run as _compile_run  # back-compat: a Core stmt object (dynamic path)

    return _compile_run(con, name, **params)


def _selftest():
    """⚑ THIS MODULE HAD NO SELFTEST, WHICH IS WHY THE BACKEND OUTLIER SHIPPED TWICE.
    `run_selftests` DISCOVERS modules that define one, so a file with none is INVISIBLE
    rather than failing — and this file decides which SQL DIALECT every named query in the
    ingest path executes."""
    import os as _os

    cases = []

    def check(label, got, want):
        cases.append((label, got == want, got, want))

    import store as _store

    # ⚑ THE ONE CASE THAT WOULD HAVE CAUGHT THE BUG: the cache's backend and the store's
    # must be the SAME ANSWER, not merely the same env var. The defect was a duplicated
    # DEFAULT — both read `SUBSTRATE_STORE`, and they disagreed when it was unset.
    _saved = _os.environ.get("SUBSTRATE_STORE")
    try:
        _os.environ.pop("SUBSTRATE_STORE", None)
        check(
            "UNSET: the cache resolves the SAME backend as the store",
            _cache_backend(),
            _store.backend(),
        )
        # ⚑ AND IT MUST BE POSTGRES WHEN UNSET — pinning the VALUE, not just the agreement.
        # Two readers that agree on the wrong answer are still wrong, and an agreement-only
        # case passes if both regress together.
        check("...and that backend is postgres (the live store)", _cache_backend(), "postgres")
        # ⚑ THE LOOP USED TO RUN OVER `("sqlite", "postgres")` and assert the two readers
        # AGREED for each. With one backend the agreement case is trivial, so what is
        # asserted instead is the REFUSAL: an explicit `SUBSTRATE_STORE=sqlite` must not
        # resolve a cache at all. A deleted case would leave the stale-pin path untested
        # in the module that decides which SQL DIALECT the ingest executes — which is the
        # exact hole that let the backend outlier ship twice.
        _os.environ["SUBSTRATE_STORE"] = "postgres"
        check("explicit postgres agrees too", _cache_backend(), _store.backend())
        _os.environ["SUBSTRATE_STORE"] = "sqlite"
        try:
            _cache_backend()
            check("a stale SUBSTRATE_STORE=sqlite REFUSES", "returned", "SystemExit")
        except SystemExit:
            check("a stale SUBSTRATE_STORE=sqlite REFUSES", "SystemExit", "SystemExit")
    finally:
        if _saved is None:
            _os.environ.pop("SUBSTRATE_STORE", None)
        else:
            _os.environ["SUBSTRATE_STORE"] = _saved

    # ⚑ THE LOADED CACHE MUST MATCH THE PARAMSTYLE ITS BACKEND BINDS. sqlite compiles
    # `:name`; psycopg needs `%(name)s`. Serving one to the other is the live failure
    # (`syntax error at or near ":"`), so assert the SHAPE of what was loaded rather than
    # trusting that the right module was imported.
    # ⚑ MY FIRST VERSION OF THIS CASE WAS DECORATION, TWICE OVER. It read the module-level
    # `SQL` — frozen at import, so it never saw the env changes above — and its condition was
    # `"%(" in s or ":" not in s.split("WHERE")[-1]`, which passes on any query with no
    # WHERE clause. It reported 6/6 under BOTH backends while asserting nothing about either.
    #
    # The real claim is about the PARAMSTYLE of the cache each backend loads: sqlite compiles
    # `:core_id`, psycopg needs `%(core_id)s`. Serving one to the other IS the live failure
    # (`syntax error at or near ":"` on `WHERE core_fp.core_id = :core_id`), so drive the
    # actual per-backend module and assert the binding form.
    def _paramstyle_of(mod):
        try:
            _m = __import__(mod)
        except Exception:
            return None
        s = next((q for q, _d in _m.SQL.values() if "core_fp" in q and "WHERE" in q), None)
        if s is None:
            return None
        tail = s.split("WHERE")[-1]
        return "pyformat" if "%(" in tail else ("named" if ":" in tail else None)

    _pg = _paramstyle_of("query_sql_postgres")
    if _pg is not None:
        check("the postgres cache binds %(name)s", _pg, "pyformat")
    # ⚑⚑ THE SQLITE CACHE MUST BE GONE, NOT MERELY UNREAD — and this is the case that
    # says so. The retired pair asserted the two caches bound DIFFERENT paramstyles and
    # were "NOT interchangeable"; deleting them would leave a `query_sql.py` that a stale
    # checkout still has on disk, which `_load_sql` no longer imports but nothing forbids
    # someone re-adding a fallback to. Asserting its ABSENCE is what makes the removal a
    # property of the tree rather than of one function's body.
    check("the sqlite cache is ABSENT, not just unread", _paramstyle_of("query_sql"), None)
    check("a cache was loaded", len(SQL) > 0, True)

    failed = [c for c in cases if not c[1]]
    for label, _, got, want in failed:
        print("  FAIL %s: got %r want %r" % (label, got, want))
    print("selftest: %d/%d" % (len(cases) - len(failed), len(cases)))
    return 0 if not failed else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__.strip().splitlines()[0])
    print("\n  --selftest   the guarded cases")
    print("\n  This is the cached RUNTIME; the compiler is query_defs.py.")
    print("  Regenerate: SUBSTRATE_STORE=<backend> python3 query_defs.py --compile")
