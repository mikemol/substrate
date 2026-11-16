#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""sppf_vocab.py — ⟡ladder-2b: the VOCAB tier. Every SCALAR in `dec`, keys and values alike.

⚑⚑ THE VOCABULARY IS A **VARIANT**, NOT A STRING TABLE — a correction to ⟡ladder-2 (user,
2026-08-12: *"That calls for a VARIANT type, not a simple exclusion."*). The first cut interned
only the jsonb strings and EXCLUDED numbers, booleans and JSON nulls, on the argument that
coercing them to text would MANUFACTURE an identity `dec` does not have — collapsing the
integer `0` and the string `\"0\"` into one row. The hazard is real; the remedy was an omission
where a TAG was needed. `jsonb` is already the tagged type: `'0'::jsonb` and `'\"0\"'::jsonb`
are distinct values, `jsonb_typeof` reads the tag, and `UNIQUE` is expressible on jsonb
precisely because jsonb HAS btree equality — the same property that chose `jsonb` over `json`
for `core_decoded.dec` one tier down. So the collapse is avoided by NOT PROJECTING (`#>> '{}'`
is deleted from the value branch) rather than by NOT INTERNING.

⚑⚑ AND THE EXCLUSION WAS NOT MERELY INCOMPLETE — IT BROKE THE NEXT RUNG. Step 4 reconstructs
the document as a CNF-2 binary tree in which a LEAF's node id IS its value id. Numbers alone
were 1,649,947 of 4,126,675 walked values (~40%): excluded, two fifths of the leaves have no
identity and cannot be addressed at all.

⚑⚑ ONE RUNG, NOT TWO, AND THE "TWO STEPS" WERE ONE ALL ALONG. The work was posed as step 2
("ensure all of the KEYS in the jsonb structure exist in a strings table") and step 3 ("the
same thing with the VALUES … honestly, into the same strings table"). They differ ONLY in
which accessor enumerates the data — `jsonb_object_keys` versus the walk itself — and share
the same table, the same id assignment and the same `WHERE NOT EXISTS`. Landing them separately
would have written the same statement twice and invited a `kind` column to tell them apart.

⚑⚑ THE TABLE HAS NO NOTION OF KEY-NESS, AND THAT IS THE DESIGN RATHER THAN AN OMISSION.
Position is a property of the STRUCTURE, not of the value: a name appearing as a field name in
one document and as a constructor name in another is ONE row, because `to_jsonb(<that text>)`
is the same jsonb scalar either way. Asked how much key and value vocabulary overlaps, the
answer is 100% — a question that presupposed two populations when there is one. So: no `kind`
column, no partitioned id space, and the overlap is not a measurement this module takes.

⚑ THE TWO PROPERTIES THE RELATION MUST HOLD AT ONCE, and they pull in opposite directions:
**one vocabulary** (a key `\"foo\"` and a string value `\"foo\"` are ONE row) and **no
manufactured identity** (the number `0` and the string `\"0\"` are TWO rows). A `kind` column
would buy the second by giving up the first; a text coercion buys the first by giving up the
second; the jsonb scalar is what holds both, because the tag it carries is the datum's type
and not its position.

    --ingest-vocab [RELPATH]   the RUNG — one statement, whole table or one document
    --vocab-census [FILTER]    completeness EXACT/MISSING driven from `dec` itself, at every
                               depth, plus the vocabulary-size measurement and the per-kind
                               (`jsonb_typeof`) breakdown
    --vocab-concurrency [N]    N rungs AT ONCE over the FILTER's documents; reports 40P01
    --vocab-collisions         the rows a `#>> '{}'` text coercion WOULD have merged — the
                               witness that the variant is necessary rather than theoretical

⚑ ITS OWN TOOL RATHER THAN THREE MORE MODES ON `sppf_db`, AND THE CAP IS WHAT DECIDED IT.
⟡ladder-1 put the SOURCED tier's three modes on `sppf_db` behind one dispatch line, recording
*"`sppf_db` sits against a 1200-line cap that exists to force exactly that question"*. It now
reads 1196 of 1200. Three usage lines plus a dispatch plus an import is eight code lines
against four of headroom — so the cap fires, and the forcing function's answer is that the
next tier's SURFACE lives with the next tier's CODE. What `sppf_db` still owns is the SUITE
(`vocab_cases`), because `run_selftests.discover()` counts a suite as the PAIR of a
`_selftest` def and a dispatch on the selftest flag, and defining neither here keeps the
total at 69.

⚑⚑ AND THIS FILE MUST NOT SPELL THAT FLAG AS A LITERAL — MEASURED, 2026-08-12, BY MINTING A
PHANTOM SUITE WITH A SENTENCE. `run_selftests.HANDLES_SELFTEST` is a bare `re.compile` of the
flag text matched over the WHOLE source, so the paragraph above — explaining that this module
is not a suite — is what made the runner treat it as one: `NOT-OK — 1 of 70 suite(s): 1 silent
— scripts/sppf_vocab.py`, with this file's bare-run usage block read as a suite verdict. That
is "a guard satisfied by the comment naming what it guards", occurring in a predicate whose
own file records that exact class three times over.

⚑ THE DEFECT IS IN THE PROXY AND IS DELIBERATELY NOT REPAIRED HERE. `HAS_ENTRY` is anchored
(`^if …`) while its partner is not, so the pair is half structural and half textual; reading
the flag off the AST is the fix, and it belongs to `run_selftests`, whose discovered
population every commit gate depends on — widening that predicate blind is how three real
suites were erased before. The other available answer is to give this module a real suite and
move `vocab_cases` out of `sppf_db`, which takes the count to 70 and changes the invariant
this arc was told to hold. Both are named; neither is taken here.

⚑ THIS MODULE TOUCHES NO FILESYSTEM. `sppf_decode` decodes `.agdai` files; this reads
`core_decoded` and writes `dec_scalar`. Its scope argument is therefore a `core_decoded.relpath`
as STORED, never a path to resolve — a rung whose input is the store must not be able to
disagree with the store about which documents exist.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "jea", "metalanguage"))

import schema as _schema  # THE schema declaration: rows/execute/apply

# ── (1) THE WALK — every jsonb value in the selected document(s), at EVERY depth ─────────────
#
# ⚑⚑ THE ENUMERATION IS RECURSIVE BECAUSE STRINGS LIVE AT EVERY DEPTH, AND THIS IS THE PART
# MOST LIKELY TO BE MIS-READ AS "NOT DOABLE IN SQL". It is doable, it is one CTE, and it is
# written out longhand here rather than cleverly on purpose.
#
# ⚑⚑ THE RECURSIVE TERM MAY NAME THE CTE EXACTLY ONCE. The obvious spelling — one `UNION ALL`
# branch descending into objects and a second descending into arrays — is a PARSE ERROR
# (*"recursive reference to query `node` must not appear more than once"*), because that is two
# references. Folding both cases into ONE `CROSS JOIN LATERAL (… UNION ALL …)` makes it a
# single FROM-entry reference, which is what the grammar allows. Anyone "simplifying" this back
# into two branches will get the error and should read this note rather than conclude the walk
# has to happen in python.
#
# ⚑ `jsonb_path_query(dec, 'strict $.**')` WAS THE OTHER CANDIDATE AND IT CANNOT SEE A KEY.
# The `.**` accessor returns member VALUES at every level; object keys are not values, so half
# the population — the larger half, 3,301,700 of 4,127,358 occurrences measured — is invisible
# to it. A shorter statement that answers a different question is not the same rung.
#
# ⚑⚑ THE CTE IS NAMED `node` AND **SO IS A VIEW IN THIS SCHEMA** (`CREATE OR REPLACE VIEW node
# AS SELECT _node.node_id, …` — see `schema.py --ddl postgres`). This works because a CTE name
# takes precedence over a table or view of the same name for the whole query, and it has worked
# since ⟡ladder-2 — but the failure mode if it ever stopped is the dangerous kind, not the loud
# kind: `FROM node` would silently resolve to the SPPF view, which HAS a `node_id` and no `v`,
# so the statement would fail on the column rather than on the relation and the message would
# name the wrong thing. Recorded here rather than renamed, because renaming the CTE touches
# every accessor and the shadowing is a guarantee, not an accident — but a reader who moves
# this CTE into a subquery that does not carry it should expect the view, not an error.
#
# ⚑ THE SCOPE IS A PARAMETER, NOT A SECOND STATEMENT. `NULL` means the whole table; a
# `core_id` means one document. One rung serves the full sweep and the per-document
# concurrency probe, so the thing under test and the thing shipped are the same string. The
# `::text` casts are load-bearing: an untyped `%s` compared to NULL leaves postgres unable to
# infer the parameter's type (`could not determine data type of parameter $1`).
_NODE = """\
WITH RECURSIVE node(v) AS (
        SELECT d.dec
          FROM core_decoded d
         WHERE (%s::text IS NULL OR d.core_id = %s::text)
    UNION ALL
        SELECT c.child
          FROM node
          CROSS JOIN LATERAL (
                  SELECT e.value
                    FROM jsonb_each(node.v) AS e
                   WHERE jsonb_typeof(node.v) = 'object'
              UNION ALL
                  SELECT a.value
                    FROM jsonb_array_elements(node.v) AS a
                   WHERE jsonb_typeof(node.v) = 'array'
          ) AS c(child)
)"""

