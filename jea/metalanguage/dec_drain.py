# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""dec_drain.py — ⟡ladder-retire: RETIRE the `sourced` tier. THE STATEMENTS, ONLY.

⚑⚑ THIS MODULE IS DATA AND ACCESSORS AND NOTHING ELSE — no CLI, no `__main__`, no fixpoint
loop, no branch, `pycodemod --control` **0**. `dec_tree.py`'s seam, inherited verbatim: the
fixpoint ("run the rebuild rung until it writes nothing") is a mode-branch and belongs to the
CALLER (`scripts/sppf_drain.py`).

⚑⚑ THE TIER INDICES, VERIFIED RATHER THAN ASSUMED. `schema_decl._TIERS` is the authority:

    sourced   = {core_decoded}                  B    — the tier this retires
    vocab     = {dec_scalar}                    B+1
    tree      = {dec_node, dec_root}            B+2  — the licence
    treestage = {dec_stage, dec_ref}            declared disposable
    valstage  = {dec_val}                       the reconstruction's memo

so `retire_tier_sourced = DELETE FROM core_decoded WHERE predicate_for_build_tier_tree`,
and **B+2 resolves to `tree`**. The `+2` is proof-of-sufficiency and it BITES here: `vocab`
alone (B+1) determines nothing about a document — it is a bag of scalars with no structure —
so a drain licensed by "the vocabulary exists" would delete every document on the strength of
a relation that cannot distinguish them. `tree` is the first tier that has PROPAGATED the
material: it holds the shape, and `dec_root` holds which shape belongs to which document.

⚑⚑ THE PREDICATE IS WRITTEN ONCE AND APPEARS IN TWO STATEMENTS AT TWO MOMENTS. It is
`rebuilt IS NOT DISTINCT FROM core_decoded.dec` — `schema_decl.rebuild_sel` computes the
left-hand side and NOTHING here restates it:

    build  `root_sql`   INSERT INTO dec_root … WHERE rebuilt IS NOT DISTINCT FROM c.dec
    delete `retire_sql` DELETE FROM core_decoded c WHERE EXISTS (… shadow … c.dec)

Build asks *is it there now* and licenses the INSERT; delete asks *is it still there* and
licenses the DELETE. They are separate RUNS, so a build-time-only check would be
check-then-act across the largest possible window. This is not a check moved; it is a `WHERE`
clause appearing twice.

⚑⚑ `IS NOT DISTINCT FROM`, NEVER `=`. A document the higher tiers cannot rebuild produces NO
shadow row, and a document they rebuild to SQL NULL would compare `NULL = dec` → NULL →
neither true nor false → the row is NOT deleted, which is accidentally right; but the same
three-valued logic inside a `NOT EXISTS` or a negation flips the other way and drains
silently. The operator that treats NULL as a value is the one whose reading does not depend
on where the predicate sits.

