# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""dec_tree.py — ⟡ladder-4: `core_decoded.dec` as a CNF-2 binary tree. THE STATEMENTS, ONLY.

⚑⚑ THIS MODULE IS DATA AND ACCESSORS AND NOTHING ELSE — no CLI, no `__main__`, no fixpoint
loop, no branch. That is a MEASURED shape, not an aspiration: `pycodemod --control` counts
every `if`, `for`, ternary, `try`, comprehension guard and `or`-default in a module, and
`jea/metalanguage/query_sql_postgres.py` (72 code lines, a pure data module with no CLI)
is the only file in this toolkit that scores **0**. The FIXPOINT — "run the rung for
`rnd = 0, 1, 2, …` until the frontier is empty" — is a mode-branch and therefore belongs to
the CALLER (`scripts/sppf_tree.py`), which is where it lives.

⚑ THE RUNG IS ONE STATEMENT PER ROUND, AND THE ROUND COUNT IS NOT A DEFECT TO ENGINEER
AWAY. Cell k of a spine needs cell k+1's id, so a sequence of length N is N sequential
rounds; N is **115,268** for the largest document in this corpus, and that is ACCEPTED
(user, 2026-08-13: *"When in doubt, favor sharing. I'd rather spend a bit more in compute
up front than have sharing locked up somewhere I can't see."*).

⚑⚑ THE REASON IS LEGIBILITY, NOT VOLUME, AND IT IS THE PART A LATER READER WILL BE TEMPTED
TO RE-OPEN. Balanced bracketing would cut the rounds to ⌈log₂ 115268⌉ = 17 and it shares
INCIDENTALLY: whether two sequences share a common tail depends on where the bracketing
falls, which depends on total length, so sharing appears and disappears for reasons
invisible in the data. A right spine shares STRUCTURALLY — equal tails share, always,
inspectably. The round count is what that costs.

⚑⚑ AND THE ROUNDS ARE **BULK**, WHICH IS THE THING THAT MAKES THE COST LINEAR. Round `r`
resolves the `r`-th node-level of EVERY document at once; only documents deep enough
contribute, so the frontier SHRINKS. Total work is Σ nodes; the round COUNT is the longest
spine. The prohibitive mistake is re-walking `dec` each round — O(values × rounds) =
O(4.1M × 115,268) — which the five narrow documents hide and the corpus does not. The
skeleton (`dec_stage`) is materialised ONCE and `ix_decstage_rnd` is what makes round `r`
read only its own slice.

The alphabet, its bounded key, and why `CONS` is absent: see `schema_decl.dec_node`.
"""

#: The four productions. ⚑ A CONSTRUCT TAG, NEVER A `dec_scalar` id — interning the word
# `"OBJ"` would manufacture vocabulary no document contains (⟡ladder-2b's defect, inverted).
HEAD_LEAF = 0
HEAD_OBJ = 1
HEAD_ARR = 2
HEAD_MEMBER = 3

#: The nullary child. ⚑ A VALUE, NOT A NULL, so it is PK-legal: identity starts at 1, so no
# node is ever numbered 0 and the spelling cannot be mistaken for a real reference.
NIL = 0

#: Address `kind`s inside `dec_stage`/`dec_ref`. 0 = a spine cell (or, at `ord` 0, an EMPTY
# compound), 1 = a MEMBER, 2 = a LEAF.
KIND_CELL = 0
KIND_MEMBER = 1
KIND_LEAF = 2

# ── (1) THE WALK — every value in the selected document(s), carrying its PATH ────────────────
#
# ⚑⚑ THE RECURSIVE TERM MAY NAME THE CTE EXACTLY ONCE — measured by ⟡ladder-2 and re-earned
# here. The obvious spelling, one `UNION ALL` branch descending into objects and a second into
# arrays, is a PARSE ERROR (*"recursive reference to query `w` must not appear more than
# once"*); folding both into ONE `CROSS JOIN LATERAL (… UNION ALL …)` makes it a single
# FROM-entry reference. Anyone "simplifying" this back into two branches will get the error.
#
# ⚑ THE PATH IS CARRIED AND ⟡ladder-2's WALK DOES NOT CARRY IT, which is the whole difference
# between a VOCABULARY rung and a TREE rung. A vocabulary needs only the value; a tree needs to
# know WHICH position a value occupies, because the node above it is addressed by that
# position. `jsonb_path_query(dec, 'strict $.**')` remains unusable for the same reason it was
# then — it cannot see a key.
#
# ⚑ AN ARRAY ELEMENT'S PATH SEGMENT IS `(ord-1)::text` — the 0-based index — so it cannot
# collide with an object key at the same path unless the document holds both an array and an
# object at one location, which is impossible: a value has one type.
#
# ⚑⚑ THE PATH IS **TEXT**, NOT `text[]`, AND THAT IS A MEASURED COST FINDING RATHER THAN A
# STYLE CHOICE. The array spelling is the obvious one and it is the one I shipped first; the
# corpus build then ran 8+ minutes without emitting a row. `EXPLAIN` named the cause:
# **postgres has no hash operator class for `text[]`**, so `ON cc.path = it.cpath` cannot be a
# Hash Join — it plans a **Merge Left Join**, which must SORT both sides, i.e. sort 4.1M path
# arrays with array-comparison as the sort operator. `text` hashes, so the identical join
# becomes a hash join over a scalar. Verified with `EXPLAIN (COSTS OFF)` on a 100k×100k
# `text[]` self-join before the change, which planned `Merge Left Join / Sort / Sort`.
#
# ⚑ THE ENCODING IS LENGTH-PREFIXED SO IT IS INJECTIVE FOR **ANY** KEY. `path || len(k) || ':'
# || k` is uniquely parseable — read digits to the colon, then take exactly that many
# characters — so no separator can be forged by a key containing it. A bare `path || '/' || k`
# would collide (`{"a/b": …}` versus `{"a": {"b": …}}`), which is precisely the class of bug
# that survives every small fixture and appears once on a real document.
#
# ⚑ AND THE ROOT IS `''`, WHICH STILL SORTS FIRST — `comp`'s `row_number()` therefore gives the
# root compound `sid = 1` under the text ordering exactly as it did under the array ordering,
# so `roots_sql` is unaffected by the change.
#
# ⚑⚑ THE SCOPE IS A **CONCRETE** `core_id`, NOT THE `(%s IS NULL OR core_id = %s)` FORM EVERY
# OTHER QUERY HERE USES, AND THE DIFFERENCE IS 55 SECONDS PER DOCUMENT. That form is right for a
# cheap indexed read and wrong for the head of a walk the whole statement's cardinality flows
# from: postgres cannot estimate a disjunction over an unbound parameter, so it assumed the
# corpus, and assuming the corpus makes it HASH JOIN `dec_scalar` — building a 231,783-row hash
# table twice, for every document, to serve a median 48,987 probes. With a concrete equality the
# estimate is one `core_decoded` row and the same joins plan as index lookups.
#
# ⚑ SO THE WHOLE-TABLE SCOPE IS THE CALLER'S JOB HERE, not a parameter value. `build_skeleton`
# iterates the documents and maxes their limits; `rounds`/`census`/`roots` keep the nullable
# form because they read INDEXED relations where the estimate does not decide the plan.
_WALK = """\
WITH RECURSIVE w(core_id, path, depth, v) AS (
        SELECT d.core_id, '', 0, d.dec
          FROM core_decoded d
         WHERE d.core_id = %s::text
    UNION ALL
        SELECT w.core_id, w.path || length(c.k)::text || ':' || c.k, w.depth + 1, c.child
          FROM w
          CROSS JOIN LATERAL (
                  SELECT e.key, e.value
                    FROM jsonb_each(w.v) AS e
                   WHERE jsonb_typeof(w.v) = 'object'
              UNION ALL
                  SELECT (a.ord - 1)::text, a.value
                    FROM jsonb_array_elements(w.v) WITH ORDINALITY AS a(value, ord)
                   WHERE jsonb_typeof(w.v) = 'array'
          ) AS c(k, child)
)"""

# ── (2) THE COMPOUNDS — every object and array, with a document-local serial ─────────────────
#
# ⚑ `sid` IS DOCUMENT-LOCAL AND DELIBERATELY SO. It addresses a position in ONE document's
# work list; it is never a node identity and never leaves `dec_stage`/`dec_ref`. Content
# identity lives in `dec_node` and nowhere else — that split is what lets the staging be
# path-addressed without costing the tier its sharing.
#
# ⚑ `n` IS THE ITEM COUNT AND IS TAKEN FROM THE VALUE, not from a count of the rows the next
# CTE happens to produce. A count derived from the enumeration would agree with the
# enumeration by construction and could not detect it dropping an item.
_COMP = """,
comp AS (
    SELECT w.core_id, w.path, w.depth, w.v,
           row_number() OVER (PARTITION BY w.core_id ORDER BY w.path) AS sid,
           (CASE jsonb_typeof(w.v) WHEN 'object' THEN 1 ELSE 2 END)::smallint AS head,
           (CASE jsonb_typeof(w.v)
                 WHEN 'object' THEN (SELECT count(*) FROM jsonb_object_keys(w.v))
                 ELSE jsonb_array_length(w.v)::bigint END) AS n
      FROM w
     WHERE jsonb_typeof(w.v) IN ('object', 'array')
)"""

# ── (3) THE ITEMS — each compound's children, ORDERED, with their leaf ids resolved ──────────
#
# ⚑⚑ THE OBJECT ORDER IS **DECLARED**, NOT INHERITED FROM jsonb. `jsonb` normalises object
# keys to (length, then bytes) on storage and `jsonb_each` yields them in that order, so
# relying on it would work today and would be an undocumented dependency on a storage detail.
# `ORDER BY key COLLATE "C"` is a total order this rung OWNS, locale-independent for the same
# reason ⟡ladder-2b's lock order is.
#
# ⚑⚑ AND THE ORDER IS LOAD-BEARING FOR **SHARING**, WHICH IS WHY IT IS PINNED RATHER THAN LEFT
# FREE. Two objects with equal key sets share a spine SUFFIX only if their members are laid out
# in the same order; a per-document or storage-dependent order would make sharing appear and
# disappear for reasons invisible in the data — the exact defect the right spine was chosen
# over balanced bracketing to avoid. Reconstruction is indifferent to the choice (a jsonb
# object is unordered), so the order costs nothing and buys the sharing.
#
# ⚑ `to_jsonb(it.k)` AND NOT `it.k::jsonb` — ⟡ladder-2b's rule, and it is the same trap here:
# the CAST parses the text as a JSON document, so a key spelled `null`, `123` or `[1]` would
# arrive as a JSON null, a number or an ARRAY instead of the string it is. `to_jsonb` wraps.
#
# ⚑ `csid IS NULL` IS THE LEAF/COMPOUND DISCRIMINATOR AND `jsonb_typeof` IS NOT USED FOR IT.
# The join to `comp` succeeds exactly when the child value is an object or an array, because
# that is `comp`'s own filter — so the two facts cannot disagree, which they could if one were
# a type test and the other a join.
#
# ⚑⚑ `AS MATERIALIZED` ON `it`, AND IT IS THE DIFFERENCE BETWEEN LINEAR AND QUADRATIC — read off
# `--tree-explain`, not guessed. `it` is referenced once, so postgres INLINES it, which pushes
# `cpath`'s `CASE` into the join condition of `itc`. A CASE expression cannot be a hash or merge
# KEY, so the planner merged on `core_id` alone — a column that is CONSTANT within a document —
# and demoted the path equality to a `Join Filter`:
#
#     Merge Left Join   Merge Cond: (c_1.core_id = cc.core_id)
#                       Join Filter: (cc.path = CASE WHEN … END)
#
# i.e. it evaluated the filter over the full CARTESIAN PRODUCT of a document's items and its
# compounds. On one 150 KB document (9,764 records) that is ~10⁹ string comparisons and it ran
# **11 minutes without finishing**. Materialising `it` makes `cpath` a real COLUMN, so the same
# join hashes. The fix is one keyword and it is invisible in the statement's meaning — which is
# exactly why the plan had to be read rather than the SQL.
_ITEM = """,
it AS MATERIALIZED (
    SELECT c.core_id, c.sid, c.depth, c.path, c.head, c.n,
           e.i, e.k, e.child,
           (CASE WHEN e.k IS NULL
                 THEN c.path || length((e.i - 1)::text)::text || ':' || (e.i - 1)::text
                 ELSE c.path || length(e.k)::text || ':' || e.k END) AS cpath
      FROM comp c
      CROSS JOIN LATERAL (
              SELECT row_number() OVER (ORDER BY o.key COLLATE "C") AS i,
                     o.key AS k, o.value AS child
                FROM jsonb_each(c.v) AS o
               WHERE jsonb_typeof(c.v) = 'object'
          UNION ALL
              SELECT a.ord, NULL::text, a.value
                FROM jsonb_array_elements(c.v) WITH ORDINALITY AS a(value, ord)
               WHERE jsonb_typeof(c.v) = 'array'
      ) AS e(i, k, child)
),
itc AS (
    SELECT it.core_id, it.sid, it.depth, it.head, it.n, it.i, it.k, it.child,
           cc.sid AS csid, cc.n AS cn, ks.id AS kid, vs.id AS vid
      FROM it
      LEFT JOIN comp cc ON cc.core_id = it.core_id AND cc.path = it.cpath
      LEFT JOIN dec_scalar ks ON ks.v = to_jsonb(it.k)
      LEFT JOIN dec_scalar vs ON vs.v = it.child
)"""

# ── (4) THE SKELETON — the work list, one row per node, with its ROUND ───────────────────────
#
# ⚑⚑ `rnd` IS ARITHMETIC AND NOT `dense_rank()`, WHICH IS THE SAME ROUND COUNT FOR NONE OF THE
# SORT. `dense_rank() OVER (ORDER BY depth DESC, t)` would be exact and would sort every one of
# ~9M skeleton rows to number them. The block form `(md - depth) * (mt + 1) + t + 1` numbers
# them by arithmetic, leaves GAPS where a (depth, t) pair is unoccupied, and costs nothing — and
# the gaps are free because the caller iterates the DISTINCT `rnd` values that exist, so the
# number of round STATEMENTS is identical either way. What must hold is that a block is wider
# than any `t` in it, which `mt = max(n)` guarantees.
#
# ⚑ `rnd = 0` IS RESERVED FOR THE ROWS WITH NO CHILDREN AT ALL — the LEAF nodes and the EMPTY
# compounds. They are not a special case in the rung; they are the base of the same induction,
# and giving them a round means the rung has ONE shape rather than a first-round branch.
#
# ⚑⚑ THE TOPOLOGICAL CLAIM, CHECKED OVER ALL FOUR PRODUCTIONS RATHER THAN ASSERTED:
#   cell(d, rev)   → its MEMBER at (d, 0): t 0 < rev ✓ ;  its tail at (d, rev-1) ✓ ;
#                    an ARRAY item at depth d+1, whose block is strictly earlier ✓
#   MEMBER(d, 0)   → a key LEAF at rnd 0 ✓ ;  a value at depth d+1 ✓ or a LEAF ✓
#   LEAF / empty   → nothing ✓
# So every child of a row at `rnd = r` has `rnd < r`, and round `r` may insert its whole
# frontier at once.
#
# ⚑ THE THREE ROW FAMILIES ARE A `UNION ALL` AND NOT THREE STATEMENTS. A node kind that got its
# own INSERT would be a place for the round numbering to drift; here one `ORDER BY` covers them
# all and one `ON CONFLICT` arbitrates them all.
#
# ⚑⚑ `lim` IS **SUPPLIED**, NOT COMPUTED FROM THE SCOPE, AND THAT IS WHAT LETS THE WORK LIST BE
# BUILT ONE DOCUMENT AT A TIME WITHOUT INFLATING THE ROUND COUNT. The block width `mt + 1` must
# be the SAME for every document or their `rnd` values land on different grids and the union of
# distinct rounds — which is the number of statements the fixpoint sends — grows for no
# structural reason. So the caller measures `(md, mt)` ONCE over the whole scope with `limits`
# (the walk alone, no joins, no sorts — seconds) and hands the same pair to every per-document
# build.
#
# ⚑ AND BUILDING THE WHOLE CORPUS IN ONE STATEMENT WAS THE FIRST SHAPE AND IS MEASURABLY THE
# WRONG ONE. It puts a ~9M-row sort and two multi-million-row hash builds in a single statement
# that emits nothing until it commits — 6+ minutes with no observable progress and no way to
# resume. Per document, each build is small, the fixpoint's ROUND COUNT is unchanged (same grid),
# and an interruption costs one document rather than the corpus.
_SKEL_ROWS = """,
lim AS (SELECT %s::int AS md, %s::bigint AS mt),
spine AS (
        SELECT itc.core_id, itc.sid, itc.i AS ord, 1::smallint AS kind,
               (1 + (lim.md - itc.depth) * (lim.mt + 1) + 0)::int AS rnd,
               3::smallint AS head,
               NULL::int AS a1_sid, NULL::bigint AS a1_ord, NULL::smallint AS a1_kind,
               itc.kid AS l1,
               itc.csid::int AS a2_sid,
               (CASE WHEN itc.cn > 0 THEN 1 ELSE 0 END)::bigint AS a2_ord,
               (CASE WHEN itc.csid IS NULL THEN NULL ELSE 0 END)::smallint AS a2_kind,
               (CASE WHEN itc.csid IS NULL THEN itc.vid ELSE NULL END) AS l2
          FROM itc CROSS JOIN lim
         WHERE itc.k IS NOT NULL
    UNION ALL
        SELECT itc.core_id, itc.sid, itc.i AS ord, 0::smallint AS kind,
               (1 + (lim.md - itc.depth) * (lim.mt + 1) + (itc.n - itc.i + 1))::int AS rnd,
               itc.head,
               (CASE WHEN itc.k IS NOT NULL THEN itc.sid ELSE itc.csid END)::int AS a1_sid,
               (CASE WHEN itc.k IS NOT NULL THEN itc.i
                     WHEN itc.cn > 0 THEN 1 ELSE 0 END)::bigint AS a1_ord,
               (CASE WHEN itc.k IS NOT NULL THEN 1
                     WHEN itc.csid IS NOT NULL THEN 0 ELSE NULL END)::smallint AS a1_kind,
               (CASE WHEN itc.k IS NULL AND itc.csid IS NULL THEN itc.vid
                     ELSE NULL END) AS l1,
               (CASE WHEN itc.i < itc.n THEN itc.sid ELSE NULL END)::int AS a2_sid,
               (CASE WHEN itc.i < itc.n THEN itc.i + 1 ELSE NULL END)::bigint AS a2_ord,
               (CASE WHEN itc.i < itc.n THEN 0 ELSE NULL END)::smallint AS a2_kind,
               NULL::bigint AS l2
          FROM itc CROSS JOIN lim
),
base AS (
        SELECT comp.core_id, comp.sid::int, 0::bigint AS ord, 0::smallint AS kind,
               0 AS rnd, comp.head,
               NULL::int, NULL::bigint, NULL::smallint, NULL::bigint,
               NULL::int, NULL::bigint, NULL::smallint, NULL::bigint
          FROM comp WHERE comp.n = 0
    UNION
        SELECT lf.core_id, 0::int, lf.sc AS ord, 2::smallint AS kind,
               0 AS rnd, 0::smallint AS head,
               NULL::int, NULL::bigint, NULL::smallint, lf.sc,
               NULL::int, NULL::bigint, NULL::smallint, NULL::bigint
          FROM (SELECT DISTINCT itc.core_id, itc.kid AS sc FROM itc WHERE itc.kid IS NOT NULL
                 UNION
                SELECT DISTINCT itc.core_id, itc.vid FROM itc
                 WHERE itc.vid IS NOT NULL AND itc.csid IS NULL) AS lf
)"""

# ⚑ THE LOCK ORDER IS THE SAME DISCIPLINE ⟡ladder-2b ESTABLISHED AND IT IS NOT THE SAME
# PROPERTY AS REMOVING THE HOLD. A set-based rung inserts N rows in ONE statement and therefore
# HOLDS N row locks until it commits; that hold is not removable, because the set IS the unit
# of work. What IS removable is the CYCLE: every writer offering rows in the same total order
# means a waiter is always strictly behind, so no two writers can each hold what the other
# wants. Stated as the weaker property it is, rather than borrowed as the stronger one.
_SKEL = (
    _WALK
    + _COMP
    + _ITEM
    + _SKEL_ROWS
    + """
INSERT INTO dec_stage (core_id, sid, ord, kind, rnd, head,
                       a1_sid, a1_ord, a1_kind, l1, a2_sid, a2_ord, a2_kind, l2)
SELECT * FROM spine
UNION ALL
SELECT * FROM base
ORDER BY 1, 2, 3, 4
ON CONFLICT DO NOTHING"""
)

# ── (5) THE RUNG — ONE statement, ONE round ──────────────────────────────────────────────────
#
# ⚑⚑ THE `CASE` LADDER IS THE CHILD-SLOT DISCIPLINE, READ OFF THE COLUMNS. An address resolves
# through `dec_ref` (the memo) and then `dec_node` (the handle); a leaf resolves to that
# scalar's LEAF node; all-null is the nullary child `0`. The single head-conditional arm —
# `head = 0` taking `l1` RAW — is `dec_node`'s own rule mirrored, and it is confined to the one
# production where `c1` is a `dec_scalar.id`. It is a data test, not a mode branch: every round
# runs the same statement.
#
# ⚑ `g1`/`g2` CARRY `s.head <> 0` IN THE **JOIN** CONDITION, not in a filter. Without it the
# LEAF rows would each probe `dec_node` for their own not-yet-existing node — harmless, since
# the CASE never reads it, and pure waste at 200k+ rows a round.
#
# ⚑⚑ THE CHILD IS FOUND WITH AN ORDINARY PK LOOKUP AGAINST A **FRESH SNAPSHOT**, AND THAT IS
# WHY THERE IS NO `RETURNING` HERE. Round `r-1` committed; round `r` is a new statement and
# sees it. The alternative — inserting into `dec_node` and reading the new id back through
# `RETURNING` in the same statement — cannot see a row a CONCURRENT writer committed between my
# snapshot and my insert, so it would leave a NULL id and stall that document silently. The
# memo storing CONTENT rather than an id is what buys the race away, with no coordination.
#
# ⚑⚑ `dec_node` IS WRITTEN INSIDE A CTE THE MAIN STATEMENT READS, WHICH FORCES THE ORDER.
# Postgres does not specify the execution order of data-modifying CTEs. The main INSERT does
# not NEED `n`'s output — it inserts `f`'s own columns — so `WHERE (SELECT count(*) FROM n)
# >= 0` is there for exactly one reason: to make `dec_node` acquire its locks BEFORE `dec_ref`
# acquires any, in every writer, so the two tables are always taken in the same order. It is a
# lock-ORDER device, not a correctness one, and it is written down as such because a reader
# who deletes it as dead weight reintroduces a cycle that only shows up under contention.
_RUNG = """\
WITH f AS (
    SELECT s.core_id, s.sid, s.ord, s.kind, s.head,
           (CASE WHEN s.head = 0 THEN s.l1
                 WHEN s.a1_sid IS NOT NULL THEN n1.id
                 WHEN s.l1 IS NOT NULL THEN g1.id
                 ELSE 0 END) AS c1,
           (CASE WHEN s.a2_sid IS NOT NULL THEN n2.id
                 WHEN s.l2 IS NOT NULL THEN g2.id
                 ELSE 0 END) AS c2
      FROM dec_stage s
      LEFT JOIN dec_ref r1 ON r1.core_id = s.core_id AND r1.sid = s.a1_sid
                          AND r1.ord = s.a1_ord AND r1.kind = s.a1_kind
      LEFT JOIN dec_node n1 ON n1.head = r1.head AND n1.c1 = r1.c1 AND n1.c2 = r1.c2
      LEFT JOIN dec_node g1 ON s.head <> 0 AND g1.head = 0 AND g1.c1 = s.l1 AND g1.c2 = 0
      LEFT JOIN dec_ref r2 ON r2.core_id = s.core_id AND r2.sid = s.a2_sid
                          AND r2.ord = s.a2_ord AND r2.kind = s.a2_kind
      LEFT JOIN dec_node n2 ON n2.head = r2.head AND n2.c1 = r2.c1 AND n2.c2 = r2.c2
      LEFT JOIN dec_node g2 ON g2.head = 0 AND g2.c1 = s.l2 AND g2.c2 = 0
     WHERE s.rnd = %s::int
       AND (%s::text IS NULL OR s.core_id = %s::text)
),
n AS (
    INSERT INTO dec_node (head, c1, c2)
    SELECT DISTINCT f.head, f.c1, f.c2 FROM f
     ORDER BY 1, 2, 3
    ON CONFLICT DO NOTHING
    RETURNING 1
)
INSERT INTO dec_ref (core_id, sid, ord, kind, head, c1, c2)
SELECT f.core_id, f.sid, f.ord, f.kind, f.head, f.c1, f.c2
  FROM f
 WHERE (SELECT count(*) FROM n) >= 0
 ORDER BY 1, 2, 3, 4
ON CONFLICT DO NOTHING"""


# ── (5b) THE CHAIN RUNG — a WHOLE SPINE in ONE statement (⟡ladder-fixpoint) ──────────────────
#
# ⚑⚑ THE WALL THIS DISSOLVES, VERBATIM, SO THE REBUTTAL IS ATTACHED TO THE CLAIM IT REBUTS
# (`radiant-weaving-dawn` §ⓧ.wall): *"An assignment along a suffix chain of length N is Θ(N)
# SEQUENTIAL — cell_k needs cell_{k+1}'s id — and a recursive CTE cannot assign (no INSERT
# inside WITH RECURSIVE). So bounded+exact ⇒ N rounds."* Both halves are TRUE and they do not
# compose into the wall, for the same reason ⟡ladder-retire's did not: **a recursive CTE cannot
# assign, but the OUTER QUERY CAN.** `w` WALKS the spine (lookups only, no assignment); the
# outer statement assigns every new cell an id and inserts the whole chain at once. 115,268
# rounds become ONE.
#
# ⚑⚑ THE PROPERTY THAT MAKES IT SOUND IS **SUFFIX-CLOSURE OF EXISTENCE**, and it is a theorem
# about this grammar rather than a fact about this corpus. `cell_i = (head, item_i, id(cell_i+1))`,
# so a `dec_node` row for cell_i CONTAINS a valid id for cell_{i+1}; `dec_node` is insert-only
# under every rung in this ladder, so that id names a row that exists. Therefore
#
#     cell_i present  ⇒  cell_{i+1} present
#
# and the present cells of a spine are exactly a SUFFIX `[cut+1 … n]`. One backward walk finds
# `cut`; every cell at `ord ≤ cut` is NEW, with no lookup required and none possible — its `c2`
# is an id this statement is about to mint, and no row that already exists can reference an id
# that does not yet exist. So the walk stops LOOKING the moment it stops FINDING, which is why
# the recursion is a lookup and not a search.
#
# ⚑⚑ AND `WHERE w.rid IS NOT NULL` IN THE RECURSIVE TERM IS THE DIFFERENCE BETWEEN A WALK AND
# A SCAN — MEASURED, after shipping it the wrong way round first. The first spelling carried
# the whole spine through the recursion and merely GUARDED the lookup, so a 9,764-cell chain
# ran 9,764 iterations, each re-probing a materialised 48,831-row CTE: the build did not finish
# in the time the old rung's first thousand rounds would have taken. Terminating the recursion
# AT the cut makes its length `|existing suffix| + 1` — ONE iteration for a document nothing is
# shared with yet — and the new cells are then read straight out of `f` by `ord ≤ cord`, with
# no recursion at all. The cells above the cut were never worth walking to: nothing about them
# is looked up.
#
# ⚑⚑ THE GENUINELY HARD PART IS DEDUP, AND IT IS SOLVED BY PARTITIONING RATHER THAN BY HASHING.
# Bulk assignment wants an id to be a function of ordinality; content sharing wants two
# content-equal cells to get ONE id. Within one spine they cannot conflict (`w`'s cells have
# pairwise-distinct `c2` by induction from the cut, so no two are content-equal). ACROSS spines
# they can — two chains that agree from the cut upward. `grp` is the whole answer: chains are
# partitioned by their **ANCHOR** `(head, c1, kid)` — the deepest new cell's content, which is
# fully determined BEFORE any assignment — and one chain per anchor is taken per statement.
#
#     distinct anchors ⇒ distinct cut cells ⇒ distinct ids ⇒ distinct `c2` one level up ⇒ …
#
# so EVERY new cell in the batch is content-distinct, by induction, with no digest, no hash and
# no key whose size grows with the subtree. The chains a statement skips are not lost: the next
# statement re-walks them and finds the just-committed chain as an EXISTING suffix, so their
# `cut` moves up and the sharing is discovered rather than manufactured. The caller iterates to
# a fixpoint; the round count is the max anchor multiplicity, MEASURED, not the spine length.
#
# ⚑⚑ `nextval` INSIDE `INSERT … SELECT`, AND THE RULING THAT LICENSES IT (user, this arc):
# *"There is allocation… but only when inserting into the strings table. But autonumber is
# sufficient."* — with the governing form: **allocation is not the defect, a CLIENT HOLDING an
# allocated value is.** `nextval` here holds nothing: the value is minted, spent and committed
# inside one statement, and a client-side `max(id)+1` — the thing that actually raced — is
# exactly what this is not.
#
# ⚑ `OVERRIDING SYSTEM VALUE` AND **NOT** A DDL CHANGE TO `GENERATED BY DEFAULT`. The brief
# blesses relaxing the identity; the relaxation is not needed and would be strictly worse.
# `GENERATED ALWAYS` exists so a writer cannot supply an id BY ACCIDENT; `OVERRIDING SYSTEM
# VALUE` is a clause that must be TYPED, so accidents stay refused everywhere else while this
# one statement — which mints its ids from the column's own sequence — says so out loud.
#
# ⚑ `AS MATERIALIZED` ON `alloc` STATES A GUARANTEE POSTGRES ALREADY GIVES, AND SAYING SO IS
# MORE HONEST THAN THE CLAIM I SHIPPED FIRST. The reasoning that put it there: `alloc` is read
# TWICE (a cell's own id and its child's), so an inlined CTE would evaluate `nextval` once per
# reference, mint two different ids for one cell, and silently break every `c2`. MEASURED by
# mutation: removing the keyword changes NOTHING behaviourally — postgres inlines a CTE only
# when it is referenced exactly once AND is side-effect-free, and this one fails both tests. So
# it is an EQUIVALENT MUTANT, met by a compiled-SQL case and not by a fabricated behavioural
# one. It stays because a later refactor down to a single reference would make it load-bearing
# with no other line changing.
#
# ⚑⚑ NO `ON CONFLICT` ON `dec_node`, AND THAT IS THE CONCURRENCY OBSERVABLE RATHER THAN AN
# OVERSIGHT. Inside a batch a duplicate is IMPOSSIBLE by the anchor argument, and no new cell
# can equal an existing row (its `c2` is freshly minted). So a `23505` on this statement is, by
# construction, evidence of a CONCURRENT WRITER and of nothing else — the transaction aborts
# having written nothing, and the caller's next pass finds the winner's nodes as an existing
# suffix and converges. `ON CONFLICT DO NOTHING` would instead DROP the losing row while its
# parent kept referencing the id it was promised, i.e. it would convert a loud, harmless abort
# into a silent dangling reference. `dec_ref` keeps `ON CONFLICT DO NOTHING` because it is
# address-keyed and a re-offer of the same address is genuinely a no-op.
#
# ⚑ THE ORDER `dec_node` THEN `dec_ref` IS FORCED THE SAME WAY `_RUNG` FORCES IT — the
# `(SELECT count(*) FROM ins) >= 0` device, kept verbatim rather than re-derived.
#
# ⚑⚑ `pend` IS A COST FILTER AND IT IS THE DIFFERENCE BETWEEN SIX HOURS AND ONE — MEASURED on
# the corpus, mid-run, not predicted. Without it `f` resolves EVERY spine cell of the document
# on EVERY round: three index probes per cell into relations of millions of rows, i.e.
# 476,798 × 3 random reads for the largest document, per round, forever — and the caller calls
# it three times a round (census, rung, census). The corpus was writing `dec_ref` at ~20k
# rows/min, which is ~6 hours for 9.5M.
#
# ⚑ `pend` COSTS ONE `dec_ref` PK PROBE **PER CHAIN** INSTEAD OF THREE PER CELL, and it is
# derived from the work list alone (`sp` — a prefix scan of `dec_stage`'s PK, no joins). After
# the first round most chains are done, so `f` collapses to the frontier rather than staying the
# whole document. **The predicate is unchanged**: `pend` is exactly the old `tgt`'s
# `NOT EXISTS (… resolving dec_ref row …)` clause, HOISTED above `f` so it prunes the input
# instead of filtering the output. Same rows, different order of evaluation.
#
# ⚑ AND THE CENSUS IS HOISTED THE SAME WAY, SO THE TWO STILL ASK ONE QUESTION. `done` is now
# `chains − pend` and `todo` is `pend AND bad = 0` — arithmetic over the same two sets the rung
# uses. `ready` is `done + todo`, which redefines it slightly: a DONE chain now counts as ready
# without re-deriving its items. That is only wrong if a built chain's items later stop
# resolving, which requires a DELETE this ladder never performs, and `--tree-census`'s
# `dangling`/`unresolved` are what would report it.
_CHAIN = """\
WITH RECURSIVE sp AS (
    SELECT s.core_id, s.sid, max(s.ord) AS n
      FROM dec_stage s
     WHERE s.kind = 0 AND s.ord > 0 AND s.core_id = %s::text
     GROUP BY 1, 2
),
pend AS (
    SELECT sp.core_id, sp.sid, sp.n FROM sp
     WHERE NOT EXISTS (SELECT 1 FROM dec_ref d
                         JOIN dec_node dn ON dn.head = d.head AND dn.c1 = d.c1 AND dn.c2 = d.c2
                        WHERE d.core_id = sp.core_id AND d.sid = sp.sid
                          AND d.ord = 1 AND d.kind = 0)
),
f AS (
    SELECT s.core_id, s.sid, s.ord, s.head,
           (CASE WHEN s.a1_sid IS NOT NULL THEN n1.id
                 WHEN s.l1 IS NOT NULL THEN g1.id END) AS c1
      FROM pend p
      JOIN dec_stage s ON s.core_id = p.core_id AND s.sid = p.sid
                      AND s.kind = 0 AND s.ord > 0
      LEFT JOIN dec_ref r1 ON r1.core_id = s.core_id AND r1.sid = s.a1_sid
                          AND r1.ord = s.a1_ord AND r1.kind = s.a1_kind
      LEFT JOIN dec_node n1 ON n1.head = r1.head AND n1.c1 = r1.c1 AND n1.c2 = r1.c2
      LEFT JOIN dec_node g1 ON s.a1_sid IS NULL AND g1.head = 0
                           AND g1.c1 = s.l1 AND g1.c2 = 0
),
rdy AS (
    SELECT f.core_id, f.sid, max(f.ord) AS n,
           count(*) FILTER (WHERE f.c1 IS NULL) AS bad
      FROM f GROUP BY 1, 2
),
tgt AS (
    SELECT r.core_id, r.sid, r.n FROM rdy r WHERE r.bad = 0
),
w AS (
        SELECT f.core_id, f.sid, f.ord, f.head, f.c1, 0::bigint AS kid, dn.id AS rid
          FROM tgt t
          JOIN f ON f.core_id = t.core_id AND f.sid = t.sid AND f.ord = t.n
          LEFT JOIN dec_node dn ON dn.head = f.head AND dn.c1 = f.c1 AND dn.c2 = 0
    UNION ALL
        SELECT f.core_id, f.sid, f.ord, f.head, f.c1, w.rid AS kid, dn.id
          FROM w
          JOIN f ON f.core_id = w.core_id AND f.sid = w.sid AND f.ord = w.ord - 1
          LEFT JOIN dec_node dn ON dn.head = f.head AND dn.c1 = f.c1 AND dn.c2 = w.rid
         WHERE w.rid IS NOT NULL
),
anch AS (
    SELECT t.core_id, t.sid, coalesce(c.ord, 0) AS cord,
           c.head, c.c1, coalesce(c.kid, 0) AS kid
      FROM tgt t
      LEFT JOIN w c ON c.core_id = t.core_id AND c.sid = t.sid AND c.rid IS NULL
),
grp AS (
    SELECT a.core_id, a.sid, a.cord, a.kid,
           (CASE WHEN a.cord = 0 THEN 1
                 ELSE row_number() OVER (PARTITION BY a.head, a.c1, a.kid
                                         ORDER BY a.core_id, a.sid) END) AS g
      FROM anch a
),
nc AS (
    SELECT f.core_id, f.sid, f.ord, f.head, f.c1, g.cord, g.kid,
           row_number() OVER (ORDER BY f.core_id, f.sid, f.ord DESC) AS j
      FROM f JOIN grp g ON g.core_id = f.core_id AND g.sid = f.sid AND g.g = 1
     WHERE f.ord <= g.cord
),
alloc AS MATERIALIZED (
    SELECT x.j, nextval(pg_get_serial_sequence('dec_node', 'id')) AS id
      FROM (SELECT nc.j FROM nc ORDER BY nc.j) x
),
node AS (
    SELECT nc.core_id, nc.sid, nc.ord, a.id, nc.head, nc.c1,
           (CASE WHEN nc.ord = nc.cord THEN nc.kid ELSE ap.id END) AS c2
      FROM nc JOIN alloc a ON a.j = nc.j
      LEFT JOIN alloc ap ON ap.j = nc.j - 1
),
old AS (
    SELECT w.core_id, w.sid, w.ord, w.head, w.c1, w.kid AS c2
      FROM w JOIN grp g ON g.core_id = w.core_id AND g.sid = w.sid AND g.g = 1
     WHERE w.rid IS NOT NULL
),
ins AS (
    INSERT INTO dec_node (id, head, c1, c2) OVERRIDING SYSTEM VALUE
    SELECT n.id, n.head, n.c1, n.c2 FROM node n ORDER BY 1
    RETURNING 1
)
INSERT INTO dec_ref (core_id, sid, ord, kind, head, c1, c2)
SELECT z.core_id, z.sid, z.ord, 0, z.head, z.c1, z.c2
  FROM (SELECT core_id, sid, ord, head, c1, c2 FROM node
        UNION ALL
        SELECT core_id, sid, ord, head, c1, c2 FROM old) z
 WHERE (SELECT count(*) FROM ins) >= 0
 ORDER BY 1, 2, 3
ON CONFLICT DO NOTHING"""

# ⚑⚑ THE WORK PREDICATE, SPELLED APART FROM THE RUNG, BECAUSE A FIXPOINT LOOP THAT KEEPS
# STEPPING WHILE THE CENSUS DOES NOT MOVE IS A **LIVELOCK SIGNATURE** and the only way to see
# one is to be able to ask "how much work is left" independently of "how much did I just do".
# `chains` is every spine of the document; `ready` is those whose items all resolve; `todo` is
# the ready ones that are not DONE — exactly `_CHAIN`'s `tgt`, and the two spellings must stay
# identical or the guard measures a different question from the one the rung answers.
# `blocked` = chains − ready is the number a round CANNOT consume, so `todo = 0 AND blocked > 0`
# is "waiting on another tier" and `todo > 0` with an unchanged `todo` is the violation.
#
# ⚑⚑ **DONE MEANS THE HEAD CELL'S `dec_ref` ROW *RESOLVES*, NOT MERELY THAT IT EXISTS** — a
# correction the suite made, not a refinement I chose. The first spelling asked only whether the
# address had a row, so a chain whose `dec_node` row had been REMOVED read as done and the rung
# skipped it: `dangling` stayed positive and the document stopped reconstructing, while the
# per-cell rung it replaced had repaired exactly that (it re-offers every round's content, and
# re-inserting an identical `(head,c1,c2)` restores the row under a new id). Joining `dec_node`
# in the predicate is what makes the chain rung a REPAIRER rather than only a builder.
#
# ⚑ AND THE REPAIR REACHES A DAMAGED **HEAD**, NOT A DAMAGED INTERIOR — named rather than
# implied. If a middle cell's node is deleted, the head cell's content still resolves, so the
# chain reads as done and this rung leaves it. That is a real narrowing against the per-cell
# rung; the observable is `--tree-census`'s `dangling`, which reports it rather than hiding it.
_CHAIN_CENSUS = """\
WITH sp AS (
    SELECT s.core_id, s.sid, max(s.ord) AS n
      FROM dec_stage s
     WHERE s.kind = 0 AND s.ord > 0 AND (%s::text IS NULL OR s.core_id = %s::text)
     GROUP BY 1, 2
),
pend AS (
    SELECT sp.core_id, sp.sid, sp.n FROM sp
     WHERE NOT EXISTS (SELECT 1 FROM dec_ref d
                         JOIN dec_node dn ON dn.head = d.head AND dn.c1 = d.c1 AND dn.c2 = d.c2
                        WHERE d.core_id = sp.core_id AND d.sid = sp.sid
                          AND d.ord = 1 AND d.kind = 0)
),
f AS (
    SELECT s.core_id, s.sid, s.ord,
           (CASE WHEN s.a1_sid IS NOT NULL THEN n1.id
                 WHEN s.l1 IS NOT NULL THEN g1.id END) AS c1
      FROM pend p
      JOIN dec_stage s ON s.core_id = p.core_id AND s.sid = p.sid
                      AND s.kind = 0 AND s.ord > 0
      LEFT JOIN dec_ref r1 ON r1.core_id = s.core_id AND r1.sid = s.a1_sid
                          AND r1.ord = s.a1_ord AND r1.kind = s.a1_kind
      LEFT JOIN dec_node n1 ON n1.head = r1.head AND n1.c1 = r1.c1 AND n1.c2 = r1.c2
      LEFT JOIN dec_node g1 ON s.a1_sid IS NULL AND g1.head = 0
                           AND g1.c1 = s.l1 AND g1.c2 = 0
),
rdy AS (
    SELECT f.core_id, f.sid, count(*) FILTER (WHERE f.c1 IS NULL) AS bad
      FROM f GROUP BY 1, 2
)
SELECT (SELECT count(*) FROM sp) AS chains,
       (SELECT coalesce(max(sp.n), 0) FROM sp) AS longest,
       (SELECT coalesce(sum(sp.n), 0) FROM sp) AS cells,
       (SELECT count(*) FROM sp) - (SELECT count(*) FROM pend)
           + (SELECT count(*) FROM rdy WHERE rdy.bad = 0) AS ready,
       (SELECT count(*) FROM sp) - (SELECT count(*) FROM pend) AS done,
       (SELECT count(*) FROM rdy WHERE rdy.bad = 0) AS todo"""


# ⚑⚑ THE BREAKDOWN INSTRUMENT, AND IT EXISTS BECAUSE THE STALL GUARD FIRED. Memory
# `deadlock-breakdown-before-any-fix`: *"the location of that hold is the finding. Clearing it
# destroys the evidence."* A guard that says "todo did not move" and cannot say WHICH chain did
# not move leaves the next reader to re-derive it — so the guard names the rows. One row per
# unconsumed chain: its document, its `sid`, its length, and whether its head-cell address is
# missing (never built) or present-but-unresolvable (built and then damaged), which are
# different repairs.
_CHAIN_TODO = """\
WITH RECURSIVE sp AS (
    SELECT s.core_id, s.sid, max(s.ord) AS n
      FROM dec_stage s
     WHERE s.kind = 0 AND s.ord > 0 AND s.core_id = %s::text
     GROUP BY 1, 2
),
pend AS (
    SELECT sp.core_id, sp.sid, sp.n FROM sp
     WHERE NOT EXISTS (SELECT 1 FROM dec_ref d
                         JOIN dec_node dn ON dn.head = d.head AND dn.c1 = d.c1 AND dn.c2 = d.c2
                        WHERE d.core_id = sp.core_id AND d.sid = sp.sid
                          AND d.ord = 1 AND d.kind = 0)
),
f AS (
    SELECT s.core_id, s.sid, s.ord, s.head,
           (CASE WHEN s.a1_sid IS NOT NULL THEN n1.id
                 WHEN s.l1 IS NOT NULL THEN g1.id END) AS c1
      FROM pend p
      JOIN dec_stage s ON s.core_id = p.core_id AND s.sid = p.sid
                      AND s.kind = 0 AND s.ord > 0
      LEFT JOIN dec_ref r1 ON r1.core_id = s.core_id AND r1.sid = s.a1_sid
                          AND r1.ord = s.a1_ord AND r1.kind = s.a1_kind
      LEFT JOIN dec_node n1 ON n1.head = r1.head AND n1.c1 = r1.c1 AND n1.c2 = r1.c2
      LEFT JOIN dec_node g1 ON s.a1_sid IS NULL AND g1.head = 0
                           AND g1.c1 = s.l1 AND g1.c2 = 0
),
rdy AS (
    SELECT f.core_id, f.sid, max(f.ord) AS n,
           count(*) FILTER (WHERE f.c1 IS NULL) AS bad
      FROM f GROUP BY 1, 2
),
tgt AS (
    SELECT r.core_id, r.sid, r.n FROM rdy r WHERE r.bad = 0
),
w AS (
        SELECT f.core_id, f.sid, f.ord, f.head, f.c1, 0::bigint AS kid, dn.id AS rid
          FROM tgt t
          JOIN f ON f.core_id = t.core_id AND f.sid = t.sid AND f.ord = t.n
          LEFT JOIN dec_node dn ON dn.head = f.head AND dn.c1 = f.c1 AND dn.c2 = 0
    UNION ALL
        SELECT f.core_id, f.sid, f.ord, f.head, f.c1, w.rid AS kid, dn.id
          FROM w
          JOIN f ON f.core_id = w.core_id AND f.sid = w.sid AND f.ord = w.ord - 1
          LEFT JOIN dec_node dn ON dn.head = f.head AND dn.c1 = f.c1 AND dn.c2 = w.rid
         WHERE w.rid IS NOT NULL
),
anch AS (
    SELECT t.core_id, t.sid, t.n, coalesce(c.ord, 0) AS cord,
           c.head, c.c1, coalesce(c.kid, 0) AS kid
      FROM tgt t
      LEFT JOIN w c ON c.core_id = t.core_id AND c.sid = t.sid AND c.rid IS NULL
)
SELECT a.core_id, a.sid, a.n, a.cord, a.kid,
       (CASE WHEN a.cord = 0 THEN 1
             ELSE row_number() OVER (PARTITION BY a.head, a.c1, a.kid
                                     ORDER BY a.core_id, a.sid) END) AS g,
       count(*) OVER (PARTITION BY a.head, a.c1, a.kid) AS anchor_share,
       EXISTS (SELECT 1 FROM dec_ref d WHERE d.core_id = a.core_id AND d.sid = a.sid
                 AND d.ord = 1 AND d.kind = 0) AS addressed
  FROM anch a
 ORDER BY 1, 2
 LIMIT 20"""


def chain_todo_sql(core_id):
    """`(sql, params)` — the UNCONSUMED chains, one row each. The stall guard's breakdown.

    ⚑ IT RUNS THE RUNG'S OWN WALK, NOT A SECOND OPINION OF IT. `cord` (where the existing
    suffix ends), `kid` (what the cut cell's tail resolves to), `g` and `anchor_share` are the
    four values that decide whether a chain is taken this round — so a chain the rung skipped
    reports WHY it was skipped, rather than only that it was.
    """
    return (_CHAIN_TODO, (core_id,))


def chain_sql(core_id):
    """`(sql, params)` — THE CHAIN RUNG. One statement, one BATCH of whole spines.

    ⚑ THE SCOPE IS A CONCRETE `core_id` FOR THE REASON THE WALK'S IS — `_WALK`'s measured 55
    seconds per document. This statement's cardinality flows from `f`, so an unestimable
    disjunction over an unbound parameter would make the planner assume the corpus and hash
    `dec_ref` for every round.
    """
    return (_CHAIN, (core_id,))


def chain_census_sql(core_id=None):
    """`(sql, params)` — the chain WORK PREDICATE: chains · ready · done · todo · longest."""
    return (_CHAIN_CENSUS, (core_id, core_id))


def flat_rounds_sql(core_id=None):
    """`(sql, params)` — the NON-CHAIN round schedule: leaves, empty compounds, MEMBERs.

    ⚑⚑ THE COMPLEMENT OF THE CHAIN RUNG, DERIVED FROM THE GRAMMAR RATHER THAN FROM THE GRID.
    A spine cell is `kind = 0 AND ord > 0`; everything else — `kind = 2` (LEAF), `kind = 1`
    (MEMBER), `kind = 0 AND ord = 0` (an EMPTY compound) — has arity-2 children with NO
    sequential dependency between siblings, so a whole `rnd` slice of them still inserts at
    once and `_RUNG` is kept VERBATIM for them. Asking `dec_stage` which rounds hold such a row
    is what makes this a partition of the work list rather than a second numbering of it.

    ⚑ AND THE SPINE ROUNDS ARE THE ONES THAT VANISH: `t` is 0 for every row this returns and
    `1 … n` for a spine cell, so the rounds dropped here are exactly the 115,268 the wall
    counted.
    """
    return (
        "SELECT DISTINCT s.rnd FROM dec_stage s "
        "WHERE (s.kind <> 0 OR s.ord = 0) "
        "AND (%s::text IS NULL OR s.core_id = %s::text) ORDER BY 1",
        (core_id, core_id),
    )


def skeleton_sql(core_id, md, mt):
    """`(sql, params)` — build the work list for one document, or for every document.

    ⚑ SPLIT OUT SO A GUARD CAN ANCHOR ON THE COMPILED SQL, and that is not sufficient on its
    own: `_insert_row_sql`'s residue records a compiled-SQL guard forged with an SQL COMMENT,
    green suite and all. The behavioural cases drive this against a real relation; the
    compiled-SQL cases pin only properties a comment cannot fake.

    ⚑ `md`/`mt` ARE REQUIRED POSITIONALS AND NOT DEFAULTED, DELIBERATELY. A default would let a
    caller build one document on a private grid and another on a different one, which is silent:
    every document still resolves correctly, the fixpoint just sends thousands more statements
    than it needs to. Making the grid impossible to omit is cheaper than a case that notices.
    """
    return (_SKEL, (core_id, md, mt))


def limits_sql(core_id):
    """`(sql, params)` — ONE document's contribution to the ROUND GRID: max depth, max width.

    ⚑ THE WALK ALONE — no joins, no window, no sort. This is the same recursion the skeleton
    build runs, stopped at two aggregates, and it is the cheap half: it reads one document and
    returns two integers, where the build materialises that document's whole work list.

    ⚑ PER DOCUMENT AND MAXED BY THE CALLER, NOT AGGREGATED HERE, for the reason the walk is
    concretely scoped at all: an unbound scope parameter is what made the planner assume the
    corpus. `max` over 43 measured pairs is the same number and costs the caller one variable.
    """
    return (
        _WALK + " SELECT coalesce(max(w.depth), 0) AS md, "
        "coalesce(max(CASE jsonb_typeof(w.v) "
        "WHEN 'object' THEN (SELECT count(*) FROM jsonb_object_keys(w.v)) "
        "WHEN 'array' THEN jsonb_array_length(w.v)::bigint ELSE 0 END), 0) AS mt "
        "FROM w WHERE jsonb_typeof(w.v) IN ('object', 'array')",
        (core_id,),
    )


def scope_sql(core_id=None):
    """`(sql, params)` — the documents in scope, as the caller's per-document build list."""
    return (
        "SELECT core_id, relpath FROM core_decoded d "
        "WHERE (%s::text IS NULL OR d.core_id = %s::text) ORDER BY relpath",
        (core_id, core_id),
    )


def round_sql(rnd, core_id=None):
    """`(sql, params)` — THE RUNG. One round, one statement, whole table or one document."""
    return (_RUNG, (rnd, core_id, core_id))


def rounds_sql(core_id=None):
    """`(sql, params)` — the ROUND SCHEDULE the caller iterates, read from the work list.

    ⚑⚑ THE SCHEDULE IS DATA, NOT A `range()`. `rnd` is numbered by arithmetic blocks, so it
    has GAPS wherever a (depth, t) pair is unoccupied — and iterating `0 … max(rnd)` would
    issue up to 576,350 statements for a corpus whose real frontier count is ~115,300. Asking
    the relation which rounds EXIST is the difference, and it is also the honest answer to
    "how many rounds did this take": the number of rows this query returns.
    """
    return (
        "SELECT DISTINCT s.rnd FROM dec_stage s "
        "WHERE (%s::text IS NULL OR s.core_id = %s::text) ORDER BY 1",
        (core_id, core_id),
    )


def digest_sql():
    """`(sql, params)` — the TREE's content as one row, for the byte-identity half of idempotence.

    ⚑ IDEMPOTENCE IS "0 ROWS WRITTEN **AND** THE RELATION UNCHANGED", AND THE SECOND HALF NEEDS
    AN INSTRUMENT — ⟡ladder-2b's `vocab_digest` argument, unchanged: a rung that deleted every
    row and rewrote it identically also reports 0 new rows on the run after, and only the id
    ASSIGNMENT betrays it. Ordering by `id` is what makes a reassignment visible; ordering by
    the content key would hide exactly the defect this is for.
    """
    return (
        "SELECT count(*) AS rows, count(DISTINCT id) AS ids, "
        "md5(coalesce(string_agg(id::text || ' ' || head::text || ' ' || c1::text "
        "|| ' ' || c2::text, E'\\n' ORDER BY id), '')) AS digest FROM dec_node",
        (),
    )


def complete_sql(core_id=None):
    """`(sql, params)` — EXACT / MISSING, driven from the work list and the tree together.

    ⚑ `missing` IS THE HEADLINE AND `present` IS NOT ENOUGH — ⟡ladder-2b's rule. "9,078,663
    present" reads identically whether the fixpoint finished or never started, so the
    population rides beside it and an empty scope is visible as a zero rather than as a pass.

    ⚑⚑ THREE DIFFERENT ABSENCES, COUNTED APART, BECAUSE THEY SEND THE OPERATOR TO DIFFERENT
    PLACES. `unresolved` = a skeleton row whose LEAF lookup found no `dec_scalar` row (the
    vocab tier is behind — run `--ingest-vocab`). `missing` = a skeleton row with no `dec_ref`
    row (the fixpoint has not finished — run more rounds). `dangling` = a `dec_ref` row whose
    `(head,c1,c2)` has no `dec_node` row (the tree relation was damaged). A single "incomplete"
    number would collapse three distinct repairs into one shrug.

    ⚑⚑ `unresolved` IS A **STRUCTURAL** PREDICATE AND MY FIRST SPELLING WAS A ROSTER OF ONE.
    It read `kind = 1 AND l1 IS NULL` — the member KEY only — and so was blind to an unresolved
    member VALUE or array ITEM, both of which fail SILENTLY: an absent leaf id leaves both the
    address and the leaf column NULL, which the rung reads as the nullary child `0`. The
    corrected form asks the question the grammar answers: **a MEMBER always has a key and a
    value, and a spine cell always has an item**, so a null slot in any of those three
    positions is an absence and not a legitimate nil. Only a cell's TAIL and an empty
    compound's slots may be null, and those are exactly the positions this predicate omits.
    """
    return (
        "SELECT (SELECT count(*) FROM dec_stage s WHERE (%s::text IS NULL "
        "OR s.core_id = %s::text)) AS staged, "
        "(SELECT count(*) FROM dec_ref r WHERE (%s::text IS NULL "
        "OR r.core_id = %s::text)) AS present, "
        "(SELECT count(*) FROM dec_stage s LEFT JOIN dec_ref r "
        "ON r.core_id = s.core_id AND r.sid = s.sid AND r.ord = s.ord AND r.kind = s.kind "
        "WHERE r.core_id IS NULL AND (%s::text IS NULL OR s.core_id = %s::text)) AS missing, "
        "(SELECT count(*) FROM dec_stage s WHERE ((s.kind = 1 AND (s.l1 IS NULL "
        "OR (s.a2_sid IS NULL AND s.l2 IS NULL))) OR (s.kind = 0 AND s.ord > 0 "
        "AND s.a1_sid IS NULL AND s.l1 IS NULL)) "
        "AND (%s::text IS NULL OR s.core_id = %s::text)) AS unresolved, "
        "(SELECT count(*) FROM dec_ref r LEFT JOIN dec_node d "
        "ON d.head = r.head AND d.c1 = r.c1 AND d.c2 = r.c2 "
        "WHERE d.head IS NULL AND (%s::text IS NULL OR r.core_id = %s::text)) AS dangling",
        (core_id,) * 10,
    )


def sharing_sql():
    """`(sql, params)` — THE NUMBER THE SPINE DECISION WAS MADE TO PROTECT.

    ⚑⚑ MEASURED, NOT ASSUMED (the brief's standing instruction). `shared` counts nodes with
    more than one PARENT REFERENCE — the fan-in the SPPF exists for — and `positions` counts
    what the forest would have cost with NO sharing at all: one node per tree position, which
    is exactly one `dec_ref` row per address plus the leaf occurrences the memo already
    deduplicates per document.

    ⚑ A PARENT REFERENCE IS COUNTED ONCE PER SLOT, NOT ONCE PER PARENT ROW. A node that is
    BOTH children of one parent (`OBJ(x, x)` — possible, since a member and a tail can coincide
    in principle) has fan-in 2, because it is reached from two places. Collapsing that to 1
    would under-report sharing on exactly the structures sharing is for.

    ⚑ `c <> 0` EXCLUDES THE NULLARY CHILD. `0` is not a node, so counting it would report the
    absence of a child as a share and would put a phantom at the top of the fan-in ranking.

    ⚑⚑ TWO "WITHOUT SHARING" NUMBERS, BECAUSE `dec_ref` IS NOT ONE. `positions` is one row per
    ADDRESS, and the work list carries a LEAF once per (document, scalar) — so it already
    deduplicates leaves within a document and is a LOWER bound on the unshared forest.
    `tree_positions` is the honest figure: every non-leaf address, plus every child SLOT that
    holds a leaf, which is the number of nodes a plain tree with no sharing at all would have.
    Reporting only the first would understate the collapse and would do it silently.
    """
    return (
        "WITH pr AS (SELECT c1 AS c FROM dec_node WHERE c1 <> 0 AND head <> 0 "
        "UNION ALL SELECT c2 FROM dec_node WHERE c2 <> 0), "
        "fan AS (SELECT c, count(*) AS k FROM pr GROUP BY c) "
        "SELECT (SELECT count(*) FROM dec_node) AS nodes, "
        "(SELECT count(*) FROM fan WHERE k > 1) AS shared, "
        "(SELECT coalesce(max(k), 0) FROM fan) AS widest, "
        "(SELECT coalesce(sum(k), 0) FROM fan) AS refs, "
        "(SELECT count(*) FROM dec_ref) AS positions, "
        "(SELECT count(*) FILTER (WHERE kind <> 2) "
        "+ count(*) FILTER (WHERE head <> 0 AND l1 IS NOT NULL) "
        "+ count(*) FILTER (WHERE l2 IS NOT NULL) FROM dec_stage) AS tree_positions, "
        "(SELECT count(*) FROM dec_node WHERE head = 1 OR head = 2) AS spine_nodes, "
        "(SELECT count(*) FROM fan JOIN dec_node d ON d.id = fan.c "
        "WHERE fan.k > 1 AND (d.head = 1 OR d.head = 2)) AS spine_shared",
        (),
    )


def roots_sql(core_id=None):
    """`(sql, params)` — each document's ROOT node id, the entry point for reconstruction.

    ⚑ THE ROOT COMPOUND IS THE ONE AT THE EMPTY PATH, WHICH IS `sid = 1` BY CONSTRUCTION:
    `comp`'s `row_number()` orders by `path`, and the empty array sorts first. That is a
    derivation, so the query does not rely on it — it takes the row whose address is the
    document's own minimum `sid`, and `--tree-roundtrip` is what proves the choice was right
    by reconstructing `dec` from it.
    """
    return (
        "SELECT r.core_id, c.relpath, d.id AS root, c.dec "
        "FROM dec_ref r JOIN dec_node d ON d.head = r.head AND d.c1 = r.c1 AND d.c2 = r.c2 "
        "JOIN core_decoded c ON c.core_id = r.core_id "
        "WHERE r.sid = 1 AND r.kind = 0 AND r.ord = (SELECT min(r2.ord) FROM dec_ref r2 "
        "WHERE r2.core_id = r.core_id AND r2.sid = 1 AND r2.kind = 0) "
        "AND (%s::text IS NULL OR r.core_id = %s::text) ORDER BY c.relpath",
        (core_id, core_id),
    )


def reach_sql(root):
    """`(sql, params)` — every node reachable from `root`, with the LEAF payloads resolved.

    ⚑⚑ THE RECURSIVE TERM NAMES THE CTE ONCE — the same grammar rule the walk obeys, and the
    same fold: both child slots come out of ONE `LATERAL (… UNION ALL …)` rather than two
    references to `t`. Written longhand because "recurse on c1 and recurse on c2" is the
    spelling a reader will reach for, and it is a parse error.

    ⚑ `UNION` AND NOT `UNION ALL`, WHICH IS THE POINT OF AN SPPF. A shared node is reached from
    many parents; `UNION ALL` would return it once per path and turn a DAG with 4,966-scale
    sharing back into the exponentially larger tree the sharing exists to avoid.
    """
    return (
        "WITH RECURSIVE t(id) AS ("
        "SELECT %s::bigint UNION "
        "SELECT c.k FROM t JOIN dec_node d ON d.id = t.id "
        "CROSS JOIN LATERAL (SELECT d.c1 WHERE d.head <> 0 AND d.c1 <> 0 "
        "UNION ALL SELECT d.c2 WHERE d.c2 <> 0) AS c(k)) "
        "SELECT d.id, d.head, d.c1, d.c2, s.v FROM t JOIN dec_node d ON d.id = t.id "
        "LEFT JOIN dec_scalar s ON d.head = 0 AND s.id = d.c1",
        (root,),
    )