# ── (2) THE TWO ACCESSORS — one vocabulary ───────────────────────────────────────────────────
#
# ⚑⚑ THIS IS THE WHOLE OF "STEP 2 AND STEP 3". The first branch is the KEY accessor, the
# second is the VALUE accessor, and they meet in `UNION ALL` over one column. Nothing
# downstream can tell which branch a datum came from, which is exactly the property the
# design asks for.
#
# ⚑ `UNION ALL`, NOT `UNION`, AND THE DISTINCT IS TAKEN LATER — because `occ` is ALSO the
# population the census counts OCCURRENCES over. Deduplicating here would make the sharing
# ratio unmeasurable and would hide the one number that says anything about the corpus.
#
# ⚑⚑ `to_jsonb(k.s)` AND **NOT** `k.s`, AND THE VALUE BRANCH KEEPS `node.v` UNPROJECTED — this
# is the ⟡ladder-2b correction in two lines (user, 2026-08-12: *"That calls for a VARIANT type,
# not a simple exclusion."*). The old value branch read `SELECT node.v #>> '{}' … WHERE
# jsonb_typeof(node.v) = 'string'`, and **THAT PROJECTION IS THE COERCION**: `#>> '{}'` strips
# the type tag, so `'0'::jsonb` and `'"0"'::jsonb` both arrive as the text `0` and the relation
# cannot tell them apart. ⟡ladder-2 avoided the collapse by NARROWING the filter to strings,
# which paid for correctness with 40% of the corpus. Keeping the jsonb makes the filter
# WIDENABLE instead: the tag rides along, so every scalar kind can be admitted at once.
#
# ⚑ THE KEY BRANCH LANDS IN THE SAME TYPE, WHICH IS WHAT "ONE VOCABULARY" NOW MEANS. A key is
# text; `to_jsonb(<text>)` is the jsonb STRING with that value — so a key `"foo"` and a string
# value `"foo"` are the identical jsonb datum and therefore one row, with no `kind` column and
# no partitioned id space. (`to_jsonb` and not `k.s::jsonb`: the cast PARSES the text as a JSON
# document, so a key spelled `null`, `123` or `[1]` would arrive as a JSON null, a number or an
# ARRAY rather than as the string it is. `to_jsonb` wraps, it does not parse.)
#
# ⚑ ⟡ladder-2's NOTE ON THE PROJECTION, KEPT AS RESIDUE BECAUSE IT IS THE MEASUREMENT THAT
# MAKES THE NEW BRANCH READABLE: *"`#>> '{}'` AND NOT `::text`. `to_jsonb('a')::text` is `\"a\"`
# WITH the JSON quotes and with any interior escapes still escaped; `#>> '{}'` extracts the
# string's VALUE. Interning the quoted rendering would put a different string in the table from
# the one in the document, and nothing downstream could detect it — every row would look
# plausible."* Both halves of that choice are now MOOT rather than wrong: the column is jsonb,
# so neither rendering is stored and the datum itself is. `v::text` survives only in the DIGEST
# and in the lock ORDER, where the quoted form is exactly what is wanted — it is the rendering
# that keeps `0` and `\"0\"` apart, which is the opposite of what it was rejected for here.
#
# ⚑⚑ THE VALUE PREDICATE IS THE COMPLEMENT OF WHAT `node` DESCENDS INTO, NOT A ROSTER OF SCALAR
# KINDS. `_NODE` recurses through `object` and `array`; everything else is a LEAF. Writing the
# filter as `NOT IN ('object','array')` makes that one fact, stated once: a value the walk does
# not descend into is a value the walk must intern, so no kind can fall between the two and be
# silently dropped. The roster spelling `IN ('string','number','boolean','null')` is the same
# set today and is the frozen-roster shape this tree keeps paying for.
_OCC = """,
occ(v) AS (
        SELECT to_jsonb(k.s)
          FROM node
          CROSS JOIN LATERAL jsonb_object_keys(node.v) AS k(s)
         WHERE jsonb_typeof(node.v) = 'object'
    UNION ALL
        SELECT node.v
          FROM node
         WHERE jsonb_typeof(node.v) NOT IN ('object', 'array')
)"""

# ── (3) THE RUNG ─────────────────────────────────────────────────────────────────────────────
#
# ⚑⚑ EVERY SCALAR IS INTERNED — THE VARIANT, NOT THE EXCLUSION (⟡ladder-2b, user 2026-08-12).
# ⟡ladder-2 shipped this block saying *"NON-STRING SCALARS ARE NOT INTERNED"*, on the argument
# that *"coercing them would MANUFACTURE an identity the documents do not have. The integer `0`
# and the string `\"0\"` are different values in `dec`, and `dec_string` cannot distinguish them
# once both are text."* That hazard is REAL and the note is kept for it; the remedy was wrong.
# The answer to "text coercion conflates two kinds" is a TAG, and `jsonb` is already the tagged
# type — so the collapse is avoided by NOT PROJECTING rather than by NOT INTERNING.
#
# ⚑⚑ AND THE EXCLUSION BROKE THE NEXT RUNG, WHICH IS THE HALF THE ORIGINAL ARGUMENT COULD NOT
# SEE. Step 4 reconstructs the document as a CNF-2 binary tree in which a LEAF's node id IS its
# value id. Numbers alone were 1,649,947 of 4,126,675 walked values (~40%): with them excluded,
# two fifths of the tree's leaves have no identity and cannot be addressed at all. The second
# argument for the exclusion — *"an integer is ALREADY a number, so a number/string mapping
# buys it nothing"* — is what made it look self-justifying, and it is false for the same
# reason: the id is not a numeric handle for a string, it is a NODE identity for a leaf.
#
# ⚑ WHAT IS STILL NOT INTERNED IS `object` AND `array`, AND THAT IS NOT AN EXCLUSION. They are
# the values `node` DESCENDS INTO; the tree represents them structurally, by their children.
# `--vocab-census` reports them beside the interned kinds so the boundary is a number rather
# than an absence someone has to notice.
#
# ⚑ `WHERE NOT EXISTS` IS THE BRIEF'S SHAPE AND IT IS NOT THE IDEMPOTENCE MECHANISM. It is a
# VOLUME reduction: without it every run offers 116,512 rows to the conflict machinery instead
# of the handful that are new. Idempotence is `ON CONFLICT (s) DO NOTHING` — a fact the ENGINE
# decides against the index, not one the SELECT decided a moment earlier and could be wrong
# about by the time the INSERT runs.
#
# ⚑⚑ `ORDER BY … COLLATE "C"` IS A LOCK ORDER, AND IT IS THE ONE THING HERE THAT IS ABOUT
# CONCURRENCY. A set-based rung inserts N rows in ONE statement and therefore HOLDS N row
# locks until it commits — the hold-and-wait `insert_row`'s note removes by writing one row per
# statement is NOT removable here, because the set IS the unit of work. What is removable is
# the CYCLE: `INSERT … ON CONFLICT` waits on the in-progress transaction that inserted a
# conflicting key, so two writers taking overlapping vocabularies in DIFFERENT orders is a
# 40P01 waiting to be constructed. Every writer sorting by the same total order means a waiter
# is always strictly behind, so no two writers can each hold what the other wants.
#
# ⚑ AND THIS IS NOT THE SORT `upsert` RETIRED, THOUGH IT LOOKS LIKE IT. That note reads *"a
# global order makes the CYCLE unconstructible while leaving the HOLD in place"* — correct
# there, because removing the batch was available and was the better fix. Here it is not: a
# rung is one statement by construction. So the honest statement is that the hold REMAINS and
# only the cycle is removed, which is a weaker property than ⟡ladder-1's and is named as such
# rather than borrowed.
#
# ⚑ `COLLATE "C"` AND NOT THE DATABASE COLLATION (`en_US.utf8` here). The lock-order argument
# needs a total order every writer agrees on; byte order is the one that does not move if the
# database is ever recreated under a different locale.
#
# ⚑⚑ AND UNDER ⟡ladder-2b IT HAS TO BE `vocab.v::text COLLATE "C"`, BECAUSE **jsonb REFUSES A
# COLLATION** — measured, not inferred: `ORDER BY <jsonb> COLLATE "C"` raises
# `DatatypeMismatch: collations are not supported by type jsonb`. Plain `ORDER BY vocab.v` is
# available and IS deterministic, but jsonb's btree order compares its string component under
# the DATABASE default collation, which is exactly the dependency the note above removes. The
# `::text` rendering is canonical and INJECTIVE on a set of pairwise-distinct jsonb scalars —
# a number never renders quoted, `true` never renders as `"true"`, `null` never as `"null"`,
# and two numerics that render alike are `=` and so were already collapsed by `DISTINCT` — so
# the cast is a total order, not a partial one with silent ties. A tie is the thing that would
# break this: two writers disagreeing on the order of two rows is a cycle, which is what the
# clause exists to make unconstructible.
#
# ⚑ POSTGRES INSERTS IN THE ORDER THE SUBPLAN PRODUCES ROWS — relied upon here, and stated
# rather than assumed silently. It is not an SQL-standard guarantee; it is executor behaviour
# (a Sort feeding ModifyTable), and if it ever changed the failure mode would be a 40P01 under
# `--vocab-concurrency`, which is exactly what that mode exists to see.
#
# ⚑ THE `id` IS NEVER MENTIONED. `dec_scalar.id` is `GENERATED ALWAYS AS IDENTITY`, so naming
# it in the column list is not merely unnecessary — postgres REFUSES it. That is the guard
# against the ⑸ defect (a client-side `max(id)+1` held across statements) being enforced by
# the engine instead of by everyone remembering it.
#
# ⚑ `DISTINCT` AND `ON CONFLICT (v)` BOTH ARBITRATE ON **jsonb EQUALITY**, WHICH IS THE WHOLE
# REASON THIS IS A SMALL CHANGE. `json` has no equality operator at all — no `DISTINCT`, no
# `UNIQUE`, no conflict target — so the rung would not have been expressible over it. That
# property is what decided `jsonb` for `core_decoded.dec` one tier down, and it is being spent
# a second time here.
_RUNG = """,
vocab(v) AS (SELECT DISTINCT occ.v FROM occ)
INSERT INTO dec_scalar (v)
SELECT vocab.v
  FROM vocab
 WHERE NOT EXISTS (SELECT 1 FROM dec_scalar t WHERE t.v = vocab.v)
 ORDER BY vocab.v::text COLLATE "C"
ON CONFLICT (v) DO NOTHING"""