⚑ AND THE LICENCE READS A **VIEW**, WHICH IS THE POINT. `core_decoded_shadow` is
`core_decoded` as the tree tier says it is; `core_decoded EXCEPT SELECT … FROM
core_decoded_shadow` is therefore the HELD SET as a relation rather than as a report somebody
has to run. See `schema_decl.SHADOWS` for why this one view is admissible under a policy that
purged six.
"""

# ── (1) THE REBUILD RUNG — one statement, one round of the value fixpoint ────────────────────
#
# ⚑⚑ ONE ROUND IS ONE LEVEL OF **JSON NESTING**, NOT ONE SPINE CELL. `schema_decl.rebuild_sel`
# walks a spine with a recursive CTE and aggregates in the OUTER query, so a 115,268-member
# object is resolved by a single statement; only a compound whose member is itself a compound
# has to wait. The corpus's `max_depth` is 4, so the fixpoint is a handful of rounds — the
# exact inversion of the build, which paid 115,294 rounds because cell *k* needed cell *k+1*'s
# ID and an INSERT cannot see its own effect.
#
# ⚑ `interior_pos` ALREADY EXCLUDES WHAT IS DONE (`NOT EXISTS (… dec_val …)`), so the rung is
# self-terminating: the caller runs it until it writes 0 rows and needs no round schedule, no
# counter and no `rnd` column. That is the difference a memo keyed by NODE rather than by
# ADDRESS buys.
#
# ⚑ `ORDER BY 1` IS THE LOCK ORDER, AND IT IS THE ONLY CONCURRENCY DEVICE THIS STATEMENT
# CARRIES — ⟡ladder-2b's discipline, unchanged: a set-based rung holds N row locks until it
# commits and that hold is not removable, but every writer offering rows in the same total
# order means a waiter is always strictly behind, so no two writers can each hold what the
# other wants.
#
# ⚑ ONE TABLE IS WRITTEN, SO THERE IS NO CROSS-TABLE ORDER TO GET WRONG. `dec_tree`'s rung
# needed `(SELECT count(*) FROM n) >= 0` to force `dec_node` before `dec_ref`; this rung writes
# `dec_val` and reads everything else, so the device has nothing to force and is absent rather
# than copied.
_REBUILD = "INSERT INTO dec_val (id, v) %s ORDER BY 1 ON CONFLICT DO NOTHING"

# ── (2) THE HEADER BUILD — tier B+2's missing half, under the predicate ──────────────────────
#
# ⚑⚑ THE ROOT COMES FROM `dec_ref`, WHICH IS THE ONE PLACE IT CAN COME FROM BEFORE THIS ROW
# EXISTS, AND THAT IS WHY THE ORDER OF THE WHOLE ARC IS FORCED. `dec_ref` is `treestage` and
# `core_decoded` is `sourced`; both are retired below. So the header must be built while both
# still exist, which is the model's *"always build tier B+2 before tier B−1 before tier B"*
# arriving as a hard dependency rather than as a scheduling preference.
#
# ⚑ THE ROOT ADDRESS IS `(sid = 1, kind = 0, min(ord))` — `dec_tree.roots_sql`'s derivation,
# reused rather than re-derived. `comp`'s `row_number()` orders by path and the empty path
# sorts first, so the root compound is `sid = 1`; the `min(ord)` is what makes it the HEAD of
# that compound's spine rather than one of its tails.
#
# ⚑⚑ AND THE PREDICATE IS THE WHOLE POINT OF THIS STATEMENT. A header inserted without
# `rebuilt IS NOT DISTINCT FROM c.dec` would be a claim that the tree reconstructs the
# document, made by a statement that never checked — and every downstream reading of the
# shadow would inherit it. The reconstruction runs HERE, against the live `dec`, while the
# source still exists.
_ROOT = """\
WITH r AS (%s)
INSERT INTO dec_root (core_id, relpath, mtime, producer, root)
SELECT c.core_id, c.relpath, c.mtime, c.producer, r.id
  FROM r
  JOIN dec_node n ON n.id = r.id
  JOIN dec_ref f ON f.head = n.head AND f.c1 = n.c1 AND f.c2 = n.c2
                AND f.sid = 1 AND f.kind = 0
  JOIN core_decoded c ON c.core_id = f.core_id
 WHERE f.ord = (SELECT min(f2.ord) FROM dec_ref f2
                 WHERE f2.core_id = f.core_id AND f2.sid = 1 AND f2.kind = 0)
   AND r.v IS NOT DISTINCT FROM c.dec
   AND (%%s::text IS NULL OR c.core_id = %%s::text)
 ORDER BY 1
