# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The row / param / execute helpers — THE portable read+write contract.

⚑⚑ WHY THESE ARE THEIR OWN MODULE, AND IT IS A DEPENDENCY FACT RATHER THAN A SIZE ONE.
Everything here is BACKEND-NEUTRAL: it exists to make one call site work on sqlite AND
postgres, which is the porting problem the whole layer was written for. The queue tier
(`schema_queue`) is built FROM these, and the declaration (`schema_decl`) is what these
are built from — so the three sit in a strict order:

    schema_decl  ←  schema_rows  ←  schema_queue  ←  schema

⚑ AND THAT ORDER IS WHY THE SPLIT WORKS AT ALL. With the helpers still in `schema.py`,
`schema_queue` had to import `schema` and `schema` had to import `schema_queue` — a
cycle that fails with `ImportError` on a partially-initialised module (measured, not
predicted: the first attempt at this split raised exactly that on `_require_pg`).
Moving the helpers BELOW the tier that consumes them turns the cycle into a DAG.

⚑ THE ⚑ BLOCKS ARE VERBATIM. Each of these functions carries the measured defect that
produced it — the 37 `.fetchone()[0]` sites that raise `KeyError: 0` under psycopg's
dict_row, the 21 hand-spelled `INSERT OR IGNORE` strings, the paramstyle that psycopg
REFUSES rather than misbinds, the `executescript` that is sqlite3-only. Those notes are
the reason the layer exists and moved with it unchanged.