def intern_scalars_sql(core_id=None):
    """`(sql, params)` — the ⟡ladder-2 rung, verbatim, as ONE statement.

    ⚑⚑ SPLIT OUT SO A GUARD CAN ANCHOR ON THE COMPILED SQL — AND THAT IS NOT SUFFICIENT ON ITS
    OWN. `_insert_row_sql`'s own residue records the measured reason: a case asserting the
    statement's shape by scanning source text was forged with an SQL COMMENT (`-- MUTATION: …`)
    and the suite read green, because SQL has comments too. So `vocab_cases` drives this
    BEHAVIOURALLY against a real relation, and the compiled-SQL cases only pin properties a
    comment cannot fake (a `--` appearing at all is itself a failure).
    """
    return (_NODE + _OCC + _RUNG, (core_id, core_id))


def intern_scalars(con, core_id=None):
    """THE RUNG. Returns the number of values interned (0 when the vocabulary is already whole).

    ⚑ THE COUNT IS THE OBSERVABLE. `rowcount` is the ONLY way a caller distinguishes "the
    vocabulary was already complete" from "nothing was in scope" without issuing the SELECT
    this design exists to remove — and the two are different facts (`insert_row`'s note, one
    tier up).
    """
    sql, params = intern_scalars_sql(core_id)
    cur = con.cursor() if hasattr(con, "cursor") else con
    cur.execute(sql, params)
    return cur.rowcount if getattr(cur, "rowcount", -1) >= 0 else 0


def vocab_digest(con):
    """The relation's CONTENT, as one row — `{rows, ids, values, digest}`.

    ⚑ IDEMPOTENCE IS "0 ROWS WRITTEN **AND** THE RELATION UNCHANGED", AND THE SECOND HALF NEEDS
    AN INSTRUMENT. A rung that deleted every row and rewrote it identically also reports 0 new
    rows on the third run; a digest over `(id, v)` ordered by `id` is what separates them,
    because a rewrite reassigns identities. `count(DISTINCT id)`/`count(DISTINCT v)` ride along
    because a vocabulary whose id map is not a bijection is broken in a way no rowcount shows.

    ⚑ `v::text` IN THE DIGEST, WHICH IS THE **TAGGED** RENDERING AND NOT THE COERCION. `v::text`
    renders `'0'::jsonb` as `0` and `'\"0\"'::jsonb` as `\"0\"` — quotes included — so the two
    contribute different bytes. `v #>> '{}'` renders BOTH as `0`, which would make the digest
    blind to precisely the distinction ⟡ladder-2b exists to keep, and a rewrite that swapped one
    for the other would read byte-identical.

    ⚑ `AS vals` AND NOT `AS values`: `VALUES` is a reserved word and the alias is a syntax error
    unquoted. The python key stays `values` — the SQL spelling is the constrained one.
    """
    for r in _schema.rows(
        con,
        "SELECT count(*) AS rows, count(DISTINCT id) AS ids, "
        "count(DISTINCT v) AS vals, "
        "md5(coalesce(string_agg(id::text || ' ' || v::text, E'\\n' "
        "ORDER BY id), '')) AS digest FROM dec_scalar",
    ):
        return dict(rows=r["rows"], ids=r["ids"], values=r["vals"], digest=r["digest"])
    return dict(rows=0, ids=0, values=0, digest=None)


def vocab_census(con, core_id=None):
    """The measurement, driven from `dec` ITSELF at every depth — never from a roster.

    ⚑⚑ THE EXPECTATION IS DERIVED, NOT LISTED. A hand-written set of "the keys a decoded core
    has" is the frozen-roster defect this tree records repeatedly: it would pass while a key
    the decoder started emitting last week went uninterned, because the roster cannot know
    about it. `expected` here is the walk's own output, so a new key is in the expectation the
    moment it is in a document.

    ⚑ `missing` IS THE HEADLINE AND `present` IS NOT ENOUGH. "43 documents, 116,512 present"
    is the absent-read-as-a-verdict shape one number away — it reads identically whether the
    walk found everything or found nothing to find. `occurrences` is reported beside it so an
    empty population is visible as a zero rather than as a pass.
    """
    res = {
        "documents": 0,
        "occurrences": 0,
        "vocabulary": 0,
        "present": 0,
        "missing": 0,
        "types": {},
        "kinds": {},
        "rows": 0,
    }
    res["documents"] = (
        _schema.scalar(
            con,
            "SELECT count(*) FROM core_decoded d WHERE (%s::text IS NULL OR d.core_id = %s::text)",
            (core_id, core_id),
        )
        or 0
    )
    for r in _schema.rows(
        con,
        _NODE + " SELECT jsonb_typeof(node.v) AS t, count(*) AS n FROM node GROUP BY 1",
        (core_id, core_id),
    ):
        res["types"][r["t"]] = r["n"]
    # ⚑⚑ THE PER-KIND BREAKDOWN IS A ⟡ladder-2b MEASUREMENT AND IT IS TWO NUMBERS, NOT ONE.
    # "numbers are 40% of occurrences" was known before the change; how many are DISTINCT was
    # not, and it is the interesting one — a corpus of Agda cores repeats small integers
    # heavily, so a kind can be a large share of the OCCURRENCES and a small share of the
    # VOCABULARY. Reporting only occurrences would have made the two indistinguishable, which
    # is the same collapse the sharing ratio exists to expose one level up.
    #
    # ⚑⚑ THE TOTALS ARE SUMMED FROM THE GROUPS RATHER THAN TAKEN BY A SECOND WALK, AND THE
    # LICENCE IS THAT `jsonb_typeof` **PARTITIONS** THE VALUE SPACE: every jsonb datum has
    # exactly one type, so the per-kind distinct counts are disjoint and their sum IS the global
    # distinct count. That is not true of an arbitrary grouping key — group by "first character"
    # and the sum over-counts nothing but the argument evaporates — so the property is stated
    # here rather than left as an arithmetic coincidence. Adding the breakdown as its OWN query
    # would have made the census walk the corpus a third time for a number it already had.
    # `vocab_cases` keeps the direct `count(DISTINCT occ.v)` as an ORACLE against this sum,
    # which is the right place for the expensive form: a fixture, not a 43-document sweep.
    #
    # ⚑ `AS distinct_v`: `DISTINCT` is a reserved word and cannot be a bare alias. `AS d` for the
    # existence probe, because `t` is taken by the type column.
    for r in _schema.rows(
        con,
        _NODE + _OCC + " SELECT jsonb_typeof(occ.v) AS t, count(*) AS n, "
        "count(DISTINCT occ.v) AS distinct_v, "
        "count(DISTINCT occ.v) FILTER (WHERE EXISTS "
        "(SELECT 1 FROM dec_scalar d WHERE d.v = occ.v)) AS present "
        "FROM occ GROUP BY 1",
        (core_id, core_id),
    ):
        res["kinds"][r["t"]] = (r["n"], r["distinct_v"])
        res["occurrences"] += r["n"]
        res["vocabulary"] += r["distinct_v"]
        res["present"] += r["present"]
    res["missing"] = res["vocabulary"] - res["present"]
    res.update(vocab_digest(con))
    return res