ON CONFLICT DO NOTHING"""


def rebuild_sql():
    """`(sql, params)` — ONE round of the reconstruction fixpoint. Writes `dec_val`.

    ⚑ NO SCOPE PARAMETER, DELIBERATELY, AND IT IS NOT AN OVERSIGHT. `dec_node` is
    CONTENT-keyed and shared across documents — that is the tier's whole claim — so "the
    interior positions of document X" is not a well-formed request: one node belongs to every
    document that contains it. A per-document rebuild would either re-walk shared structure
    once per owner or silently attribute it to the first. The memo is global because the tree
    is.
    """
    import schema_decl as _D

    return (_REBUILD % _D.compile_sel(_D.rebuild_sel(_D.interior_pos, "i")), ())


def root_sql(core_id=None):
    """`(sql, params)` — build tier B+2's header, under the reconstruction predicate."""
    import schema_decl as _D

    return (_ROOT % _D.compile_sel(_D.rebuild_sel(_D.root_pos, "r")), (core_id, core_id))


# ── (3) THE RETIRE RUNG — the DELETE, and its dry run ────────────────────────────────────────
#
# ⚑⚑ ONE STATEMENT, AND THE COMPARISON IS INSIDE IT. `rebuild the core's rows from the durable
# side, compare to the live rows, delete ONLY on equality` (`Substrate.Lifecycle.Drainable`) is
# three acts in prose and must be ONE act in SQL, or the comparison happens at a different
# moment from the delete and something can change in between. `EXISTS (… s.dec IS NOT DISTINCT
# FROM c.dec)` is the comparison, evaluated per row, against the row being deleted.
#
# ⚑⚑ AND AN A-PRIORI STRUCTURAL CHECK CANNOT SUBSTITUTE FOR IT — F31's finding, which cost 926
# silently-wrong rows. "The tree exists and is complete" is a fact about the DERIVATION, and
# the build's own census is computed from the work list the build also wrote, so a walk that
# dropped a value is absent from both and reads as complete. Only a comparison against `dec`
# ITSELF sees that class, and it can only run while `dec` still exists — which is exactly the
# moment this statement runs.
#
# ⚑ NO `ORDER BY`: postgres's DELETE has none. What replaces it is that every writer sends the
# IDENTICAL statement, so the planner gives every writer the same scan order and a waiter is
# always strictly behind — the weaker property, stated as the weaker property. Measured under
# concurrency rather than argued; see `--drain-concurrency`.
#
# ⚑ THE SCOPE IS THE NULLABLE DISJUNCTION AND NOT A CONCRETE EQUALITY, which is the opposite of
# `dec_tree`'s walk. That statement's cardinality flowed from its scope, so an unestimable
# disjunction cost 55s per document; this one reads two indexed relations of 43 rows and the
# estimate decides nothing.
_RETIRE = """\
DELETE FROM core_decoded c
 WHERE EXISTS (SELECT 1 FROM core_decoded_shadow s
                WHERE s.core_id = c.core_id
                  AND s.dec IS NOT DISTINCT FROM c.dec)
   AND (%s::text IS NULL OR c.core_id = %s::text)"""

# ── (4) THE LICENCE, AS A RELATION — held vs licensed, and WHY ───────────────────────────────
#
# ⚑⚑ `EXCEPT` IS THE HELD SET AND IT IS THE OBSERVABILITY THE SHADOW WAS BUILT FOR. Before the
# view, "which documents are not yet drainable" was a computation somebody had to run and then
# describe; it is now `SELECT core_id FROM core_decoded EXCEPT SELECT core_id FROM
# core_decoded_shadow` — a relation, joinable, countable, and answerable per document.
#
# ⚑ THREE VERDICTS, COUNTED APART, BECAUSE THEY SEND THE OPERATOR TO DIFFERENT PLACES —
# `dec_tree.complete_sql`'s rule. `no-header` = the tree tier has no `dec_root` row (run
# `--drain-root`, or the tree is not built for this document at all). `mismatch` = a header
# exists and the shadow's `dec` differs from the live one (the tree is WRONG for this document
# — nothing here will fix it and nothing may delete it). `licensed` = the predicate holds. A
# single "not drainable" number would collapse a missing build into a corrupted one.
_LICENCE = """\
SELECT c.core_id, c.relpath,
       (CASE WHEN s.core_id IS NULL THEN 'no-header'
             WHEN s.dec IS NOT DISTINCT FROM c.dec THEN 'licensed'
             ELSE 'mismatch' END) AS verdict,
       pg_column_size(c.dec) AS bytes
  FROM core_decoded c
  LEFT JOIN core_decoded_shadow s ON s.core_id = c.core_id
 WHERE (%s::text IS NULL OR c.core_id = %s::text)
 ORDER BY 3, 2"""

