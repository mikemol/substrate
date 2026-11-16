# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""THE schema declaration: one SQLAlchemy model, DDL emitted per dialect.

⚑⚑ SPLIT OUT OF `schema.py` 2026-08-11, AND THE SEAM IS A DEPENDENCY DIRECTION, NOT A
SIZE CUT. `schema.py` had grown to 2,102 code lines — past the point where the whole
region can be read before editing it, which is not a tidiness complaint but a MEASURED
defect class: retiring one function from it took four edits, two of which repaired
damage the previous edit caused (a note placed past a docstring's closing quotes, and
an assertion left referring to the retired name). Each edit was locally reasonable;
none could see the region whole.

⚑ WHY *THIS* CUT. Everything here is DECLARATION — it names tables, indexes, views and
tiers, and compiles them to DDL. It calls nothing in `schema.py`; `schema.py` calls it.
So the arrow points one way and the split needs no import cycle, no shim and no
deferred import: the two `import store` calls inside `ddl`/`_tier` were already
deferred (see `_cli_connect`'s note on why module-scope `store` is not available), and
they stay exactly as they were.

⚑ THE OTHER HALF — the row/execute helpers, the queue tier, the CLI — is NOT here, and
that is deliberate rather than unfinished. `_selftest` reads its OWN module's source
(`getsource(sys.modules[__name__])`) to police `_store.connect(` bypasses and to check
the `--holes` CLI block; moving those functions to a sibling would make both guards
scan a file that no longer contains what they police and pass by measuring NOTHING.
That is the same failure they were written to catch, so the cut stops where the
introspection begins. See `schema.py`'s own note at the guard.

`schema.py` re-exports every name defined here, so no consumer changes.

⚑ WHY THIS EXISTS (user, 2026-08-06: *"Doesn't SQLAlchemy give us a way to synthesize
DDL from spec?"*). It does — `CreateTable(t).compile(dialect=…)` — and reaching for it
retires a fork before it is written. The alternative was a second hand-written DDL
string beside `sppf_db.EVENT_SCHEMA`/`SPPF_SCHEMA`, i.e. the same schema spelled twice,
free to drift, with nothing able to check the agreement. That is the defect this
session already paid for at three other layers: eight `CATALOG_DB` derivations, two
dialect spellings, four connection styles.

⚑ AND THE EXISTING DECLARATION WAS NOT USABLE AS ONE. `query_defs._T` builds every
table as `Column(c, String)` — a QUERY shim, not a schema. It carries no types, no
primary keys, no indexes, no NOT NULL, and it mixes base tables with VIEWS (`node`,
`unit`, `structs`) and with `sqlite_master`. Emitting DDL from that would have produced
a schema that is silently wrong: every INTEGER a TEXT, every key absent. So the facts
are declared HERE, read off the DDL that actually built the store, and `query_defs`
keeps its shim for querying.

⚑ WHAT THIS BUYS BEYOND PORTABILITY: the types become CHECKABLE. SQLite accepts
`INTEGER` as a suggestion — it will store a string in an INT column without complaint —
so `mtime`, `ord`, `level`, `copy` have never been enforced. PostgreSQL refuses. That
is a migration RISK worth stating rather than discovering: an ingest that has been
writing a str into `ord` succeeds today and fails on the port, which is the schema
finding something real rather than the port being broken.
"""

import sys

# ⚑ `Sequence` / `CreateSequence` WERE IMPORTED FOR THE SURROGATE-ID SEQUENCES AND WENT WITH
# THEM (⑸, 2026-08-12). A content-DERIVED id needs no engine state, so the emitter needs no
# sequence construct; leaving the import would advertise a capability the declaration no
# longer has, which is the same defect as a relocation note naming a function that did not move.
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Text,
    Integer,
    BigInteger,
    SmallInteger,
    Index,
    Identity,
    PrimaryKeyConstraint,
    select,
    func,
    exists,
    literal,
    and_,
    case,
    text,
    union_all,
)

# ⚑ `JSONB` IS THE POSTGRES DIALECT TYPE, NOT THE GENERIC `sqlalchemy.JSON`, AND THAT IS
# NOW A FREE CHOICE RATHER THAN A PORTABILITY COST (⟡ladder-1, 2026-08-12). `schema_decl`'s
# `obs_node.ch` note argues against `ARRAY` because *"`ARRAY` has no sqlite rendering, so
# declaring it would make this tier postgres-only and break every fixture that builds the
# schema on `:memory:`"*. That constraint EXPIRED with the sqlite backend (⓺, 2026-08-11):
# `store.backend()` now REFUSES anything but postgres, `store.dialect()` returns the
# postgresql dialect unconditionally, and `sandbox_fixture` builds every suite fixture in a
# postgres SCHEMA rather than an in-memory file. Generic `JSON` would render `JSON` on
# postgres — the type with no equality operator (measured below), which is exactly the one
# the rung's WHERE clause cannot use.
from sqlalchemy.dialects.postgresql import JSONB, aggregate_order_by
from sqlalchemy.schema import CreateTable, CreateIndex
# ── `from sqlalchemy.sql import table` / `from sqlalchemy_views import CreateView`
# ── DELETED 2026-08-12 (⟡view-purge). They existed for ONE call each, both inside
# `_view_ddl_named`: `table(name)` built the bare target a `CreateView` needed, and
# `CreateView` MATERIALISED a Core selectable into a `CREATE OR REPLACE VIEW` statement.
# With the emitter no longer emitting views neither construct has a caller, and leaving
# either would advertise a capability the declaration no longer has — the rule this file
# already applies to `Sequence`/`CreateSequence` two lines up.

MD = MetaData()


def _t(name, *cols, pk=None):
    """A base table. `pk` names the primary-key column(s); everything else is nullable.

    ⚑ TYPES COME FROM THE DDL THAT BUILT THE STORE (`sppf_db.EVENT_SCHEMA` /
    `SPPF_SCHEMA`), not from what a column's NAME suggests. `ord` is INT there and
    `root_lid` is INT; `level` is INTEGER; `mtime` is INTEGER. Reading them off the
    strings is the only way this declaration is not a fresh invention.
    """
    t = Table(name, MD, *cols)
    if pk is not None:
        t.append_constraint(PrimaryKeyConstraint(*(pk if isinstance(pk, (list, tuple)) else [pk])))
    return t


# ── the SOURCED tier (⟡ladder-1: the decoded core, WHOLE — below the event tier) ────
#
# ⚑⚑ THIS IS THE OUTPUT OF THE `ε → sourced` BOUNDARY, AND THAT IS WHY IT IS *BELOW* THE
# EVENT TIER RATHER THAN BESIDE IT. `lifecycle.boundary(0)` is `(ε, sourced)` — *"the
# filesystem edge, where the ingest draws"* — and until now that boundary had no relation at
# all: `write_events` derived source-liveness every run and DISCARDED it into local variables
# (`lifecycle`'s own note: *"`sourced` IS THE STAGE THE STORE DID NOT MODEL"*). The event tier
# is what a SHREDDER makes of this row; this row is the material it shreds.
#
# ⚑ THE TIER IS NAMED FOR THE STAGE IT FEEDS, NOT FOR ITS POSITION. `lifecycle.boundary_index`
# records why in full: *"`3` was a position standing in for 'the boundary retire spans'.
# Positions renumber; identities do not."* A tier called `tier_minus_one` renumbers the moment
# something is put below it; `sourced` moves only under a rename or a deletion, and both of
# those should be loud.
#
# ⚑⚑ EVERY COLUMN THE CURRENT INGEST NEEDS IS HERE **AS A FACT, NOT AS A REFERENCE UPWARD**,
# and that asymmetry is the whole reason `relpath` is a column. `_insert_decoded` recovers the
# core's path with `cid = tid(relpath)` — i.e. from `terms`, which lives in the tier ABOVE.
# A lower tier that needs a higher one to be readable INVERTS the reconstruction arrow the
# tier exists to provide (*"each tier must be reconstructible losslessly by the tiers it
# replaces"*), so the path is stored here rather than joined for.
#
# ⚑ AND `core_id` IS THE DERIVED COLUMN, NOT A SECOND COPY OF THE PATH — the distinction ⓟ
# got wrong in the other direction. `core_fp.path` was deleted because it duplicated
# `terms.text` WITHIN ONE TIER; here the duplication runs the other way: `relpath` is the
# fact and `core_id = _content_addr._addr(relpath)` is a PURE FUNCTION of it (see
# `schema_diag.intern`: *"NO SELECT, NO nextval, NO RE-READ — THE ID IS A PURE FUNCTION OF
# THE TEXT"*). It is carried because it is the join key every relation above names, and the
# agreement `_addr(relpath) == core_id_for(relpath, con)` is CHECKED by a case rather than
# assumed — a derived column with no check is how two authorities drift.
#
# ⚑⚑ `JSONB` AND NOT `JSON`, DECIDED BY MEASUREMENT (⟡ladder-1, 2026-08-12). 60 real cores
# sampled by stride across the corpus, 38 decodable, 1,540,854 node records round-tripped
# through a live postgres sandbox in BOTH types:
#
#     readback == json.loads(json.dumps(dec))   jsonb 38/38 · json 38/38   (0 mismatches)
#     stored ::text identical to input text     jsonb NO (keys reordered) · json YES
#     `IS DISTINCT FROM` available              jsonb YES · json **NO**
#       → `UndefinedFunction: operator does not exist: json = json`
#     on-disk size, 38 cores                    jsonb 23,986,176 B · json 23,920,640 B
#
# ⚑ SO BOTH ARE LOSSLESS AS A *VALUE* AND ONLY `json` IS LOSSLESS AS *TEXT* — and the text
# half buys nothing here. There is no downstream encoding to stay compatible with (user,
# 2026-08-12: *"I don't care about the b64 text. It doesn't matter. All the existing db
# structure is cognitive debt."*), so the deciding property is the one that changes what can
# be WRITTEN: `json` has no equality operator, so the content-conditioned rung
# (`… DO UPDATE … WHERE row IS DISTINCT FROM EXCLUDED`) is not expressible over it at all.
# A ladder rung's predicate lives in its WHERE clause; a type that cannot be compared cannot
# carry one. jsonb costs 0.27% more on disk for that.
#
# ⚑⚑ THE ONE FIDELITY LOSS IS AT THE **JSON** LEVEL AND IS IDENTICAL FOR BOTH TYPES, so it is
# not a reason to prefer either. `dec["nodes"]` is keyed by **int**; JSON object keys are
# strings, so `json.loads(json.dumps(dec)) != dec` before postgres is involved at all.
# MEASURED: **0 of 1,540,854** node records whose key differs from that record's own `id`
# field, so the int keying is recoverable from the row without a codec assumption. It is NOT
# repaired here by a heuristic re-key (a rule like *"re-int any object whose keys all parse as
# integers"* would silently rewrite a genuine string key `"0"`); it is measured, named, and
# left to the rung that replaces `_insert_decoded` — which can key on `id` and never form the
# int-keyed dict in the first place.
#
# ⚑ NO SECONDARY INDEX, DELIBERATELY. The PK is the only access path any rung has needed so
# far, and this tier DRAINS: an index over a relation whose rows are meant to leave costs
# maintenance on every insert and delete for a read nothing does yet. `ref`'s own note is the
# precedent for what a derived, disposable access path is allowed to cost.
core_decoded = _t(
    "core_decoded",
    Column("core_id", Text),
    Column("relpath", Text, nullable=False),
    Column("mtime", BigInteger),
    Column("producer", Text, nullable=False, server_default="agdai"),
    Column("dec", JSONB, nullable=False),
    pk="core_id",
)

# ── the VOCAB tier (⟡ladder-2b: every SCALAR in `dec`, keys and values alike) ───────
#
# ⚑⚑ THE COLUMN IS `v JSONB`, NOT `s TEXT`, AND THAT IS A CORRECTION (user, 2026-08-12:
# *"That calls for a VARIANT type, not a simple exclusion."*). ⟡ladder-2 interned only the
# jsonb STRINGS and EXCLUDED numbers, booleans and JSON nulls, reasoning that coercing them
# with `#>> '{}'` would MANUFACTURE an identity the documents do not have — the integer `0`
# and the string `"0"` collapsing into one row. That reasoning is CORRECT ABOUT THE HAZARD and
# WRONG ABOUT THE REMEDY: the answer to "text coercion conflates two kinds" is a TAG, not an
# omission. Kept verbatim as residue because the hazard it names is exactly what the tag now
# prevents, and because the exclusion's second argument (*"an integer is ALREADY a number, so a
# number/string mapping buys it nothing"*) is what made the omission look self-justifying:
#
#     *"coercing them would MANUFACTURE an identity the documents do not have. The integer `0`
#     and the string `\"0\"` are different values in `dec`, and `dec_string` cannot distinguish
#     them once both are text. That is precisely the collapse `sppf_decode.json_value`'s note
#     refuses to make in the other direction (\"a rule like re-key any object whose keys all
#     parse as integers would silently rewrite a genuine string key `0`\"), and this is the
#     same trap facing the same way."*
#
# ⚑⚑ AND THE EXCLUSION WAS NOT MERELY INCOMPLETE — IT BROKE THE NEXT RUNG. Step 4 reconstructs
# the document as a CNF-2 binary tree in which a LEAF's node id IS its value id. Numbers are
# 1,649,947 of 4,126,675 values walked (~40%): excluded, two fifths of the tree's leaves have
# no identity and cannot be addressed at all. A vocabulary that cannot name a leaf is not a
# vocabulary for this tree.
#
# ⚑⚑ `jsonb` IS ALREADY THE VARIANT TYPE, WHICH IS WHY THIS IS A SMALL CHANGE AND NOT NEW
# MECHANISM. A jsonb scalar CARRIES ITS OWN TYPE TAG: `'0'::jsonb` and `'\"0\"'::jsonb` are
# distinct values (MEASURED: `=` is False), `jsonb_typeof` reads the tag, and `UNIQUE(v)` is
# expressible **precisely because jsonb has btree equality** — the same property that decided
# `jsonb` over `json` for `core_decoded.dec` one tier down (`json` has no equality operator, so
# it could not carry this rung's predicate at all). The variant was in the store the whole time;
# ⟡ladder-2 projected it away with `#>> '{}'` and then legislated around the projection.
#
# ⚑ A JSON NULL IS A VALUE AND `nullable=False` ADMITS IT — MEASURED, not assumed:
# `'null'::jsonb IS NULL` is **False**. `'null'::jsonb` is a real jsonb datum whose
# `jsonb_typeof` is `null`; SQL NULL is the absence of a datum. There were 497 of them in the
# corpus and every one is interned. The two spellings differ by one word in English and by
# everything in what they denote, which is why this is written down rather than reasoned about
# again later.
#
# ⚑ THE NAME IS `dec_scalar` AND NOT `dec_value`, WHICH WAS THE OBVIOUS CHOICE AND IS WORSE ON
# BOTH AXES. (1) PRECISION: the relation holds exactly the jsonb values that are NOT `object`
# and NOT `array` — postgres's own word for that class is *scalar* (`jsonb_typeof`'s four
# non-compound answers), while RFC 8259 uses "value" for objects and arrays TOO, so `dec_value`
# would name a superset of what is here and would go on being wrong once step 4 gives interior
# nodes their ids from the TREE rather than from this table. (2) THE KEY/VALUE READING: the
# whole design of this relation is that a key and a value are ONE row, and *value* is half of
# the pair *key or value* — naming the table after that half re-introduces in the identifier
# exactly the distinction the schema went to the trouble of quotienting away. `dec_` keeps the
# provenance prefix the tier already uses (`core_decoded.dec` is what is walked), so the name
# reads as "the scalars of `dec`", which is what it is.
#
# ⚑⚑ ONE VOCABULARY, NOT TWO, AND THE ABSENCE OF A `kind` COLUMN IS THE DESIGN (user,
# 2026-08-12). Steps 2 and 3 of moving the store's work into SQL were posed as "the KEYS of the
# jsonb structure" and "the VALUES … honestly, into the same strings table". They are ONE rung
# because **position is a property of the STRUCTURE, not of the string**: a string appearing as
# a field name in one document and as a constructor name in another is ONE row, because it is
# one string. Measured key/value vocabulary overlap: 100% — which is not a finding, it is what
# a table with no notion of key-ness means. A `kind` column, or a partitioned id space, would
# re-introduce exactly the distinction this relation exists to have already quotiented.
#
# ⚑⚑ `id` IS AN AUTONUMBER — `GENERATED ALWAYS AS IDENTITY` — AND THAT IS A CORRECTION, NOT A
# DEFAULT (user, 2026-08-12: *"There is allocation… but only when inserting into the strings
# table. But autonumber is sufficient."*). The ⑸ race that produced 21,840 rows resolving to
# another term's text was `max(term_id)+1` computed **client-side**: two python processes each
# read N, each minted N+1, each inserted different text under one id. The defect was a
# SCRATCHPAD HELD ACROSS STATEMENTS, not allocation as such. `nextval` inside an
# `INSERT … SELECT` has no client and holds nothing — the engine assigns per row, atomically,
# inside one statement, so two concurrent runs cannot receive the same number.
#
# ⚑ AND IT NEEDS NO RECONCILIATION BECAUSE NOTHING OUTSIDE THE ENGINE EVER PREDICTS AN id. The
# argument against a sequence is that two writers interning the same value allocate two
# numbers, one loses on `UNIQUE(v)`, and the loser must re-read to find the winner's id. That is
# true only when a CLIENT wants the id back. A rung JOINS `dec_scalar` on `v` to obtain `id` —
# it never computes one, never holds one, and so never has one to discard. Content-derivation
# (`_content_addr._addr`) was right for `terms` precisely because there WAS a scratchpad that
# had to predict the id without asking; there is no scratchpad in a rung.
#
# ⚑ `always=True`, NOT `always=False`, AND THE STRONGER FORM IS THE POINT. `GENERATED ALWAYS`
# makes postgres REFUSE a client-supplied value outright (`cannot insert a non-DEFAULT value
# into column "id"`), which is `obs.seq`'s retired rule — *"STORE-ASSIGNED, NEVER
# CLIENT-ASSIGNED … the rule survives the column: any future engine-owned column owes it"* —
# enforced by the engine rather than by everyone remembering it.
#
# ⚑ `nullable=False` IS LOAD-BEARING AND ITS ABSENCE ONCE TOOK THE STORE DOWN. `obs.seq`'s
# residue: *"`Identity` AND `nullable=True` ARE CONTRADICTORY IN EMITTED DDL … it emits
# `seq BIGINT GENERATED BY DEFAULT AS IDENTITY NULL` — a syntax error — and it took the store
# down mid-flush, after the DROPs and before the recreate."* `_t` leaves every non-pk column
# nullable, so this has to be said here.
#
# ⚑ `UNIQUE(v)` IS THE INTERNING KEY — the `ix_terms_text` role, and the reason ⑸'s
# `path_text` race was possible at all was that the identical structure one level up simply
# LACKED it (*"an interning table that had no interning key"*). It is what makes the rung's
# `ON CONFLICT (v) DO NOTHING` expressible: there has to be a named content arbiter, and the
# SURROGATE is exactly the target that cannot dedupe by content.
#
# ⚑ AND THE ARBITER IS `jsonb`'s OWN EQUALITY, WHICH IS NUMERIC ON NUMBERS — MEASURED, and
# stated because it is the one identity this relation DOES impose: `'1.0'::jsonb = '1'::jsonb`
# is **True**, so `1` and `1.0` are ONE row and the stored rendering is whichever arrived first.
# That is not the text collapse this correction removes (`0` vs `"0"` remain two rows, which is
# the point); it is postgres's number model — jsonb stores a number as `numeric` and trailing
# zeros are not part of a numeric's identity. A corpus emitting both spellings of one quantity
# is therefore quotiented HERE rather than downstream, which is the right place for it, but it
# is an identity and so it is named rather than left to be rediscovered.
#
# ⚑ NOT A SECOND `terms`. `terms`/`path_text` are the EVENT tier's interners and are left
# running untouched (user, 2026-08-12: *"All the existing db structure is cognitive debt."*).
# This relation is additive, is populated by nothing that writes those two, and shares no id
# space with them — the ids here are small dense integers and theirs are 11-character derived
# handles, so a value from one cannot be mistaken for a value from the other.
dec_scalar = _t(
    "dec_scalar",
    Column("id", BigInteger, Identity(always=True), nullable=False),
    Column("v", JSONB, nullable=False),
    pk="id",
)

# ── the TREE tier (⟡ladder-4: `dec` as a CNF-2 binary tree, right spine) ────────────
#
# ⚑⚑ FOUR PRODUCTIONS AND NO SPINE CONSTRUCTOR, WHICH IS A CORRECTION TO THE PLAN THIS RUNG
# WAS SPECIFIED FROM. The design note proposed `OBJ · ARR · MEMBER · CONS`, with the OBJ/ARR
# WRAPPER existing to *"distinguish a complete object from a tail"*. The decision that
# unblocked the step says the opposite, and says it about the binariser this tree already
# owns (user, 2026-08-13; `jea_pyalg.PyDivStr.wedge`): **the tail is re-interned under the
# PARENT's head**, so a quoted tail and a standalone value of equal content are ONE node.
# A wrapper whose only job is to keep those two apart is a wrapper against the decision.
#
#     0 LEAF(s, 0)        s = dec_scalar.id                     a jsonb scalar
#     1 OBJ(m, tail)      m = a MEMBER node                     tail = members 2..n, 0 if n = 1
#     2 ARR(e, tail)      e = a value node                      tail = elements 2..n, 0 if n = 1
#     3 MEMBER(k, v)      k = LEAF of the key, v = any value    arity-2 in the GRAMMAR
#
# ⚑ SO `{}` IS `OBJ(0,0)` AND `[]` IS `ARR(0,0)` — the empty-object/empty-array distinction
# survives WITHOUT the wrapper, because the head is already carrying it. MEASURED: five of the
# 43 documents are literally `{"nodes": {}, "defmarks": []}`, so both empties occur in one real
# document and the distinction is exercised by the corpus rather than only by a fixture.
#
# ⚑ MEMBER IS **NOT** BINARISED, AND THAT IS THE ONE PLACE `wedge` IS NOT APPLIED. `wedge` is
# the BIN step of CNF and BIN applies to a VARIADIC production; `MEMBER` is arity-2 in the
# grammar itself, so there is nothing to fold. Handing a 2-child MEMBER to `wedge` would spine
# it into `MEMBER(k, MEMBER(v, 0))` — one extra node per member and a value buried one level
# deeper — which is why the rung wedges `OBJ`/`ARR` only.
#
# ⚑⚑ `head` IS A CONSTRUCT TAG AND **NOT** A `dec_scalar` id. Interning the word `"OBJ"` would
# manufacture vocabulary no document contains — ⟡ladder-2b's defect, facing the other way.
#
# ⚑⚑ THE KEY IS `(head, c1, c2)` AND THE `id` IS THE THING THAT MAKES IT BOUNDED. Identity as
# a tuple, with a compound child holding its child's KEY, makes a node's key encode its whole
# subtree: MEASURED on this corpus, the median document's root key is ≈49k ids and the largest
# ≈577k, against postgres's 2704-byte btree entry limit — so the PK is not creatable for any
# document here. The fix is the mechanism `dec_scalar` already runs: an ENGINE-ASSIGNED
# autonumber beside a unique CONTENT key. `c1`/`c2` hold that 8-byte handle, the PK stays the
# content tuple, and `ON CONFLICT DO NOTHING` still arbitrates on content. No digest, no hash,
# no collision question.
#
# ⚑ AND THE ALTERNATIVE — interning the QUOTE `jsonb_build_array(head,c1,c2)` into `dec_scalar`
# and referencing it — WAS THE PLAN'S, IS BOUNDED TOO, AND IS REJECTED FOR TWO MEASURED
# REASONS. (1) It puts a COMPOUND into the scalar vocabulary: `jsonb_typeof` over `dec_scalar`
# is `{string 116,512 · number 115,268 · boolean 2 · null 1}` and **zero arrays**, so the
# relation's own claim — *"the scalars of `dec`"* — would stop being true and `--vocab-census`
# would count rows no document contains. ⟡ladder-2b removed a `kind` column to keep that
# population honest; the quote reopens it from the other side. (2) It makes a round write TWO
# tables, and postgres does not specify the execution order of data-modifying CTEs — so two
# writers could acquire `dec_scalar` and `dec_node` in opposite orders. That is a 40P01
# designed IN, in a tier whose concurrency claim is the point.
#
# ⚑ THE ONE TYPE PUN, NAMED RATHER THAN LEFT TO BE DISCOVERED: in `LEAF(s, 0)` the `c1` slot
# holds a **`dec_scalar.id`**; under every other head `c1`/`c2` hold a **`dec_node.id`**, with
# `0` meaning "no child". The HEAD is the tag, exactly as in CNF a terminal is a symbol of the
# grammar. This is what keeps the child columns ONE reference space — every child of every
# non-LEAF node is a node id, with no per-slot type column widening the key.
#
# ⚑ `0` IS THE NULLARY CHILD AND IS PK-LEGAL BECAUSE IT IS NOT NULL. Identity starts at 1, so
# no node can ever be numbered 0 and the spelling is unambiguous — `schema_diag`'s rule that
# *"things which might be null are not part of the pkey"* is honoured by making the absence a
# VALUE rather than a NULL.
dec_node = _t(
    "dec_node",
    Column("head", SmallInteger, nullable=False),
    Column("c1", BigInteger, nullable=False),
    Column("c2", BigInteger, nullable=False),
    Column("id", BigInteger, Identity(always=True), nullable=False),
    pk=["head", "c1", "c2"],
)

# ── the TREE tier's HEADER (⟡ladder-retire: what makes `tree` reconstruct `sourced`) ─
#
# ⚑⚑ WITHOUT THIS RELATION THE `sourced` TIER IS NOT RETIRABLE AT ALL, AND THAT IS A
# STRUCTURAL FINDING RATHER THAN A CONVENIENCE. `dec_node` holds the CONTENT of every
# document and nothing else: it cannot say which node is a document's root, and it does
# not carry `relpath`, `mtime` or `producer`. `roots_sql` answered "which node is this
# document's root" by joining `dec_ref` (the DISPOSABLE staging tier) to `core_decoded`
# (the tier being retired) — so both of its inputs vanish in the drain, and after the
# drain the tree would hold every byte of the corpus with no way to NAME a document.
#
# ⚑ THAT IS EXACTLY THE ARROW `core_decoded`'s OWN NOTE FORBIDS, FACING THE OTHER WAY:
# *"A lower tier that needs a higher one to be readable INVERTS the reconstruction arrow
# the tier exists to provide."* Here the HIGHER tier needed the lower one to be readable.
# The model's *"each tier must be reconstructible losslessly by the tiers it replaces"*
# is a claim about the WHOLE row, and four of `core_decoded`'s five columns are not
# derivable from `dec_node` by any means. So the header is not an index over the tree —
# it is the part of tier B+2 that had not been built yet, and building it is what the
# `+2` requires before a single row of `sourced` may go.
#
# ⚑ `root` IS A `dec_node.id` AND NOT A CONTENT TRIPLE. The triple would be equally
# durable and would cost three columns and three-column joins everywhere; `id` is the
# 8-byte handle the tree already assigns and `ix_decnode_id` already indexes. The
# distinction that matters is that `root` is ENGINE-ASSIGNED and stable, never derived
# client-side — `dec_node`'s own rule, inherited.
#
# ⚑ AND THIS ROW IS WRITTEN ONLY UNDER THE RECONSTRUCTION PREDICATE. `dec_drain.root_sql`
# inserts a header exactly when the rebuilt value of that root IS NOT DISTINCT FROM the
# live `core_decoded.dec` — the same `WHERE` clause the retire DELETE carries. A header
# present is therefore a claim that WAS true at insert time; the DELETE re-asks it, because
# build and delete are separate runs and *"a build-time-only check is check-then-act across
# the largest possible window"*.
dec_root = _t(
    "dec_root",
    Column("core_id", Text, nullable=False),
    Column("relpath", Text, nullable=False),
    Column("mtime", BigInteger),
    Column("producer", Text, nullable=False, server_default="agdai"),
    Column("root", BigInteger, nullable=False),
    pk="core_id",
)

# ── the VALUE MEMO (⟡ladder-retire: the reconstruction's frontier, derived+disposable) ─
#
# ⚑⚑ THIS EXISTS BECAUSE A RECURSIVE CTE MAY NOT AGGREGATE IN ITS RECURSIVE TERM, WHICH IS
# THE DUAL OF THE REASON `dec_ref` EXISTS. The build needed a memo because *"postgres cannot
# see a data-modifying CTE's effect on its target within the same statement"*; the
# reconstruction needs one because the value of a compound is `jsonb_object_agg` over its
# members and postgres refuses an aggregate in a recursive term. Both are the same
# limitation seen from opposite ends of one map, and both are answered by a memo relation
# plus a caller-held fixpoint.
#
# ⚑⚑ THE ROUND COUNT IS THE **JSON NESTING DEPTH**, NOT THE SPINE LENGTH — which is why the
# reverse direction is cheap where the forward one cost 115,294 rounds. A spine of length N
# is walked by ONE recursive CTE and aggregated by the OUTER query, so a 115,268-member
# object is one statement; only a compound whose MEMBER is itself a compound must wait for
# another round. MEASURED on this corpus: `max_depth = 4`.
#
# ⚑ IT HOLDS THE INTERIOR ONLY — every compound that is a MEMBER's value or an ARR cell's
# element — and NOT the document roots. The roots are aggregated by the shadow view itself,
# so the delete-time predicate COMPUTES the top level from `dec_node` rather than reading a
# stored answer, and the memo never has to hold a second copy of a whole document.
#
# ⚑ A MISSING MEMO ROW CAN ONLY CAUSE A **REFUSAL**, NEVER A WRONG DRAIN, and that asymmetry
# is what makes the memo safe to treat as a cache. An unresolved child makes `ok = 0`, which
# makes `nok <> n`, which drops the parent from the reconstruction, which makes the shadow
# hold NO row for that document, which makes `IS NOT DISTINCT FROM` false and HOLDS it.
#
# ⚑ THE RESIDUE, NAMED RATHER THAN ARGUED AWAY: a memo row is trusted as a function of
# `dec_node`, which is insert-only under every rung in this ladder — so a row can go stale
# only if something DELETES from `dec_node`, which nothing here does. `--drain-census`
# reports memo rows whose node is absent; that is the observable, not a proof.
# ⚑ `autoincrement=False` IS LOAD-BEARING AND ITS ABSENCE RENDERED `BIGSERIAL` — caught by
# reading the emitted DDL, not by a case. SQLAlchemy makes any single-column integer primary
# key auto-incrementing unless told otherwise, so this column would have acquired a SEQUENCE
# and a default: the memo's `id` is a `dec_node.id` supplied by the rung, and an engine-assigned
# default would have silently renumbered every row that was inserted without one. The tier's
# rule is the inverse of `dec_node`'s and both must be spelled: there the id is
# ENGINE-assigned and a client value is REFUSED; here it is a FOREIGN handle and the engine
# must not invent one.
dec_val = _t(
    "dec_val",
    Column("id", BigInteger, primary_key=True, autoincrement=False, nullable=False),
    Column("v", JSONB, nullable=False),
)

# ── the TREE STAGING tier (⟡ladder-4: the materialised frontier) ─────────────────────
#
# ⚑⚑ TWO RELATIONS, BOTH DERIVED AND DISPOSABLE, FOR THE REASON `ref` AND `obs_node` HAVE
# THEIR OWN TIERS: every row is recoverable by re-running the build, and nothing reconstructs
# a document FROM them. `dec_node` alone is the tier's product.
#
# ⚑⚑ THE STAGING IS WHAT KEEPS THE COST LINEAR, AND ITS ABSENCE IS THE PROHIBITIVE MISTAKE.
# Cell k needs cell k+1's id, so a spine of length N is N SEQUENTIAL rounds and N is 115,268
# here. Re-walking `dec` each round would be O(values × rounds) = O(4.1M × 115,268); reading a
# `rnd`-indexed slice of a skeleton built ONCE is O(cells) total, with the round COUNT — not
# the work — equal to the longest spine.
#
# ⚑⚑ PATH-ADDRESSING IS SAFE **HERE** AND WOULD BE FATAL IN `dec_node`, and conflating the two
# is what made this look impossible. The design note rejected *"path-addressed intermediates
# `(core_id, path, k)`"* because they *"destroy content sharing — every node above a sequence
# becomes document-local, which is the SPPF property the tier exists for."* That is true of the
# OUTPUT and false of the WORK LIST: `dec_stage` is document-local by construction and
# `dec_node` is content-keyed, so the sharing lives entirely in the relation that is supposed
# to carry it.
#
# ⚑ `rnd` IS A SINGLE INTEGER AND IS COMPUTED ONCE, NOT DERIVED PER ROUND. It is
# `dense_rank() OVER (ORDER BY depth DESC, t)` where `t` is 0 for a MEMBER and the ordinal
# FROM THE END for a spine cell, with 0 reserved for the rows that have no children at all
# (leaves and empty compounds). The ordering is a topological one, checked exhaustively over
# the four productions: a cell at `(d, rev)` needs its MEMBER at `(d, 0)` and its tail at
# `(d, rev-1)`; a MEMBER at `(d, 0)` needs a value at depth `d+1`, which `depth DESC` has
# already placed earlier. So round `r` may insert every row with `rnd = r` at once.
#
# ⚑ A CHILD SLOT IS AN ADDRESS **XOR** A LEAF **XOR** NIL, spelled as columns rather than as a
# tag: `a*_sid/a*_ord/a*_kind` non-null means "the node at that address"; `l*` non-null means
# "the LEAF node of that scalar"; all-null means the nullary child `0`. The one exception is a
# LEAF row itself, whose `l1` is the scalar id RAW — the same rule `dec_node` states, mirrored
# so the two cannot drift.
dec_stage = _t(
    "dec_stage",
    Column("core_id", Text, nullable=False),
    Column("sid", Integer, nullable=False),
    Column("ord", BigInteger, nullable=False),
    Column("kind", SmallInteger, nullable=False),
    Column("rnd", Integer, nullable=False),
    Column("head", SmallInteger, nullable=False),
    Column("a1_sid", Integer),
    Column("a1_ord", BigInteger),
    Column("a1_kind", SmallInteger),
    Column("l1", BigInteger),
    Column("a2_sid", Integer),
    Column("a2_ord", BigInteger),
    Column("a2_kind", SmallInteger),
    Column("l2", BigInteger),
    pk=["core_id", "sid", "ord", "kind"],
)

# ⚑⚑ THE ADDRESS→NODE MEMO, AND IT STORES THE **CONTENT** `(head, c1, c2)` RATHER THAN THE
# `id` FOR ONE MEASURED REASON: postgres cannot see a data-modifying CTE's effect on its target
# within the same statement, so a round that inserted into `dec_node` could only learn the new
# `id` through `RETURNING` — which yields NOTHING for a row another writer inserted between my
# snapshot and my statement. Storing the content instead means round `r+1` finds the id with an
# ordinary PK lookup against a FRESH snapshot, after round `r` committed. No `RETURNING`, no
# race, and no coordination added to get there.
#
# ⚑ AND IT IS INSERT-ONLY, WHICH IS WHY IT IS A SECOND RELATION RATHER THAN A COLUMN ON
# `dec_stage`. Filling the memo by `UPDATE` would take exclusive row locks in a plan-dependent
# order, so two writers on one document could acquire the same rows in opposite orders — the
# cycle this tier must not construct. `INSERT … ON CONFLICT DO NOTHING` under a declared
# ORDER BY is the shape ⟡ladder-2b already measured at 8 concurrent writers with no 40P01.
dec_ref = _t(
    "dec_ref",
    Column("core_id", Text, nullable=False),
    Column("sid", Integer, nullable=False),
    Column("ord", BigInteger, nullable=False),
    Column("kind", SmallInteger, nullable=False),
    Column("head", SmallInteger, nullable=False),
    Column("c1", BigInteger, nullable=False),
    Column("c2", BigInteger, nullable=False),
    pk=["core_id", "sid", "ord", "kind"],
)

# ── the EVENT tier (append-only source of truth) ────────────────────────────────────
terms = _t("terms", Column("term_id", Text), Column("text", Text), pk="term_id")
path_seg = _t(
    "path_seg", Column("path_id", Text), Column("ord", Integer), Column("seg_term_id", Text)
)
event = _t(
    "event",
    Column("ekey", Text),
    Column("ctor_id", Text),
    Column("qname_pid", Text),
    Column("idx", Integer),
    Column("lit_id", Text),
    pk="ekey",
)
# ── `obs.seq` — THE POSITION — DELETED 2026-08-12. The queue tier's last column. ────────────
#
#     Column("seq", BigInteger, Identity(always=False), nullable=False)
#
# ⚑⚑ IT WENT BECAUSE ITS ONLY CONSUMERS WERE THE QUEUE'S OWN. `seq` existed to answer "has
# every registered reader passed this row?" — retain-until-consumed. Reconstruct-on-demand asks
# instead "can the durable tier rebuild this core?", which `query_defs.q_drainable_res` answers
# PER CORE with no position at all. Once `consumer` went (2026-08-12, step 2) the column's
# readers were: `hwm()` (measured **1 def, 0 calls** — already dead), `q_drainable`'s `below`
# conjunct, `drained()`'s `min(seq) > 1`, and a `lifecycle_census` CASE arm that could never
# fire. None of them is a fact about an observation.
#
# ⚑ THE NOTES IT CARRIED, KEPT BECAUSE THEY ARE MEASUREMENTS AND ONE IS A LIVE OUTAGE:
#
# *"`seq` ORDERS OBSERVATIONS, NOT EVENTS. `event.ekey` is a content-addressed hash:
# deliberately unordered, so shared subtrees dedupe across cores. A sequence on `event` would
# either break that dedup (a re-emitted ekey needing a new number) or be meaningless."* — still
# true of `event`, and the reason no position was ever added there.
#
# *"STORE-ASSIGNED, NEVER CLIENT-ASSIGNED. A counter maintained by the writer collides or gaps
# under concurrent ingests, and the user's standing instruction is not to assume ingest is
# serial."* — the rule survives the column: any future engine-owned column owes it.
#
# *"`Identity` AND `nullable=True` ARE CONTRADICTORY IN EMITTED DDL, and this only surfaced on
# the first FULL CREATE: the live column was added by `ALTER TABLE` during the queue migration,
# so `CreateTable` had never rendered it. It emits `seq BIGINT GENERATED BY DEFAULT AS IDENTITY
# NULL` — a syntax error — and it took the store down mid-flush, after the DROPs and before the
# recreate."* ⚑ **THE TRANSFERABLE HALF IS THAT A COLUMN REACHED ONLY BY `ALTER` HAS NEVER HAD
# ITS `CREATE` RENDERED**, so the declaration and the live store can disagree indefinitely with
# nothing failing until the one path that exercises both runs at once.
#
# *"`Identity(always=False)` VERIFIED IN THE SANDBOX AGAINST A POPULATED TABLE (1000 rows): the
# ALTER backfills every existing row in physical order (1..1000, none NULL) and the next insert
# continues at 1001. I had predicted an ARBITRARY backfill order and been prepared to accept
# it."* — kept as a positive record of a prediction refuted by measurement.
obs = _t("obs", Column("core_id", Text), Column("local_id", Integer), Column("ekey", Text))
edge = _t(
    "edge",
    Column("core_id", Text),
    Column("plid", Integer),
    Column("ord", Integer),
    Column("clid", Integer),
)
unit_obs = _t(
    "unit_obs",
    Column("core_id", Text),
    Column("unit_id", Text),
    Column("name_pid", Text),
    Column("root_lid", Integer),
    Column("kind_id", Text),
    Column("module_pid", Text),
    Column("copy", Integer),
    Column("level", Integer),
)
unit_member = _t(
    "unit_member",
    Column("core_id", Text),
    Column("unit_id", Text),
    Column("ord", Integer),
    Column("member_name_pid", Text),
    Column("member_unit_id", Text),
)
path_text = _t("path_text", Column("path_id", Text), Column("text", Text), pk="path_id")
# ⚑ `producer` SCOPES THE PRUNE — see sppf_db's core_fp note. NOT NULL with a default
# is load-bearing: a NULL producer would belong to no tier, so `prune` could neither
# claim nor spare it.
# ⚑ THE OTHER 19 Integer COLUMNS WERE AUDITED, NOT ASSUMED. After this overflow I
# enumerated every narrow column and read each against its WRITER, because "the one that
# broke is the only one" is the reasoning that finds the next overflow with another
# failed ingest. They are local ids, ordinals and small counts — `obs.local_id` and
# `edge.plid`/`clid` index nodes WITHIN one core (thousands), `*.ord` is a child
# position, `copy`/`level`/`stab` are near-boolean, `fanin` is a share count. None
# approaches 2.1e9. `mtime` was the outlier because it is a TIMESTAMP, not a count —
# which is the property to check, not the column's name.
#
# ⚑ `mtime` IS BigInteger, NOT Integer — MEASURED as a live ingest failure
# (`NumericValueOutOfRange: integer out of range`, 2026-08-06). It holds
# `os.stat(path).st_mtime_ns`: NANOSECONDS since epoch, ~1.79e18 today. Postgres INTEGER
# is 32-bit (max ~2.1e9), so every row overflows by nine orders of magnitude.
#
# ⚑ AND SQLITE HID IT COMPLETELY. Its INTEGER is a 64-bit affinity, so the same column
# stored the same values for the life of the store without complaint — this is exactly
# the "types become CHECKABLE" risk this declaration was written to expose, arriving on
# the first real ingest. The retired `EVENT_SCHEMA` said `mtime INTEGER` and was RIGHT
# about sqlite; transcribing it as SQLAlchemy `Integer` is what narrowed it to 32 bits.
# ⚑⚑ NO `path` COLUMN HERE, AND ITS BRIEF EXISTENCE IS WORTH RECORDING. Under ⓝ P4 I added
# one, reasoning that a surrogate `core_id` needs a canonicalizer to hold the map back —
# `KEY-ENCODING.md` says exactly that, and the reasoning is sound. The error was that the map
# ALREADY EXISTED: the ingest writes `cid = tid(relpath)`, so a core's id IS the term id of its
# relpath and `terms` already stores that text under that id. The column was a second copy.
#
# ⚑ AND `terms` IS THE CANONICALIZER, WITH `ix_terms_text` AS THE INTERNING KEY. That unique
# index is what makes `core_id_for` idempotent — a re-ingested core resolves to the id it
# already had — which is the property a duplicate column could only shadow, never provide.
core_fp = _t(
    "core_fp",
    Column("core_id", Text),
    Column("mtime", BigInteger),
    Column("producer", Text, nullable=False, server_default="agdai"),
    pk="core_id",
)
# ── the QUEUE tier (⟡wm: LWM/HWM watermarks — POSTGRES ONLY) ────────────────────────
# The event tier is an append-only LOG, and every consumer of it is a CURSOR, not a
# scanner. `event_head` re-read all 155k rows on every projection, and the GC
# (`DELETE FROM event WHERE ekey NOT IN (SELECT ekey FROM obs)`) existed only to stop
# that scan growing without bound — measured at 38 MINUTES on the live store, spilling
# to disk, having modified ZERO rows (`backend_xid` null) before it was cancelled.
#
# ⚑ THE GC WAS SOLVING THE WRONG PROBLEM, AND THE CODE SAID SO. `sppf_db.py:410` carries
# the comment "guard; inert for the projection" — the author had already recorded that
# the delete is not load-bearing. An orphaned event is INERT: no live read can reach it,
# so it costs storage and nothing else. Reclamation therefore needs neither atomicity nor
# synchrony, and "is this row orphaned" stops being a set-membership anti-join over the
# whole table and becomes an INEQUALITY on an ordered column.
#
# ⚑ AND THE HIGH-WATER MARK IS NOT `max(seq)`. A sequence gives monotonic ASSIGNMENT,
# never monotonic COMMIT: two concurrent transactions may take 100 and 101, and 101 may
# commit first — so a consumer that advances past 101 NEVER SEES 100 when it lands. That
# drop is silent (no error, an incomplete projection reporting success), which is the same
# shape as the `dict_row` defect that emptied the unit tier. The HWM is therefore the
# point below which no write transaction is still in flight, read from the engine's own
# snapshot rather than approximated.
#
# ⚑ POSTGRES ONLY, BY DECISION (user, 2026-08-06). sqlite cannot express the in-flight
# floor, and approximating MVCC portably when the engine offers it exactly is the
# rebuild-vs-read failure. The watermark simply DOES NOT EXIST on sqlite — not a degraded
# variant, which would be a second semantics nobody audits.
# ── `consumer` — THE WHOLE TABLE, DELETED 2026-08-12. RETAIN-UNTIL-CONSUMED IS RETIRED. ────
#
# It declared `(name, lwm, xmin_at, updated)` PK `name`: a registry of readers, each with a
# stored position, so a row could be deleted once every registered reader had passed it.
# That is a PROMISE ABOUT THE FUTURE, and it is replaced by a FACT ABOUT THE PRESENT — a core
# may be retired iff the durable tier can rebuild it, `query_defs.q_drainable_res`, checked
# per core in ONE statement. `reclaim` had already stopped consulting this table; what
# remained was self-referential — **`consumer` existed so `--watermark` could print
# `consumer`** — and `sppf_db.converge`, the production loop, is SOURCE-driven
# (`_ingested_relpaths` reads `core_fp`), never cursor-driven.
#
# ⚑ THE `kind` COLUMN WAS DROPPED ONE STEP EARLIER AND ITS RULE OUTLIVES BOTH. It held
# 'cursor' | 'pin' and its note read: *"I nearly made `kind` SUBTRACT FROM THE MIN, which
# would have been the catastrophic reading — seeing `scope_fix:resolver` at 0 with a 6.2M lag,
# I typed it a mis-registered cursor and started excluding non-advancers from `lwm()`."* The
# rule survives the column AND the table: **a label added to explain a number must not become
# an input to it.** The next diagnostic column will need it again.
#
# ⚑ AND THE COLUMN'S REAL DEFECT IS THE TABLE'S DEFECT, ONE LEVEL UP. A 'pin' was a promise
# about future behaviour ("never advances") stored beside a position nothing stopped from
# moving — the state F11 reproduced on demand (`kind='pin' | lwm=177,397`). A stored CURSOR is
# the same shape: a cached answer to "how far has this reader got", free to disagree with the
# data. A per-core licence has no such pair to disagree, which is why it needs no registry.
#
# ⚑ WHAT A FUTURE READER SHOULD NOT REBUILD: `lifecycle.py`'s standing note (*"a cursor, as a
# stateful object, should probably not be reified; it should be derivable"*) is the general
# form and it is kept there verbatim. If a position is ever wanted again it is DERIVED —
# `max(seq) over obs ⋈ obs_node` inside the reader's own transaction — never stored.

# ── the REF index (⟡ref: the resolver's positional reference relation) ──────────────
# ⚑ AN INDEX, NOT A TIER, AND THE DISTINCTION IS THE GOVERNING CONSTRAINT. The product
# `SPPF × fibre` must reconstruct the event set (user, 2026-08-07); this relation is DERIVED
# from that product and reconstructs nothing on its own — it keeps 380 of 74,223 observations
# on a measured core. Draining INTO it would delete the 86% of rows that carry no payload at
# all. It is rebuildable at any time, which is what makes it safe to keep and safe to drop.
#
# ⚑ IT EXISTS TO RETIRE `obs`'s SECOND ROLE. `scope_fix` pins the reclamation floor at 0
# because it reads `obs`/`edge` directly — the projection *"discards position and so cannot
# tell `Cyclic.Base 1` from `Cyclic.Base 2`"* (`scope_fix.py:630-632`). This index keeps
# position: `(core_id, plid)` is the reference's OWN location, so two applications of one
# module stay apart, which `_node`'s content key cannot do.
#
# ⚑ AND THE FALLBACK IT REPLACES IS MEASURABLY BROKEN, NOT MERELY WEAKER. With `qname` NULL
# tree-wide, `_event_refs` returns [] for every module and the resolver silently drops to its
# projection fallback (`scope_fix.py:643-650`), which requires `_node.op_path_id IS NOT NULL`
# — true for **13 of 4,775 nodes**. It returns almost nothing and reports success.
#
# ⚑ `arg_ord`/`arg_lit` ARE NOT PRECOMPUTED ARGUMENTS. `_event_refs` slices the first `nargs`
# children where `nargs` comes from `_module_params(owner)` — a SOURCE lookup, not a store
# fact. Baking that in would freeze a judgement that belongs to the caller and would rot when
# a module's telescope changes. This carries the positional facts; the caller still decides
# how many to take.
ref = _t(
    "ref",
    Column("core_id", Text),
    Column("plid", Integer),
    Column("qname_pid", Text),
    Column("arg_ord", Integer),
    Column("arg_lit_id", Text),
)

# ── the ADDRESSING index (⟡obs-node: which interned node each observation became) ────
# ⚑ THE MAP THE PROJECTION COMPUTES AND THROWS AWAY. `project_sppf`'s `packing` dict
# (`sppf_db.py:869`) is exactly `(core_id, local_id) → node_id`, built for every observation
# on every projection and discarded when the function returns. Nothing in the store records
# it — verified against the live catalogue: 28 relations, none of them this.
#
# ⚑ AND ITS ABSENCE IS WHAT HOLDS THE DRAIN. `reflects_obs` cannot verify a single core
# without it — measured, "438,009 of 438,009 ekeys have no interned head symbol" — so the
# reconstruction gate correctly refuses, and the queue's 1,255,688 reclaimable rows stay put.
# This is the last term in the conjunction.
#
# ⚑ AN INDEX, NOT A FACTOR, like `ref`. It is derived from `SPPF × fibre` and reconstructs
# nothing on its own, so it stays out of the drain path: the product identity the tier drains
# TOWARD must not depend on a table the drain could delete. Rebuildable by one projection.
#
# ⚑ `(core_id, local_id)` AND NOT `ekey`, which is the correction the whole session earned.
# One ekey occurs many times across cores and positions; the SPPF node it becomes depends on
# its CHILDREN, so two occurrences of one ekey can intern differently. Keying on ekey would
# collapse exactly the distinction `obs`'s fibre exists to preserve.
# ⚑⚑ `ch` IS THE CARRIER THAT MAKES THE DRAIN LICENSABLE, AND IT IS A COLUMN, NOT A RELATION.
# MEASURED 2026-08-11: `obs_node ⋈ _node` determines only 56.2% of ekeys — 43.8% ambiguous,
# 107 of 193 node_ids carrying more than one ekey — and stripping the `ch` field collapsed the
# ambiguous set from 107 to **1**. So the head is recoverable from the interned node and the
# CHILDREN are not, and `ch` lived only in tier-0 `edge`, which made `obs` and `edge` mutually
# determining: the tier could drop either, never both.
#
# ⚑ WHY A COLUMN ON THIS TABLE RATHER THAN A NEW ONE: the fibre is keyed `(core_id, local_id)`
# and so is `ch` — same key, same grain, same lifetime. A separate relation would add a join to
# every reconstruction and a second thing to keep in step with the projection, for no fact this
# table does not already address.
#
# ⚑ AND IT IS A SEQUENCE, WHICH IS WHAT LICENSES COLLAPSING 177,370 EDGE ROWS TO 77,759.
# MEASURED: `edge.ord` is dense `0..n-1` on **all 77,759 parents, zero ragged** — the same
# argument `--fibre` makes for `ekey[]`, one level down. So position carries the `ord` and only
# the child ids need storing. Average fan-out 2.28, so this is a 2.3× row collapse AND it stops
# repeating the 52-byte `core_id` once per edge.
#
# ⚑ TEXT, NOT `integer[]`, AND THE REASON IS PORTABILITY NOT TASTE. `ARRAY` has no sqlite
# rendering, so declaring it would make this tier postgres-only and break every fixture that
# builds the schema on `:memory:` — including `reconstruct`'s own determinacy cases. The
# comma-joined form is exactly the signature the validating probe used
# (`string_agg(clid::text, ',' ORDER BY ord)` → **0 ambiguous**), so the encoding is the one
# that was measured rather than one assumed equivalent to it. `ekey` sets the precedent:
# structured content in a string column is this store's existing idiom.
obs_node = _t(
    "obs_node",
    Column("core_id", Text),
    Column("local_id", Integer),
    Column("node_id", Text),
    Column("ch", Text),
)

# ── `_STORE_ASSIGNED` — DELETED 2026-08-12 WITH ITS ONE MEMBER. ────────────────────────────
#
#     # Columns the ENGINE assigns; excluded from every generated INSERT column list.
#     _STORE_ASSIGNED = {"obs": ("seq",)}
#
# ⚑ A ONE-MEMBER REGISTRY IS THE COLUMN WEARING A MECHANISM'S CLOTHES. It was read at exactly
# one site (`schema_rows.upsert`) about exactly one column, and with `obs.seq` gone the mapping
# is `{}` — a lookup that can only ever return its default. The generality was never exercised.
#
# ⚑ THE ARITY DID NOT MOVE, WHICH IS THE MEASUREMENT THIS DELETION OWED. `upsert` takes
# POSITIONAL tuples in declared order MINUS the store-assigned set, so `obs` was a 3-tuple
# (`core_id, local_id, ekey`) with `seq` excluded and is a 3-tuple now with `seq` absent. Every
# caller is unchanged — checked, not assumed, because a changed arity fails LOUDLY on postgres
# (`the query has N placeholders but M parameters were passed`) and that is the good case.
#
# ⚑ IF AN ENGINE-ASSIGNED COLUMN IS EVER ADDED BACK, THE RULE IT ENCODED IS THE PART TO
# RESTORE, not this dict: *"a writer should not have to know which columns it is not allowed to
# write"* — read the exclusion off the declaration, never at the call sites.

# ⚑ REPLACES `PRAGMA user_version`, which is a 32-bit slot in the sqlite FILE HEADER —
# not a SQL feature, and with no postgres equivalent. A table is portable and strictly
# more honest: the header int can hold a number, a row can also say when it was set.
schema_version_t = _t("schema_version", Column("version", Integer))

# ── the SPPF PROJECTION tier (materialized, derived from events) ────────────────────
# ⚑⚑ `sym` REMOVED 2026-08-23 — A DISPLAY COLUMN NOTHING READ. It held
# `_b64("\x00".join(head))` and its own writer labelled it *"head-only: a DISPLAY symbol,
# NOT the key"*. MEASURED on the live store before removal:
#   · `ix_node_sym` idx_scan = **3** lifetime, against `_node_pkey`'s 21,820,687
#     (`pg_stat_database.stats_reset` is NULL — never reset, so 3 is genuine lifetime,
#     not an artifact of a recent restart)
#     ⚑ AND THE COLLECTOR IS LIVE, WHICH IS A SECOND QUESTION `stats_reset` DOES NOT ANSWER.
#       A FROZEN stats collector reads exactly like a genuinely-unused index: both report a
#       small number, plausibly. What rules it out here is that `_node_pkey`'s 21.8M sits in
#       the SAME view — one collector feeds both rows, so it cannot be frozen for one index
#       and current for its sibling. Recorded because a peer measured a log collector that
#       shipped GREEN-BUT-EMPTY for ELEVEN DAYS (a bare `except` froze its cursor at 13.7MB
#       while the file grew to 4.9GB), which is this exact shape one system over: an
#       instrument reporting success while measuring nothing, and a false ZERO gets banked
#       where a false positive would have been investigated.
#   · 443,169 rows carrying 12 MB of text + a 4,584 kB index, over only 14,552 DISTINCT
#     values — ~30× redundant against itself
#   · `query_defs --touching _node` lists 17 declared readers; NONE selects `sym`
#     (`q_node_head` reads node_id/op_path/op_term/role; `q_max_node_len` measures node_id)
#
# ⚑ AND ITS IDENTITY ROLE WAS ALREADY RETIRED, which is why nothing read it. `project_sppf`'s
# own note records that head-plus-children-heads identity was UNSOUND — measured, all 926
# `QName` observations interned to ONE node_id — so `pack()` now builds `_sig` from interned
# `tid`/`pid` handles plus child NODE IDS. `sym` survived as a vestige of the retired scheme.
#
# ⚑ `orbit_node.sym` BELOW IS A DIFFERENT COLUMN AND STAYS. It is fed by
# `project_orbit_sppf`'s own `sym` binding, whose comment records that making it a surrogate
# would turn the Sₙ-orbit representative INGEST-ORDER-DEPENDENT. Two same-named columns, one
# load-bearing; a "make these consistent" edit is exactly what must not happen here.
_node = _t(
    "_node",
    Column("node_id", Text),
    Column("kind_id", Text),
    Column("role_id", Text),
    Column("op_term_id", Text),
    Column("op_path_id", Text),
    Column("lit_id", Text),
    pk="node_id",
)
node_child = _t(
    "node_child", Column("node_id", Text), Column("ord", Integer), Column("child_id", Text)
)
_unit = _t(
    "_unit",
    Column("unit_id", Text),
    Column("name_pid", Text),
    Column("root_id", Text),
    Column("file_id", Text),
    Column("kind_id", Text),
    Column("module_pid", Text),
    Column("root_lid", Integer),
    Column("copy", Integer),
    Column("level", Integer),
    pk="unit_id",
)
_unit_cod = _t(
    "_unit_cod",
    Column("unit_id", Text),
    Column("cod_ctor_id", Text),
    Column("cod_qname_pid", Text),
    pk="unit_id",
)
unit_node = _t("unit_node", Column("unit_id", Text), Column("node_id", Text))

# ── the ORBIT tier — REMOVED 2026-08-23 (operator: *"We can erase orbit_node, too. It's
# obsolete now that we have the compound-identity framing."*) ───────────────────────
#
# It declared `orbit_node(orbit_id, sym, kind_id, role_id, op_term_id, op_path_id, lit_id)`,
# `orbit_child(orbit_id, ord, child_id)` and `orbit_member(orbit_id, node_id)` — nodes keyed
# by their orbit under the rig group, written by `sppf_db.project_orbit_sppf` (⟡rig).
#
# ⚑ SUPERSEDED, NOT MERELY UNUSED. The orbit key was an ATTEMPT AT THE IDENTITY QUESTION —
# `opk = _b64(head ‖ canonical child symbols)`, a single opaque string standing in for
# "this node up to the rig action". The compound-identity framing answers it directly, so
# the tier is a retired approach rather than dead weight that happened to accumulate.
#
# MEASURED at removal, all three relations at **0 rows** on the live store, and the two
# declared readers (`q_max_orbit_len`, `q_orbit_node_count`) are bare `count(*)`/`max(length)`
# counters over that emptiness — no consumer reads a VALUE from this tier.
#
# ⚑ THE `argperm` TIER BELOW IS A DIFFERENT PROJECTION AND STAYS. `_orbit_def` /
# `graded_orbit_*` are written by `project_argperm`, are likewise 0 rows, and share only the
# word "orbit" — the same two-things-one-name hazard as `_node.sym` vs `orbit_node.sym`.
# Removing them is a separate decision nobody has made.

# ── the ARGPERM tier (⟡graded-orbit: per-def graded orbit-key + coset residue) ──────
_orbit_def = _t(
    "_orbit_def",
    Column("unit_id", Text),
    Column("type_key", Text),
    Column("graded_key", Text),
    Column("residue", Text),
    Column("stab", Integer),
    pk="unit_id",
)
graded_orbit_node = _t(
    "graded_orbit_node",
    Column("graded_id", Text),
    Column("kind", Text),
    Column("op", Text),
    Column("qname", Text),
    Column("fanin", Integer),
    pk="graded_id",
)
graded_orbit_child = _t(
    "graded_orbit_child",
    Column("graded_id", Text),
    Column("ord", Integer),
    Column("child_id", Text),
)
graded_orbit_member = _t("graded_orbit_member", Column("graded_id", Text), Column("unit_id", Text))

# ── indexes (the access paths the projection depends on) ────────────────────────────
INDEXES = [
    Index("ix_terms_text", terms.c.text, unique=True),
    # ⚑⚑ THE INTERNING KEY OF THE VOCAB TIER, AND IT IS WHAT MAKES THE RUNG IDEMPOTENT AND
    # CONCURRENT-SAFE AT ONCE. `ix_terms_text`'s own note calls it *"the same unique-on-content
    # index that makes `tid` idempotent"*; here it is the arbiter `ON CONFLICT (s) DO NOTHING`
    # names, so a second run — or a second WRITER mid-run — offers strings that already exist
    # and the engine declines them. Without it there is no conflict target at all and the only
    # one available would be the SURROGATE `id`, which is precisely the target that cannot
    # dedupe by content (⑸'s `path_text` finding, verbatim).
    #
    # ⚑⚑ IT IS A BTREE OVER `jsonb`, AND THAT IS THE PROPERTY THAT DECIDED `jsonb` OVER `json`
    # ONE TIER DOWN — now load-bearing twice. `json` has NO equality operator, so `UNIQUE` over
    # it is not expressible at all and `ON CONFLICT (v)` would have nothing to name; `jsonb` has
    # a total btree order, so the same index that made a TEXT vocabulary interning-safe makes a
    # VARIANT one interning-safe with no change of mechanism. The btree entry limit (~2704 B)
    # is the one bound this key has to respect: MEASURED over the corpus, the widest interned
    # string is 94 bytes and no row is within 100× of the limit.
    Index("ix_decscalar_v", dec_scalar.c.v, unique=True),
    # ⚑⚑ THE HANDLE, AND IT IS UNIQUE BECAUSE IT IS AN IDENTITY — the property `c1`/`c2` spend.
    # A child slot holds this number, so if two nodes could share it the tree would be
    # ambiguous in exactly the place the composite PK went to the trouble of being exact.
    # `GENERATED ALWAYS` makes postgres REFUSE a client-supplied value, which is ⟡ladder-2b's
    # rule enforced by the engine rather than by everyone remembering it.
    Index("ix_decnode_id", dec_node.c.id, unique=True),
    # ⚑ THE FAN-IN ACCESS PATHS. The sharing measurement — how many nodes have more than one
    # PARENT — is a group-by over the two child columns, and it is the number the right-spine
    # decision was made to protect. Reading it off a sequential scan of a multi-million-row
    # relation twice is what an index is for.
    Index("ix_decnode_c1", dec_node.c.c1),
    Index("ix_decnode_c2", dec_node.c.c2),
    # ⚑⚑ THE ROUND SLICE. This is the index that makes the cost LINEAR rather than
    # O(cells × rounds): with it, round `r` touches only its own frontier; without it every one
    # of 115,268 rounds sequentially scans the whole skeleton. It is the single most
    # load-bearing line in this tier.
    Index("ix_decstage_rnd", dec_stage.c.rnd, dec_stage.c.core_id),
    # ⚑⚑ `path_text` IS AN INTERNING TABLE THAT HAD NO INTERNING KEY (⑸, 2026-08-12). Every
    # note in this file calls `ix_terms_text` *"the interning key — the same unique-on-content
    # index that makes `tid` idempotent"*, and `path_text` is the identical structure one level
    # up (a surrogate id ↔ one dotted qname) with the index simply absent. So `pid` could not
    # be written as `INSERT … ON CONFLICT (text) DO NOTHING` at all: there was no constraint to
    # name, and the only conflict target available was the SURROGATE — which is the target that
    # cannot dedupe by content, and therefore the one that lets a race mint two ids for one
    # path (a gap) or one id for two paths (a wrong answer).
    #
    # ⚑ THE ABSENCE WAS INVISIBLE BECAUSE THE PYTHON MAP WAS DOING THE INDEX'S JOB. `paths_map`
    # in `_mk_interners` deduped by text WITHIN one process, so a serial ingest produced exactly
    # the rows a unique index would have allowed and nothing ever failed. An invariant enforced
    # by the writer's memory instead of by the store holds precisely until a second writer exists.
    Index("ix_pathtext_text", path_text.c.text, unique=True),
    Index("ix_pathseg_uniq", path_seg.c.path_id, path_seg.c.ord, unique=True),
    Index("ix_obs_pk", obs.c.core_id, obs.c.local_id, unique=True),
    Index("ix_obs_ekey", obs.c.ekey),
    # ⚑ THE PAIR IS ENOUGH HERE AND THE TRIPLE IS REQUIRED IN `node_child` — and the contrast
    # is the whole point, not an inconsistency. PRE-INTERN, `plid` is a per-core LOCAL id, so
    # `(core_id, plid, ord)` addresses exactly one physical slot in one core's tree: nothing
    # has collapsed yet, so POSITION ALONE IS IDENTITY and `clid` is determined by it.
    # POST-INTERN (`ix_nc_edge`), many per-core parents share one packing, so position stops
    # being unique and the CONTENT (`child_id`) must join the key — see the note there.
    #
    # So the two indexes measure the same structure on opposite sides of the quotient, and
    # the extra column is exactly what the quotient costs. Reading either as the template for
    # the other is how a "make these consistent" edit would break one of them.
    Index("ix_edge_pk", edge.c.core_id, edge.c.plid, edge.c.ord, unique=True),
    Index("ix_edge_child", edge.c.core_id, edge.c.clid),
    Index("ix_unitobs_pk", unit_obs.c.unit_id, unique=True),
    # ⚑ `ix_node_sym` REMOVED with the column it indexed (2026-08-23) — 3 lifetime scans
    # against `_node_pkey`'s 21.8M; see the `_node` declaration for the full measurement.
    Index("ix_nc_node", node_child.c.node_id),
    Index("ix_nc_child", node_child.c.child_id),
    # ⚑ THE TRIPLE IS UNIQUE-BY-CONSTRUCTION AND `(node_id, ord)` IS NOT — and the reason is
    # structural, not an accident of this data (user, 2026-08-07: *"unique-by-construction
    # MUST consist of both the node(child1,child2) and edge(parent,child) knowledge in order
    # to fix both degrees of freedom."*).
    #
    # There are TWO degrees of freedom in a child slot and each view fixes exactly one:
    #     ord       — the EDGE knowledge: WHICH SLOT of the parent
    #     child_id  — the NODE knowledge: WHICH THING sits there
    # `(node_id, ord)` fixes position and leaves content free; `(node_id, child_id)` fixes
    # content and leaves position free. Neither is a key. The triple is, because it carries
    # both readings of the same row — which is precisely why the identity view (`_node`) and
    # the connection view (`node_child`) FOLD into one hypergraph rather than one replacing
    # the other. Drop either column and the fold loses a coordinate.
    #
    # ⚑ MEASURED CONSEQUENCE, so this is not a hypothetical: `ord` has 22 distinct values
    # while a single interned parent holds up to 1,008 rows. One ordinal legitimately carries
    # MANY distinct children — that is the SPPF's sharing, many per-core parents collapsing
    # to one packing — so a `(node_id, ord)` unique index would REFUSE correct data.
    Index("ix_nc_edge", node_child.c.node_id, node_child.c.ord, node_child.c.child_id, unique=True),
    Index("ix_un_unit", unit_node.c.unit_id),
    Index("ix_un_node", unit_node.c.node_id),
    Index("ix_un_edge", unit_node.c.unit_id, unit_node.c.node_id, unique=True),
    # ⚑ the orbit tier's indexes (`ix_orbit_mem`, `ix_orbit_child`) went with the tier,
    # 2026-08-23. The argperm indexes below are a DIFFERENT tier and stay.
    # argperm tier
    Index("ix_odef_type", _orbit_def.c.type_key),
    Index("ix_odef_graded", _orbit_def.c.graded_key),
    Index("ix_gorbit_child", graded_orbit_child.c.graded_id),
    Index("ix_gorbit_nqn", graded_orbit_node.c.qname),
    # ref tier — the resolver's lookup is BY MODULE, so the core leads the key.
    # ⚑ NOT UNIQUE, DELIBERATELY. One reference may carry several argument positions, so
    # `(core_id, plid)` repeats across `arg_ord` — the same two-degrees-of-freedom shape as
    # `ix_nc_edge`, and a unique index on the pair would refuse correct data.
    Index("ix_ref_core", ref.c.core_id, ref.c.plid, ref.c.arg_ord),
    Index("ix_ref_qname", ref.c.qname_pid),
    # obs_node tier — UNIQUE on the fibre coordinate: one observation becomes exactly one
    # node. That is not a convention, it is what makes the map a FUNCTION; a duplicate here
    # would mean the projection interned one occurrence twice, which is a defect the index
    # should refuse rather than store.
    Index("ix_obsnode_pk", obs_node.c.core_id, obs_node.c.local_id, unique=True),
    # and the reverse direction: which occurrences fell into this node — the fibre, read
    # from the class side. `reflects_obs` needs the forward map; sharing analysis needs this.
    Index("ix_obsnode_node", obs_node.c.node_id),
]


# ── the compat relations, as COMPOSABLE FRAGMENTS (no DDL) ──────────────────────────
#
# ⚑⚑ THESE EMIT NO DDL — ⟡view-purge, 2026-08-12 (user: *"I don't want us to emit any
# CREATE VIEW DDL **at all**; whatever would query that view should leverage the
# sqlalchemy fragments instead."*). The selectables are UNCHANGED and are the whole
# point: they were always the definition, and `sqlalchemy_views.CreateView` merely
# MATERIALISED them into a stored copy. What went is the materialisation.
#
# ⚑ THE ARGUMENT WAS ALREADY IN THIS ARC, MADE FOR A DIFFERENT FEATURE AND NEVER APPLIED
# BACKWARDS: *"A DB view would be a second spelling of the query algebra living OUTSIDE
# `--check`'s drift gate and outside `--verify` — the same argument `q_edge_disagreement`
# already makes against `text()` blobs."* Three consequences, all live until now:
#
#   1. A VIEW IS SCHEMA STATE. It must be created, dropped and kept in sync;
#      `project_sppf` DROPped and recreated these on every non-additive run. That is DDL
#      churn for something that is pure composition.
#   2. A VIEW HAS NO TIER. `_TIERS` maps tiers to relations and a view is neither a
#      relation that drains nor a rung, so it sat in the schema namespace PRETENDING to
#      be a relation — `schema.relations()` reported it beside tables and `--census`
#      counted it. `_TIER_VIEWS` existed only to paper over that.
#   3. A VIEW IS A FROZEN COMPOSITION. A Core selectable can be parameterised
#      (`live_only=`, a core filter, a scope) and pushed into a larger statement; a view
#      can only be selected from.
#
# ⚑⚑ THE OLD SECTION HEADER'S CLAIM IS KEPT AS RESIDUE BECAUSE IT IS STILL TRUE AND IS
# NOW SATISFIED A DIFFERENT WAY: *"An emitter carrying only tables would have produced a
# store where every table and index is present and every consumer fails — the shape that
# looks like a successful migration."* Exactly so — which is why this change CONVERTED
# every consumer rather than merely deleting the emit. The four consumed fragments are
# imported by `query_decl` and `.subquery()`d in place of its `_T("node", …)` shims, and
# the raw-SQL readers in `scratch/` were rewired the same way. MEASURED against the
# stored views before dropping them (`query_defs --equiv frag.X view.X --sandbox`, a
# populated tenant): node 4,966 = 4,966 · unit 57 = 57 · node_fanin 4,910 = 4,910 ·
# shared_subtree 913 = 913 · node_atom 313 = 313, all IDENTICAL. `orbit` is UNMEASURED —
# `orbit_node` holds 0 rows in every tenant, so both arms returned empty and `--equiv`
# correctly refused the comparison; its stored `pg_get_viewdef` body is this selectable
# verbatim, and it has ZERO consumers (`pycodemod --relname orbit`: 0 sql sites).
#
# ⚑ AND THE OTHER HALF OF THE OLD ARGUMENT SURVIVES INTACT (user, 2026-08-06: *"hardcoding
# views runs counter to my structuralist preferences"*). A body is a `select()` and not SQL
# text — structurally queryable, composable (`shared_subtree` is literally built FROM
# `node_fanin`'s selectable). The purge does not walk that back; it removes the one step
# that turned the structure back into a stored string.
#
# ⚑ WHAT THE FRAGMENT FORM NOW ADMITS THAT THE VIEW COULD NOT — named, NOT built, because
# a parameter nobody calls is the `rewire_only` class: `shared_subtree_sel`'s threshold is
# the literal `2` frozen into a stored body, and as a fragment it can take a `bindparam`
# (`q_shared_subtree` already binds `min_fanin` in the OUTER query and then filters a
# relation that has ALREADY applied `>= 2` — two thresholds, one of them unreachable);
# `node_sel`/`unit_sel` can take a core or unit scope pushed INSIDE the joins rather than
# wrapped around them; `node_fanin_sel` can carry a `live_only` predicate. Each is one
# keyword argument away, and each is owed to whichever consumer asks first.
_k = terms.alias("k")
_r = terms.alias("r")
_l = terms.alias("l")
_o = terms.alias("o")
_f = terms.alias("f")
_ku = terms.alias("ku")
_pt = path_text.alias("pt")

# ⚑ `_node.c.sym` DROPPED FROM THIS PROJECTION (2026-08-23) with the column itself. It was
# SELECTED here — which is why a naive "does any builder read sym?" check said no while this
# shared select-list fed several that did. The consumers took it positionally or by label and
# none rendered it; see `_node`'s declaration for the measurement (3 lifetime index scans).
node_sel = select(
    _node.c.node_id,
    _k.c.text.label("kind"),
    _r.c.text.label("role"),
    func.coalesce(_pt.c.text, _o.c.text).label("op"),
    _l.c.text.label("lit"),
).select_from(
    _node.join(_k, _k.c.term_id == _node.c.kind_id)
    .join(_r, _r.c.term_id == _node.c.role_id)
    .join(_l, _l.c.term_id == _node.c.lit_id)
    .outerjoin(_o, _o.c.term_id == _node.c.op_term_id)
    .outerjoin(_pt, _pt.c.path_id == _node.c.op_path_id)
)

unit_sel = select(
    _unit.c.unit_id,
    _pt.c.text.label("name"),
    _unit.c.root_id,
    _f.c.text.label("path"),
    _ku.c.text.label("kind"),
    _unit.c.copy,
).select_from(
    _unit.join(_pt, _pt.c.path_id == _unit.c.name_pid)
    .join(_f, _f.c.term_id == _unit.c.file_id)
    .outerjoin(_ku, _ku.c.term_id == _unit.c.kind_id)
)

node_fanin_sel = select(
    node_child.c.child_id.label("node_id"), func.count().label("fanin")
).group_by(node_child.c.child_id)

# ⚑ COMPOSITION IS THE PAYOFF, and it is why this is not merely tidier. `shared_subtree`
# was a string that NAMED `node_fanin`; it is now built from that view's own selectable,
# so a change to the fanin definition propagates by construction instead of by someone
# remembering to edit two strings.
node_fanin_v = node_fanin_sel.subquery("nf")
shared_subtree_sel = select(node_fanin_v.c.node_id, node_fanin_v.c.fanin).where(
    node_fanin_v.c.fanin >= 2
)

_node_v = node_sel.subquery("nv")
node_atom_sel = select(_node_v.c.node_id, _node_v.c.op).where(
    ~exists(
        select(literal(1)).select_from(node_child).where(node_child.c.node_id == _node_v.c.node_id)
    )
)

# ⚑ ORDER IS LOAD-BEARING for the EMIT even though composition made the SQL independent:
# postgres inlines a subquery, so `shared_subtree` no longer *requires* `node_fanin` to
# exist — but `catalog_query` and the builders still SELECT from both by name, so both
# must be created. Declared as a list to keep the emit deterministic.
# the ORBIT tier's compat view — same shape as `node`, over the orbit projection
# ⚑ `orbit_sel` REMOVED 2026-08-23 with the orbit tier — it was `node_sel`'s twin over
# `orbit_node`, decoding the same five interned handles. Its five `terms`/`path_text` aliases
# (`_ok`/`_orr`/`_ol`/`_oo`/`_opt`) went with it; the positional `node_sel` above is unaffected
# and keeps its own aliases.


# ── THE RECONSTRUCTION (⟡ladder-retire) — ONE FRAGMENT, THREE USES ──────────────────
#
# ⚑⚑ THIS IS THE ONLY SPELLING OF "WHAT THE HIGHER TIERS SAY A COMPOUND HOLDS", and the
# three places that need it get it by calling this with a different `pos`, never by
# restating it. Two spellings of a reconstruction is the defect a drain cannot survive:
# the one that LICENSES the delete and the one that ANSWERS afterwards would be free to
# disagree, and the disagreement would surface only after the source was gone.
#
#     pos = the interior positions with no memo row  → `dec_drain.rebuild_sql`, the RUNG
#     pos = the candidate roots, from `dec_ref`      → `dec_drain.root_sql`,    the BUILD
#     pos = `dec_root`'s roots                       → `core_decoded_shadow`,   the VIEW
#
# ⚑⚑ THE GRAMMAR IS READ OFF `dec_node`'s FOUR PRODUCTIONS AND IS ENTIRELY BINARY:
#     val(LEAF(s,0))    = dec_scalar[s].v
#     val(MEMBER(k,v))  = the pair  (dec_scalar[LEAF k].v #>> '{}',  val(v))
#     val(OBJ(m,tail))  = jsonb_object_agg over the spine m, m', m'' …
#     val(ARR(e,tail))  = jsonb_agg     over the spine e, e', e'' …  ORDERED
# `sp` walks the spine (a linear chain — one CTE reference, the same grammar rule the build
# obeys) and `agg` aggregates it in the OUTER query, which is the whole trick: the recursive
# term never aggregates, so the 115,268-member object costs ONE statement rather than
# 115,268 rounds. Only NESTING costs a round.
#
# ⚑ `ok` IS PER-ENTRY AND THE PARENT IS ADMITTED ONLY ON `nok = n`. A member whose value is
# a compound with no memo row, or whose KEY does not resolve to a scalar, sets `ok = 0`; the
# parent is then not emitted at all. Emitting it with a JSON `null` in that slot would be
# the M2′ defect from the build side — a reconstruction that reads complete while being
# wrong — and `jsonb_object_agg` will happily write `{"k": null}` for a SQL NULL, so this
# has to be a count rather than a null test on the result.
#
# ⚑ THE `kv IS NOT NULL` IN THE OBJECT FILTER IS NOT REDUNDANT WITH `ok`. `jsonb_object_agg`
# RAISES on a null field name, so an unresolvable key would take the whole statement down
# instead of holding one document; the FILTER keeps the row out of the aggregate while `n`
# still counts it, so the parent is refused rather than the run.
#
# ⚑ `#>> '{}'` AND NOT `::text` — the key is a jsonb STRING and `::text` would keep its
# quotes, so every rebuilt object would be keyed `"\"nodes\""`. This is `to_jsonb(k)`'s
# inverse and it is the only place the reconstruction leaves jsonb.
#
# ⚑ THE ALIAS TAG IS A PARAMETER BECAUSE ONE STATEMENT MAY CONTAIN TWO INSTANCES. Without
# it the CTE names collide the moment a caller composes two reconstructions in one
# statement, and postgres reports a name clash rather than a wrong answer — loud, but only
# at the point where the composition was already written.
def rebuild_sel(pos, tag):
    """`select(id, v)` — the jsonb value each compound in `pos(id, head)` denotes."""
    stp, cel, mem = (
        dec_node.alias("stp" + tag),
        dec_node.alias("cel" + tag),
        dec_node.alias("mem" + tag),
    )
    kle, vnd = dec_node.alias("kle" + tag), dec_node.alias("vnd" + tag)
    ksc, lsc = dec_scalar.alias("ksc" + tag), dec_scalar.alias("lsc" + tag)
    dvl = dec_val.alias("dvl" + tag)
    sp = select(pos.c.id.label("root"), literal(0).label("i"), pos.c.id.label("cell")).cte(
        "sp" + tag, recursive=True
    )
    sp = sp.union_all(
        select(sp.c.root, (sp.c.i + 1).label("i"), stp.c.c2.label("cell"))
        .select_from(sp.join(stp, stp.c.id == sp.c.cell))
        .where(stp.c.c2 != 0)
    )
    # ⚑ `c1 <> 0` DROPS THE EMPTY COMPOUND'S ONLY CELL, which is what makes `OBJ(0,0)` and
    # `ARR(0,0)` fall through to the `coalesce` below as `{}` and `[]` rather than needing a
    # production of their own. Five of the 43 documents are `{"nodes": {}, "defmarks": []}`,
    # so both empties are exercised by the corpus.
    it = (
        select(sp.c.root, sp.c.i, cel.c.head.label("chead"), cel.c.c1.label("item"))
        .select_from(sp.join(cel, cel.c.id == sp.c.cell))
        .where(cel.c.c1 != 0)
    ).cte("it" + tag)
    ent = (
        select(
            it.c.root,
            it.c.i,
            it.c.chead,
            case((it.c.chead == 1, mem.c.c2), else_=it.c.item).label("vnode"),
            ksc.c.v.label("kv"),
        ).select_from(
            it.outerjoin(mem, and_(it.c.chead == 1, mem.c.id == it.c.item))
            .outerjoin(kle, and_(it.c.chead == 1, kle.c.id == mem.c.c1))
            .outerjoin(ksc, and_(it.c.chead == 1, ksc.c.id == kle.c.c1))
        )
    ).cte("ent" + tag)
    res = (
        select(
            ent.c.root,
            ent.c.i,
            ent.c.chead,
            ent.c.kv,
            case((vnd.c.head == 0, lsc.c.v), else_=dvl.c.v).label("val"),
            case(
                (and_(ent.c.chead == 1, ent.c.kv.is_(None)), literal(0)),
                (vnd.c.head == 0, literal(1)),
                (dvl.c.id.isnot(None), literal(1)),
                else_=literal(0),
            ).label("ok"),
        ).select_from(
            ent.join(vnd, vnd.c.id == ent.c.vnode)
            .outerjoin(lsc, and_(vnd.c.head == 0, lsc.c.id == vnd.c.c1))
            .outerjoin(dvl, and_(vnd.c.head != 0, dvl.c.id == ent.c.vnode))
        )
    ).cte("res" + tag)
    agg = (
        select(
            res.c.root,
            func.count().label("n"),
            func.count().filter(res.c.ok == 1).label("nok"),
            func.jsonb_object_agg(res.c.kv.op("#>>")(text("'{}'")), res.c.val)
            .filter(and_(res.c.chead == 1, res.c.kv.isnot(None)))
            .label("ov"),
            func.jsonb_agg(aggregate_order_by(res.c.val, res.c.i))
            .filter(res.c.chead == 2)
            .label("av"),
        ).group_by(res.c.root)
    ).cte("agg" + tag)
    return (
        select(
            pos.c.id,
            case(
                (pos.c.head == 1, func.coalesce(agg.c.ov, text("'{}'::jsonb"))),
                else_=func.coalesce(agg.c.av, text("'[]'::jsonb")),
            ).label("v"),
        )
        .select_from(pos.outerjoin(agg, agg.c.root == pos.c.id))
        .where(func.coalesce(agg.c.nok, 0) == func.coalesce(agg.c.n, 0))
    )


# ── the INTERIOR positions — every compound that is a member's value or an array element ─
#
# ⚑ A **TAIL** IS NOT A POSITION, AND EXCLUDING IT IS WHAT KEEPS THE MEMO LINEAR RATHER THAN
# QUADRATIC. `rebuild`'s own docstring on the python side records the measurement: memoising
# the value of every spine cell stores the 115,268-member dict, then the 115,267-member
# dict, then … — Θ(N²) for one document. `c1` of an OBJ cell is a MEMBER (not a value) and
# `c2` of either spine head is a TAIL, so exactly two slots produce positions: a MEMBER's
# `c2`, and an ARR cell's `c1`.
_pin = dec_node.alias("pin")
_pq = union_all(
    select(dec_node.c.c2.label("id")).where(dec_node.c.head == 3),
    select(dec_node.c.c1.label("id")).where(and_(dec_node.c.head == 2, dec_node.c.c1 != 0)),
).subquery("pq")
_dvx = dec_val.alias("dvx")
interior_pos = (
    select(_pin.c.id, _pin.c.head)
    .distinct()
    .select_from(_pq.join(_pin, and_(_pin.c.id == _pq.c.id, _pin.c.head.in_([1, 2]))))
    .where(~exists(select(literal(1)).select_from(_dvx).where(_dvx.c.id == _pin.c.id)))
).cte("posi")

# ── the CANDIDATE ROOTS — the only root source that exists BEFORE `dec_root` does ────
#
# ⚑ `dec_ref`'s ROOT ADDRESS IS `(sid = 1, kind = 0)` — `dec_tree.roots_sql`'s derivation,
# reused rather than re-derived: `comp`'s `row_number()` orders compounds by path and the
# empty path sorts first, so the document's root compound is `sid = 1`. The `min(ord)`
# selection that picks the spine HEAD out of that compound belongs to the statement that
# needs one root per DOCUMENT; this fragment feeds the reconstruction, which needs one row
# per NODE, so it takes all of them and lets the header build choose.
_rdn = dec_node.alias("rdn")
root_pos = (
    select(_rdn.c.id, _rdn.c.head)
    .distinct()
    .select_from(
        dec_ref.join(
            _rdn,
            and_(
                _rdn.c.head == dec_ref.c.head, _rdn.c.c1 == dec_ref.c.c1, _rdn.c.c2 == dec_ref.c.c2
            ),
        )
    )
    .where(and_(dec_ref.c.sid == 1, dec_ref.c.kind == 0))
).cte("posr")


def compile_sel(sel, back=None):
    """A Core selectable as the SQL text `back` would be sent.

    ⚑ ONE COMPILER, SO A FRAGMENT AND ITS DEPLOYED FORM CANNOT BE PRODUCED TWO WAYS.
    `view_ddl` and `dec_drain`'s rungs both render `rebuild_sel`; if either spelled its own
    `.compile(...)` call the two could drift in `literal_binds` alone — which decides whether
    a construct tag arrives as `1` or as `%(param_1)s`, i.e. whether the statement runs at
    all under a driver that was handed no parameters.

    ⚑ `literal_binds` IS REQUIRED AND IS SAFE ONLY WHILE NO CALLER VALUE REACHES A FRAGMENT.
    Every literal in `rebuild_sel`/`interior_pos`/`root_pos` is a construct tag or an ordinal
    THIS FILE writes; a scope is appended by the statement outside as a real placeholder. If a
    caller value ever reaches a compiled fragment, that is an injection site, not a formatting
    question.
    """
    import store

    return str(sel.compile(dialect=store.dialect(back), compile_kwargs={"literal_binds": True}))


# ── THE SHADOW (⟡ladder-retire) — `core_decoded` AS THE HIGHER TIERS SAY IT IS ───────
#
# ⚑⚑ A VIEW, AND THIS FILE HAS A HARD POLICY AGAINST VIEWS — SO THE EXCEPTION IS STATED
# RATHER THAN ASSUMED (user, 2026-08-13: *"I know I have a hard policy against 'CREATE
# VIEW' … but a **good** case of CREATE VIEW would be to create shadows of the tables that
# are supposed to be reconstructible, showing the precise content that is reconstructible
# from the higher tiers."*). ⟡view-purge deleted six views and the machinery that emitted
# them; the objection it recorded is precise and it does NOT reach this one:
#
#   * THE PURGED VIEWS WERE CONVENIENCES — *"a second spelling of the query algebra"*, a
#     join given a name to save retyping, frozen so no parameter could be pushed in. A
#     SHADOW is not an abbreviation of a join: it IS the drain's predicate, and naming it is
#     what makes the claim inspectable. `core_decoded EXCEPT SELECT … FROM
#     core_decoded_shadow` is the HELD SET, as a relation — where today "is this
#     reconstructible" is a computation somebody has to run.
#   * IT IS ALSO THE MODEL'S GLOBAL-QUERYABILITY CLAIM MADE REAL: *"all read-only queries
#     must aggregate their findings over all tiers"*. A reader selecting the shadow gets the
#     content whether or not the base still holds the row.
#   * ⚑ AND THE OBJECTION THAT KILLED A RECONSTRUCTING VIEW EARLIER IN THIS ARC HAS EXPIRED,
#     WHICH IS NOT THE SAME AS BEING WRONG. It was rejected because the QUEUE machinery could
#     not read it — `xmin` is a system column a reconstructed row cannot have and `seq` was
#     identity-assigned, so `hwm()` over such a view was INEXPRESSIBLE. `consumer`, `lwm`,
#     `advance`, `hwm` and `obs.seq` were all deleted 2026-08-12. The premise went; the
#     decision follows it.
#
# ⚑ THE GENERAL PROHIBITION STANDS AROUND THIS ONE, AND THE CRITERION IS WRITEABLE: a view
# is admissible here IFF it is the reconstruction claim of a relation that is SUPPOSED to be
# reconstructible — one per such tier, no others. `SHADOWS` below is the whole population and
# `_tier` emits nothing else, so a convenience view cannot be added without also asserting it
# shadows a drainable relation.
#
# ⚑⚑ THE DRIFT GATE IS WHAT MAKES THIS SAFE AND IT IS THE PURGE'S REAL OBJECTION, NOT THE
# NAMING. A deployed view can drift from the fragment it was emitted from because nothing
# compares them. `schema_selftest` re-creates the declared body under a probe name and
# compares `pg_get_viewdef` of BOTH — postgres normalises its own stored body, so comparing
# the emitted TEXT to `pg_get_viewdef` would report drift on every whitespace change and
# miss a semantic one; normalising both sides through the engine is exact.
#
# ⚑ THE COLUMN LIST MIRRORS `core_decoded` EXACTLY — `(core_id, relpath, mtime, producer,
# dec)`, same names, same order. A shadow whose columns differ from the relation it shadows
# cannot be `EXCEPT`ed against it, and `EXCEPT` is the whole observability claim.
_rn = dec_node.alias("rn")
shadow_pos = (
    select(dec_root.c.root.label("id"), _rn.c.head)
    .select_from(dec_root.join(_rn, _rn.c.id == dec_root.c.root))
    .distinct()
).cte("poss")
_rv = rebuild_sel(shadow_pos, "s").subquery("rv")
core_decoded_shadow_sel = select(
    dec_root.c.core_id,
    dec_root.c.relpath,
    dec_root.c.mtime,
    dec_root.c.producer,
    _rv.c.v.label("dec"),
).select_from(dec_root.join(_rv, _rv.c.id == dec_root.c.root))

#: The shadow population — `{view name: (selectable, the tier whose DDL creates it)}`.
#
# ⚑ ONE ENTRY PER RECONSTRUCTIBLE TIER, and the tier here is NEVER the one being shadowed. A
# shadow created alongside `sourced` would be dropped by the flush that rebuilds `sourced` and
# would be missing exactly when the drain wanted it.
#
# ⚑⚑ IT IS `valstage` AND NOT `tree`, WHICH LOOKS WRONG AND IS THE ONLY CORRECT ANSWER. This
# shadow reads FOUR relations across THREE tiers — `dec_root` (tree), `dec_node` (tree),
# `dec_scalar` (vocab), `dec_val` (valstage) — so it belongs to no single tier's tables. What
# decides its placement is `_TIER_VIEWS`'s surviving rule: *"a derived object must be created
# after everything it reads."* `valstage` is the LAST of the three to be applied, so emitting
# it there is the only assignment under which `apply(con, only=…)` can never create the view
# before something it selects from. Emitting it with `tree` fails on a fresh store —
# `UndefinedTable: dec_val` — and postgres accepts a view over a missing table at CREATE time
# only when it is created via the full `ddl()`, i.e. it would fail at the FIRST SELECT instead,
# which is the shape that looks like a successful migration.
#
# ⚑ AND A TIER OF ITS OWN WOULD HAVE BEEN THE OTHER CANDIDATE AND IS REFUSED BY THIS FILE'S
# OWN RESIDUE: *"a tier with no tables is not a tier"* (the `QUEUE_TABLES` retirement). A view
# is not a relation that drains, so a `shadow` tier would hold zero tables forever.
#
# ⚑⚑ THE RESIDUE THIS PLACEMENT LEAVES, NAMED RATHER THAN PAPERED OVER: `--flush tree` drops
# `dec_root` with `CASCADE`, which takes the shadow with it, and `_tier("tree")` does not
# re-emit it — so a tree flush leaves a store whose licence cannot be asked. `--flush valstage`
# self-heals (the shadow is that tier's own emit) and so does any `sppf_drain` invocation,
# because its `_tiers` applies `valstage` every run. The fix that suggests itself — emit the
# shadow from EVERY tier it reads — is refused: it would make `apply(only="tree")` fail on a
# fresh store, which would couple the TREE builder to a drain-tier dependency it has no reason
# to carry. A loud `UndefinedTable` at the next drain is the better failure than a silently
# absent claim, and this is where the reader finds out which one they have.
SHADOWS = {"core_decoded_shadow": (core_decoded_shadow_sel, "valstage")}


def view_ddl(back=None, want=None):
    """`CREATE OR REPLACE VIEW` for each shadow (optionally restricted to `want`).

    ⚑⚑ RESTORED 2026-08-13, DELIBERATELY AND NARROWLY. ⟡view-purge deleted `VIEWS`,
    `_TIER_VIEWS`, `view_ddl` and `_view_ddl_named` and dropped `sqlalchemy_views` from
    `pyproject.toml`. What comes back is ONE function over ONE declared population; what
    does NOT come back is the dependency, because `CreateView`'s entire contribution was
    rendering the `CREATE OR REPLACE VIEW <name> AS` prefix — and the purge's own residue
    records it rendering that prefix WRONG under sqlite (*"a library that abstracts a real
    capability DIFFERENCE between engines is abstracting a fiction"*). A prefix this
    emitter can produce itself is not a dependency worth carrying.

    ⚑ `literal_binds` IS REQUIRED AND IS SAFE HERE FOR A REASON THAT MUST STAY TRUE: a view
    body cannot carry a bind parameter, and every literal in `rebuild_sel` is a construct
    tag or an ordinal this file writes. No caller value reaches this compile — if one ever
    does, it is an injection site, not a formatting question.
    """
    import store

    d = store.dialect(back)
    return [
        "CREATE OR REPLACE VIEW %s AS %s"
        % (n, str(SHADOWS[n][0].compile(dialect=d, compile_kwargs={"literal_binds": True})))
        for n in sorted(SHADOWS)
        if want is None or n in want
    ]


# ── `VIEWS` / `_TIER_VIEWS` / `view_ddl` / `_view_ddl_named` — DELETED 2026-08-12 ──────
# ── (⟡view-purge). THE EMITTER LOSES VIEW EMISSION AS A CAPABILITY, NOT AS AN OPTION. ──
# ── ⚑ AND `view_ddl` IS BACK 2026-08-13 FOR SHADOWS ONLY — see `SHADOWS` above. The
# ── residue below is kept verbatim because its argument is still the governing one for
# ── every view that is NOT a reconstruction claim, and because "the exception swallowed
# ── the rule" is the failure this pairing exists to make visible.
#
#     VIEWS = [("node", node_sel), ("unit", unit_sel), ("node_fanin", node_fanin_sel),
#              ("shared_subtree", shared_subtree_sel), ("node_atom", node_atom_sel),
#              ("orbit", orbit_sel)]
#     _TIER_VIEWS = {"sppf": ("node", "unit", "node_fanin", "shared_subtree",
#                             "node_atom"), "orbit": ("orbit",)}
#     def view_ddl(back=None):        return [s for _n, s in _view_ddl_named(back)]
#     def _view_ddl_named(back=None): …CreateView(table(name), sel, or_replace=True)…
#
# ⚑ NOT BEHIND A FLAG AND NOT AS A MATERIALIZED VIEW. A retained emit — even unused, even
# opt-in — is the second spelling of the query algebra this change exists to remove, and
# the flag would be the thing a future reader turns back on instead of composing.
#
# ⚑ `_TIER_VIEWS`'s ARGUMENT WAS CORRECT AND IS NOW MOOT, which is the good way for a
# guard to end: *"A view selects from its tier's tables, so applying it with a different
# tier would create a view over tables that do not exist yet — and postgres accepts that
# at CREATE time only to fail at first SELECT."* A fragment is never applied to a store at
# all, so there is no CREATE to mis-order and no tier to assign. The general rule it
# encodes — a derived object must be created after everything it reads — outlives it and
# is still enforced for tables by `MD.sorted_tables`.
#
# ⚑⚑ `view_ddl`'s MEASUREMENT IS THE PART WORTH KEEPING, because it is a refuted
# prediction and those are the expensive kind: *"I replaced my hand-written `OR REPLACE`/
# `IF NOT EXISTS` split with `CreateView(or_replace=True)` and wrote that the construct
# 'renders the right idempotence for the target engine'. MEASURED: it renders `CREATE OR
# REPLACE VIEW` under BOTH dialects — which sqlite rejects as a syntax error. My own case
# caught it, having been written against the behaviour I was replacing."* The transferable
# half: **a library that abstracts a real capability DIFFERENCE between engines is
# abstracting a fiction**, and the way that surfaces is a case written against the OLD
# behaviour still passing. The sqlite arm is itself long retired (⓺); the rule is not.
#
# ⚑ NOTHING REPLACES THESE. The four consumed selectables are imported directly by
# `query_decl`; `node_atom_sel` and `orbit_sel` have no consumer at all
# (`pycodemod --relname node_atom` / `--relname orbit`: 0 sql sites each) and are kept as
# the composition, not as a stub for a re-emit.


# ── the SURROGATE-ID SEQUENCES — ENGINE-ASSIGNED, NEVER CLIENT-ASSIGNED (⑸) ─────────
#
# ⚑⚑ THE RULE WAS ALREADY WRITTEN DOWN IN THIS FILE, ABOUT A DIFFERENT COLUMN, AND WAS NEVER
# APPLIED TO THESE TWO. `obs.seq`'s retirement block above preserves it verbatim:
#
#     *"STORE-ASSIGNED, NEVER CLIENT-ASSIGNED. A counter maintained by the writer collides or
#     gaps under concurrent ingests, and the user's standing instruction is not to assume
#     ingest is serial."* — and its own closing line: *"the rule survives the column: any
#     future engine-owned column owes it."*
#
# `term_id` and `path_id` are client-maintained counters that PREDATE that note. Two writers
# each computed `max(id)+1` — `schema_diag.core_id_for` in one SQL statement, `_mk_interners`
# from a python `ctr` seeded once at load — and both handed the same number to different text.
#
# ⚑⚑ MEASURED, NOT ARGUED (2026-08-12, sandbox, 8 concurrent `--ingest-core` processes):
#   * `core_id_for` names `ON CONFLICT (text)`, so its collision is on the UNNAMED constraint
#     and RAISES — `UniqueViolation … "terms_pkey"`, 4 of 8 processes;
#   * `_mk_interners` writes through `upsert(on_conflict="ignore")`, which compiles to
#     `ON CONFLICT DO NOTHING` with NO target, so its collision is SWALLOWED — a second run
#     had **all 8 processes exit 0** and left **21,840 rows whose `ctor_id` resolves to another
#     term's text** plus 288 texts interned and absent from `terms`. Zero dangling references:
#     no constraint in the schema can see it.
#
# ⚑ SO THE MIS-TARGETED `ON CONFLICT` IS THE BENIGN HALF. A named target turns the race into a
# crash; the untargeted one turns it into a wrong answer with exit code 0.
#
# ⚑ A SEQUENCE AND NOT A CONTENT HASH, DELIBERATELY (user: *"we're not aiming for cross-store
# compatibility of raw ID numbers"*). Reproducibility lives in the interned CONTENT — `terms.text`,
# `path_seg`, `node_child` — and reversal is a QUERY. An engine-owned assignment keeps ids
# surrogate; a digest would replace a collision that the engine refuses with one it cannot see.
#
# ⚑ AND NOT `Identity` ON THE COLUMN, because these ids are `Text`. `obs.seq`'s own residue
# records what that costs: *"`Identity` AND `nullable=True` ARE CONTRADICTORY IN EMITTED DDL …
# it took the store down mid-flush"*.
#
# ── `ID_SEQUENCES` / `seq_align_sql` / `_seq_ddl` — BUILT AND RETIRED THE SAME DAY, 2026-08-12
#
# ⚑⚑ THE SEQUENCE WAS THE RIGHT FIX TO THE WRONG FRAMING. It was built, DDL-emitted,
# selftested and mutation-tested (reverting the mint took `schema.py --selftest` 151 → 147,
# naming `UniqueViolation … "terms_pkey"`), and it is gone because it treated ALLOCATION as
# a given and made the allocator uncollidable, when allocation is the thing to remove.
# `schema_diag.intern` now derives the id from the content (`_content_addr._addr`), so the
# same text yields the same handle in every writer with no communication at all. The deleted
# code read:
#
#     ID_SEQUENCES = [("terms", "term_id", Sequence("terms_term_id_seq")),
#                     ("path_text", "path_id", Sequence("path_text_path_id_seq"))]
#     def seq_align_sql():
#         return ["SELECT setval('%s', GREATEST("
#                 "(SELECT coalesce(max(%s::bigint), 0) FROM %s WHERE %s ~ '^[0-9]+$'), "
#                 "(SELECT last_value FROM %s)))" % (s.name, col, tbl, col, s.name)
#                 for tbl, col, s in ID_SEQUENCES]
#     def _seq_ddl(d, want=None): …CreateSequence(s, if_not_exists=True)…
#
# ⚑ TWO OF ITS ARGUMENTS OUTLIVE IT AND ARE THE PART TO KEEP:
#
#   *"MONOTONE BY CONSTRUCTION, WHICH IS WHAT MAKES IT SAFE TO RE-RUN. `setval(s, GREATEST(
#   max-in-table, s.last_value))` can only move a sequence FORWARD … A bare `setval(s,
#   max-in-table)` would move it BACKWARD past a value a concurrent writer had already taken
#   and not yet committed, which is the same check-then-act shape being retired here."*
#   — the general rule: **any repair of a shared counter must be monotone or it is the defect
#   it repairs.** It applies to the next such column, and there is none today.
#
#   *"THE NUMERIC FILTER IS THE LEGACY-ID TOLERANCE `_next` USED TO CARRY, MOVED INTO SQL …
#   `max(term_id::bigint)` over a store still holding the OLD `_b64` ids raises
#   `InvalidTextRepresentation` and would take every ingest path down at `apply()` time."*
#   — a derived id is not numeric either, so **nothing in this schema may cast an id to a
#   number.** That constraint is now permanent rather than transitional.
#
# ⚑ AND THE MIGRATION COST IS UNCHANGED BY THE SWAP: both schemes re-key every id, so both
# require a full re-ingest. That was already owed — see the STICKY-CORRUPTION finding (a wrong
# `event.ekey → ctor_id` row is never overwritten under `ON CONFLICT DO NOTHING`, so a store
# written concurrently by the pre-fix code must be REBUILT, not repaired).


def ddl(back=None):
    """The full DDL for `back`, as a list of statements — synthesized, never spelled.

    ⚑ `IF NOT EXISTS` IS SET ON EVERY STATEMENT because the callers are idempotent
    builders: `write_events` runs `executescript(EVENT_SCHEMA)` on every invocation and
    relies on re-running being a no-op. A DDL emitter that dropped that would turn the
    second ingest of a session into an error.

    ⚑ IT EMITS NO SEQUENCE AND NO ALIGNMENT, AND THAT IS THE POINT OF A DERIVED ID. An
    intermediate cut put `CREATE SEQUENCE` first and a monotone `setval` last, reasoning that
    *"the alignment rides with the DDL rather than sitting in a `migrate_*` mode, so no entry
    point can be added that mints without it."* That reasoning was right about WHERE the
    alignment had to live and moot once there is nothing to align: a content-derived id needs
    no state in the store at all, so there is no step for a new entry point to forget.
    """
    import store

    d = store.dialect(back)
    out = []
    for t in MD.sorted_tables:
        out.append(str(CreateTable(t, if_not_exists=True).compile(dialect=d)).strip())
    for ix in INDEXES:
        out.append(str(CreateIndex(ix, if_not_exists=True).compile(dialect=d)).strip())
    # ── `out.extend(view_ddl(back))  # views LAST: they select from the tables above`
    # ── DELETED 2026-08-12 (⟡view-purge) and RESTORED 2026-08-13 for SHADOWS ONLY.
    # ⚑ THE ORDERING ARGUMENT THE PURGE CALLED VACUOUS IS LOAD-BEARING AGAIN, and it is
    # exactly the one `_TIER_VIEWS`'s residue states: *"a derived object must be created
    # after everything it reads"*. `core_decoded_shadow` selects from `dec_root`,
    # `dec_node`, `dec_scalar` and `dec_val`, so it goes LAST — postgres accepts a view over
    # a missing table at CREATE time only to fail at first SELECT, which is the shape that
    # makes an out-of-order emit look like a successful migration.
    out.extend(view_ddl(back))
    return out


# The tiers, named by the tables each owns. ⚑ DERIVED FROM THE DECLARATION, not a second
# list to keep in sync: a table added to EVENT_TABLES appears in the event tier's DDL
# automatically, and one added to neither is a declaration error the selftest catches.
# ⚑ THE SOURCED TIER SITS BELOW `event` — see `core_decoded`'s note. It is applied
# SEPARATELY (`apply(con, only="sourced")`) for the same reason `ref`/`obsnode` are: an
# ingest path that does not write it must not be made to create it, and a path that does
# write it must be able to create it WITHOUT dragging the event tier's ten tables along.
SOURCED_TABLES = {"core_decoded"}
# ⚑ ITS OWN TIER, FOR THE REASON `ref` AND `obsnode` HAVE ONE: DERIVED AND DISPOSABLE. Every
# row here is recoverable from `core_decoded` by re-running the rung, and nothing reconstructs
# a document FROM it — so it is an INDEX over the sourced tier in `ref`'s sense, not a
# lifecycle stage (`lifecycle.LIFECYCLE` has three, and this assigns no position and reflects
# nothing). Folding it into `sourced` would make `--ingest-source` — which never writes a
# string row — create a relation it never populates, which is the precedent those two set.
VOCAB_TABLES = {"dec_scalar"}
# ⚑ THE TREE IS ITS OWN TIER AND ITS STAGING IS ANOTHER, for the reason `ref`/`obsnode` are
# separate: an entry point that never populates a relation must not be made to create it.
# `--ingest-vocab` writes no tree row, and a reader that only wants `dec_node` must not be
# made to create a 9-million-row work list it will never fill.
# ⚑ `dec_root` IS IN THE TREE TIER AND NOT A TIER OF ITS OWN, WHICH IS THE OPPOSITE CALL
# FROM `ref`/`obsnode`. Those two are INDEXES — derived, disposable, reconstructing nothing —
# so an entry point that never populates them must not create them. `dec_root` is the
# opposite kind: it is the only carrier of four of `core_decoded`'s five columns, so the
# tree tier WITHOUT it does not reconstruct the tier below and the drain is unlicensable.
# A tier is the set of relations that must be present together for the tier's claim to hold;
# splitting the header out would let a store hold `dec_node` alone and read as a complete
# tree tier while being unable to name a single document.
TREE_TABLES = {"dec_node", "dec_root"}
TREESTAGE_TABLES = {"dec_stage", "dec_ref"}
# ⚑ ITS OWN TIER FOR `treestage`'s REASON, NOT `tree`'s: every row is recoverable by
# re-running `dec_drain.rebuild_sql` from `dec_node` + `dec_scalar` alone, and nothing
# reconstructs a document FROM it — the shadow reads it, but a missing row makes the shadow
# REFUSE rather than answer wrongly. A reader that only wants to query the shadow must not
# be made to create a memo it will never fill, and a `--flush valstage` must be a no-op
# against correctness rather than a data loss.
VALSTAGE_TABLES = {"dec_val"}
EVENT_TABLES = {
    "terms",
    "path_seg",
    "event",
    "obs",
    "edge",
    "unit_obs",
    "unit_member",
    "path_text",
    "core_fp",
    "schema_version",
}
SPPF_TABLES = {"_node", "node_child", "_unit", "_unit_cod", "unit_node"}
# ⚑ SEPARATE TIERS BECAUSE THEY ARE SEPARATELY BUILT. `project_orbit_sppf` and
# `project_argperm` run behind `--orbit` / `--argperm`, drop their own tables first, and
# are additive to the projection — so applying them with the sppf tier would create
# tables that a default ingest never populates.
# ⚑ `ORBIT_TABLES` REMOVED with its tier (2026-08-23). I first kept it as an empty set, on the
# reasoning that a consumer iterating tiers should see "this tier has no tables" rather than
# find the tier gone — but `--literal ORBIT_TABLES` measured **0 sites in 818 files**: nothing
# read it, so the "consumer" that empty set protected does not exist. Keeping it would have
# left a name whose only function was to make a removed tier look present.
ARGPERM_TABLES = {"_orbit_def", "graded_orbit_node", "graded_orbit_child", "graded_orbit_member"}
# ⚑ ITS OWN TIER BECAUSE IT IS DERIVED AND DISPOSABLE. `ref` is an INDEX over
# `SPPF × fibre`, not a factor of it — rebuildable at any time, and safe to drop without
# losing a fact. Folding it into `sppf` would make a default ingest create a table the
# projection never populates (the reason `orbit`/`argperm` are separate), and would blur the
# one property that keeps it out of the drain path: nothing reconstructs FROM it.
REF_TABLES = {"ref"}
# ⚑ ITS OWN TIER FOR THE SAME REASON `ref` HAS ONE: derived, disposable, and not created by
# a default ingest that would never populate it (the `orbit`/`argperm` precedent).
OBSNODE_TABLES = {"obs_node"}


# ── `QUEUE_TABLES` / the `queue` TIER — DELETED 2026-08-12 with the table it named. ─────────
#
# It held `{"consumer"}` and its note read: *"POSTGRES-ONLY TIER. `apply(con, only=\"queue\")`
# on sqlite would create a registry nothing can populate a correct HWM for — worse than
# absent, because a present-but-wrong watermark reads as a working one."* That argument is
# still correct and is now moot: a tier with no tables is not a tier, and `--flush queue`
# refuses by name through `_TIERS`'s own unknown-tier guard rather than through a special case.
#
# ⚑ THE POSTGRES-ONLY SHAPE DID NOT LEAVE WITH IT. `_require_pg` still gates this module and
# still carries the reason (sqlite cannot express the in-flight-transaction floor); what went
# is the one tier whose ONLY member was the registry.
# ⚑⚑ MEMBERSHIP ONLY. THE ORDER IS `TIER_BELOW`, DIRECTLY BELOW — and this note said the
# opposite until 2026-08-13. It read:
#
#     *"`sourced` IS FIRST BECAUSE IT IS LOWEST, and the ordering of this dict is the only
#     place the tier ORDER is written down at all — `_TIERS` is a lookup, not a chain, so
#     nothing DERIVES precedence from it and nothing should start to. The chain that IS
#     authoritative about order is `lifecycle.LIFECYCLE`; this literal merely reads in the
#     same direction so the two do not appear to disagree."*
#
# Quoted rather than deleted because it was wrong in three separate ways and each is worth
# keeping visible:
#
#   1. **It claimed to BE the order and forbade reading it as one in the same sentence.** A
#      reader who obeys the second half has no order; one who obeys the first half has a
#      wrong one. An agent took the first half on 2026-08-13; the gate measured otherwise.
#   2. **The insertion order is WRONG as a drain order, measurably.** It puts `tree` before
#      `treestage`, and `dec_drain.retire_ref_sql`/`retire_stage_sql` delete `dec_ref`/
#      `dec_stage` (treestage) on the strength of `dec_root` (tree) — so `treestage` is
#      BELOW `tree`, the reverse. What the insertion order actually reads as is a CREATE
#      order (a derived object after everything it reads); nothing enforces even that.
#   3. **`lifecycle.LIFECYCLE` cannot settle it.** It is a `Chain` over a DATUM's stages
#      (`sourced → observed → reflected`), not over relations. Different object.
#
# ⚑ AND NOTHING READS THIS DICT'S ORDER — measured, not assumed (`pycodemod --attr _TIERS`,
# 3 reads): `reconstruct.py` takes `_TIERS["event"]`, `sppf_drain.py` takes `set(_TIERS)`,
# `scripts/tier_readset.py` inverts it to `{relation: tier}`. `apply()` orders DDL by
# `MD.sorted_tables`. So the literal below may be reordered freely; `TIER_BELOW` may not.
# ⚑ `"orbit"` REMOVED FROM THE ROSTER 2026-08-23, not merely emptied. An entry mapping to an
# empty set would make every tier-count read 11 while one of them held nothing — a tier that
# EXISTS and is EMPTY and a tier that DOES NOT EXIST are different facts, and the roster is
# what consumers enumerate (`sppf_drain` takes `set(_TIERS)`, `tier_readset` inverts it).
# Advertising a tier with no relations is the absent-vs-empty collapse this file polices
# elsewhere. `argperm` is a DIFFERENT tier and stays.
_TIERS = {
    "sourced": SOURCED_TABLES,
    "vocab": VOCAB_TABLES,
    "tree": TREE_TABLES,
    "treestage": TREESTAGE_TABLES,
    "valstage": VALSTAGE_TABLES,
    "event": EVENT_TABLES,
    "sppf": SPPF_TABLES,
    "argperm": ARGPERM_TABLES,
    "ref": REF_TABLES,
    "obsnode": OBSNODE_TABLES,
}

#: The TIER ORDER — `(lower, higher, why)`, the GENERATING pairs of a strict partial order.
#
# ⚑⚑ ONE SENTENCE FIXES THE DIRECTION, AND EVERYTHING ELSE HERE DEPENDS ON IT:
#
#     `(a, b)` means **`b` OUTLIVES `a`.** `a`'s retire predicate may READ `b`; `a`'s
#     content is reconstructible from `b` (and from whatever is above `b`). Equivalently
#     `tier(write) < tier(read)` for every retire statement — the DRAIN order.
#
# ⚑⚑ AND THE ANTI-READING, BECAUSE THIS FILE ALREADY CONTAINS PROSE IN THE OTHER SENSE. It
# is NOT the BUILD order (*"b is derived from a"*). `VOCAB_TABLES`' note is written in the
# build sense — *"every row here is recoverable from `core_decoded` by re-running the rung"*
# — which reads as `vocab < sourced`, while `core_decoded`'s retire READS `dec_scalar`,
# which is `sourced < vocab`. Both sentences are true; only one of them is an ORDER. Read in
# the build sense this relation is CYCLIC ON A CORRECT LADDER, which `scripts/tier_readset.py`
# measured independently for the promote edges (`tree ↔ valstage`, the memo). A reader who
# takes the wrong sense gets a contradiction, not a wrong answer — but only if they finish.
#
# ⚑⚑ WHY PAIRS AND NOT A LIST OF TIER NAMES. A `TIER_ORDER = ["sourced", …]` roster would do
# two things this must not: duplicate `_TIERS`' key roster (the `_TIER_VIEWS` defect — a
# second list to keep in sync, and the failure direction is silent), and assert a TOTAL order
# where the truth is partial. Nothing puts `vocab` below `tree` or `tree` below `vocab`, and
# a total order would invent that precedence. Pairs enumerate no names: a tier related by no
# pair is simply UNORDERED, `tier_readset` counts and PRINTS the unordered pairs, and the
# incompleteness is a measured number instead of a silence.
#
# ⚑ UNDER-DECLARED ON PURPOSE — every pair carries a WITNESS in this corpus, and a pair
# without one is left out rather than guessed. `orbit`, `argperm` and `obsnode` say only
# *derived and disposable* without naming the tier they are derived FROM, so ordering them
# would be invention. `event`'s internal membership is KNOWN WRONG (F10: `terms`/`path_seg`/
# `path_text` sit in the event tier while `_node`/`_unit`/`ref` hold ids into them) — an
# order over a tier whose membership is a filed defect would freeze the defect.
#
# ⚑ THE COST OF UNDER-DECLARING IS EXACTLY THE HOLE THIS EXISTS TO NARROW, and it is
# reported rather than absorbed: on an unordered pair the gate's at-or-below rule cannot
# fire, so a retire reading down between two unordered tiers still passes. Adding a
# witnessed pair here is how that number goes down.
#
# ⚑ `why` IS NOT DECORATION — it is `lifecycle.Chain`'s LOCATED-REJECTION discipline
# (*"`Rejected` names WHICH link failed versus 'something earlier did'"*) applied one level
# up: a refusal quotes the reason the pair was declared, so the reader learns why the order
# is what it is at the moment they are told they violated it.
TIER_BELOW = (
    (
        "sourced",
        "tree",
        "`dec_drain.retire_sql` DELETEs `core_decoded` on the strength of "
        "`core_decoded_shadow`, which selects `dec_root` and `dec_node`; and `TREE_TABLES`' own "
        "note: `dec_root` is the only carrier of four of `core_decoded`'s five columns, so "
        "*the tree tier WITHOUT it does not reconstruct the tier below*",
    ),
    (
        "sourced",
        "vocab",
        "the same shadow selects `dec_scalar`: the `dec` value cannot be rebuilt without the "
        "string vocabulary, so `core_decoded` may not be retired while `vocab` is gone",
    ),
    (
        "sourced",
        "valstage",
        "the same shadow selects `dec_val`. ⚑ This is an ACQUISITION fact, not a durability "
        "claim: `valstage` is a MEMO (*`--flush valstage` must be a no-op against "
        "correctness*), and a missing row makes the shadow REFUSE rather than answer wrongly — "
        "it withholds the licence, it never licenses a wrong DELETE",
    ),
    (
        "treestage",
        "tree",
        "`dec_drain.retire_ref_sql` / `retire_stage_sql` DELETE `dec_ref` / `dec_stage` on the "
        "strength of `dec_root`. ⚑ THIS IS THE PAIR `_TIERS`' INSERTION ORDER GETS BACKWARDS, "
        "and it is why that note's claim to be the order was withdrawn",
    ),
    (
        "sourced",
        "event",
        "`core_decoded`'s note, twice: *the decoded core, WHOLE — below the event tier*, and "
        "*the event tier is what a SHREDDER makes of this row; this row is the material it "
        "shreds*, under the model's rule *each tier must be reconstructible losslessly by the "
        "tiers it replaces*",
    ),
    (
        "ref",
        "sppf",
        "`REF_TABLES`' note: `ref` is *an INDEX over SPPF × fibre, not a factor of it — "
        "rebuildable at any time, and safe to drop without losing a fact*, and *nothing "
        "reconstructs FROM it*, so nothing may sit below `ref`",
    ),
)


def _tier(back, tier):
    """The DDL for one tier — its tables, their indexes, and its SHADOW.

    ⚑ *"and its views"* WAS THE THIRD CLAUSE HERE UNTIL 2026-08-12 (⟡view-purge); it
    read `out += [s for name, s in _view_ddl_named(back) if name in _TIER_VIEWS.get(tier,
    ())]`. A tier is a set of RELATIONS that drain; a fragment is neither applied nor
    drained, so it has nothing to contribute to a tier's DDL.

    ⚑⚑ AND THE CLAUSE IS BACK 2026-08-13 WITH A DIFFERENT MEANING, WHICH IS WHY THE OLD ONE
    IS QUOTED RATHER THAN EDITED. A fragment still contributes nothing; a SHADOW is not a
    fragment — it is the tier's own reconstruction CLAIM about the tier below, and it must
    exist wherever that tier does or the drain has no licence to read. The membership is
    read off `SHADOWS`, whose value names the OWNING tier, so there is no second roster:
    `_TIER_VIEWS` was deleted precisely because it was one.
    """
    import store

    d = store.dialect(back)
    try:
        want = _TIERS[tier]
    except KeyError:
        # ⚑ REFUSE AN UNKNOWN TIER rather than defaulting. `want = A if t=="event" else B`
        # was the old shape: a typo'd tier name silently applied the sppf tier, creating
        # the wrong tables and reporting success.
        raise ValueError(f"unknown tier {tier!r}; known: {sorted(_TIERS)}")
    out = [
        str(CreateTable(t, if_not_exists=True).compile(dialect=d)).strip()
        for t in MD.sorted_tables
        if t.name in want
    ]
    out += [
        str(CreateIndex(ix, if_not_exists=True).compile(dialect=d)).strip()
        for ix in INDEXES
        if ix.table.name in want
    ]
    out += view_ddl(back, want={n for n in SHADOWS if SHADOWS[n][1] == tier})
    return out