def vocab_report(res):
    """Render `vocab_census` — completeness first, then the corpus measurement.

    ⚑ THE SHARING RATIO IS THE ONLY LINE HERE THAT IS A FACT ABOUT THE CORPUS. Completeness is
    a fact about the rung and the type census is a fact about the decoder; occurrences per
    distinct value is what says something about the documents — and it is a ratio of two
    measured counts, not an extrapolation from a sample.

    ⚑ THE PER-KIND LINE CARRIES **BOTH** COUNTS FOR THE SAME REASON. A kind's share of the
    occurrences and its share of the vocabulary are different facts, and a corpus that repeats
    small integers has a large first and a small second.
    """
    print("  ⟡ladder-2b dec_scalar — %s document(s) in scope" % format(res["documents"], ","))
    print(
        "     COMPLETE  EXACT %s · MISSING %s   (every SCALAR in `dec`, keys AND values, "
        "at every depth)" % (format(res["present"], ","), format(res["missing"], ","))
    )
    print(
        "     VOCABULARY %s distinct · %s occurrence(s) · sharing %.1f× "
        "(occurrences per distinct value)"
        % (
            format(res["vocabulary"], ","),
            format(res["occurrences"], ","),
            res["occurrences"] / max(1, res["vocabulary"]),
        )
    )
    print(
        "     RELATION  %s row(s) · %s distinct id(s) · %s distinct value(s) · md5 %s"
        % (
            format(res["rows"], ","),
            format(res["ids"], ","),
            format(res["values"], ","),
            res["digest"],
        )
    )
    # ⚑⚑ THE BREAKDOWN IS BY `jsonb_typeof`, WHICH IS THE VARIANT'S OWN TAG READ BACK. It is the
    # instrument that says the exclusion is GONE rather than merely renamed: a rung that still
    # dropped numbers would print `number` here with a 0 it cannot hide.
    for k in ("string", "number", "boolean", "null"):
        if k in res["kinds"]:
            n, d = res["kinds"][k]
            print(
                "       %-8s %14s occurrence(s) · %10s distinct · %5.1f%% of occurrences"
                % (k, format(n, ","), format(d, ","), 100.0 * n / max(1, res["occurrences"]))
            )
    # ⚑ THE UNINTERNED POPULATION IS PRINTED, NOT IMPLIED — and under ⟡ladder-2b it is exactly
    # the COMPOUND values, which are not an exclusion: `node` descends into them, so the tree
    # represents them by their children rather than by a vocabulary row. A decision nobody can
    # see the size of is indistinguishable from an oversight, which is why the line stays.
    t = res["types"]
    print(
        "     NOT INTERNED (compound — `node` descends into these; the tree represents them "
        "structurally): object %s · array %s"
        % (format(t.get("object", 0), ","), format(t.get("array", 0), ","))
    )
    print(
        "     walked %s jsonb value(s): object %s · array %s · string %s · number %s · "
        "boolean %s · null %s"
        % (
            format(sum(t.values()), ","),
            format(t.get("object", 0), ","),
            format(t.get("array", 0), ","),
            format(t.get("string", 0), ","),
            format(t.get("number", 0), ","),
            format(t.get("boolean", 0), ","),
            format(t.get("null", 0), ","),
        )
    )


def _connect(sandbox):
    """The store this invocation writes — sandbox or live, resolved ONCE.

    ⚑ ONE RESOLVER, NOT PER-DISPATCH — `schema_rows._cli_connect`'s recorded defect is that a
    per-mode `sandbox_connect(...) if …` line left the READ modes silently on the live store
    while the WRITE modes honoured the flag, and a read against the wrong tenant returns
    plausible rows nobody can distinguish.
    """
    import store

    return (
        store.sandbox_connect(reset=False) if sandbox else store.connect(mode="rw", require=False)
    )


def _core_id(con, relpath):
    """The `core_id` of a STORED document, read from the store — or None for the whole table.

    ⚑⚑ READ, NOT RECOMPUTED, AND THE DIFFERENCE IS ⓟ's DEFECT. `_content_addr._addr(relpath)`
    would give the same answer today, and that is exactly what makes a second authority
    dangerous: two derivations of one id, each internally consistent, with nothing joining
    them. This rung's input IS `core_decoded`, so its scope must come from `core_decoded`.
    A relpath with no row yields None-the-document rather than None-the-whole-table, so the
    caller is told rather than silently widened — see `ingest_vocab`.
    """
    if relpath is None:
        return None, True
    cid = _schema.scalar(con, "SELECT core_id FROM core_decoded WHERE relpath = %s", (relpath,))
    return cid, cid is not None


def ingest_vocab(relpath, sandbox=False):
    """⟡ladder-2 ENTRY POINT: intern every scalar of one document — or of the whole table.

    ⚑ IT APPLIES THE `vocab` TIER AND **NOT** THE `sourced` ONE, DELIBERATELY. Creating
    `core_decoded` here would turn "you have not sourced anything yet" into a successful run
    that interned zero values — the absent-read-as-a-verdict shape. Letting postgres raise
    `UndefinedTable: relation "core_decoded" does not exist` names the missing tier and the
    step that fills it.

    ⚑⚑ THE DDL WAS APPLIED PER CALL AND THIS DOCSTRING NAMED THE HAZARD WITHOUT CLOSING IT
    (⟡ddl-is-a-write, 2026-08-24). It read: *"concurrent `CREATE TABLE … IF NOT EXISTS` can
    still collide on `pg_type`, so a fan-out owes itself one serial touch first"* — a correct
    diagnosis, discharged onto the CALLER as an owed convention. A convention a reader must
    honour is not a bound; `--vocab-concurrency` did the serial touch and nothing made the
    other callers. The precondition is now ASSERTED here and established once at build time
    (`schema.py --establish vocab --apply`), so a fan-out cannot skip it by forgetting.

    ⚑ SAME SHAPE AS `pack_core_sql` / `project_ref` / `ingest_core`: `CREATE … IF NOT EXISTS`
    takes the relation lock BEFORE it can discover the object exists, so a per-item writer that
    establishes its own tier is check-then-act at whatever concurrency the build runs at.
    """
    con = _connect(sandbox)
    _schema.require_tiers(con, ("vocab",), label="ingest_vocab")
    cid, found = _core_id(con, relpath)
    if not found:
        # ⚑ A RELPATH WITH NO ROW IS A REFUSAL, NOT A NO-OP. `cid is None` also means "the
        # whole table", so falling through would silently promote a typo'd document name into
        # a full-corpus run — the widest possible action from the narrowest possible request.
        print(
            "  --ingest-vocab: no core_decoded row for %r (the scope is the STORE, not the "
            "filesystem)" % relpath
        )
        con.close()
        return 2
    n = intern_scalars(con, cid)
    con.commit()
    con.close()
    print(
        "  dec_scalar %-9s %s new value(s) for %s"
        % ("WROTE" if n else "current", format(n, ","), relpath or "(whole table)")
    )
    return 0


def vocab_census_cli(argv, args, sandbox=False):
    """`--vocab-census [FILTER]`: completeness and the vocabulary measurement. Writes nothing.

    ⚑ AND IT NOW WRITES NOTHING (⟡ddl-is-a-write). The line above the census was
    `apply(con, only="vocab")` + `commit()` — a mode whose docstring says *"Writes nothing"*
    establishing its own tier before counting it, so it could never report on a store that
    lacked the tier: it reported on the one it had just made.
    """
    con = _connect(sandbox)
    _schema.require_tiers(con, ("vocab",), label="vocab_census")
    cid, found = _core_id(con, args[0] if args else None)
    if not found:
        print("  --vocab-census: no core_decoded row for %r" % args[0])
        con.close()
        return 2
    res = vocab_census(con, cid)
    vocab_report(res)
    con.close()
    # ⚑ AN EMPTY POPULATION IS NOT A PASS. "0 missing" over 0 occurrences is the shape this
    # arc has fixed three times; `--vocab-census` on an unsourced store must exit non-zero.
    return 0 if (res["missing"] == 0 and res["occurrences"] > 0) else 1


def coercion_collisions(con):
    """The rows a `#>> '{}'` TEXT COERCION would have MERGED — ⟡ladder-2's defect, as data.

    ⚑⚑ A MODE, BECAUSE "WAS THE VARIANT NECESSARY OR ONLY THEORETICAL?" IS A QUESTION AND THE
    STANDING RULE FORBIDS ANSWERING IT BY HAND. ⟡ladder-2 argued the exclusion from a HAZARD
    (*"the integer `0` and the string `\"0\"` … cannot be distinguished once both are text"*)
    and never measured whether the corpus exhibits it. The hazard justifies the design either
    way — a relation that depends on a corpus accident is wrong even while the accident holds —
    but *"the change is right because the collapse WOULD occur"* and *"…because it DOES occur,
    here, at these ids"* are different claims, and collapsing them is the overclaim this arc
    keeps recording. This mode is what makes the difference readable.

    ⚑ IT MODELS THE OLD COERCION EXACTLY, `v #>> '{}'`, RATHER THAN AN APPROXIMATION OF IT. Any
    group of size > 1 is a set of DISTINCT jsonb values that ⟡ladder-2's projection would have
    mapped to one text — so each group is one row the old relation would have held where the
    documents hold several, and `kinds` names which tags were merged.

    ⚑ A JSON NULL COERCES TO **SQL NULL**, NOT TO THE TEXT `'null'` — so it groups alone and can
    never appear in a collision. That is a separate consequence of the same projection and a
    sharper one: `s TEXT NOT NULL` would have REFUSED the row outright rather than merging it.
    Named here because the reader of a zero-collision report would otherwise conclude the
    coercion was harmless for nulls, when in fact it was fatal for them.
    """
    return [
        dict(text=r["t"], n=r["n"], kinds=r["kinds"], ids=r["ids"], rendered=r["rendered"])
        for r in _schema.rows(
            con,
            "SELECT v #>> '{}' AS t, count(*) AS n, "
            "string_agg(jsonb_typeof(v), '/' ORDER BY jsonb_typeof(v)) AS kinds, "
            "string_agg(id::text, ',' ORDER BY id) AS ids, "
            "string_agg(v::text, ' | ' ORDER BY jsonb_typeof(v)) AS rendered "
            "FROM dec_scalar GROUP BY 1 HAVING count(*) > 1 "
            "ORDER BY count(*) DESC, 1",
        )
    ]