# ── (5) THE ANSWER — a RETIRED document, read back from the durable tiers alone ──────────────
#
# ⚑⚑ THIS IS THE LADDER'S ENTIRE CLAIM AND IT IS A SELECT, NOT AN ARGUMENT. After the drain,
# `core_decoded` holds nothing for these documents and the shadow still answers for every one
# of them — `relpath`, `mtime`, `producer` and `dec`, byte-identical. It reads `dec_root`,
# `dec_node`, `dec_scalar` and `dec_val`, and NONE of `core_decoded`, `dec_stage` or `dec_ref`.
#
# ⚑ IT IS THE SHADOW UNCHANGED, WITH A SCOPE. A separate reader would be a second
# reconstruction — the one thing this arc may not have two of.
_ANSWER = """\
SELECT s.core_id, s.relpath, s.mtime, s.producer, s.dec
  FROM core_decoded_shadow s
 WHERE (%s::text IS NULL OR s.relpath = %s::text)
 ORDER BY 2"""

# ── (6) THE STAGING RETIRE — a CLEANUP, and it is NOT an instance of the model ───────────────
#
# ⚑⚑ SAID PLAINLY BECAUSE THE TWO CLAIMS ARE DIFFERENT AND THE WEAKER ONE IS TRUE HERE. The
# model's retire is licensed by a HIGHER tier that reconstructs the retired rows;
# `retire_tier_B = DELETE FROM b WHERE predicate_for_build_tier_{B+2}` needs a `B+2` to
# resolve. For `treestage` it does not: nothing sits above `dec_stage`/`dec_ref`, nothing
# reconstructs FROM them, and after `sourced` is drained nothing can rebuild them either. So
# this is a TRUNCATE with a conscience, not a rung.
#
# ⚑⚑ AND IT IS STILL NOT FREE, WHICH IS THE PART THE "just a cleanup" reading would miss:
# `dec_ref` is where a document's ROOT lives until `dec_root` exists, so retiring the staging
# before the header would destroy the only pointer from a document to its tree — the tree would
# hold every byte of the corpus and be unable to name a document. That ordering constraint IS
# the model's, even though the licence is not.
#
# ⚑ SO THE PREDICATE IS THE HEADER'S EXISTENCE, WHICH IS STRICTLY STRONGER THAN NEEDED AND IS
# CHOSEN FOR THAT REASON. `dec_root` is written only under the reconstruction predicate, so
# "this document has a header" already means "the tree rebuilt it exactly". A cleanup that
# waits for a licence it does not need cannot run early by accident.
_RETIRE_REF = """\
DELETE FROM dec_ref f
 WHERE EXISTS (SELECT 1 FROM dec_root d WHERE d.core_id = f.core_id)
   AND (%s::text IS NULL OR f.core_id = %s::text)"""

_RETIRE_STAGE = """\
DELETE FROM dec_stage s
 WHERE EXISTS (SELECT 1 FROM dec_root d WHERE d.core_id = s.core_id)
   AND (%s::text IS NULL OR s.core_id = %s::text)"""


