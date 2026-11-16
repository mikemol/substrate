# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The store-shape QUESTIONS the CLI renders — lifted out of the dispatch so cases can drive them.

⚑⚑ SPLIT OUT OF `schema.py` 2026-08-11 (⟡split-1200), AND THE SEAM IS ONE `schema.py` ALREADY
TOOK ONCE AND NAMED. `positional`'s own docstring is the argument, written before this move:
*"LIFTED OUT OF THE CLI SO IT CAN BE TESTED. Inline in a `--fibre` branch, the one judgement
the materialization depends on was reachable only by running a query against the live store —
so no case could drive it, and a wrong predicate would read as a clean measurement."* Every
function here is that same shape: a question about the store's SHAPE, separable from the block
that prints the answer, and therefore drivable by a case.

    census(con)              row count per declared relation, in tier order  (`--census`)
    core_path(core_id)       a surrogate id → the path it names, REFUSING on a miss
    core_id_for(path)        the inverse — minting one if this store has not seen it
    classify_hole(n_names)   'empty' | 'hole' | 'unclassified'                (`--holes`)
    positional(lo,hi,n,d)    is this core's fibre POSITIONAL? → (ok, gaps, dups) (`--fibre`)
    _dialects_differ()       does the emitter actually honour its dialect argument?

⚑ THE ARROW: THIS READS `schema_rows` AND `schema_decl`, AND NOTHING READS IT BACK. The
re-export chain `schema_decl ← schema_rows ← schema_queue ← schema` has one direction, and the
first cut of THAT split failed with `ImportError: cannot import name '_require_pg'` against a
half-built module because a supplier imported its consumer. This module sits beside
`schema_queue` on the same rung: it reaches down to the row helpers and the declaration, and
`schema.py` reaches up to it. Nothing here calls back into `schema`.

⚑ AND IT IS NOT THE QUEUE TIER, WHICH IS WHY IT IS NOT IN `schema_queue`. That module's
membership test is exact and structural — *"every function here is POSTGRES-ONLY and every one
of them opens by calling `_require_pg`"*. None of these do. `census` reports a missing relation
as `-` on either backend; `classify_hole` and `positional` are pure; `core_path` is one keyed
SELECT. Filing them by topic ("they're all diagnostics") would have put a backend-neutral
function behind a postgres gate, which is the kind of membership drift the `_require_pg`
predicate exists to make impossible.