def vocab_collisions_cli(argv, args, sandbox=False):
    """`--vocab-collisions`: the number-vs-string witness. Writes nothing.

    ⚑ AN EMPTY RELATION IS NOT "NO COLLISIONS" — it is nothing measured, and the two read
    identically in a report that prints only the finding. The population is printed first and
    the exit code distinguishes them, which is the `--vocab-census` precedent.
    """
    con = _connect(sandbox)
    _schema.require_tiers(con, ("vocab",), label="vocab_collisions")  # ⟡ddl-is-a-write
    rs = coercion_collisions(con)
    d = vocab_digest(con)
    con.close()
    print("  ⟡ladder-2b COERCION COLLISIONS — over %s interned value(s)" % format(d["rows"], ","))
    if not rs:
        print("     NONE. No two distinct values in this corpus share a `#>> '{}'` rendering.")
        print("     ⚑ THE EVIDENCE IS THEREFORE STRUCTURAL, NOT EMPIRICAL. The variant is still")
        print("       right — it stops the relation DEPENDING on that accident — but this run")
        print("       is not a witness that the coercion was a live defect, and saying so")
        print("       would blur two different claims.")
    else:
        print(
            "     %s group(s) — %s row(s) a TEXT vocabulary would have held as ONE"
            % (format(len(rs), ","), format(sum(r["n"] for r in rs), ","))
        )
        for r in rs[:20]:
            print(
                "       %-3d ×  %-18s  %-24s ids %s"
                % (r["n"], r["kinds"], r["rendered"][:24], r["ids"][:60])
            )
    return 0 if d["rows"] > 0 else 1


def _opt_int(argv, flag, default):
    """The integer following `flag` in `argv`, or `default`.

    ⚑ THE NEXT **FLAG** IS NOT MISTAKEN FOR N. `--vocab-concurrency --sandbox` is exactly how
    these modes are typed; `int("--sandbox")` raises, and a `try/except: 0` would run ZERO
    processes and report a clean deadlock verdict over nothing.
    """
    argv = list(argv)
    if flag not in argv:
        return default
    i = argv.index(flag)
    n = argv[i + 1] if len(argv) > i + 1 else ""
    return int(n) if n.isdigit() else default


