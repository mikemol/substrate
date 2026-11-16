# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The QUEUE tier — watermarks, the consumer registry, reclamation, and the migration.

⚑⚑ WHY THIS IS A SEAM AND NOT A SIZE CUT. Every function here is POSTGRES-ONLY and every
one of them opens by calling `_require_pg`, which is defined at the top of this module.
That is the tier's precondition made structural: sqlite cannot express the in-flight
transaction floor, so it has no correct high-water mark, and a degraded variant would be
"a second semantics nobody audits" (the refusal `_require_pg` raises, kept verbatim).
A capability with ONE gate, and the gate travels with it.

⚑ THE OTHER HALF STAYED IN `schema.py` DELIBERATELY. The row/execute helpers (`rows`,
`scalar`, `execute`, `ph`, `upsert`) are backend-NEUTRAL and are what this tier is built
FROM — so the arrow runs queue → helpers, never back. `schema.py` re-exports everything
here, so `_schema.hwm`, `_schema.reclaim`, `_schema.drained`, `_schema.register` and the
rest resolve exactly as they did; `scripts/sppf_db.py` is the only external consumer of
this surface and was not touched.

⚑ THE ⚑ BLOCKS ARE VERBATIM. Nearly every function below carries a note recording the
measured incident that produced it — the 38-minute anti-join, the xid-wraparound
misreading, the pin that `PERSISTENT_READERS` calls *"catastrophic in fact"* to retype,
the 1,255,688-row drain that broke a fibre's density. Those notes are the arc's incident
log and are the more valuable half of what moved.