`schema.py` re-exports every name defined here, so `_schema.rows`, `_schema.scalar`,
`_schema.upsert`, `_schema.ph`, `_schema.execute`, `_schema.apply`, `_schema.relations`
and `_schema.Row` all resolve exactly as they did for all nine importing modules.
"""

import sys

from schema_decl import *  # noqa: F401,F403  (the declaration)

# ⚑ `VIEWS`, `_TIER_VIEWS`, `_view_ddl_named`, `view_ddl`, `table` AND `CreateView` LEFT
# THIS LINE 2026-08-12 (⟡view-purge) WITH THE CAPABILITY THEY NAMED — see the same note on
# `schema.py`'s re-export. `ddl` and `_tier` stay: they still emit, just no views.
from schema_decl import (
    MD,
    INDEXES,
    _TIERS,
    _tier,
    ddl,
    MetaData,
    Table,
    Column,
    Text,
    Integer,
    BigInteger,
    Index,
    Identity,
    PrimaryKeyConstraint,
    select,
    func,
    exists,
    literal,
    CreateTable,
    CreateIndex,
)


class Row(tuple):
    """A result row readable BY NAME (`row["core_id"]`) and, transitionally, by position.

    ⚑ NAMES ARE THE POINT — they make a read structurally traceable (`pycodemod --key
    core_id` finds every consumer of that column, which no positional read admits) and
    they survive a SELECT gaining a column, which a positional read does not.

    ⚑ IT SUBCLASSES `tuple` SO THE MIGRATION CAN BE INCREMENTAL. ~37 sites read
    `.fetchone()[0]` today; making names the ONLY access would require converting all of
    them in one commit, and an atomic rewrite of every reader is the migration that
    stalls. Positional access keeps working, so a reader is converted when it is touched.
    ⚑ That tolerance is a RAMP, not the destination: new code reads by name, and the
    positional sites are debt with a name (`row[0]` in a store reader) rather than an
    idiom to preserve.

    Unpacking (`for a, b in rows(...)`) works unchanged — it is tuple iteration.
    """

    # ⚑ NO `__slots__` AT ALL, AND THE REASON IS A LANGUAGE CONSTRAINT I DID NOT KNOW:
    # a tuple subclass cannot declare a NON-EMPTY __slots__ ("nonempty __slots__ not
    # supported for subtype of 'tuple'") because a tuple's storage is fixed at
    # allocation. `__slots__ = ()` is legal but then FORBIDS the `_keys` attribute.
    # Measured by running it — both spellings fail, in different ways.
    #
    # ⚑ SO THE KEYS ARE SHARED, NOT PER-ROW, which is better than what I was reaching
    # for. Every row of one result set has the SAME columns, so `_keys` is a property of
    # the CURSOR: interning one tuple per query and pointing every row at it costs one
    # pointer per row rather than a dict, and there are millions of rows.
    def __new__(cls, keys, values):
        self = super().__new__(cls, values)
        self._keys = keys  # the SHARED key tuple, interned once per result set
        return self

    def __getitem__(self, k):
        if isinstance(k, str):
            try:
                return tuple.__getitem__(self, self._keys.index(k))
            except ValueError:
                raise KeyError(f"{k!r} not in row; columns are {list(self._keys)}") from None
        return tuple.__getitem__(self, k)

    def keys(self):
        return self._keys

    def get(self, k, default=None):
        try:
            return self[k]
        except KeyError:
            return default

    def as_dict(self):
        return dict(zip(self._keys, self))

    def __repr__(self):
        return "Row(%s)" % ", ".join(f"{k}={v!r}" for k, v in zip(self._keys, self))


def ph(n=1):
    """`n` parameter placeholders: `%s, %s`. There is one paramstyle.

    ⚑ THE PARAMSTYLE WAS BACKEND-SPECIFIC AND WAS BEING SPELLED PER SITE. sqlite takes
    `?`, psycopg takes `%s`, and psycopg REFUSES the wrong one outright ("the query has 0
    placeholders but 1 parameters were passed") rather than misbinding — loud, at least.

    ⚑ THE MEASURE OF HOW EASILY THIS REPRODUCES: the site that caught it was written
    EARLIER THE SAME DAY as the store authority, by me, while porting. Knowing better
    once does not help; the fix is that a caller never types a placeholder, so there is
    no per-site chance to type the wrong one.

    ⚑⚑ AND THE FUNCTION THAT FIXED THE PER-SITE SPELLING STILL CARRIED THE DEFECT ONE
    LEVEL UP, WHICH IS WHY THE `back` PARAMETER IS GONE (⓺, 2026-08-11). It resolved
    `back or store.backend()` — the AMBIENT backend, an environment variable — while the
    placeholder it returns is bound to a specific CONNECTION. Those two can disagree, and
    every time they did the failure was the same: `SUBSTRATE_STORE=postgres` emitted `%s`
    into a sqlite cursor (`OperationalError: near "%"`) or a sqlite ambient emitted `?`
    into a psycopg one ("0 placeholders but 1 parameters"). FOUR recorded occurrences:
    `set1_ratchet_cores._freshen`, its second connect, `sppf_db.build`, and the
    `verify_incremental` fixture that had to pin `ph(1, 'sqlite')` by hand to work around
    it. The last of those is the tell — a parameter whose only user in the whole corpus
    was a workaround for its own defect.

    ⚑ MEASURED BEFORE REMOVING, AND THE TWO MEASUREMENTS DISAGREED IN A WAY WORTH
    KEEPING. `pycodemod --forwards ph back` reported **0 of 50 call sites** forward it —
    which reads as "nothing uses it". But `--forwards` asks about a KEYWORD, and the
    parameter was also passed POSITIONALLY: `pycodemod --literal sqlite` found
    `ph(1, back)` and `ph(len(cols), back)` here plus three `ph(n, 'sqlite')` fixtures in
    `schema_selftest`. Same population, two spellings, and the first census could not see
    the second — *a fact about the METHOD reported as a fact about the substrate*. The
    conclusion held; the evidence for it did not, until it was asked the other way.

    ⚑ REMOVING THE PARAMETER, NOT JUST IGNORING IT. An ignored `back=` still reads at
    every call site as though the backend were selectable there, which is how the branch
    gets re-added. `ph(1, 'sqlite')` is now a `TypeError` — loud, at the one place that
    could reintroduce the disagreement.
    """
    return ", ".join(["%s"] * n)


def execute(con, sql, params=()):
    """Run one statement on either backend. The WRITE counterpart to `rows`.

    ⚑ `con.execute(...)` IS NOT PORTABLE. sqlite3 puts `execute`/`executemany` on the
    CONNECTION; psycopg puts them only on a CURSOR — so every `con.execute` raises
    `AttributeError: 'Connection' object has no attribute 'executemany'` against
    postgres. MEASURED: 23 `executemany` sites, 9 of them in `sppf_db`'s delete paths.
    """
    cur = con.cursor() if not hasattr(con, "execute") else con
    return cur.execute(sql, params) if params else cur.execute(sql)


def execute_many(con, sql, seq):
    """Run one statement over a sequence of parameter tuples, on either backend.

    ⚑ TWO DEFECTS PER SITE, and they travel together: the connection-level method (above)
    and a hardcoded `?` in the SQL. A caller must therefore build its statement with
    `ph()` — passing a `?`-spelled string here would still fail on postgres, so this
    helper cannot save a caller that types its own placeholder.
    """
    seq = list(seq)
    if not seq:
        return 0
    cur = con.cursor() if not hasattr(con, "executemany") else con
    cur.executemany(sql, seq)
    return len(seq)


def rows(con, sql, params=()):
    """YIELD result rows, one at a time, on either backend. THE read contract.

    ⚑ THIS IS THE YIELD-DRIVEN CONTRACT AND THE ROW-FACTORY PORT AT ONCE — they are the
    same defect seen twice. `catalog_query._rows` already established "a cursor IS the
    generator; do not materialize" (user, 2026-08-05: *"we should not be using RAM as
    storage"*), but it was `con.execute(...)`, which is sqlite-only AND returns rows that
    index positionally. A caller writing `row[0]` breaks on psycopg's `dict_row` with
    `KeyError: 0` — MEASURED live in `query_registry`, three defects in five lines.

    ⚑ SO THE FIX IS ONE FUNCTION, NOT TWO SWEEPS. Streaming and portability are the same
    walk: whatever yields the rows must also normalise how a row is read.

    ⚑ ROWS COME BACK KEYED BY NAME (user, 2026-08-06: *"I'll actually push that we
    migrate to names here. My reasoning is forward-looking: By using names, it's easier
    for us to structurally trace for reuse"*).

    My first cut yielded TUPLES, arguing that positional rows port the ~37 existing
    `row[0]` call sites unchanged. That is a COST argument, not a reason — the same
    shape as preserving any defect because touching it is work. The naming argument is
    about what the code can then TELL you:

      * `row["core_id"]` is STRUCTURALLY TRACEABLE — `pycodemod --key core_id` finds
        every reader of that column. `row[2]` is opaque: nothing can resolve it without
        reading the SELECT and counting, so positional access severs a column from its
        consumers and defeats the reuse-search this repo runs on.
      * A positional read SILENTLY SHIFTS when a SELECT gains a column. `core_fp` gained
        `producer` THIS SESSION; a `row[2]` against it now reads a different field with
        no error. A named read fails loudly or keeps working.

    The row type is a `Row` mapping supporting BOTH `row["x"]` and `row[0]`, so the
    positional sites keep working while new code is written by name — the sweep converts
    readers as they are touched instead of demanding one atomic rewrite.
    """
    cur = con.cursor() if not hasattr(con, "execute") else con
    res = cur.execute(sql, params) if params else cur.execute(sql)
    it = res if res is not None else cur
    desc = getattr(cur, "description", None) or getattr(res, "description", None)
    # ⚑ THE KEY TUPLE IS BUILT ONCE PER RESULT SET, not once per row. Every row of a
    # query has the same columns, so interning it here and sharing the reference costs
    # one pointer per row instead of a per-row structure — and these result sets run to
    # millions of rows (1.6M `edge`, 1.6M `obs` in the sqlite tier).
    names = tuple(d[0] for d in desc) if desc else ()
    for r in it:
        if isinstance(r, dict):
            yield Row(tuple(r.keys()), list(r.values()))
        else:
            yield Row(names, list(r))


def scalar(con, sql, params=()):
    """The FIRST COLUMN of the first row, or None — the `fetchone()[0]` idiom, ported.

    ⚑ 37 SITES DO `.fetchone()[0]` ACROSS 11 MODULES (measured 2026-08-06), and every
    one of them raises `KeyError: 0` against psycopg's dict_row. That is the class which
    fails at RUNTIME ON REAL DATA rather than at import — so it survives every smoke test
    that runs against an empty store, which is exactly the state the postgres tier is in
    right now.

    ⚑ AND `None` FOR NO ROWS IS THE HONEST ANSWER, not 0. `fetchone()[0]` raises
    `TypeError` on an empty result; callers that want a default should say so, because a
    silent 0 from an EMPTY table reads identically to a genuine count of zero — and the
    Set₁ census is precisely a gate that must not confuse those.
    """
    for r in rows(con, sql, params):
        return r[0] if r else None
    return None


def schema_version(con, back=None):
    """The SCHEMA_VERSION the store was built at, or None if it predates versioning.

    ⚑ `PRAGMA user_version` IS SQLITE-ONLY and there is no postgres equivalent — it is a
    32-bit integer slot in the sqlite file header, not a SQL feature. So the version has
    to live in a TABLE, which is portable and strictly better: a header int can hold a
    number and nothing else, while a row can say WHEN it was set and by WHICH tier.

    ⚑ ASKS THE CATALOGUE FIRST; DOES NOT CATCH A FAILED QUERY. On a store built before
    this table existed the SELECT raises, and that must read as "unversioned" — the same
    answer `PRAGMA user_version` gives for a fresh file. My first cut wrapped the SELECT
    in `except Exception: return None`, which is SQLITE REASONING APPLIED TO POSTGRES:

      ⚑ POSTGRES ABORTS THE WHOLE TRANSACTION ON ANY ERROR. Catching the exception does
      NOT undo that — every subsequent statement fails with `InFailedSqlTransaction:
      current transaction is aborted`, so a "tolerant" read poisons the connection for
      everything after it. MEASURED: the Set₁ gate got past this read and then died on
      the next `DROP TABLE`, four frames away, with an error naming neither the read nor
      the table. sqlite has no such coupling, which is why the pattern looks fine there.

    So the existence question is asked of the CATALOGUE (`relations`), which succeeds
    whether or not the table is there, and the SELECT runs only when it will not raise.
    *Do not "handle" an error on postgres that you could have avoided asking.*
    """
    if "schema_version" not in relations(con, back):
        return None
    return scalar(con, "SELECT version FROM schema_version")


def set_schema_version(con, version, back=None):
    """Record `version` as the store's schema version (single-row table)."""
    cur = con.cursor()
    cur.execute("DELETE FROM schema_version")
    # ⚑ WAS AN if/else ON THE PARAMSTYLE — the fork `ph()` exists to remove. Two spellings
    # of one fact, in the authority that is supposed to own it.
    cur.execute(f"INSERT INTO schema_version (version) VALUES ({ph(1)})", (version,))


def dedup(con, table_name, key_cols, back=None):
    """Delete duplicate rows of `table_name`, keeping one per `key_cols` tuple.

    ⚑ `rowid` IS SQLITE-ONLY and postgres's `ctid` is NOT a substitute: ctid is a
    physical location that CHANGES on UPDATE and after VACUUM, so `MIN(ctid)` names a
    different row over time. The portable formulation is a window function —
    `ROW_NUMBER() OVER (PARTITION BY key)` — which both engines support (sqlite since
    3.25) and which says what is meant: keep the first row per key, drop the rest.

    ⚑ AND IT IS A REPAIR, NOT A ROUTINE STEP. `path_seg` acquires duplicates only when an
    interner writes the same (path_id, ord) twice; the unique index normally prevents it.
    Keeping the operation means a store built before that index can still be cleaned.

    ⚑ THE `ROWID` ARM IS GONE WITH SQLITE, AND ITS REASONING IS WHAT SURVIVES: the note
    above says `rowid` is sqlite-only and `ctid` is NOT a substitute, because ctid is a
    physical location that CHANGES on UPDATE and after VACUUM. That is still true, and it
    is why this deletes by ctid inside ONE statement rather than reading ctids out and
    deleting by them later — the identity is valid only for the duration of the scan.
    """
    keys = ", ".join(key_cols)
    cur = con.cursor()
    cur.execute(f"""
        DELETE FROM {table_name} a
         USING (SELECT ctid, ROW_NUMBER() OVER (PARTITION BY {keys}) AS rn
                  FROM {table_name}) b
         WHERE a.ctid = b.ctid AND b.rn > 1
    """)


def relations(con, back=None):
    """{name: 'table'|'view'} for every relation in the store — the engine's own answer.

    ⚑ FIVE SITES ASKED THIS VIA `sqlite_master`, which postgres does not have. They span
    `graded_orbit` (does `_orbit_def` exist?), `query_registry`, `catalog_query` (two),
    and `query_topo` — one capability, five spellings, each of them a hard porting stop
    rather than a stylistic one.

    ⚑ AND THE TWO CATALOGUES DISAGREE ABOUT WHAT A 'TABLE' IS: `information_schema`
    reports a view's `table_type` as VIEW while listing it in `tables`, so a naive port
    that counted rows there would silently include views wherever sqlite's
    `type='table'` excluded them. That difference already produced one wrong verdict
    today (a probe read 19 relations against a 14-table expectation and reported the
    schema as broken). Normalising to a {name: kind} map makes the distinction explicit
    at every call site instead of implicit in each query.

    ⚑ THE `sqlite_master` ARM IS GONE, AND THE {name: kind} NORMALISATION IS WHY IT COULD
    BE. The five call sites this consolidated each asked their OWN `sqlite_master`
    question; had they been ported one at a time they would have become five
    `information_schema` questions with five different views/tables conventions. One map,
    one convention, one deletion.
    """
    # ⚑⚑ SCOPED TO `current_schemas(false)`, NOT "everything but the system schemas".
    # The retired filter was `table_schema NOT IN ('pg_catalog', 'information_schema')`,
    # which answers *"what does this DATABASE contain"*. Every caller means *"what can I
    # reach by unqualified name"* — they write `SELECT … FROM core_fp`, never a qualified
    # one — and the two stopped agreeing the moment `sandbox_fixture` put a private schema
    # on the search_path: a fixture's `relations()` would list its OWN tables AND the
    # tenant's, so a count against `len(MD.sorted_tables)` reads double.
    #
    # ⚑ `false` EXCLUDES THE IMPLICIT SYSTEM SCHEMAS, which is what makes this a strict
    # improvement rather than a swap: `current_schemas(true)` would include `pg_catalog`
    # and reintroduce exactly what the old NOT IN clause was written to remove.
    cur = con.cursor()
    cur.execute("""
        SELECT table_name, table_type FROM information_schema.tables
         WHERE table_schema = ANY (current_schemas(false))
    """)
    out = {}
    for r in cur:
        name, kind = (r["table_name"], r["table_type"]) if isinstance(r, dict) else r
        out[name] = "view" if kind == "VIEW" else "table"
    return out


def columns_of(con, name, back=None):
    """The column names of `name`, in declared order — the engine's own answer.

    ⚑ `PRAGMA table_info` IS SQLITE-ONLY, and it travelled with `sqlite_master` at the
    same call sites: a listing that names relations almost always then names their
    columns. Porting one without the other would have moved the failure by one line.

    ⚑ READ FROM THE ENGINE, NOT FROM `MD`, deliberately. The model knows the DECLARED
    schema; this reports what the store ACTUALLY has — which is what a `schema` listing
    is for, and the only way it can show drift between the two.

    ⚑ `PRAGMA table_info` IS GONE WITH ITS BACKEND. The note above records that it
    TRAVELLED with `sqlite_master` — a listing that names relations almost always then
    names their columns — so the two arms are removed together for the same reason they
    had to be ported together: dropping one would move the failure by one line.
    """
    # ⚑ SAME SCOPING AS `relations()`, AND FOR THE SAME REASON — the two travel together
    # (a listing that names relations then names their columns). Under a fixture's private
    # schema the old filter would return the columns of BOTH copies of a table,
    # interleaved by `ordinal_position`, which is a wrong answer that looks like a schema
    # drift report.
    cur = con.cursor()
    cur.execute(
        """
        SELECT column_name FROM information_schema.columns
         WHERE table_name = %s
           AND table_schema = ANY (current_schemas(false))
         ORDER BY ordinal_position
    """,
        (name,),
    )
    return [(r["column_name"] if isinstance(r, dict) else r[0]) for r in cur]


# ⚑ BELOW THIS, COPY'S SETUP COSTS MORE THAN IT SAVES. A COPY write is three statements
# (CREATE TEMP / COPY / INSERT…SELECT) plus a DROP, so for a handful of rows the round-trips
# it adds exceed the ones it removes. The number is a THRESHOLD, not a tuning constant: the
# win is asymptotic and any small value picks the right branch for the 6.27M-row case, which
# is the one that mattered. Deliberately not measured to a precise crossover — a fitted
# constant here would be a stale proxy the first time the schema or the network changes.
_COPY_MIN = 64


def transport_report():
    """What the WRITE PATH actually does — driver, pipeline support, and which branch runs.

    ⚑⚑⚑ THIS MODE EXISTS BECAUSE I ASSERTED A DRIVER PROPERTY, BUILT ON IT, AND THEN REACHED
    FOR AN INSTRUMENT BEFORE READING THE DOCS (operator, 2026-08-14: *"I don't want us assuming
    a driver is doing the right thing … if we simply defer to it, we paint ourselves into a
    contorted corner"*, then: *"Have we considered reading its documentation?"*). Both notes
    landed. The sequence was: assert "psycopg 3 executemany does not batch" from general
    knowledge → build a COPY path on it → propose measuring it → finally read `cursor.py`.

    ⚑⚑ AND THE SOURCE REFUTED MY ASSERTION. `Cursor.executemany` (:126-146) branches:

        if Pipeline.is_supported():
            ... self._executemany_gen_pipeline(query, params_seq, returning)
        else:
            ... self._executemany_gen_no_pipeline(...)

    So psycopg 3 DOES pipeline `executemany` when libpq supports it — the whole `params_seq`
    goes out in one flush, not one round-trip per row. "psycopg doesn't batch" was FALSE, and
    the docstring (`"Execute the same command with a sequence of input data."`) says nothing
    either way, which is why reading the SOURCE and not the summary was the step that settled
    it.

    ⚑ SO THE ROW-AT-A-TIME WITNESS HAS A DIFFERENT CAUSE, AND IT IS STILL UNEXPLAINED. The
    measurement stands — `INSERT INTO obs_node (…) VALUES ($1,$2,$3,$4)` at 0.8ms inside a
    12-minute transaction, pg `idle in transaction` on ClientRead. If the driver pipelines,
    that pattern points at the CALLER: rows arriving one at a time from a Python loop that
    calls `upsert` per item, rather than one `upsert` over a batch. That is a substrate defect,
    not a driver one — which is exactly the "learn how we're holding it wrong" the operator
    named, and it would have been invisible from behind a COPY path that made the symptom
    disappear.

    ⚑ THE COPY PATH IS STILL CORRECT and stays: COPY beats even a pipelined INSERT for bulk
    (no per-row parse/plan), and `INSERT … SELECT` off a staging table keeps the conflict
    clause. But it is now justified by what COPY IS, not by a false claim about what
    `executemany` is not.
    """
    import psycopg
    from psycopg import Pipeline

    return {
        "driver": "psycopg %s" % psycopg.__version__,
        "pipeline_supported": Pipeline.is_supported(),
        "executemany_batches": Pipeline.is_supported(),
        "copy_threshold_rows": _COPY_MIN,
        "bulk_path": (
            "COPY → temp → INSERT…SELECT (conflict clause preserved)"
            if Pipeline.is_supported()
            else "COPY → temp → INSERT…SELECT; executemany fallback is NOT pipelined here"
        ),
    }


def _copy_capable(cur):
    """Can this cursor stream a COPY? — a CAPABILITY probe, never a backend name.

    ⚑ ASKED OF THE OBJECT, NOT OF A VERSION STRING. The sibling `hasattr(con, "cursor")`
    note in `upsert` records exactly this distinction: conflating "which driver is this"
    with "what can this object do" is what broke every cursor-passing caller last time.
    A caller may pass a connection, a cursor, or a test double; the double's whole point is
    that it does NOT speak COPY, and it must fall through to the row path rather than raise.
    """
    return hasattr(cur, "copy")


def upsert(con, table_name, rows, on_conflict="ignore", back=None):
    """Bulk-insert `rows` (tuples, in declared column order), tolerating conflicts.

    on_conflict='ignore'  → skip a row that violates a key   (was `INSERT OR IGNORE`)
    on_conflict='replace' → overwrite it                     (was `INSERT OR REPLACE`)

    ⚑ ONE CAPABILITY, 21 SPELLINGS. `sppf_db` alone carried 21 `INSERT OR
    IGNORE/REPLACE INTO <t> VALUES (?,…)` strings, each hardcoding THREE sqlite-isms:
    the `OR IGNORE` clause (postgres spells it `ON CONFLICT DO NOTHING`), the `?`
    paramstyle (postgres uses `%s`), and a positional VALUES list whose arity must match
    the table by hand — so adding `producer` to `core_fp` meant editing a `(?,?)` into a
    `(?,?,?)` and hoping every site agreed.

    ⚑ THE ARITY COMES FROM THE DECLARATION, which is the real win. Rows are tuples in
    DECLARED COLUMN ORDER and the column names are read off the model, so a schema change
    cannot silently desynchronise from an insert site: add a column and every caller
    passing the old arity fails loudly at the zip rather than writing shifted data.

    ⚑ `on_conflict='replace'` REQUIRES A CONFLICT TARGET on postgres — `DO UPDATE` must
    know WHICH constraint it is resolving, while sqlite's `OR REPLACE` infers it. The
    primary key is that target, so a table without one cannot use 'replace'; this raises
    rather than silently degrading to an append, because a silent append into `core_fp`
    would double every re-ingest.

    ⚑ THE `OR IGNORE` / `OR REPLACE` ARM IS GONE (⓺). The paragraph above is now the
    WHOLE contract rather than the postgres half of it, and that is a strengthening: the
    sqlite arm could infer a conflict target, so a table with no primary key silently
    worked there and raised here. One arm means one behaviour, and the one that survives
    is the one that refuses.
    """
    t = MD.tables[table_name]
    # ⚑ THE `_STORE_ASSIGNED` EXCLUSION WAS DELETED HERE 2026-08-12 WITH `obs.seq`, its only
    # member. The line read:
    #     cols = [c.name for c in t.columns if c.name not in _STORE_ASSIGNED.get(table_name, ())]
    # and its note is the part to keep: *"A STORE-ASSIGNED COLUMN MUST NOT APPEAR IN THE INSERT
    # LIST … excluding it here rather than at 27 call sites is the same reasoning as reading the
    # arity off the declaration in the first place: a writer should not have to know which
    # columns it is not allowed to write."* No column is engine-assigned today, so the column
    # list IS the declaration; restore the FILTER, not the dict, if one ever is.
    cols = [c.name for c in t.columns]
    if not rows:
        return 0

    # ⚑ ONE PLACEHOLDER SOURCE. Each branch built its own (`'?' * len(cols)` here,
    # `["%s"] * len(cols)` there) and the postgres one was named `ph`, SHADOWING the
    # module-level `ph()` added for exactly this. Two correct spellings of one fact is
    # how the third, wrong one gets written.
    marks = ph(len(cols))
    if on_conflict == "ignore":
        tail = "ON CONFLICT DO NOTHING"
    else:
        pk = [c.name for c in t.primary_key.columns]
        if not pk:
            raise ValueError(
                f"upsert(replace) needs a PRIMARY KEY as its conflict target; "
                f"{table_name} declares none"
            )
        sets = ", ".join(f"{c} = EXCLUDED.{c}" for c in cols if c not in pk)
        tail = (
            f"ON CONFLICT ({', '.join(pk)}) DO UPDATE SET {sets}"
            if sets
            else f"ON CONFLICT ({', '.join(pk)}) DO NOTHING"
        )
    sql = f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({marks}) {tail}"

    # ⚑ `hasattr(con, "cursor")` IS NOT THE SQLITE SHIM AND MUST NOT BE REMOVED WITH IT.
    # The retired spelling was `hasattr(con, "cursor") and back != "sqlite"`, which
    # conflated TWO facts: "this is a psycopg connection, not a sqlite one" (backend —
    # gone) and "this is a CONNECTION, not an already-open CURSOR" (polymorphism —
    # still live, since callers pass both). Deleting the whole test because half of it
    # named the retired backend would break every cursor-passing caller.
    cur = con.cursor() if hasattr(con, "cursor") else con
    rows = list(rows)
    # ── ⑺ THE DETERMINISTIC-ORDER SORT — ADDED AND REMOVED 2026-08-12, WITHIN THE HOUR ──────
    #
    # ⚑⚑ IT WAS AN ANTIPATTERN FOR THIS ARCHITECTURE AND IT IS REMOVED UNAPPLIED (user,
    # 2026-08-12: *"I really feel like it's going about this exactly the wrong way, trying to
    # sort things. It's trying to deal with race conditions when that's what content-addressing
    # is for."* and *"a deadlock should be impossible by construction"*). The deleted lines were
    #
    #     try:
    #         rows.sort()
    #     except TypeError:
    #         rows.sort(key=lambda r: tuple((v is None, str(v)) for v in r))
    #
    # justified as: *"A GLOBAL ORDER REMOVES THE CYCLE RATHER THAN RETRYING IT … this makes the
    # cycle unconstructible."*
    #
    # ⚑⚑ THE JUSTIFICATION IS TRUE AND IS THE WRONG MOVE, WHICH IS THE POINT. A global order
    # makes the CYCLE unconstructible while leaving the HOLD in place: writer B still waits for
    # writer A, it simply cannot wait back. That converts a deadlock into a serialisation — B
    # blocks for the whole of A's batch — which is the "serialise the pipeline" antipattern in a
    # different costume, and it gets worse as `make ingest -j` widens. **Ordering contention is
    # not the same as removing the need for it.**
    #
    # ⚑ THE ACTUAL LOCATION OF THE HOLD IS THE LINE BELOW, AND IT IS NOT ORDERING. See
    # `executemany`'s note: one call is ONE transaction over N rows, so it holds every index
    # tuple it has already inserted while wanting the next. That is the hold-and-wait, and it
    # is introduced by the BATCH WIDTH, not by the order the batch happens to be in.
    #
    # ⚑ ONE FRAGMENT WORTH KEEPING FOR WHOEVER SORTS ROWS HERE FOR SOME OTHER REASON: a bare
    # `sorted()` raises `TypeError` on the first column that MIXES None with a value
    # (`event.qname_pid`), while an ALL-NULL column does NOT raise — tuple comparison tests
    # `==` before `<`, and `None == None` is True. And a `key=` allocates one object per row,
    # which on `obs_node` (654k rows in the sandbox, corpus-scaled thereafter) is hundreds of
    # MB on top of a row list that is already the peak.
    # ⚑⚑⚑ CORRECTION, 2026-08-14: THE CLAIM THAT USED TO HEAD THIS BLOCK WAS FALSE. It read
    # *"`executemany` IS ONE ROUND-TRIP PER ROW ON psycopg 3"* — asserted from general
    # knowledge, never checked. `cursor.py:126-146` branches on `Pipeline.is_supported()` and
    # pipelines the whole `params_seq` when libpq allows; see `transport_report()`. So psycopg
    # DOES batch, the docs' one-line summary settles nothing either way, and reading the SOURCE
    # was the step that resolved it — after I had already built this path on the assertion and
    # proposed an instrument to measure what a five-minute read answered.
    #
    # ⚑⚑ THE WITNESS BELOW IS STILL REAL AND ITS CAUSE IS NOW OPEN — which is the useful state,
    # not a resolved one. If the driver pipelines, a per-row INSERT pattern points at the
    # CALLER: rows arriving one at a time from a Python loop calling this per item, rather than
    # one call over a batch. That would be a substrate defect the COPY path would have HIDDEN.
    # Measured against the live store, mid-run:
    #
    #     pid 90  active  xact 0:12:16 / query 0:00:00.000800
    #     INSERT INTO obs_node (core_id, local_id, node_id, ch) VALUES ($1,$2,$3,$4)
    #
    # A 0.8 MILLISECOND statement inside a TWELVE MINUTE transaction, with pg `idle in
    # transaction` on ClientRead and absent from atop's CPU list while `python` sat at 48%
    # (operator, independently). Those are the MEASURED facts.
    #
    # ⚑ WHAT IS **NOT** MEASURED, and an earlier version of this comment stated as fact: "there
    # are 6.27M of them, one network round-trip apiece." The per-row round-trip count was
    # INFERRED from the false driver claim above, not observed — `pg_stat_activity` samples the
    # CURRENT statement, so it shows a single-row INSERT was executing at that instant and says
    # nothing about how many round-trips carried the batch. `pg_stat_statements` would answer
    # it and is not loaded on this instance. So: single-row INSERT statements are real, their
    # COUNT and their transport are open.
    #
    # ⚑⚑ THE CODE READ AS SET-BASED AND WAS NOT, WHICH IS WHY IT SURVIVED AN AUDIT.
    # `sql_lift.py --report` lists `project_sppf` as a licensed lift; its docstring says
    # "a 1-JOIN, not recursive"; the surrounding comments reason about BATCH WIDTH and the
    # hold-and-wait as though a batch were one statement. Every one of those is about the
    # SQL. The TRANSPORT underneath spelled the same rows as N statements, and no reading of
    # the query text could see it — only `pg_stat_activity` could.
    #
    # ⚑ THIS FIXES THE TRANSPORT AND IS **NOT** THE ARCHITECTURAL FIX — recorded so nobody
    # reads a faster ingest as a solved one. A first version of this comment argued `packing`
    # "is legitimately computed client-side", citing the call site's *"ONE WRITE OF A VALUE
    # ALREADY IN MEMORY"*. That is a justification for why the WRITE is cheap; it is not an
    # argument that the value should have been in Python memory at all (operator, 2026-08-14:
    # *"Just because something CAN be computed in python doesn't mean it SHOULD be"*), and
    # taking a code comment as a finding is the error this repo files against itself weekly.
    #
    # ⚑⚑ `project_sppf`'s packing loop IS A FOLD-OVER-CLOSURE AND `sql_lift --report` ALREADY
    # SAYS SO — it lists this function under RECURSION→PARALLEL as `WITH RECURSIVE + SUM`,
    # one of the 50-of-59 licensed lifts, with only 9 honest residue (render hylomorphisms,
    # Merkle-style folds) and this is not among them. The loop is a post-order traversal
    # assigning content-addressed surrogate ids: `sorted(obs)` + post-order is the recursive
    # walk, `node_ids.get(sig)` is a GROUP BY on the signature, `_next += 1` is DENSE_RANK over
    # the distinct signatures. Every input (`obs`, `edge`, `event`) is ALREADY IN THE STORE.
    # So the current shape pulls server-side data out to compute a fold postgres does natively,
    # then pushes the result back — and BOTH directions are transport this fix only halves.
    #
    # ⚑ The bulk path below is still correct and still worth having: it is what every write
    # site needs regardless of where the computation lives, and a lifted `INSERT … SELECT`
    # never crosses the wire at all. Fixing transport first is the reachable step; the lift is
    # the one that makes pg the CPU contender instead of a row sink. Do not close the lift on
    # the strength of this.
    #
    # ⚑ COPY CANNOT EXPRESS `ON CONFLICT`, and that is the one real constraint. So conflict-
    # tolerant writes stage into a TEMP table and INSERT … SELECT out of it — one statement,
    # server-side, conflict clause intact. That is the shape `sql_lift` calls a licensed lift
    # and it is now what actually goes over the wire.
    n = len(rows)
    if _copy_capable(cur) and n >= _COPY_MIN:
        # ⚑ `pg_temp.` QUALIFIED, BECAUSE THE SEARCH PATH IS NOT OURS. A fixture (and the
        # sandbox tenant generally) sets `search_path` to its own schema, so an unqualified
        # `_bulk_x` resolves there and the COPY raised `relation "_bulk_terms" does not exist`
        # even though CREATE TEMP TABLE had just succeeded — the table was in `pg_temp`, which
        # was not on the path. Naming the schema makes the staging table independent of
        # whatever path the caller has set, which is the only assumption a shared writer may
        # safely make about its caller.
        tmp = "pg_temp._bulk_%s" % table_name
        # ⚑ `ON COMMIT DROP` REQUIRES AN OPEN TRANSACTION AND SILENTLY DID NOTHING WITHOUT ONE.
        # Under psycopg's default autocommit=False the CREATE is its own transaction, which
        # COMMITS immediately — dropping the table before the COPY on the next line can see it.
        # The failure surfaced as `relation "_bulk_terms" does not exist` from the COPY, i.e.
        # at the SECOND statement, which is why the first two guesses chased search_path and
        # cursor identity: the error named the reader, and the defect was in the writer's
        # lifetime clause. Dropping it explicitly at the end is what the DROP below is for.
        cur.execute("CREATE TEMP TABLE %s (LIKE %s)" % (tmp, table_name))
        with cur.copy("COPY %s (%s) FROM STDIN" % (tmp, ", ".join(cols))) as cp:
            for r in rows:
                cp.write_row(r)
        cur.execute(
            "INSERT INTO %s (%s) SELECT %s FROM %s %s"
            % (table_name, ", ".join(cols), ", ".join(cols), tmp, tail)
        )
        cur.execute("DROP TABLE IF EXISTS %s" % tmp)
    elif hasattr(cur, "executemany"):
        cur.executemany(sql, rows)
    else:
        for r in rows:
            cur.execute(sql, r)
    return n


def insert_row(con, table_name, values, on_conflict="ignore"):
    """ONE row, ONE statement, values keyed BY NAME. Returns rows affected (0 or 1).

    The single-row counterpart to `upsert`'s batch — and it exists because the batch is
    where the hold lives, not because one row is tidier.

    ⚑⚑ `executemany` IS **ONE TRANSACTION OVER N ROWS**, EVEN UNDER `autocommit=True`, AND
    THAT IS THE HOLD-AND-WAIT (probed 2026-08-12: a failure at row 3 of 4 rolls back rows
    1–3; the per-row xids are shared across a batch). A core's ~10⁴ `event` index tuples are
    therefore all HELD while the writer WANTS the next one, and the insert order is
    `dec["nodes"].items()` — a decoder artifact, so two concurrent cores' orders are
    unrelated. Two writers, each holding what the other wants, in orders nothing reconciles:
    that is a `40P01`, and it was reproduced under 8 concurrent `--ingest-core --sandbox`.
    `upsert`'s own retired sort records why ORDERING it was the wrong fix — *"a global order
    makes the CYCLE unconstructible while leaving the HOLD in place"*. **One row per
    statement has no batch to hold.**

    ⚑ THE COLUMN ROSTER COMES FROM THE DECLARATION AND THE VALUES COME BY NAME, WHICH IS A
    STRENGTHENING OVER `upsert`, NOT A STYLE DIFFERENCE. `upsert` takes POSITIONAL tuples in
    declared column order, so adding a column shifts every caller's data one place and is
    caught only by a zip-arity mismatch; a name map cannot shift. An undeclared key REFUSES
    (a typo'd column would otherwise compose a syntactically valid INSERT into the wrong
    one), and a declared NOT-NULL column with no server default and no value REFUSES too —
    postgres would say the same thing, but not until the statement ran, and not naming the
    declaration it came from.

    on_conflict='ignore'   → `ON CONFLICT DO NOTHING`
    on_conflict='replace'  → `ON CONFLICT (pk) DO UPDATE SET … WHERE <row> IS DISTINCT FROM
                              <EXCLUDED row>`

    ⚑ THE `WHERE` IS THE RUNG, AND IT IS DERIVED FROM THE DECLARATION RATHER THAN NAMED.
    Ladder logic has no window between reading a contact and energising a coil: the predicate
    IS the WHERE clause, not a check performed before an action. So "has this core's decoded
    form actually changed?" is not a SELECT the writer makes and then acts on — it is a
    conjunct of the write itself, evaluated by the engine against the row it is already
    holding. An unchanged re-ingest becomes a no-op the engine decides, and the caller learns
    which happened from the returned count rather than from a prior read that could go stale
    between the two statements.

    ⚑ THIS IS STRICTLY A SUBSET OF `upsert(on_conflict='replace')`, WHICH IS WHY THE WORD
    'replace' MEANS ONE THING ACROSS BOTH. Same conflict target (the primary key), same SET
    list; the only difference is that the writes it declines to perform are exactly the ones
    that would have written the value already stored. Two spellings of one word across two
    functions is the drift this layer exists to prevent, so the guard had to be a narrowing
    of the existing meaning rather than a second one.

    ⚑ AND IT REQUIRES EVERY NON-KEY COLUMN TO HAVE AN EQUALITY OPERATOR — which is not
    universal in postgres and is the measured reason `core_decoded.dec` is `jsonb` and not
    `json`: `SELECT … WHERE a.dec IS DISTINCT FROM b.dec` over a `json` column raises
    `UndefinedFunction: operator does not exist: json = json`. A type that cannot be compared
    cannot carry a rung's predicate.
    """
    sql, params = _insert_row_sql(table_name, values, on_conflict)
    cur = con.cursor() if hasattr(con, "cursor") else con
    cur.execute(sql, params)
    # ⚑ THE COUNT IS THE OBSERVABLE, AND WITHOUT IT THE RUNG IS UNMEASURABLE. `rowcount` is
    # 1 when the row was written or genuinely updated and 0 when the `WHERE` declined it —
    # which is the ONLY way a caller can tell "already current" from "just landed" without
    # issuing the SELECT this design exists to remove.
    return cur.rowcount if getattr(cur, "rowcount", -1) >= 0 else 1


def _insert_row_sql(table_name, values, on_conflict="ignore"):
    """`(sql, params)` — the statement `insert_row` issues, built from the DECLARATION.

    ⚑⚑ SPLIT OUT SO A GUARD CAN ANCHOR ON THE COMPILED SQL, NEVER ON SOURCE TEXT. This repo
    has THREE recorded instances of a guard satisfied by the retirement comment naming the
    thing it guards, so a case asserting *"the writer emits a single-row VALUES with a
    content-conditioned WHERE"* by scanning `getsource` would pass against a body that emits
    nothing of the kind while a ⚑ block above it says the words. This returns exactly what
    will be sent, and `insert_row` has no other way to build a statement — so the string a
    case checks and the string postgres parses cannot differ.
    """
    t = MD.tables[table_name]
    declared = [c.name for c in t.columns]
    unknown = sorted(k for k in values if k not in declared)
    if unknown:
        raise ValueError(
            f"insert_row({table_name!r}): {unknown} is not a declared column. "
            f"{table_name} declares {declared}. A name that does not resolve is REFUSED "
            f"rather than dropped, because a silently ignored key writes a row missing the "
            f"fact the caller believed it had written."
        )
    missing = sorted(
        c.name
        for c in t.columns
        if not c.nullable and c.server_default is None and c.name not in values
    )
    if missing:
        raise ValueError(
            f"insert_row({table_name!r}): {missing} is declared NOT NULL with no server "
            f"default and was not supplied. Refusing here rather than letting postgres "
            f"raise, so the message names the DECLARATION the requirement comes from."
        )
    cols = [c for c in declared if c in values]
    pk = [c.name for c in t.primary_key.columns]
    if on_conflict == "ignore":
        tail = "ON CONFLICT DO NOTHING"
    elif on_conflict == "replace":
        if not pk:
            raise ValueError(
                f"insert_row(replace) needs a PRIMARY KEY as its conflict target; "
                f"{table_name} declares none"
            )
        rest = [c for c in cols if c not in pk]
        if rest:
            sets = ", ".join(f"{c} = EXCLUDED.{c}" for c in rest)
            # ⚑ A ROW CONSTRUCTOR, NOT A CONJUNCTION OF PER-COLUMN TESTS — `(a, b) IS
            # DISTINCT FROM (x, y)` is NULL-safe in both directions, where `a <> x OR b <> y`
            # evaluates to NULL (hence not-true, hence a SKIPPED update) the moment either
            # side is NULL. `core_decoded.mtime` is nullable, so this is reachable rather
            # than defensive: an unreadable `stat` writes NULL there.
            lhs = ", ".join(f"{table_name}.{c}" for c in rest)
            rhs = ", ".join(f"EXCLUDED.{c}" for c in rest)
            tail = (
                f"ON CONFLICT ({', '.join(pk)}) DO UPDATE SET {sets} "
                f"WHERE ({lhs}) IS DISTINCT FROM ({rhs})"
            )
        else:
            tail = f"ON CONFLICT ({', '.join(pk)}) DO NOTHING"
    else:
        raise ValueError(
            f"insert_row: on_conflict={on_conflict!r}; the modes are 'ignore' and 'replace'"
        )
    return (
        (f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({ph(len(cols))}) {tail}"),
        tuple(values[c] for c in cols),
    )


def apply(con, back=None, only=None):
    """Create the schema on `con`. Returns the number of statements executed.

    ⚑ THIS REPLACES `con.executescript(EVENT_SCHEMA)` / `executescript(SPPF_SCHEMA)`,
    and the method is the porting blocker, not just the strings. `executescript` is
    **sqlite3-only** — psycopg has no such method — so every DDL site would have raised
    `AttributeError` on the postgres path regardless of how good the SQL was. Executing
    statement-by-statement is what both drivers can do.

    ⚑ AND IT IS WHY THE EMITTER RETURNS A LIST rather than one blob. `executescript`
    takes a script and splits on `;`, which is a parser that does not know about
    semicolons inside string literals; a list of statements needs no such parse.

    `only` selects a tier: 'event' | 'sppf' | None (both). The two tiers are dropped and
    rebuilt at different times — `write_events` rebuilds the event tier on a schema bump,
    `project_sppf` rebuilds the projection every run — so they must be separately
    applicable, which is the one thing the two-string arrangement got right.
    """
    stmts = ddl(back) if only is None else _tier(back, only)
    n = 0
    for s in stmts:
        con.execute(s)
        n += 1
    return n


def fixture_schema(name):
    """The private SCHEMA NAME `sandbox_fixture(name)` creates — a pure function.

    ⚑⚑ EXPOSED BECAUSE THE CREATOR WAS THE ONLY THING THAT KNEW THE TARGET, AND IT KEPT
    IT.  `sandbox_fixture` created the namespace, pointed `search_path` at it and
    returned only the connection — so a caller that wants to SCHEMA-QUALIFY a statement
    (the `ddl_lifecycle` teardown, whose whole thesis is derived destruction) had no way
    to name the schema its objects live in.  Every DROP therefore went out unqualified
    and resolved through `search_path`: right by luck, not by mechanism, and `dec_val`
    exists in SIXTEEN schemas of `substrate_sandbox`.

    ⚑ AND IT IS A FUNCTION, NOT A DOCUMENTED CONVENTION.  A caller re-spelling
    `"fx_" + sanitize(name)` for itself would be a target that agrees with the creator
    by coincidence — the two would drift the first time the sanitiser changed, and the
    drift's symptom is a DROP against the wrong namespace.  `sandbox_fixture` resolves
    through this, so there is exactly one computation of the name.

    ⚑ NOT `current_schema()`, WHICH WOULD BE THE SAME AMBIGUITY ONE LAYER DOWN: that
    reads `search_path` as well, merely later and from inside the server. The
    qualification has to come from where the object was CREATED.

    ⚑ PURE — it opens no connection.  That is what lets a caller qualify its statements
    (and a case assert the qualification) with postgres unreachable.
    """
    return "fx_" + "".join(c if c.isalnum() else "_" for c in name)[:48]


def sandbox_fixture(name):
    """A sandbox connection scoped to a PRIVATE SCHEMA holding the full declared model.

    The `:memory:` replacement for suite fixtures: a namespace nobody else writes,
    rebuilt from the declaration, dropped and recreated on each call so a run never
    inherits the last one's rows. `name` identifies the fixture and must be unique across
    every suite — it becomes the schema name.

    ⚑⚑ THIS EXISTS BECAUSE `:memory:` GAVE **PRIVACY**, AND THE SANDBOX TENANT GIVES ONLY
    **MUTABILITY** (⓺, 2026-08-11). Dropping sqlite moved five suite fixtures from private
    in-memory databases to the one sandbox database, and my first two attempts substituted
    the wrong property — each failed differently, and each failure named the missing one:

      1. `sandbox_connect(reset=True)` per fixture. DROPS EVERY RELATION, so the first
         fixture left the tenant holding only the tables it needed and later suites read
         `UndefinedTable: relation "_orbit_def" does not exist` / `relation "ref" does not
         exist`. Fixed by re-applying the declaration after the reset — which fixed the
         SHAPE and not the sharing.
      2. Reset + `apply()` per fixture. `run_selftests` runs suites **CONCURRENTLY**, so
         two fixtures issued `CREATE TABLE orbit_member` against one database at the same
         moment: `UniqueViolation … Key (typname, typnamespace)=(orbit_member, 2200)
         already exists`. No discipline about what a fixture LEAVES BEHIND can fix that;
         the collision is in what they do simultaneously.

    ⚑ SO THE PROPERTY TO RESTORE IS THE NAMESPACE, AND POSTGRES SPELLS IT `CREATE SCHEMA`.
    A private schema plus a per-connection `search_path` is exactly what a private
    in-memory database was: unqualified names resolve to tables only this session sees,
    concurrent fixtures cannot collide, and the live `public` schema is never touched — so
    `reset=False`, and the suites that read real corpus rows keep reading them.

    ⚑ THE NAME IS DETERMINISTIC, NOT RANDOMISED, and that is what makes it self-cleaning.
    A random name leaks a schema per run forever; a deterministic one is `DROP … CASCADE`d
    and recreated, so the tenant holds at most one namespace per fixture no matter how
    often the suite runs.

    ⚑ AND IT IS PASSED IN RATHER THAN INFERRED FROM THE CALLING FRAME — my first cut read
    `inspect.stack()[1]`'s module `__name__`, which is correct exactly while the runner
    imports suites under their own names. `run_selftests` does not always: the suite that
    is `__main__` (or any module `inspect.getmodule` cannot resolve) collapsed to one
    fallback name, so two fixtures shared a namespace and the second `DROP SCHEMA …
    CASCADE` deleted the first's search_path out from under it — `InvalidSchemaName: no
    schema has been selected to create in`, several frames later, naming a table. A
    namespace that two callers can silently share is not a namespace; an explicit
    argument makes a collision a thing you can READ instead of one you have to reproduce.
    """
    import store

    # ⚑ THROUGH `fixture_schema`, NOT A SECOND SPELLING.  A caller qualifying its DROPs
    # must be able to name this schema, and a name computed twice is a target that
    # agrees by coincidence.
    ns = fixture_schema(name)
    con = store.sandbox_connect(reset=False)
    cur = con.cursor()
    cur.execute(f'DROP SCHEMA IF EXISTS "{ns}" CASCADE')
    cur.execute(f'CREATE SCHEMA "{ns}"')
    # ⚑ `search_path` IS PER-SESSION, WHICH IS THE WHOLE MECHANISM. It is set on THIS
    # connection only, so every unqualified name in the fixture — and in the production
    # code under test, which spells no schema anywhere — resolves inside the namespace
    # without a single call site knowing it exists.
    cur.execute(f'SET search_path TO "{ns}"')
    apply(con)
    return con


def _cli_connect(mode="ro"):
    """The store THIS invocation NAMES — `--live` or `--sandbox`, never a default.

    ⚑ ONE RESOLVER, NOT PER-DISPATCH. `--reclaim`, `--advance` and `--retype` each grew
    their own `sandbox_connect(reset=False) if "--sandbox" in sys.argv else …` line, so
    the WRITE modes honoured the flag while every READ mode silently ignored it. Measured:
    `--fibre --sandbox` reported "152 cores, every core positional" over a sandbox holding
    ONE core — the live store's answer, printed under the sandbox's question. That is the
    shape `reconstruct._cli_connect` was written to retire, reproduced here in the sibling
    module, and it is worse in a read mode than a write one: a write that hits the wrong
    tenant is loud, while a read just returns plausible rows nobody can distinguish.

    ⚑ NOT A `sandbox=` FLAG ON `store.connect()` — see `store.sandbox_connect`'s own note:
    a boolean would put the real store one argument away from a probe that drops tables.
    The choice belongs to the INVOCATION, resolved once, here.

    ⚑ `reset=False` ALWAYS. This resolver serves inspection; a resolver that could empty
    the tenant it connects to is not one a read mode may call.

    ⚑ `mode` APPLIES TO THE LIVE STORE ONLY, and that asymmetry is real rather than an
    oversight: `sandbox_connect` opens autocommit read-write because the sandbox exists
    to be mutated. So `mode="rw"` is "do not hand me a read-only LIVE connection"; it is
    not a claim that both routes enforce the same thing. `store.connect`'s own docstring
    already records that `ro` means two different guarantees across backends — this adds
    a third axis, so a caller depending on refusal must check which store it got.
    """
    # ⚑ IMPORTED HERE, LIKE EVERY SIBLING. Module-scope `store` is bound inside the
    # `__main__` block, so a module-level reference works at dispatch and raises
    # NameError from the selftest — which is precisely why this resolver had no case
    # until now: the suite could not reach it.
    # ⚑⚑ THE `else` BRANCH WAS THE SILENT DEFAULT, AND THAT IS NOW `store.tenant`'s
    # JOB.  This read `sandbox_connect(...) if "--sandbox" in sys.argv else connect(...)`
    # — correct about WHICH tenant, silent about the fact that NOBODY CHOSE.  There was
    # no `--live` spelling anywhere in the toolkit, so the absence of a flag could not be
    # distinguished from a decision to use live.  `store.TENANT_FLAGS` supplies the
    # missing half; `store.tenant` REFUSES when neither is stated — `sys.exit(2)`, not an
    # advisory. ⚑ This line read "(advisory today)" until ⟡tenant-mandatory landed on
    # 2026-08-24 and `SUBSTRATE_EXPLICIT_TENANT` stopped being consulted at all. Recorded
    # rather than silently corrected: `gate-F19` found `ratchet.store_argv` as the last
    # reader of that same deleted variable, and `run_selftests`' TENANT block as a third
    # site still promising an advisory. Three places described a behaviour the tree had
    # already dropped, which is what a parenthetical hedge costs when the hedge expires.
    #
    # ⚑ AND IT IS ONE AUTHORITY FOR THE SAME REASON THIS FUNCTION EXISTS: the note above
    # records four tools growing per-dispatch sandbox checks independently.  A resolver per
    # module is the same defect one layer up.
    #
    # ⚑⚑ THIS SAID "`sppf_db` still has FOURTEEN" AND A COUNT WAS THE WRONG THING TO WRITE.
    # It was 11 when measured (2026-08-21), of which 6 are now consolidated — so the sentence
    # was stale in the tree AND would go stale again the moment anyone touched the file.
    # Replacing 14 with 6 is the same defect one iteration on; the same argument CLAUDE.md
    # makes about memory caps applies to censuses: **do not quote the figure, name the
    # partition and point at the tool that re-derives it.**
    #
    #   `pycodemod --guarded sandbox_connect scripts/sppf_db.py` splits them by SHAPE:
    #     UNDER `__main__` — a dispatch reading `sys.argv` inline. These are the drift this
    #       resolver exists to absorb, and consolidating them onto `tenant(...)` is paydown.
    #     AT TOP LEVEL — a library function taking `sandbox=` as a PARAMETER, its caller
    #       supplying the argv test. ⚑ THESE ARE ALREADY CORRECT AND MUST NOT BE "FIXED":
    #       routing a library call through an argv-reading resolver would make it
    #       argv-dependent, which is strictly worse than a parameter. A count of "N tenant
    #       checks" hides that split and invites paying down the half that is right.
    #
    # ⚑ THE PARTITION IS THE FACT; THE NUMBER IS A READING OF IT AT ONE MOMENT.
    import store as _s

    return _s.tenant(mode=mode, label="schema")