def vocab_concurrency(filt, n, sandbox=True):
    """Run `n` `--ingest-vocab` rungs AT ONCE and report whether any `40P01` occurred.

    ⚑⚑ THIS IS THE CLAIM ⟡ladder-2 MAKES, SO IT IS A MODE RATHER THAN A SHELL FAN-OUT — the
    `source_concurrency` argument verbatim: launching N background jobs and reading N outputs
    is reasoning performed in the turn, and it evaporates when the turn ends.

    ⚑ IT REPORTS AND DOES NOT REPAIR. No retry, no backoff, no serialisation, no ordering
    imposed BETWEEN processes. Under this architecture a deadlock is a DESIGN VIOLATION and
    clearing it destroys the evidence, so a `40P01` is a finding, printed verbatim.

    ⚑ THE POPULATION IS THE STORE'S, NOT THE FILESYSTEM'S. `sppf_decode._sample` globs
    `.agdai` files because its rung reads them; this rung reads `core_decoded`, and a probe
    that launched writers at documents the store does not hold would measure contention that
    the rung cannot produce.

    ⚑ A ONE-DOCUMENT FILTER IS THE SAME-SCOPE CASE AND A WIDE FILTER IS THE DISJOINT ONE, and
    both matter for a DIFFERENT reason than in ⟡ladder-1. There the same-core run tested the
    PK and the distinct-core run tested the old batch deadlock. Here the vocabularies OVERLAP
    almost entirely whatever the scope — so disjoint documents still contend on the same
    values, which is the harder case and the one the lock order exists for.
    """
    import subprocess

    con = _connect(sandbox)
    # ⚑⚑ THIS WAS THE "ONE SERIAL TOUCH" `ingest_vocab`'s docstring CREDITED THIS MODE WITH,
    # and it is now an ASSERTION (⟡ddl-is-a-write). The old arrangement had the deadlock
    # instrument ESTABLISH the tier before fanning N processes at it — so the measurement was
    # taken against a store this mode had just written DDL to, and the serial touch was a
    # convention only this one caller honoured. Establishing once at build time makes the
    # precondition a fact rather than a courtesy, and leaves the instrument measuring only
    # what the fan-out does.
    _schema.require_tiers(con, ("vocab",), label="vocab_concurrency")
    picks = [
        r["relpath"]
        for r in _schema.rows(
            con,
            "SELECT relpath FROM core_decoded WHERE relpath LIKE %s ORDER BY relpath",
            ("%" + filt + "%",),
        )
    ]
    before = vocab_digest(con)
    con.close()
    if not picks:
        # ⚑ AN EMPTY SAMPLE IS A FACT ABOUT THE FILTER, NOT A PASS — in the instrument whose
        # whole job is to detect a rare event, "0 processes, 0 deadlocks" is worthless.
        print(
            "  ⚑ no core_decoded document matches %r — nothing was run, nothing is claimed" % filt
        )
        return 1
    # ⚑ CYCLED UP TO `n`, so N processes always start even when the filter yields fewer
    # documents. Silently running 3 for a request of 12 reports a contention level never applied.
    picks = [picks[i % len(picks)] for i in range(n)]
    tool = os.path.join(_ROOT, "scripts", "sppf_vocab.py")
    procs = [
        subprocess.Popen(
            [sys.executable, tool, "--ingest-vocab", p] + (["--sandbox"] if sandbox else []),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for p in picks
    ]
    outs = [(pr.wait(), pr.stdout.read(), pr.stderr.read()) for pr in procs]
    con = _connect(sandbox)
    after = vocab_digest(con)
    con.close()
    # ⚑ `40P01` IS THE SQLSTATE AND IS WHAT IS MATCHED, not the word "deadlock": psycopg spells
    # the exception `DeadlockDetected` and the server message is localisable; the SQLSTATE is
    # neither. Both are looked for — a match on either is a finding, a miss on both is the claim.
    dead = [
        (i, e) for i, (_rc, _o, e) in enumerate(outs) if "40P01" in e or "DeadlockDetected" in e
    ]
    # ⚑⚑ `e` AND NOT `_e`, AND THIS LINE RAISED `UnboundLocalError` THE FIRST TIME A CHILD
    # ACTUALLY FAILED (the ON-CONFLICT mutation test, 2026-08-12). The failure-reporting path
    # of a probe is the path that runs least and is needed most: it was written, read fine, and
    # was reachable only by the event the mode exists to report. Found by MUTATING the thing it
    # guards, which is the only way it could have been found.
    fail = [(i, rc, e) for i, (rc, _o, e) in enumerate(outs) if rc != 0]
    wrote = sum(1 for _rc, o, _e in outs if "WROTE" in o)
    print(
        "  ⟡ladder-2 CONCURRENCY — %d rung(s) at once over %d distinct document(s) under %r"
        % (n, len(set(picks)), filt)
    )
    print("     exit codes: %s" % ", ".join(str(rc) for rc, _o, _e in outs))
    # ⚑⚑ "THE REST" HAS TWO CAUSES AND THIS LINE DOES NOT DISTINGUISH THEM — said here rather
    # than asserted away. A process reports 0 either because its `WHERE NOT EXISTS` already saw
    # the values (it started late) or because it offered them all and `ON CONFLICT` declined
    # every one (it started level and lost the race). The second is the contended path and the
    # one this mode exists to exercise; naming only the first would be a mechanism claimed from
    # an outcome, which is the shape this arc keeps recording.
    print(
        "     processes that WROTE: %d of %d — the other %d were declined, by the anti-join "
        "or by ON CONFLICT (not distinguished)" % (wrote, n, n - wrote)
    )
    print(
        "     dec_scalar rows: %s → %s · distinct id %s → %s · distinct v %s → %s"
        % (
            format(before["rows"], ","),
            format(after["rows"], ","),
            format(before["ids"], ","),
            format(after["ids"], ","),
            format(before["values"], ","),
            format(after["values"], ","),
        )
    )
    # ⚑⚑ EXACTLY-ONCE IS `rows == distinct v`, AND IT IS THE PROPERTY THE FAN-OUT COULD BREAK.
    # A duplicate would mean two writers each landed the same value — which `UNIQUE(v)` makes
    # unrepresentable, so this reads the index's guarantee back rather than trusting it.
    print(
        "     EXACTLY-ONCE: %s (rows == distinct values == distinct ids)"
        % ("YES" if after["rows"] == after["values"] == after["ids"] else "**NO**")
    )
    if dead:
        print("     ⚑⚑ 40P01 DEADLOCK — %d of %d process(es). VERBATIM:" % (len(dead), n))
        for i, e in dead[:2]:
            print("        [proc %d] %s" % (i, e.strip()[:1200]))
    else:
        print("     40P01 DEADLOCK: NONE observed in %d concurrent rung(s)" % n)
    for i, rc, e in fail:
        if (i, e) not in dead:
            print("     ⚑ process %d exited %d — %s" % (i, rc, e.strip().splitlines()[-1:]))
    # ⚑ `not (a == b == c)` AND NOT `a != b != c` — the second is a CHAINED comparison
    # (`a != b and b != c`), which is true for `(5, 4, 5)` and false for `(5, 4, 4)`: it would
    # have reported a broken relation as clean. Found in the same pass as the `_e` bug above,
    # in the same three lines, and for the same reason — nothing had ever made this path run.
    return 1 if (dead or fail or not (after["rows"] == after["values"] == after["ids"])) else 0


#: The ⟡ladder-2 modes `vocab_cli` owns. ⚑ ONE PLACE, so the dispatch and the mode set cannot
# disagree — a mode branched on but not declared here simply never fires, and `vocab_cases`
# asserts the two agree on the AST rather than on the prose that names every flag.
VOCAB_MODES = {
    "--ingest-vocab",
    "--vocab-census",
    "--vocab-concurrency",
    "--vocab-sql",
    "--vocab-collisions",
}


def vocab_cli(argv, args):
    """The ⟡ladder-2 CLI — one entry point for the VOCAB tier's five modes."""
    argv = list(argv)
    sandbox = "--sandbox" in argv
    if "--vocab-sql" in argv:
        # ⚑⚑ A MODE, BECAUSE "WHAT STATEMENT DOES THE RUNG ISSUE?" IS A QUESTION AND ANSWERING
        # IT BY HAND IS THE THING THE STANDING RULE FORBIDS. ⟡ladder-1 answered it by pasting
        # the statement into a plan file, where it is a COPY that ages: the plan's text and the
        # emitted SQL are then two authorities with nothing checking them. This prints exactly
        # what `intern_scalars` sends, so a reader — or a report — quotes the statement rather
        # than a transcription of it. It touches no store and writes nothing.
        _sql, _p = intern_scalars_sql(args[0] if args else None)
        print(_sql)
        print("-- parameters: %r  (NULL scope = every document)" % (_p,))
        return 0
    if "--ingest-vocab" in argv:
        i = argv.index("--ingest-vocab")
        nxt = argv[i + 1] if len(argv) > i + 1 else None
        # ⚑ A FLAG IS NOT A RELPATH. `--ingest-vocab --sandbox` must mean "the whole table, in
        # the sandbox", not "the document named --sandbox"; the bare `--` prefix test is the
        # `source_cli` precedent and is not itself a mode.
        return ingest_vocab(None if (nxt is None or nxt.startswith("--")) else nxt, sandbox)
    if "--vocab-concurrency" in argv:
        return vocab_concurrency(
            args[0] if args else "", _opt_int(argv, "--vocab-concurrency", 8), sandbox=sandbox
        )
    if "--vocab-collisions" in argv:
        return vocab_collisions_cli(argv, args, sandbox)
    return vocab_census_cli(argv, args, sandbox)


def vocab_cases(check):
    """The ⟡ladder-2 guarded cases, driven from `sppf_db._selftest`.

    ⚑ THE CASES LIVE BESIDE THE CODE AND THE SUITE STAYS WHERE IT WAS — `source_row_cases`'s
    precedent: `run_selftests.discover()` counts a suite as the PAIR of a `_selftest` def and a
    dispatch on the selftest flag, so defining neither here adds no suite and the total stays
    69. (The flag is not spelled out anywhere in this file — see the module docstring for the
    phantom suite that one mention produced.)

    ⚑⚑ THE FIXTURE IS HANDWRITTEN AND ADVERSARIAL, NOT A REAL CORE, AND THAT IS THE POINT. A
    real `.agdai` cannot exhibit "this string appears ONLY as a key", "this one ONLY as a
    value" and "this one as BOTH" on demand — which is exactly the property "one vocabulary,
    not two" is a claim about. The real corpus is what `--vocab-census` measures; a fixture is
    what a claim is TESTED against.

    ⚑⚑ AND ⟡ladder-2b ADDS THE OTHER HALF, WHICH THE OLD FIXTURE STRUCTURALLY COULD NOT HOLD:
    the same TEXT occurring as a number AND as a string, as a boolean AND as a string, as a
    JSON null AND as a string. Those pairs are the ONLY thing that can fail "no manufactured
    identity", and a corpus is not guaranteed to contain them — `--vocab-collisions` says
    whether the real one does, and this fixture says the relation is right EITHER WAY.
    """
    con = _schema.sandbox_fixture("sppf_vocab")
    import json as _json

    # keyonly: appears only as an object key.  valonly: only as a string value.
    # both:    appears as a key at depth 1 AND as a value at depth 5, inside arrays.
    # ⚑ THE COLLISION TRIPLES ARE DELIBERATE: 7/"7", True/"true", None/"null". Each pair is two
    # DISTINCT jsonb values whose `#>> '{}'` renderings are equal — the exact collapse the old
    # text column could not represent and the new variant must.
    doc = {
        "keyonly": 7,
        "both": "valonly",
        "deep": [[{"lvl": [{"z": "both"}]}]],
        "n": 42,
        "t": True,
        "f": False,
        "nul": None,
        "empty": "",
        "sevenstr": "7",
        "truestr": "true",
        "nullstr": "null",
        "again": 7,
    }
    _schema.execute(
        con,
        "INSERT INTO core_decoded (core_id, relpath, mtime, dec) "
        "VALUES ('c1', 'fixture/one.agdai', 1, %s)",
        (_json.dumps(doc),),
    )
    con.commit()

    _pre = _schema.scalar(con, "SELECT count(*) FROM dec_scalar")
    # ⚑⚑ THE FIRST RUNG CALL IS GUARDED SO A REFUSAL NAMES ITSELF INSTEAD OF TAKING THE SUITE
    # DOWN — the repair ⟡ladder-1 already made once, re-earned here by MUTATION. Dropping
    # `UNIQUE` from `ix_decscalar_v` makes postgres refuse the statement (`there is no unique
    # or exclusion constraint matching the ON CONFLICT specification`), and unguarded that
    # raised out of `vocab_cases` into `_selftest`, losing 115 cases to report one. A traceback
    # out of a case function fails EVERYTHING, which is indistinguishable from an unrelated
    # collapse; a named case fails ONE line and says which invariant went.
    try:
        n1 = intern_scalars(con)
        con.commit()
    except Exception as _rung_err:  # noqa: BLE001 — naming IS the job
        con.rollback()
        check("the rung RUNS at all — its conflict arbiter exists", str(_rung_err), "")
        con.close()
        return
    # ⚑ THE POPULATION GUARD COMES FIRST. Every case below is satisfied by an empty table, so
    # without this line the whole block is the absent-read-as-a-verdict shape.
    check("the rung interns a non-empty vocabulary from an empty table", (_pre, n1 > 0), (0, True))

    def _has(v):
        """Rows equal to the jsonb datum `v` denotes — `_json.dumps` supplies the TAG.

        ⚑ THE PARAMETER IS A JSON DOCUMENT, NOT A STRING, WHICH IS WHY THE COLLISION CASES CAN
        BE WRITTEN AT ALL. `_has(7)` asks for `'7'::jsonb` and `_has("7")` for `'\"7\"'::jsonb`;
        under ⟡ladder-2's `WHERE s = %s` both were the text `7` and no case could tell them
        apart — the suite could not have EXPRESSED the defect it was meant to prevent.
        """
        return _schema.scalar(
            con, "SELECT count(*) FROM dec_scalar WHERE v = %s::jsonb", (_json.dumps(v),)
        )

    # ── STEP 2 (keys) and STEP 3 (values) are ONE vocabulary ─────────────────────────────
    check("a string reached ONLY as an object KEY is interned", _has("keyonly"), 1)
    check("a string reached ONLY as a scalar VALUE is interned", _has("valonly"), 1)
    # ⚑⚑ THE CENTRAL CLAIM: ONE ROW, NOT TWO. `both` occurs as a key at depth 1 and as a value
    # at depth 5. A table that partitioned the id space by position, or carried a `kind`
    # column, would hold two rows here and every case above would still pass.
    check("...and a string reached as BOTH is ONE row, because it is one value", _has("both"), 1)
    check("the empty string is a value and is interned", _has(""), 1)

    # ── the enumeration is RECURSIVE — values live at every depth ────────────────────────
    check("a KEY at depth 5, inside two arrays and two objects, is reached", _has("z"), 1)
    check("...and so is the key of the object that contains it", _has("lvl"), 1)

    # ── ⟡ladder-2b: EVERY SCALAR KIND IS INTERNED, WITH ITS TAG ──────────────────────────
    # ⚑⚑ ASSERTED AS THE PRESENCE OF THE **TAGGED** FORM. Under ⟡ladder-2 these were asserted
    # as ABSENCES of the rendered text (`_has("42") == 0`), which is what a silent coercion
    # would have produced — the right guard for a relation that excluded them, and exactly the
    # guard that had to invert when the exclusion became a tag.
    check("an integer VALUE is interned, as a NUMBER", _has(42), 1)
    check("...and so are both booleans", (_has(True), _has(False)), (1, 1))
    # ⚑ A JSON NULL IS A VALUE AND `v JSONB NOT NULL` ADMITS IT — `'null'::jsonb IS NULL` is
    # False (measured). A rung that dropped it would leave this at 0 and nothing else would move.
    check("...and a JSON null, which is a VALUE and not the absence of one", _has(None), 1)
    check(
        "...while the KEYS naming them are interned too, because a key is a value",
        (_has("n"), _has("t"), _has("nul")),
        (1, 1, 1),
    )

    # ── NO MANUFACTURED IDENTITY: the number `0` and the string `"0"` are TWO rows ────────
    # ⚑⚑ THIS IS THE PROPERTY THE VARIANT EXISTS FOR, AND IT IS THE ONE A TEXT COLUMN CANNOT
    # HOLD. Each pair below renders identically under `#>> '{}'` — `7`/`"7"`, `true`/`"true"`,
    # `null`/`"null"` — so ⟡ladder-2's projection would have merged each pair into one row (or,
    # for the null, refused it against NOT NULL). The tag is what keeps them apart, and
    # `jsonb_typeof` is that tag read back rather than inferred from the id.
    def _kind(v):
        return _schema.scalar(
            con, "SELECT jsonb_typeof(v) FROM dec_scalar WHERE v = %s::jsonb", (_json.dumps(v),)
        )

    check(
        'the number 7 and the string "7" are TWO rows, distinctly tagged',
        (_has(7), _has("7"), _kind(7), _kind("7")),
        (1, 1, "number", "string"),
    )
    check(
        '...and so are the boolean true and the string "true"',
        (_has(True), _has("true"), _kind(True), _kind("true")),
        (1, 1, "boolean", "string"),
    )
    check(
        '...and the JSON null and the string "null"',
        (_has(None), _has("null"), _kind(None), _kind("null")),
        (1, 1, "null", "string"),
    )
    # ⚑ AND THE COERCION IS SHOWN TO BE THE COLLAPSE, not merely asserted to be: the mode that
    # measures it on the corpus is run here against a fixture ENGINEERED to contain it, so a
    # zero on the real store is readable as a fact about the corpus rather than a broken probe.
    _coll = {c["kinds"] for c in coercion_collisions(con)}
    check(
        "`--vocab-collisions` SEES the pairs a text coercion would have merged",
        sorted(_coll),
        ["boolean/string", "number/string"],
    )
    # ⚑⚑ AND THE JSON NULL IS **NOT** ONE OF THEM, WHICH IS A SHARPER FAILURE AND NOT A MILDER
    # ONE — MEASURED, and it is why the null does not appear in the list above. `#>> '{}'` maps
    # a JSON null to **SQL NULL**, not to the text `'null'`: so ⟡ladder-2's column, had it been
    # widened by coercion instead of by tagging, would have REFUSED the row against `NOT NULL`
    # rather than merging it. A reader who saw only the two collision groups would conclude the
    # coercion was harmless for nulls; it was fatal for them.
    check(
        "...and a JSON null coerces to SQL NULL — refused by NOT NULL, not merged",
        (
            _schema.scalar(con, "SELECT v #>> '{}' FROM dec_scalar WHERE v = 'null'::jsonb"),
            _has(None),
            _has("null"),
        ),
        (None, 1, 1),
    )
    # ⚑ THE SAME NUMBER REACHED TWICE (`keyonly: 7`, `again: 7`) IS STILL ONE ROW — the sharing
    # property, on the kind that the old rung could not intern at all.
    check("...while one number reached from two places is ONE row", _has(7), 1)

    # ── IDEMPOTENCE: 0 rows AND the relation byte-identical ─────────────────────────────
    _d1 = vocab_digest(con)
    n2 = intern_scalars(con)
    con.commit()
    _d2 = vocab_digest(con)
    check("a second run of the rung writes NOTHING", n2, 0)
    # ⚑ THE DIGEST IS THE HALF A ROWCOUNT CANNOT SEE. A rung that deleted and rewrote every row
    # identically also reports 0 on the run after; only the id assignment would betray it.
    check(
        "...and leaves the relation byte-identical (same ids, same order)",
        _d1["digest"] == _d2["digest"] and _d1["digest"] is not None,
        True,
    )
    # ⚑⚑ AND THE ANTI-JOIN IS WHAT THIS ASSERTS, BECAUSE NOTHING ELSE CAN. Deleting
    # `WHERE NOT EXISTS` leaves the rowcount at 0 and the digest unchanged — `ON CONFLICT DO
    # NOTHING` absorbs every row — so both cases above pass against a rung that offers the
    # whole vocabulary to the index on every run. What DOES change is the SEQUENCE: postgres
    # evaluates the identity default BEFORE detecting the conflict, so a declined row still
    # consumes a number.
    #
    # ⚑⚑ AND MY FIRST SPELLING OF THIS GUARD READ `max(id)`, WHICH CANNOT SEE IT — caught by
    # running the mutation, not by reading the code. A burned value leaves a GAP; `max(id)`
    # moves only when a row actually lands, so the case passed against the defeated anti-join
    # and measured nothing. MEASURED on the live sandbox: offering all 116,512 existing strings
    # back to the rung moved `last_value` 116,589 → 233,101 (+116,512, exactly one per offered
    # row) while `max(id)` and `count(*)` did not move at all.
    #
    # ⚑ `pg_sequence_last_value(pg_get_serial_sequence(…))` AND NOT THE SEQUENCE BY NAME: the
    # suite fixture lives in a private schema, so a hardcoded `dec_scalar_id_seq` would resolve
    # against whichever tenant happened to be on the search_path.
    _seq = "SELECT pg_sequence_last_value(pg_get_serial_sequence('dec_scalar','id'))"
    _before = _schema.scalar(con, _seq)
    intern_scalars(con)
    con.commit()
    check(
        "...and consumes no identity value, so the anti-join really ran",
        (_schema.scalar(con, _seq), _before is not None),
        (_before, True),
    )

    # ── COMPLETENESS, DRIVEN FROM `dec` ITSELF ──────────────────────────────────────────
    _c = vocab_census(con)
    check(
        "completeness is driven from `dec` and reports MISSING 0",
        (_c["missing"], _c["vocabulary"] > 0),
        (0, True),
    )
    check(
        "...over a population the census can actually see",
        (_c["documents"], _c["occurrences"] > _c["vocabulary"]),
        (1, True),
    )
    # ⚑⚑ THE PER-KIND BREAKDOWN IS WHAT MAKES THE EXCLUSION'S ABSENCE OBSERVABLE. A rung that
    # still dropped numbers would leave `number` out of this dict entirely, and every
    # completeness case above would pass — because the census derives its expectation from the
    # SAME `occ` the rung uses, so a filter narrowing both stays invisible to `missing`.
    check(
        "the census breaks the vocabulary down by jsonb_typeof — all four scalar kinds",
        sorted(_c["kinds"]),
        ["boolean", "null", "number", "string"],
    )
    # ⚑⚑ THE ORACLE FOR THE SUMMED TOTALS. `vocab_census` derives `occurrences`/`vocabulary`/
    # `present` by SUMMING its per-kind groups, on the licence that `jsonb_typeof` partitions
    # the value space. That licence is an ARGUMENT, and an argument in a comment is what this
    # tree keeps paying for — so the direct `count(DISTINCT occ.v)` over the ungrouped `occ` is
    # computed here, against a fixture where a whole-corpus walk costs nothing, and the two are
    # required to agree. A grouping key that did NOT partition would fail this and nothing else.
    for _o in _schema.rows(
        con,
        _NODE + _OCC + " SELECT count(*) AS occurrences, "
        "count(DISTINCT occ.v) AS vocabulary "
        "FROM occ",
        (None, None),
    ):
        check(
            "...and its summed totals agree with a direct ungrouped count(DISTINCT)",
            (_c["occurrences"], _c["vocabulary"]),
            (_o["occurrences"], _o["vocabulary"]),
        )
    # ⚑ AND THE COMPOUND KINDS ARE IN `types` AND **NOT** IN `kinds`, which is the boundary
    # between "interned" and "represented structurally" read off two dicts rather than asserted.
    check(
        "...while object and array are walked and NOT interned",
        (
            _c["types"].get("object", 0) > 0,
            _c["types"].get("array", 0) > 0,
            "object" in _c["kinds"],
            "array" in _c["kinds"],
        ),
        (True, True, False, False),
    )
    # ⚑ THE CENSUS MUST BE ABLE TO SAY "MISSING". A completeness instrument that reports 0
    # missing unconditionally is the `reflects_obs` defect — so it is shown FAILING, with the
    # store's own row deleted rather than with a mutated comparator.
    _schema.execute(con, "DELETE FROM dec_scalar WHERE v = '\"both\"'::jsonb")
    con.commit()
    check(
        "...and REPORTS a gap when one exists, rather than reading 0 either way",
        vocab_census(con)["missing"],
        1,
    )
    check(
        "...which the rung then closes", (intern_scalars(con), vocab_census(con)["missing"]), (1, 0)
    )
    con.commit()

    # ── the id is ENGINE-ASSIGNED — `GENERATED ALWAYS`, enforced by postgres ────────────
    # ⚑⚑ BEHAVIOURAL, NOT A DDL SCAN. `schema_selftest` already pins the emitted keyword; this
    # asks the ENGINE, because the ⑸ defect was a client that supplied an id and was ALLOWED to.
    _refused = None
    try:
        _schema.execute(con, "INSERT INTO dec_scalar (id, v) VALUES (999999, '\"client-minted\"')")
        con.commit()
        _refused = False
    except Exception as e:  # noqa: BLE001 — the class is the point
        con.rollback()
        _refused = "identity" in str(e).lower() or "GENERATED" in str(e)
    check("a CLIENT-supplied id is REFUSED by the engine, not merely discouraged", _refused, True)
    # ⚑ AND `UNIQUE(v)` IS THE INTERNING KEY, ASSERTED THE SAME WAY. Without it the rung's
    # `ON CONFLICT (v)` has no arbiter to name and two writers can each land the same value.
    _dup = None
    try:
        _schema.execute(con, "INSERT INTO dec_scalar (v) VALUES ('\"both\"')")
        con.commit()
        _dup = False
    except Exception:  # noqa: BLE001
        con.rollback()
        _dup = True
    check("a duplicate value is REFUSED by ix_decscalar_v", _dup, True)
    # ⚑⚑ AND THE INDEX REFUSES ON **jsonb** EQUALITY, WHICH IS NOT TEXT EQUALITY — the property
    # that makes the whole correction expressible, asserted where it is enforced. `'7'::jsonb`
    # is a DIFFERENT key from `'\"7\"'::jsonb` even though both render `7`, so the unique index
    # must ACCEPT this insert-and-rollback pair where a `text` index would have refused one.
    _distinct_ok = None
    try:
        _schema.execute(con, "INSERT INTO dec_scalar (v) VALUES ('7.5'), ('\"7.5\"')")
        con.commit()
        _distinct_ok = True
    except Exception:  # noqa: BLE001
        con.rollback()
        _distinct_ok = False
    check(
        "...while a number and its string rendering are DIFFERENT keys, both admitted",
        (_distinct_ok, _has(7.5), _has("7.5")),
        (True, 1, 1),
    )
    _d3 = vocab_digest(con)
    check(
        "so the map is a bijection: rows == distinct ids == distinct values",
        (_d3["rows"] == _d3["ids"] == _d3["values"], _d3["rows"] > 0),
        (True, True),
    )

    # ── the rung is SCOPED, and a second document extends the SAME vocabulary ───────────
    _schema.execute(
        con,
        "INSERT INTO core_decoded (core_id, relpath, mtime, dec) "
        "VALUES ('c2', 'fixture/two.agdai', 1, %s)",
        (_json.dumps({"both": "fresh", "keyonly": 1}),),
    )
    con.commit()
    _n3 = intern_scalars(con, "c2")
    con.commit()
    # ⚑ TWO new values — the string `'fresh'` and the NUMBER `1` — while the keys `'both'` and
    # `'keyonly'` are already interned FROM THE OTHER DOCUMENT, which is what "one vocabulary"
    # means across documents rather than merely within one.
    #
    # ⚑⚑ THE COUNT MOVED 1 → 2 UNDER ⟡ladder-2b AND THAT IS THE MEASUREMENT, NOT A FIXTURE
    # ADJUSTMENT. `keyonly: 1` was in this document all along and `c1` holds no `1`, so the
    # number was always new and always uncounted: ⟡ladder-2 simply could not see it. The
    # cross-document sharing case was, until now, silently testing only half the vocabulary.
    check("a scoped rung interns only what is new, across documents", _n3, 2)
    check(
        "...and the shared values still hold exactly one row each",
        (_has("both"), _has("keyonly")),
        (1, 1),
    )
    check("a scope naming no document interns nothing", intern_scalars(con, "no-such-core"), 0)
    # ⚑⚑ AND A RELPATH WITH NO ROW IS A REFUSAL, NOT A WIDENING. `None` is the scope's spelling
    # of "the whole table", so a `_core_id` that returned it for an unknown document would turn
    # the narrowest possible request into the widest possible action — silently. The `found`
    # flag is what keeps those two Nones apart, and this is the case that says so.
    check(
        "a relpath the store does not hold is REFUSED, never widened to the whole table",
        (_core_id(con, "fixture/one.agdai")[1], _core_id(con, "nope.agdai"), _core_id(con, None)),
        (True, (None, False), (None, True)),
    )

    # ── the compiled SQL: properties a COMMENT cannot fake ──────────────────────────────
    _sql, _params = intern_scalars_sql("c1")
    # ⚑⚑ NO `--` AT ALL. `_insert_row_sql`'s residue records the measured forgery: a guard
    # anchored on compiled SQL was satisfied by an SQL COMMENT naming what it guarded, and the
    # suite read green. SQL has comments too, so the emitted statement may carry none.
    check("the emitted statement carries no SQL comment", "--" in _sql, False)
    check("...and is ONE statement, so the rung cannot become a script", _sql.count(";"), 0)
    check(
        "...parameterised by scope, never interpolated",
        (_params, "c1" in _sql),
        (("c1", "c1"), False),
    )
    # ⚑ THE LOCK ORDER IS PINNED BECAUSE IT IS THE ONLY CONCURRENCY PROPERTY THE STATEMENT
    # ITSELF CARRIES; `--vocab-concurrency` is what actually exercises it.
    check(
        "...and orders its inserts by a locale-independent total order",
        'ORDER BY vocab.v::text COLLATE "C"' in _sql,
        True,
    )
    # ⚑⚑ AND THE VALUE BRANCH DOES NOT PROJECT — THE COERCION IS ABSENT FROM THE STATEMENT, not
    # merely absent from the result. `#>> '{}'` appearing anywhere in the rung is ⟡ladder-2's
    # defect restored, and it is the one property of this change a behavioural case cannot
    # localise: a rung that coerced and then re-tagged would produce a plausible table.
    check(
        "...and the emitted rung contains NO text coercion of a walked value", "#>>" in _sql, False
    )
    # ⚑ THE KEY BRANCH LANDS IN jsonb, ASSERTED ON THE STATEMENT because it is what makes a key
    # and a string value ONE row. `k.s` unwrapped would be a type error, not a silent defect —
    # but `k.s::jsonb` would PARSE the key and is exactly the plausible-looking wrong spelling.
    check(
        "...and lifts object keys with to_jsonb, never a ::jsonb PARSE",
        ("to_jsonb(k.s)" in _sql, "k.s::jsonb" in _sql),
        (True, False),
    )

    # ── the dispatch: a mode that never fires is the silent-skip defect one layer up ────
    import ast as _ast
    import inspect as _inspect
    import re as _re

    # ⚑⚑ THE POPULATION IS "STRINGS SHAPED LIKE A FLAG", NOT "STRINGS STARTING WITH `--`" —
    # narrowed by MEASUREMENT, after `--vocab-sql` landed and this case failed naming
    # `'-- parameters: %r  (NULL scope = every document)'`. That literal is an SQL COMMENT
    # prefix in a print, not a flag. `source_row_cases` hit the same edge and excluded the bare
    # `"--"` BY NAME; a name-list is the frozen roster this repo keeps paying for, so the
    # narrowing here is by SHAPE and admits no exceptions to maintain.
    _flag = _re.compile(r"^--[a-z0-9]+(-[a-z0-9]+)*$")
    _branched = {
        n.value
        for n in _ast.walk(_ast.parse(_inspect.getsource(vocab_cli)))
        if isinstance(n, _ast.Constant) and isinstance(n.value, str) and _flag.match(n.value)
    }
    check(
        "every flag `vocab_cli` branches on is a declared VOCAB_MODE",
        sorted(_branched - {"--sandbox"} - VOCAB_MODES),
        [],
    )
    check(
        "...and VOCAB_MODES declares nothing `vocab_cli` cannot serve",
        sorted(VOCAB_MODES - _branched - {"--vocab-census"}),
        [],
    )
    check(
        "`--vocab-concurrency N` is parsed beside the mode",
        (
            _opt_int(["--vocab-concurrency", "12"], "--vocab-concurrency", 8),
            _opt_int(["--vocab-concurrency", "--sandbox"], "--vocab-concurrency", 8),
        ),
        (12, 8),
    )
    con.close()


if __name__ == "__main__":
    _argv = sys.argv
    _args = [a for a in _argv[1:] if not a.startswith("--")]
    if not (VOCAB_MODES & set(_argv)):
        # ⚑ A BARE RUN DESCRIBES AND DOES NOT WRITE — `sppf_db`'s worst recorded defect is a
        # bare run that defaulted to a subtree and opened a write transaction against the live
        # store. Refusing here costs a reader one flag and costs a mistake nothing.
        print(__doc__.strip().splitlines()[0])
        print(
            "\n⚑ NO MODE GIVEN — refusing. A tool that writes when asked to describe "
            "itself is the defect.\n"
        )
        print("modes:")
        print("  --ingest-vocab [RELPATH]   THE RUNG — every SCALAR in `dec` (object KEYS and")
        print("                             scalar VALUES alike) into dec_scalar, by ONE")
        print("                             statement. No RELPATH = every document.")
        print("  [FILTER] --vocab-census    completeness EXACT/MISSING driven from `dec` itself")
        print("                             at every depth + the vocabulary-size measurement")
        print("                             and the per-kind (jsonb_typeof) breakdown")
        print("  [FILTER] --vocab-concurrency [N]")
        print("                             run N rungs AT ONCE over FILTER's documents and")
        print("                             report whether any 40P01 (deadlock) occurred")
        print("  --vocab-collisions         the DISTINCT values a `#>> {}` text coercion would")
        print("                             have MERGED — the witness that the VARIANT was")
        print("                             necessary rather than theoretical. Reports an")
        print("                             empty result as structural-not-empirical evidence")
        print("  [RELPATH] --vocab-sql      print the rung VERBATIM — the statement the engine")
        print("                             is sent, not a transcription of it. Touches nothing")
        print("      [--sandbox]            every mode: the THROWAWAY tenant, never the corpus")
        sys.exit(2)
    sys.exit(vocab_cli(_argv, _args))