⚑ AND THE DEFERRED IMPORTS ARE PRESERVED EXACTLY. `import store as _store`,
`import lifecycle as _lc`, `import query_builders as QB` all stay inside the function
bodies that need them. `reconstruct.py` imports `schema`, so a module-scope import of
these would invert a direction the tree already relies on — the same reason those imports
were deferred before the move. Nothing was hoisted.
"""

import sys

# ⚑ FROM `schema_rows`, NOT FROM `schema`, AND THE DIFFERENCE IS WHAT MAKES THIS A DAG.
# Importing `schema` here would be a cycle — `schema` re-exports this module — and the
# first cut of this split did exactly that and failed with `ImportError: cannot import
# name '_require_pg'` on a half-initialised module. The helpers this tier is built from
# live one level down, so it reaches THERE and nothing reaches back.
from schema_rows import (
    rows,
    scalar,
    execute,
    ph,
    upsert,
    relations,
    columns_of,
    apply,
    Row,
    _cli_connect,
    _tier,
    _TIERS,
)

# ⚑ THE SHADOW POPULATION, FROM THE DECLARATION — `migrate_views` must not purge it. Imported
# from `schema_decl` and NOT from `schema` for the reason above: `schema` re-exports this
# module, so reaching up would be the cycle this file's own note records failing.
from schema_decl import SHADOWS


def _require_pg(what):
    import store as _store

    if _store.backend() != "postgres":
        raise NotImplementedError(
            "%s is postgres-only: sqlite cannot express the in-flight-transaction "
            "floor, so it has no correct high-water mark. A degraded variant would be "
            "a second semantics nobody audits." % what
        )


# ── `hwm` — THE HIGH-WATER MARK — DELETED 2026-08-12 WITH `obs.seq`. ───────────────────────
#
#     SELECT COALESCE(MAX(seq), 0) FROM obs WHERE age(xmin) > 0
#
# ⚑⚑ IT WAS ALREADY DEAD WHEN IT WENT: `pycodemod --calls hwm` → **1 def, 0 calls**. Its last
# caller was `--watermark`, which went with the registry. So this is not a capability being
# withdrawn; it is the `rewire_only` class, found by census rather than by argument.
#
# ⚑⚑ AND `age(xmin) > 0` IS NOT RELOCATED — IT IS DELETED, WHICH IS THE CORRECTION THAT COST
# THIS ARC TWO WRONG READINGS (user, 2026-08-12: *"It's not a meaningful metric; it's a scalar
# that gets mistaken for a field."*). `age(xmin)` is `current_xid − xmin`: a fact about the row
# **from the asking transaction's snapshot**, not a property of the row. Two readers get two
# answers for one row. Under MVCC an in-flight row is INVISIBLE to another transaction's
# snapshot, so the hazard a promote-side settledness filter would guard against cannot occur —
# the only thing the predicate can distinguish is the reader's own uncommitted inserts, which is
# the reader knowing about its own writes.
#
# ⚑ THE SUITE HAD BEEN PRINTING THE PROOF: `check("every settled row counts toward the hwm",
# count(WHERE age(xmin) > 0), count(*))` — two counts, equal on every run. That reads as a guard
# confirming the predicate sound; it is a TAUTOLOGY DRESSED AS A GUARD, which is `reflects_obs`'s
# shape (F0) recurring in the queue tier. It is deleted with the predicate.
#
# ⚑ WHAT WAS TRUE, AND ONLY IN THE AGGREGATE, so it is recorded rather than assumed recoverable:
# *"the HWM is the point below which no write transaction is still in flight, read from the
# engine's own snapshot rather than approximated"* is sound reasoning about a WATERMARK, where it
# genuinely differs from `max(seq)` because assignment order is not commit order. That
# boundary-over-a-SET was the only form carrying information, and it is precisely what is being
# deleted. **Per row there is no residue.**
#
# ⚑ THE MEASUREMENTS IT PRODUCED ARE WORTH KEEPING BECAUSE THEY REFUTED A DESIGN. *"A sequence
# guarantees monotonic ASSIGNMENT, never monotonic COMMIT — concurrent transactions may take 100
# and 101 with 101 committing first."* And: *"`xmin::text::bigint < pg_snapshot_xmin(...)` is
# UNSOUND UNDER WRAPAROUND — MEASURED, NOT REASONED. An xid is 32-bit and CIRCULAR, so `<` is not
# a total order on it; `'4294967290'::xid::text::xid8` carries the raw value through with NO
# epoch reconstruction, and `pg_visible_in_snapshot` then reports that ancient, long-committed
# transaction as NOT settled."* Any future xid comparison owes that: `age()`, never `<`.


# ── `lwm`, `consumers`, `register`, `advance` — DELETED 2026-08-12 WITH THE `consumer`
#    TABLE. Retain-until-consumed is retired; reconstruct-on-demand replaced it. ────────────
#
# `lwm` was `MIN(lwm)` over the registry — the reclamation floor. `consumers` listed the
# registry with each cursor's lag. `register` inserted a reader at 0 with `ON CONFLICT DO
# NOTHING`. `advance` moved one cursor forward. Four functions over one column, and the column
# is gone: `reclaim` runs `q_drainable_res`, which answers PER CORE whether the durable tier
# can rebuild it, and consults no registry at all.
#
# ⚑⚑ THE EMPTY-REGISTRY RULE IS THE ONE TO CARRY FORWARD, because it is about NULL and not
# about queues. `lwm`'s note: *"AN EMPTY REGISTRY RECLAIMS NOTHING, NEVER EVERYTHING. `MIN()`
# over no rows is NULL, and reading NULL as 'no constraint' would license deleting the whole
# corpus the first time the registry is empty."* Any future aggregate that BOUNDS A DELETION
# owes exactly this: absent-read-as-permission is the one failure mode that cannot be undone.
#
# ⚑⚑ AND `lwm` WAS RIGHT ABOUT THE PIN WHILE BEING THE WRONG INSTRUMENT FOR IT. Its note —
# *"A `pin` MUST STAY IN THE MIN, AND I ALMOST SCOPED IT OUT (2026-08-07) … `obs` serves TWO
# roles — an append-only LOG the projection drains, and a persistent JOIN TABLE resolvers
# reconstruct from … 'A reclaim that saw only the first would delete the corpus out from under
# the second — correct per the queue contract, catastrophic in fact.'"* — states a TRUE fact
# about `obs` that a scalar `MIN()` could only express by freezing the whole tier. The
# two-roles finding survives; the floor that could only answer it for the entire chain at once
# does not.
#
# ⚑ `register`'s IDEMPOTENCE ARGUMENT IS THE OTHER SURVIVOR: *"a re-register that zeroed `lwm`
# would make a consumer re-read the corpus — merely wasteful — but one that set it to the HWM
# would make it SKIP everything pending, which is silent loss."* The general rule is that an
# idempotent registration may declare that a reader EXISTS and must never assert where it has
# got to. Nothing writes a position now, so there is nothing to assert wrongly.
#
# ⚑ AND `register`'s TWO RETYPE GUARDS (deleted one step earlier) left the rule the licence is
# built on: **a precondition validated in a separate statement from the write it protects is
# advisory, whatever it is called** (user, 2026-08-11: *"TOCTOU"*). That is why
# `q_drainable_res` is ONE conjunction over ONE snapshot rather than six composed world-states.
#
# ⚑ `advance`'s FORWARD-ONLY GUARD WAS A PARTIAL FIX FOR A RACE A DERIVED FRONTIER CANNOT
# HAVE — `lifecycle.py`'s standing note says so and is kept there verbatim. Two projections
# racing on `UPDATE consumer SET lwm` could move the frontier BACKWARD past committed work;
# a computed frontier has no second write to order.


# ── `advance_readers` — WRITTEN AND RETIRED IN ONE SESSION (2026-08-11). ──────────────────
#
#     Advance every declared reader whose REPLACEMENT RELATION this run just rebuilt.
#
# ⚑⚑ IT WAS THE MISSING HALF OF `_READER_NEEDS` **UNDER THE POSITIONAL MODEL**, and that
# model is what went. The gap it closed is real and is worth keeping written down:
# `_READER_NEEDS` names what a pin's consumer must read INSTEAD of the raw log, and
# `register()` refuses the pin→cursor retype while that relation is empty — but both halves
# are about the RETYPE, and NOTHING then moved the resulting cursor. `lwm = MIN(lwm)` over
# the registry, so a retyped-but-never-advanced reader pins the floor at 0 exactly as the pin
# did. MEASURED on the live store: `hwm 6,274,182 / lwm 0 / 0 observation(s) below the floor`,
# a full tier with one consumer registered.
#
# ⚑ IT IS DELETED RATHER THAN KEPT BECAUSE THE FLOOR IT SERVED NO LONGER EXISTS (user,
# 2026-08-11: *"under IF NOT EXISTS, hwm and lwm are boolean predicates"*). `q_drainable_res`
# states the licence PER CORE over the durable tier, so there is no `MIN(lwm)` to lift and no
# cursor to move; `pycodemod --calls advance_readers` read **1 def, 0 calls** the moment the
# converge loop stopped advancing. Keeping it would be a capability whose only purpose is to
# make a retired scalar honest — the `rewire_only` shape, added deliberately.
#
# ⚑ AND THE ARGUMENT IT ENCODED SURVIVES, ONE LAYER DOWN. Its claim was *"the reader's
# criterion after the migration is `ref` describes the corpus, not a position in `obs`"*. In
# the residue licence that is the `projected` conjunct: `project_ref` writes `ref` in the same
# promote that writes `obs_node`, so "the reader has what it needs" is not a second fact to
# track — it is the same fact, per core, already in the conjunction.


# ── `reclaimable` — DELETED 2026-08-12 with the floor it counted against. ──────────────────
#
#     How many observations sit below the reclamation floor — the GC's real population.
#
# ⚑ ITS QUESTION SURVIVES AND IS ANSWERED BETTER. Its note read: *"Reported rather than
# deleted: this answers 'is a sweep worth running at all', which the 38-minute anti-join could
# never be asked."* That question is now `reclaim(dry_run=True)` — which reports the rows the
# per-core licence admits, not the rows below a scalar — and `--lifecycle`, which LOCATES why
# each row is held instead of collapsing the tier to one count.
#
# ⚑ AND OF THE THREE PROPERTIES THE WATERMARK WAS CREDITED WITH, THIS WAS THE *askable* ONE
# (see `reclaim`'s note). *Interruptible* was always the DELETE's atom being a whole fibre;
# only *bounded-by-`budget`* ever belonged to the floor, and it went with it.


# ── `PERSISTENT_READERS` — DELETED 2026-08-12, and it was RIGHT about everything but the
#    instrument it was forced to use. ──────────────────────────────────────────────────────
#
# It held `("scope_fix:resolver",)`: consumers whose liveness criterion is the SOURCE, not a
# position — *"if the source exists I need the data; don't delete what is real, but don't keep
# what is stale."* Its own notes called the pin the wrong instrument while using it: *"pinning
# at 0 delivers 'don't delete what is real' and silently breaks 'don't keep what is stale' — a
# deleted core's rows would be preserved forever by the very mechanism meant to protect the
# reader. Position-based reclamation cannot express this at all: staleness here is not an
# ordering, it is a JOIN against the source."*
#
# ⚑⚑ SO THE CONSTANT DIAGNOSED ITS OWN REPLACEMENT AND THEN LIVED FOR ANOTHER SIX DAYS AS THE
# THING IT CRITICISED. The per-core licence IS the JOIN it asked for; the roster was a scalar
# workaround kept because nothing had been built to make it unnecessary.
#
# ⚑ ITS SECOND ⚑ BLOCK WAS REFUTED BY ⓝ AND NOBODY REVISITED IT. It argued the reader could
# never move off the raw log because *"node identity there is depth-1 `sym ‖ child-SYMS`, so a
# module applied twice packs both carriers onto every argument position — a resolver reading
# the projection is unsound BY CONSTRUCTION."* ⓝ made the node key CONTENT-COMPLETE, and
# `scope_fix` now reads `ref ⋈ path_text ⋈ terms`. MEASURED before deleting: `--sql obs` over
# `scope_fix`/`scope_store`/`scope_source` → **0 sites**; `--literal obs_all` → consumed only
# by `project_sppf`/`project_orbit_sppf`. The constant outlived the claim that justified it.
#
# ⚑ AND IT WAS ASSIGNED TWICE, BYTE-IDENTICALLY (F5, at :352 and :366), FOR THE WHOLE ARC. The
# first assignment's value was unobservable and its doc-block orphaned from any binding — so
# one of the two ⚑ arguments above was attached to a name nothing could read. Recorded because
# the census that found it (`--binding`) ran months of edits after the duplication landed.
#
# ⚑ WHAT SURVIVES, AND IT IS THE PART TO CARRY FORWARD: source-driven reclamation is already
# implemented and already correct — `write_events` derives `removed = [c for c in stored if c
# not in cur and c in mine]` and hands it to `_delete_core_rows`. That is the JOIN-against-the-
# source this constant wanted, and it never needed a queue position to work.

# ── `_READER_NEEDS` — DELETED 2026-08-12. Its precondition was MET, not abandoned. ──────────
#
# It held `{"scope_fix:resolver": "ref"}` so `register()` could REFUSE to retype the pin while
# its replacement relation was absent or empty — "a pin is retired when its consumer has
# somewhere else to read", encoded rather than remembered. That was the right shape and it did
# its job: `scope_fix` now reads `ref ⋈ path_text ⋈ terms`, and `--sql obs` over
# `scope_fix`/`scope_store`/`scope_source` returns **0 sites**.
#
# ⚑ IT IS DELETED BECAUSE THE TRANSITION IT GATED NO LONGER EXISTS, NOT BECAUSE THE RULE WAS
# WRONG. There is no pin→cursor retype to refuse once there is no floor for a cursor to lift.
# The general form — *name the replacement relation in code so an ordering cannot live only in
# a plan document* — is worth reaching for again the next time a reader is migrated.


# ── `_repair_registry` and `pin_persistent` — DELETED 2026-08-12 with the floor they served ──
#
# `pin_persistent` registered every `PERSISTENT_READERS` entry at 0 so `lwm() = MIN(lwm)` could
# never rise; `_repair_registry` put those rows back when the suite deleted them. Both existed
# to keep a POSITION honest, and there is no position any more: `reclaim` runs `q_drainable_res`,
# which answers per core whether the durable tier can rebuild it.
#
# ⚑ `_repair_registry` WAS ALREADY DEAD IN PRODUCTION AND NOBODY HAD LOOKED. Censused before
# deleting: **1 def, 1 call — and the call is in the SUITE.** A repair mechanism whose only
# caller is the test that damages the thing it repairs is a closed loop, not a safety net.
#
# ⚑ AND ITS BEST ARGUMENT SURVIVES THE DELETION, WHICH IS WHY IT IS QUOTED RATHER THAN LOST:
# *"a cursor's position is a PROMISE about what it has consumed — this function must never
# invent one, because a fabricated cursor either re-reads the corpus (wasteful) or skips
# pending rows (silent loss)."* That is still the rule for anything that writes `consumer.lwm`.
# What changed is that nothing needs to write a 0 there to protect the log.


#: Lifecycle links the census's POPULATION witnesses, so no CASE arm can describe their failure.
#
# ⚑ `lifecycle_census`'s population is `FROM obs` — the append-only log — and `_observed` is
# *"it has an ADDRESS in the log"*. Every row the census can return therefore satisfies that
# link BY CONSTRUCTION; an `'unobserved'` arm would be a CASE over the population's own
# defining property, which is a vocabulary entry rather than a stage. The arm existed anyway
# until 2026-08-12 (as `o.seq IS NULL`, over a `NOT NULL` column) and could never fire.
#
# ⚑⚑ IT IS DECLARED RATHER THAN INFERRED BECAUSE INFERRING IT PASSED ON A COMMENT. The guard in
# `schema_selftest` derives `"un" + link` for every declared link and requires the census to
# compute it; with the arm deleted, `unobserved` survived in ZERO string literals tree-wide
# (`pycodemod --literal unobserved`: 0 sites in 0 of 695 files) and the case still passed,
# because the guard scanned `inspect.getsource` — source TEXT — and the retirement note above
# the SQL contains the word. Third recorded instance of a retirement note satisfying a scan
# written to catch the second. The guard now anchors on the SQL's string constants (comments
# are dropped by `ast` BY CONSTRUCTION) and reads this roster for what the population supplies.
POPULATION_SUPPLIES = ("observed",)


def lifecycle_census(con=None):
    """Every observation's LIFECYCLE STAGE, counted — the model's own answer to
    "what is held, and by which constraint".

    ⚑ THIS REPLACES A SCALAR WITH A LOCATED ONE. `reclaimable()` returns a count, and a
    count cannot distinguish "held because its source is gone" from "held because a
    consumer has not advanced" — different facts, different remedies, and the 38-minute
    anti-join could report neither. `lifecycle.LIFECYCLE` locates the rejection at a
    named link, so the census reports WHERE each row is held.

    ⚑ THE STAGES ARE COMPUTED IN SQL, NOT PER-ROW IN PYTHON. Pulling 506k rows to
    evaluate four predicates would be the relational-algebra-withheld-from-the-engine
    defect this store exists to stop; the chain's links are expressible as columns, so
    the engine groups them.
    """
    _require_pg("lifecycle_census()")
    import store as _store
    import lifecycle as _lc

    if con is None:
        con = _cli_connect(mode="rw")
    # ── THE `consumed` STAGE AND ITS `floor` — DELETED 2026-08-12 WITH THE REGISTRY. ─────────
    #
    # The CASE below carried `WHEN %s IS NULL OR o.seq >= %s THEN 'unconsumed'`, bound from
    # `floor = lwm(con)`. Two ⚑ notes stood here and both are kept because they record the
    # step-by-step retreat of one mechanism:
    #
    # ⚑ *"`pin_persistent(con)` STOOD HERE AND WAS THE CENSUS'S LAST PRODUCTION CALLER. It made
    # the `consumed` stage honest by ensuring the pin was registered before `lwm` was read — a
    # check-then-act ordering defended as a design."* Then, one step later: *"With the pin gone
    # the floor below is a DIAGNOSTIC only … and the DRAIN no longer consults it."*
    #
    # ⚑⚑ A DIAGNOSTIC WHOSE ONLY INPUT IS A TABLE NOTHING ELSE WRITES IS NOT A DIAGNOSTIC —
    # it is the self-referential remainder the queue tier had become. With `consumer` gone
    # `lwm` is None by construction, so the branch would report EVERY row `unconsumed` and
    # every later link would be unreachable: the census would say the tier is held by a
    # constraint that no longer exists. Deleting the link is what keeps the census honest.
    #
    # `sourced` is a JOIN against the source of truth (core_fp), not a position — which
    # is exactly why the watermark alone could not express it.
    # ⚑⚑ THE FIFTH LINK WAS MISSING AND THE FOURTH WORE ITS NAME. This CASE stopped at
    # `'reclaimable'` — four predicates for a five-link chain — so `reflected` was DECLARED in
    # `lifecycle.LIFECYCLE` and computed nowhere, and `lifecycle._reflected` sat at 1 def /
    # 0 calls reading a key nothing set. A row past the consumer floor was reported
    # `reclaimable` on the QUEUE predicate alone, which is precisely the conflation
    # `Substrate.Lifecycle.Reflection` warns of: *"a cursor advancing is not a durable
    # artifact"*, and `Drainable`: *"'the data is elsewhere' is not enough."*
    #
    # ⚑ IT IS EXPRESSIBLE NOW BECAUSE Ⓒ1 GAVE `ch` A HOME. Reflection needs the durable side
    # to DETERMINE the staged one (`drainable`'s injectivity hypothesis); before `obs_node.ch`
    # that was false for 43.8% of rows and no SQL could have said otherwise. The predicate
    # here is the per-core determinacy — a core whose `(node_id, ch)` addresses two ekeys is
    # NOT reflected, whatever its position.
    #
    # ⚑ AND `reclaimable` NOW MEANS WHAT IT SAYS. It is the conjunction the drain actually
    # needs, not the queue floor wearing the drain's name.
    # ⚑⚑⚑ THE STAGE MAY NOT EXIST YET, AND ASSUMING IT DOES BROKE THE READER EXACTLY WHEN IT
    # WAS NEEDED.  `obs_node` is created by a LATER stage of the pipeline, so on a
    # partially-built store this query raised `UndefinedTable: relation "obs_node" does not
    # exist` — i.e. **the mode that reports where the pipeline stands crashed BECAUSE the
    # pipeline is early.**  Measured 2026-08-14 on the live store: 23 of 31 relations present,
    # event tier populated (6.27M obs), `obs_node` absent, `--lifecycle` dead.
    #
    # ⚑⚑ AND THAT IS THE WORST PLACE FOR THIS ASSUMPTION.  A lifecycle census exists to answer
    # "how far has this got"; a store that has not got far is its PRIMARY case, not an edge one.
    # The reader was usable only once its own answer had stopped being interesting.
    #
    # ⚑ `census(con)` ALREADY DISTINGUISHES ABSENT (`None`) FROM EMPTY (`0`) — `schema_diag`
    # prints `-` vs `0` off exactly that.  So presence is not a new capability here, it is one
    # this reader declined to use.  An absent stage reports as an EMPTY ambiguity set: no core
    # can be ambiguous on a relation that does not exist, which is the truthful reading and not
    # a suppression.
    # ⚑ THE FIX IS ONE SUBSTITUTED CTE, NOT A SECOND CENSUS.  A first cut branched to a
    # `_lifecycle_census_without()` — a parallel implementation of the same chain, i.e. the
    # two-bodies-one-name shape this repo retires on sight, and the two would drift the moment
    # either predicate changed.  The absent stage contributes an EMPTY ambiguity set; every
    # other link is computed identically, by the same SQL, in both cases.
    # ⚑ `relations()` IS THE EXISTING PRIMITIVE and a second existence-check would be a third
    # spelling of one question (`census` already reads it to print `-` vs `0`).
    #
    # ⚑⚑ THE STAGE IS REFERENCED TWICE AND THE FIRST FIX ONLY FOUND ONE — the traceback named
    # the CTE, I patched the line it named, and the SAME query joined `obs_node` again forty
    # lines further down for the `'unprojected'` verdict.  Fixing the line an error points at,
    # rather than reading the statement it sits in, is how a two-site defect ships as fixed.
    _have_nd = "obs_node" in relations(con)
    _amb = (
        "  SELECT o.core_id FROM obs o JOIN obs_node n "
        "      ON n.core_id = o.core_id AND n.local_id = o.local_id "
        "   GROUP BY o.core_id, n.node_id, n.ch HAVING count(DISTINCT o.ekey) > 1"
        if _have_nd
        # ⚑ UNTYPED, same reason as `_nd` below — `obs.core_id` is TEXT and a `::bigint`
        # placeholder here failed identically. I fixed the join first and left THIS cast,
        # because the traceback named only the join: the same one-site-at-a-time reading
        # twice in one repair.
        else "  SELECT NULL AS core_id WHERE false"
    )
    # ⚑ AND THE ABSENT-STAGE READING IS THE TRUTHFUL ONE, NOT A SUPPRESSION.  `nd` drives the
    # `'unprojected'` arm, so with no `obs_node` every row is `nd.core_id IS NULL` — i.e. every
    # observation IS unprojected, which is exactly the state of a store whose projection stage
    # has never run.  The degenerate join reports that rather than hiding it.
    _nd = (
        "  LEFT JOIN obs_node nd ON nd.core_id = o.core_id AND nd.local_id = o.local_id "
        if _have_nd
        # ⚑ NO CASTS, AND `ON false` RATHER THAN A COLUMN COMPARISON.  A first cut wrote
        # `NULL::bigint AS core_id` and postgres refused it — `operator does not exist:
        # bigint = text`, because `obs.core_id` is TEXT and the placeholder guessed a type.
        # The empty side needs no types at all: `ON false` never evaluates the comparison,
        # so the join is degenerate by construction and cannot disagree with the real
        # column's type however that column is later declared.
        else "  LEFT JOIN (SELECT NULL AS core_id, NULL AS local_id WHERE false) nd ON false "
    )
    rows_ = list(
        rows(
            con,
            "WITH amb AS (" + _amb + ") "
            # ── `'unobserved'` (`o.seq IS NULL`) — DELETED 2026-08-12 WITH `obs.seq`. ────────────
            #    ⚑ IT COULD NEVER FIRE, AND THAT WAS TRUE BEFORE THE COLUMN WENT. `seq` was
            #    `nullable=False`, so `o.seq IS NULL` is false for every row the census can read;
            #    the population is `FROM obs`, which means every row is observed BY CONSTRUCTION.
            #    A CASE arm over the population's own defining property is a vocabulary entry, not
            #    a stage — the census has been publishing a six-name chain of which one name was
            #    unreachable.
            # ── `'unsettled'` (`age(o.xmin) <= 0`) — DELETED 2026-08-12 WITH THE `settled` LINK. ─
            #    ⚑⚑ IT WAS A READER-RELATIVE SCALAR IN A COLUMN'S CLOTHING (user: *"It's not a
            #    meaningful metric; it's a scalar that gets mistaken for a field."*). `age(xmin)`
            #    is `current_xid − xmin` — a fact about the row FROM THE ASKING TRANSACTION'S
            #    SNAPSHOT, so two readers get two answers for one row and neither is a property of
            #    the row. Under MVCC the population `FROM obs` is already only rows this snapshot
            #    can SEE, and a row you can see is committed: the arm could fire for nothing except
            #    the census's own uncommitted inserts, which is the reader knowing about its own
            #    writes.
            #    ⚑ SAME SHAPE AS THE `'unobserved'` ARM BELOW IT, one square further out. That one
            #    tested the population's defining property (`seq IS NULL` over `FROM obs`); this one
            #    tests the SNAPSHOT's defining property. Both are CASE arms over something that is
            #    true by construction of the query they sit in.
            "SELECT CASE "
            "  WHEN cf.core_id IS NULL THEN 'unsourced' "
            "  WHEN nd.core_id IS NULL THEN 'unprojected' "
            "  WHEN a.core_id IS NOT NULL THEN 'unreflected' "
            "  ELSE 'reclaimable' END AS stage, count(*) AS n "
            "FROM obs o "
            "  LEFT JOIN core_fp cf ON cf.core_id = o.core_id "
            + _nd
            + "  LEFT JOIN (SELECT DISTINCT core_id FROM amb) a ON a.core_id = o.core_id "
            "GROUP BY 1 ORDER BY 1",
        )
    )
    # ⚑⚑ `supplied` NAMES THE LINK THE POPULATION ITSELF WITNESSES, AND WITHOUT IT THE GUARD
    # OVER THIS CENSUS PASSED ON A COMMENT. `schema_selftest` asks that every link the chain
    # declares gets a stage here, deriving `"un" + link` and scanning — and it scanned
    # `inspect.getsource`, i.e. source TEXT. `unobserved` has appeared in ZERO string literals
    # anywhere in the tree since the arm was retired (`pycodemod --literal unobserved`: 0 sites
    # in 0 of 695 files), yet the case passed, because the retirement COMMENT above contains
    # the word. That is the obituary-satisfies-a-scan class this repo has now recorded three
    # times, and the third instance was inside a guard written for the second.
    #
    # ⚑ AND THE HONEST FACT IS NOT "the census is incomplete". The population is `FROM obs` —
    # the log — so every row it can return is `observed` BY CONSTRUCTION. There is no datum for
    # an `unobserved` arm to describe, which is why the arm was deleted rather than fixed. What
    # was missing is that the census never SAID so, leaving the guard to infer it from prose.
    # Declared in `POPULATION_SUPPLIES` above, so the check can anchor on the SQL and stay total.
    return {
        "stages": [(r["stage"], r["n"]) for r in rows_],
        "chain": _lc.LIFECYCLE.names(),
        "supplied": list(POPULATION_SUPPLIES),
    }


# ── `_unreflected_floor` — RETIRED 2026-08-11 (⓶). Kept as a comment, not a function. ──────
#
#     The lowest `seq` belonging to a core that does NOT reconstruct — or None if all do.
#
# It computed a chain-wide scalar by looping cores, calling `reflects()` on each, and
# BREAKING at the first failure — so one unreconstructible low core held every drainable
# core above it. `query_defs.q_drainable`'s `determined` conjunct now excludes exactly the
# failing cores, in the same statement as the queue predicate, with the floor bound at
# execution.
#
# ⚑ THE DEBT WAS NAMED IN ITS OWN DOCSTRING AND LEFT UNPAID FOR DAYS, which is the part
# worth keeping. It said: *"the honest predicate is now a SET DIFFERENCE, not a floor"* —
# and then, of its own earlier claim that the loop could not be SQL: *"REFUTED BY ASKING
# POSTGRES (user: 'Have you SEEN the builtins SQL engines have these days?'). It is neither
# honest nor a boundary — it is a fact about what I reached for, reported as a fact about
# the substrate."* The measurement that refuted it:
#
#     convert_from(decode(ekey,'base64'),'UTF8')::jsonb ->> 'c'   → 'Id'
#     jsonb_array_elements_text(j->'ch') WITH ORDINALITY          → (child, ord)
#
# ⚑ AND WHAT FINALLY MADE IT BUILDABLE WAS DATA, NOT EFFORT. The determinacy half needs
# `(node_id, ch)`, and `ch` had no home above tier 0 until Ⓒ1 added `obs_node.ch` — before
# that the conjunct was false for 43.8% of rows and no query could have said otherwise.
# A debt can be correctly diagnosed and still be unpayable until a carrier exists.
#
# ⚑ THE REFUSAL IT CARRIED IS PRESERVED, NOT DROPPED. A missing checker was a REFUSAL (floor
# 0), never a fall-through to the queue predicate alone. `reclaim` now refuses one level
# earlier and on the same grounds: if `obs_node` is absent the reflection conjunct cannot be
# evaluated at all, and the sweep returns `UNMEASURED, not reconstructible` — the rule asked
# of the relation rather than of an import.


# ── `_reclaim_residue` — FOLDED INTO `reclaim` 2026-08-12. Kept as a note, not a function. ──
#
# It ran the residue licence beside the positional one, reached by `reclaim(residue=True)`,
# and duplicated the DELETE, the bounded event tail and the return shape so the two licences
# could share a sweep. With the positional licence retired there is one licence, so the
# second entry point is a fork with nothing on the other side of it.
#
# ⚑ THE DIVERGENCE IT WAS HIDING IS THE PART WORTH KEEPING. `converge._do_retire` — the
# production drain — passed `residue=True`, while `--reclaim` defaulted to `residue=False`.
# So the two paths ran DIFFERENT LICENCES against the same store, and the CLI's answer (`0
# observation(s) below the floor`) described a mechanism the loop was not using. A flag whose
# two settings are two designs is not a flag; it is an unfinished migration wearing one.


def reclaim(con=None, chunk=50_000, budget=None, dry_run=True):
    """Retire every core the durable tier can rebuild — the GC, with NO stored position.

    ⚑⚑ THE POSITIONAL LICENCE IS GONE, AND WITH IT THE PIN'S HOLD ON THE DRAIN (2026-08-12,
    user: *"It was the wrong design, and it's still dragging us backwards"*). This ran
    `pin_persistent` → `lwm()` → `floor` → `q_drainable`; it now runs `q_drainable_res` —
    the SAME conjunction with the one positional conjunct deleted. There is no floor to
    compute and therefore no floor for a pin to hold.

    ⚑⚑ WHAT THE FLOOR WAS COSTING, MEASURED ON BOTH STORES BEFORE THE CHANGE. The pin sets
    `scope_fix:resolver` to 0, so `lwm() = MIN(lwm) = 0` and `HAVING max(seq) < 0` is false
    for every core: `--watermark` reported **0 observation(s) below the floor** against
    `hwm 6,274,182` live and `hwm 627,327` on the sandbox. It was not inert debt — it was
    the reason a full tier could never drain at all.

    ⚑ AND THE PIN WAS RIGHT ABOUT ITS OWN QUESTION; THE FLOOR IS WHAT COULD NOT EXPRESS IT.
    `obs` genuinely serves two roles — a drainable LOG and a persistent JOIN TABLE — and a
    scalar `MIN(lwm)` can only answer "may anything be deleted" for the whole chain at once.
    The three surviving conjuncts answer it PER CORE and exactly, which is what makes the
    two-roles finding expressible instead of merely true.

    ⚑ THE REPLACEMENT'S PRECONDITION IS VERIFIED, NOT INHERITED. `projected` carries the
    pinned reader's release only if `ref` is written by the SAME promote as `obs_node` —
    checked at both call sites rather than taken from a docstring: `sppf_db.build` runs
    `project_sppf` then `project_ref`, and `converge._do_promote` runs
    `project_sppf(additive=True)` then `project_ref(additive=True)`. Nothing writes one
    without the other. Independently: `--sql obs` over `scope_fix`/`scope_store`/
    `scope_source` returns **0 sites**, and `--literal obs_all` shows the builder-layer
    reader consumed only by `project_sppf`/`project_orbit_sppf`.

    ⚑ AND `converge` — THE PRODUCTION DRAIN — WAS ALREADY ON THIS LICENCE (`_do_retire`
    passed `residue=True`). So the positional path was never the shipping behaviour it
    looked like; it was the CLI default, diverging from the loop that actually runs.

    ⚑ THE PARAMETER IS DELETED, NOT INVERTED. A `residue=False` left standing keeps the
    floor one boolean away from the sweep that deletes rows — the argument
    `store.connect`/`sandbox_connect` are kept as separate entry points for.

    ⚑⚑ THIS PARAGRAPH WAS OVERTAKEN TWICE AND IS KEPT AS THE RECORD OF THAT. It read: *"WHAT
    THIS DOES NOT RETIRE: the `consumer` registry's IDENTITY — who exists, of what kind — is a
    DECLARATION and stays, as does `--watermark` reporting it."* Both halves are now false —
    `--watermark` went with `lwm`/`consumers`, and the `consumer` TABLE was dropped on
    2026-08-12. Each retreat was defended as stopping at the previous one, and none did. **The
    transferable form: when a subsystem's last remaining justification is that it DECLARES
    something, check who READS the declaration** — here, nothing did, and the registry existed
    so that `--watermark` could print the registry.

    ⚑ THE ANTI-JOIN THIS ALL REPLACED IS STILL WHY THE EVENT TAIL IS SPELLED `NOT EXISTS`.
    `DELETE FROM event WHERE ekey NOT IN (SELECT ekey FROM obs)` was MEASURED at 38 minutes
    on the live store, spilling to disk, having modified ZERO rows before it was cancelled:
    `NOT IN` over a 506k-row subquery cannot use the index, because NULL semantics forbid
    it. That lesson survives the floor that was introduced alongside it.

    ⚑ AND OF THE THREE PROPERTIES THE WATERMARK WAS CREDITED WITH, TWO WERE NEVER ITS.
    *Interruptible* is the DELETE's atom being a whole fibre (a kill loses the transaction,
    never half a core); *askable* is `reclaimable()`, which now reports the residue. Only
    *bounded-by-`budget`* belonged to the floor, and `chunk`/`budget` are vestigial here —
    named rather than quietly dropped, because a parameter that no longer bounds anything
    is a claim the signature is still making.
    """
    _require_pg("reclaim()")
    import store as _store
    import query_builders as QB

    # ⚑ `rw` EVEN FOR A DRY RUN — no longer because pinning is a write (it is not called
    # any more), but because `_cli_connect`'s read-only default would refuse the DELETE on
    # the apply path and the two must resolve the same store the same way.
    if con is None:
        con = _cli_connect(mode="rw")
    # ⚑⚑ THE `obs_node`-ABSENT REFUSAL, AND IT IS THE ONE THING THAT MUST NOT BE OPTIMISED
    # AWAY. Without the addressing relation the reconstruction conjuncts cannot be
    # EVALUATED — which is `UNMEASURED, not reconstructible`. A residue licence that fell
    # through to "nothing excludes it, so drain it" would delete the corpus, and
    # absent-read-as-permission is the one failure mode that cannot be undone.
    #
    # ⚑ IT FIRES TODAY, on the live store: `--reclaim` there returns exactly this, because
    # live has never been re-ingested and holds no `obs_node`. That is the correct answer
    # and it is the refusal branch of this path being exercised in production.
    if "obs_node" not in relations(con):
        return {
            "floor": None,
            "obs": 0,
            "events": 0,
            "why": (
                "HELD: obs_node absent, so the reflection conjuncts cannot be "
                "evaluated — UNMEASURED, not reconstructible. Run `sppf_db.py "
                "<FILTER> --full%s` to build the durable tier first."
                % (" --sandbox" if "--sandbox" in sys.argv else "")
            ),
        }
    # ⚑⚑ THE QUEUE FLOOR IS NOT A LICENCE TO DELETE — RECONSTRUCTION IS. `seq < floor` says
    # no registered cursor can still reach these rows; it says NOTHING about whether the
    # durable form can rebuild them. `lifecycle.py` keeps `consumed` and `reflected` as
    # separate links for exactly this reason, and its note is explicit: *"draining on
    # `consumed` alone would delete records whose replacement may not exist."*
    #
    # ⚑ AND UNTIL NOW NOTHING IN THIS PATH CONSULTED REFLECTION. Measured with
    # `pycodemod --calls reflects_obs`: two callers, both inside `reconstruct.py`. So a
    # `--reclaim --apply` would have deleted 1,255,688 observations on the queue predicate
    # alone, with the product identity (`SPPF × fibre ≡ event set`) unverified.
    #
    # ⚑ A CORE THAT CANNOT BE CHECKED IS HELD, NOT PASSED. An unreachable checker, a missing
    # relation, an exception — each yields `unreflected`, and the core is simply absent from
    # the drainable set. (This used to read "*the floor drops to protect those rows*"; with
    # the floor retired the protection is structural — a core that fails a conjunct is
    # excluded by the set difference, not shielded by a scalar.) Absent-read-as-permission
    # is the one failure mode that cannot be undone.
    #
    # ⚑⚑ AND THE DRAIN'S GRANULARITY IS WRONG — MEASURED BY RUNNING IT (2026-08-11). The
    # first real apply reclaimed 1,255,688 obs + 495,247 events on a sandbox where all 30
    # cores reflected. Afterwards, reconstruction FAILED: one observation survived at
    # `local_id 6213`, and `positional()` correctly refused a fibre that no longer starts
    # at 0.
    #
    # THE CAUSE IS STRUCTURAL, NOT A BUG IN THE SWEEP. `seq` is assigned across the whole
    # log; `local_id` is per-core and DENSE by construction (`--fibre` measured 0..n-1 with
    # no gaps, which is what licenses the positional `ekey[]` encoding). A floor on `seq`
    # cuts ACROSS cores, so it deletes a PREFIX of one core's fibre and leaves the rest —
    # destroying the density the residue's whole representation depends on.
    #
    # ⚑ SO THE UNIT OF RECLAMATION MUST BE THE CORE, NOT THE POSITION. A core is drainable
    # exactly when it RECONSTRUCTS; its rows then go together and no partial fibre can exist.
    # (The original form of this note added "*and every cursor has passed its highest seq*" —
    # that half retired with the floor on 2026-08-12. It was never a second requirement so
    # much as a scalar standing in for the first.) `seq < floor` is the right predicate for
    # an append-only LOG and the wrong one for a tier whose residue is positional — which is
    # exactly the two-roles-of-`obs` finding, surfacing a third time.
    #
    # FIXED — the sweep below is core-granular. This note is kept as the diagnosis, not as
    # a standing defect.
    # ⚑⚑ ⓶ — THE SCALAR REFLECTION FLOOR IS GONE, AND `q_drainable` SUBSUMES IT EXACTLY.
    # This ran `_unreflected_floor` — a Python loop over cores calling `reflects()` with an
    # early `break`, returning the FIRST failure as a chain-wide position — and then the
    # sweep below excluded those same cores relationally. Two mechanisms for one fact, of
    # which this was the one with the break, the extra round-trips, and the TOCTOU window.
    #
    # ⚑ IT WAS ALSO STRICTLY WEAKER, WHICH IS THE ARGUMENT FOR DELETING RATHER THAN KEEPING
    # IT AS A BELT-AND-BRACES CHECK. A floor HOLDS EVERYTHING ABOVE THE FIRST FAILURE: one
    # unreconstructible low core blocked every drainable core above it. The conjunction
    # excludes exactly the cores that fail and drains the rest — which is what its own
    # docstring already prescribed (*"the honest predicate is now a SET DIFFERENCE, not a
    # floor"*) while calling the floor a deliberate over-approximation.
    #
    # ⚑ AND THE `HELD at N by reflection` VERDICT IT PRINTED IS NOT LOST — it moved into the
    # data. A core excluded by the `determined` conjunct simply is not in the drainable set,
    # and `--lifecycle` reports it as `unreflected` (Ⓛ), which LOCATES the rejection per core
    # instead of collapsing the tier to one number. That is the located-rejection property
    # `lifecycle` exists for, finally reaching the drain.
    # ⚑⚑ THE UNIT OF RECLAMATION IS THE CORE, NOT THE POSITION — and the principle is
    # general: **a tier drains at the granularity its residue's encoding is dense over.**
    # `obs`'s residue is a POSITIONAL fibre (`--fibre`: `local_id` runs 0..n-1 per core with
    # no gaps, which is what licenses the `ekey[]` representation at all). `seq` is assigned
    # across the whole LOG, so a `seq < floor` cut slices ACROSS cores and leaves a PREFIX of
    # one core's fibre deleted — destroying the density the representation depends on.
    #
    # ⚑ MEASURED, BY RUNNING IT (2026-08-11): the first apply reclaimed 1,255,688 obs from a
    # sandbox where all 30 cores reflected; afterwards the one surviving core sat at
    # `local_id 6213` and `positional()` refused it. The measurement was the trigger — but
    # the specification is the principle above, which was derivable from `--fibre`'s result
    # without deleting anything.
    #
    # ⚑ SO A CORE IS DRAINABLE WHEN THE FLOOR HAS PASSED ITS *HIGHEST* SEQ, not its lowest.
    # That is strictly more conservative than the positional cut and it is what makes the
    # fibre survive: either every row of a core goes, or none does. Cores straddling the
    # floor are held until the next sweep, when the cursors have moved past them entirely.
    # ⚑ THE DRAINABLE SET IS A SUBQUERY, NOT A PYTHON LIST (user, 2026-08-11: *"That's a lot
    # of relational-algebra-in-python I would expect the DB to own."*). My first cut selected
    # core ids into Python and looped a `DELETE` per element — a grouped aggregate, a
    # semi-join and an iteration, all withheld from the engine that owns them. It is the same
    # defect `lifecycle_census` records ("the stages are computed in SQL, not per-row in
    # Python") and that this store was built to stop.
    # ⚑⚑ ⓵ — THE LICENCE IS ONE COMPILED CONJUNCTION, NOT A HAND-WRITTEN PREDICATE.
    # This was `SELECT core_id FROM obs GROUP BY core_id HAVING max(seq) < %s` — the QUEUE
    # half only, with reflection bolted on ahead of it as a separate scalar
    # (`_unreflected_floor`) computed in a separate statement from a Python loop with an
    # early break. Six world-states composed into one decision under `autocommit=True`.
    #
    # `q_drainable` is the same licence as a single expression:
    #
    #     drainable = below_floor  ×  projected  ×  determined
    #                   (queue)       (obs_node)    (node_id, ch)
    #
    # — the `jea_edge_states.py:9` factoring (`bound × efficiency × live_state`, three
    # provenances combined in ONE expression) translated to relational algebra, which is the
    # form that CANNOT go stale because nothing is held between reads.
    #
    # ⚑ VERIFIED EQUIVALENT BEFORE REPLACING: the builder and the six-statement path both
    # answer 13 cores on the current sandbox snapshot. A replacement that changes the answer
    # is a different licence, not a refactor.
    # ⚑ THE TEXT, NOT `QB.run` — AND THE DISTINCTION IS THE POINT OF THE ITEM. `run()`
    # EXECUTES and returns rows; embedding the licence as a SUBQUERY is what keeps the
    # `DELETE` a single statement. Pulling the drainable core ids into Python and looping a
    # delete per element is the exact defect this sweep already retired once (user: *"that's
    # a lot of relational-algebra-in-python I would expect the DB to own"*), and doing it
    # again to consume a compiled builder would be worse, not better.
    #
    # ⚑ `QB.SQL[...]` IS THE COMPILED TEXT AND `QB.run` HAS NO SUBQUERY MODE — a real gap,
    # named rather than routed around: the builder layer can execute a query or nothing.
    # Reaching into `SQL` is the honest minimum today; a `--as-subquery`/composable accessor
    # is what would make this not a reach. (I first wrote `QB.sql("drainable")`, which does
    # not exist — checking is the only reason it did not ship.)
    # ⚑ DEFERRED IMPORT, matching `_unreflected_floor`'s precedent in this module: the
    # builder layer is not a module-scope dependency of the schema (importing it at the top
    # would invert the direction `reconstruct → schema` already relies on). One place in the
    # write path needs the compiled licence, so it asks for it here.
    # ⚑⚑ THE TEXT **AND** ITS BAKED DEFAULTS — taking only `[0]` is a live bug, caught here
    # by psycopg refusing loudly (`query parameter missing: count_1`). A compiled builder
    # carries defaults SQLAlchemy parameterised on its own; `QB.run` merges them before
    # executing, and reaching past it takes the string and silently loses them.
    #
    # ⚑ THE `floor` BINDPARAM IS GONE WITH THE POSITIONAL CONJUNCT, and that is the one
    # difference in this block. `drainable` carried `%(floor)s` for the caller to supply;
    # `drainable_res` has no caller-supplied parameter at all, so the defaults ARE the
    # whole parameter set. A licence with nothing to bind cannot be bound wrongly.
    #
    # ⚑ AND THAT IS THE PRICE OF THE MISSING SUBQUERY MODE, made concrete: every caller that
    # needs a builder as a SUBQUERY must now re-implement `run`'s parameter merge. One
    # re-implementation is a workaround; the second would be the duplication this module
    # exists to prevent — which is the argument for a composable accessor rather than a note.
    _DRAINABLE, _drain_defaults = QB.SQL["drainable_res"]
    _drain_p = dict(_drain_defaults)
    pending = scalar(con, "SELECT count(*) FROM obs WHERE core_id IN (%s)" % _DRAINABLE, _drain_p)
    # ⚑ THE `edge` COUNTERPART OF `pending`, SO THE DRY RUN REPORTS BOTH RELATIONS IT WOULD
    # TOUCH. A dry run that named only `obs` would understate the sweep by the larger half —
    # `edge` was 627,077 rows against `obs` 0 at the moment ⑹ was written.
    pending_edge = scalar(
        con, "SELECT count(*) FROM edge WHERE core_id IN (%s)" % _DRAINABLE, _drain_p
    )
    if dry_run:
        n_cores = scalar(con, "SELECT count(*) FROM (%s) d" % _DRAINABLE, _drain_p)
        return {
            "floor": None,
            "obs": pending,
            "edge": pending_edge,
            "events": None,
            "why": "dry run — %d core(s) reconstructible" % n_cores,
        }

    # ⚑ ONE STATEMENT, AND THE ATOM IS A WHOLE FIBRE. The chunked loop bought
    # interruptibility over a 38-minute anti-join; here the bound is the drainable SET, which
    # the engine computes once. A kill loses the transaction, never half a core's fibre —
    # the state the positional sweep could leave behind, and the reason granularity moved.
    #
    # ⚑⚑ `edge` AND `obs` GO IN **ONE** STATEMENT, AND SPLITTING THEM IS A SILENT FAILURE
    # RATHER THAN AN ERROR (⑹, 2026-08-12). Run as two statements with `DELETE FROM obs`
    # first, the licence RE-EVALUATES for the edge delete with the drained cores now ABSENT
    # from its minuend — `SELECT core_id FROM obs GROUP BY core_id` produces no group for a
    # core whose rows have just gone — so the second `DELETE` matches nothing, `edge` keeps
    # every row, and **nothing raises**. The relation that has never drained would go on not
    # draining while the sweep reported success.
    #
    # ⚑⚑ THE DATA-MODIFYING CTE IS THE BRANCHLESS FORM THE LICENCE WAS BUILT FOR. Postgres
    # evaluates every sub-statement of a `WITH` against the SAME SNAPSHOT and runs each
    # exactly once, to completion, regardless of whether the primary query reads its output.
    # So `d` is computed once, both DELETEs see the identical core set, and there is no window
    # between them — the same property `jea_edge_states`' *"never blind-multiply a stale factor
    # by a fresh live_state"* names, at statement granularity instead of at expression
    # granularity. Two statements would be exactly the held-state shape this licence replaced
    # six of.
    #
    # ⚑ AND BOTH ROWCOUNTS COME BACK, WHICH IS WHY IT ENDS IN A `SELECT` RATHER THAN A
    # `DELETE`. `.rowcount` can report only the OUTERMOST statement, so a CTE ending in
    # `DELETE FROM obs` would return the `obs` count and leave the `edge` count unobservable —
    # and an unobservable delete is indistinguishable from one that did not happen, which is
    # the very failure the single statement exists to prevent. `RETURNING 1` + `count(*)` per
    # arm makes both countable in the same round trip.
    _sweep = (
        "WITH d AS (%s), "
        "e AS (DELETE FROM edge WHERE core_id IN (SELECT core_id FROM d) RETURNING 1), "
        "o AS (DELETE FROM obs WHERE core_id IN (SELECT core_id FROM d) RETURNING 1) "
        "SELECT (SELECT count(*) FROM e) AS edge, (SELECT count(*) FROM o) AS obs" % _DRAINABLE
    )
    _swept = next(rows(con, _sweep, _drain_p))
    edge_done, done = _swept["edge"], _swept["obs"]
    con.commit()

    # ⚑ THE EVENT SWEEP RUNS ONLY OVER WHAT THE RECLAIM FREED, not the whole table. An
    # event is removable once nothing observes it; after the range delete that set can
    # only have grown within the reclaimed range, so this is bounded work rather than
    # the full-corpus anti-join. `NOT EXISTS` (not `NOT IN`) so the planner may anti-join.
    ev = execute(
        con, "DELETE FROM event e WHERE NOT EXISTS (SELECT 1 FROM obs o WHERE o.ekey = e.ekey)"
    ).rowcount
    con.commit()
    return {"floor": None, "obs": done, "edge": edge_done, "events": ev, "why": "applied"}


def reclaim_verdict(licensed, staged_any):
    """The one-line verdict for `--reclaim-core` — `NO` split into its TWO causes.

    ⚑⚑ A BARE `NO` CONFLATES TWO STATES THAT WANT OPPOSITE RESPONSES. The licence's minuend is
    `SELECT core_id FROM obs GROUP BY core_id`, so a core with no staged rows produces no group
    and never enters the licence at all — it is refused by ABSENCE FROM THE POPULATION, not by
    failing a conjunct. Told only "NO", an operator goes to fix a core that is already finished.

    ⚑⚑⚑ AND THE DISCRIMINATOR CANNOT BE READ OFF THE DRY RUN — the defect this function exists
    to pin. `reclaim_core`'s `obs`/`edge` count rows MATCHING THE LICENCE, so a REFUSED core
    reports 0 whatever its staged size: MEASURED, an unprojected core with **449 observations**
    reports `obs 0`. My first cut used those counts as "is anything staged" and printed both
    refusals identically. `staged_any` must come from asking `obs` DIRECTLY (one `ix_obs_pk`
    probe with `LIMIT 1`), which is why it is a parameter here rather than derived.

    ⚑ EXTRACTED FROM THE DISPATCH SO A CASE CAN REACH IT. Inline in an `if "--reclaim-core" in
    sys.argv:` branch, the judgement was reachable only by running the CLI against a live store
    with a core in each of three states — which is why the first version's error was caught by
    running two cores and comparing output BY EYE, a check that does not survive the session.
    """
    if licensed:
        return "YES"
    if staged_any:
        return "NO — a conjunct holds it"
    return "NO — nothing staged (already drained, or never ingested)"


def reclaim_core(core_id, con=None, dry_run=True):
    """Retire ONE core, IF the licence admits it — the make-driven twin of `reclaim`.

    ⚑⚑⚑ ⟡converge-scheduled — THE LAST LINK IN THE PER-MODULE CHAIN.
    `<Mod>.agdai → .ingested → .promoted → .drained`. Ingest and promote became dependency
    edges because a module is not fully processed at its `.agdai`, nor at its internment; it is
    finished when the staged copy it no longer needs has been RECLAIMED. `reclaim` walks the
    whole corpus and has no `core_id` parameter, so there was nothing for a per-module rule to
    call.

    ⚑⚑ THE LICENCE IS UNCHANGED AND IS ONLY NARROWED — via `drainable_res.one_core`, which is
    `q_drainable_res(one_core=True)`: the same five conjuncts with a core predicate pushed into
    `_live_cores`, so all nine of its `IN (SELECT obs.core_id FROM obs)` sites plus the `GROUP
    BY` minuend restrict together. A core this refuses is a core `reclaim` would also refuse.

    ⚑⚑⚑ AND THAT AGREEMENT IS MEASURED, NOT ARGUED — `schema_selftest`'s licence fixture drives
    both arms over cores A–F and asserts, PER CORE, that the scoped arm yields `[c]` exactly
    when the shipped licence contains `c`. Including the four REFUSED cores, where it must
    return `[]`: a narrowing that WIDENED would show up precisely there, and widening is the one
    failure mode that cannot be undone.

    ⚑ THE PREDICATE GOES INSIDE THE LICENCE, NOT AROUND ITS OUTPUT, and the first cut of this
    function got that wrong. It wrote `SELECT core_id FROM (<licence>) d WHERE core_id = :c`,
    which computes the CORPUS-WIDE drainable set and throws all but one row away — the failure
    `q_drainable_res`'s own docstring names one level up: *"the unscoped licence READ the thing
    that never shrinks while its ANSWER was bounded by the thing that does."* Scoping the OUTPUT
    is not scoping the WORK.

    ⚑⚑⚑ `edge` AND `obs` STAY IN ONE STATEMENT, AND SPLITTING THEM WOULD BE A SILENT FAILURE.
    `reclaim` records the measured trap: run as two statements with `DELETE FROM obs` first, the
    licence RE-EVALUATES for the edge delete with the drained core now ABSENT from its minuend —
    `SELECT core_id FROM obs GROUP BY core_id` produces no group for a core whose rows have just
    gone — so the second DELETE matches nothing, `edge` keeps every row, and **nothing raises**.
    The data-modifying CTE is what makes both arms see one snapshot; this preserves it verbatim.

    ⚑ NO EVENT SWEEP HERE, DELIBERATELY. `reclaim` finishes with a `DELETE FROM event WHERE NOT
    EXISTS (… obs …)` — bounded, because it runs once after a whole sweep. Per module that same
    statement is a FULL anti-join against `event` on every one of ~3,600 targets. Events are
    content-addressed and shared across cores, so a per-core event sweep is not even well-posed:
    the last core observing an ekey is not knowable from one core's rows. The corpus-level
    `reclaim` remains the owner of that half.

    ⚑ DRY BY DEFAULT, like every mutating entry in this file — a retire that runs bare is the
    shape `--establish` was built to prevent, and this one DELETES.
    """
    con = con or _cli_connect()
    # ⚑ COMPILED LIVE, BECAUSE THE ARM IS DELIBERATELY NOT IN THE CACHE. `REFERENCE_ARMS` are
    # kept out of `INTERN_BUILDERS` so no caller can splice one into a `DELETE` by accident —
    # and this caller is a `DELETE`. Reaching it through `_named_builder` rather than `QB.SQL`
    # is therefore the deliberate act that safety property is designed to force, not a
    # workaround for it. `schema_selftest._licensed` compiles the same way for the same reason.
    import query_defs as _QD

    _one, _dp = _QD._compile_one(_QD._named_builder("drainable_res.one_core")())
    _p = dict(_dp)
    _p["rc_core"] = core_id
    if dry_run:
        n = scalar(con, "SELECT count(*) FROM (%s) k" % _one, _p)
        obs_n = scalar(con, "SELECT count(*) FROM obs WHERE core_id IN (%s)" % _one, _p)
        edge_n = scalar(con, "SELECT count(*) FROM edge WHERE core_id IN (%s)" % _one, _p)
        return {
            "licensed": bool(n),
            "obs": obs_n,
            "edge": edge_n,
            "why": "dry run — licence %s this core" % ("ADMITS" if n else "REFUSES"),
        }
    # ⚑⚑ ONE STATEMENT, AND SPLITTING IT WOULD BE A SILENT FAILURE — `reclaim`'s measured trap,
    # preserved verbatim at this granularity. The data-modifying CTE makes both DELETEs see one
    # snapshot; run as two statements with `obs` first, the licence re-evaluates for the `edge`
    # delete with the core now ABSENT from its minuend, the second DELETE matches nothing, and
    # NOTHING RAISES.
    _sweep = (
        "WITH d AS (%s), "
        "e AS (DELETE FROM edge WHERE core_id IN (SELECT core_id FROM d) RETURNING 1), "
        "o AS (DELETE FROM obs WHERE core_id IN (SELECT core_id FROM d) RETURNING 1) "
        "SELECT (SELECT count(*) FROM e) AS edge, (SELECT count(*) FROM o) AS obs" % _one
    )
    _swept = next(rows(con, _sweep, _p))
    con.commit()
    # ⚑ `licensed` READS THE ROWCOUNTS, NOT A SECOND LICENCE EVALUATION. Asking the licence
    # again after the delete would consult a store the delete has just changed — the core is
    # gone from `obs`, so its own minuend no longer produces a group for it and the answer
    # would be `False` on every SUCCESSFUL retire. The rowcounts are the evidence that the
    # statement admitted it.
    return {
        "licensed": bool(_swept["obs"] or _swept["edge"]),
        "obs": _swept["obs"],
        "edge": _swept["edge"],
        "why": "applied",
    }


def cancel(pid, terminate=False, con=None):
    """Ask the store to stop a running backend — `pg_cancel_backend` (statement) or
    `pg_terminate_backend` (connection).

    ⚑ KILLING THE CLIENT DOES NOT STOP THE SERVER. Measured: SIGTERM to the python
    process returned exit 15 and left `pg_stat_activity` still showing the DELETE
    `active` and spilling to disk. Postgres executes a statement to completion
    independently of whether its client is still listening — so "I killed the ingest" is
    a claim about the CLIENT, and reading it as a claim about the WORK is the same
    method-vs-substrate collapse this file keeps recording.

    Cancel is the correct verb (it interrupts the statement, leaving the session usable);
    terminate drops the whole connection and is the escalation when cancel does not take.
    """
    import store as _store

    if con is None:
        con = _cli_connect()
    fn = "pg_terminate_backend" if terminate else "pg_cancel_backend"
    return scalar(con, "SELECT %s(%s)" % (fn, ph()), (pid,))


def drained(con):
    """Has the event tier lost rows it once held? — the precondition every PROJECTION owes.

    ⚑⚑ THIS EXISTS BECAUSE A WORKING COMMAND SILENTLY DESTROYS DURABLE STATE. `project_sppf`
    DROPs `_node`/`node_child`/`_unit`/`unit_node` and rebuilds them from `obs`/`edge`/`event`;
    `project_ref` DROPs `ref` and rebuilds it from the same. So after a drain, re-running either
    one **regenerates the durable tier from a tier that no longer holds the data** — the higher
    tier is not a projection at all but a CACHE WITH A DROP-AND-REBUILD REFRESH, and the drain
    converts that refresh into deletion. `project_sppf`'s own comment says *"NEVER touch the
    event tier"*: the guard points the wrong way, and nothing protected the projection FROM a
    drained event tier.

    ⚑ IT LANDS HARDEST ON `ref`, THE INDEX THE PIN WAS RETIRED AGAINST. `scope_fix` was migrated
    off `obs`/`edge` onto `ref` precisely so it could outlive the drain — and `project_ref`
    rebuilds `ref` from the drained tier, after which `_event_refs` returns `[]` and the
    resolver falls back to a predicate true for 13 of 4,775 nodes: *"returns almost nothing and
    reports success"*, in a tool that rewrites Agda source.

    ⚑⚑ THE PREDICATE WAS `min(seq) > 1` AND IS NOW `obs_node ∖ obs` — SAME QUESTION, AND THE
    NEW SPELLING IS WHAT THE OLD DOCSTRING WAS ALREADY DESCRIBING. The retired argument:
    *"`seq` is an identity assigned monotonically from 1 over a fresh tier, and the drain
    deletes whole cores BELOW a floor — i.e. bottom-up in `seq`. So a surviving minimum above 1
    is exactly the footprint of rows that were once present and are gone. `--full` drops and
    re-ingests the tier, restarting `seq` at 1, so a deliberate reset reads as NOT drained."*

    ⚑⚑ THAT REASONING WAS SOUND ONLY WHILE DELETION WAS BOTTOM-UP IN POSITION — which is the
    property the positional licence had and `q_drainable_res` does not. The residue licence
    admits cores on their own facts, in no particular order, so a drain can leave `min(seq)` at
    1 with whole cores gone. **The proxy did not merely lose its column; it had already lost its
    premise**, and would have degraded silently — reading INTACT over a drained tier, which is
    the exact direction that destroys `ref`.

    ⚑ THE DIRECT FORM IS `reconstruct.drained_reach`'s, AND SHARING IT IS THE POINT — *"cores
    the DURABLE tier addresses but tier 0 no longer holds"*. A core in `obs_node` with no `obs`
    rows IS the footprint of rows once present and now gone, stated as a fact rather than
    inferred from a numbering. `--full` re-ingests every core before projecting, so a deliberate
    reset still reads as NOT drained — the discriminator is still the data, not a flag.

    ⚑ AN ABSENT `obs_node` IS NOT DRAINED, AND THAT IS A POSITIVE ARGUMENT RATHER THAN AN
    ABSENT-READ-AS-PASS. With no durable addressing there is nothing a DROP-and-rebuild could
    destroy: the hazard here is *regenerating a durable relation from an incomplete source*, and
    on a store holding no such relation the premise is false. A fresh store's first projection
    proceeds because nothing is at risk, not because the check could not be evaluated.

    ⚑ AND IT IS DELIBERATELY BLIND TO *WHY* ROWS LEFT. The core-prune (`_delete_core_rows`)
    removes rows on source-liveness rather than position, and a projection rebuilt over that is
    just as wrong. A predicate that asked "was it the DRAIN specifically" would have to be told;
    this one asks the question that actually matters — *is the source still complete* — and
    answers it from the store.

    Returns (is_drained, detail). A tier with no rows at all is NOT drained: it is empty, which
    is a different fact and one `--full` produces on purpose.
    """
    # ⚑⚑ THE EMPTY TEST RUNS **LAST**, AND MOVING IT IS A DEFECT FIX MEASURED 2026-08-12 ON THE
    # SANDBOX. It used to run FIRST, and a FULLY drained tier is empty — so the maximally
    # dangerous state (`obs` 0 rows, `obs_node` 627,327 rows addressing 42 cores) reported *"obs
    # is empty — nothing has been ingested, so nothing is missing"* and the guard did not fire.
    # `min(seq)` had the identical hole (`min()` over zero rows is NULL), so this is inherited,
    # not introduced — but the new predicate can TELL THE TWO APART and the old one could not:
    # "nothing was ever ingested" and "everything that was ingested has been reclaimed" are the
    # same row count and opposite verdicts, and only the durable side distinguishes them.
    # Reached in order, `empty` now means what it says: nothing here, and nothing addressed.
    if "obs_node" not in relations(con):
        return False, (
            "obs_node is absent — no durable addressing exists, so no rebuild can "
            "destroy one; the event tier is the only copy and it is intact"
        )
    gone = scalar(
        con,
        "SELECT count(*) FROM (SELECT n.core_id FROM obs_node n "
        "WHERE NOT EXISTS (SELECT 1 FROM obs o WHERE o.core_id = n.core_id) "
        "GROUP BY n.core_id) d",
    )
    if not gone and scalar(con, "SELECT count(*) FROM obs") == 0:
        return False, "obs is empty — nothing has been ingested, so nothing is missing"
    if gone:
        return True, (
            "the durable tier addresses %s core(s) tier 0 no longer holds — they were "
            "reclaimed, so the event tier is no longer a complete source" % format(gone, ",")
        )
    return False, (
        "every core the durable tier addresses is still in obs — the event tier is intact"
    )


# ── `activity`, `flush`, `migrate_queue` — ARRIVED 2026-08-11, LATE ───────────────────────
#
# ⚑⚑ THIS MODULE'S RELOCATION NOTE IN `schema.py` ALREADY LISTED ALL THREE AS HAVING MOVED
# HERE, AND THEY HAD NOT. The note reads *"⚑ 741 LINES: `_require_pg`, `hwm`, `lwm`, …,
# `activity`, `flush`, `migrate_queue`, `cancel`, `drained`"* — a roster written from the plan
# rather than from the result, and `pycodemod --binding activity` returned exactly one binding,
# at `schema.py:125`. A relocation note that names a function which did not move is the same
# defect class as a banner listing a mode the dispatch never grew: **it reads as authoritative
# while being false**, and the reader who trusts it looks in the wrong file.
#
# ⚑ AND THE MEMBERSHIP TEST WAS ALREADY CORRECT — only the execution was missing. This module's
# own header states the predicate structurally: *"every function here is POSTGRES-ONLY and every
# one of them opens by calling `_require_pg`"*. `flush` and `migrate_queue` open with exactly
# that call; `activity` raises the same refusal inline because its message is about a missing
# CATALOGUE rather than a missing transaction floor. So this is not a size cut dressed as a
# seam — it is the seam the note already described, finally taken.
def activity(con=None):
    """What the store thinks its connections are DOING — pid, state, wait event, and the
    running statement, newest-first by transaction age.

    ⚑ THIS EXISTS BECAUSE "IS THE INGEST STUCK OR WORKING?" HAD NO READER. Row counts
    answer *how full*, never *why it stopped*: a writer at 21 minutes elapsed and 2 minutes
    CPU is BLOCKED, and nothing in `--census` can say on what. The alternative was
    `cat /proc/<pid>/wchan` piped into a status read — a composition over a structured
    artifact, and one that reports the KERNEL's view (sleeping on a socket) when the fact
    wanted is the STORE's (waiting on a lock, or mid-COPY).

    ⚑ AND A BLOCKED CONNECTION IS NOT A FAILED ONE. `wait_event` distinguishes a lock wait
    from a client wait from ordinary idleness; collapsing them into "stuck" is the same
    absent-read-as-failed collapse `census` guards against one level down. sqlite has no
    such view and says so rather than returning an empty list, which would read as "no
    activity" when it means "no instrument".
    """
    import store as _store

    if con is None:
        con = _cli_connect()
    # ⚑ `dialect()` RETURNS A DIALECT OBJECT, NOT A NAME. Comparing it to the string
    # "postgresql" is never true, so the guard fired on postgres too — a refusal that
    # looks like a correct precondition and is a type error. `backend()` is the name
    # authority; the dialect is for compiling statements.
    if _store.backend() != "postgres":
        raise NotImplementedError(
            "activity() is postgres-only: sqlite has no connection catalogue. "
            "An empty list here would read as 'nothing running'; it would mean "
            "'no instrument'."
        )
    # ⚑ `backend_xid` IS THE RESUMABILITY FACT, AND IT IS NOT INFERABLE FROM `state`.
    # A statement running 37 minutes looks identical whether its work is committed
    # incrementally or will vanish on rollback — and the difference decides whether
    # killing it discards the work. A non-null `backend_xid` means this connection has
    # ASSIGNED a write transaction: everything it has done is inside that transaction and
    # a kill rolls it ALL back. Null means no write xid is held.
    #
    # `xact_start` alone does NOT answer this: psycopg opens an implicit transaction on
    # any statement, so `xact_start` is set for a read too. Reading it as "in a
    # transaction" is the same shape as reading an empty query result as "absent" —
    # a fact about the instrument reported as a fact about the subject.
    return list(
        rows(
            con,
            # ⚑ `now()` IS TRANSACTION-START TIME, NOT WALL CLOCK — so `now() - query_start`
            # for a statement that began AFTER this connection's transaction opened yields a
            # NEGATIVE interval, rendered as "-1 day, 23:59:59". Observed live while watching
            # a projection: an age that reads as almost -1 day is not clock skew, it is the
            # wrong `now`. `clock_timestamp()` is the actual current time.
            "SELECT pid, state, wait_event_type, wait_event, backend_xid, backend_xmin, "
            "       clock_timestamp()-xact_start AS xact_age, "
            "       clock_timestamp()-query_start AS query_age, "
            "       left(query, 160) AS query "
            "FROM pg_stat_activity "
            "WHERE datname = current_database() AND pid <> pg_backend_pid() "
            "ORDER BY xact_start NULLS LAST",
        )
    )


def flush(tiers, con=None, dry_run=True):
    """DROP and recreate whole tiers from the declaration — the honest re-intern path.

    ⚑ `sppf_db`'s `full=True` IS NOT THIS, IN TWO WAYS. It drops six named EVENT tables via
    `con.execute` — sqlite-only, so it raises `AttributeError` on psycopg — and it leaves the
    SPPF projection standing. After a walker change that is the worst outcome: a fresh event
    tier under a stale projection built by the OLD walk, with nothing marking which is which.

    ⚑ THE CURSOR RESET IS DELETED 2026-08-12 WITH THE REGISTRY, AND ITS ARGUMENT IS THE ONE
    GENERAL THING THIS FUNCTION KNEW: *"`consumer.lwm` indexes `obs.seq`; a flush restarts that
    sequence, so a surviving cursor points past the end of a log that no longer contains what
    it claims to have consumed — the queue then reports a caught-up consumer over data it has
    never seen."* **A DERIVED ARTEFACT THAT OUTLIVES THE TIER IT DESCRIBES IS A STALE PROMISE.**
    That rule is why nothing is stored now; it is NOT discharged by the deletion, and the next
    thing this function drops beside a derived index will owe it again.

    Tier order matters on the way down (projection before event) but `DROP TABLE` here is
    per-table and unordered — postgres has no FK between these tiers, so nothing constrains
    it. Stated because a future FK would make the order load-bearing.
    """
    _require_pg("flush()")
    import store as _store

    if con is None:
        con = _cli_connect(mode="rw")
    unknown = [t for t in tiers if t not in _TIERS]
    if unknown:
        raise ValueError("unknown tier(s) %s; known: %s" % (sorted(unknown), sorted(_TIERS)))
    live = relations(con)
    drops = [t for tier in tiers for t in sorted(_TIERS[tier]) if getattr(t, "name", t) in live]
    plan = ["DROP TABLE IF EXISTS %s CASCADE" % getattr(t, "name", t) for t in drops]
    if dry_run:
        return plan
    for s in plan:
        execute(con, s)
    con.commit()
    for tier in tiers:
        apply(con, only=tier)
    con.commit()
    return plan


def migrate_queue(con=None, dry_run=True):
    """RETIRE the queue tier from an EXISTING store — drop the `consumer` registry.

    ⚑⚑ THIS MIGRATION NOW RUNS BACKWARDS, AND KEEPING IT UNDER ITS OLD NAME IS DELIBERATE.
    It used to ADD `obs.seq` (identity) + `ix_obs_seq` + the `consumer` registry, and then to
    drop `consumer.kind`; it now drops the registry itself. The name is the OPERATOR'S handle
    for "reconcile this store's queue tier with the declaration", and renaming it would leave
    two commands where one store-shape question exists. Its steps are what changed.

    ⚑ IDEMPOTENT, AND CHECKED RATHER THAN ASSUMED — the property every step here has always
    had. Re-running must be a no-op, not an error: a migration that cannot be safely re-run is
    one nobody dares run at all. The live catalogue is tested first, so a store that never ran
    the FORWARD step and a store that already ran the REVERSE one both end up in the same
    place. That reasoning is the forward migration's own, verbatim, and it is exactly why
    dropping is expressible as a step rather than as a one-off.

    ⚑ THE FORWARD STEP'S NOTE IS KEPT AS RESIDUE BECAUSE IT RECORDS A PAIRING RULE. Adding
    `kind` backfilled `'cursor'` and relied on `register()` re-declaring the pins afterwards,
    *"so the order is: widen, then re-declare"* — and that only worked because `register` had
    been taught to UPDATE the kind, since `ON CONFLICT DO NOTHING` alone left the existing row
    untouched. **Two halves of one migration, neither working alone**, which is why a migration
    step must be read together with the writer it depends on. This step has no such pair: there
    is no writer left to keep in step with.

    ⚑ DRY RUN BY DEFAULT. This ran against a 506k-row table under a lock on the live store;
    the sibling write tools in this repo gate on `--apply` for the same reason, and the
    one that did not (`prune_imports`) cost an unintended deletion.
    """
    # ⚑ `connect()` DEFAULTS TO READ-ONLY, and the default caught this: the first apply
    # raised `ReadOnlySqlTransaction` because a migration had asked for a plain
    # connection. That guard is doing its job — a function that writes must SAY it
    # writes — so the fix is to declare the intent, never to weaken the default.
    _require_pg("migrate_queue()")
    import store as _store

    if con is None:
        con = _cli_connect(mode="rw" if not dry_run else "ro")
    live = relations(con)
    plan = []
    # ⚑ DROPPING THE TABLE TAKES ITS ROWS' STALE CLAIMS WITH IT, which is the cleanup this
    # needed anyway: both stores still hold a `scope_fix:resolver` row asserting a position
    # over a log the resolver no longer reads (`--sql obs` over `scope_fix`/`scope_store`/
    # `scope_source` → **0 sites**; it reads `ref ⋈ path_text ⋈ terms`). A row asserting a
    # promise the code has forgotten is exactly the stale-claim shape this arc keeps paying for.
    #
    # ⚑ GUARDED ON THE CATALOGUE **AND** SPELLED `IF EXISTS` — belt and braces on purpose, and
    # not redundant. The catalogue test is what keeps the PLAN honest (a dry run on a
    # already-migrated store must print nothing, not a step that would be a no-op); `IF EXISTS`
    # is what keeps the APPLY safe if the two reads straddle another migration.
    if "consumer" in live:
        plan.append("DROP TABLE IF EXISTS consumer")
    # ⚑ THE POSITION ITSELF — `obs.seq` + `ix_obs_seq` — the queue tier's last footprint in a
    # LIVE store. Same reverse-migration shape as the table above: guarded on the CATALOGUE so
    # a dry run on an already-migrated store prints nothing, and spelled `IF EXISTS` so the
    # apply is safe if the two reads straddle another migration.
    #
    # ⚑ THE INDEX IS DROPPED EXPLICITLY EVEN THOUGH `DROP COLUMN` WOULD TAKE IT. Postgres drops
    # an index whose column is dropped, so this is redundant on any store whose column is still
    # there — but a store that lost the column by some other route can be left holding the index
    # alone, and a migration that only reconciles the shape it expects is not idempotent, it is
    # merely untested. Two independent `IF EXISTS` steps converge from either half-state.
    if "obs" in live and "seq" in columns_of(con, "obs"):
        plan.append("DROP INDEX IF EXISTS ix_obs_seq")
        plan.append("ALTER TABLE obs DROP COLUMN IF EXISTS seq")
    if dry_run:
        return plan
    for s in plan:
        execute(con, s)
    con.commit()
    return plan


def migrate_views(con=None, dry_run=True):
    """DROP every VIEW an existing store still holds — ⟡view-purge, 2026-08-12.

    ⚑⚑ REMOVING THE EMIT DOES NOT REMOVE THE OBJECT. Both tenants were built by a DDL that
    emitted `CREATE OR REPLACE VIEW`, and they still HOLD `node`, `unit`, `node_fanin`,
    `shared_subtree`, `node_atom` (live: 5) and `orbit` (sandbox: 6). Left alone,
    `relations()` keeps reporting them, `--census` keeps counting them, and the tree reads as
    if the purge never happened — a stale relation outliving the code that declared it, which
    is the same shape as `consumer`'s rows asserting a position over a log nobody reads.

    ⚑ CATALOGUE-DRIVEN, NOT NAME-DRIVEN, AND THAT IS THE DIFFERENCE FROM `migrate_queue`.
    That migration names `consumer` because it retires ONE known table; this retires a KIND.
    A hardcoded six-name list would be a frozen roster of exactly the thing being deleted —
    it would miss a seventh view some other branch created, and would go on naming six long
    after they are gone. `relations()` already normalises the engine's own catalogue to
    `{name: 'table'|'view'}`, so "every relation of kind view" is a read, not a list.
    Idempotent by construction: on a migrated store the read returns nothing and the plan is
    empty, so a store that never had views and one that already dropped them converge.

    ⚑⚑ `CASCADE` IS BELT-AND-BRACES, NOT LOAD-BEARING — MEASURED, not assumed, because the
    brief that ordered this migration predicted the opposite. `pg_depend ⋈ pg_rewrite` over
    the sandbox returns **15 dependency edges and every one is `relkind='r'`, a TABLE**:
    `node_atom` depends on `_node`/`node_child`/`path_text`/`terms`, NOT on `node`;
    `shared_subtree` on `node_child`, NOT on `node_fanin`. The emitter built each body from a
    SELECTABLE, so postgres inlined it at CREATE time and recorded base-table dependencies —
    there are ZERO view→view edges and the drop order cannot matter. `CASCADE` stays because
    `store.sandbox_reset` already establishes it as the idiom and because a view created by
    some other route COULD have a dependent; it is not what makes this correct.

    ⚑ DRY RUN BY DEFAULT — `migrate_queue`'s rule, for its reason: a write tool whose safe
    path is not the default is the `prune_imports` shape, and that one cost a deletion.
    """
    _require_pg("migrate_views()")
    if con is None:
        con = _cli_connect(mode="rw" if not dry_run else "ro")
    # ⚑⚑ THE SHADOWS ARE SPARED, AND THE EXCLUSION IS READ OFF THE DECLARATION (⟡ladder-retire,
    # 2026-08-13). This migration retires a KIND — *"every relation of kind view"* — which was
    # exactly right while every view was a convenience. `core_decoded_shadow` is not: it is the
    # tier's reconstruction CLAIM and the drain's licence reads it, so a catalogue-driven purge
    # would delete the thing that makes `core_decoded` retirable and would report success.
    #
    # ⚑ `SHADOWS` IS THE AUTHORITY, NOT A NAME LIST HERE. This function's own note argues that a
    # hardcoded roster *"would miss a seventh view some other branch created, and would go on
    # naming six long after they are gone"* — the same objection applies to a hardcoded EXCLUSION,
    # so the set is derived from the declaration and a shadow added there is spared with no edit.
    plan = [
        'DROP VIEW IF EXISTS "%s" CASCADE' % n
        for n, kind in sorted(relations(con).items())
        if kind == "view" and n not in SHADOWS
    ]
    if dry_run:
        return plan
    for s in plan:
        execute(con, s)
    con.commit()
    return plan


# ══ the tier's own REPORTS — `--activity` / `--watermark` / `--lifecycle` ════════════════
#
# ⚑ THESE WERE `schema.py` DISPATCH BODIES, AND THEY MOVED ON THE SAME TEST AS THE REST:
# WHERE DOES EACH BLOCK'S ⚑ COMMENTARY POINT? `--watermark`'s note is *"THE KIND IS SHOWN
# BECAUSE A LAG ALONE CANNOT BE READ … Printing the kind is what makes the display answer the
# question instead of inviting the guess"* — about the DISPLAY, so it travels with the
# display. The blocks that stayed behind (`--advance`, `--retype`, `--reclaim`, `--flush`,
# `--migrate-queue`) carry notes about the CALL the dispatch makes — a defaulted `kind`, a
# `strict=True` that only the operator route turns on, a connection the dispatch never
# passed — so those belong beside the call site, in the CLI.
#
# ⚑ AND THEY LAND HERE RATHER THAN IN `schema_diag` BECAUSE THIS TIER'S MEMBERSHIP TEST IS
# EXACT: everything they render (`hwm`, `lwm`, `consumers`, `reclaimable`, `lifecycle_census`,
# `activity`) is postgres-only behind `_require_pg` or its inline twin. Filing a renderer away
# from the thing it renders is what put `activity`/`flush`/`migrate_queue` in `schema.py` for
# a whole session while a relocation note said they were here.
def activity_report():
    """`--activity` — what the store's connections are doing. Returns an exit code."""
    import store

    try:
        acts = activity()
    except NotImplementedError as e:
        print(str(e))
        return 2
    if not acts:
        print("no other connections to %s" % store.dsn().get("dbname", "?"))
    for r in acts:
        # the write-transaction verdict, stated rather than left to be inferred
        xid = r["backend_xid"]
        tx = (
            ("WRITE TXN xid=%s — a kill ROLLS BACK this work" % xid)
            if xid
            else "no write xid held — committed work survives a kill"
        )
        print(
            "pid %-8s %-10s %-14s %-18s xact %s / query %s"
            % (
                r["pid"],
                r["state"],
                r["wait_event_type"] or "-",
                r["wait_event"] or "-",
                r["xact_age"] or "-",
                r["query_age"] or "-",
            )
        )
        print("    %s" % tx)
        print("    %s" % (r["query"] or "").replace("\n", " "))
    return 0