# ── (7) THE INVERSE — refill `sourced` FROM the shadow ──────────────────────────────────────
#
# ⚑⚑ THIS IS THE `PROMOTE` DIRECTION AND IT IS WHAT MAKES THE LINK A LINK RATHER THAN A
# DELETION. The model: *"a record's TIER is an EFFICIENCY fact, not an AVAILABILITY fact"* —
# which is a claim about what can be materialised on demand, and a claim nobody had made
# operational. `INSERT INTO tier_{N-1} SELECT … FROM tier_{N+1}` is the flow the model names,
# spelled over the shadow; the retire is its dual, and running them in sequence returns the
# store to a state the drain accepts again.
#
# ⚑ IT IS ALSO WHAT MAKES THE CONCURRENCY DEMONSTRATION REPEATABLE. A drain is a one-way trip:
# once six rows are gone there is nothing left for twelve racing processes to contend over, so
# without an inverse the contention test could be run exactly once per corpus.
#
# ⚑ `ON CONFLICT DO NOTHING` AND NOT `DO UPDATE`. A `core_decoded` row that still exists is
# the AUTHORITY — it is the tier the shadow is a shadow OF — so a restore must never overwrite
# a live row with a reconstruction of it. The two agreeing is the drain's licence; the two
# disagreeing is a `mismatch` for an operator, not a row for this statement to resolve.
_RESTORE = """\
INSERT INTO core_decoded (core_id, relpath, mtime, producer, dec)
SELECT s.core_id, s.relpath, s.mtime, s.producer, s.dec
  FROM core_decoded_shadow s
 WHERE (%s::text IS NULL OR s.core_id = %s::text)
 ORDER BY 1
ON CONFLICT DO NOTHING"""


def retire_sql(core_id=None):
    """`(sql, params)` — THE RETIRE RUNG. Delete only on equality, in one statement."""
    return (_RETIRE, (core_id, core_id))


def restore_sql(core_id=None):
    """`(sql, params)` — the retire's INVERSE: materialise `sourced` from the shadow."""
    return (_RESTORE, (core_id, core_id))


def licence_sql(core_id=None):
    """`(sql, params)` — per document: licensed / mismatch / no-header, and its size."""
    return (_LICENCE, (core_id, core_id))


def answer_sql(relpath=None):
    """`(sql, params)` — read a document back from the durable tiers alone."""
    return (_ANSWER, (relpath, relpath))


def retire_ref_sql(core_id=None):
    """`(sql, params)` — retire the `treestage` address memo. A cleanup, not a rung."""
    return (_RETIRE_REF, (core_id, core_id))


def retire_stage_sql(core_id=None):
    """`(sql, params)` — retire the `treestage` work list. A cleanup, not a rung."""
    return (_RETIRE_STAGE, (core_id, core_id))


def census_sql():
    """`(sql, params)` — the drain's population, per relation, in one row.

    ⚑ `held` IS THE HEADLINE AND `drained` IS NOT ENOUGH — ⟡ladder-2b's rule, twice inherited.
    "37 drained" reads identically whether six documents are held for cause or the scope was
    never populated, so the held count and the source population ride beside it.

    ⚑ `stale_memo` IS THE RESIDUE `dec_val`'s OWN NOTE NAMES, MADE OBSERVABLE. A memo row is
    trusted as a function of `dec_node`, which every rung in this ladder only ever inserts
    into; a row whose node is GONE is the one state that could make the shadow answer from
    something the tree no longer holds. It is a number to read, not a proof — nothing here
    deletes from `dec_node`, and if that stops being true this is where it shows.
    """
    return (
        "SELECT (SELECT count(*) FROM core_decoded) AS sourced, "
        "(SELECT count(*) FROM dec_root) AS headers, "
        "(SELECT count(*) FROM dec_val) AS memo, "
        "(SELECT count(*) FROM dec_stage) AS staged, "
        "(SELECT count(*) FROM dec_ref) AS refs, "
        "(SELECT count(*) FROM core_decoded_shadow) AS shadow, "
        "(SELECT count(*) FROM (SELECT core_id FROM core_decoded "
        "EXCEPT SELECT core_id FROM core_decoded_shadow) AS h) AS held, "
        "(SELECT count(*) FROM dec_val v WHERE NOT EXISTS "
        "(SELECT 1 FROM dec_node n WHERE n.id = v.id)) AS stale_memo, "
        "(SELECT coalesce(sum(pg_column_size(dec)), 0) FROM core_decoded) AS bytes",
        (),
    )