⚑ `_dialects_differ` IS RE-EXPORTED BY NAME, NOT BY THE STAR. `import *` skips a leading
underscore by construction — the defect that silently removed `schema._node`, `_unit`,
`_unit_cod` and `_orbit_def` from the re-export surface while `--selftest` still read 123/123,
because most cases never touch most names. `schema_selftest` imports `_dialects_differ`
explicitly from `schema`, so `schema.py` names it explicitly beside its star.
"""

from schema_decl import CreateTable
from schema_rows import _cli_connect, _TIERS, execute, ph, relations, rows, scalar


def _dialects_differ():
    """Does the emitter compile against the POSTGRES dialect specifically?

    ⚑⚑ THIS PROBE ASKED A COMPARATIVE QUESTION AND THERE IS NOTHING LEFT TO COMPARE (⓺,
    2026-08-11). It rendered a `DateTime` column under both dialects and returned `a != b`
    — sqlite says DATETIME, postgres says TIMESTAMP — because, as its own note recorded,
    *"every column in this model is `Text` or `Integer`, and both dialects render those
    identically, so the production DDL is byte-identical under sqlite and postgres and
    comparing it proves nothing about whether `dialect=` was consulted at all. A guard
    that cannot fail is decoration."*

    ⚑ THAT REASONING IS WHY IT IS REWRITTEN RATHER THAN DELETED, AND WHY IT KEEPS THE SAME
    PROBE TYPE. The property still worth guarding is that the emitter consults a dialect at
    all — an emitter that ignored `dialect=` and fell back to SQLAlchemy's generic
    compiler would render `DATETIME`, not `TIMESTAMP`. So the discriminator is unchanged;
    only the comparison collapsed, from "the two disagree" to "the one is postgres". A
    same-name predicate now answering a one-sided question is worth stating plainly:
    consumers read the NAME, and the name is now a slight overclaim kept for continuity.
    """
    from sqlalchemy import MetaData as _MD2, Table as _T2, Column as _C2, DateTime
    import store

    md = _MD2()
    probe = _T2("_dialect_probe", md, _C2("t", DateTime))
    return "TIMESTAMP" in str(CreateTable(probe).compile(dialect=store.dialect("postgres")))


def census_shape(con=None):
    """`[(tier, name, present)]` — WHICH declared relations exist, in tier order. NO COUNTS.

    ⚑⚑⚑ THE STRUCTURAL HALF OF `census`, SPLIT OUT BECAUSE COUNTING TO ANSWER A STRUCTURAL
    QUESTION IS CORPUS-SCALE WORK FOR A NAME-SCALE ANSWER. Measured 2026-08-23: the schema
    selftest called `census(_con)` to assert only *"the census covers every declared
    relation"* and *"each row is tagged with its tier"* — two questions about NAMES — and
    paid `SELECT count(*)` over every relation to get them, including `obs` (132.3M rows)
    and `edge` (142.4M rows). Against a store under concurrent build load that single case
    ran **24m24s without completing** and timed the whole suite out THREE times, so the
    suite that gates this module could not be run at all.

    ⚑ THIS IS THE DEFECT `--holes`' OWN DOCSTRING NAMES — *"a query doing corpus-scale work
    for a core-scale answer is the restructure candidate"* — and it was sitting inside the
    census that note was written about. `relations(con)` is a catalogue read; membership in
    it is the entire fact both selftest cases need.

    ⚑ `present` IS A BOOLEAN AND MISSING IS STILL ITS OWN VERDICT. The absent/empty
    distinction `census` preserves as `None`-vs-`0` is preserved here as `False`-vs-`True`:
    this reports whether a relation EXISTS, and says nothing about whether it holds rows.
    A caller wanting "applied but empty" wants `census`, which counts.
    """
    live = relations(con if con is not None else _cli_connect())
    return [
        (tier, getattr(t, "name", t), getattr(t, "name", t) in live)
        for tier, tables in _TIERS.items()
        for t in tables
    ]


def census(con=None):
    """Row count for every declared relation, in tier order — the store's OWN answer to
    "how full is it".

    ⚑ FOR *WHICH* RELATIONS EXIST, USE `census_shape` — it answers from the catalogue alone.
    This mode COUNTS, which on this store means scanning `obs`/`edge` (275M rows between
    them); reach for it only when the counts are the answer, never to enumerate names.

    ⚑ THIS EXISTS BECAUSE THE QUESTION HAD NO MODE. Asking "did the ingest land" was a
    `python3 -c` looping `SELECT count(*)` over a table list I typed from memory — a list
    that drifts from `_TIERS` the moment a table is added, and judgement living in a turn
    rather than in a program. The relation set comes from `_TIERS`, so a new table is
    censused with no edit here.

    ⚑ AND A MISSING RELATION IS ITS OWN VERDICT, NOT A ZERO. A tier that was never applied
    and a tier that is applied-but-empty are different facts; collapsing them into `0` is
    exactly the "absent read as failed" the observability rule forbids. Missing rows read
    `-` and are counted separately.
    """
    import store as _store

    close = con is None
    if close:
        con = _cli_connect()
    live = relations(con)
    # ⚑⚑⚑ FROM THE CATALOGUE, NOT FROM `count(*)` (operator, 2026-08-23: *"Tables have
    # metadata. That's good enough if the metadata is reasonably fresh."*). Postgres already
    # MAINTAINS a row count per relation; scanning 275M rows across `obs`+`edge` to re-derive
    # a number the server is tracking anyway is the corpus-scale-for-a-cheap-answer defect
    # `--holes`' docstring names. One catalogue read replaces N sequential scans.
    #
    # ⚑⚑ `n_live_tup`, NOT `reltuples`, AND THE DIFFERENCE IS MEASURABLE HERE. `reltuples` is
    # the PLANNER's estimate, refreshed only by ANALYZE/autoanalyze, so it lags a live ingest:
    # measured 2026-08-23 mid-build, `obs` read 138,271,904 (reltuples) vs 141,072,408
    # (n_live_tup) — 2% stale — and `path_text` read 21,786 vs 22,272. That stale 21,786 is
    # EXACTLY the number a peer and I spent three messages disputing while the store held
    # 22,272. `n_live_tup` is maintained continuously by the stats collector, so it tracks
    # the ingest this mode exists to watch.
    #
    # ⚑ IT IS AN ESTIMATE AND THE MODE MUST SAY SO — a stats reset zeroes `n_live_tup` while
    # the rows remain, so a caller reading it as exact would report an empty store. The
    # report labels the figure; `count(*)` remains the answer when exactness is the question
    # (`--uniqueness` and `--holes` both still count, because a discrepancy IS their subject).
    est = {}
    for r in rows(
        con,
        "SELECT relname, n_live_tup FROM pg_stat_user_tables "
        "WHERE schemaname NOT IN ('pg_catalog','information_schema')",
    ):
        est[r["relname"]] = r["n_live_tup"]
    out = []
    for tier, tables in _TIERS.items():
        for t in tables:
            name = getattr(t, "name", t)
            # ⚑ ABSENT STAYS ABSENT. A relation not in the catalogue reads `None` exactly as
            # before — "never applied" and "applied but empty" remain different facts, and a
            # relation present but missing from the stats view reads 0, not None.
            out.append((tier, name, None if name not in live else (est.get(name) or 0)))
    return out


def core_path(core_id, con):
    """A core_id rendered as the PATH it names — by LOOKUP, refusing on a miss.

    ⚑ THE STORE PRINTS OPAQUE IDS AND MAKES THE READER DECODE THEM. `--holes` listed sixteen
    blobs; the fact that ALL SIXTEEN are `Algebra/F2/*` — a contiguous alphabetical run, i.e.
    one interrupted ingest rather than sixteen per-core failures — was invisible until decoded
    by hand. That is reasoning in the turn: the pattern is in the data and the tool refused to
    show it. Rendering the path is therefore not cosmetic.

    ⚑⚑ AND THE OLD FALLBACK WAS THE MOST DANGEROUS LINE IN THIS MODULE UNDER ⓝ P4. It was
    `except: return core_id`, justified as *"a core_id that is not base64 is a fact worth
    seeing, not a crash"* — sound while ids WERE base64. Once `core_id` is a surrogate, EVERY
    id stops decoding, so that fallback would return the raw id for all of them and eight
    callers would print opaque blobs while reporting success. **A silent wrong value, at
    scale, in exactly the surface built to make a pattern visible.**

    ⚑ AND ONE CALLER IS SEMANTIC, NOT DISPLAY: `schema --holes` hands the decoded path to
    `agda_defs` via `_defines(p)`. A raw id there does not misrender a report — it classifies
    every hole wrongly and the classification is what the mode exists to produce.

    ⚑ SO IT REFUSES (user's call, 2026-08-11): a miss raises rather than degrading, because
    the failure this replaces was invisible by construction and a loud one is not.

    ⚑⚑ AND `con` IS REQUIRED, BECAUSE THE `con=None` DEFAULT REPLACED ONE SILENT-WRONG-ANSWER
    WITH ANOTHER — MEASURED, WITHIN THE HOUR. I made it optional "to keep the signature
    back-compatible for callers that already hold one", which is precisely backwards: the
    callers that hold one are the ones that must pass it. `scope_store._selftest` sets
    `SUBSTRATE_SANDBOX=1`, holds a SANDBOX connection, and called `core_path(cid)` — so the
    default resolved `_cli_connect()` to the **LIVE** store, whose `core_fp` predates the
    surrogate scheme, and the read died on a column that exists in the tenant the caller
    actually held. A broad `except` turned that into `0/0` and the suite reported VACUOUS.

    ⚑ THAT IS THE `wrong-tenant-read-is-silent` CLASS, WHICH THIS REPO ALREADY RECORDS — and I
    introduced it WHILE FIXING the silent-decode version of the same defect, in the same
    function, in one edit. A defaulted connection is not a convenience; it is a second,
    invisible tenant resolver competing with the caller's.

    ⚑ REQUIRED RATHER THAN REFUSING-ON-None, so the omission is a TypeError at the call site
    instead of an exception at runtime. The failure this guards is a wrong ANSWER, and the
    earliest place to catch it is where the connection was available and not passed.
    """
    # ⚑ READS `terms`, THE SAME AUTHORITY `core_id_for` WRITES (ⓟ). It read `core_fp.path` —
    # a column I added — while the path was ALREADY interned in `terms` under exactly this id,
    # because `cid = tid(relpath)`. Two copies of one fact, and the reader consulting the copy
    # rather than the original is how they drift apart unnoticed.
    #
    # ⚑ `core_fp.path` WAS THEREFORE REDUNDANT, AND THIS NOTE USED TO SAY IT WAS "LEFT IN
    # PLACE, DELIBERATELY UNUSED FOR NOW — ripping a column out mid-migration is churn against
    # a store this arc has not yet re-ingested." IT IS NOW GONE from the declaration, so the
    # paragraph was stale in the direction that misleads: it told the next reader a duplicate
    # still existed and was safe to read.
    #
    # ⚑ AND A STALE "it is still there" NOTE IS WORSE THAN NO NOTE, MEASURED. `scope_store`
    # kept reading `core_fp.path` on this reasoning and broke the moment the SANDBOX was
    # re-ingested from the current declaration (`UndefinedColumn`). The column's removal and
    # its last reader's repair were two edits apart, with this paragraph in between saying the
    # first had not happened.
    got = scalar(con, "SELECT text FROM terms WHERE term_id = %s" % ph(), (core_id,))
    if got is None:
        raise LookupError(
            "core_id %r resolves to no path in `terms` — the id is unknown to this store. "
            "Under surrogate ids a core_id carries no path of its own, so an unresolvable id "
            "is a real finding (wrong tenant, un-ingested core, or a stale id from a previous "
            "scheme) and must not be rendered as though it were the path." % (core_id,)
        )
    return got


def uniqueness(con):
    """Does the live data satisfy every UNIQUE index the declaration names? — the pre-flight
    for adding one to a populated store.

    Returns one row per declared unique index: `{index, table, cols, present, dup_groups}`.
    `present=False` means the RELATION is absent from this tenant — a fact about the tenant,
    reported as its own state rather than folded into `dup_groups=0`.

    ⚑⚑ THIS MODE EXISTS BECAUSE THE QUESTION HAD NO READER AND THE ANSWER GATES A WRITE.
    `ix_pathtext_text` was added to `INDEXES` on 2026-08-12, and `CreateIndex(…, unique=True)`
    against a table that already holds a duplicate does not warn — it RAISES, from inside
    `apply(con, only="event")`, which is the first statement of every ingest entry point. So
    "would this declaration apply to that tenant" is a precondition for a schema change, and
    the only way to ask it was a hand-written `GROUP BY … HAVING count(*)>1` per index.

    ⚑ IT ASKS THE DECLARATION, NOT A LIST OF INDEXES SOMEONE TYPED. `INDEXES` is the authority
    and the roster is derived from it, so an index added tomorrow is checked tomorrow with no
    edit here — the same reason `_TIERS` is derived and `_PROJ_TABLES` was a defect.

    ⚑ AND A DUPLICATE IS REPORTED AS A COUNT OF *GROUPS*, NOT OF ROWS. "3 duplicate rows" is
    ambiguous between one key repeated three times and three keys repeated twice; the group
    count is what `CREATE UNIQUE INDEX` actually refuses on, and it is the number that goes to
    zero when the data is repaired.
    """
    from schema_decl import INDEXES

    have = set(relations(con))
    out = []
    for ix in INDEXES:
        if not ix.unique:
            continue
        tbl = ix.table.name
        cols = [c.name for c in ix.expressions]
        row = {
            "index": ix.name,
            "table": tbl,
            "cols": cols,
            "present": tbl in have,
            "dup_groups": None,
        }
        if row["present"]:
            row["dup_groups"] = scalar(
                con,
                "SELECT count(*) FROM (SELECT 1 FROM %s GROUP BY %s HAVING count(*) > 1)"
                " AS d" % (tbl, ", ".join(cols)),
            )
        out.append(row)
    return out


# ⚑ THE INTERNING DICTIONARIES AND THEIR ID COLUMNS — the two relations whose key is a
# function of their content. A leading-underscore-free constant so `schema`'s star re-export
# carries it; `intern` refuses any table not named here rather than guessing a column.
ID_COLUMNS = {"terms": "term_id", "path_text": "path_id"}


def intern(con, table, text):
    """Intern `text` and return its id — a PURE FUNCTION of the text, plus an idempotent write.

    `table` is `'terms'` (→ `term_id`) or `'path_text'` (→ `path_id`); `ID_COLUMNS` is the
    authority.

    ⚑⚑ THE ID IS DERIVED FROM THE CONTENT, NOT ALLOCATED — and that dissolves the race rather
    than surviving it. **ALLOCATION IS THE THING THAT REQUIRES COORDINATION BETWEEN WRITERS.**
    Every earlier spelling allocated: this function's ancestor computed `max(id)+1` in SQL,
    `sppf_decode._mk_interners` did it in a python counter seeded once at load, and an
    intermediate cut of THIS function drew from a postgres SEQUENCE. All three are the shape
    `obs.seq`'s retirement note forbade for a DIFFERENT column — *"STORE-ASSIGNED, NEVER
    CLIENT-ASSIGNED. A counter maintained by the writer collides or gaps under concurrent
    ingests"* — and the sequence merely moved the counter to an authority that cannot collide.

    ⚑⚑ THE SEQUENCE WAS BUILT, MEASURED, MUTATION-TESTED AND THEN REPLACED, AND THE REASON IS
    WORTH KEEPING (user, 2026-08-12: *"I really feel like it's going about this exactly the
    wrong way, trying to sort things. It's trying to deal with race conditions when that's what
    content-addressing is for."*). A sequence is CORRECT: two writers interning the same text
    allocate different numbers, one loses on `UNIQUE(text)`, and the loser re-reads to discover
    the winner's id. But that is a reconciliation dance — an extra round trip, a gapped
    sequence, and an id nobody can compute without asking. Derivation has no such step.

    ⚑ **INTERNING *IS* CONTENT-ADDRESSING.** "The same content gets the same handle" was being
    achieved by a UNIQUE index plus a read-then-write, when it could be achieved by the handle
    BEING a function of the content. The store already does exactly this next door:
    `event.ekey` is a content address and is that table's PRIMARY KEY. A leaf dictionary keyed
    by a counter was the odd one out.

    ⚑ THE WIDTH OBJECTION IS REAL AND WAS MEASURED RATHER THAN ASSERTED. A full `_b64` address
    is bijective and therefore grows with what it names (avg 16.4 / max 60 chars), and on the
    LEADING COLUMN of the store's dominant indexes that costs **2.39×** — 25,722,880 B →
    61,562,880 B over 184k obs / 184k edge / 258k obs_node; on the live store those indexes are
    3.19 GB of 4.01 GB at 5% corpus ingest. `_addr`'s fixed 11 characters cost **1.07×**
    (27,402,240 B), with three of the four indexes coming out BYTE-IDENTICAL to the 4-character
    surrogate. So the objection that motivated allocation does not reach a NARROW derived id —
    but only a measurement could say that, and the first version of this docstring asserted the
    opposite from a brief.

    ⚑⚑ AND THE TWO CALLERS FAILED DIFFERENTLY, WHICH IS WHY ONE OF THEM WENT UNNOTICED FOR
    THE WHOLE ARC. MEASURED (2026-08-12, 8 concurrent `--ingest-core --sandbox` processes):
    `core_id_for`'s `ON CONFLICT (text)` names the wrong constraint for a `term_id` clash, so
    it RAISED `UniqueViolation … "terms_pkey"` in 4 of 8 processes — loud, and the half the
    brief knew about. `_mk_interners` wrote through `upsert(on_conflict="ignore")`, which
    compiles to `ON CONFLICT DO NOTHING` with NO target: a second run had **all 8 processes
    exit 0** while leaving **21,840 rows whose `ctor_id` resolves to another term's text** and
    288 texts interned-but-absent. `DANGLING event.ctor_id → terms: 0` — nothing in the schema
    can see it. **A mis-targeted conflict clause is the benign failure; an untargeted one is a
    wrong answer with exit code 0.**

    ⚑ IDEMPOTENT BY THE UNIQUE-ON-CONTENT INDEX, NOT BY A CHECK — `ix_terms_text` /
    `ix_pathtext_text`. `ix_pathtext_text` did not exist until this change; `path_text` was an
    interning table with NO interning key, so `pid` could not name a content arbiter at all and
    the python `paths_map` had been standing in for the index. An invariant enforced by the
    writer's memory instead of by the store holds precisely until a second writer exists.

    ⚑ THERE IS NO FAST PATH BECAUSE THERE IS NO SLOW PATH. An earlier cut opened with
    `SELECT id FROM t WHERE text = …` and justified it: *"interning is overwhelmingly a HIT, so
    paying a nextval and a dead tuple per lookup would burn the sequence at the rate of the
    corpus rather than of its vocabulary."* True of an allocated id and MOOT for a derived one —
    the hit costs nothing to compute, and the caller's in-memory map already absorbs the repeat.

    ⚑⚑ THE `con.commit()` IS A BEHAVIOUR CHANGE FOR `_mk_interners` AND IT IS NAMED RATHER THAN
    ELIDED. `core_id_for` always committed here; `_mk_interners` did not, so on the LIVE store
    (`store.connect` is NOT autocommit — only `sandbox_connect` is) a miss now commits the
    caller's in-flight work. It is kept because it is what keeps an intern TRANSACTION SHORT:
    an uncommitted intern holds the unique index against every other session that wants the
    same text, which converts the interner into a cross-process serialisation point and
    re-opens a deadlock window between two writers each holding what the other wants.

    ⚑ THE EARLY COMMIT IS SAFE FOR THE INGEST BECAUSE OF WHERE INTERNING SITS. `_insert_decoded`
    does ALL of a core's interning BEFORE any of its `upsert`s, so a commit during interning
    commits only PREVIOUS cores' complete row sets — and `core_fp`, the completion claim, is
    written last. The tier is append-only and the loop resumes from the store, so a partial
    window is a non-event. It is NOT free for `project_sppf`'s non-additive path, which DROPs
    before rebuilding: a commit mid-rebuild makes a partial projection visible. That is F8's
    hazard, not a new one, and it is why the projection is the thing that must not be run
    against a drained tier in the first place.
    """
    import os as _os
    import sys as _sys

    _sys.path.insert(
        0,
        _os.path.join(
            _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))),
            "scripts",
        ),
    )
    from _content_addr import _addr

    col = ID_COLUMNS.get(table)
    if col is None:
        # ⚑ REFUSE AN UNDECLARED TABLE rather than guessing a column name. A typo'd table
        # would otherwise compose a syntactically valid INSERT against the wrong relation.
        raise ValueError(
            "intern(): %r is not an interning dictionary; known: %s" % (table, sorted(ID_COLUMNS))
        )
    tid = _addr(text)
    # ⚑⚑ NO SELECT, NO nextval, NO RE-READ — THE ID IS A PURE FUNCTION OF THE TEXT. Every
    # earlier spelling had to ASK the store what the id was, because the id was allocated:
    # `SELECT`-then-`INSERT`-then-`SELECT`-again under a race. A derived id is known before the
    # statement runs, so the only thing left to do is make the row exist, and that is
    # idempotent. This is the whole content of the fix; the sequence it replaced merely
    # SURVIVED the race, one round-trip at a time.
    #
    # ⚑ `ON CONFLICT (text)` IS NOW EXACTLY THE RIGHT CLAUSE RATHER THAN A PARTIAL ONE. Under
    # allocation it named one of two constraints and left the other — the PRIMARY KEY, the one
    # a race actually hit — uncovered, which is what made `core_id_for` raise and
    # `_mk_interners` (via untargeted `DO NOTHING`) corrupt silently. Under derivation the two
    # constraints agree by construction: same text ⇒ same id, so a duplicate conflicts on the
    # arbiter and takes the DO-NOTHING path without ever reaching the PK.
    #
    # ⚑⚑ AND A GENUINE COLLISION RAISES, WHICH IS WHY THIS IS DETECTION AND NOT AN ASSUMPTION.
    # DIFFERENT text hashing to the same 64 bits finds NO conflict on the named arbiter, so the
    # insert proceeds and violates `terms_pkey` — which `ON CONFLICT (text)` does not cover.
    # `psycopg.errors.UniqueViolation` on the PK is therefore the collision alarm, and it is the
    # same signal the ALLOCATED scheme produced for its (routine, expected) collisions. Here it
    # can only mean the one thing.
    execute(
        con,
        "INSERT INTO %s (%s, text) VALUES (%s, %s) ON CONFLICT (text) DO NOTHING"
        % (table, col, ph(), ph()),
        (tid, text),
    )
    con.commit()
    return tid


def core_id_for(path, con):
    """The surrogate id for a relpath — the relpath's TERM id, interned in `terms`.

    ⚑ IT DELEGATES TO `intern` (⑸, 2026-08-12) AND HAS NO MINT OF ITS OWN. A core's id IS the
    term id of its relpath, so "mint a core id" was never a second capability — it was the
    general interner with one argument fixed, and keeping a separate body is what let the two
    diverge on the one line that mattered (the conflict target).

    ⚑⚑ THIS MINTED A PARALLEL SEQUENCE AND THAT WAS THE DEFECT (ⓟ). The first version drew
    from `core_fp` (`max(core_id)+1`), giving ONE id TWO AUTHORITIES: the ingest writes
    `cid = tid(relpath)` — the relpath interned as a TERM — while this handed out a different
    number. `obs.core_id` and `core_fp.core_id` would then disagree for the same core.

    ⚑ AND IT HID BECAUSE NOTHING JOINS THEM. `--triage` read 177,397 EXACT throughout, since
    reconstruction never crosses that seam; a split authority is invisible until something
    does. That is the shape, not a near-miss.

    ⚑ THE REUSE-SEARCH SHOULD HAVE FIRED AND DID NOT. `core_id` was ALREADY an interned term
    id — `_b64(relpath)` was simply what the OLD `tid` returned, so the id merely LOOKED
    derived. One `--binding cid` would have shown `tid(relpath)` and reshaped the whole item.
    This is the one piece of the migration built before measuring what existed.

    ⚑ SO IT INTERNS INTO `terms`, WHERE THE PATH ALREADY LIVES, and `ix_terms_text` is the
    interning key — the same unique-on-content index that makes `tid` idempotent. Same table,
    same rule, one authority.

    ⚑⚑ THIS NAME WAS ALREADY CALLED AND HAD **ZERO DEFINITIONS** — `reconstruct.py:860` reads
    `_schema.core_id_for(path) if hasattr(_schema, "core_id_for") else None`, so the `hasattr`
    was ALWAYS false and the call ALWAYS fell through to an inline `b64encode`. A dead branch
    guarding a hand-rolled encoder, which is precisely the seam a surrogate scheme needs, left
    unbuilt. Building it retires the fallback rather than adding a parallel one.

    ⚑ IDEMPOTENT BY THE UNIQUE INDEX, NOT BY A CHECK. `ix_corefp_path` makes the path the
    interning key, so a re-ingested core resolves to the id it already had. Without that a
    second ingest would mint a second id and split one core's rows across both — undetectable
    from either half, and the exact property that makes `ON CONFLICT DO NOTHING` correct
    everywhere else in this store.

    ⚑ AND IT PERSISTS THE ID IN THE SAME STATEMENT THAT MINTS IT. A version that computed
    `max(core_id)+1` and left the caller to INSERT is check-then-act on shared state — two
    concurrent ingests read the same max and mint the same id. `INSERT … ON CONFLICT (path) DO
    NOTHING` followed by a re-SELECT is correct under a race in both directions: the loser's
    insert is discarded and the re-SELECT returns the WINNER's id, so both callers agree.
    `make ingest -j` runs exactly this concurrently, so it is not a hypothetical.

    ⚑⚑ AND THAT PARAGRAPH WAS HALF RIGHT, WHICH IS WHY IT SURVIVES VERBATIM RATHER THAN BEING
    CORRECTED AWAY. The `ON CONFLICT (text)` + re-SELECT pair IS the correct convergence
    argument — it is what `intern` now does. What it missed is that the value being inserted
    was still a client-computed `max+1`, so the OTHER key could clash, and the clause named a
    constraint that clash is not on. **The convergence proof was about the text and the defect
    was in the id**: a correct argument about the wrong column, which is the strongest reason
    to keep it beside the fix.

    ⚑ THE MINT THAT STOOD HERE — REPLACED 2026-08-12 (⑸). It read:

        execute(con,
                "INSERT INTO terms (term_id, text) "
                "SELECT coalesce(max(term_id::bigint), 0) + 1, %s FROM terms "
                "ON CONFLICT (text) DO NOTHING" % ph(), (path,))

    MEASURED failing: `psycopg.errors.UniqueViolation: duplicate key value violates unique
    constraint "terms_pkey"  DETAIL: Key (term_id)=(1749) already exists`, 4 of 8 concurrent
    `--ingest-core --sandbox` processes.
    """
    return intern(con, "terms", path)


def classify_hole(n_names):
    """A fingerprinted core with no obs rows: 'empty' | 'hole' | 'unclassified'.

    ⚑ THE TWO OUTCOMES ARE OPPOSITE VERDICTS ON THE SAME OBSERVATION. Zero rows from a
    module that DEFINES NOTHING means the ingest did its job; zero rows from a module that
    defines names means it did not. Reporting them as one population is how I read all 16
    as an interrupted ingest — the alphabetical clustering (15 of 16 under `Algebra/F2/`)
    fit that story, and measuring refuted it: every one is empty.

    ⚑ `None` IS 'UNCLASSIFIED', NEVER 'EMPTY'. If `agda_defs` cannot be asked, that is a
    fact about the METHOD; folding it into the benign bucket would report an unmeasured
    core as a clean one, which is the absent-read-as-passing collapse.
    """
    if n_names is None:
        return "unclassified"
    return "empty" if n_names == 0 else "hole"


def positional(lo, hi, n, distinct_lid):
    """Can this core's fibre be stored POSITIONALLY? → (ok, gaps, dups).

    ⚑ LIFTED OUT OF THE CLI SO IT CAN BE TESTED. Inline in a `--fibre` branch, the one
    judgement the materialization depends on was reachable only by running a query against
    the live store — so no case could drive it, and a wrong predicate would read as a clean
    measurement. This is the shape `check_snapshot_guard` and the 6c `expectedFailure` both
    shipped: a guard that validates the population it defines.

    ⚑ GAPS AND DUPS ARE SEPARATE OUTPUTS BECAUSE THEY FAIL DIFFERENTLY. A gap leaves an
    index with no ekey (the array needs a hole); a dup gives one index two ekeys (the array
    silently drops one — the same collapse `_node` makes, which is what the residue exists
    to undo). A single boolean cannot say which, so it cannot say what to do.
    """
    if n == 0:
        return (True, 0, 0)  # vacuously positional: no rows, no holes
    span = (hi - lo + 1) if hi is not None else 0
    gaps = span - distinct_lid
    dups = n - distinct_lid
    return (gaps == 0 and dups == 0 and lo == 0, gaps, dups)


# ══ the REPORTS — the same seam, one step further out ═══════════════════════════════════
#
# ⚑⚑ THESE SIX WERE THE BODIES OF `schema.py`'s `--spread` / `--arity` / `--nullity` /
# `--sample` / `--fibre` / `--growth` DISPATCH BLOCKS, AND THE CUT IS THE ONE `positional`
# ARGUED FOR, EXTENDED FROM THE PREDICATE TO THE RENDERING. Each is READ-ONLY, each asks the
# store one shape question and prints the answer, and each returns an exit code so the
# dispatch stays a dispatch: parse the argument, call, exit.
#
# ⚑ THE ⚑ NOTES CAME WITH THEM BECAUSE THEY ARE ABOUT WHAT THE NUMBERS MEAN, NOT ABOUT THE
# `sys.argv` PARSE. *"ARITY IS PER-TERM AND MUST COME FROM `edge`, NOT `node_child`"*,
# *"NULL AND EMPTY-STRING ARE COUNTED SEPARATELY"*, *"THE SPREAD IS THE POINT"* — every one
# of those annotates the computation. That is the test that decided WHICH blocks moved: the
# admin modes' notes (`--advance`'s defaulted `kind`, `--retype`'s `strict=True`,
# `--reclaim`'s never-passed connection) annotate the CALL the dispatch makes, so they and
# their blocks stayed in `schema.py` where the call is.
#
# ⚑ AND `--holes` DID NOT MOVE, THOUGH IT IS THE SAME SHAPE. `schema_selftest` drives it by
# SLICING `getsource(schema)` between `'if "--holes" in sys.argv:'` and `'if "--fibre"'` and
# asserting `"*.agdai"`, `"PARTIAL INGEST"` and `"on_disk"` appear in that slice. Moving the
# body would leave the guard scanning a file that no longer contains what it polices —
# passing by measuring NOTHING, the exact failure it exists to catch. The exception is
# recorded here as well as there, because a layout whose one exception is enforced by a
# string slice in another file is otherwise invisible to whoever edits next.


def census_report(sandbox=False, con=None):
    """`--census` — the row-count table plus its tenant footer. Returns an exit code.

    ⚑ `sandbox` IS A PARAMETER, NOT A `sys.argv` READ, AND THAT IS THE POINT OF LIFTING IT.
    The footer's whole job is to name the tenant the ROWS came from; a function that consults
    the ambient argv could not be driven by a case with the flag set either way, which is the
    same untestability `positional` was lifted out of the CLI to escape.
    """
    import store

    rs = census(con)
    present = [(t, n, c) for t, n, c in rs if c is not None]
    tier = None
    for t, n, c in rs:
        if t != tier:
            tier = t
            print("\n%s" % tier)
        print("  %-24s %s" % (n, "-" if c is None else format(c, ",")))
    # ⚑ THE DSN MUST DESCRIBE THE TENANT THE ROWS CAME FROM. This printed `store.dsn()`
    # unconditionally — the LIVE dsn — so after the routing fix the COUNTS were the
    # sandbox's and the LABEL still read `dbname: substrate`. That is the wrong-tenant
    # hazard inverted: previously the label was right and the data wrong; a footer that
    # can disagree with its own table is the worse of the two, because the disagreement
    # is invisible unless you already know the answer.
    # ⚑ THE FIGURES ARE LABELLED ESTIMATES, BECAUSE THEY ARE. `census` reads `n_live_tup`
    # from the catalogue rather than scanning; that is what makes this mode answerable on a
    # 275M-row store during a build, and a reader who takes it for an exact count would
    # mis-report a store whose stats were just reset (rows present, `n_live_tup` zeroed).
    # Naming the source is what keeps "the store is empty" and "the collector was reset"
    # distinguishable — the same absent-vs-zero discipline the `-` rows above carry.
    print(
        "\n%d of %d relations present (%s: %s); ~%s rows total"
        % (
            len(present),
            len(rs),
            store.backend(),
            # ⚑ REDACTED: this footer printed the live password on the first successful
            # connect after the store gained TCP auth (A193). See `store.redacted_dsn`.
            store.redacted_dsn(store.sandbox_dsn() if sandbox else store.dsn()),
            format(sum(c for _, _, c in present), ","),
        )
    )
    print(
        "  ⚑ counts are LIVE-TUPLE ESTIMATES (pg_stat_user_tables.n_live_tup), not "
        "count(*) — maintained by the stats collector, so they track an in-flight ingest\n"
        "    but read 0 after a stats reset. For an exact figure on one relation: "
        "--nullity <rel>."
    )
    return 0


def declared_indexes(con):
    """Ⓢ1 — every DECLARED index against the live catalogue: `{index, table, present,
    relation_present}`.

    ⚑⚑ THE REQUIREMENT WAS DISCOVERED BY ATTEMPTING CREATION, WHICH IS CHECK-THEN-ACT.
    `ingest_core` opened with `apply(con, only="event")`, re-issuing the whole
    `CREATE UNIQUE INDEX IF NOT EXISTS` suite on EVERY core — and **`IF NOT EXISTS`
    still takes the ShareLock before it can discover the index already exists.**
    Under `make -j` that is one `ShareLock on terms` per module. MEASURED live: 13
    backends lock-waiting, 11 of them queued on the identical
    `CREATE UNIQUE INDEX IF NOT EXISTS ix_terms_text`.

    ⚑ SO THE FIX IS NOT A CHEAPER CHECK, IT IS A DECLARED PRECONDITION (operator,
    2026-08-20: *"Can we be explicit about which indexes a query should use, so that
    a query fails if the index isn't present? That could help deal with TOCTOU."*).
    A reader asserts what it requires and FAILS if it is missing; no reader creates.

    ⚑ THE ROSTER IS DERIVED FROM `INDEXES`, NEVER TYPED — the same discipline
    `uniqueness` states: an index added tomorrow is checked tomorrow with no edit
    here. A second hand-maintained list is the duplication `schema_decl`'s own
    header records retiring.

    ⚑ AN ABSENT RELATION IS ITS OWN STATE, NOT A FAILURE. A tenant that does not
    hold a tier cannot be missing that tier's indexes, and folding the two together
    would make every sandbox read as broken. Same distinction `uniqueness` draws.

    ⚑ PRESENCE IS NOT POPULATION, and this mode cannot see the difference. MEASURED:
    12 declared indexes sit at 8,192 B over EMPTY relations. A green here says the
    access path exists, never that the tier holds anything — the
    census-green-is-a-fact-about-the-census shape, stated so it is not overread.
    """
    from schema_decl import INDEXES

    have_rel = set(relations(con))
    live = {r["index"] for r in index_sizes(con)}
    out = []
    for ix in INDEXES:
        tbl = ix.table.name
        out.append(
            {
                "index": ix.name,
                "table": tbl,
                "relation_present": tbl in have_rel,
                "present": ix.name in live,
            }
        )
    return out


def require_indexes(con, tier, label=""):
    """⟡ddl-once-not-per-core — ASSERT a tier's declared indexes are present; REFUSE if not.

    ⚑⚑⚑ THE PRECONDITION `declared_indexes` ARGUED FOR AND NOTHING CALLED. Its own docstring
    records the diagnosis and the operator's ruling — *"A reader asserts what it requires and
    FAILS if it is missing; no reader creates"* — and then only a CLI REPORT was built on it.
    So the rule existed as prose while `pack_core_sql` still opened with
    `_schema.apply(con, only="obsnode")`, re-issuing the whole CREATE suite per core.

    ⚑⚑ AND THAT IS A DEADLOCK, MEASURED 2026-08-22, NOT MERELY A COST. `IF NOT EXISTS` STILL
    TAKES THE RELATION LOCK BEFORE IT CAN DISCOVER THE INDEX ALREADY EXISTS. Under
    `make -j 8 promote`, eight workers each ran
    `CREATE UNIQUE INDEX IF NOT EXISTS ix_obsnode_pk ON obs_node (core_id, local_id)`; five sat
    on `Lock: relation` and pairs deadlocked outright —
    `Process 457 waits for RowExclusiveLock … blocked by 453; 453 waits … blocked by 457`.
    The identical shape `declared_indexes` recorded for `ingest_core`/`ix_terms_text` (13
    backends, 11 queued on one statement), in a second call site that never got the fix.

    ⚑ SO THE WRITE PATH ASSERTS AND BAILS. Establishing a tier is a BUILD-TIME act, done once;
    a per-core operation that creates its own indexes is check-then-act at whatever concurrency
    the build happens to run at. `schema.py --check-indexes` is the human spelling; this is the
    programmatic one, over the same `declared_indexes` roster so an index added tomorrow is
    required tomorrow with no edit here.

    ⚑ AN ABSENT RELATION IS ITS OWN STATE AND STILL A REFUSAL HERE, which differs from
    `declared_indexes`' reporting stance deliberately: that mode answers *"is this tenant
    consistent"* about tenants that legitimately lack a tier, while this one is asked by
    something ABOUT TO WRITE to that tier. A missing relation is a missing precondition for a
    writer even though it is not an inconsistency for a reader.

    Raises `RuntimeError` naming the tier, the missing indexes, and the command that fixes it.
    """
    from schema_decl import _TIERS

    want = {t.name if hasattr(t, "name") else t for t in _TIERS.get(tier, ())}
    missing = [d for d in declared_indexes(con) if d["table"] in want and not d["present"]]
    if missing:
        raise RuntimeError(
            "%s: tier %r is not established — %d declared index(es) absent: %s\n"
            "  A per-core write ASSERTS its access paths; it does not create them "
            "(`CREATE INDEX IF NOT EXISTS` takes the relation lock before it can discover the\n"
            "  index exists, which deadlocks concurrent writers).\n"
            "  Establish it once:  python3 jea/metalanguage/schema.py --establish %s --live --apply"
            % (
                label or "require_indexes",
                tier,
                len(missing),
                " ".join(d["index"] for d in missing),
                tier,
            )
        )
    return True


def require_tiers(con, tiers, label=""):
    """⟡ddl-is-a-write — ASSERT every named tier is ESTABLISHED (relations AND declared
    indexes present); REFUSE naming `--establish`. Creates nothing. Commits nothing.

    ⚑⚑⚑ THE FOURTH AND FIFTH SITES OF ⟡assert-dont-establish, AND THE FIRST ONES IN A **READ**
    PATH. `sppf_drain._tiers` and `sppf_tree._tiers` were TWO BODIES OF ONE NAME (the
    `agda_files()`-was-four-bodies shape) that each ran `_schema.apply(...)` twice and
    `con.commit()` UNCONDITIONALLY, on entry to all 19 of their callers. Ten of those callers
    are pure reads whose own docstrings say so verbatim — `--drain-census` (*"the populations.
    Writes nothing"*), `--drain-licence` (*"the dry run. Writes nothing"*), `--tree-census`,
    `--tree-chains`, `--tree-roundtrip`, `--tree-wedge`, `--tree-explain` (which deliberately
    omits `ANALYZE` so it *"must not run the INSERT"* — and then issued CREATE + COMMIT four
    lines earlier). A census that establishes its own schema cannot report on a store that
    lacks it; it reports on the store it just made.

    ⚑⚑ AND IT IS THE SAME LOCK HAZARD, NOT MERELY A TIDINESS POINT. `CREATE … IF NOT EXISTS`
    TAKES THE RELATION LOCK BEFORE IT CAN DISCOVER THE OBJECT EXISTS (measured three times in
    this tree: 13 backends on `ix_terms_text`, five workers plus deadlocked pairs on
    `ix_obsnode_pk`). `--tree-concurrency` and `--drain-concurrency` fan N processes at these
    very modes, so the read path was contributing DDL contention to the concurrency
    measurement it exists to take.

    ⚑ THE `tree` SHADOW CONSTRAINT IS SATISFIED BY ESTABLISHING, NOT BY APPLYING PER CALL.
    `sppf_drain._tiers` argued `tree` must be applied *"because the SHADOW is part of that
    tier's DDL and the licence cannot be asked without it"* — true, and it is an argument for
    the shadow EXISTING, which `_tier()` (*"its tables, their indexes, and its SHADOW"*) puts
    in the tier's DDL and `schema.py --establish` therefore creates. A precondition is met
    once at build time; re-issuing it per invocation is check-then-act at whatever concurrency
    the caller happens to run at.

    ⚑ RELATION-ABSENT IS A REFUSAL HERE, deliberately matching `require_indexes` and differing
    from `declared_indexes`' reporting stance. These callers are ASKED ABOUT a tier they
    intend to read or write; a tier that is not there is a missing precondition, and the two
    `_tiers` docstrings already argued exactly this for their NEIGHBOURS — *"Creating
    `core_decoded` here would turn 'you have not sourced anything' into a successful drain of
    an empty table"*. That reasoning was correct and was applied to every tier EXCEPT the ones
    the function itself created.

    ⚑ IT DELEGATES THE INDEX HALF TO `require_indexes` RATHER THAN RE-DERIVING IT — one
    roster, one refusal text, so an index added tomorrow is required tomorrow with no edit
    here. This adds only the RELATION-presence half, which `require_indexes` cannot see for a
    tier whose tables are absent entirely (no relation, no declared index rows to be missing).

    Raises `RuntimeError` naming the tiers, what is absent, and the command that fixes it.
    """
    from schema_decl import _TIERS

    tiers = [tiers] if isinstance(tiers, str) else list(tiers)
    unknown = [t for t in tiers if t not in _TIERS]
    if unknown:
        raise RuntimeError(
            "%s: unknown tier(s) %s — known: %s"
            % (label or "require_tiers", " ".join(unknown), " ".join(sorted(_TIERS)))
        )
    have = set(relations(con))
    absent = []
    for t in tiers:
        for rel in _TIERS[t]:
            name = rel.name if hasattr(rel, "name") else rel
            if name not in have:
                absent.append((t, name))
    if absent:
        raise RuntimeError(
            "%s: tier(s) %s not established — %d relation(s) absent: %s\n"
            "  This path ASSERTS its schema; it does not create it (`CREATE … IF NOT EXISTS`\n"
            "  takes the relation lock before it can discover the object exists, which\n"
            "  deadlocks concurrent callers — and a census that establishes its own schema\n"
            "  reports on the store it just made).\n"
            "  Establish it once:  python3 jea/metalanguage/schema.py --establish %s --apply"
            % (
                label or "require_tiers",
                " ".join(tiers),
                len(absent),
                " ".join("%s.%s" % (t, n) for t, n in absent),
                " ".join(tiers),
            )
        )
    for t in tiers:
        require_indexes(con, t, label=label or "require_tiers")
    return True


def index_sizes(con, like=None):
    """Every index in this tenant: `{index, table, bytes, rows, bytes_per_row}`.

    ⚑⚑ `--growth` REPORTS RELATIONS AND NOTHING REPORTED INDEXES, which is the half that
    decides a KEY-WIDTH question. The surrogate-vs-content-address decision for `term_id` is
    exactly that question — a content address is ~56 bytes where a counter is ~4, on the
    LEADING COLUMN of five indexes over millions of rows — and the only instrument for it was
    an adjective. A per-index byte figure plus rows makes the tradeoff a number.

    ⚑ BYTES-PER-ROW IS THE COMPARABLE FIGURE, not total bytes. Two tenants hold different row
    counts, so a total says which store is bigger and never which KEY is wider; the per-row
    cost is the thing that transfers from a 258k-row sandbox to a 12.5M-row corpus.

    `like` filters on the index name (SQL `LIKE`), so a variant experiment can name its own.
    """
    sql = (
        "SELECT c.relname AS index, t.relname AS table, "
        "pg_relation_size(c.oid) AS bytes, t.reltuples::bigint AS rows "
        "FROM pg_class c JOIN pg_index i ON i.indexrelid = c.oid "
        "JOIN pg_class t ON t.oid = i.indrelid "
        "JOIN pg_namespace n ON n.oid = c.relnamespace "
        "WHERE c.relkind = 'i' AND n.nspname = ANY (current_schemas(false))"
    )
    params = ()
    if like:
        sql += " AND c.relname LIKE %s" % ph()
        params = (like,)
    out = []
    for r in rows(con, sql + " ORDER BY pg_relation_size(c.oid) DESC", params):
        n = r["rows"] or 0
        out.append(
            {
                "index": r["index"],
                "table": r["table"],
                "bytes": r["bytes"],
                "rows": n,
                "bytes_per_row": (r["bytes"] / n) if n > 0 else None,
            }
        )
    return out


def index_size_report(con=None, like=None):
    """`--index-size` — per-index on-disk bytes, rows and bytes/row. Exit code."""
    con = con or _cli_connect()
    rs = index_sizes(con, like)
    for r in rs:
        print(
            "  %-24s %-14s %12s B  %10s rows  %s B/row"
            % (
                r["index"],
                r["table"],
                format(r["bytes"], ","),
                format(r["rows"], ","),
                "-" if r["bytes_per_row"] is None else "%.1f" % r["bytes_per_row"],
            )
        )
    print("\n%d index(es); %s bytes total" % (len(rs), format(sum(r["bytes"] for r in rs), ",")))
    return 0


def check_indexes_report(con=None, sandbox=False):
    """Ⓢ1 `--check-indexes` — declared indexes vs the live catalogue. Exit code.

    ⚑ NON-ZERO WHEN A DECLARED INDEX IS MISSING FROM A RELATION THAT EXISTS, because
    this is a PRECONDITION and a precondition that always exits 0 is a report. The
    point is that a reader can assert its access paths instead of a writer creating
    them, so the failure has to be a failure.

    ⚑⚑ THE FAILURE NAMES ITS TENANT, and that is not decoration. Memory
    `wrong-tenant-read-is-silent` records that a per-dispatch `--sandbox` drifts so
    READ modes ignore it silently — so an index missing from a SANDBOX would report
    as a live-store defect and send someone to repair a store that is fine. The
    tenant is the first thing on the line for exactly that reason.
    """
    con = con or _cli_connect()
    rs = declared_indexes(con)
    who = "sandbox" if sandbox else "live"
    missing = [r for r in rs if r["relation_present"] and not r["present"]]
    for r in rs:
        state = (
            "- relation absent"
            if not r["relation_present"]
            else "OK"
            if r["present"]
            else "MISSING"
        )
        print("  %-22s %-14s %s" % (r["index"], r["table"], state))
    print(
        "\n[%s] %d of %d declared index(es) present; %d absent relation(s)"
        % (
            who,
            sum(1 for r in rs if r["present"]),
            sum(1 for r in rs if r["relation_present"]),
            sum(1 for r in rs if not r["relation_present"]),
        )
    )
    if missing:
        print(
            "⚑ [%s] %d declared index(es) MISSING from a relation that EXISTS: %s"
            % (who, len(missing), ", ".join(r["index"] for r in missing))
        )
        print(
            "  A reader that needs one of these has no access path. Create them "
            "ONCE via\n  `sppf_db.py --init` — do NOT let an ingest job create them: "
            "`CREATE … IF NOT\n  EXISTS` takes the ShareLock before it can discover "
            "the index is already there,\n  which is the DDL storm this mode exists "
            "to replace."
        )
    return 1 if missing else 0


def uniqueness_report(con=None):
    """`--uniqueness` — every declared UNIQUE index against the live data. Exit code.

    ⚑ NON-ZERO WHEN A DECLARED INDEX WOULD BE REFUSED, because this is a PRE-FLIGHT and a
    pre-flight that always exits 0 is a report. An ABSENT relation is not a failure: this
    tenant simply does not hold that tier, which is the normal state for `ref`/`obsnode`.
    """
    con = con or _cli_connect()
    rs = uniqueness(con)
    bad = [r for r in rs if r["dup_groups"]]
    for r in rs:
        state = (
            "- absent"
            if not r["present"]
            else "OK"
            if not r["dup_groups"]
            else "REFUSED — %s duplicate key group(s)" % format(r["dup_groups"], ",")
        )
        print("  %-20s %-12s (%s)  %s" % (r["index"], r["table"], ", ".join(r["cols"]), state))
    print(
        "\n%d of %d declared unique index(es) satisfied by the data; %d absent relation(s)"
        % (
            sum(1 for r in rs if r["present"] and not r["dup_groups"]),
            sum(1 for r in rs if r["present"]),
            sum(1 for r in rs if not r["present"]),
        )
    )
    if bad:
        print(
            "⚑ %d index(es) would be REFUSED by `apply()` on this tenant — repair the data "
            "or\n  drop the declaration; do NOT add an exemption." % len(bad)
        )
    return 1 if bad else 0


def core_report(path, con=None):
    """`--core PATH` — is THIS core in the store, and how many rows does it hold? Exit code."""
    # ⚑ THIS EXISTS BECAUSE `--census` COUNTS RELATIONS, NEVER A ROW. I reported that a
    # richer walk "landed end to end" on the strength of `core_fp` going 1958 → 1959 —
    # but the core I ingested was ALREADY PRESENT, so a correct run would have
    # self-skipped and changed nothing. A total moving by one says a core was added; it
    # cannot say WHICH, and I read it as confirmation of the one I had in hand.
    # ⚑ THE CONTENT-ADDRESS AUTHORITY, NOT A RE-DERIVATION. `sppf_db` imports
    # `_content_addr._b64`; hand-rolling a blake2b here would be a second spelling of
    # the core_id and would silently miss every row when it drifted.
    import os
    import sys

    sys.path.insert(
        0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts")
    )
    from _content_addr import _b64 as _cid

    # ⚑ THE ROOT COMES FROM `substrate_core_root`, NOT FROM A RECONSTRUCTED PATH. My
    # first cut took the relpath against `agda/_build` and tried two hand-guessed
    # prefixes; the real base is `<agda>/_build/<ver>/agda/Substrate`, so EVERY lookup
    # missed and the mode reported "not in the store" for cores that are certainly in
    # it — an absence claim that was a fact about my path arithmetic.
    from jea_agdai import substrate_core_root

    agda_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "agda")
    root = substrate_core_root(agda_root)
    cands = [os.path.relpath(os.path.abspath(path), os.path.abspath(root))]
    con = con or _cli_connect()
    found = False
    for c in cands:
        cid = _cid(c)
        row = None
        for r in rows(
            con, "SELECT core_id, mtime, producer FROM core_fp WHERE core_id=%s" % ph(), (cid,)
        ):
            row = r
        if row is None:
            continue
        found = True
        nobs = scalar(con, "SELECT count(*) FROM obs WHERE core_id=%s" % ph(), (cid,))
        ned = scalar(con, "SELECT count(*) FROM edge WHERE core_id=%s" % ph(), (cid,))
        nun = scalar(con, "SELECT count(*) FROM unit_obs WHERE core_id=%s" % ph(), (cid,))
        print(
            "%s\n  core_id  %s\n  producer %s\n  mtime    %s"
            % (c, cid, row["producer"], row["mtime"])
        )
        print(
            "  obs %s   edge %s   unit_obs %s"
            % (format(nobs, ","), format(ned, ","), format(nun, ","))
        )
    if not found:
        print("not in the store under any of: %s" % ", ".join(cands))
    return 0 if found else 1


def spread_report(con=None):
    """`--spread` — per-core row DISTRIBUTION. Returns an exit code."""
    # ⚑ THIS EXISTS BECAUSE I EXTRAPOLATED FROM ONE SAMPLE, THREE TIMES, AND WAS WRONG
    # EVERY TIME. Estimates of the generic walk's cost went 11× → 100× → the measured
    # figure, each taken from `Instance.agdai` — an 8-definition module — as if it stood
    # for the corpus. A single core is not a distribution, and the store could not be
    # asked for one.
    con = con or _cli_connect()
    for r in rows(
        con,
        "SELECT count(*) AS cores, min(n) AS lo, max(n) AS hi, "
        "       round(avg(n))::bigint AS mean, "
        "       percentile_cont(0.5) WITHIN GROUP (ORDER BY n)::bigint AS median, "
        "       percentile_cont(0.9) WITHIN GROUP (ORDER BY n)::bigint AS p90, "
        "       sum(n) AS total "
        "FROM (SELECT core_id, count(*) AS n FROM obs GROUP BY core_id) s",
    ):
        if not r["cores"]:
            print("no cores ingested")
            return 0
        print("obs rows per core, over %s core(s):" % format(r["cores"], ","))
        for k in ("lo", "median", "mean", "p90", "hi"):
            print("  %-8s %12s" % (k, format(r[k] or 0, ",")))
        print("  %-8s %12s" % ("total", format(r["total"] or 0, ",")))
        # ⚑ THE SPREAD IS THE POINT: a mean far below the max means a few monoliths
        # dominate, and any estimate taken from a small module understates the corpus.
        if r["median"] and r["hi"]:
            print(
                "\n  max/median = %.0f× — an estimate from ONE core is off by "
                "up to this factor" % (r["hi"] / max(r["median"], 1))
            )
    # ⚑⚑⚑ AND IT NAMES THE CORES, WHICH IT DID NOT UNTIL 2026-08-15 — a statistic whose whole
    # point is *"go measure the outliers, not a sample"* while DISCARDING which core is the
    # outlier. The argmax was computed by `max(n)` and thrown away, so the reader was told the
    # spread was 152× and given no way to reach the core achieving it.
    #
    # ⚑⚑ MEASURED CONSEQUENCE, and it is the reason this line exists: the SQL packing fold was
    # verified on four cores of 7k–55k observations and the live maximum is 943,927 — 17× the
    # largest ever exercised. `sppf_db.py --height <core_id>` can read that core's level schedule
    # live and read-only, giving the exact size of the largest single statement BEFORE anything
    # writes — but it takes a core id, and this report was the only thing that knew there was a
    # 943,927-row core at all. One statistic away from an unmeasurable tail.
    #
    # ⚑ TOP-N, NOT JUST THE MAX. A single argmax invites the same one-sample extrapolation this
    # docstring opens by confessing; the shape of the tail (is it one monolith or twenty?) is
    # what decides whether a run is bounded, and that needs several rows.
    print("\n  the TAIL, by name — the cores any per-core estimate must be checked against:")
    for r in rows(
        con, "SELECT core_id, count(*) AS n FROM obs GROUP BY core_id ORDER BY n DESC LIMIT 8"
    ):
        print("    %-14s %12s obs" % (r["core_id"], format(r["n"], ",")))
    print("  ⚑ `sppf_db.py --height <core_id>` reads any of these LIVE and READ-ONLY: the level")
    print("     schedule plus per-level row counts — i.e. the largest single statement a fold")
    print("     over that core would issue, measurable before it writes anything.")
    # ⚑⚑⚑ AND THE MEDIAN BAND, FOR THE SAME REASON ONE LEVEL OVER — this report named the
    # extremes and DISCARDED the typical, which is the argmax gap above repeated on the other
    # statistic. Measured 2026-08-17: the first live write wanted a TYPICAL core (exercise the
    # wiring end-to-end at low stakes before the 943,927-row tail), the median was printed as
    # `6,212`, and nothing here could say WHICH core that was. A statistic one cannot reach the
    # subject of is the same defect whether it sits at the max or at the middle.
    #
    # ⚑⚑ A BAND, NOT THE ARGMEDIAN. One core at the exact median is a single sample again — the
    # thing this docstring opens by confessing to. Several rows around it show whether the middle
    # of the distribution is flat (any of them stands for the rest) or steep (it does not), which
    # is what decides whether a trial core generalises at all.
    print("\n  the MEDIAN BAND, by name — the cores a TYPICAL-case trial should use:")
    for r in rows(
        con,
        "SELECT core_id, n FROM ("
        "  SELECT core_id, count(*) AS n,"
        "         row_number() OVER (ORDER BY count(*)) AS rk,"
        "         count(*) OVER () AS tot"
        "  FROM obs GROUP BY core_id) s "
        "WHERE rk BETWEEN (tot / 2) - 2 AND (tot / 2) + 2 "
        "ORDER BY n",
    ):
        print("    %-14s %12s obs" % (r["core_id"], format(r["n"], ",")))
    return 0


def packed_report(con=None):
    """`--packed` — which cores are INTERNED, and how far. Returns an exit code."""
    # ⚑⚑⚑ THIS EXISTS BECAUSE THE QUESTION HAD NO READER AND I ANSWERED IT BY HAND, WRONG.
    # `--equiv pack.sql pack.python` compares two folds, and BOTH arms read `obs_node`. So a
    # probe core must be BOTH ingested AND projected — and nothing could name one. Reaching
    # for `--query` (does not exist) and `--probe` (SANDBOX only), I picked a core from
    # `unprojected_cores`, got `pack.sql 4 / pack.python 0`, and nearly read a MISSING
    # REFERENCE ARM as a disagreement between the folds. The second attempt picked a core
    # from `obs_node` and hit the opposite wall: it was already DRAINED, so `sppf_db --height`
    # refused with *"core has NO observations"* and both arms read empty again.
    #
    # ⚑⚑ THE WINDOW IS THE FINDING. A core is comparable only while it is ingested AND
    # projected — after the drain its staged side is gone, before the promote its durable
    # side is absent. `obs_node` holds ~950k rows against ~124M unprojected observations, so
    # that window is THIN and cannot be found by guessing. This report is the reader that
    # names it.
    #
    # ⚑ AND "0.9% INTERNED" WAS A SUBTRACTION DONE IN A TURN. Two `--census` figures read
    # minutes apart, divided by hand — the judgement-not-codified shape, and it evaporates
    # when the turn ends. A ratio the store can be ASKED for is re-derivable; one computed in
    # prose is not.
    con = con or _cli_connect()
    # ⚑ DRIVER-SHAPED, NOT CORPUS-AGGREGATED — the spill lesson `--holes` records one level
    # up. `obs_node` is the SMALL side (~950k rows over 3 cores); driving from its grouped
    # cores and probing `obs` per core is ~n index probes, where `LEFT JOIN (SELECT DISTINCT
    # core_id FROM obs)` would materialise the distinct set over all 124M rows first. Same
    # answer, and the difference is a disk fill.
    got = list(
        rows(
            con,
            "SELECT n.core_id, count(*) AS packed, "
            "       (SELECT count(*) FROM obs o WHERE o.core_id = n.core_id) AS staged "
            "FROM obs_node n GROUP BY n.core_id ORDER BY count(*) DESC",
        )
    )
    if not got:
        # ⚑ EMPTY IS NOT ZERO-COVERAGE, IT IS AN UNRUN PROMOTE, and the two want opposite
        # repairs. Saying "0% interned" would report a fact about the SCHEDULE as a fact
        # about the data.
        print("obs_node is EMPTY — the promote has not run on this tenant.")
        print("  This is UNMEASURED coverage, not zero coverage: nothing has been offered")
        print("  to the fold yet. `sppf_db.py --converge` is what fills it.")
        return 0
    print("interned cores — the `--equiv` COMPARISON WINDOW\n")
    print("  %-46s %12s %12s  %s" % ("core_id", "staged", "packed", "state"))
    live = drained = partial = 0
    for r in got:
        st, pk = r["staged"] or 0, r["packed"]
        # ⚑ THREE STATES, NOT A PERCENTAGE. `staged=0` is DRAINED (the staged tier retired,
        # durable kept) and reads as 0% coverage under naive division while being the
        # SUCCESS case. Collapsing them to one ratio is the scalar-over-two-flows defect.
        if st == 0:
            state, drained = "DRAINED — staged retired", drained + 1
        elif pk >= st:
            state, live = "COMPARABLE ⟵ use this", live + 1
        else:
            state, partial = "partial (%.1f%%)" % (100.0 * pk / st), partial + 1
        print(
            "  %-46s %12s %12s  %s" % (r["core_id"][:46], format(st, ","), format(pk, ","), state)
        )
    print("\n  %s comparable · %s drained · %s partial" % (live, drained, partial))
    # ⚑ THE DENOMINATOR, for the reason `--holes` states: a numerator alone makes a PARTIAL
    # ingest read as a finished one. Asked of the store rather than divided by hand.
    # ⚑ CATALOGUE ESTIMATES: the figure wanted here is a COVERAGE RATIO, and two full scans
    # (~269M rows) to render a percentage is corpus-scale work for a proportion. Labelled
    # `~` so the reader knows which kind of number this is — an interning percentage that
    # moves during a build is expected to be approximate, and a precise-looking one would
    # invite exactly the stock-vs-rate misreading a peer and I already made on `path_text`.
    for r in rows(
        con,
        "SELECT (SELECT n_live_tup FROM pg_stat_user_tables WHERE relname='obs_node') AS pk, "
        "       (SELECT n_live_tup FROM pg_stat_user_tables WHERE relname='obs') AS st",
    ):
        if r["st"]:
            print(
                "  corpus: ~%s of ~%s observation(s) interned (~%.2f%%, live-tuple estimates)"
                % (format(r["pk"], ","), format(r["st"], ","), 100.0 * r["pk"] / r["st"])
            )
    if not live:
        # ⚑ A REFUSAL THAT NAMES ITS SUCCESSOR. Reporting "no comparable core" without saying
        # what makes one is the half-gate shape: a correct verdict the reader cannot act on.
        print("\n  ⚑ NO COMPARABLE CORE — `--equiv pack.sql pack.python` cannot be made")
        print("     non-vacuous against this tenant. Both arms read `obs_node`, so a core")
        print("     must be ingested AND projected; every row above is drained or partial.")
        print("     Promote one core (`sppf_db.py --project-core <id>`) to open the window.")
    return 0


#: ⟡pathtext-coverage — the DERIVED tables and the source each is materialized FROM.
#: A row is `(materialized, source, key, grain)`: `grain` says what ONE source row IS, because
#: that is exactly the fact whose absence produced a wrong ratio (below).
#:
#: ⚑⚑⚑ THIS TABLE IS A STOPGAP AND SHOULD BE DERIVED, NOT DECLARED (⟡derive-derived-from,
#: operator 2026-08-22: *"Shouldn't this be emergent from interning SQL, the same way we
#: intern agda and will be interning python?"*). It should — and the carrier that would
#: emit it ALREADY EXISTS.
#:
#: A derivation edge is `INSERT INTO X … SELECT … FROM Y`: a statement-tree fact, not a
#: modelling opinion. `refresh_path_text` states `path_text ← path_seg` on `path_id` in its
#: own INSERT, and `sql_lift` already interns every SQL builder pipeline into the SAME graded
#: carrier as the python (measured: 1092 python + 52 SQL pipelines, 2418 nodes) and already
#: PRINTS the read side per entry — `build_units() reads: _unit, _unit_cod, unit_node,
#: unit_obs`. The write target is derivable identically; nothing projects the PAIR yet.
#:
#: ⚑ SO MY FIRST COMMENT HERE WAS WRONG ON ITS OWN TERMS. It said *"declared and not
#: discovered, deliberately — inferring it from column names would be the guess this module
#: refuses"*, which is true of a COLUMN-NAME heuristic and irrelevant to reading the INSERT.
#: I defended a hand table against a guess nobody proposed, while the exact, non-heuristic
#: derivation sat one tool over. That is the derived-view-that-rots this repo keeps retiring,
#: written by someone who had just cited the rule.
#:
#: ⚑ WHAT IS GENUINELY NOT DERIVABLE IS `grain` — "one path_seg row is one SEGMENT" is a
#: semantic fact no statement carries, and it is the fact whose absence produced a wrong
#: ratio. When the edge set becomes derived, THIS table shrinks to grain annotations keyed by
#: relation, and the edges stop being restated.
DERIVED_FROM = (("path_text", "path_seg", "path_id", "one SEGMENT of a dotted path (≈4 per path)"),)


def coverage_report(con=None):
    """`--coverage` — for each DERIVED table: source, materialized, and the residue owed.

    ⚑⚑⚑ THIS EXISTS BECAUSE I PRODUCED THREE WRONG NUMBERS ABOUT ONE TABLE IN ONE TURN, and
    every one of them was a hand-derivation the store could have been asked for:

      * *"56 readers"* — `--relname path_text`'s TEXT-level site count, of which 40 were the
        GENERATED compiled cache restating the same builders. The declared population is 19
        (`query_defs --touching path_text`). A method's count reported as a substrate fact.
      * *"~18% coverage"* — `21,932 / 122,982`, i.e. path_text ROWS over path_seg ROWS. Those
        are DIFFERENT GRAINS: path_seg holds one row per dotted SEGMENT (~4 per path), so the
        denominator is ~4× the real one and the ratio is meaningless. This is the defect
        `packed_report` already records — *"a subtraction done in a turn"* — repeated by the
        person who had just read that comment.
      * *"path_seg.path_id is the dotted qname"* — read off `--sample`, which DECODES base64
        fields for display. A rendering taken for the data.

    ⚑ SO THE GRAIN IS A DECLARED COLUMN, not a comment. `DERIVED_FROM` carries it, the report
    prints it, and the ratio is computed over DISTINCT keys on both sides — which is the only
    division that means anything when the grains differ.

    ⚑ THREE STATES, NOT A PERCENTAGE — `packed_report`'s rule, and it applies unchanged here.
    An EMPTY materialization is an UNRUN projection, not zero coverage; a source that is
    itself empty is UNMEASURED, not complete. Collapsing either into a ratio reports a fact
    about the SCHEDULE as a fact about the data.

    ⚑ AND THE FIGURE IS A SERIES, NOT A SCALAR (operator, 2026-08-22: *"have the tools always
    log into victoriametrics"*). This store MOVES under the measurement — `obs` read 130.9M
    and 137.7M in one session — so a single reading is stale on arrival and only the curve is
    honest. `--emit` sends these through `membudget_otlp.emit_gauges`, THE shared producer
    (never a fourth emitter), which pins the Resource and emits its own heartbeat.
    """
    con = con or _cli_connect()
    print("derived-table coverage — DISTINCT KEYS on both sides (grains differ)\n")
    print(
        "  %-14s %-12s %12s %12s %8s %8s  %s"
        % ("derived", "from", "src keys", "material", "owed", "orphan", "state")
    )
    out = []
    for mat, src, key, grain in DERIVED_FROM:
        # ⚑⚑ BOTH RESIDUES, BECAUSE THE SET DIFFERENCE IS NOT SYMMETRIC AND ONLY ONE OF THEM
        # IS "COVERAGE". `owed` (source ∖ materialized) is work the projection has not done.
        # `orphan` (materialized ∖ source) is the OPPOSITE defect: rows outliving the source
        # they were derived from, which a coverage ratio cannot express at all and a
        # count-vs-count subtraction reports as NEGATIVE DEBT. Measured on the live store the
        # first time this ran: path_text had 21,932 keys against path_seg's 21,786 — owed=0,
        # orphan=146. A one-sided reader would have printed COMPLETE and hidden it.
        got = list(
            rows(
                con,
                "SELECT (SELECT count(DISTINCT %s) FROM %s) AS src, "
                "       (SELECT count(DISTINCT %s) FROM %s) AS mat, "
                "       (SELECT count(*) FROM (SELECT DISTINCT %s FROM %s EXCEPT "
                "                              SELECT %s FROM %s) r) AS owed, "
                "       (SELECT count(*) FROM (SELECT DISTINCT %s FROM %s EXCEPT "
                "                              SELECT %s FROM %s) r) AS orphan"
                % (key, src, key, mat, key, src, key, mat, key, mat, key, src),
            )
        )
        r = got[0]
        s, m = r["src"] or 0, r["mat"] or 0
        owed, orph = r["owed"] or 0, r["orphan"] or 0
        # ⚑ STATES NAME REPAIRS, NEVER A RATIO — `packed_report`'s rule. Each of these wants a
        # different action, and a percentage would collapse all five into one number.
        if not s:
            state = "UNMEASURED — source is empty"
        elif not m:
            state = "UNRUN — nothing materialized yet"
        elif owed and orph:
            state = "DIVERGED — %s owed AND %s orphaned" % (format(owed, ","), format(orph, ","))
        elif owed:
            state = "%s key(s) owed (%.1f%% covered)" % (format(owed, ","), 100.0 * m / s)
        elif orph:
            state = "COMPLETE, %s ORPHAN key(s) — outlived their source" % format(orph, ",")
        else:
            state = "COMPLETE"
        print(
            "  %-14s %-12s %12s %12s %8s %8s  %s"
            % (
                mat,
                src,
                format(s, ","),
                format(m, ","),
                format(owed, ","),
                format(orph, ","),
                state,
            )
        )
        print("      grain: one %s row is %s" % (src, grain))
        out.append((mat, src, s, m, owed, orph))
    return out


def coverage_reap(con=None, apply=False):
    """`--coverage --reap {--dry-run|--apply}` — delete ORPHAN keys: materialized rows whose
    source is gone. Returns an exit code.

    ⚑ ORPHANS ONLY, NEVER `owed`. The two residues want opposite acts: an owed key is work the
    projection must DO, an orphan is a row that outlived its source. A mode that touched both
    would be a sweep wearing a repair's name.

    ⚑⚑ NOT A TIER FLUSH, AND THAT DISTINCTION IS THE WHOLE POINT (⟡no-automated-drop).
    `schema.py --flush` drops and recreates a tier from the declaration — correct for a schema
    change, catastrophic for 146 rows. This deletes exactly the computed key set, by key, in
    one bounded statement per table. No DDL, no `DROP`, no lock beyond the rows named.

    ⚑ AND IT IS THE MEASUREMENT THAT LICENSES THE DELETE. `coverage_report` computes the
    orphan set as `materialized ∖ source`; this deletes THAT set, re-derived at the moment of
    the delete rather than carried from the earlier read. The store moves under us — `obs`
    read 130.9M then 137.7M in one session — so a key list captured minutes ago could name a
    row whose source has since returned. Re-deriving inside the statement makes the predicate
    and the act one snapshot, which is `q_drainable_res`'s discipline: nothing is deleted on
    the strength of an argument.

    ⚑ EXPLICIT AXES. Neither dry nor apply is the default; the caller states one, per the
    standing rule (*"I want dry or apply, sandbox or live, explicitly stated on the command
    line"*). A delete that runs because a flag defaulted is the shape this repo removed from
    `write_events` today.
    """
    con = con or _cli_connect()
    total = 0
    for mat, src, key, _grain in DERIVED_FROM:
        pred = (
            "DELETE FROM %s WHERE %s IN "
            "(SELECT DISTINCT %s FROM %s EXCEPT SELECT %s FROM %s)" % (mat, key, key, mat, key, src)
        )
        if not apply:
            for r in rows(
                con,
                "SELECT count(*) AS n FROM (SELECT DISTINCT %s FROM %s EXCEPT "
                "SELECT %s FROM %s) o" % (key, mat, key, src),
            ):
                n = r["n"] or 0
            print("  [dry-run] %s: would delete %s orphan key(s)" % (mat, format(n, ",")))
            total += n
            continue
        n = execute(con, pred).rowcount
        con.commit()
        print("  %s: deleted %s orphan row(s)" % (mat, format(n, ",")))
        total += n
    # ⚑ READ BACK, never trust the rowcount alone — the same read-your-write rule the OTLP
    # path follows. A delete that reports N and leaves the residue non-zero is the failure
    # this line exists to catch.
    if apply:
        left = sum(o for _m, _s, _k, _v, _owed, o in coverage_report(con))
        if left:
            print(
                "  ⚑ %s orphan key(s) REMAIN after the delete — not the expected 0."
                % format(left, ",")
            )
            return 1
    print(
        "\n  %s orphan key(s) %s" % (format(total, ","), "deleted" if apply else "would be deleted")
    )
    return 0


def coverage_emit(con=None, endpoint=None):
    """`--coverage --emit` — the same reading, as a SERIES in VictoriaMetrics.

    ⚑ ROUTED THROUGH THE SHARED PRODUCER, never a hand-rolled exporter. `emit_gauges` pins
    `Resource(attributes=…)` (NOT `Resource.create()`, which mints a random per-process
    `service.instance.id` and churns a fresh series set every run — ~4148 series bought that
    lesson) and emits its own `_emit_unixtime` heartbeat, so verification is read-your-write
    on a value we control rather than the transport's 200.

    ⚑ GAUGES, NOT COUNTERS, and the reason is domain-specific: these populations legitimately
    go DOWN. A drain/retire removes rows, and in this store a falling count is HEALTH. A
    counter would read every successful reclaim as a reset.
    """
    import time as _t
    import sys as _sys
    import os as _os

    _root = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
    _sys.path.insert(0, _os.path.join(_root, "scripts"))
    _sys.path.insert(0, _os.path.join(_root, "scratch"))
    import membudget_otlp as _otlp
    import tsdbprobe as _probe

    at = _t.time()
    got = coverage_report(con)
    # ⚑ `_otlp.OTLP_ENDPOINT`, NOT A `default_endpoint()` HELPER — I called one and it does
    # not exist (`--calls default_endpoint` → 0 defs, 1 call, mine). The three existing
    # producers all pass the module constant; inventing a resolver beside it would be a
    # second authority for one fact.
    try:
        _otlp.emit_gauges(
            service="substrate.store",
            prefix="substrate_store",
            series={
                "source_keys": {(("derived", d), ("source", s)): v for d, s, v, _m, _o, _p in got},
                "materialized_keys": {
                    (("derived", d), ("source", s)): m for d, s, _v, m, _o, _p in got
                },
                # ⚑ TWO RESIDUE SERIES, NOT ONE. `owed` and `orphan` are opposite defects and
                # a single signed number would make them cancel — a table with 100 owed and
                # 100 orphaned would emit 0 and read as healthy. Told cassian the alert sense
                # of `residue`: rising is the anomaly. That only holds if the two stay split.
                "owed_keys": {(("derived", d), ("source", s)): o for d, s, _v, _m, o, _p in got},
                "orphan_keys": {(("derived", d), ("source", s)): p for d, s, _v, _m, _o, p in got},
            },
            at=at,
            endpoint=endpoint or _otlp.OTLP_ENDPOINT,
            units={
                "source_keys": "1",
                "materialized_keys": "1",
                "owed_keys": "1",
                "orphan_keys": "1",
            },
        )
    except Exception as e:  # noqa: BLE001
        print("  substrate_store: not emitted (%s)." % e, file=_sys.stderr)
        return 1
    # ⚑ READ-YOUR-WRITE ON A VALUE WE CONTROL, never the transport's 200 — which an
    # empty or malformed POST also returns.
    rc = _probe.verify(_probe.DEFAULT_BASE, "substrate_store_emit_unixtime", at)
    if rc == 0:
        print("  substrate_store: ✓ recorded — %d derived table(s), queryable back." % len(got))
        return 0
    # ⚑ NOT CONFIRMED IS NOT FAILED, and no predicate here distinguishes the three causes.
    print(
        "  substrate_store: ✗ NOT CONFIRMED. The write may have ingested and not yet be "
        "queryable, or been dropped, or the store may be down — this check cannot tell "
        "which. Diagnose with: python3 scratch/tsdbprobe.py --reachable",
        file=_sys.stderr,
    )
    return 1


def arity_report(con=None):
    """`--arity` — child-count distribution: is the forest BINARY, or n-ary? Exit code."""
    # ⚑ THIS DECIDES WHETHER THE node↔edge TRANSLATION IS A RULE OR A SPECIAL CASE.
    # `node(c₁,c₂) ↔ edge(p,c₁);edge(p,c₂)` is stated for a BINARY node; if the forest is
    # n-ary the "two views" are not two views of one shape, they are a grade-2 cell versus
    # n grade-1 cells, and `WitnessTower.Hodge:50-53` records exactly why that asymmetry
    # is real rather than a defect: *"the cell COUNTS behind the grades are NOT
    # label-symmetric — Δ³: 4 vertices, 6 edges, 4 faces"*.
    #
    # ⚑ REPORTED AS A DISTRIBUTION, NOT A MAX. "the tree is binary" and "the tree has a
    # binary node" are different claims, and only the histogram separates them.
    # ⚑ ARITY IS PER-TERM AND MUST COME FROM `edge`, NOT `node_child`. My first cut
    # grouped `node_child` by `node_id` and called the row count arity — but `node_child`
    # is the INTERNED edge set, and `ix_nc_edge` is UNIQUE on the TRIPLE
    # `(node_id, ord, child_id)`, not on `(node_id, ord)`. So one packing may hold many
    # distinct children at ONE ordinal, and a 1008-row node is a heavily-SHARED node —
    # fan-IN — not a 1008-wide constructor. Measured: `ord` has 22 distinct values in
    # `node_child` AND in the 6.3M-row pre-intern `edge`, so true fanout never exceeds 22.
    # Reporting fan-in under the name "arity" answered a question I did not ask.
    con = con or _cli_connect()
    rows_ = list(
        rows(
            con,
            "SELECT n, count(*) AS nodes FROM (SELECT core_id, plid, count(*) AS n "
            "FROM edge GROUP BY core_id, plid) s GROUP BY n ORDER BY n",
        )
    )
    total = scalar(con, "SELECT count(*) FROM obs")
    internal_src = scalar(
        con, "SELECT count(*) FROM (SELECT core_id, plid FROM edge GROUP BY core_id, plid) s"
    )
    leaves = (total or 0) - (internal_src or 0)
    if not total:
        print("the event tier is empty — nothing to measure")
        return 0
    print("TERM ARITY — children per observation, from `edge` (pre-intern)\n")
    print("over %s observation(s)\n" % format(total, ","))
    print("  %8s %10s  %s" % ("children", "nodes", ""))
    print("  %8d %10s  %s" % (0, format(leaves, ","), "█" * 40 if leaves else ""))
    mx = max([r["nodes"] for r in rows_] + [leaves]) or 1
    for r in rows_:
        print(
            "  %8d %10s  %s"
            % (r["n"], format(r["nodes"], ","), "█" * max(1, int(40 * r["nodes"] / mx)))
        )
    binary = sum(r["nodes"] for r in rows_ if r["n"] == 2)
    internal = sum(r["nodes"] for r in rows_)
    top = max((r["n"] for r in rows_), default=0)
    print(
        "\n  leaves %s · internal %s · max arity %d"
        % (format(leaves, ","), format(internal, ","), top)
    )

    # ⚑ FAN-IN IS A DIFFERENT QUANTITY AND GETS ITS OWN LINE. Conflating it with arity is
    # the defect this mode was rebuilt to fix; suppressing it would lose the sharing
    # measurement, which is the SPPF's whole point.
    fan = next(
        rows(
            con,
            "SELECT count(*) AS interned, max(n) AS widest FROM "
            "(SELECT node_id, count(*) AS n FROM node_child GROUP BY node_id) s",
        ),
        None,
    )
    if fan and fan["interned"]:
        print(
            "  interned parents %s · widest fan-IN %s  (SHARING, not arity —"
            % (format(fan["interned"], ","), format(fan["widest"] or 0, ","))
        )
        print("    ix_nc_edge is UNIQUE on the TRIPLE, so one ordinal holds many children)")
    if internal:
        print(
            "  binary internal nodes: %s of %s (%.0f%%)"
            % (format(binary, ","), format(internal, ","), 100.0 * binary / internal)
        )
    # ⚑ ARITY IS A PROPERTY OF THE REPRESENTATION, NOT THE STRUCTURE (user, 2026-08-07:
    # *"All trees can be deconstructed into binary nodes."*). I built this mode to ask
    # "is the forest binary?" as though a 1008-child node refuted the node↔edge
    # translation. It does not — that node is an UNFOLDED SPINE, and folding it back is
    # a representation change, not a loss. The question the numbers answer is therefore
    # what binarization COSTS, not whether it applies.
    #
    # An n-ary node becomes n−1 binary nodes (a left spine), so:
    spine = sum(r["nodes"] * (r["n"] - 1) for r in rows_ if r["n"] >= 2)
    already = sum(r["nodes"] for r in rows_ if r["n"] <= 1)
    print(
        "\n  BINARIZED: %s internal node(s) → %s (a spine of n−1 per n-ary node)"
        % (format(internal, ","), format(already + spine, ","))
    )
    print("  ⚑ that is a REPRESENTATION change: every tree deconstructs into binary")
    print("    nodes, so the node↔edge translation applies everywhere. Arity is a")
    print("    property of the REPRESENTATION, not the structure — a wide node is an")
    print("    unfolded spine, and folding it back loses nothing.")
    return 0


#: The btree index-entry ceiling: a tuple must fit in roughly a third of a page, and postgres
#: refuses the INSERT — not the CREATE INDEX — when it does not.
#: ⚑ DERIVED FROM THE LIVE PAGE SIZE, NEVER TYPED AS A CONSTANT. `block_size` is a compile-time
#: setting of the server (8 kB by default, but a source build can differ), so a hardcoded 2704
#: would be a figure about SOMEBODY ELSE'S postgres frozen in our source — the exact shape this
#: repo keeps paying for (`MEM_CAP` restated in four files, cassian's latencyOffset).
def _btree_ceiling(con):
    """The largest index entry this server accepts, in bytes — asked, not assumed."""
    bs = int(scalar(con, "SELECT current_setting('block_size')"))
    return bs // 3 - 8  # postgres' own BTMaxItemSize shape: ~a third of a page


def width_report(rel, con=None):
    """`--widest REL` — per-column max/avg octet width, against the btree key ceiling.

    ⚑⚑ BUILT BECAUSE A KEY-WIDTH DECISION HAD NO READER, AND THE MISSING FACT WAS THE ONE
    THAT DECIDES IT. Making `event.doc` a `jsonb` PRIMARY KEY (⟡doc-as-jsonb) is admissible
    only if every document fits a btree entry — and nothing could answer "how wide is the
    widest one". `--nullity` gives NULL/empty rates, `--index-size` gives bytes/row for
    indexes that ALREADY EXIST, and `--sample` reads the head of the table (an extrapolation
    `--spread` measures at 152× error). Three modes over one relation, none of them this.
    #
    ⚑ THE AVERAGE IS NOT THE CONSTRAINT AND REPORTING ONLY IT WOULD BE THE DEFECT. The
    planner says `width=90` for `event.ekey`; a PK fails on the ONE row that exceeds the
    ceiling, not on the mean. So MAX is the headline and avg is context — the inverse of how
    a cost report would rank them.

    ⚑ AND THE CEILING IS READ FROM THE SERVER (`_btree_ceiling`), because it is a function of
    `block_size` — a compile-time setting, not a constant of postgres. Typing 2704 here would
    be a figure about a different server frozen in our source.

    ⚑ REPORTS `octet_length`, NOT `length` — a btree entry is BYTES. On this corpus that gap
    is real and not pedantic: `Substrate.Foundation.Product.Σ.proj₂` is 36 characters and 39
    bytes, and every additional non-ASCII identifier widens it further. A character count
    would under-report the constraint on exactly the rows most likely to violate it.
    """
    con = con or _cli_connect()
    live = relations(con)
    if rel not in live:
        print("no relation %r; live: %s" % (rel, ", ".join(sorted(live))))
        return 1
    cols = [
        r["column_name"]
        for r in rows(
            con,
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = %s ORDER BY ordinal_position" % ph(),
            (rel,),
        )
    ]
    n = scalar(con, "SELECT count(*) FROM %s" % rel)
    if not n:
        # ⚑ EMPTY IS UNMEASURED, NOT NARROW. Reporting a 0-byte max would license a key width
        # on a table nothing has been written to — the false-zero this toolkit files against.
        print("%s is empty — width is UNMEASURED, not zero." % rel)
        return 0
    cap = _btree_ceiling(con)
    print(
        "%s — %s row(s); per-column octet width (btree key ceiling %s B)\n"
        % (rel, format(n, ","), format(cap, ","))
    )
    print("  %-16s %12s %12s  %s" % ("column", "max bytes", "avg bytes", "verdict"))
    rc = 0
    for c in cols:
        r = next(
            rows(
                con,
                'SELECT max(octet_length("%s"::text)) AS mx, '
                'avg(octet_length("%s"::text))::int AS av FROM %s' % (c, c, rel),
            )
        )
        mx, av = r["mx"] or 0, r["av"] or 0
        # ⚑ THE VERDICT IS THE ENGINE'S RULE APPLIED, never an opinion about the design.
        if mx > cap:
            verdict, rc = "⚑ EXCEEDS the btree ceiling — cannot be a key", 1
        elif mx > cap // 2:
            verdict = "within the ceiling, but over half of it"
        else:
            verdict = "fits a btree key"
        print("  %-16s %12s %12s  %s" % (c, format(mx, ","), format(av, ","), verdict))
    print("\n  ⚑ MAX is the constraint, not avg: a key fails on the ONE row that exceeds")
    print("    the ceiling. Bytes, not characters — a non-ASCII identifier is wider than")
    print("    it looks (`Σ.proj₂` is 36 chars / 39 bytes).")
    return rc


def _bucket_pow2(vals, label, unit="B"):
    """Power-of-two bucketed histogram of `vals`, printed. Returns nothing.

    ⚑ POWER-OF-TWO BUCKETS, NOT LINEAR ONES, because the question is about a distribution
    whose max/median ratio is in the tens. Linear bins over a 400× range put everything in
    the first bin and the tail in the last, which reports "one outlier" for what may be a
    populated tail — the shape that decides whether a cap is safe.
    """
    if not vals:
        print("  %s: no values — UNMEASURED, not zero." % label)
        return
    buckets = {}
    for v in vals:
        b = 1
        while b < max(v, 1):
            b *= 2
        buckets[b] = buckets.get(b, 0) + 1
    wide = max(buckets.values())
    print("  %s (n=%s)" % (label, format(len(vals), ",")))
    for b in sorted(buckets):
        n = buckets[b]
        bar = "█" * max(1, int(40 * n / wide))
        print("    ≤%-10s %6s  %s" % (_human(b, unit), format(n, ","), bar))


def _human(n, unit="B"):
    """A byte count as a short human string — 1024-based, matching the pow2 buckets."""
    for suf in ("", "K", "M", "G"):
        if n < 1024 or suf == "G":
            return "%g%s%s" % (n, suf, unit)
        n /= 1024.0
    return "%g%s" % (n, unit)


def _pearson(xs, ys):
    """Pearson r over two equal-length sequences, or None if undefined."""
    n = len(xs)
    if n < 2:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0 or syy <= 0:
        return None
    return sxy / (sxx**0.5 * syy**0.5)


def _spearman(xs, ys):
    """Spearman ρ — Pearson over RANKS, so it sees a MONOTONE relation a linear fit misses.

    ⚑ BOTH ARE REPORTED AND THE PAIR IS THE POINT. A low Pearson with a high Spearman means
    "predicts the ORDER but not the MAGNITUDE" — which for a capacity question is a very
    different answer from "predicts nothing", and reporting only one of them collapses them.
    """

    def _rank(vs):
        order = sorted(range(len(vs)), key=lambda i: vs[i])
        r = [0.0] * len(vs)
        i = 0
        while i < len(order):  # average ties, or ρ is wrong on a corpus with dupes
            j = i
            while j + 1 < len(order) and vs[order[j + 1]] == vs[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    return _pearson(_rank(xs), _rank(ys))


def corpus_size_report(build_root=None, con=None):
    """`--sizes` — the `.agdai` and jsonb size distributions, JOINED, with correlation.

    ⚑⚑⚑ BUILT BECAUSE A CAPACITY DECISION WAS ABOUT TO BE SIZED ON A PROXY THAT DOES NOT
    PREDICT (operator, 2026-08-27: *"Collect all of the agdai and jsonb sizes. Construct
    proper bucketed distributions for the two classes, and also measure correlation
    statistics between the two classes."*). A pooler's `pool_size` was to be derived from
    `per-doc peak × concurrency`, and the only cheap handle on "which core is big" was the
    `.agdai` on disk. **MEASURED FIRST: the largest `.agdai` in the tree is ~156 KB while
    the largest stored jsonb is 67,355,023 B — a ~430× expansion that happens INSIDE the
    decode.** So the file size cannot pick the tail core, and a cap sized from it would be
    sized on a variable that is not the one that costs.

    ⚑⚑ TWO CLASSES JOINED ON `relpath`, NOT TWO SEPARATE REPORTS. `--widest` already gives
    the jsonb side and `find -printf %s` gives the disk side; reading them separately is
    exactly the shape that lets someone eyeball "both have a tail" and infer they are the
    SAME tail. Only the join can say whether the big file is the big document, and the
    answer here decides whether a filesystem-side probe is admissible at all.

    ⚑ PEARSON **AND** SPEARMAN, because they answer different questions and the pair is the
    finding: a weak Pearson with a strong Spearman would mean the file size predicts the
    ORDER but not the MAGNITUDE — still useless for a byte cap, but useful for picking which
    core to measure. Reporting one number would hide that distinction.

    ⚑ AND THE `.agdai` SIDE IS READ FROM DISK, NOT FROM THE STORE'S `mtime`/size columns —
    `core_decoded` records no file size, so the store cannot answer this about itself. A row
    with no file on disk (a drained or renamed core) is reported as UNJOINED rather than
    dropped: an unjoined population is a fact about the corpus, and silently inner-joining
    it away is how a coverage gap becomes an invisible one.
    """
    import os as _os

    con = con or _cli_connect()
    root = build_root or _os.path.join(
        _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))),
        "agda",
        "_build",
    )
    if "core_decoded" not in relations(con):
        print("core_decoded is absent — the sourced tier is not established.")
        return 1
    n = scalar(con, "SELECT count(*) FROM core_decoded")
    if not n:
        print("core_decoded is empty — sizes are UNMEASURED, not zero.")
        return 0

    # ⚑ THE FILESYSTEM SIDE, keyed by the same `relpath` the store records. `octet_length`
    # on the jsonb's TEXT form is the INPUT-shaped number (what a backend parses), which is
    # the multiplicand a per-doc memory estimate needs — NOT `pg_column_size`, which is the
    # TOAST-COMPRESSED stored size and understates the parse cost by the compression ratio.
    disk = {}
    for dp, _dirs, fns in _os.walk(root):
        for fn in fns:
            if fn.endswith(".agdai"):
                p = _os.path.join(dp, fn)
                # ⚑⚑ THE KEY IS THE PATH UNDER `Substrate/`, NOT UNDER `agda/` — MEASURED,
                # after a first cut split on `/agda/` and produced `Substrate/Algebra/…`
                # against a store that records `Algebra/…`. **Every row was UNJOINED and the
                # correlation came back "fewer than 2 pairs".** It reported that honestly
                # rather than printing a spurious r=0, which is the only reason the bug was
                # visible at all — an inner join would have silently correlated nothing.
                parts = p.split(_os.sep + "Substrate" + _os.sep)
                if len(parts) > 1:
                    try:
                        disk[parts[-1]] = _os.path.getsize(p)
                    except OSError:
                        pass

    pairs, unjoined = [], []
    for r in rows(con, "SELECT relpath, octet_length(dec::text) AS n FROM core_decoded"):
        rp, sz = r["relpath"], r["n"] or 0
        if rp in disk:
            pairs.append((disk[rp], sz))
        else:
            unjoined.append((rp, sz))

    print(
        "corpus sizes — %s core_decoded row(s), %s .agdai file(s) under _build\n"
        % (format(n, ","), format(len(disk), ","))
    )
    _bucket_pow2([a for a, _ in pairs], ".agdai on disk")
    print()
    _bucket_pow2([j for _, j in pairs], "jsonb dec::text (INPUT size, uncompressed)")

    if unjoined:
        # ⚑ NAMED, NOT COUNTED — an unjoined row is a core whose file is gone (drained,
        # renamed, rebuilt); which ones matters for whether the join is representative.
        print(
            "\n  ⚑ %s row(s) have NO .agdai on disk and are EXCLUDED from the correlation:"
            % format(len(unjoined), ",")
        )
        for rp, sz in sorted(unjoined, key=lambda t: -t[1])[:5]:
            print("     %-52s %12s" % (rp, format(sz, ",")))

    if len(pairs) < 2:
        print("\n  fewer than 2 joined pairs — correlation is UNDEFINED, not zero.")
        return 0
    xs = [a for a, _ in pairs]
    ys = [j for _, j in pairs]
    pr, sr = _pearson(xs, ys), _spearman(xs, ys)
    print("\n  CORRELATION over %s joined pair(s):" % format(len(pairs), ","))
    print(
        "    Pearson  r = %s   (LINEAR: does file size predict document BYTES?)"
        % ("%.4f" % pr if pr is not None else "undefined")
    )
    print(
        "    Spearman ρ = %s   (MONOTONE: does it predict the ORDER?)"
        % ("%.4f" % sr if sr is not None else "undefined")
    )
    mx_a, mx_j = max(xs), max(ys)
    print(
        "\n    largest .agdai %s → its doc %s"
        % (_human(mx_a), _human([j for a, j in pairs if a == mx_a][0]))
    )
    print(
        "    largest doc    %s → its .agdai %s"
        % (_human(mx_j), _human([a for a, j in pairs if j == mx_j][0]))
    )
    print("\n  ⚑ IF THE TWO LINES ABOVE NAME DIFFERENT CORES, the file size cannot pick the")
    print("    tail document, and any capacity estimate taken from disk is measuring the")
    print("    wrong variable. The expansion happens in the DECODE, not in the file.")
    return 0


def nullity_report(rel, con=None):
    """`--nullity REL` — per-column NULL/empty rate: identity vs payload. Exit code."""
    # ⚑ BUILT BECAUSE "WHICH COLUMNS ARE PART OF IDENTITY" IS A SCHEMA QUESTION THE STORE
    # COULD NOT ANSWER (user, 2026-08-07: *"Things which might be null are not part of the
    # pkey."*). That rule makes nullability the DECIDING property for a composite-key
    # design, and the only way to ask it was `--sample`, which reads the head of the
    # table — the extrapolation `--spread` measures at 152× and this session has been
    # caught by repeatedly.
    #
    # ⚑ NULL AND EMPTY-STRING ARE COUNTED SEPARATELY AND THAT DISTINCTION IS THE POINT.
    # `lit_id` reads `''` where `qname_pid` reads `None` — both are "absent" to a human
    # and only ONE is null to postgres. A column that is 100% empty-string is NOT NULL by
    # the engine's rules, so it could sit in a PK while carrying no information; a column
    # that is 100% NULL cannot. Collapsing them would answer the wrong question.
    con = con or _cli_connect()
    live = relations(con)
    if rel not in live:
        print("no relation %r; live: %s" % (rel, ", ".join(sorted(live))))
        return 1
    cols = [
        r["column_name"]
        for r in rows(
            con,
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = %s ORDER BY ordinal_position" % ph(),
            (rel,),
        )
    ]
    n = scalar(con, "SELECT count(*) FROM %s" % rel)
    if not n:
        print("%s is empty" % rel)
        return 0
    print("%s — %s row(s); per-column absence\n" % (rel, format(n, ",")))
    print("  %-16s %10s %10s %10s  %s" % ("column", "null", "empty", "distinct", "verdict"))
    for c in cols:
        r = next(
            rows(
                con,
                'SELECT count(*) FILTER (WHERE "%s" IS NULL) AS nulls, '
                "count(*) FILTER (WHERE \"%s\"::text = '') AS empties, "
                'count(DISTINCT "%s") AS distinct_vals FROM %s' % (c, c, c, rel),
            )
        )
        nulls, empties, dv = r["nulls"], r["empties"], r["distinct_vals"]
        # ⚑ THE VERDICT IS THE USER'S RULE, APPLIED — not a judgement of mine.
        if nulls:
            verdict = "PAYLOAD — nullable, cannot be in a PK"
        elif dv <= 1:
            verdict = "CONSTANT — carries no identity"
        else:
            verdict = "identity candidate"
        print(
            "  %-16s %10s %10s %10s  %s"
            % (c, format(nulls, ","), format(empties, ","), format(dv, ","), verdict)
        )
    print("\n  ⚑ a column that is EVER null is payload, not identity — a PK column")
    print("    cannot be null, and UNIQUE would treat two nulls as DISTINCT, which")
    print("    silently breaks the idempotent-interning property.")
    return 0


def sample_report(rel, lim=5, con=None):
    """`--sample REL [N]` — N rows of a live relation, base64 fields DECODED. Exit code."""
    # ⚑ BUILT BECAUSE `--probe` IS SANDBOX-ONLY AND THAT IS CORRECT. The sandbox exists so
    # DDL experiments cannot touch the corpus; it holds no data, so "what does a real row
    # look like" has no answer there. Without this mode the only route is a `python3 -c`
    # against the live store — reasoning in the turn, and the shape the standing rule
    # forbids. READ-ONLY by construction: a relation name and a row count, nothing else.
    #
    # ⚑ AND IT DECODES, WHICH IS THE WHOLE POINT. Every id in this store is base64 of a
    # delimited string (`_b64` in sppf_db), so a raw dump is unreadable — the
    # `Algebra/F2/` clustering in `--holes` was invisible until decoded, and the question
    # THIS mode exists for (is `node_id` reversible, or is it a hash?) cannot even be
    # asked against opaque text. Fields that decode to printable text are shown decoded
    # with the raw value elided; fields that do not are shown raw.
    con = con or _cli_connect()
    live = relations(con)
    if rel not in live:
        print("no relation %r; live relations: %s" % (rel, ", ".join(sorted(live))))
        return 1

    def _show(v):
        """Decoded form when the value is base64 of printable text, else the raw value."""
        if not isinstance(v, str) or len(v) < 4:
            return repr(v)
        import base64 as _b

        try:
            d = _b.b64decode(v.encode(), validate=True).decode()
        except Exception:
            return repr(v)
        # ⚑ NUL IS THE FIELD DELIMITER (`"\x00".join(head)`), so a decoded value
        # containing it is a STRUCTURED key, not a string — render the parts.
        if any(ord(c) < 9 for c in d.replace("\x00", "")):
            return repr(v)
        return "⟨%s⟩" % " ‖ ".join(repr(p) for p in d.split("\x00")) if "\x00" in d else "⟨%r⟩" % d

    n = 0
    for r in rows(con, "SELECT * FROM %s LIMIT %d" % (rel, lim)):
        n += 1
        print("── row %d" % n)
        for k in r.keys():
            print("   %-14s %s" % (k, _show(r[k])))
    print(
        "\n%d row(s) of %s — ⟨…⟩ is a DECODED base64 field; ‖ separates NUL-joined parts" % (n, rel)
    )
    return 0


def fibre_report(con=None):
    """`--fibre` — is obs.local_id DENSE per core? Whether the residue can be POSITIONAL."""
    # ⚑ THIS MEASURES THE PREMISE THE MATERIALIZATION RESTS ON, and nothing else could
    # ask it. `lifecycle._reflected` specifies the residue's shape as *"a fibre over a
    # DENSE `local_id` is a SEQUENCE, not a set of triples: per core, an `ekey[]` whose
    # index IS the `local_id`"*. That is a CLAIM ABOUT THE DATA — positional encoding is
    # only lossless if `local_id` runs 0..n-1 with no gaps and no repeats.
    #
    # ⚑ AND A GAP AND A DUPLICATE FAIL IT FOR OPPOSITE REASONS, so a single "is it
    # dense?" boolean would hide which. A GAP means an index has no ekey — the array
    # needs a hole, and a hole is a value the sequence cannot express. A DUPLICATE means
    # one index has two ekeys — the array would silently keep one, which is the same
    # collapse `_node` makes and the residue exists to undo. Report both, per core.
    #
    # ⚑ REPORTED AS A POPULATION, NEVER A VERDICT. `--spread` records that a single core
    # is off by up to 152×; a fibre check answering "dense: yes" from one core would
    # repeat exactly that error. Every core is measured and the exceptions are named.
    con = con or _cli_connect()
    bad = []
    n_cores = 0
    for r in rows(
        con,
        "SELECT core_id, count(*) AS n, count(DISTINCT local_id) AS distinct_lid, "
        "       min(local_id) AS lo, max(local_id) AS hi "
        "FROM obs GROUP BY core_id ORDER BY count(*) DESC",
    ):
        n_cores += 1
        ok, gaps, dups = positional(r["lo"], r["hi"], r["n"], r["distinct_lid"])
        if not ok:
            bad.append((r["core_id"], r["n"], r["lo"], r["hi"], gaps, dups))
    print(
        "obs.local_id density over %s core(s) — is the fibre POSITIONAL?\n" % format(n_cores, ",")
    )
    if not n_cores:
        print("  no cores ingested — nothing to measure")
        return 0
    if not bad:
        print("  every core: local_id runs 0..n-1, no gaps, no duplicates")
        print("  ⇒ the residue IS a sequence; `ekey[]` indexed by local_id is LOSSLESS")
    else:
        print(
            "  %s of %s core(s) are NOT positional:\n"
            % (format(len(bad), ","), format(n_cores, ","))
        )
        print("  %-46s %9s %6s %8s %6s %6s" % ("core_id", "rows", "lo", "hi", "gaps", "dups"))
        for cid, n, lo, hi, g, d in bad[:20]:
            print(
                "  %-46s %9s %6s %8s %6s %6s"
                % (core_path(cid, con)[-46:], format(n, ","), lo, hi, g, d)
            )
        if len(bad) > 20:
            print("  … %s more" % format(len(bad) - 20, ","))
        print("\n  ⚑ a GAP means an index with no ekey (the array needs a hole);")
        print("    a DUP means one index with two ekeys (the array would DROP one).")
        print("    Either one makes a positional encoding lossy — the residue must")
        print("    then carry local_id explicitly, and the ~100× saving does not hold.")
    return 0


# ══ the LIVE-HANG READER — `pg_locks ⋈ pg_stat_activity` ═════════════════════════════════
#
# ⚑⚑ BUILT 2026-08-14 BECAUSE IT WAS PRESCRIBED AND NEVER BUILT. Memory
# `deadlock-breakdown-before-any-fix` names the method verbatim — *"40P01 logs both sides;
# `pg_locks ⋈ pg_stat_activity` for a live hang"* — and `toolmodes.py --find locks` returned
# **0 hits across 93 declared modes**. When a live non-advancing ingest was finally
# investigated (2026-08-14) the answer had to come from ANOTHER repo's instrument, because
# substrate could see WHAT a backend was running (`--activity`) and not WHO WAITED ON WHOM.
# A method written down in an always-recalled memory and absent from the toolkit is the weak
# half of the standing rule: a named-but-unbuilt gap.
#
# ⚑⚑ AND IT READS THE CHEAP WAY, WHICH IS NOT TASTE — IT IS THAT INCIDENT'S SECOND HALF. The
# same investigation measured the store pinned flat against a `CPUQuota=0.5` ceiling, so every
# query the breakdown issued competed for the same half core as the job it was diagnosing, and
# the active-backend count was watched rising as the breakdown ran. **An instrument that costs
# what it measures reports a system it has changed.** `pg_stat_activity`, `pg_locks` and
# `pg_blocking_pids()` are SHARED-MEMORY views: no table locks, no heap reads, no planner work
# over a user relation. There is deliberately **no `JOIN pg_class`** — that join is a real heap
# read per lock row, and it is the shape `--drain-census`'s `CREATE INDEX IF NOT EXISTS` and
# this reader's own suspicion both took: a read-only mode reaching a user relation.
# `l.relation::regclass::text` is a syscache lookup instead.
#
# ⚑ AND IT TAKES NO `--sandbox` DECISION OF ITS OWN. The resolver is `_cli_connect`, one
# authority (`wrong-tenant-read-is-silent`), and the tenant is NAMED in the footer — a lock
# reader pointed at the wrong database reports "nothing is waiting" about a database where
# nothing was ever running.

_ACTIVITY_SQL = (
    # ⚑ `clock_timestamp()`, NEVER `now()` — `activity()` records the same correction:
    # `now()` is TRANSACTION-start time, so an age for a statement that began after this
    # connection's transaction opened renders as "-1 day, 23:59:59".
    # ⚑ SELF IS **INCLUDED**, flagged rather than filtered. `activity()` excludes
    # `pg_backend_pid()`; for a lock question that is the instrument editing itself out of
    # its own reading, which is exactly the blindness this arc measured.
    "SELECT pid, leader_pid, state, wait_event_type, wait_event, backend_xid, "
    "       clock_timestamp()-xact_start  AS xact_age, "
    "       clock_timestamp()-query_start AS query_age, "
    "       pg_blocking_pids(pid) AS blocked_by, "
    "       (pid = pg_backend_pid()) AS is_self, "
    # ⚑ THE BACKEND'S OWN NAME FOR ITSELF, published by `store.connect(label=…)`. Selected
    # HERE rather than in a second query so `--locks` and `--promotes` read one row shape
    # from one authority — two spellings of "what is this backend" is the drift this file
    # keeps paying down. Empty for any connection opened without a label.
    "       application_name, "
    "       left(query, 200) AS query "
    "  FROM pg_stat_activity "
    " WHERE datname = current_database() "
    " ORDER BY query_start NULLS LAST"
)

_LOCKS_SQL = (
    # ⚑ `granted` IS THE HELD/WANTED SEAM AND IS THE WHOLE POINT OF READING `pg_locks` AT ALL.
    # `pg_stat_activity.wait_event` says a backend is waiting; only `granted = false` says
    # WHAT it is waiting FOR, and only the granted rows of the OTHER backends say who has it.
    "SELECT l.pid, l.locktype, l.mode, l.granted, "
    "       CASE WHEN l.relation IS NULL THEN l.locktype "
    "            ELSE l.relation::regclass::text END AS target "
    "  FROM pg_locks l "
    " WHERE l.pid IN (SELECT pid FROM pg_stat_activity "
    "                  WHERE datname = current_database()) "
    " ORDER BY l.pid, l.granted, l.mode"
)


def wait_cycle(edges):
    """A HOLD-AND-WAIT CYCLE in the wait-for graph `{pid: [pids it waits on]}`, or `[]`.

    Returned as the closed walk — `[a, b, a]` for a two-party cycle — so the report can print
    the ring rather than a boolean.

    ⚑⚑ THE CYCLE IS THE ONLY THING THAT MAKES A WAIT A **DESIGN VIOLATION** IN THIS
    ARCHITECTURE, so it is computed rather than eyeballed. `deadlock-breakdown-before-any-fix`
    argues the tiers are deadlock-free *by construction* (every retire reads strictly UP and
    writes DOWN, so the acquisition order is globally consistent as a THEOREM, not a
    discipline). A wait-for cycle is that theorem failing, and its RING is the location of the
    hold-and-wait — the finding the memory says must be captured before anything is cleared.

    ⚑ AND AN ACYCLIC WAIT IS A DIFFERENT FACT, NOT A WEAKER ONE. One backend queued behind a
    long writer is ordinary and self-clearing; postgres's own detector would never fire on it.
    Collapsing "someone is waiting" into "deadlock" is what turns a slow round into a false
    alarm — which is the exact misreading this module was built out of.

    ⚑ PURE, AND THAT IS WHY IT IS A FUNCTION AT ALL. The judgement that decides whether an
    operator kills a process must be drivable by a case; inline in the report it would be
    reachable only by reproducing a live deadlock, which is precisely the state nobody may
    manufacture on demand.
    """
    colour, out = {}, []
    for start in sorted(edges):
        if colour.get(start):
            continue
        colour[start] = 1
        path, stack = [start], [(start, iter(edges.get(start, ())))]
        while stack:
            node, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                colour[node] = 2
                stack.pop()
                path.pop()
                continue
            if colour.get(nxt) == 1:
                return path[path.index(nxt) :] + [nxt]
            if not colour.get(nxt):
                colour[nxt] = 1
                path.append(nxt)
                stack.append((nxt, iter(edges.get(nxt, ()))))
    return out


def wait_verdict(backends):
    """Separate the states a NON-ADVANCING store can be in. `backends` is `locks()`'s output.

    → `{"cycle", "lock_waiters", "idle_in_txn", "working", "verdict"}`.

    ⚑⚑ THE WHOLE VALUE OF THIS FUNCTION IS THAT `working` AND `lock_waiters` ARE NOT THE SAME
    OBSERVATION, AND A PROGRESS COUNTER CANNOT TELL THEM APART. Measured 2026-08-14: an ingest
    whose MONOTONE measure (`done`) was byte-identical across a 45-minute resume was read as a
    stall — and it was `active`, with **no** `wait_event`, inside one long CPU-bound
    `INSERT … SELECT` that had not COMMITted. The store was pinned flat against a
    `CPUQuota=0.5` ceiling. **A monotone measure standing still distinguishes nothing on its
    own: `stalled` and `slow` produce the identical reading, and only the wait state separates
    them.** That is the transferable finding and it is the reason this returns four disjoint
    populations instead of a boolean.

    ⚑ `idle in transaction` IS THE THIRD STATE AND IS THE ONE THAT IS ACTUALLY THE ANTIPATTERN.
    A backend holding granted locks while waiting on its CLIENT is hold-and-wait with the wait
    outside the database entirely — no postgres detector can see it, and `--activity` reports
    it as unremarkable idleness. It is listed separately for that reason.
    """
    edges = {b["pid"]: list(b["blocked_by"] or ()) for b in backends}
    lock_waiters = [b["pid"] for b in backends if b["wait_event_type"] == "Lock"]
    idle_in_txn = [
        b["pid"] for b in backends if (b["state"] or "").startswith("idle in transaction")
    ]
    working = [
        b["pid"]
        for b in backends
        if b["state"] == "active" and not b["wait_event_type"] and not b["is_self"]
    ]
    cycle = wait_cycle(edges)
    if cycle:
        verdict = "HOLD-AND-WAIT CYCLE — a design violation; capture, do not clear"
    elif lock_waiters:
        verdict = "LOCK WAIT, ACYCLIC — someone is queued; postgres will not deadlock-detect"
    elif idle_in_txn:
        verdict = "IDLE IN TRANSACTION — locks held while waiting on a CLIENT, not on postgres"
    elif working:
        verdict = "WORKING, NO LOCK WAIT — a flat progress counter here means SLOW, not stalled"
    else:
        verdict = "QUIESCENT — nothing active in this tenant"
    return {
        "cycle": cycle,
        "lock_waiters": lock_waiters,
        "idle_in_txn": idle_in_txn,
        "working": working,
        "verdict": verdict,
    }


def locks(con):
    """Per backend in THIS tenant: what it runs, what it HOLDS, what it WANTS, who blocks it.

    Each row is a `pg_stat_activity` row plus `held` / `wanted` lists of
    `{locktype, mode, target}`. Shared-memory reads only — see the section note.
    """
    held, wanted = {}, {}
    for r in rows(con, _LOCKS_SQL):
        d = {"locktype": r["locktype"], "mode": r["mode"], "target": r["target"]}
        (held if r["granted"] else wanted).setdefault(r["pid"], []).append(d)
    out = []
    for a in rows(con, _ACTIVITY_SQL):
        b = {k: a[k] for k in a.keys()}
        b["held"] = held.get(a["pid"], [])
        b["wanted"] = wanted.get(a["pid"], [])
        out.append(b)
    return out


def locks_report(con=None, sandbox=False):
    """`--locks` — the live-hang breakdown: HELD vs WANTED per backend, and the verdict.

    ⚑ EXIT CODE 1 ONLY ON A CYCLE. An acyclic lock wait and a busy backend are both normal
    states; a mode that exits non-zero for either would train its operator to ignore it, and
    the one thing this must be able to say loudly is the one thing that is impossible by
    construction here.
    """
    import store

    con = con or _cli_connect()
    bs = locks(con)
    v = wait_verdict(bs)
    for b in bs:
        print(
            "pid %-8s %-22s %-10s %-16s xact %s / query %s%s"
            % (
                b["pid"],
                b["state"],
                b["wait_event_type"] or "-",
                b["wait_event"] or "-",
                b["xact_age"] or "-",
                b["query_age"] or "-",
                "   ⚑ THIS READER" if b["is_self"] else "",
            )
        )
        if b["leader_pid"]:
            # ⚑ A PARALLEL WORKER IS NOT A SECOND CLIENT, and counting it as one inflates
            # every "how many things are running" figure by the degree of parallelism.
            print("    parallel worker of leader pid %s" % b["leader_pid"])
        if b["backend_xid"]:
            print("    WRITE TXN xid=%s — a kill ROLLS BACK this work" % b["backend_xid"])
        if b["blocked_by"]:
            print("    BLOCKED BY  %s" % ", ".join(str(p) for p in b["blocked_by"]))
        for label, ls in (("WANTS", b["wanted"]), ("HOLDS", b["held"])):
            if ls:
                print(
                    "    %-6s %s"
                    % (
                        label,
                        " · ".join(
                            "%s %s on %s" % (l["locktype"], l["mode"], l["target"]) for l in ls
                        ),
                    )
                )
        print("    %s" % (b["query"] or "").replace("\n", " "))
    print(
        "\n%d backend(s) in %s — working %d · lock-waiting %d · idle-in-txn %d"
        % (
            len(bs),
            (store.sandbox_dsn() if sandbox else store.dsn()).get("dbname", "?"),
            len(v["working"]),
            len(v["lock_waiters"]),
            len(v["idle_in_txn"]),
        )
    )
    if v["cycle"]:
        print("⚑⚑ WAIT-FOR CYCLE: %s" % " → ".join(str(p) for p in v["cycle"]))
    print("⚑ %s" % v["verdict"])
    return 1 if v["cycle"] else 0


# ⚑ THE STAGE ROSTER IS DATA, AND THE ZEROES ARE PART OF IT. Each entry is
# `(stage, marker)` where `marker` is a fragment of the statement THAT STAGE issues, from
# the code that issues it: `ht_seed`/`ht_step` (`sppf_db.build_ht_map`'s fixpoint),
# `pack-level` (`_pack_level_sliced`'s `_lvl_assign`), `a3-readback` (`promote_core_a3`
# stage 3). Rendered including the stages nobody is in — "no backend is packing" and "the
# classifier stopped recognising packing" are different facts, and only a zero row keeps
# them apart (`--control --constructs` records the same reasoning).
_PROMOTE_STAGES = (
    ("ht-seed", "CREATE TEMP TABLE _ht_map"),
    ("ht-step", "INSERT INTO _ht_map"),
    ("pack-level", "_lvl_assign"),
    ("a3-readback", "FROM obs_node WHERE core_id"),
)


def promote_stage(query):
    """Which promote stage a statement IS — or `None`, which is NOT a stage.

    ⚑ `None` MEANS UNRECOGNISED, NEVER "not promoting". A backend running something this
    roster does not name is a fact about the ROSTER; reporting it as idle would be the
    report-presence-never-absence defect at statement grain. The caller renders these
    separately as `other`, because they are exactly the backends that STARVE a promote
    without being one — which is what the 2026-08-23 investigation actually found.
    """
    q = (query or "").replace("\n", " ")
    for stage, marker in _PROMOTE_STAGES:
        if marker in q:
            return stage
    return None


def promotes(con):
    """In-flight promote backends, each named by its MODULE — `locks()` plus attribution.

    Each row is a `locks()` backend plus `stage` (see `promote_stage`) and `module` (from
    the backend's own `application_name`, published by `store.connect(label=…)`).

    ⚑ THE MODULE COMES FROM THE BACKEND, NOT FROM THE QUERY. `core_id` travels as a bound
    `$1` that `pg_stat_activity` renders unexpanded, so the statement text can say which
    STAGE a backend is in and can never say which MODULE. Deriving one from the other
    would be a guess wearing an answer's format.
    """
    out = []
    for b in locks(con):
        b = dict(b)
        b["stage"] = promote_stage(b.get("query"))
        app = (b.get("application_name") or "").strip()
        b["module"] = app or None
        out.append(b)
    return out


def promotes_report(con=None, sandbox=False):
    """`--promotes` — what the build is promoting right now, by module.

    ⚑⚑ THIS MODE EXISTS BECAUSE ANSWERING ITS QUESTION ONCE REQUIRED READING RAW
    `pg_stat_activity` (2026-08-23). Five `--promote-core` processes sat 1–3.5h at seconds
    of CPU; `--locks` correctly said `lock-waiting 0`, and the remaining question — *which
    module is each one on, and what is starving them* — had no reader at all, so the
    judgement happened in the turn. THE STANDING RULE names that as work, not a finding.

    ⚑ IT DOES NOT REPLACE `--locks`, IT KEYS ON A DIFFERENT THING. `--locks` partitions by
    WAIT STATE (who blocks whom); this partitions by WHOSE WORK IT IS. The 2026-08-23
    reading is the case that separates them: identical lock state across all five, and the
    whole finding was in the attribution.
    """
    import store

    con = con or _cli_connect()
    bs = promotes(con)
    v = wait_verdict(bs)

    mine = [b for b in bs if b["stage"] and not b["is_self"]]
    # ⚑ WORKERS FOLD UNDER THEIR LEADER, as `--locks` does — a parallel worker is not a
    # second promoter, and counting it as one inflates the figure by the degree of
    # parallelism (the same correction `locks_report` carries).
    leaders = [b for b in mine if not b["leader_pid"]]
    workers = {}
    for b in mine:
        if b["leader_pid"]:
            workers.setdefault(b["leader_pid"], []).append(b["pid"])
    other = [
        b
        for b in bs
        if not b["stage"]
        and not b["is_self"]
        and not b["leader_pid"]
        and (b["state"] or "") != "idle"
    ]

    for b in sorted(leaders, key=lambda r: str(r["query_age"]), reverse=True):
        # ⚑ AN UNLABELLED BACKEND IS `unattributed`, NEVER "no module". Connections opened
        # before the label reached `store.connect`, and any caller that passes none, land
        # here — a fact about what the backend published, not about what it is doing.
        print(
            "%-12s %-8s pid %-8s xact %s / query %s"
            % (b["stage"], "", b["pid"], b["xact_age"] or "-", b["query_age"] or "-")
        )
        print("    module   %s" % (b["module"] or "⚑ unattributed (no application_name)"))
        if workers.get(b["pid"]):
            print("    workers  %s" % ", ".join(str(p) for p in workers[b["pid"]]))
        if b["backend_xid"]:
            print("    WRITE TXN xid=%s — a kill ROLLS BACK this work" % b["backend_xid"])
        if b["blocked_by"]:
            print("    BLOCKED BY  %s" % ", ".join(str(p) for p in b["blocked_by"]))

    # ⚑⚑ THE `other` SECTION IS NOT DECORATION — IT IS THE OTHER HALF OF THE FINDING. The
    # backends that make a promote slow are typically NOT promotes (2026-08-23: a 1h13m
    # corpus census with 4 workers, and a 1h13m idle-in-transaction). A view showing only
    # promotes would have shown five healthy promoters and no reason for the wall clock.
    if other:
        print("\n  ── NOT promotes, sharing this tenant ──")
        for b in sorted(other, key=lambda r: str(r["query_age"]), reverse=True):
            print(
                "  pid %-8s %-10s query %s  %s"
                % (b["pid"], b["state"], b["query_age"] or "-", (b["module"] or "unattributed"))
            )
            print("      %s" % (b["query"] or "").replace("\n", " ")[:120])

    print(
        "\n  stages: %s"
        % " · ".join(
            "%s %d" % (s, sum(1 for b in leaders if b["stage"] == s)) for s, _ in _PROMOTE_STAGES
        )
    )
    print(
        "%d promote(s) in flight in %s — %d other backend(s) sharing the tenant"
        % (
            len(leaders),
            (store.sandbox_dsn() if sandbox else store.dsn()).get("dbname", "?"),
            len(other),
        )
    )
    unattributed = sum(1 for b in leaders if not b["module"])
    if unattributed:
        print(
            "⚑ %d promote(s) UNATTRIBUTED — the backend published no application_name; "
            "this is a fact about the connection, not about the module" % unattributed
        )
    if not leaders:
        # ⚑ THE EMPTY READING IS A FACT ABOUT THE QUERY. "No promote matched the roster in
        # this tenant at this instant" is what was measured; "no promotes are running" is
        # a claim it cannot support (wrong tenant, a stage the roster misses, a backend
        # between statements). Same distinction `summit` draws for a capability miss.
        print(
            "⚑ NO PROMOTE MATCHED in this tenant at this instant — not the same as "
            "'none is running' (see the stage roster above for what was looked for)"
        )
    print("⚑ %s" % v["verdict"])
    return 0


def growth_report(con=None):
    """`--growth` — on-disk size per relation; sees UNCOMMITTED writes `census` cannot."""
    # ⚑ `--census` COUNTS COMMITTED ROWS, SO A LONG WRITE READS AS ZERO — indistinguishable
    # from stalled. Measured: an 18-minute ingest transaction showed 0 across every
    # relation while the database was demonstrably growing on disk (user: "I can tell you
    # the database size is still growing"). An operator outside the tooling could see what
    # the tooling could not, which is the gap this closes.
    #
    # On-disk size counts pages written by an OPEN transaction, so it moves during the
    # write. It is not a row count and must never be reported as one — a relation's size
    # also includes dead tuples and free space.
    con = con or _cli_connect()
    rows_ = list(
        rows(
            con,
            "SELECT c.relname AS rel, pg_total_relation_size(c.oid) AS bytes "
            "FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
            "WHERE n.nspname='public' AND c.relkind='r' "
            "ORDER BY pg_total_relation_size(c.oid) DESC",
        )
    )
    total = 0
    for r in rows_:
        b = r["bytes"] or 0
        total += b
        print("  %-24s %10.1f MB" % (r["rel"], b / 1048576.0))
    print(
        "\n%.1f MB across %d relation(s) — ON DISK, including uncommitted pages;\n"
        "this is not a row count." % (total / 1048576.0, len(rows_))
    )
    return 0


def headroom_verdict(free, bar):
    """Does the volume admit the run? — the THREE-VALUED answer `--headroom` renders.

    ⚑ THREE VALUES, NOT TWO, AND THE THIRD IS THE POINT. `free is None` means the reader
    could not measure, which is NEITHER admit nor refuse. Collapsing it either way is the
    defect this whole mode kept reproducing: read as admit, an unmeasured bar becomes a
    cleared one; read as refuse, an unreadable filesystem becomes a full one. The first
    draft of the caller did the second and reported a space-recovering run as blocked.

    ⚑ EXTRACTED SO IT CAN BE CASED. Inline in the report it was reachable only by
    connecting to a live store, so the arithmetic that decides whether a 3.5 GB bar
    clears had no test at all.
    """
    if free is None:
        return "withheld"
    return "admits" if free >= bar else "refuses"


def headroom_report(con=None):
    """`--headroom` — free space on the store's volume vs the PROJECTED write.

    ⚑ THE QUESTION A LARGE RUN ACTUALLY ASKS, AND IT HAD NO READER. `--growth` reports
    what the store OWNS; a run needs to know whether the volume ADMITS what it is about
    to write. Those are different questions, and reading the first as the second is
    `footprint-is-not-headroom` — an instrument reporting its own footprint where
    headroom was asked reads healthy right up to the failure.

    ⚑ MEASURED 2026-08-18 (the incident this exists for): one full-corpus hash-aggregate
    held 34 GB of `pgsql_tmp` for 91 minutes and ENOSPC'd at 97%. A spilling query fills
    a volume WITHOUT STALLING ANYONE until it dies, so PSI and lock waits both read clean
    while the disk goes. Free space is the signal; nothing else sees it coming.

    ⚑ ASKED OF POSTGRES, NOT OF `df`. The server knows its own data directory and may sit
    on a different host or volume than the client — a client-side `df` answers about the
    WRONG FILESYSTEM and cannot tell you so.

    ⚑ THE PROJECTION IS DERIVED, NEVER TYPED. bytes/row is MEASURED from what `obs_node`
    already holds, then multiplied by the observations still unprojected. A hardcoded
    estimate here would be the stale-scalar defect this repo keeps paying down.
    """
    con = con or _cli_connect()
    # ⚑ BOTH IMPORTED IN-FUNCTION, LIKE EVERY SIBLING HERE — module scope binds neither.
    # `os` in particular: the first draft called `os.path.isdir(ddir)` at module scope,
    # which raised NameError inside a bare `except` and made the LOCAL-path test read as
    # False. The volume was readable the whole time; the tool reported it could not see it.
    import os
    import shutil as _shutil

    loc = list(rows(con, "SELECT setting AS dd FROM pg_settings WHERE name = 'data_directory'"))
    ddir = loc[0]["dd"] if loc else None

    dbsz = list(rows(con, "SELECT pg_database_size(current_database()) AS b"))
    db_bytes = (dbsz[0]["b"] or 0) if dbsz else 0

    # ⚑⚑ CATALOGUE ESTIMATES, NOT `count(*)` — AND HERE IT IS NOT EVEN A TRADE-OFF. This
    # scanned `obs_node` (127.7M) + `obs` (141.1M) = ~269M rows to compute a BYTES/ROW
    # PROJECTION, which is an estimate by construction: the ratio's precision is bounded by
    # the projection, not by the counts. Paying two full scans to feed an approximation is
    # the corpus-scale-for-a-cheap-answer defect at its purest, and it made a
    # headroom-before-a-big-run check cost what the run itself would.
    # ⚑ AND THE SPILL THIS MODE EXISTS TO FORESEE (34 GB of `pgsql_tmp`, 91 minutes, ENOSPC
    # at 97%) is exactly what a two-relation scan risks provoking. An instrument that can
    # cause the condition it measures is worse than none.
    pk = list(
        rows(
            con,
            "SELECT (SELECT n_live_tup FROM pg_stat_user_tables WHERE relname='obs_node') "
            "         AS packed, "
            "       (SELECT n_live_tup FROM pg_stat_user_tables WHERE relname='obs') "
            "         AS staged, "
            "       pg_total_relation_size('obs_node') AS onb",
        )
    )
    packed = (pk[0]["packed"] or 0) if pk else 0
    staged = (pk[0]["staged"] or 0) if pk else 0
    onb = (pk[0]["onb"] or 0) if pk else 0

    print("  data directory        %s" % (ddir or "(not reported by the server)"))
    print("  database size         %10.1f MB" % (db_bytes / 1048576.0))

    free = None
    if ddir and os.path.isdir(ddir):
        du = _shutil.disk_usage(ddir)
        free = du.free
        print("  volume total          %10.1f MB" % (du.total / 1048576.0))
        print(
            "  volume free           %10.1f MB   (%.1f%% used)"
            % (du.free / 1048576.0, 100.0 * du.used / du.total)
        )
    else:
        # ⚑ A LOCAL PATH THAT DOES NOT RESOLVE MEANS THE SERVER IS ELSEWHERE. Report that
        # as a fact about the READER, never as "no free space information exists" —
        # report-presence-never-absence, at the filesystem boundary.
        # ⚑⚑ THE FIRST DRAFT OF THIS BRANCH EXPLAINED THE GAP WITH A CAUSE IT HAD NOT
        # MEASURED, and the explanation sent the reader to the wrong place. It printed
        # "the server is on another host or in a container … ask on the server's host" —
        # an INFERENCE stacked on an observation. What the tool actually knows is that the
        # SERVER DID NOT REPORT `data_directory` (the role most likely lacks
        # `pg_read_all_settings`). Measured 2026-08-21: the DSN host is a unix socket and
        # the data directory sits one directory over from it, on THIS machine — so the
        # reader was sent to "the server's host", which was the host it was already on.
        #
        # ⚑ THE WITHHOLD IS THE VALUABLE HALF; THE CAUSAL STORY APPENDED TO IT IS WHERE
        # THE FABRICATION ENTERS. Same family as `--calls` reporting DEAD when it means
        # "not visible from this scope". So this branch now CONSULTS the locality evidence
        # it already holds instead of narrating a cause: a unix-socket DSN host is proof
        # the server is local, and the volume can be read beside it.
        # ⚑ `store` IS IMPORTED HERE, LIKE EVERY SIBLING IN THIS FILE — module-scope `store`
        # is bound inside the `__main__` block, so a module-level reference works at
        # dispatch and raises NameError from the selftest. `_cli_connect`'s own note
        # records this; my first draft referenced it at module scope behind a bare
        # `except`, which SWALLOWED the NameError and silently took the unreadable branch
        # on a machine where the volume was readable. A blanket except turned a wiring bug
        # into a false "cannot measure" — the same silent-miss shape as `getattr(…, {})`.
        import store

        h = (store.dsn() or {}).get("host")
        sock = h if (h and h.startswith("/") and os.path.isdir(h)) else None
        print("  volume free           the server did not report `data_directory` — the")
        print("                        connecting role most likely lacks `pg_read_all_settings`.")
        if sock:
            # ⚑ LOCALITY IS OBSERVED, NOT ASSUMED: a unix socket cannot be reached across
            # a host boundary, so its presence settles the question the missing setting left open.
            # ⚑ THE SOCKET DIRECTORY IS ITSELF ON THE VOLUME, so stat THAT rather than
            # guessing a sibling data-directory name. `pg-data` beside `pg-run` is one
            # deployment's convention, and a name typed here from one observation is the
            # stale-constant defect this file keeps paying down. What is needed is the
            # FILESYSTEM, and the socket path identifies it without naming anything.
            du = _shutil.disk_usage(sock)
            free = du.free
            print("                        ⚑ but the DSN host is a UNIX SOCKET, so the server is")
            print("                          LOCAL — reading the volume it sits on (%s):" % sock)
            print(
                "  volume free           %10.1f MB   (%.1f%% used)"
                % (du.free / 1048576.0, 100.0 * du.used / du.total)
            )
            print("                        ⚑ the SOCKET's volume. If the data directory is a")
            print("                          separate mount this is the wrong filesystem — the")
            print("                          setting that would settle it is the one withheld.")
        if free is None:
            print("                        ⚑ the volume is not readable from here. That is a fact")
            print("                          about THIS READER — it is NOT evidence the server is")
            print("                          remote, and it does not say the volume is short.")
            print("                        ⚑ so the ADMITS/REFUSES verdict below is WITHHELD,")
            print("                          not passed — an unreadable bar is not a cleared one.")

    print()
    if packed <= 0:
        print("  ⚑ obs_node is EMPTY, so bytes/row cannot be measured and no projection")
        print("    is honest. Project one core first — then this mode has a basis.")
        return 0

    bpr = onb / float(packed)
    remaining = max(0, staged - packed)
    projected = int(bpr * remaining)
    print(
        "  obs_node          %s row(s), %.1f MB  →  %.0f bytes/row  (MEASURED)"
        % (format(packed, ","), onb / 1048576.0, bpr)
    )
    print("  still unprojected %s observation(s)" % format(remaining, ","))
    print("  PROJECTED write   %10.1f MB   (bytes/row × unprojected)" % (projected / 1048576.0))

    # ⚑⚑ AND THE WRITE IS ONLY HALF THE LEDGER — READING IT ALONE INVERTS THE VERDICT.
    # The promote does not merely ADD durable rows; the drain RETIRES the staged rows it
    # made redundant, per core, and that half is far larger. Sizing a promote campaign as
    # net-new growth is the same one-sided reading as `footprint-is-not-headroom`, one
    # level up: it makes a SPACE-RECOVERING operation read as a space-consuming one and
    # refuses a run that would have freed the volume.
    #
    # ⚑ THIS IS WHY THE 2026-08-18 INCIDENT DOES NOT TRANSFER (operator, 2026-08-21:
    # "The difference between then and now is that then, we had no drain capability.
    # Now, we have and use it."). That ENOSPC was a single unbounded hash-aggregate with
    # nothing retiring behind it. The per-core promote→drain chain has no such shape: the
    # peak is ONE CORE's staged-and-durable overlap, not the campaign's total.
    ret = list(
        rows(
            con,
            "SELECT pg_total_relation_size('obs')  AS obsb, "
            "       pg_total_relation_size('edge') AS edgeb",
        )
    )
    stagedb = ((ret[0]["obsb"] or 0) + (ret[0]["edgeb"] or 0)) if ret else 0
    frac = (remaining / float(staged)) if staged else 0.0
    retire = int(stagedb * frac)
    print(
        "  PROJECTED retire  %10.1f MB   (obs+edge, prorated over the unprojected share)"
        % (retire / 1048576.0)
    )
    print(
        "  NET               %10.1f MB   %s"
        % (abs(retire - projected) / 1048576.0, "RECOVERED" if retire > projected else "consumed")
    )

    print()
    # ⚑ THE BAR IS PER-CORE, NOT PER-CAMPAIGN, BECAUSE THE UNIT IS PER-CORE. The chain
    # promotes and drains one core at a time, so what the volume must admit at any moment
    # is the largest single core's durable write plus spill room — never the whole run.
    # ⚑⚑ FROM THE STATISTICS, NOT A FULL `GROUP BY`. This aggregated all ~141M `obs` rows to
    # learn ONE number — the largest core's row count — and it was the remaining cost of this
    # mode after the count(*) pair above became catalogue reads. Measured 2026-08-23 under a
    # live build: 2m06s and still running.
    #
    # ⚑ `n_distinct` + `n_live_tup` GIVES THE MEAN; THE BAR WANTS THE MAX, so the estimate is
    # scaled by the most-common-frequency when ANALYZE recorded one. `most_common_freqs[1]` is
    # the fraction of the relation held by the single most common `core_id` — exactly "the
    # largest core's share" — and multiplying by the live tuple count yields its row count
    # without touching a heap page.
    #
    # ⚑ AND THE FALLBACK IS THE MEAN, NOT ZERO. A relation ANALYZE has not sampled yields no
    # MCF; reporting a 0-row largest core would make the bar 0 and turn this gate's verdict
    # into an unconditional ADMIT — an unmeasured bar read as a cleared one, which is the
    # exact two-valued collapse `headroom_verdict` exists to refuse. The mean is an
    # UNDER-estimate of the max, so it is flagged when used.
    tail = list(
        rows(
            con,
            "SELECT (SELECT n_live_tup FROM pg_stat_user_tables WHERE relname='obs') AS live, "
            "       (SELECT most_common_freqs[1] FROM pg_stats "
            "         WHERE tablename='obs' AND attname='core_id') AS mcf, "
            "       (SELECT n_distinct FROM pg_stats "
            "         WHERE tablename='obs' AND attname='core_id') AS nd",
        )
    )
    _live = (tail[0]["live"] or 0) if tail else 0
    _mcf = (tail[0]["mcf"] or 0) if tail else 0
    _nd = (tail[0]["nd"] or 0) if tail else 0
    if _mcf:
        tail_n = int(_live * _mcf)
    elif _nd and _nd > 0:
        tail_n = int(_live / _nd)  # mean — an UNDER-estimate of the max
    else:
        tail_n = 0
    peak = int(bpr * tail_n) * 3
    print(
        "  headroom bar      %10.1f MB   (3 × the LARGEST core's durable write —"
        % (peak / 1048576.0)
    )
    print(
        "                                   ~%s obs: the write, plus spill room)"
        % format(tail_n, ",")
    )
    # ⚑ WHICH ESTIMATOR PRODUCED THE BAR IS PART OF THE VERDICT. An MCF-derived figure really
    # is the largest core; a mean-derived one UNDER-states it, so an `ADMITS` resting on the
    # fallback is weaker than one resting on the MCF — and a reader cannot tell them apart
    # unless the mode says which it used. Naming the estimator keeps "measured and cleared"
    # distinct from "approximated and cleared", the same three-valued discipline
    # `headroom_verdict` enforces for the free-space half.
    if not _mcf and _nd:
        print(
            "    ⚑ from the MEAN core (ANALYZE recorded no most-common-frequency for "
            "obs.core_id),\n      so this bar UNDER-states the largest core — "
            "`ANALYZE obs` sharpens it."
        )
    elif not _mcf:
        print(
            "    ⚑ NO STATISTICS for obs.core_id — the bar is 0 and this verdict is "
            "UNSUPPORTED.\n      Run `ANALYZE obs` before trusting an ADMITS here."
        )

    verdict = headroom_verdict(free, peak)
    if verdict == "admits":
        print(
            "  → ADMITS the run: %.1f MB free ≥ %.1f MB bar" % (free / 1048576.0, peak / 1048576.0)
        )
        return 0
    if verdict == "refuses":
        print(
            "  ⚑ REFUSES the run: %.1f MB free < %.1f MB bar" % (free / 1048576.0, peak / 1048576.0)
        )
        print("    Drain the tail cores first, or add space.")
        return 1
    return 0