# ── `watermark_report` (`--watermark`) — DELETED 2026-08-12 WITH ITS SUBJECT. ──────────────
#
# It printed hwm, lwm, the registry with each consumer's lag, and the count of observations
# below the floor. Every one of those five figures came from `consumer` or from the position
# column, so the report retired with them — and it is worth stating plainly why it was the
# LAST thing holding the tier up: **`consumer` existed so `--watermark` could print
# `consumer`.** Nothing outside the queue read the registry.
#
# ⚑⚑ ITS FINAL LINE ALREADY CONCEDED THE POINT, ONE COMMIT BEFORE THE DELETION: *"AND THE
# FIGURE BELOW IS NOW A DIAGNOSTIC, NOT A VERDICT. 'N observation(s) below the floor' answers a
# question nothing asks any more."* A readout kept because it is *"still the honest way to see
# whether a CURSOR is stalled"* is a readout kept for a reader that does not exist.
#
# ⚑⚑ AND THE INCIDENT IT RECORDED IS THE ONE TO CARRY OUT OF THIS WHOLE TIER. Straight after
# the pin's retirement this report said *"while one is registered the floor stays at its
# position and the tier does not drain BY POSITION"* — beside a sandbox that had just fully
# drained WITH the pin registered (`obs` 14,836 → 0). **A report explaining a mechanism its own
# numbers contradict is the stale-comment minefield in its worst form, because the reader
# trusts the prose over the figures.** `--lifecycle` is the surviving readout and it prints
# only what it computes.
#
# ⚑ THE KIND COLUMN'S DISPLAY ARGUMENT IS RESIDUE TOO: the kind was printed because *"a lag
# alone cannot be read"* — `scope_fix:resolver` at 0 with a 6.2M lag looked identical to a
# stalled cursor, and it was mis-read as exactly that. The general form outlives both column
# and report: **a number a reader must guess the meaning of needs a second column or no column.**


def lifecycle_report():
    """`--lifecycle` — every observation's STAGE and what holds it. Exit code."""
    import lifecycle as _lc

    c = lifecycle_census()
    print("chain:  %s\n" % " ▷ ".join(c["chain"]))
    for stage, n in c["stages"]:
        print("  %-14s %12s" % (stage, format(n, ",")))
    print()
    for i, (name, _f, because) in enumerate(_lc.LIFECYCLE):
        print("  %d %-10s %s" % (i, name, because))
    return 0
