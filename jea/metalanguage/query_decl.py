# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""query_decl.py — ⟡qinfra: the DECLARATION + the BUILDERS. Everything `query_defs.py` MEASURES.

The lightweight `Table` shims and the ~67 named `q_*` / `v_*` `select()` builders — the
SINGLE SOURCE for the project's SQL read-queries. `query_defs.py` is the measurement/CLI
layer over them and re-exports every name here, so `query_defs.<name>` still resolves.

⚑ REFLECTION-FREE LIGHTWEIGHT TABLES, verbatim from the header this file was cut out of,
because it is the rule governing `_T`: *"a SELECT compiles correctly from `Column(String)`
regardless of declared type (we never write, only read/intern). Views are modelled as Tables
of their OUTPUT columns."* `schema_decl.py` is where the REAL types, keys and indexes live,
and its own ⚑ block records why this shim is not usable as a schema.

⚑⚑ SPLIT OUT OF `query_defs.py` 2026-08-12, AND THE SEAM IS THE ARROW, NOT THE LINE COUNT.
`query_defs.py` stood at 1,197 code lines against its 1,200 cap — three lines of headroom,
i.e. the next builder could not be written. But a positional cut would have put half the
tables in one file and half their readers in the other; what makes THIS cut sound is that the
dependency runs ONE WAY. The tooling (`INTERN_BUILDERS`, `REFERENCE_ARMS`, `_reg`, `verify`,
`do_scans`, `do_equiv`, `--compile`/`--check`, `touching`, `main`) calls the builders; NO
builder here calls the tooling. So the split needs no import cycle, no shim and no deferred
import — exactly the property `schema_decl.py` records for its own cut.

⚑⚑ WHICH HALF MOVED, AND THE SELF-INSPECTION DECIDED IT — the rule `schema_decl.py` states as
*"the cut stops where the introspection begins"*, applied in the direction it actually points
here. Three sites in the other half resolve relative to "this file", and they do NOT agree:

  * `compile_text` bakes `python3 jea/metalanguage/query_defs.py --compile` into the GENERATED
    header of `query_sql_postgres.py`, and `do_check` prints the same path as its remedy. Both
    are still TRUE only because `--compile` stayed in `query_defs.py`. Had the CLI moved
    instead, the generated cache would instruct the next reader to run a mode that file no
    longer has — and `--check` would still be GREEN, because it diffs the text it just
    generated against the text it generated last time. A silent wrong answer, which is the
    whole hazard class; it is why the CLI is the half that stayed.
  * `_cache_path` and `HERE` read `__file__` as a DIRECTORY. That is invariant under a SIBLING
    emission (and is precisely why these are siblings and not a subpackage), so it does not
    decide the cut either way.
  * `touching()` walked `dir(sys.modules[__name__])` for `q_*` names, and that one DID move
    out from under it. It would still have PASSED via the star re-export — which is the
    hazard's exact signature, an introspection that answers about a smaller thing and looks
    fine — so it now names this module explicitly. See its ⚑ note in `query_defs.py`.

⚑ AND `_reg` / `verify` STAYED WITH THE TOOLING, WHICH IS THE OTHER HALF OF THE SAME HAZARD.
`_reg` names every builder directly and `verify` pairs each against its ORIGINAL raw SQL;
both still see what they police through the re-export. But "the names resolve" is not the
evidence — `--check` reporting NO DRIFT, builder by builder, is: it is the only mechanical
statement that the compiled SQL is unchanged by the move.

⚑ THE CONSUMER SURFACE WAS MEASURED, NOT ASSUMED. `pycodemod --importers query_defs` (a mode
built for this split, because `--imports` only COUNTS and `--attr query_defs.*` reports zero —
every consumer spells it `from query_defs import …`, which reads no attribute): five files,
six sites, reaching `run`, `INTERN_BUILDERS`, `q_reach`, `q_edges_dst_distinct`,
`q_indegree_top` and `FREE_CTORS`. None `_`-prefixed, so the `schema._node` class — a `_` name
silently dropped by `import *` while every suite reads green — has no live instance here. The
underscore names are re-imported BY NAME beside the star regardless.
"""

import os, sys
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    String,
    Text,
    Integer,
    select,
    bindparam,
    func,
    literal,
    and_,
    or_,
    literal_column,
    union_all,
    except_,
    case,
    cast,
    exists,
    distinct,
    ARRAY,
)

# ⚑ POSTGRES-SPECIFIC, AND DELIBERATE for the same reason `JSONB` below is: `array_agg(x ORDER BY
# y)` has no portable SQLAlchemy spelling, and the ORDER BY inside the aggregate is not
# decoration — `(f a b)` and `(f b a)` are different terms with the same child SET, so an
# unordered array_agg would merge them. The ordered form is the signature's child component.
from sqlalchemy.dialects.postgresql import aggregate_order_by

# ⚑ POSTGRES-SPECIFIC TYPE, IMPORTED DELIBERATELY. The decode→jsonb chain is how the engine
# reads an `ekey`, and there is no portable spelling — sqlite has no jsonb cast. A builder
# using it is postgres-only BY CONSTRUCTION, which the per-backend compile already models
# (`query_sql_postgres.py` vs `query_sql.py`), so the type is honest rather than a leak.
from sqlalchemy.dialects.postgresql import JSONB

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import store as _store  # THE store authority: dsn, dialect, connect

# ⚑ THE REFERENTIAL CTORS, IN ONE PLACE — and this is now the THIRD spelling, which is the
# finding. `jea_agdai` declares `FREE` as a LOCAL inside a function (so it cannot be
# imported), `sppf_db:34` declares its own module-level copy, and `scope_fix` imports
# `_FREE_CTORS` from somewhere else again. A shared NAME is not a shared authority — the
# defect this repo has paid for in `agda_files()` (four bodies) and `CATALOG_DB` (eight
# derivations). Homed here because this module is already the single source for the QUERIES
# that consume it; lifting `jea_agdai`'s local to a module constant and importing it
# everywhere is the real fix, and it is owed.
FREE_CTORS = {"Def", "Con", "Prim", "PrimSort", "Proj", "PCon", "PDef", "PProj"}
_MD = MetaData()


def _T(name, *cols):
    return Table(name, _MD, *[Column(c, String) for c in cols])


# ── base tables ─────────────────────────────────────────────────────────────────────────────────
path_text = _T("path_text", "path_id", "text")
terms = _T("terms", "term_id", "text")
path_seg = _T("path_seg", "path_id", "ord", "seg_term_id")
_unit = _T(
    "_unit",
    "unit_id",
    "name_pid",
    "root_id",
    "file_id",
    "kind_id",
    "module_pid",
    "root_lid",
    "copy",
    "level",
)
_unit_cod = _T("_unit_cod", "unit_id", "cod_ctor_id", "cod_qname_pid")
_node = _T("_node", "node_id", "kind_id", "role_id", "op_term_id", "op_path_id", "lit_id")
node_child = _T("node_child", "node_id", "ord", "child_id")
unit_node = _T("unit_node", "unit_id", "node_id")
unit_member = _T("unit_member", "unit_id", "ord", "member_name_pid", "member_unit_id")
# ⚑ `seq` WAS MISSING FROM THIS MODEL WHILE BEING THE QUEUE'S ENTIRE COORDINATE. The column
# has existed since the watermark migration (`schema.obs`, `Identity`), but no builder could
# reference it — so every queue-shaped question was necessarily answered by raw SQL elsewhere,
# which is how `reclaim` came to be six hand-written statements. A model that omits a column
# does not merely lack a feature; it FORCES the withheld-algebra shape it exists to prevent.
obs = _T("obs", "core_id", "local_id", "ekey", "seq")
event = _T("event", "ekey", "ctor_id", "qname_pid", "idx", "lit_id")
unit_obs = _T(
    "unit_obs",
    "core_id",
    "unit_id",
    "name_pid",
    "root_lid",
    "kind_id",
    "module_pid",
    "copy",
    "level",
)
edge = _T("edge", "core_id", "plid", "ord", "clid")
meta = _T("meta", "key", "value")
_orbit_def = _T("_orbit_def", "unit_id", "type_key", "graded_key", "residue", "stab")
# ⚑ `orbit_node` / `orbit_member` REMOVED 2026-08-23 with the orbit tier — superseded by the
# compound-identity framing. `_orbit_def` above is the ARGPERM tier and is unaffected.
core_fp = _T("core_fp", "core_id", "mtime")  # ⟡gqs-S1 incremental-decode fingerprint
# ⚑ THE ADDRESSING INDEX + THE CHILD FIBRE (Ⓒ1). `obs_node` was absent from this model, which
# an audit flagged as the single mechanical blocker on expressing the drain licence as a
# builder — a relation the store has held since Q17, unreachable from the compile path. `ch`
# is the carrier added 2026-08-11; together they are what makes `determined` a query rather
# than a Python loop.
obs_node = _T("obs_node", "core_id", "local_id", "node_id", "ch")
ref = _T("ref", "core_id", "plid", "qname_pid", "arg_ord", "arg_lit_id")
# ── the DECODE TIERS (⟡dec-model): tree / treestage / valstage / vocab ──────────────────────
#
# ⚑⚑ ADDED BECAUSE THE OMISSION WAS FORCING THE WITHHELD-ALGEBRA SHAPE, which is the SAME
# finding `obs.seq` records forty lines up and the reason that note ends *"a model that omits a
# column does not merely lack a feature; it FORCES the withheld-algebra shape it exists to
# prevent."* Applied here to whole RELATIONS rather than one column: `dec_tree.py` and
# `dec_drain.py` carry ~50 hand-written `(sql, params)` functions — `round_sql`, `chain_sql`,
# `reach_sql`, `retire_sql`, `digest_sql`, `census_sql` &c. — a PARALLEL query layer that grew
# because no builder could name these relations. `pycodemod --relalg jea/metalanguage/dec_tree.py`
# reports **0 withheld-algebra sites**: that family is already SQL, and was outside the compiled
# set only because the model could not reach it, never because the algebra was withheld.
#
# ⚑ WHAT THIS COMMIT DOES AND DOES NOT DO. It makes the relations REACHABLE — `--touching` now
# answers about them instead of printing NOT DECLARED, so the parallel layer becomes a COUNTED
# population rather than an invisible one. It migrates NO query; each `*_sql` is its own
# judgement (⟡dec-lift), and the recursive fixpoint rounds may not compile at all — postgres
# bans GROUP BY / aggregates / window fns in a recursive term, the constraint `q_obs_height`
# already records. Reachability first, migration per-query, and an honest residue at the end.
#
# ⚑ DECLARING A RELATION IS NOT CLAIMING A BUILDER READS IT. `--touching` distinguishes three
# provenances, and a newly-declared relation with zero readers reports exactly that — which is
# the point: an EMPTY reader list against a DECLARED relation is a measurement, while NOT
# DECLARED is the absence of one. This turns ⟡dec-lift's roster from a prose claim into a query.
#
# ⚑ THE TYPE PUN IS `schema_decl`'s TO STATE, NOT THIS SHIM'S. Under `LEAF(s, 0)` the `c1` slot
# holds a `dec_scalar.id`; under every other head `c1`/`c2` hold a `dec_node.id`, with `0` the
# nullary child. `_T` models every column as `Column(String)` by construction (the header's
# rule: we read and intern, never write through this shim), so the pun is invisible here and
# MUST stay documented at its authority. A reader who learns the child space from this line
# alone learns it wrong.
dec_node = _T("dec_node", "head", "c1", "c2", "id")
dec_root = _T("dec_root", "core_id", "relpath", "mtime", "producer", "root")
dec_stage = _T(
    "dec_stage",
    "core_id",
    "sid",
    "ord",
    "kind",
    "rnd",
    "head",
    "a1_sid",
    "a1_ord",
    "a1_kind",
    "l1",
    "a2_sid",
    "a2_ord",
    "a2_kind",
    "l2",
)
dec_ref = _T("dec_ref", "core_id", "sid", "ord", "kind", "head", "c1", "c2")
dec_val = _T("dec_val", "id", "v")
dec_scalar = _T("dec_scalar", "id", "v")
# ⚑ `core_decoded` IS THE TIER BEING RETIRED, and it is declared for that reason rather than in
# spite of it: the drain licence is a statement ABOUT it (`dec_drain.py:298` counts it against
# the shadow), so a model that omits it cannot express the very question the ladder asks.
# ⚑ AND `core_decoded_shadow` IS A VIEW, modelled as a Table of its OUTPUT columns — the header's
# stated rule. It is NOT a `_T` over a stored composition of the ⟡view-purge kind purged below:
# that view is DECLARED in `schema_decl.SHADOWS` and materialised from it, so naming it here
# points at the declaration's own artifact rather than minting a second spelling of a body.
core_decoded = _T("core_decoded", "core_id", "relpath", "mtime", "producer", "dec")
core_decoded_shadow = _T("core_decoded_shadow", "core_id", "relpath", "mtime", "producer", "dec")


def _nullable_scope(col, name):
    """`(:p IS NULL OR col = :p)` — the family's "all documents, or exactly one" idiom.

    ⚑⚑ ONE HELPER BECAUSE THE RAW FORM SPELLS THE PARAMETER TWICE AND THE TWO MUST NOT DRIFT.
    Every statement in `dec_drain.py` scopes with `(%s::text IS NULL OR c.core_id = %s::text)`
    and every caller passes `(core_id, core_id)` — the SAME value, positionally, twice. That is
    two spellings of one fact, and `census-keyed-on-one-spelling` is this repo's name for what
    goes wrong when a relation is keyed that way: a caller that updates one occurrence and not
    the other produces a statement that still compiles and silently scopes to nothing.

    ⚑ A NAMED `bindparam` COLLAPSES THE PAIR TO ONE. SQLAlchemy renders the same name at both
    sites and the runtime binds it ONCE, so `(core_id, core_id)` becomes `{"scope": core_id}`
    and the drift is not merely discouraged, it is unspellable.

    ⚑⚑ THE `::text` CAST IS EMITTED EXPLICITLY, AND `type_=String` ALONE IS NOT ENOUGH —
    MEASURED, not reasoned. A first cut of this helper declared the bind's type and trusted
    SQLAlchemy to render it; the compile succeeded, `--check` went green, and `--explain`
    against postgres failed with **`DatatypeMismatch: type of parameter 1 (text) does not match
    that when preparing the plan (unknown)`**. Inside `%(p)s IS NULL` there is no column to
    infer from, so postgres prepares the plan with the parameter as `unknown` and then receives
    `text` at execute. The declared type governs how the DRIVER sends the value; it does not put
    a cast in the SQL. `dec_drain.py`'s raw form spells `%s::text` at BOTH occurrences for
    exactly this reason — a detail that reads like noise until it is the whole defect.

    ⚑ SO THIS IS THE CASE FOR TRANSLATING THE FLAT RUNG FIRST. The failure is invisible to
    `--compile`, `--check` and `--selftest` — three green gates over a statement that cannot
    execute — and only an EXPLAIN against a real backend catches it. Had this been discovered
    inside a four-fragment CTE chain it would have been attributed to the CTE.

    ⚑ `value=None` MAKES THE UNSCOPED FORM THE DEFAULT — the same reading the raw callers give
    it (`core_id=None` in every signature). `--sql` can then render the statement standalone.
    """
    p = cast(bindparam(name, value=None, type_=String), Text)
    return or_(p.is_(None), col == p)


# ⚑⚑ THE FIRST RUNG OF ⟡dec-lift, AND IT IS THE FLAT ONE ON PURPOSE. `dec_drain._ANSWER` is a
# plain SELECT over the shadow with a nullable scope — no CTE, no `ON CONFLICT`, no lock-order
# `ORDER BY` to preserve — so it is where the TRANSLATION ITSELF can be verified before the
# composed rungs rely on it. The family's hard cases (`round_sql`'s four-fragment CTE chain,
# `rebuild_sql`'s fixpoint) are deliberately NOT here.
#
# ⚑⚑ AND IT IS THE LADDER'S WHOLE CLAIM AS A STATEMENT, WHICH IS WHY IT IS WORTH COMPILING
# FIRST. `dec_drain.py`'s own note: *"After the drain, `core_decoded` holds nothing for these
# documents and the shadow still answers for every one of them — `relpath`, `mtime`, `producer`
# and `dec`, byte-identical."* Compiled, that claim becomes `--explain`-able and drift-gated
# rather than a string the caller interpolates.
#
# ⚑ IT READS THE SHADOW AND NOTHING ELSE, DELIBERATELY. A separate reader would be a second
# reconstruction — `dec_drain.py`'s rule, *"the one thing this arc may not have two of"* — so
# this builder is the view, scoped and ordered, and adds no expression of its own.
def q_dec_answer():  # ⟡dec-lift: a RETIRED document, from the durable tiers
    """One document (or all), read back from `core_decoded_shadow` alone.

    ⚑ `ORDER BY relpath` REPRODUCES THE RAW FORM'S `ORDER BY 2` — positional in the original
    because the column list is fixed there. Named here: a positional ORDER BY over a compiled
    projection is a silent reordering waiting for someone to insert a column.
    """
    return (
        select(
            core_decoded_shadow.c.core_id,
            core_decoded_shadow.c.relpath,
            core_decoded_shadow.c.mtime,
            core_decoded_shadow.c.producer,
            core_decoded_shadow.c.dec,
        )
        .where(_nullable_scope(core_decoded_shadow.c.relpath, "relpath"))
        .order_by(core_decoded_shadow.c.relpath)
    )


# ⚑ THE `sqlite_master` TABLE IS GONE FROM THE MODEL (⓺). Declaring it made a
# sqlite-only catalogue reachable from the DIALECT-AGNOSTIC builder layer — the one layer
# whose whole premise is that a Core statement ports for free. `schema.relations()` is
# where "what does the store hold" lives; a model entry for the other engine's catalogue
# is a hole straight through that abstraction.
# ── the former projection VIEWS, now COMPOSED FRAGMENTS ─────────────────────────────────────
#
# ── `node_v` / `unit_v` / `node_fanin` / `shared_subtree` as `_T(…)` SHIMS — DELETED
# ── 2026-08-12 (⟡view-purge). They read:
#
#     node_v     = _T("node", "node_id", "sym", "kind", "role", "op", "lit")
#     unit_v     = _T("unit", "unit_id", "name", "root_id", "path", "kind", "copy")
#     node_fanin = _T("node_fanin", "node_id", "fanin")
#     shared_subtree = _T("shared_subtree", "node_id", "fanin")
#
# ⚑⚑ A `_T` OVER A VIEW IS A SECOND SPELLING OF THE QUERY ALGEBRA, and the argument against
# it was already recorded in this arc for a different feature and never applied backwards:
# *"A DB view would be a second spelling of the query algebra living OUTSIDE `--check`'s drift
# gate and outside `--verify` — the same argument `q_edge_disagreement` already makes against
# `text()` blobs."* Three consequences, all of them live until now: a view is schema state that
# must be created, dropped and kept in sync (`project_sppf` DROPped and recreated them every
# non-additive run); a view has no TIER, so it sat in the schema namespace pretending to be a
# relation that `--census` counted; and a view is a FROZEN composition — a Core selectable can
# be parameterised and pushed into a larger statement, a view can only be selected from.
#
# ⚑ THE COMPOSITION ALREADY EXISTED, so this is a REMOVAL rather than a rewrite. `schema_decl`
# has held `node_sel` / `unit_sel` / `node_fanin_sel` / `shared_subtree_sel` as Core `select()`
# objects since the port; `sqlalchemy_views.CreateView` merely MATERIALISED them into DDL, and
# what is purged is that materialisation step. `.subquery(<name>)` keeps `.c` and `.alias()`,
# so every builder below is unchanged in shape — only the FROM is now the body instead of a
# name pointing at a stored copy of the body.
#
# ⚑ IMPORTED, NOT RE-EXPRESSED OVER THE `_T` SHIMS, AND THAT IS THE WHOLE POINT. This module
# carries its own untyped `_T("_node", …)` / `_T("terms", …)` models, so a fragment could have
# been rebuilt here over them — which would have recreated the second spelling one layer down,
# free to drift from the declaration exactly as the view body was. `schema_decl` is the
# relation authority (its own note: *"the facts are declared HERE … and `query_defs` keeps its
# shim for querying"*), so the fragment bodies stay there and this module names them.
#
# ⚑ AND THE ARROW IS THE ONE THAT ALREADY EXISTED. `schema_decl` imports nothing from here and
# defers even `store`; the docstring above records that the SAME one-way property is what made
# both this cut and `schema_decl`'s own sound. So this needs no cycle, no shim, no deferred
# import — the header's rule, applied to one more edge.
from schema_decl import (
    node_sel as _node_sel,
    unit_sel as _unit_sel,
    node_fanin_sel as _node_fanin_sel,
    shared_subtree_sel as _shared_subtree_sel,
)

node_v = _node_sel.subquery("node")
unit_v = _unit_sel.subquery("unit")
node_fanin = _node_fanin_sel.subquery("node_fanin")
shared_subtree = _shared_subtree_sel.subquery("shared_subtree")
# reuse_catalog base tables (backing the compat VIEWS — where the path_text.path_id breadth lives)
_structs = _T("_structs", "qname_pid", "name_id", "kind_id", "module_pid", "desc_id", "root")
_members = _T("_members", "struct_qname_pid", "struct_root", "name_id", "ord")
_member_heads = _T("_member_heads", "struct_qname_pid", "struct_root", "head_id")
_refs = _T("_refs", "struct_qname_pid", "ref_qname_pid")
_edges = _T("_edges", "src_pid", "dst_pid")
_module_edges = _T("_module_edges", "src_pid", "dst_pid")
_modules = _T("_modules", "module_pid", "purpose_id", "is_index")
# reuse_catalog compat VIEWS as OUTPUT-column Tables (physical views in catalog.db; SELECT straight from them
# to REPRODUCE render rows — distinct from the simplified v_* interning models above) ── ⟡rewire-catalog-render
structs_v = _T("structs", "qname", "name", "kind", "module", "fp", "desc", "root", "unhold_fp")
edges_v = _T("edges", "src", "dst")
modedges_v = _T("module_edges", "src", "dst")
modules_v = _T("modules", "module", "purpose", "is_index")
indegree_v = _T("in_degree", "qname", "deg")


def run(con, stmt, **params):
    """Compile a Core `stmt` for the ACTIVE backend and execute it on an EXISTING connection.

    ⚑ THE DIALECT IS NO LONGER SPELLED HERE (2026-08-06). It was
    `sqlite.dialect(paramstyle="named")` at this line AND at `_compile_one`, so the live
    executor and the committed `query_sql.py` cache each named the target independently —
    two spellings of one fact, free to drift while both looked right. `store.dialect()`
    is the single authority; this is one of its two consumers.

    ⚑ AND THIS IS WHY THE SQLALCHEMY LAYER IS THE MIGRATION PATH. A Core statement is
    dialect-agnostic for everything SQLAlchemy MODELS, so all 63 builders port when this one
    call changes. MEASURED across the corpus: 146 compiled-builder sites vs 58 raw-SQL ones,
    and the raw set is full of things that CANNOT port (`sqlite_master`, `INSERT OR REPLACE`,
    `GROUP_CONCAT`, `rowid`). Core-vs-raw is the line between free and hand-written.

    ⚑⚑ EXCEPT AT `func.<name>`, AND THIS FILE IS THE WORST CASE OF IT. `func` passes an
    ARBITRARY name through verbatim — SQLAlchemy has one generic registry (52 names) and no
    per-dialect list, so `func.totally_made_up_xyz` compiles silently on every dialect. That
    is not a hypothetical here: **`query_decl.py` holds 34 of the corpus's 40 verbatim
    `func.` calls** (`hashtext`, `convert_from`, `string_to_array`, `jsonb_array_elements_text`,
    …), measured by `pycodemod --funcnames --verbatim`, not by eye. They are
    correct for THIS tenant and they are exactly what would NOT port when this one call
    changes. So the paragraph above is true of the statement STRUCTURE and false of the
    function NAMES, and the file asserting "ports for free" is the file most full of the
    exceptions. `pycodemod --funcnames --verbatim` is the census; `store.py`'s
    migration-path paragraph carries the full statement of the boundary.
    ⚑ The cost of not having this written down was `autocorr_synth.synth_agda` using
    `func.group_concat` — named as unportable in the sentence above, in a CORE site the
    sentence classified as free — and raising `UndefinedFunction` on every invocation from
    the migration until 2026-08-19, with `--portable` reading green over it throughout.

    Column order is preserved (drop-in for Row/positional reads); params bind as a dict
    under both dialects — `:x` on sqlite, `%(x)s` on postgres.
    """
    compiled = stmt.compile(dialect=_store.dialect())
    p = dict(compiled.params)
    p.update(params)
    return con.execute(str(compiled), p)


# ════════════════════════════════════ M1 — path_text.path_id carriers ════════════════════════════
def q_node_head():  # reuse_tui db_rows L92-96
    o = terms.alias("o")
    r = terms.alias("r")
    return select(_node.c.node_id, path_text.c.text, o.c.text, r.c.text).select_from(
        _node.outerjoin(path_text, path_text.c.path_id == _node.c.op_path_id)
        .outerjoin(o, o.c.term_id == _node.c.op_term_id)
        .outerjoin(r, r.c.term_id == _node.c.role_id)
    )


def q_unit_names():  # reuse_tui db_rows L149
    return select(_unit.c.unit_id, path_text.c.text).select_from(
        _unit.join(path_text, path_text.c.path_id == _unit.c.name_pid)
    )


def q_event_head():  # sppf_db project_sppf / project_orbit_sppf (head + ⟡gqs-lit-propagate lit)
    tc = terms.alias("tc")
    pq = path_text.alias("pq")
    lt = terms.alias("lt")
    return select(event.c.ekey, tc.c.text, pq.c.text, event.c.idx, lt.c.text).select_from(
        event.join(tc, tc.c.term_id == event.c.ctor_id)
        .outerjoin(pq, pq.c.path_id == event.c.qname_pid)
        .outerjoin(lt, lt.c.term_id == event.c.lit_id)
    )


def q_event_head_core():
    """`q_event_head` scoped to ONE core — the events that core actually observes.

    ⚑⚑⚑ THE SCOPE ARRIVES BY SEMI-JOIN BECAUSE `event` HAS NO `core_id`, AND THAT IS NOT AN
    OVERSIGHT TO INDEX AWAY. `event` is CONTENT-ADDRESSED on `ekey`: the same event observed by
    fifty cores is ONE row, which is the sharing the tier exists for. So there is no column to
    filter and no index that would help — *"the events of this core"* is not expressible on
    `event` alone. It is expressible on `obs`, which is exactly the relation that carries the
    `(core_id, local_id) → ekey` fibre.

    ⚑⚑ MEASURED, `schema.py --plan` on the live store: the scoped form estimates **25,468 rows
    at cost 290,645** against a `event` relation of **24,580,540 rows** — ~1,000× less work,
    with NO NEW INDEX. Every access path already exists and the planner uses all of them:

        Bitmap Index Scan  ix_obs_pk   (core_id = …)      → 34,396
          HashAggregate    (distinct ekey)                → 18,871
            Index Scan     event_pkey  (ekey = obs.ekey)  → 1 each
              Memoize + terms_pkey                        → cached

    ⚑ SO THE MISSING THING WAS A PREDICATE, NOT AN INDEX (operator, 2026-08-21: *"I don't buy
    that we need to scan the entire corpus to find a subset of the data. That screams 'we're
    missing an index'."* — right about the shape, and the correction is only which piece was
    absent). `project_sppf` scopes its FOLD and its WRITES by `core_id` while its READS took the
    whole corpus: measured, 181,174 observations spent ~40 minutes almost entirely reading.

    ⚑ `IN (SELECT …)` IS A SEMI-JOIN, DELIBERATELY, and not `DISTINCT` — the same argument
    `_live_cores` records: postgres de-duplicates as part of the join, so spelling `DISTINCT`
    would add a sort/hash the planner already performs and would claim the dedup is load-bearing
    where a membership test is what is meant.
    """
    tc = terms.alias("tc")
    pq = path_text.alias("pq")
    lt = terms.alias("lt")
    return (
        select(event.c.ekey, tc.c.text, pq.c.text, event.c.idx, lt.c.text)
        .select_from(
            event.join(tc, tc.c.term_id == event.c.ctor_id)
            .outerjoin(pq, pq.c.path_id == event.c.qname_pid)
            .outerjoin(lt, lt.c.term_id == event.c.lit_id)
        )
        .where(
            event.c.ekey.in_(
                select(obs.c.ekey).where(
                    obs.c.core_id == bindparam("core_id", value="", type_=String)
                )
            )
        )
    )


def _live_cores(one_core=False):  # ⟡tier-scope: the semi-join key, in ONE place
    """The cores tier 0 STILL HOLDS — what every conjunct of the drain licence is bounded by.

    ⚑⚑ ONE SPELLING, BECAUSE THE SCOPING IS ONE FACT ASKED IN THREE PLACES. `q_drainable`'s
    minuend is a set of `obs.core_id` and all three of its subtrahends are computed over the
    DURABLE tier, which grows monotonically and forever; this is the intersection that makes
    each of them O(live) instead. A second literal `select(obs.c.core_id)` at each site would
    be three spellings of one predicate, free to drift — the defect this module exists to be
    the single source against, and the reason `_rebuilt_edges` was homed rather than copied.

    ⚑ IT IS NOT `DISTINCT`, DELIBERATELY. `IN (SELECT …)` is a SEMI-JOIN: postgres
    de-duplicates as part of the join, and MEASURED it drives `ix_obsnode_pk` /
    `ix_edge_child` as a bitmap index scan per live core. Spelling `DISTINCT` would add a
    sort/hash the planner already performs, and would say the dedup is load-bearing when the
    membership test is what is meant.

    ⚑⚑⚑ AND `one_core=True` NARROWS IT TO A SINGLE CORE — the predicate belongs HERE, not
    around the licence's output (operator, 2026-08-21: *"Don't forget the predicate!"*). A first
    cut wrote `SELECT core_id FROM (<licence>) d WHERE core_id = :c`, which computes the
    CORPUS-WIDE drainable set and throws all but one row away. `q_drainable_res`'s own docstring
    already names that failure one level up — *"the unscoped licence READ the thing that never
    shrinks while its ANSWER was bounded by the thing that does"* — so scoping the OUTPUT is not
    scoping the WORK, and the fix is the same one that function already applied to its
    subtrahends.

    ⚑⚑ ONE EDIT REACHES ALL EIGHT SEMI-JOINS, which is the payoff of this function existing.
    `--sql drainable_res` spells `IN (SELECT obs.core_id FROM obs)` EIGHT times across five
    `EXCEPT` arms, and every one of them gets it by calling here. Eight literal copies would
    have been eight places to forget — the drift this module was homed to prevent.
    """
    q = select(obs.c.core_id)
    if one_core:
        q = q.where(obs.c.core_id == bindparam("rc_core", value="", type_=String))
    return q


def q_drainable_res(
    _live_scope=True, _obs_edge_conjunct=True, one_core=False
):  # ⟡tier-residue: the licence with NO stored position
    """The cores that may drain, as a RESIDUE — the whole licence as ONE conjunction, one snapshot.

    ⚑⚑ `q_drainable` — THE POSITIONAL BUILDER — DELETED 2026-08-12 INTO THIS ONE. Two builders
    existed because one flag (`_residue_only`) selected between two DESIGNS: `q_drainable`
    conjoined `below = select(obs.c.core_id).group_by(obs.c.core_id).having(func.max(obs.c.seq)
    < bindparam("floor"))`, and `q_drainable_res` was literally `q_drainable(_residue_only=
    True)`. **A flag whose two settings are two designs is an unfinished migration wearing
    one** — this arc's own sentence about `reclaim(residue=…)` one step earlier — so the
    parameter is deleted, not defaulted. Its two ⚑ notes, kept because they are the argument:

    *"THE UNIT IS THE CORE, AND `HAVING max(seq) < floor` IS WHY: `seq` is log-wide while
    `local_id` is per-core and dense, so a positional cut slices ACROSS cores and leaves a
    PREFIX of one fibre"* — with F14's boundary, where the core holding the top position can
    never drain because the floor IS the hwm and `<` fails by exactly one. Per-core conjuncts
    have no such boundary. And: *"`bindparam`, NOT `literal(floor)` … the compiled cache is
    generated ONCE and reused, so a `literal` freezes whatever floor held at compile time into
    every later run."* A licence with nothing to bind cannot bake a stale scalar.

    ⚑⚑ UNDER `NOT EXISTS`, hwm AND lwm ARE BOOLEAN PREDICATES (user, 2026-08-11: *"I see it's
    looking at hwm and lwm. I'll note that under IF NOT EXISTS, hwm and lwm are boolean
    predicates."*). A draw-hwm asks *may I read further?*; a feed-lwm asks *have I released
    everything I drew?*; the RESIDUE is their difference — and `Substrate.Lifecycle.Residue`
    already names it: *"drawn but not yet fed … a residue of zero is an actor fully caught up"*.
    `ActorWedge`'s `draw-hwm = feed-lwm + residue` degenerates, under booleans, to
    `has-work = residue ≠ ∅`. So this relation IS the retire's residue, and its emptiness IS
    convergence at this boundary.

    ⚑ THE POSITION WAS NEVER THE FACT — IT WAS A STAND-IN FOR ONE. `below` asked "has every
    registered consumer passed this core's highest `seq`?" as a proxy for "does anyone still
    need these rows?". The three surviving conjuncts answer the real question PER CORE and
    exactly: the durable tier holds this core's addressing, its every row rebuilds to the key
    the tier stores, and its edges agree. A `MIN(lwm)` scalar could only ever answer it for the
    whole chain at once, which is why one unreconstructible core used to hold every drainable
    core above it.

    ⚑ AND THE TERMINAL-ACTOR PROBLEM DISSOLVES RATHER THAN BEING HANDLED.
    `Substrate.Lifecycle.Terminal`: *"an actor with no feed side has nothing to release, so
    'advance' is not an operation it has — the operation is absent, not rejected."* With no
    floor there is no floor to hold, so `scope_fix:resolver` — a pin at 0 that blocked every
    drain on both stores, measured `hwm 6,274,182 / lwm 0 / 0 observations below the floor` —
    simply has no work predicate here. Its replacement relation `ref` is written by the same
    promote that writes `obs_node`, so `projected` already carries its release.

    ⚑ THIS SAID *"WHAT THIS DOES NOT RETIRE: the `consumer` registry's IDENTITY (who exists, of
    what kind) is a declaration and stays."* True when written, FALSE now — the table was
    dropped 2026-08-12. Kept because the retreat is the record: position, then reader-kind, then
    the roster, each step defended as stopping at the last. A declaration nothing reads is not
    one.

    ⚑⚑ `_live_scope` IS A SEMI-JOIN ON THE SUBTRAHENDS AND IT CHANGES NO ANSWER — the identity
    is `A \\ B = A \\ (B ∩ A)`, so an element of a subtrahend that is not in the MINUEND is
    work whose result is discarded. Every minuend here is a set of `obs.core_id` (`below`
    groups `obs`; the residue form's base is `obs` itself), so restricting each subtrahend to
    `core_id IN (SELECT core_id FROM obs)` is exactly that intersection. Two of the three
    subtrahends were computed over the DURABLE tier and only then cut down by a difference:
    `ambiguous` rebuilt every addressed observation in the store, and `edge_disagrees` read
    the whole accumulated `edge` on both sides of a symmetric difference.

    ⚑ WHY THAT IS AN ASYMPTOTIC BUG RATHER THAN A SLOW QUERY. The durable tier grows
    MONOTONICALLY and forever; the live tier is what the drain keeps near one core. So the
    unscoped licence READ the thing that never shrinks while its ANSWER was bounded by the
    thing that does — `--scans drainable_res.unscoped` reports `obs_node` and `edge` at
    1.00 × their whole size, twice each, on a store where the answer was one core.

    ⚑⚑ THE SERIES THAT FIRST EXPOSED IT WAS WALL CLOCK — retire steps of 1.0 / 12.1 / 25.9 /
    35.3 s against `obs_node` of 2,745 / 102,635 / 361,141 / 470,411 — AND THAT SERIES IS
    EVIDENCE OF A SHAPE, NOT A MEASUREMENT (user, 2026-08-12). It was taken under unknown
    machine load, and each duration was read at a different moment from the store size it is
    paired with. It was enough to NOTICE "this tracks the durable tier"; it could never have
    VERIFIED the fix, because a smaller number afterwards is equally explained by a quieter
    box. The verification is the row count, which is deterministic under any load.

    ⚑ THREE SUBTRAHENDS, THREE SCOPINGS, AND THE SMALLEST ONE IS THE INSTRUCTIVE ONE. Two
    were obvious once measured (`obs_node` rebuilt whole, `edge` read whole twice); the third
    — `unprojected`'s anti-join — was a cheap-per-row full scan that the clock hid entirely.
    See its note: the predicate is *does this read the durable tier*, not *is this slow yet*.

    ⚑ `_live_scope=False` IS THE REFERENCE ARM, NOT A FALLBACK (see `REFERENCE_ARMS`). It is
    the pre-scoping licence verbatim, kept reachable so `--equiv` can MEASURE the two core
    sets equal on a live store rather than have this docstring assert it. It is deliberately
    absent from `INTERN_BUILDERS`, so it never reaches the compiled runtime cache and no
    caller can execute the unscoped licence as a `DELETE`'s subquery by accident.

    ⚑⚑ THIS EXISTS BECAUSE THE LICENCE WAS A SEQUENCE OF STATEMENTS, WHICH IS WHAT MAKES IT
    RACY (user, 2026-08-11: *"TOCTOU"*, then *"look at the JEA GPU code and see how it handles
    stateful work, BRANCHLESSLY — that paradigm should translate well to relational algebra"*).
    `reclaim` composed SIX world-states into one decision — `pin_persistent` → `lwm()` →
    `_unreflected_floor` (a Python loop with an early `break`) → `count` → `DELETE` → `DELETE` —
    under `autocommit=True`, so every arrow is a separate transaction with no lock across it.

    ⚑ THE PARADIGM, FROM `jea/jea_edge_states.py:9`, IS THE FACTORING — not the warning:

        achieved_conductance = structural_bound × efficiency × live_state

    Three factors of DIFFERENT provenance and lifetime, combined in ONE expression rather than
    read into variables and reconciled across steps. That file's own docstring names the failure
    of the other shape — *"never blind-multiply a stale factor by a fresh live_state"* — and the
    reason the branchless form is immune is not that it is guarded but that **nothing is HELD**.

    The relational translation is direct, and it is this query:

        drainable  =  below_floor  ×  projected  ×  determined
                        (queue)       (obs_node)    (node_id, ch)

    ⚑ EACH FACTOR IS THE SAME FACT THE LIFECYCLE CHAIN DECLARES, so this is not a fourth
    spelling: `below_floor` is `consumed`, `projected`+`determined` together are `reflected`
    (`lifecycle.LIFECYCLE`, and `Substrate.Lifecycle.Drainable`'s injectivity hypothesis —
    *"the durable form must DETERMINE the staged one"*). `lifecycle_census`'s CASE already
    evaluates them this way; `reclaim` did not, and that was the gap.

    ⚑ THE UNIT IS THE CORE, AND `HAVING max(seq) < floor` IS WHY. `seq` is log-wide while
    `local_id` is per-core and dense, so a positional cut slices ACROSS cores and leaves a
    PREFIX of one fibre — measured 2026-08-11, one observation surviving at `local_id 6213`
    with `positional()` correctly refusing. Either every row of a core goes or none does.

    ⚑ AND THE DETERMINACY CONJUNCT REPLACES A LOOP WITH AN EARLY BREAK. `_unreflected_floor`
    iterated cores calling `reflects()` and returned the FIRST failure as a chain-wide scalar,
    so one unreconstructible low core held the entire sweep. Its own docstring already called
    that wrong — *"the honest predicate is now a SET DIFFERENCE, not a floor"* — and called its
    own it-cannot-be-SQL claim false. This is the set difference: a core is excluded iff it has
    an ambiguous `(node_id, ch)` group, not iff it sits above someone else's failure.

    ⚑⚑ AND A FOURTH SUBTRAHEND LANDED 2026-08-12 (⑹): `edge` MAY NOW DRAIN. The licence is
    `projected ∧ reconstructs ∧ edge-reflected-vs-obs ∧ edge-recoverable-from-durable`. The
    last is the one that had never existed, and its absence is why `edge` was the store's
    largest relation and the only one violating *"the tier must drain as it fills"* —
    MEASURED on the sandbox: `obs` 0 · `event` 0 · `edge` 627,077, i.e. 46% of 1,362,384 rows.
    The two edge conjuncts read OPPOSITE SIDES of the wedge: (4) rebuilds from `obs.ekey`
    (tier 0) and so proves `edge` redundant WITH `obs`; (5) rebuilds from `obs_node.ch` (the
    durable tier) and so proves it recoverable WITHOUT it. Only the second licenses deleting
    both, and reading the first as covering it is the wedge backwards.

    ⚑ THE EDGE CONJUNCT IS NOW FOLDED IN (⓷), so the licence is
    `projected ∧ determined ∧ edge-reflected` — the full conjunction `reflects()`
    names, in one statement. The obstruction this docstring used to record — *"it is
    whole-tier and this is per-core"* — **was a misreading of the builder's shape**:
    `q_edge_disagreement` returns per-ROW tuples `(core_id, plid, ord, clid)`, never a
    tier-level verdict, so composing it needs only a projection to its distinct `core_id`s.
    Nothing had to be widened or weakened; the two were always the same granularity.

    ⚑ AND IT GAVE A DEAD CAPABILITY ITS FIRST CONSUMER. MEASURED BEFORE THE FOLD:
    `pycodemod --calls q_edge_disagreement` → **1 def, 0 calls** — the `rewire_only` class,
    a builder that compiled into `SQL[...]` and was reachable only by asking for it by name.
    The most expensive correctness check in the repo was wired to nothing.

    ⚑ WHAT THIS STILL DOES NOT COVER, so it is not misread as total: the interning tier
    (`terms`, `path_seg`, `path_text`) has no conjunct here and no `reflects_*` at all — F10's
    tier misclassification, which is a DECLARATION fix (`_TIERS`), not a predicate to add.
    """
    # ── (1) CONSUMED (`below`, `lo = bindparam("floor")`) — DELETED 2026-08-12 with `obs.seq`.
    #    The conjunct and its parameter are quoted in this function's docstring; the reasoning
    #    that removed them is there too, so it is not re-stated at the site.
    # (2) PROJECTED — every observation of the core has an interned node. A LEFT JOIN with a
    #     NULL test is the anti-join; `NOT IN` would be the NULL-semantics trap `reclaim`'s GC
    #     was rewritten away from.
    #
    # ⚑⚑ THE RIGHT SIDE IS SCOPED TOO, AND THIS ONE IS NOT AN OPTIMISATION OF A SUBTRAHEND —
    # it is the same restriction the ON clause already ENTAILS (`obs_node.core_id =
    # obs.core_id`, and `obs.core_id` ranges over the live tier by construction), spelled so
    # the planner can act on it. MEASURED without it, AFTER the other two were scoped:
    # `Hash Right Anti Join` over a full `Seq Scan on obs_node`, 508,554 rows — i.e. 1.00 ×
    # the whole durable relation. With it: `Index Only Scan`, 35,398 rows.
    #
    # ⚑⚑ IT SURVIVED THE FIRST PASS BECAUSE IT LOOKED CHEAP, WHICH IS THE WHOLE TRAP — and
    # "looked cheap" meant I had glanced at a duration. A seq scan of a narrow relation is
    # fast per row and LINEAR IN A RELATION THAT NEVER SHRINKS: the identical defect as the
    # two large terms, at a size where the clock does not yet show it. **The predicate to fix
    # on is *does this read the durable tier*, not *is this slow today*** — which is exactly
    # why the instrument reports `× |rel|` and not milliseconds. A ratio of 1.00 against a
    # monotonically growing relation is a defect at every store size, including the ones
    # where it is invisible.
    _on = [obs_node.c.core_id == obs.c.core_id, obs_node.c.local_id == obs.c.local_id]
    if _live_scope:
        _on.append(obs_node.c.core_id.in_(_live_cores(one_core)))
    unprojected = (
        select(obs.c.core_id)
        .select_from(obs.outerjoin(obs_node, and_(*_on)))
        .where(obs_node.c.core_id.is_(None))
    )
    # (3) DETERMINED — no (node_id, ch) group addresses two ekeys. This is `drainable`'s
    #     injectivity hypothesis, and it is the conjunct Ⓒ1's carrier made expressible: before
    #     `obs_node.ch` existed it was false for 43.8% of rows and no query could say otherwise.
    # (3) RECONSTRUCTS — the core's every row REBUILDS to exactly the key the tier holds.
    #
    # ⚑⚑ THIS REPLACED AN AMBIGUITY PROXY THAT WAS WRONG IN THE UNSAFE DIRECTION (F31). The
    # conjunct here used to be `count(DISTINCT ekey) > 1` per `(node_id, ch)` group — which
    # asks whether the map is a FUNCTION, and it IS: 0 ambiguous. But **being determined in
    # principle is not being computable from the durable side.** The qname of a `QName` node
    # is in no relation above tier 0, so the function exists and cannot be evaluated, and the
    # licence read the first as evidence of the second. MEASURED: it licensed 13 cores while
    # **zero** were reconstructible.
    #
    # ⚑ AND THE UNIQUENESS IT MEASURED CAME FROM THE WRONG PLACE. `(node_id, ch)` is injective
    # only because `ch` holds per-core POSITIONAL local ids, which distinguish occurrences the
    # head cannot — so it certifies ADDRESSABILITY and never RECOVERABILITY.
    #
    # ⚑ THE HONEST PREDICATE IS `Lifecycle.Drainable`'s, VERBATIM: *"rebuild the core's obs
    # from the SPPF + reverse index, compare to the live rows, DELETE ONLY ON EQUALITY."* It
    # needs no a-priori refusal — F31 proves none can exist for the invisible class — because
    # the comparison runs while `obs` is still there. `IS DISTINCT FROM` (not `!=`) so a NULL
    # rebuild, the honest refusal, COUNTS AS A MISMATCH rather than vanishing in NULL logic.
    _rb = _rebuilt_obs(live_only=_live_scope, one_core=one_core).subquery()
    ambiguous = (
        select(obs.c.core_id)
        .select_from(
            obs.join(_rb, and_(_rb.c.core_id == obs.c.core_id, _rb.c.local_id == obs.c.local_id))
        )
        .where(_rb.c.ekey.is_distinct_from(obs.c.ekey))
    )
    # (4) REFLECTED-AT-THE-EDGE — the core contributes no row to the obs↔edge symmetric
    #     difference. `q_edge_disagreement` returns ROWS (core_id, plid, ord, clid); the
    #     licence is a set of core_id, so the composition is a PROJECTION: a core is excluded
    #     iff it contributes any disagreeing row.
    #
    # ⚑ THIS IS THE CONJUNCT THE DOCSTRING ABOVE SAID WAS OWED — and its stated obstruction
    # ("whole-tier, and this is per-core") dissolves under the projection: the symmetric
    # difference was never whole-tier, it was per-ROW, and `core_id` is one of its columns.
    #
    # ⚑ AND IT IS THE STRAIGHT PROJECTION, WITH NO CLAUSE COMPENSATING FOR DRAINED CORES
    # (user, 2026-08-11: *"So what? You're arguing in favor of TOCTOU"*). I had argued for
    # restricting this to cores that still hold `obs` rows, on the grounds that a drained core
    # reads as maximally disagreeing (empty rebuild vs surviving `edge`) and would make the
    # drain non-idempotent across runs. **That reasoning was the TOCTOU shape wearing a safety
    # argument's clothes**: "the same answer on run 1 and run 2" is a claim about two
    # evaluations at two times, and this query's whole purpose is that there is exactly ONE
    # evaluation over ONE snapshot. After a drain the tier state genuinely changed; a licence
    # returning the same answer over changed state would be the STALE one. Refusing what no
    # longer needs draining is CORRECT, not a regression.
    #
    # ⚑ THE COMPENSATING CLAUSE WOULD HAVE BEEN THE ACTUAL RACE — it carries an assumption
    # about what a PREVIOUS run did, i.e. state held across evaluations, which is exactly what
    # `bindparam` instead of `literal(floor)` prevents one layer up.
    #
    # ⚑ NOR IS THE COMPENSATION NEEDED, STRUCTURALLY — and the argument SURVIVES the positional
    # conjunct it was originally made about. It used to read: *"conjunct (1) is `GROUP BY
    # core_id HAVING max(seq) < floor`, and a core with no `obs` rows produces NO GROUP — so it
    # is absent from `below`."* The minuend is now `SELECT core_id FROM obs GROUP BY core_id`,
    # which produces no group for such a core for the same reason. The property was never the
    # `HAVING`; it was that the base set is grouped over `obs`.
    # ⚑ THE THREE SCOPINGS REST ON TWO DIFFERENT ARGUMENTS, AND COLLAPSING THEM WOULD HIDE
    #   the weaker one. `ambiguous` and `unprojected` are JOIN PUSHDOWNS: their join
    #   conditions already equate `obs_node.core_id` to `obs.core_id`, so the row set is
    #   UNCHANGED, not merely unchanged-after-the-difference. `edge_disagrees` is the
    #   `A \ B = A \ (B ∩ A)` step — it genuinely drops rows from the SUBTRAHEND, and they
    #   are sound to drop only because they were never in the minuend. Both are exact; only
    #   the second needs the minuend's shape to be true, which is why `--equiv` measures the
    #   whole licence rather than each conjunct.
    # ⚑⚑⚑ CONJUNCT (4) NEEDS **BOTH** ARMS SCOPED, AND I THREADED ONLY ONE ON THE FIRST PASS.
    # `_rebuilt_edges_from_durable` (conjunct 5) and `_rebuilt_edges` (this one) are two
    # similarly-named helpers reading OPPOSITE SIDES of the wedge; I gave the first a `one_core`
    # and left the second alone. `--sql drainable_res.one_core` then showed `IN (SELECT
    # obs.core_id FROM obs)` still UNSCOPED four times right here — caught by reading the
    # compiled SQL, which is the only place the miss was visible.
    #
    # ⚑⚑ AND THIS IS THE ARM THAT FILLED A DISK. The 2026-08-18 ENOSPC incident measured
    # conjunct (4) sorting **9,438,375,610 rows**: `jsonb_array_elements_text` explodes each
    # `obs` row into ~100 children and `EXCEPT` demands a full sort. Leaving its `obs`-side
    # LATERAL corpus-wide under a per-core retire would reproduce that while the ANSWER looked
    # narrow — the precise failure `q_drainable_res`'s docstring names one level up.
    _st = lambda: _stored_edges(live_only=_live_scope, one_core=one_core)
    _re = lambda: _rebuilt_edges(one_core=one_core)
    _dis = union_all(_re().except_(_st()), _st().except_(_re())).subquery()
    edge_disagrees = select(_dis.c.core_id).distinct()
    # (5) EDGE-RECOVERABLE-WITHOUT-`obs` — the core contributes no row to the symmetric
    #     difference between `edge` and its rebuild from `obs_node.ch`. Same projection as
    #     (4): `q_edge_durable_disagreement` returns ROWS `(core_id, plid, ord, clid)`, the
    #     licence is a set of `core_id`, so composing it is `SELECT DISTINCT core_id`.
    #
    # ⚑⚑ THIS IS THE CONJUNCT THAT LETS `edge` DRAIN, AND ITS ABSENCE IS WHY `edge` BECAME THE
    # ACCUMULATOR. MEASURED on the sandbox 2026-08-12: `obs` 0, `event` 0, `edge` 627,077 —
    # **46% of the store's 1,362,384 rows**, in the tier whose governing constraint is *"it must
    # drain as it fills"*. `obs` and `event` drain; `edge` never has, because nothing licensed it.
    #
    # ⚑⚑ AND (4) CANNOT SUBSTITUTE FOR IT, WHICH IS THE EASIEST THING HERE TO GET BACKWARDS.
    # `_rebuilt_edges` rebuilds from `obs.ekey` — TIER 0 — so (4) proves `edge` is redundant
    # *WITH* `obs`, not that it is recoverable *WITHOUT* it. That is the wedge read backwards:
    # `obs` and `edge` are mutually determining, so the pair may lose EITHER, never both.
    # `_rebuilt_edges_from_durable` reads the OTHER side (`obs_node.ch`, a durable-tier
    # relation), which is what makes deleting both in one statement sound.
    #
    # ⚑⚑ AND IT GAVE A DEAD CAPABILITY ITS FIRST CONSUMER — the same class as (4) one step
    # earlier. MEASURED BEFORE THE FOLD: `pycodemod --calls q_edge_durable_disagreement` →
    # **1 def, 0 calls**. The one arm that decides whether the store's largest relation may be
    # reclaimed compiled into `SQL[...]` and was reachable only by asking for it by name.
    #
    # ⚑⚑ AND THE CENSUS STILL SAYS `1 def, 0 calls` AFTER THE FOLD, WHICH IS A FACT ABOUT THE
    # METHOD RATHER THAN ABOUT THE SUBSTRATE — recorded here so the next reader does not
    # conclude the fold never happened. The conjunct composes the same expression from
    # `_rebuilt_edges_from_durable` + `_stored_edges` rather than calling the BUILDER (it must
    # live-scope both arms, which the whole-tier builder deliberately does not), so the
    # capability's census moved and the builder's did not: `--calls _rebuilt_edges_from_durable`
    # went **1 → 2 calls**. The builder itself is now EXECUTED by name from
    # `schema_selftest`'s licence fixture — a string-keyed dispatch, exactly the shape `--calls`
    # is recorded as unsound for (it once reported a live `QB.run(con,"orbit_node_count")` as
    # dead). Conjunct (4) has the identical shape and its own note above makes the same claim.
    #
    # ⚑⚑ (4) IS **NOT** REMOVED, AND THE ARGUMENT THAT IT COULD BE IS AN ARGUMENT. It goes:
    # conjunct (3) already requires `obs.ekey` to equal the key rebuilt from `obs_node`, and
    # that key EMBEDS `ch`, so for any core passing (3) the two rebuilds are row-identical and
    # (5) implies (4). That is a proof sketch about the encoder, and **removing a conjunct
    # WIDENS the licence, which is the unsafe direction** — the one failure mode that cannot be
    # undone. Both stand; `REFERENCE_ARMS["drainable_res.no_obs_edge"]` is the arm that MEASURES
    # whether (4) still subtracts anything, and retiring it is a separate step that must carry
    # that measurement.
    # ⚑ `one_core` RIDES `live_only` INTO BOTH EDGE ARMS. These compose the conjunct rather than
    # calling the whole-tier builder (see the note above), so they scope through the same
    # `_live_cores` — but only if the flag reaches them. Conjuncts (4) and (5) are the two that
    # filled a disk in the 2026-08-18 ENOSPC incident; leaving them corpus-wide under a per-core
    # retire would reproduce it while the ANSWER looked narrow.
    _sd = lambda: _stored_edges(live_only=_live_scope, one_core=one_core)
    _rd = lambda: _rebuilt_edges_from_durable(live_only=_live_scope, one_core=one_core)
    _dur = union_all(_rd().except_(_sd()), _sd().except_(_rd())).subquery()
    durable_edge_disagrees = select(_dur.c.core_id).distinct()
    # ⚑⚑ THE MINUEND IS EVERY CORE THE STAGED TIER STILL HOLDS — and it is no longer a BRANCH.
    # This return used to sit under `if _residue_only:` beside a second one over `below`; the
    # note there said the positional conjunct *"is not a threshold at all: the question a
    # watermark was answering (has every consumer passed this core?) is answered per-core, and
    # exactly, by the three conjuncts that follow it. A core is `projected` when the durable
    # addressing holds it, and `project_ref` writes `ref` in the same promote — so 'the reader
    # has what it needs' is the SAME fact, not a second one to position."* That argument is now
    # the code's only shape rather than one arm of it.
    #
    # ⚑ THE CONJUNCTION AS SET DIFFERENCE, WHICH IS THE BRANCHLESS FORM: no per-core Python
    # verdict, no early break, no scalar floor standing in for a set. One statement, one
    # snapshot — the window the guards were trying to narrow does not exist here.
    # ⚑ `except_(a, b, c)` AS AN N-ARY CONSTRUCTOR, NOT CHAINED. `.except_()` returns a
    # `CompoundSelect`, which has no set-operator METHODS — measured here as
    # `AttributeError: 'CompoundSelect' object has no attribute 'except_'`, which is the
    # identical error `q_edge_disagreement`'s comment records for `union_all`. I read that
    # note while writing this and chained anyway: knowing a rule and applying it are
    # different acts, and the second is the one a compile step enforces.
    _subtrahends = [unprojected, ambiguous, edge_disagrees, durable_edge_disagrees]
    if not _obs_edge_conjunct:
        # ⚑ THE RETIREMENT ARM, AND IT IS A MEASUREMENT INSTRUMENT RATHER THAN A DESIGN FORK.
        # `_residue_only` had to be deleted because its two settings were two LICENCES with two
        # designs; this flag's `False` setting is the licence WITHOUT (4), reachable ONLY through
        # `REFERENCE_ARMS` — deliberately absent from `INTERN_BUILDERS`, so it never reaches the
        # compiled cache and no caller can splice it into a `DELETE` by accident. It exists so
        # "does (4) still subtract anything now that (5) is in" is a SET DIFFERENCE somebody
        # measured, not a sentence in this docstring. Same discipline as `_live_scope=False`.
        _subtrahends.remove(edge_disagrees)
    # ⚑⚑⚑ THE MINUEND IS SCOPED TOO, AND OMITTING IT WOULD DEFEAT THE WHOLE NARROWING. Every
    # subtrahend narrows through `_live_cores(one_core)`, but the minuend is where the licence
    # ENUMERATES: `GROUP BY obs.core_id` over the staged tier is a full aggregate of 128M rows
    # whatever the subtrahends do. Scoping the subtrahends and not the base is the same
    # half-measure as scoping the licence's OUTPUT — the answer narrows, the WORK does not.
    _minuend = select(obs.c.core_id).group_by(obs.c.core_id)
    if one_core:
        _minuend = _minuend.where(obs.c.core_id == bindparam("rc_core", value="", type_=String))
    return except_(_minuend, *_subtrahends)


def _rebuilt_obs(live_only=False, one_core=False):  # ⟡tier-live ⓙ: THE LINK — durable side → `obs`
    """Every addressed `obs` row REBUILT FROM THE DURABLE TIER → (core_id, local_id, ekey).

    ⚑⚑ `live_only=True` SCOPES THE REBUILD TO THE CORES `obs` STILL HOLDS, AND IT IS OFF BY
    DEFAULT BECAUSE THE TWO CONSUMERS WANT OPPOSITE THINGS. `q_obs_reconstructed` — the
    per-core READ path — must resolve a core whose `obs` rows are GONE; that is the entire
    point of the link, and scoping it here would silently break reconstruction for exactly
    the drained cores it exists to serve. The drain LICENCE wants the opposite: it only ever
    compares against rows `obs` still holds, so every rebuilt row outside that set is work
    whose result is discarded. One expression, one flag, no second spelling of a byte-exact
    encoder — which is the property `q_obs_reconstructed`'s docstring says must be kept.

    ⚑⚑ MEASURED, WHICH IS WHY THE FLAG EXISTS RATHER THAN A COMMENT SAYING THE PLANNER WILL
    HANDLE IT. The licence joins this rebuild to `obs` on `(core_id, local_id)`, so the
    restriction is *implied* — an inner join to a one-core `obs` cannot admit another core's
    row. **Postgres does not push it.** `--scans drainable_res.unscoped` at `obs` 35,398 /
    `obs_node` 508,554 reports `obs_node  Seq Scan  1,017,108 row(s)`; with the semi-join
    spelled, `Bitmap Heap Scan` + `Index Only Scan`, 70,796 rows — the LIVE tier, twice.
    **A restriction the algebra entails is not a restriction the planner applies.**

    ⚑⚑ AND THE UNIT OF THE CLAIM IS RELATION TRAFFIC, NOT SECONDS (user, 2026-08-12: *"NEVER
    rely on wall clock; CPU saturation will always be a wildcard, and it introduces TOCTOUs
    that confound the measurements"*). Two independent reasons here, and the second is the
    general one: this plan crosses `jit_above_cost` (postgres costs the LATERAL
    `jsonb_array_elements_text` at its default 100 rows, so 35,398 `obs` rows are estimated
    as 3,539,800) and spends most of its clock in JIT compilation — so the elapsed figure
    describes the OPTIMISER, not the scan. And a duration is read at a different moment from
    the store state it supposedly describes, which makes it a TOCTOU by construction whatever
    else is true. **A flat row count across a growing durable tier is the proof; a smaller
    number of seconds is not.**

    ⚑⚑ THIS ARM HAS NEVER EXISTED, AND ITS ABSENCE IS WHY THE REFLECTOR WAS A TAUTOLOGY (F30).
    `reconstruct.reconstruct()` called `fibre()`, which is `SELECT local_id, ekey FROM obs` —
    it read the staged rows and handed them back. So `reflects_obs` compared `obs` to `obs` not
    by oversight but BY NECESSITY: there was no other side. This is the other side.

    ⚑ IT IS ONE **LINK**, NOT "THE CROSS-TIER READ" (user, 2026-08-11: *"chaining the algebra of
    that requirement is what provides the global queryability from any given tier all the way
    down to the events root"*). Global queryability is the COMPOSITION of per-tier reconstruct
    maps, so there is nothing bespoke to build for it — there are links, and composing them IS
    the global query. Which is also why a 99.18% link is not "99.18% coverage": it is a BROKEN
    link, and everything below it becomes unreachable through that path.

    ⚑ IN SQL RATHER THAN PYTHON, DELIBERATELY (user's call, 2026-08-11). A Python rebuild would
    share the encoder and be byte-exact by construction — but it could not COMPOSE into a larger
    query, so every cross-tier read would pull rows to the client, which defeats the model's
    *"efficiently"*. The exactness risk is discharged by measurement instead: every rebuilt key
    is compared against its stored one, and that comparison IS the honest `reflects_obs`.

    THE SOURCES, read off the encoder (`sppf_db.py:481-490`) rather than recalled:

      obs_node.ch   TEXT, child LOCAL ids comma-joined in `ord` order, '' when childless
      _node.*_id    every one is `_b64(text)` — BOTH interners are literally `_b64`, so each
                    decodes with NO join to `terms`/`path_text`

    ⚑ THE HEAD COMES FROM `_node`, NOT FROM DECODING `obs_node.node_id` — and the shortcut that
    looks free is a runtime error. `node_id`'s preimage is `kind\\x00role\\x00op\\x00lit\\x00…`,
    and **postgres `text` cannot hold NUL**, so `convert_from(decode(node_id, …))` THROWS.

    THE ENCODING, byte-exact or it is worthless. Three traps, each measured, not reasoned:

      * `sort_keys=True` ⇒ emitted order is **c, ch, i, l, q** — NOT the insertion order
        `c,q,i,ch` that this repo's own docs quote. `l` sorts between `i` and `q`.
      * default separators — **`", "` and `": "`, WITH spaces** — so `ch` needs `,` → `, `,
        and `''` must render `[]` rather than `[""]`.
      * ⚑ `encode(…, 'base64')` **INSERTS A NEWLINE EVERY 76 CHARS**. Without the `replace`
        every long key mismatches, which would read as data loss and is an encoding artifact.

    ⚑ AND `format()` RATHER THAN `||`, WHICH IS NOT A STYLE CHOICE: the `no-chaining` hook
    false-positives on SQL string concatenation inside a quoted argument (measured this session
    on a `--probe`). `format()` sidesteps it and reads better; the hook defect is filed as ⓚ.

    ⚑ THE EKEY IS **NULL** WHERE THE HEAD CANNOT DETERMINE IT, RATHER THAN THE ROW BEING
    DROPPED. A missing row and an unreconstructible row are different findings, and a builder
    that silently returns fewer rows makes them indistinguishable — the caller could only report
    "the lists differ" instead of "N of M rows are unreconstructible, first at local_id K".

    ⚑ WHAT IT CANNOT DO, STATED SO NO CALLER ASSUMES OTHERWISE (F31). The head is
    `(kind, role, op, lit)` — FOUR slots for FIVE fields — so it is lossy BY CONSTRUCTION:

        ctor ∈ FREE  →  op = qname  →  the CTOR is lost
        else         →  op = ctor   →  the QNAME is lost, and this case is INVISIBLE here
                                       (op is dotless, role is empty — it looks recoverable)

    Measured on the sandbox: 175,060 rows rebuild exactly, 1,411 are NULLed by the guards, and
    **926 would rebuild WRONG** — ctor `QName`, whose qname the head drops. No predicate over the
    durable side can catch that class, which is exactly why the licence is
    `Lifecycle.Drainable`'s — *rebuild, compare to the live rows, DELETE ONLY ON EQUALITY* — and
    not an a-priori refusal. The comparison runs while `obs` still exists, so it catches the
    invisible class for free. ⓸ (a carrier for what the head drops) is what makes the link total.
    """
    # ⚑⚑ JOINS, NOT `convert_from(decode(…))` (ⓝ). The ids stopped carrying their own text when
    # interning went surrogate, so a decode here would return digits. That IS the trade: a
    # reversible id is a decode and grows with what it names; a surrogate is a JOIN and does not.
    # Reversal by query is the point, not a consolation.
    t_ctor, t_lit, t_role = (terms.alias("t_ctor"), terms.alias("t_lit"), terms.alias("t_role"))
    p_q = path_text.alias("p_q")
    src = (
        obs_node.join(_node, _node.c.node_id == obs_node.c.node_id)
        .join(t_ctor, t_ctor.c.term_id == _node.c.op_term_id)
        .join(t_lit, t_lit.c.term_id == _node.c.lit_id)
        .join(t_role, t_role.c.term_id == _node.c.role_id)
        # ⚑ OUTER ON THE QNAME ALONE — it is the one head field legitimately absent. An INNER
        # join would silently DROP every node without a qname, which is most of them, and a
        # reconstruction returning fewer rows reads as a missing row rather than a bad join.
        .outerjoin(p_q, p_q.c.path_id == _node.c.op_path_id)
    )
    ctor, lit, role, qname = t_ctor.c.text, t_lit.c.text, t_role.c.text, p_q.c.text
    # `l` is present iff TRUTHY in the encoder (`if litval:`) — never `"l": null`.
    lit_part = case(
        (lit != literal(""), func.format(literal(', "l": %s'), cast(func.to_json(lit), Text))),
        else_=literal(""),
    )
    # ⚑ `idx` LIVES IN `role` AS `db<n>` — the encoder's own spelling, so this recovers it rather
    # than guessing. `''` means the term carries no index and the ekey holds `"i": null`.
    idx = case(
        (role.like(literal("db%")), cast(func.substr(role, literal(3)), Text)),
        else_=literal("null"),
    )
    body = func.format(
        literal('{"c": %s, "ch": [%s], "i": %s%s, "q": %s}'),
        cast(func.to_json(ctor), Text),
        func.replace(obs_node.c.ch, literal(","), literal(", ")),
        idx,
        lit_part,
        func.coalesce(cast(func.to_json(qname), Text), literal("null")),
    )
    ekey = func.replace(
        func.encode(func.convert_to(body, literal("UTF8")), literal("base64")),
        literal("\n"),
        literal(""),
    )
    # ⚑⚑ AND THE `determined` GUARD IS GONE — THAT IS THE POINT OF ⓝ. It existed because the head
    # was four slots for five fields, so a dotted `op` or a `db<n>` role meant a field had been
    # DESTROYED and the row could only be REFUSED (NULL). The head now carries ctor AND qname AND
    # idx, so every addressed row rebuilds. `--triage`'s REFUSED going 1,411 → 0 is the
    # measurement that says the guard was compensating for a lossy promote, not for hard data.
    stmt = select(obs_node.c.core_id, obs_node.c.local_id, ekey.label("ekey")).select_from(src)
    if live_only:
        # ⚑ A SEMI-JOIN (`IN (SELECT …)`), NOT `NOT IN` AND NOT A JOIN. `obs_node` is keyed
        # `(core_id, local_id)`, so the leading column lets postgres drive this as an
        # index-scan-per-live-core instead of a seq scan of the whole durable tier. `IN` over
        # a subquery is the POSITIVE direction, where NULL semantics do not forbid the
        # anti-join rewrite the `NOT IN` → `NOT EXISTS` note in `q_edge_disagreement` records.
        stmt = stmt.where(obs_node.c.core_id.in_(_live_cores(one_core)))
    return stmt


def q_obs_reconstructed():  # ⟡tier-live ⓙ: one core, for `reconstruct()`
    """`_rebuilt_obs()` narrowed to ONE core — the per-core read `reconstruct()` issues.

    ⚑ THE FILTER IS THE ONLY DIFFERENCE, AND THAT IS WHY THE REBUILD IS FACTORED OUT. The
    licence needs the SAME expression over the WHOLE tier (`q_drainable`'s reconstructibility
    conjunct); a second spelling of a byte-exact encoder is precisely the drift this module
    exists to prevent, and here it would drift into "the check passes and the read is wrong".
    """
    return _rebuilt_obs().where(obs_node.c.core_id == bindparam("core_id"))


def q_obs_node_all():  # ⟡tier-live: the addressing map, whole
    """`(core_id, local_id, node_id)` for every addressed observation.

    ⚑ `obs_node` HAD NO DECLARED READER AT ALL until ⓙ, despite being the carrier Ⓒ1 added and
    the thing the drain licence turns on. `project_orbit_sppf` needed the same map and, lacking
    a builder, RECOMPUTED it — which was merely redundant while node ids were derivable and is
    WRONG under surrogates, because a second derivation mints values the store never assigned.
    """
    return select(obs_node.c.core_id, obs_node.c.local_id, obs_node.c.node_id)


def _rebuilt_edges_from_durable(live_only=False, one_core=False):
    """`edge`'s rows rebuilt from `obs_node.ch` — the DURABLE side, not tier 0.

    ⚑⚑ THIS IS THE ARM THAT DECIDES WHETHER `edge` MAY DRAIN, AND ITS ABSENCE IS WHY `edge`
    BECAME THE ACCUMULATOR. The converge run measured `obs` returning to 0 after every core
    while `edge` grew monotonically to 472,959 rows — so the tier that was supposed to drain
    as it fills has a second relation in it that never drains at all.

    ⚑ AND `_rebuilt_edges()` CANNOT ANSWER THIS, WHICH IS EASY TO MISREAD AS COVERAGE. That
    function rebuilds `edge` from `obs.ekey` — tier 0 — so it proves `edge` is redundant WITH
    `obs`, not that it is recoverable WITHOUT it. Draining `edge` on the strength of that check
    is the wedge read backwards: `obs` and `edge` are mutually determining, so the pair may
    lose EITHER, never both. This reads the other side.

    ⚑ `obs_node.ch` IS THE CARRIER Ⓒ1 ADDED FOR EXACTLY THIS — child local ids, comma-joined
    in `ord` order, put above tier 0 "where the drain cannot reach it". Position IS `ord`
    (the ordinality), the element IS `clid`, and `local_id` IS `plid`. Nothing is derived; the
    row is a transposition of a stored string.

    ⚑ `.render_derived()` IS LOAD-BEARING, NOT STYLE. Without it SQLAlchemy emits `WITH
    ORDINALITY AS anon_1` with no column alias list, postgres names the columns after the
    function, and every reference raises `UndefinedColumn` AT RUNTIME while compiling cleanly.
    `q_edge_disagreement` shipped that way and was never executable — it had 0 callers, so
    nothing found out until ⓷ gave it one.

    ⚑ AND THE `ch <> ''` FILTER IS A CORRECTNESS GUARD, NOT AN OPTIMISATION. A childless node
    stores the EMPTY STRING, and `string_to_array('', ',')` yields a one-element array holding
    `''` — so without the filter every leaf would fabricate a phantom edge to a nonexistent
    child. The stored side has no such row, so the symmetric difference would report one
    disagreement per leaf: 56% of observations in this corpus.
    """
    kids = (
        func.unnest(func.string_to_array(obs_node.c.ch, literal(",")))
        .table_valued("clid", with_ordinality="ord")
        .render_derived()
        .lateral()
    )
    stmt = (
        select(
            obs_node.c.core_id,
            obs_node.c.local_id.label("plid"),
            (kids.c.ord - 1).label("ord"),
            kids.c.clid,
        )
        .select_from(obs_node.join(kids, literal(True)))
        .where(obs_node.c.ch != literal(""))
    )
    if live_only:
        # ⚑⚑ `live_only=True` IS THE SAME SEMI-JOIN AS `_rebuilt_obs` / `_stored_edges`, ADDED
        # 2026-08-12 WHEN ⑹ GAVE THIS FUNCTION ITS SECOND CONSUMER. Unscoped it unnests
        # `obs_node.ch` for the WHOLE durable tier — 627,327 rows here, and that relation grows
        # monotonically and forever — while the licence's answer is bounded by the LIVE tier.
        # The identity is `A \ B = A \ (B ∩ A)`: a rebuilt edge for a core `obs` no longer holds
        # cannot exclude a core from a minuend grouped over `obs`, so restricting it is exact.
        #
        # ⚑ OFF BY DEFAULT, because `q_edge_durable_disagreement` is WHOLE-TIER BY DESIGN — it
        # asks "may `edge` drain AT ALL", and scoping it would make it answer a smaller question
        # under the larger question's name, with an empty result then reading as a licence over
        # a population that was never looked at. Exactly `_stored_edges`' own argument.
        #
        # ⚑ `one_core` RIDES THE SAME SEMI-JOIN AND CHANGES NOTHING FOR EXISTING CALLERS — it
        # defaults False at every definition and every call site keeps its current spelling, so
        # the whole-tier question is asked exactly as before. The narrowing is reachable ONLY
        # from a caller that names a core, which is what keeps the warning above true: a smaller
        # question is asked under a smaller question's NAME.
        stmt = stmt.where(obs_node.c.core_id.in_(_live_cores(one_core)))
    return stmt


def q_edge_durable_disagreement():  # ⟡tier-live: may `edge` drain?
    """Rows where `edge` and its rebuild FROM THE DURABLE TIER disagree — empty ⟹ `edge` drains.

    ⚑ SYMMETRIC, FOR THE REASON `q_edge_disagreement` ALREADY RECORDS: a one-directional
    `rebuilt ⊆ stored` check passes while the store holds edges the rebuild does not produce,
    which is precisely the half that matters when deciding whether the stored copy is
    redundant.

    ⚑ EMPTY HERE IS A LICENCE, NOT A REPORT — so the honest reading of a zero must be
    "measured and equal", never "nothing was checked". `--triage`'s discipline applies: a
    verdict over an empty population is UNMEASURED, and `edge` at 472,959 rows against an
    `obs_node` of 470,411 is a real population either way.
    """
    rebuilt, stored = _rebuilt_edges_from_durable(), _stored_edges()
    return union_all(rebuilt.except_(stored), stored.except_(rebuilt))


def _stored_edges(live_only=False, one_core=False):
    """`edge` as stored, with `clid` cast to TEXT so it can be compared to the rebuild.

    ⚑⚑ `live_only=True` IS THE SAME SCOPING AS `_rebuilt_obs`, AND IT WAS THE LARGER HALF —
    which is the part a plan naming only the rebuild would have missed. `q_drainable`'s
    edge conjunct is `(rebuilt △ stored)` projected to `core_id`, and `rebuilt` is driven
    from `obs`, so it is live-scoped by construction; `stored` was the WHOLE `edge` table on
    both sides of the symmetric difference. Every core `edge` still holds but `obs` no longer
    does therefore appears in `stored \\ rebuilt` — i.e. the licence was computing, and then
    discarding, one disagreement row per drained edge in the store, plus the SORT that
    `EXCEPT` needs over both. MEASURED with `--scans` at `edge` 508,349 / `obs` 35,398:
    `edge  Seq Scan  1,016,698 row(s)` unscoped (the whole table, twice — once per direction
    of the symmetric difference) against `edge  Bitmap Heap Scan  70,780 row(s)` scoped.

    ⚑ IT IS OFF BY DEFAULT BECAUSE THE OTHER TWO CONSUMERS ARE WHOLE-TIER BY DESIGN.
    `q_edge_disagreement` IS `reflects_edge` — "does the store hold an edge the rebuild does
    not produce" — and `q_edge_durable_disagreement` asks whether `edge` may drain at all.
    Scoping either to the cores `obs` still holds would make both answer a smaller question
    while keeping the name of the larger one, and an empty result would then read as a
    licence over a population that was never looked at.

    ⚑ THE CAST IS REQUIRED, NOT COSMETIC. `jsonb_array_elements_text` yields TEXT while
    `edge.clid` is INTEGER, so the set operation raises `DatatypeMismatch: EXCEPT types text
    and integer cannot be matched` — at RUNTIME, invisibly to `--compile`. This module's
    lightweight model declares every column `String` (it never writes), so SQLAlchemy cannot
    see the real type and will not insert the cast for you.

    ⚑ TEXT RATHER THAN PARSING THE OTHER SIDE TO INT, because a cast that can FAIL turns a
    comparison into an error on malformed data — and the comparison is the thing that was
    supposed to REPORT malformed data. Sound here because both sides are canonical decimal:
    the stored side is an integer, and the rebuilt side is `json.dumps` of an integer.
    """
    stmt = select(edge.c.core_id, edge.c.plid, edge.c.ord, cast(edge.c.clid, Text).label("clid"))
    if live_only:
        # ⚑ THE SAME SEMI-JOIN AS `_rebuilt_obs`, ON THE SAME LEADING KEY COLUMN: `edge` is
        # keyed `(core_id, plid, ord)`, so `core_id IN (SELECT core_id FROM obs)` is
        # index-drivable per live core rather than a scan of the accumulated tier.
        stmt = stmt.where(edge.c.core_id.in_(_live_cores(one_core)))
    return stmt


def q_drainable_res_correlated():  # ⟡disk-incident: the SAME licence, asked without EXCEPT
    """`q_drainable_res`'s answer, computed with correlated `NOT EXISTS` instead of `EXCEPT`.

    ⚑⚑⚑ A REFERENCE ARM, NOT A REPLACEMENT, AND THE DISTINCTION IS A SAFETY ONE.  This is
    deliberately absent from `INTERN_BUILDERS` (like `drainable_res.unscoped` beside it), so
    no caller can splice it into a `DELETE` subquery by accident.  `q_drainable_res` AUTHORISES
    DELETION, and its own docstring records that altering a conjunct WIDENS the licence — the
    one failure mode that cannot be undone.  A performance rewrite that silently widened what
    is eligible for deletion would be far worse than the spill it fixes: the spill crashes
    loudly and recovers, a widened licence corrupts silently and permanently.  So the rewrite
    lands HERE, is compared by `--equiv`, and is promoted into the licence only as a separate,
    reviewed act — never as part of a performance fix.

    ⚑⚑ WHAT IT FIXES, MEASURED 2026-08-18 during a live ENOSPC incident.  `q_drainable_res`
    is `except_(minuend, *four_subtrahends)`.  `EXCEPT` is a SET operator: it must sort or hash
    both sides in full, at the subtrahend's tuple width.  Three of the four spill:

        conjunct            production plan                     this arm
        (2) unprojected     anti-join 92,344,062 rows            HashAggregate → 1,501/worker
        (3) ambiguous       1.75M, index-driven — HEALTHY        unchanged
        (4) edge_disagrees  Sort over 9,438,375,610 rows, 3.73B  67.6M, no sort          55×
        (5) durable_edge    Sort over 98,684,290 rows, 35.6M     1.53M, no sort          23×

    Conjunct (4) is the one that filled the disk: `jsonb_array_elements_text` explodes each of
    93.4M `obs` rows into ~100 children, and `EXCEPT` then demands a full sort of the result.

    ⚑ THE PRINCIPLE IS ONE MOVE, APPLIED THREE TIMES: the outer query only ever wants DISTINCT
    `core_id`, so producing tuple-granularity rows `(core_id, plid, ord, clid)` and deduplicating
    afterwards does six orders of magnitude more work than the answer needs.  A correlated
    `NOT EXISTS` short-circuits per row on `ix_edge_pk` and materialises nothing.  This is the
    same move as `--holes`' `fp_only` fix and as `schema_queue.py:821`'s healthy sibling.

    ⚑ IT IS A STRONGER CLAIM THAN A DEDUP CHANGE FOR (4) AND (5), and `--equiv` must be given a
    sample that can see it.  For (2) the change is `EXCEPT`-dedup vs `GROUP BY`-dedup, which is
    not data-dependent.  For (4)/(5) the change is HOW THE DISAGREEMENT IS DETECTED, so a sample
    of only-agreeing cores proves nothing: both arms correctly return empty and the comparison
    never exercises the predicate.  `do_equiv`'s both-empty refusal catches the degenerate case;
    only a sample built from KNOWN-DISAGREEING cores catches the subtle one.

    ⚑ THE LIVE-SCOPING IS PRESERVED BY CONSTRUCTION rather than by copying its clauses: every
    correlation here is an equality against `obs`/`obs_node` rows the outer query is already
    walking, so the durable tier is reached only through the live one.  Measured: adding the
    explicit `core_id IN (SELECT core_id FROM obs)` back made it SLIGHTLY WORSE (69.5M vs 67.6M)
    — the scoping is redundant once the predicate is correlated.  Recorded because "restore the
    live-scope" is the obvious next thing a reader would try.
    """
    # (2) PROJECTED — every observation has an interned node.
    unprojected = ~exists(
        select(literal(1))
        .select_from(obs_node)
        .where(and_(obs_node.c.core_id == obs.c.core_id, obs_node.c.local_id == obs.c.local_id))
    )
    # (3) RECONSTRUCTS — unchanged from production: it is already index-driven at 1.75M, and
    #     changing a healthy conjunct would widen the diff with no measured gain.
    _rb = _rebuilt_obs(live_only=True).subquery()
    ambiguous = exists(
        select(literal(1))
        .select_from(_rb)
        .where(
            and_(
                _rb.c.core_id == obs.c.core_id,
                _rb.c.local_id == obs.c.local_id,
                _rb.c.ekey.is_distinct_from(obs.c.ekey),
            )
        )
    )
    # (4) REFLECTED-AT-THE-EDGE — some child of this row's ekey has no matching `edge` row.
    _j = func.convert_from(func.decode(obs.c.ekey, literal("base64")), literal("UTF8")).cast(JSONB)
    _kids = (
        func.jsonb_array_elements_text(_j[literal("ch")])
        .table_valued("child", with_ordinality="ord")
        .render_derived()
        .lateral()
    )
    # ⚑⚑ `.correlate(obs)` IS LOAD-BEARING AND ITS ABSENCE WAS A CARTESIAN PRODUCT.  Without
    # it SQLAlchemy auto-froms the `obs` it sees in the innermost predicate, compiling
    # `FROM edge, obs` — so the subquery joined EVERY `obs` row instead of correlating to the
    # outer one, and the arm would have compared against a licence it does not implement.
    # CAUGHT 2026-08-18 by reading the COMPILED SQL of the arm rather than trusting the python,
    # which is exactly the check the incident's caveat 3 exists for: a translation that looks
    # right in the builder and is wrong in the statement.
    edge_missing = exists(
        select(literal(1))
        .select_from(_kids)
        .where(
            ~exists(
                select(literal(1))
                .select_from(edge)
                .where(
                    and_(
                        edge.c.core_id == obs.c.core_id,
                        edge.c.plid == obs.c.local_id,
                        edge.c.ord == _kids.c.ord - 1,
                        edge.c.clid.cast(Text) == _kids.c.child,
                    )
                )
                .correlate(obs, _kids)
            )
        )
    )
    # (5) EDGE-RECOVERABLE-WITHOUT-`obs` — some child of this core's DURABLE `ch` has no
    #     matching `edge` row.  ⚑ IT IS NOT OPTIONAL AND (4) CANNOT SUBSTITUTE FOR IT: (4)
    #     rebuilds from `obs.ekey` (tier 0) and so proves `edge` redundant WITH `obs`; (5)
    #     rebuilds from `obs_node.ch` (durable) and so proves it recoverable WITHOUT it.  Only
    #     the second licenses deleting both, and reading the first as covering it is the wedge
    #     backwards — the production docstring's own words.  Omitting it here would make this
    #     arm a WIDER licence than production, which `--equiv` would report as a difference in
    #     the unsafe direction.
    #
    # ⚑ CORRELATED ON `core_id` ALONE, NOT ON THE ROW.  (4) walks `obs` rows and asks about
    #   each row's own children; (5)'s subject is `obs_node`, a different relation, so the
    #   correlation is at core granularity — which is also the granularity the licence wants.
    _dch = (
        func.unnest(func.string_to_array(obs_node.c.ch, literal(",")))
        .table_valued("clid", with_ordinality="ord")
        .render_derived()
        .lateral()
    )
    durable_edge_missing = exists(
        select(literal(1))
        .select_from(obs_node.join(_dch, literal(True)))
        .where(
            and_(
                obs_node.c.core_id == obs.c.core_id,
                obs_node.c.ch != literal(""),
                ~exists(
                    select(literal(1))
                    .select_from(edge)
                    .where(
                        and_(
                            edge.c.core_id == obs_node.c.core_id,
                            edge.c.plid == obs_node.c.local_id,
                            edge.c.ord == _dch.c.ord - 1,
                            edge.c.clid.cast(Text) == _dch.c.clid,
                        )
                    )
                ),
            )
        )
    )
    return (
        select(obs.c.core_id)
        .where(~unprojected & ~ambiguous & ~edge_missing & ~durable_edge_missing)
        .group_by(obs.c.core_id)
    )


def _rebuilt_edges(one_core=False):
    """`edge`'s rows as DECODED FROM `obs.ekey` — the shared subexpression.

    ⚑ HOMED BECAUSE IT NOW HAS TWO CONSUMERS, AND A COPY WOULD BE THE SECOND SPELLING THIS
    MODULE EXISTS TO PREVENT. `q_edge_disagreement` compares it against stored `edge`;
    `q_drainable` excludes cores where that comparison is non-empty. The decode chain is the
    only `convert_from` in the repo (`pycodemod --attr convert_from jea/metalanguage/` → 1
    site), so duplicating it would take the count to two and make "the reconstruction's core
    expression exists exactly once" false — a claim this plan relies on.
    """
    j = func.convert_from(func.decode(obs.c.ekey, literal("base64")), literal("UTF8")).cast(JSONB)
    # ⚑⚑ `.render_derived()` IS LOAD-BEARING, AND WITHOUT IT THIS BUILDER HAS NEVER BEEN
    # EXECUTABLE. SQLAlchemy emitted `WITH ORDINALITY AS anon_1` with NO column alias list, so
    # postgres named the columns `jsonb_array_elements_text` and `ordinality` and every
    # reference to `anon_1.ord` / `anon_1.child` raised `UndefinedColumn` AT RUNTIME.
    #
    # ⚑ IT COMPILED CLEANLY THE WHOLE TIME — SQLAlchemy does not validate against the server —
    # and `--calls q_edge_disagreement` was **1 def, 0 calls**, so nothing ever executed it.
    # A dead capability cannot fail, which is why "it compiles" said nothing here; the defect
    # surfaced the moment ⓷ gave it its first consumer.
    kids = (
        func.jsonb_array_elements_text(j[literal("ch")])
        .table_valued("child", with_ordinality="ord")
        .render_derived()
        .lateral()
    )
    stmt = select(
        obs.c.core_id,
        obs.c.local_id.label("plid"),
        (kids.c.ord - 1).label("ord"),
        kids.c.child.label("clid"),
    ).select_from(obs.join(kids, literal(True)))
    # ⚑⚑ `one_core` SCOPES THE `obs` SIDE OF THE LATERAL, WHICH IS THE EXPENSIVE HALF. This
    # explodes each `obs` row into ~100 children before anything filters — measured at
    # 9,438,375,610 sorted rows in the 2026-08-18 ENOSPC incident. Filtering `obs` FIRST is the
    # difference between exploding one core and exploding the corpus.
    #
    # ⚑ THE PREDICATE IS ON `obs.core_id` DIRECTLY, not a semi-join through `_live_cores`. The
    # other helpers restrict a DURABLE relation to the cores tier 0 still holds, so they need
    # the membership test; this one already reads `obs`, where the core is a column and
    # `ix_obs_pk` leads on it. A semi-join here would ask the same question twice.
    if one_core:
        stmt = stmt.where(obs.c.core_id == bindparam("rc_core", value="", type_=String))
    return stmt


def q_edge_disagreement():  # ⟡reflect: reflects_edge, as ONE statement
    """Rows where the rebuilt edges and the stored `edge` DISAGREE — normally empty.

    ⚑ THIS IS THE HIGHEST-VOLUME WITHHELD QUERY IN THE REPO, AS A BUILDER. `reconstruct.
    reflects_edge` decodes base64 JSON for 6,274,182 `obs` rows in Python, pulls 6,273,548
    `edge` rows, and set-compares — 12.5M rows moved to compute a set that is normally EMPTY.
    Here the engine does all of it and returns only the disagreement.

    ⚑ AND IT IS A CORE EXPRESSION, NOT A STRING (user, 2026-08-11: *"if SQLAlchemy allows us
    to compose relational algebra expressions in python, that's probably the right way to go
    about it"*). I had been settling expressibility with raw SQL in `--probe` and would have
    landed a `text()` blob — which is outside `--check`'s drift gate and outside `--verify`,
    i.e. exactly the single-source this module exists to be.

    ⚑ THE DECODE CHAIN IS ORDINARY FUNCTION COMPOSITION: `convert_from(decode(ekey,'base64'),
    'UTF8')::jsonb -> 'ch'`, then `jsonb_array_elements_text(...) WITH ORDINALITY` as a
    LATERAL table function — `func.jsonb_array_elements_text(...).table_valued('child',
    with_ordinality='ord')`. `except_`/`union_all` are Core set operators, so the symmetric
    difference composes rather than being spelled.
    """
    rebuilt, stored = _rebuilt_edges(), _stored_edges()
    # ⚑ SYMMETRIC — one direction only would pass when the store holds edges the rebuild
    # does not, which is the half a "rebuilt ⊆ stored" check silently permits.
    #
    # ⚑ `union_all(a, b)` AS A FUNCTION, NOT `a.union_all(b)`. A `CompoundSelect` (what
    # `.except_()` returns) has no chained set-operator methods — measured:
    # `AttributeError: 'CompoundSelect' object has no attribute 'union_all'`. Core models
    # set operations as n-ary constructors over selectables, which is the more honest shape
    # anyway: `A ∪ B` is not a method on A.
    #
    # ⚑ OPEN — DE MORGAN AS A PLANNER LEVER (user, 2026-08-11: *"Can we apply de morgan's
    # laws in order to get more efficient query plans?"*). Recorded here because this builder
    # is the shape it would act on: a symmetric difference is two anti-joins, and an
    # anti-join IS `¬∃` — the same negation De Morgan moves through.
    #
    # ⚑ AND THE PLANNER ALREADY DOES SOME OF IT, which is the first thing to establish before
    # hand-rewriting anything. MEASURED: `SELECT … WHERE NOT EXISTS (…)` plans as an
    # `Anti Join`, not a filtered nested loop. That is exactly why `reclaim`'s GC was rewritten
    # from `NOT IN` to `NOT EXISTS` — `NOT IN` cannot become an anti-join because NULL
    # semantics forbid it, so the 38-minute full scan was a De Morgan question all along
    # (`¬(x ∈ S)` vs `¬∃s∈S. s = x` differ exactly on NULL) without being named as one.
    #
    # ⚑ SO THE REAL QUESTION IS WHERE THE ALGEBRA AND SQL'S THREE-VALUED LOGIC DISAGREE. De
    # Morgan is unconditionally valid in Boolean algebra and NOT unconditionally valid over
    # SQL NULLs — `NOT (a AND b)` ≡ `NOT a OR NOT b` holds in K3, but `NOT IN` vs `NOT EXISTS`
    # shows a rewrite that LOOKS like De Morgan changing the answer. A rewrite is worth
    # applying only where nullability makes the two agree, and `--nullity` is the instrument
    # that says which columns those are: a NOT NULL column is one where the Boolean law is
    # sound. Worth doing as a census (which negated predicates sit over nullable columns)
    # rather than as a per-query tuning pass.
    return union_all(rebuilt.except_(stored), stored.except_(rebuilt))


def q_ref_rows():  # ⟡ref: sppf_db project_ref — the positional reference index
    """The resolver's reference relation: (core, ref position, qname, arg position, arg lit).

    ⚑ A BUILDER, NOT A HAND-WRITTEN STRING (user, 2026-08-07: *"were you editing sql queries
    directly instead of using the sqlalchemy->query builder compile path?"*). I wrote this as
    a raw SQL literal inside `sppf_db.project_ref` — outside the single source, outside
    `--check`'s drift gate, and outside `--verify`. That is exactly why I ended up patching
    joins blind: with no compile step and no verification, the only feedback was a row count,
    and I twice read a FALLING row count as progress while it was dropping 54% of the
    references the index exists to hold.

    ⚑ THE ELIM WALK IS `Def → [] → Apply → Arg → term`, four levels under the v2 generic
    walker where v1 put arguments directly under the reference. Each hop is an `edge` join on
    `(core_id, plid)`; the outer joins keep argument-less references, which a plain join would
    silently drop.

    ⚑ KNOWN: THIS FANS OUT. `Apply` is not the only elim shape, so unconstrained hops emit a
    row per path — duplicates keyed identically on `(core_id, plid, arg_ord)`. Consumers must
    DISTINCT. Constraining the hop is owed; my first attempt at it lost references, and
    coverage is the property that matters (see project_ref's note).
    """
    a = edge.alias("a")
    ap = edge.alias("ap")
    ag = edge.alias("ag")
    ed = edge.alias("ed")
    ao = obs.alias("ao")
    av = event.alias("av")
    rc = terms.alias("rc")
    # ⚑ THE CTOR GATE BELONGS HERE, NOT IN EVERY CONSUMER. Measured: only two ctors carry a
    # qname — `Def` (178) and `QName` (206) — and a `QName` node is the NAME ITSELF, not a
    # reference to it. Indexing both would make every reference appear twice with different
    # argument shapes, which reads as real multiplicity. `scope_fix._event_refs` gates on
    # `_FREE_CTORS` for exactly this reason; putting the filter in the index means a second
    # consumer cannot forget it.
    return (
        select(obs.c.core_id, obs.c.local_id, event.c.qname_pid, a.c.ord, av.c.lit_id)
        .select_from(
            obs.join(event, event.c.ekey == obs.c.ekey)
            .join(rc, rc.c.term_id == event.c.ctor_id)
            .join(
                ed,
                and_(
                    ed.c.core_id == obs.c.core_id,
                    ed.c.plid == obs.c.local_id,
                    ed.c.ord == literal("1"),
                ),
            )
            .outerjoin(a, and_(a.c.core_id == obs.c.core_id, a.c.plid == ed.c.clid))
            .outerjoin(ap, and_(ap.c.core_id == obs.c.core_id, ap.c.plid == a.c.clid))
            .outerjoin(ag, and_(ag.c.core_id == obs.c.core_id, ag.c.plid == ap.c.clid))
            .outerjoin(ao, and_(ao.c.core_id == obs.c.core_id, ao.c.local_id == ag.c.clid))
            .outerjoin(av, av.c.ekey == ao.c.ekey)
        )
        # ⚑ `literal()` PER MEMBER, NOT A BARE `in_(list)`. A plain `in_` compiles to an
        # EXPANDING bindparam (`IN (__[POSTCOMPILE...])`), which the precompiled-SQL
        # runtime cannot bind — it executes the cached string, so the placeholder reaches
        # postgres verbatim (`column "__" does not exist`). Baking the members is what
        # makes this cacheable, and it is the same reason `ed.c.ord == literal("1")` is
        # spelled that way above.
        .where(
            and_(
                event.c.qname_pid.isnot(None),
                rc.c.text.in_([literal(c) for c in sorted(FREE_CTORS)]),
            )
        )
    )


def q_ref_insert():  # ⟡sql-lift: sppf_db project_ref — the WRITE, server-side
    """`INSERT INTO ref SELECT …` — the ref index built WITHOUT the rows crossing the wire.

    ⚑⚑⚑ A DML BUILDER, AND THAT IS THE WHOLE POINT. `project_ref` used to `run("ref_rows")`,
    materialise every row in python, and `upsert` them back — so a projection that is one
    statement on the server became one round-trip per row plus two full traversals of the result
    in the client. The SELECT half was ALREADY a compiled builder (`q_ref_rows`); only the write
    was hand-rolled, which is exactly the seam where the transport cost lived.

    ⚑⚑ IT IS A BUILDER RATHER THAN A FORMATTED STRING BECAUSE READING THE COMPILED ARTIFACT IS
    NOT USING THE COMPILER. A first attempt took `QB.SQL["ref_rows"]` — the compiled text — and
    wrapped `INSERT INTO ref (…) %s` around it in the tool. `sppf_db._selftest`'s own guard
    refused it (*"...with no hand-written INSERT..SELECT in the tool"*) and the operator said the
    same independently: *"Thou shalt not write raw sql. That's why we compile the builders."*
    Composed here, the statement passes through `--compile`, `--check`'s drift gate and
    `--explain` like every other query.

    ⚑ THE FAN-OUT IS PRESERVED, NOT REPAIRED. `q_ref_rows` records that it emits a row per elim
    path — *"duplicates keyed identically on (core_id, plid, arg_ord). Consumers must DISTINCT."*
    `ref` declares no key, so the python path inserted those duplicates verbatim and this does
    too. A `.distinct()` here would be a SEMANTIC change hidden inside a performance change, and
    the builder's own note records an earlier tidy-up that cost 54% of the references.
    """
    # ⚑⚑ POSITIONAL, BECAUSE THAT IS THE CONTRACT THE PYTHON PATH HAD. `q_ref_rows` selects
    # `(obs.core_id, obs.local_id, event.qname_pid, a.ord, av.lit_id)` — labels that do NOT match
    # `ref`'s column names (`plid`, `arg_ord`, …), and the replaced code was
    # `upsert(con, "ref", [tuple(r) for r in rows])`, which zips DECLARED COLUMN ORDER against
    # tuple position. Matching by NAME here raised `KeyError: 'plid'` and would silently have
    # written shifted data if the names had happened to overlap. `from_select` takes the target
    # column list, so the same positional correspondence is stated explicitly instead of implied.
    return ref.insert().from_select([c.name for c in ref.columns], q_ref_rows())


def q_ref_clear_projected():  # ⟡sql-lift: the additive DELETE, as a correlated subquery
    """`DELETE FROM ref WHERE core_id IN (SELECT DISTINCT core_id FROM q_ref_rows)`.

    ⚑ THE ADDITIVE PASS CLEARS EXACTLY THE CORES IT IS ABOUT TO REWRITE — the drain's own
    granularity. Clearing the whole table (the destructive path) would delete rows of cores that
    have already drained out of the event tier and can never be re-derived.

    ⚑ WAS `execute_many(… , [(c,) for c in sorted({r[0] for r in rows})])` — the core set
    computed in python from a fully-materialised result, then sent back one parameter tuple at a
    time. The set lives in the query; computing it here means the DELETE and the INSERT read the
    SAME source, so they cannot disagree about which cores are in scope.
    """
    src = q_ref_rows().subquery("r")
    return ref.delete().where(ref.c.core_id.in_(select(src.c.core_id).distinct()))


#: ⟡pack-slice-within-level — the per-level ASSIGNMENT table `q_lvl_assign` writes and `q_lvl_emit`
#: reads in windows. Declared against a PRIVATE MetaData for the same reason `_ht_map_t` is: the
#: shared one is the schema authority that `--census`/`--ddl` read, and a per-connection disposable
#: registered there would read as a declared tier.
_LVL_TBL = "_lvl_assign"
_sig_tbl_t = Table(
    _LVL_TBL,
    MetaData(),
    Column("core_id", String),
    Column("local_id", Integer),
    Column("node_id", String),
    Column("ch", Text),
)


def _level_sig(_materialised, _core, _ht):
    """The level's `(core_id, local_id, <signature columns>, kids)` — ONE body, three consumers.

    ⚑ EXTRACTED FOR ⟡pack-slice-within-level, and the seam is the same one `_height_src` uses:
    `q_pack_level` and `q_lvl_assign` need this identically, so a copy would be a second spelling
    of the fold's most correctness-critical stage. The signature key is what the whole equivalence
    argument turns on — `idx` was once dropped from it and passed three IDENTICAL verdicts.
    """
    ht = _height_src(_materialised)
    kids = (
        select(
            edge.c.core_id.label("core_id"),
            edge.c.plid.label("plid"),
            func.array_agg(aggregate_order_by(obs_node.c.node_id, edge.c.ord)).label("kids"),
        )
        .select_from(
            edge.join(
                obs_node,
                and_(obs_node.c.core_id == edge.c.core_id, obs_node.c.local_id == edge.c.clid),
            )
        )
        .where(edge.c.core_id == _core)
        .group_by(edge.c.core_id, edge.c.plid)
        .subquery("k")
    )
    return (
        select(
            ht.c.core_id,
            ht.c.local_id,
            event.c.ctor_id,
            event.c.qname_pid,
            event.c.idx,
            event.c.lit_id,
            func.coalesce(kids.c.kids, literal_column("'{}'::text[]")).label("kids"),
        )
        .select_from(
            ht.join(obs, and_(obs.c.core_id == ht.c.core_id, obs.c.local_id == ht.c.local_id))
            .join(event, event.c.ekey == obs.c.ekey)
            .outerjoin(kids, and_(kids.c.core_id == ht.c.core_id, kids.c.plid == ht.c.local_id))
        )
        .where(ht.c.ht == _ht)
        .cte("s")
    )


def q_pack_level(_materialised=False):  # ⟡sql-lift: ONE level of project_sppf's packing fold
    """`(core_id, local_id, node_id)` for every observation at height `:ht` — ids minted server-side.

    ⚑⚑⚑ THE SIGNATURE MUST CARRY THE CHILDREN'S **ASSIGNED IDS**, NOT THEIR HEADS, and
    `sppf_db.py:811-822` records what happens otherwise: a key built from a node's own head plus
    its children's HEADS is depth-2 information, so *"any two terms agreeing to depth 2 collapse
    into one node"*. **MEASURED: all 926 `QName` observations interned to a SINGLE node_id,
    carrying 52 distinct qnames** — every QName has a constant head and constant-headed children,
    so the key was byte-identical for all of them. A child's node_id is content-complete because
    it is itself built from its children's ids; that is the whole reason the fold is bottom-up,
    and it is why this runs per LEVEL rather than as one statement.

    ⚑⚑ `array_agg(… ORDER BY ord)` IS THE SIGNATURE'S CHILD COMPONENT, and the ORDER BY is
    load-bearing: `(f a b)` and `(f b a)` are different terms with the same child SET. The python
    spelling is `tuple(packing.get(...) for _, _cl in sorted(_kids))` — the same ordering, over
    the same `edge.ord`.

    ⚑⚑ GROUP BY RATHER THAN `DISTINCT` OVER THE ARRAY — A PREFERENCE, AND THE STRONGER CLAIM WAS
    RETRACTED. An earlier version of this docstring said a `DISTINCT` over an array "degrades to
    a sort — a measured 8+ minutes without emitting a row", citing `dec_tree.py:70-77`. That
    citation is real but it is about **`text[]` as a JOIN KEY** (no hash opclass ⇒ Merge Join ⇒
    sort 4.1M path arrays), which is a different statement from a `DISTINCT` in a projection.
    The 8-minute figure was borrowed across that gap, and the run I thought had confirmed it here
    had actually hit the HARNESS's 300s foreground limit — not a postgres stall. Both
    formulations complete.

    ⚑ SO: `GROUP BY` is kept because it is the idiom that measurably wins and because the array
    genuinely has no hash opclass to lean on — but "DISTINCT does not finish" is NOT established,
    and `query_defs.py --explain` is the instrument that would settle it. Recorded rather than
    quietly corrected: a performance claim inherited from an adjacent measurement is exactly the
    prose-forging-a-structural-fact shape this file's own `--check` gate exists to prevent.

    ⚑ `:base + dense_rank()` REPRODUCES `_next += 1` EXACTLY, and `:base` is where
    `_seed_node_ids`' `_top + 1` feeds in on the additive path — `sppf_db.py:639` states the
    coupling: *"Two things had to change together — the DROP and the surrogate numbering; either
    alone corrupts."* `dense_rank` (not `row_number`) is what makes the id a function of the
    SIGNATURE rather than of the row, so equal signatures share an id.

    ⚑ THE ID IS A SURROGATE OVER THE SIGNATURE, NOT AN ENCODING OF IT (`sppf_db.py:833-838`) —
    so ids assigned here need not match the python's numbering, only its PARTITION. That is what
    the equivalence check compares.
    """
    _core = bindparam("core_id", value="", type_=String)
    _ht = bindparam("ht", value=0, type_=Integer)
    _base = bindparam("base", value=0, type_=Integer)
    # ⚑ THE CHILDREN'S ids AND THE HEIGHT SOURCE NOW LIVE IN `_level_sig` — the height source is
    # still the only stage that varies between this builder and its materialised twin, which is
    # why the twin stays a one-line caller.
    #
    # ⚑⚑⚑ `idx` IS PART OF THE SIGNATURE AND OMITTING IT COLLAPSES DE BRUIJN INDICES. The python
    # head is `("AgdaCore", role, ctor, qname, litval)` with `role = "db%d" % idx`
    # (`sppf_db.py:754-756`), so two `Var` nodes at different indices are DIFFERENT terms. A first
    # cut of this builder grouped on `(ctor_id, qname_pid, lit_id)` only — dropping `idx` and
    # merging every `Var` in a core into one node.
    #
    # ⚑⚑ AND THE EQUIVALENCE CHECK PASSED ANYWAY, WHICH IS THE PART WORTH RECORDING. `--nullity
    # event` reports `idx` NULL in **2,124,418 of 2,124,418 rows**: the sandbox cannot
    # discriminate on it, so `pack.sql` and `pack.python` agreed on every level tested. A gate
    # over a population whose values are constant is a gate that cannot fail — the same shape as
    # `reflects_obs`' empty core reporting "0 row(s) reconstructed exactly". The column census
    # caught what three IDENTICAL verdicts could not.
    #
    # ⚑ THE STORE'S OWN WARNING SAYS SO TOO: `sppf_db.py:773` prints *"N Var/PVar event(s) have
    # NULL idx — every one interns role 'db?', collapsing de Bruijn indices. Re-ingest to
    # populate via recover_fields()."* That is a defect in the DATA the projection reads, not a
    # licence to drop the column from the key.
    # ⚑⚑ THE BODY IS `_level_sig`, SHARED WITH `q_lvl_assign` — extracted for
    # ⟡pack-slice-within-level rather than copied. It is a **CTE**, not a subquery, and `EXPLAIN`
    # is why: as a `.subquery()` it appeared TWICE in the plan, so the height source, the
    # obs/event joins and the child `array_agg` were all computed twice per level.
    sig = _level_sig(_materialised, _core, _ht)
    _key = (sig.c.ctor_id, sig.c.qname_pid, sig.c.idx, sig.c.lit_id, sig.c.kids)
    # ⚑⚑⚑ ⟡window-not-rejoin — ONE WINDOW PASS, NO GROUP-AND-REJOIN (operator, 2026-08-22:
    # *"We shifted away from DISTINCT to EXISTS specifically because of this kind of mess."*).
    # This built a GROUPED subquery `n` to MINT the ids, then joined it BACK onto `sig` on all
    # five key columns — four of them with `IS NOT DISTINCT FROM` — purely to discover which row
    # had received which id. `dense_rank()` is a WINDOW function: it already assigns equal ranks
    # to equal key tuples over the ungrouped rows, so the group, the join, and the five NULL-safe
    # predicates were re-deriving what the window emits directly.
    #
    # ⚑⚑ AND THE JOIN DEGENERATED TO A CROSS JOIN, MEASURED. `IS NOT DISTINCT FROM` has no hash
    # opclass, so only `kids` (plain `=`) reached the hash condition and the other four became a
    # post-filter. At height 0 every leaf has `kids = '{}'` — `--pack-level` reports
    # `children=1`, ONE distinct value — so the single hashable column is CONSTANT and everything
    # matched everything: `Hash Cond: (s_1.kids = s.kids)` with
    # **`Rows Removed by Join Filter: 39,784,050`** for 176,818 input rows (= 176,818 × 226
    # node ids). ~18s of a ~28s level, and it scales with level size.
    #
    # ⚑ THE NULL SEMANTICS ARE PRESERVED, NOT ASSUMED — probed before the edit rather than
    # reasoned about, because this is exactly the change that would silently repartition:
    #     dense_rank() OVER (ORDER BY a, b) over (1,NULL),(1,NULL),(NULL,NULL),(NULL,NULL)
    #       → ranks 2,2,3,3 — NULLs compare EQUAL, matching GROUP BY and IS NOT DISTINCT FROM.
    #     over '{}','{}',{1,2},{1,2},{2,1}  → 1,1,2,2,3 — equal arrays share a rank AND
    #       {1,2} ≠ {2,1}, so the `ORDER BY ord` order-sensitivity this docstring calls
    #       load-bearing ((f a b) vs (f b a)) survives.
    #
    # ⚑ `dense_rank`, STILL NOT `row_number` — the id must be a function of the SIGNATURE, not of
    # the row, so equal signatures share an id. That property is what the window provides and is
    # the whole reason the rejoin was expressible at all.
    return select(
        sig.c.core_id,
        sig.c.local_id,
        (_base + func.dense_rank().over(order_by=_key)).label("node_id"),
    )


# ⚑⚑⚑ THE MATERIALISED TWINS — one line each, because the fold was decomposed at the seam where
# the variation is. `kids`, `sig`, `newsig` and the join back are shared verbatim; only the
# height SOURCE differs, so there is exactly one body to keep correct and no copy to drift.
#
# ⚑⚑ SEPARATE REGISTRY ENTRIES BECAUSE THE CACHE KEYS ON NAME. `SQL[name]` is one text and one
# default set, so a builder cannot carry two compiled forms under one key — a `materialised=`
# runtime parameter would silently serve whichever form was compiled last. Named twins make the
# choice explicit at the CALL SITE (`QB.run(con, "pack_level_mat", …)`), which is also what lets
# `pack_core_sql` opt in without every other consumer of the fold changing.
#
# ⚑ THEY REQUIRE `_ht_map` TO EXIST — a caller that has not materialised it gets a clean
# "relation does not exist" rather than a wrong answer, which is the right failure: the map is a
# precondition of these entries, not an ambient condition they should paper over.
def q_pack_level_mat():  # ⟡sql-lift: q_pack_level over the MATERIALISED height map
    """`q_pack_level`, reading the per-core temp `_ht_map` instead of re-deriving the CTE."""
    return q_pack_level(_materialised=True)


def q_lvl_assign(_materialised=True):  # ⟡pack-slice-within-level: STAGE 1 — (local_id → node_id)
    """`(core_id, local_id, node_id, ch)` for the WHOLE level — the assignment, materialised once.

    ⚑⚑⚑ ⟡pack-slice-within-level — STAGE 1 OF TWO, AND THE SLICE IS NOT A ROW RANGE OVER THE FOLD
    (operator, 2026-08-22: *"I need the commits to be fine-grained, period."*). A first cut sliced
    `pack_level_insert` on `local_id` directly, and it is WRONG: `dense_rank()` ranks over the
    WHOLE level, so two slices rank independently and mint DIFFERENT ids for the SAME signature.
    MEASURED on `wpk3blnvCNA` ht 0 — **176,818 observations → 226 signatures**, scattered across
    every `local_id`, so a positional slice splits nearly every signature. That is the
    duplicate-id corruption `_seed_node_ids` records (*"signature S gets id 3 in run 2 while id 3
    already denotes a different signature from run 1 … silent corruption, not a conflict"*),
    reached by slicing rather than by re-running.

    ⚑⚑ SO THE ASSIGNMENT IS COMPUTED WHOLE AND THE **WRITE** IS SLICED. This statement produces
    `(local_id → node_id)` for the entire level into a temp table — the ranking is intact and
    atomic — and `q_lvl_emit` then copies it into `obs_node` in `local_id` windows, each its own
    transaction. The expensive-and-indivisible part stays one statement; the bulky part becomes N
    commits. Nothing is re-ranked, so the partition `--equiv` compares is unchanged by
    construction.

    ⚑ AND IT CARRIES `ch` HERE rather than in the emit, because `ch` is the POSITIONAL child fibre
    (`string_agg(clid ORDER BY ord)`) and joining `edge` once for the level beats joining it once
    per slice.
    """
    _core = bindparam("core_id", value="", type_=String)
    _ht = bindparam("ht", value=0, type_=Integer)
    _base = bindparam("base", value=0, type_=Integer)
    sig = _level_sig(_materialised, _core, _ht)
    _key = (sig.c.ctor_id, sig.c.qname_pid, sig.c.idx, sig.c.lit_id, sig.c.kids)
    ch = (
        select(
            edge.c.core_id.label("core_id"),
            edge.c.plid.label("plid"),
            func.string_agg(
                cast(edge.c.clid, Text), aggregate_order_by(literal(","), edge.c.ord)
            ).label("ch"),
        )
        .where(edge.c.core_id == _core)
        .group_by(edge.c.core_id, edge.c.plid)
        .subquery("c")
    )
    return select(
        sig.c.core_id,
        sig.c.local_id,
        (_base + func.dense_rank().over(order_by=_key)).label("node_id"),
        func.coalesce(ch.c.ch, literal("")).label("ch"),
    ).select_from(
        sig.outerjoin(ch, and_(ch.c.core_id == sig.c.core_id, ch.c.plid == sig.c.local_id))
    )


def q_lvl_emit():  # ⟡pack-slice-within-level: STAGE 2 — one COMMITTABLE slice
    """`(core_id, local_id, node_id, ch)` for `local_id ∈ [:lo, :hi)` of the assigned level.

    ⚑⚑ A PURE RANGE READ OFF THE ASSIGNMENT — no ranking, no signature comparison, no join to
    `edge` or `event`. That is what makes slicing SOUND here and unsound one stage earlier: a
    lookup returns the same answer over any subset, a `dense_rank()` does not.

    ⚑ THE WIDTH IS THE CALLER'S, because commit granularity is a policy decision and not a
    property of the data. The caller reads the level's row count and picks; this builder only
    honours the bound.
    """
    _lo = bindparam("lo", value=0, type_=Integer)
    _hi = bindparam("hi", value=2**31 - 1, type_=Integer)
    a = _sig_tbl_t.alias("a")
    return select(a.c.core_id, a.c.local_id, a.c.node_id, a.c.ch).where(
        and_(a.c.local_id >= _lo, a.c.local_id < _hi)
    )


def q_obs_heights_distinct_mat():  # ⟡sql-lift: the schedule, from the materialised map
    """`q_obs_heights_distinct` over `_ht_map` — the loop bound, without a 70-level recursion."""
    return q_obs_heights_distinct(_materialised=True)


def q_pack_discrimination_mat():  # ⟡sql-lift: the strength statement, from the materialised map
    """`q_pack_discrimination` over `_ht_map`."""
    return q_pack_discrimination(_materialised=True)


def q_pack_level_insert_mat():  # ⟡sql-lift: the WRITE path over the materialised map
    """`q_pack_level_insert` over `_ht_map` — the entry `pack_core_sql` runs per level."""
    return q_pack_level_insert(_materialised=True)


def q_pack_level_summary_mat():  # ⟡sql-lift: the READ path over the materialised map
    """`q_pack_level_summary` over `_ht_map` — the `write=False` twin."""
    return q_pack_level_summary(_materialised=True)


def q_unit_members():  # ⟡sql-lift: unit → its member NODES, the reachability half
    """`(unit_id, node_id)` — every node reachable from a unit's root, for one core.

    ⚑⚑⚑ THIS IS **NOT** `q_reach`, AND THE DIFFERENCE IS THE CARRIER. `query_decl.py:1160-1165`
    names `sppf_db.py`'s unit-membership DFS as the loop `q_reach` was built from, and that is
    true of its SHAPE and false of its RELATION. `q_reach` closes over `node_child` —
    POST-SHARING node ids. This walk closes over `edge` — PRE-SHARING per-core `local_id`s — and
    only then maps each reached observation through `obs_node` to a node id. The projection's own
    comment says so (`sppf_db.py:994`): *"reach from root over the acyclic raw edges — pre-sharing,
    no closure"*.

    ⚑⚑ THE SETS ARE DIFFERENT, NOT MERELY THE SPELLING. Sharing merges distinct observations into
    one node, so a closure taken over `node_child` from a shared root reaches everything ANY unit
    containing that node reaches. Substituting `q_reach` here would have silently widened every
    unit's membership — a change in DATA, passing as a refactor, in the relation
    `unit_node` that 12 builders join on (`query_registry`: breadth 12 on `unit_node.node_id`).

    ⚑ SO THE REUSE WAS REAL AND THE INSTANTIATION WAS WRONG. The right reuse is the CTE SHAPE —
    anchor on the root, step over the child relation, UNION for the distinct closure — over this
    walk's own carrier. Recorded because "q_reach already does this" was on the plan as a
    one-line swap.

    ⚑ `UNION`, NOT `UNION ALL`: the python carries an explicit `seen` set (`sppf_db.py:1017-1024`),
    and UNION is exactly that dedup — which is also what makes the recursion terminate.

    ⚑⚑⚑ AND THIS SHOULD REPLACE THE STORED `unit_node`, NOT MERELY REPRODUCE IT. Operator,
    2026-08-15: *"It needs to not reference (unit_id, node_id), it needs to reference WHAT THAT
    MEANS. … The fact that something can be invalidated means that the query depended on reified
    state."*

    ⚑⚑ THE INVALIDATION IS MEASURED, AND MY FIRST RESPONSE TO IT WAS THE WRONG KIND. A refold
    renumbers a core's surrogates, so `unit_node` rows written under the old numbering point at
    different signatures — `--equiv` reported 326 pairs on each side, SQL ids 139-147 against
    stored ids 1708-1812. I added a WARNING ("N stale rows, re-run the unit half"), which treats
    a design defect as an operational caveat. A stored `(unit_id, node_id)` is a HANDLE, and
    `pycodemod --relname unit_node` shows every one of its 21 SQL read sites immediately joining
    `_node` to dereference it (`n.op` / `nd.role` / `nd.kind` / `p2.text`). Nobody wants the id.

    ⚑ SO THE TIER RULE APPLIES TO RELATIONS, NOT ONLY TO TIERS: build the higher from the lower
    such that the lower stays recoverable. `unit_obs` (which unit, which root), `edge` (the raw
    child fibre) and `obs_node` (observation → node) are the lower tiers; membership is their
    composite, so it is a QUERY and cannot go stale by construction. `_seed_node_ids` already
    argues the same direction for the signature (*"the signature is RECOVERED, not stored"*).

    ⚑ NOT YET RETIRED — `unit_node` still has 21 reader sites and a `--verify` arm
    (`members.python`) pinning this closure against it. Retiring a relation 8 files read is its
    own increment; this docstring is the reason, recorded where the replacement lives.
    """
    _core = bindparam("core_id", value="", type_=String)
    roots = (
        select(unit_obs.c.unit_id.label("unit_id"), unit_obs.c.root_lid.label("lid"))
        .where(unit_obs.c.core_id == _core)
        .cte("r", recursive=True)
    )
    step = (
        select(roots.c.unit_id, edge.c.clid)
        .select_from(edge.join(roots, edge.c.plid == roots.c.lid))
        .where(edge.c.core_id == _core)
    )
    reach = roots.union(step)  # UNION = the python's `seen` set
    return (
        select(reach.c.unit_id, obs_node.c.node_id)
        .distinct()
        .select_from(
            reach.join(
                obs_node, and_(obs_node.c.core_id == _core, obs_node.c.local_id == reach.c.lid)
            )
        )
    )


def q_unit_members_stored():  # ⟡sql-lift: the PYTHON arm — what `unit_node` already holds
    """`(unit_id, node_id)` from the stored `unit_node`, scoped to one core.

    ⚑ THE REFERENCE ARM for `q_unit_members`. `unit_node` has no `core_id` column — membership is
    keyed by unit — so the scope comes through `_unit.file_id`, which IS the core id
    (`sppf_db.py:1028`: *"`_unit.file_id` IS the core id, so the pairs of exactly this pass's
    cores are reachable by one join"*).

    ⚑ WITHOUT THIS ARM THE COMPARISON IS `--equiv unit_members unit_members`, which is a smoke
    test wearing a verdict's clothes — I ran exactly that and got IDENTICAL, which established
    only that the builder is deterministic.
    """
    _core = bindparam("core_id", value="", type_=String)
    return (
        select(unit_node.c.unit_id, unit_node.c.node_id)
        .select_from(unit_node.join(_unit, _unit.c.unit_id == unit_node.c.unit_id))
        .where(_unit.c.file_id == _core)
    )


def q_node_id_top():  # ⟡sql-lift: the surrogate counter's high-water mark
    """`(top)` — the highest numeric `node_id` the durable tier has issued, or 0.

    ⚑⚑⚑ THE COUNTER MUST BE SEEDED FROM THE STORE OR AN ADDITIVE PROMOTE CORRUPTS SILENTLY.
    `project_sppf:846-848`: *"a second `project_sppf` over a DIFFERENT set of live cores restarts
    the numbering: signature S gets id 3 in run 2 while id 3 already denotes a different
    signature from run 1 … silent corruption, not a conflict."* A per-core promote is that second
    run 152 times over, so every core must start above every id already issued.

    ⚑⚑ IT IS ONE AGGREGATE BECAUSE THE MAP IS NOT WANTED. `_seed_node_ids` returns
    `(signature → id, top)` and builds the map by scanning ALL of `node_child` and `_node` — the
    python fold looks signatures up in it, but the SQL fold re-derives sharing per level through
    `obs_node`, so it needs the counter alone. Calling the full seeder once per core would scan
    both relations 152 times to discard the larger half of the answer each time: the same
    materialise-then-throw-away shape this arc has now removed three times.

    ⚑ `node_id ~ '^[0-9]+$'` MIRRORS `_seed_node_ids`' `if nid.isdigit()`. The column is TEXT and
    ids are store-local (`_mk_interners`' content-derived addressing), so a non-numeric id is
    possible by construction and must not poison a `max`. `coalesce(…, 0)` makes an empty durable
    tier answer 0 rather than NULL — the first-run case, which is the live store today.
    """
    return select(
        func.coalesce(func.max(cast(_node.c.node_id, Integer)), literal(0)).label("top")
    ).where(_node.c.node_id.op("~")(literal("^[0-9]+$")))


def q_unprojected_cores():  # ⟡sql-lift: the promote's residue, PER CORE and ordered
    """`(core_id, n)` — cores holding observations with no `obs_node` row, largest first.

    ⚑⚑⚑ THIS IS WHAT MAKES THE PROMOTE A **BOUNDED UNIT**. `converge`'s contract is *"do ONE
    bounded unit at the highest boundary with work, restart from the top"* — but `_do_promote`
    calls `project_sppf` over the WHOLE store, so at the promote boundary the "unit" is the
    entire 6,274,182-row residue. One step that either finishes or loses everything is not a
    fixpoint step; it is the batch the fixpoint was built to replace.

    ⚑⚑ IT IS THE SAME RESIDUE `work_promote` ALREADY ASKS, GROUPED. That predicate is
    `EXISTS (obs LEFT JOIN obs_node … WHERE n.core_id IS NULL)` — and its docstring states the
    property this builder depends on: *"THE WORK PREDICATE AND THE WORK ARE THE SAME SET."* So a
    per-core promote is not a new mechanism, it is that set with a `GROUP BY` and no `EXISTS`.

    ⚑ ORDERED LARGEST-FIRST, which is the operator's tail-first ruling expressed in the query
    rather than in a driver's sort. Measured live: 152 cores, median 6,212, max 943,927 — five
    above 367k. If the tail is going to fail it should fail on step one, before 147 smaller cores
    of work have landed.

    ⚑ NO `obs_node` EXISTENCE TEST. It is a declared tier applied by the writer
    (`pack_core_sql`), so on a store where it is absent this query is simply every core — which
    is the correct answer, not an error to handle.
    """
    return (
        select(obs.c.core_id, func.count().label("n"))
        .select_from(
            obs.outerjoin(
                obs_node,
                and_(obs_node.c.core_id == obs.c.core_id, obs_node.c.local_id == obs.c.local_id),
            )
        )
        .where(obs_node.c.core_id.is_(None))
        .group_by(obs.c.core_id)
        .order_by(func.count().desc())
    )


def q_pack_level_summary(
    _materialised=False,
):  # ⟡sql-lift: the level's THREE NUMBERS, without its rows
    """`(n, ids, top)` for one level — the read-path twin of `q_pack_level_insert`'s aggregate.

    ⚑ THE TWO PATHS MUST RETURN THE SAME SHAPE or the caller branches on which mode it is in,
    which is how `pack_core_sql` came to run a level twice in an earlier cut. Same aggregate,
    same casts; only the write differs.

    ⚑ `--pack-level` still uses `q_pack_level` itself, because that mode's job is to report the
    sharing collapse and it needs the rows to do it — at a bounded, caller-chosen height.
    """
    p = q_pack_level(_materialised).subquery("p")
    return select(
        func.count().label("n"),
        func.count(distinct(p.c.node_id)).label("ids"),
        func.coalesce(func.max(cast(p.c.node_id, Integer)), literal(0)).label("top"),
    ).select_from(p)


def q_unprojected_cores_shard():  # ⟡sql-lift: the shard's OWN slice of the promote residue
    """`(core_id, n)` — unprojected cores whose id hashes to THIS shard, largest first.

    ⚑⚑⚑ THE CLAIM STEP THAT SHARDING NEEDS, AND ITS ABSENCE WOULD HAVE BEEN SILENT. The unsharded
    `q_unprojected_cores` is residue-driven with no cursor — deliberately, so a kill loses at most
    the core in flight. That property makes it perfectly safe for ONE worker and perfectly WRONG
    for N: every worker asks the same question and gets the same largest-first head, so three
    shards would fold the SAME core three times, each minting a different id block for identical
    signatures. `ix_obsnode_pk` would swallow the duplicates via `ON CONFLICT DO NOTHING` and the
    run would look successful while two thirds of the work was wasted and the sharing was wrong.
    #
    ⚑⚑ `hashtext(core_id) % shards = shard` — A PARTITION, NOT A LOCK. Every worker computes its
    own slice with no coordination, no claim table, and no lease to expire; a worker that dies
    leaves its slice unclaimed and a re-run picks it up because the predicate is still a residue
    read. Coordination-free is what keeps the resumability argument intact — a claim table would
    be the "second cursor that dies with the process" this loop exists to avoid.
    #
    ⚑ `abs()` BECAUSE `hashtext` IS SIGNED, and `%` on a negative left operand is negative in
    postgres: `hashtext(x) % 3` yields -2..2, so a shard numbered 0..2 would silently never match
    the negative half of the corpus. That is a partition that looks total and covers ~half.
    #
    ⚑ LARGEST-FIRST WITHIN THE SHARD, preserving the tail-first ruling per worker: if a shard
    holds a 943,927-observation core, that core surfaces on its step one rather than after its
    smaller siblings have landed.
    """
    _shards = bindparam("shards", value=1, type_=Integer)
    _shard = bindparam("shard", value=0, type_=Integer)
    return (
        select(obs.c.core_id, func.count().label("n"))
        .select_from(
            obs.outerjoin(
                obs_node,
                and_(obs_node.c.core_id == obs.c.core_id, obs_node.c.local_id == obs.c.local_id),
            )
        )
        .where(
            and_(
                obs_node.c.core_id.is_(None),
                func.abs(func.hashtext(obs.c.core_id)) % _shards == _shard,
            )
        )
        .group_by(obs.c.core_id)
        .order_by(func.count().desc())
    )


def q_edge_postorder():  # ⟡sql-lift: is `local_id` POST-ORDER, corpus-wide?
    """`(total, post_order, max_parents)` over the WHOLE `edge` relation.

    ⚑⚑⚑ THE PRECONDITION FOR REPLACING THE RECURSION, AND IT WAS A SANDBOX MEASUREMENT QUOTED AS
    A CORPUS FACT. `pack_core_sql`'s docstring records *"`clid < plid` on 177,370/177,370 edges"* —
    true, measured, and taken on the SANDBOX tenant. The live corpus holds 6,273,548 edges, 35×
    that, and nothing had asked it the same question. A structural claim that licenses deleting a
    recursive CTE is exactly the kind that must not be inherited across tenants.

    ⚑⚑ POST-ORDER IS WHAT MAKES HEIGHT A SINGLE ASCENDING PASS. If every child's `local_id` is
    below its parent's, then processing observations in ascending `local_id` visits every child
    before its parent, so `ht[p] = 1 + max(ht[children])` needs no recursion — one ordered scan
    instead of the nested-loop index probe per edge per level that costs 283K buffer hits on a
    6,210-row core and does not parallelize (postgres will not parallelize a recursive CTE, which
    is why the box sits idle while one backend burns).

    ⚑ `max_parents` IS REPORTED BESIDE IT because the forest-of-trees property is the OTHER half:
    height is well-defined without a visited set only if each child has one parent. Both are
    stated in the fold's docstring from the same sandbox run; both are checked here together, so
    a tenant where either fails is refused rather than silently mis-folded.
    """
    return select(
        func.count().label("total"),
        func.count().filter(edge.c.clid < edge.c.plid).label("post_order"),
        select(func.coalesce(func.max(literal_column("pc")), 0))
        .select_from(
            select(func.count().label("pc"))
            .select_from(edge)
            .group_by(edge.c.core_id, edge.c.clid)
            .subquery("p")
        )
        .scalar_subquery()
        .label("max_parents"),
    ).select_from(edge)


def q_obs_heights_distinct(
    _materialised=False,
):  # ⟡sql-lift: the SCHEDULE ONLY — ~70 ints, not 943,927 rows
    """`(ht)` — the distinct heights present in one core, ascending.

    ⚑⚑⚑ THE LEVEL LOOP NEEDS ~70 INTEGERS AND WAS PULLING 943,927 ROWS TO GET THEM.
    `pack_core_sql` opened with `sorted({r[2] for r in QB.run(con, "obs_height", …)})` — every
    observation's height crossing the wire so python could take the distinct set. Measured on the
    live tail core (`sppf_db.py --height`, read-only): **943,927 observations, 70 distinct
    heights.** A 13,000:1 materialisation to compute a loop bound.

    ⚑ INVISIBLE AT THE SCALE IT WAS BUILT AT. The four verified cores were 7k–55k, where the same
    line moves 55,551 rows and costs nothing noticeable. The tail is 17× larger, and the defect
    scales with core size while the answer does not — `DISTINCT` is 70 rows at any size.

    ⚑ SAME SHAPE AS THE TRANSPORT DEFECT THIS WHOLE ARC BEGAN WITH: work done client-side that
    the server was already positioned to do. Distinct-ing in python is the row-at-a-time INSERT
    one layer up.
    """
    h = _height_src(_materialised)
    return select(h.c.ht).distinct().order_by(h.c.ht)


def q_pack_level_insert(
    _materialised=False,
):  # ⟡sql-lift: the packing fold's WRITE, one level, server-side
    """`INSERT INTO obs_node … SELECT q_pack_level … RETURNING` — the level's rows never leave pg.

    ⚑⚑ ONE STATEMENT WRITES AND REPORTS. `RETURNING` is what lets the caller advance its `base`
    without re-running the level to count it: a first version of `pack_core_sql` ran the SELECT
    to count and then the INSERT to write, computing every level twice and threading a
    re-derived base back in.

    ⚑ `ON CONFLICT DO NOTHING` because `obs_node` carries `ix_obsnode_pk` UNIQUE on
    `(core_id, local_id)` — which `sppf_db.py:879` still describes as *"declares no key"*, a
    comment a selftest case falsified today. Idempotence matters here specifically: the level
    loop is resumable, so re-running a level that partly landed must not double its rows.

    ⚑⚑ `ch` IS COMPUTED HERE, NOT LEFT NULL. `project_sppf` stores it as the comma-joined child
    `local_id`s in `ord` order (`sppf_db.py:873-878`), and it is load-bearing: *"obs_node ⋈ _node
    determines only 56.2% of ekeys; the missing 43.8% is the CHILDREN, whose only home was tier-0
    `edge`"* — persisting it is what breaks the mutual dependency that made neither `obs` nor
    `edge` drainable. A first cut of this builder omitted the column and proposed to "declare the
    gap"; the column is nullable with no default, so that would have written NULL into the one
    field the drain licence turns on.

    ⚑ THE JOIN IS ON `local_id`, NOT `node_id` — `ch` is the POSITIONAL child fibre (which
    observations are the children), a different fact from the signature's child ids (which NODES
    they interned to). `sppf_db.py:869-872` records why it is positional: `edge.ord` is dense
    `0..n-1` on all 77,759 parents, measured zero ragged, so sorting by `ord` and joining the ids
    is lossless.
    """
    src = q_pack_level(_materialised).subquery("p")
    # ⚑⚑ SCOPED TO THE CORE — visible ONLY in the compiled text, which is why `--sql` is part of
    # the loop and not a formality. A first cut wrote `FROM edge GROUP BY core_id, plid` with no
    # `WHERE`, so computing ONE core's child lists aggregated all 6.27M corpus edges. The join
    # above would still have selected the right rows; the cost was invisible in the builder and
    # obvious in the SQL. Same defect the height CTE had (`dec_tree.chain_sql` records it as a
    # scoping REQUIREMENT, not an optimisation) — and I reintroduced it one function later.
    ch = (
        select(
            edge.c.core_id.label("core_id"),
            edge.c.plid.label("plid"),
            func.string_agg(
                cast(edge.c.clid, Text), aggregate_order_by(literal(","), edge.c.ord)
            ).label("ch"),
        )
        .where(edge.c.core_id == bindparam("core_id", value="", type_=String))
        .group_by(edge.c.core_id, edge.c.plid)
        .subquery("c")
    )
    # ⚑⚑⚑ THE `RETURNING` IS AGGREGATED, NOT STREAMED — the caller wants THREE NUMBERS and was
    # receiving one row per observation to compute them. `pack_core_sql` did
    # `got = list(QB.run(...))`, then `{r[2] for r in got}`, then `max(int(n) for n in …)`: for
    # the tail core's largest level that is **529,003 rows materialised in python** to derive
    # (count, distinct ids, max id). Measured live and read-only via `--height` BEFORE any write,
    # which is the whole reason the tail was measured first.
    #
    # ⚑⚑ A DATA-MODIFYING CTE IS WHAT MAKES IT ONE STATEMENT. `INSERT … RETURNING` cannot be
    # aggregated in place, so the insert becomes a CTE and the outer query aggregates its output:
    # the level lands and reports in a single round trip with nothing but the summary crossing
    # the wire. `dec_tree._RUNG` uses the same construction (`INSERT … RETURNING` inside a CTE
    # the outer statement reads) for the same reason.
    #
    # ⚑ `max(node_id::bigint)`, NOT `max(node_id)` — the column is TEXT (ids are store-local
    # strings, `_mk_interners`' content-derived addressing), so a text max would order '9' above
    # '10' and the next level's `base` would go BACKWARDS. The python spelling was
    # `max(int(n) for n in _here)`, i.e. the cast was always there; moving the aggregate server-
    # side must move the cast with it.
    # ⚑ THE POSTGRES INSERT, NOT THE GENERIC ONE — `on_conflict_do_nothing` is dialect-specific
    # and `Insert` has no such attribute (measured: AttributeError at compile). Legitimate here
    # because `_compile_one` renders against `_store.dialect()`, ONE dialect, the live backend —
    # the cache and the executor must name the same one or the committed SQL describes a
    # different database than the runtime talks to.
    from sqlalchemy.dialects.postgresql import insert as _pg_insert

    ins = (
        _pg_insert(obs_node)
        .from_select(
            ["core_id", "local_id", "node_id", "ch"],
            select(
                src.c.core_id, src.c.local_id, src.c.node_id, func.coalesce(ch.c.ch, literal(""))
            ).select_from(
                src.outerjoin(ch, and_(ch.c.core_id == src.c.core_id, ch.c.plid == src.c.local_id))
            ),
        )
        # ⚑⚑⚑ ⟡pack-level-commit — THE CLAUSE THIS DOCSTRING ALREADY PROMISED AND THE CODE DID
        # NOT HAVE (2026-08-22). The ⚑ above says *"`ON CONFLICT DO NOTHING` because `obs_node`
        # carries `ix_obsnode_pk` UNIQUE on `(core_id, local_id)` … the level loop is
        # RESUMABLE, so re-running a level that partly landed must not double its rows"* — a
        # correct statement of intent, describing a clause that was never emitted. MEASURED:
        # `--promote-core` on an already-packed core raised
        # `UniqueViolation: ix_obsnode_pk (core_id, local_id)=(LRRu2kXZAsU, 1951)`.
        #
        # ⚑⚑ AND ITS ABSENCE IS WHY THE FOLD HELD ONE TRANSACTION FOR THE WHOLE CORE. Without
        # idempotence per level there is nothing safe to commit early, so every level's writes
        # stayed invisible until the caller committed ~70 levels later — a transaction whose
        # lock footprint grows monotonically across the fold. That is a BIG-LOCK paradigm
        # replacing the lockless one this arc is built on (operator, 2026-08-22), and it is how
        # two `make -j` workers reached a deadlock: the residue predicate makes a committed
        # PREFIX a readable, resumable state, and holding a transaction across it throws that
        # property away in exchange for an undo nobody needs.
        #
        # ⚑ `DO NOTHING`, NOT `DO UPDATE`. A row already present for `(core_id, local_id)` is
        # this same fold's output from an earlier attempt — the signature is content-derived,
        # so re-deriving it yields the same node. Overwriting would rewrite a row with its own
        # value and take a row lock to do it; skipping is both correct and lock-free.
        .on_conflict_do_nothing(index_elements=["core_id", "local_id"])
        .returning(obs_node.c.node_id)
        .cte("w")
    )
    return select(
        func.count().label("n"),
        func.count(distinct(ins.c.node_id)).label("ids"),
        func.coalesce(func.max(cast(ins.c.node_id, Integer)), literal(0)).label("top"),
    ).select_from(ins)


def q_pack_discrimination(
    _materialised=False,
):  # ⟡sql-lift: can this level's data FALSIFY a key omission?
    """`(n, ctors, qnames, idxs, lits, kid_shapes)` for the observations at `:ht` in `:core_id`.

    ⚑⚑⚑ AN EQUIVALENCE VERDICT IS ONLY AS STRONG AS THE POPULATION'S ABILITY TO DISAGREE, and
    this is that ability, measured per component. The fold groups WITHIN a height, so a
    signature component taking ONE value at that height cannot separate any two nodes there —
    omitting it from the key would change nothing, and `--equiv pack.sql pack.python` would
    report IDENTICAL over a key that is missing a field.

    ⚑⚑ THAT IS NOT HYPOTHETICAL. A first cut of `q_pack_level` dropped `idx` — the de Bruijn
    role (`sppf_db.py:754`: `role = "db%d" % idx`), so two `Var` nodes at different indices are
    DIFFERENT terms — and passed **three** IDENTICAL verdicts across two cores and three heights
    before a column census surfaced it. The gate was green and the key was wrong.

    ⚑ SO A LOW COUNT HERE IS A FACT ABOUT THE TEST, NEVER ABOUT THE FOLD. `ctors = 1` at a level
    means "this level cannot falsify a missing `ctor_id`", not "`ctor_id` is unnecessary". The
    distinction is the same one `do_equiv`'s both-empty refusal makes (*"⚠ UNMEASURED"*), one
    component finer.

    ⚑ `kid_shapes` COUNTS DISTINCT CHILD ARRAYS, which is what makes the child component's
    discriminating power visible: at height 0 every node is a leaf and every array is empty, so
    `kid_shapes = 1` and a level-0 verdict says NOTHING about whether children belong in the key.
    """
    _core = bindparam("core_id", value="", type_=String)
    _ht = bindparam("ht", value=0, type_=Integer)
    kids = (
        select(
            edge.c.core_id.label("core_id"),
            edge.c.plid.label("plid"),
            func.array_agg(aggregate_order_by(obs_node.c.node_id, edge.c.ord)).label("kids"),
        )
        .select_from(
            edge.join(
                obs_node,
                and_(obs_node.c.core_id == edge.c.core_id, obs_node.c.local_id == edge.c.clid),
            )
        )
        .where(edge.c.core_id == _core)
        .group_by(edge.c.core_id, edge.c.plid)
        .subquery("k")
    )
    # ⚑ THE HEIGHT SOURCE IS THE ONLY STAGE THAT VARIES between this builder and its materialised
    # twin — `kids`, `sig`, `newsig` and the join back are identical either way. That is why the
    # twin is a one-line caller rather than a copy: the fold is decomposed at the seam where the
    # variation actually is, so there is exactly one body to keep correct.
    ht = _height_src(_materialised)
    at = (
        select(
            event.c.ctor_id,
            event.c.qname_pid,
            event.c.idx,
            event.c.lit_id,
            func.coalesce(kids.c.kids, literal_column("'{}'::text[]")).label("kids"),
        )
        .select_from(
            ht.join(obs, and_(obs.c.core_id == ht.c.core_id, obs.c.local_id == ht.c.local_id))
            .join(event, event.c.ekey == obs.c.ekey)
            .outerjoin(kids, and_(kids.c.core_id == ht.c.core_id, kids.c.plid == ht.c.local_id))
        )
        .where(ht.c.ht == _ht)
        .subquery("a")
    )
    return select(
        func.count().label("n"),
        func.count(distinct(at.c.ctor_id)).label("ctors"),
        func.count(distinct(at.c.qname_pid)).label("qnames"),
        func.count(distinct(at.c.idx)).label("idxs"),
        func.count(distinct(at.c.lit_id)).label("lits"),
        func.count(distinct(at.c.kids)).label("kid_shapes"),
    ).select_from(at)


def q_pack_partition():  # ⟡sql-lift: the SQL fold's partition, as CANONICAL CLASSES
    """`(members)` — one row per equivalence class of the SQL packing, keyed by its MEMBER SET.

    ⚑⚑⚑ THE COMPARISON MUST QUOTIENT OUT THE NUMBERING, because the id is a SURROGATE OVER THE
    SIGNATURE, NOT AN ENCODING OF IT (`sppf_db.py:833-838`). The python assigns ids in
    `sorted(obs)` order; `dense_rank()` assigns in signature order. Both are correct and they
    disagree on every id. Comparing `(core_id, local_id, node_id)` triples as sets — which is
    what `--equiv` does by default — would report a TOTAL mismatch for two identical foldings.

    ⚑⚑ SO THE INVARIANT IS THE PARTITION: two foldings agree iff they induce the same grouping
    of observations, regardless of what the groups are CALLED. Emitting each class as its sorted
    member list makes that a plain set comparison — `--equiv` then works unmodified, and the
    existing both-empty refusal (`do_equiv`, *"⚠ UNMEASURED"*) comes along for free, which is
    exactly the trap `reflects_obs` records (an empty core reporting *"REFLECTS — 0 row(s)
    reconstructed exactly"*).

    ⚑ THE MEMBER LIST IS `local_id`s WITHIN ONE CORE, so it is bounded by the core and not by the
    corpus — this is a comparison key, not a node key, and §ⓧ.wall's objection to subtree-sized
    keys does not reach it (`sppf_tree.py:1306` draws the same distinction for its PARTITION BY).
    """
    # ⚑⚑ THE GATE'S OWN ARM STAYS ON THE CTE, deliberately — the same reason `q_pack_partition_python`
    # does. `--equiv` compares the two folds; if this arm read `_ht_map` it would depend on the
    # materialisation being correct, and a defect there would move the SQL side while the python
    # side derived independently — a REAL difference the gate would report, or worse, a shared
    # defect it could not see. The optimisation is verified BY this comparison, so it must not be
    # inside it.
    p = q_pack_level().subquery("p")
    return select(
        func.array_agg(aggregate_order_by(p.c.local_id, p.c.local_id)).label("members")
    ).group_by(p.c.node_id)


def q_pack_partition_python():  # ⟡sql-lift: the SAME quotient, over the PYTHON fold's output
    """`(members)` — one row per equivalence class of `obs_node`, keyed by its MEMBER SET.

    ⚑ THE REFERENCE ARM. `obs_node` holds the python fold's `(core_id, local_id) → node_id`, so
    quotienting it the same way yields classes comparable with `q_pack_partition`'s. Scoped to
    ONE core and ONE height so the two arms cover the same population — comparing a level against
    a whole core would report every unmatched level as a difference.
    """
    _core = bindparam("core_id", value="", type_=String)
    _ht = bindparam("ht", value=0, type_=Integer)
    # ⚑⚑ THE REFERENCE ARM STAYS ON THE CTE, DELIBERATELY, and this is the one consumer that must
    # NOT take the materialised source. `--equiv pack.sql pack.python` exists to check the SQL
    # fold against the python fold; if BOTH arms read the same temp map, a defect in the
    # materialisation would move both sides identically and the gate would certify it. An
    # independent derivation on the reference side is what keeps the comparison a comparison.
    ht = q_obs_height().subquery("m")
    scoped = (
        select(obs_node.c.local_id, obs_node.c.node_id)
        .select_from(
            obs_node.join(
                ht, and_(ht.c.core_id == obs_node.c.core_id, ht.c.local_id == obs_node.c.local_id)
            )
        )
        .where(and_(obs_node.c.core_id == _core, ht.c.ht == _ht))
        .subquery("q")
    )
    return select(
        func.array_agg(aggregate_order_by(scoped.c.local_id, scoped.c.local_id)).label("members")
    ).group_by(scoped.c.node_id)


def _WITHDRAWN_q_module_exports():
    """⟡oracle: (module, name, kind) — WHAT A MODULE ACTUALLY EXPORTS.

    ⚑⚑ WITHDRAWN, NOT SHIPPED — and the reason is a finding, not a retreat.
    These three builders were written in another session's file (this one is
    UNTRACKED — a peer's in-flight work), registered in `INTERN_BUILDERS`, and
    that registration alone turned `query_defs.py --check` RED, which is a
    BLOCKING pre-commit gate (`.githooks/pre-commit:100`).  Clearing it requires
    `--compile`, an operator-owned WRITE to `query_sql_postgres.py`.  So a
    capability with ZERO consumers had blocked the commit path of a tree already
    blocked on Agda.  Renamed rather than deleted so the measurements below are
    not lost; a future author should move them into a real arc with a consumer.

    ⚑ AND `--verify` WOULD NOT HAVE CAUGHT THE ABSENCE.  `verify()` iterates the
    `_reg` table, not `INTERN_BUILDERS`, so an unregistered builder is never
    selected and the summary prints `PASS — 0/0` on an empty selection.  A gate
    that passes because it measured nothing is the shape this repo censuses.

    ⚑⚑ THE ANSWER TO A QUESTION A SOURCE SCAN CANNOT ANSWER.  `agda_defs.def_index`
    is a COLUMN-0 text scan, so it under-reports provision in at least four ways —
    a name inside `mutual`/`abstract`, a record FIELD, a constructor, and anything
    a target re-exports.  Every one of those was measured as a FALSE `NONEXPORT`
    in `agda_defs --clause-audit`, i.e. a green module reported as a latent build
    failure: `GCD.TraceDivides` indexes as ZERO names (its two theorems are in a
    `mutual` block) while its consumer compiles clean; `Algebra.Wedge` indexes 21
    names, not including the field `C`, whose consumer also compiles clean.

    ⚑ AND THE FIX IS NOT A FIFTH SPECIAL CASE.  Patching per-symptom is how that
    census reached 185 rows and then 155 with no principled floor — each round
    discovering another shape the text scan cannot see.  `unit_obs` is the
    TYPECHECKED core's own unit table: constructors, fields, functions, mutual
    contents, all present because agda put them there.  Reading it replaces the
    guess with the fact.

    `unit_obs.name_pid` is a PATH (the qualified name) and `module_pid` its owning
    module, both resolved through `path_text`; `kind_id` through `terms`
    (Function / Constructor / …).  `unit_id` also carries the qualified name but
    NUL-JOINED with `root_lid` — do not read it as text, which is the trap that
    made a hand-probe fail with `invalid byte sequence`/`null character not
    permitted`; the pid joins are the supported route.

    ⚑ ABSENCE OF ROWS IS NOT ABSENCE OF NAMES.  The ingest is PARTIAL (measured
    1,965 of 2,322 cores, 85%) and `schema.py --holes` names 3 modules that define
    names and have no rows — `Foundation/Fin/Literals` (33 names) is one, and it
    is the direct source of the `₀₁`/`₀₂`/`₁`/`₇` false positives in the current
    census.  A consumer of this builder MUST treat "module not present" as UNKNOWN
    and never as "exports nothing", which is the same discipline `--provides`
    learned the hard way when a confident `0 name(s)` made a peer retract a
    correct reading.
    """
    pm = _a(path_text, "pm")
    pn = _a(path_text, "pn")
    k = _a(terms, "k")
    return select(
        pm.c.text.label("module"), pn.c.text.label("name"), k.c.text.label("kind")
    ).select_from(
        unit_obs.join(pm, pm.c.path_id == unit_obs.c.module_pid)
        .join(pn, pn.c.path_id == unit_obs.c.name_pid)
        .join(k, k.c.term_id == unit_obs.c.kind_id)
    )


def _WITHDRAWN_q_module_export_names():
    """⟡oracle: the names ONE module exports — the bound form `provides()` wants.

    Separate from `q_module_exports` because the unscoped form is a whole-corpus
    read and a clause audit asks per TARGET; binding the module is what keeps the
    per-target lookup from scanning the corpus once per import statement.
    """
    pm = _a(path_text, "pm")
    pn = _a(path_text, "pn")
    return (
        select(pn.c.text.label("name"))
        .select_from(
            unit_obs.join(pm, pm.c.path_id == unit_obs.c.module_pid).join(
                pn, pn.c.path_id == unit_obs.c.name_pid
            )
        )
        .where(pm.c.text == bindparam("module", value="", type_=String))
    )


def _WITHDRAWN_q_module_export_modules():
    """⟡oracle: every module the store HAS rows for — the UNKNOWN discriminator.

    ⚑ THIS IS THE HALF THAT KEEPS THE ORACLE HONEST.  Without it a consumer cannot
    tell "this module exports nothing" from "this module was never ingested", and
    conflating those is exactly the defect the oracle exists to remove — it would
    trade four text-scan blind spots for one ingest-coverage blind spot and report
    it with the same confidence.
    """
    pm = _a(path_text, "pm")
    return (
        select(pm.c.text.label("module"))
        .distinct()
        .select_from(unit_obs.join(pm, pm.c.path_id == unit_obs.c.module_pid))
    )


def q_set1_count():  # ⟡gqs-S0.2: the Set₁ census as a COLUMN READ (was set1_ratchet's 94s decode)
    return select(func.count()).select_from(unit_obs).where(unit_obs.c.level >= 1)


def q_level_populated():  # ⟡gqs-ratchet-query guard (1): is unit_obs.level emitted at all?
    return select(func.count()).select_from(unit_obs).where(unit_obs.c.level.isnot(None))


def q_argperm_uid():  # sppf_db project_argperm preload L420-421
    return (
        select(_unit.c.unit_id, path_text.c.text)
        .select_from(_unit.join(path_text, path_text.c.path_id == _unit.c.name_pid))
        .where(_unit.c.copy == "0")
    )


def q_deserialize_oppath():  # reuse_catalog deserialize_from_projection L315-317
    p2 = path_text.alias("p2")
    return (
        select(unit_node.c.unit_id, p2.c.text)
        .select_from(
            unit_node.join(_node, _node.c.node_id == unit_node.c.node_id).join(
                p2, p2.c.path_id == _node.c.op_path_id
            )
        )
        .where(_node.c.op_path_id.isnot(None))
    )


def q_reuse_rows(
    has_copy, limit=None
):  # sppf_query reuse_rows L86-96 (DYNAMIC → conditional builder)
    pt = path_text.alias("pt")
    o = terms.alias("o")
    r = terms.alias("r")
    u = unit_v.alias("u")  # the `unit` VIEW
    nd = _node.alias("nd")
    un = unit_node.alias("un")
    head = func.coalesce(func.nullif(pt.c.text, ""), o.c.text, r.c.text, "?").label("head")
    units = func.count(func.distinct(un.c.unit_id)).label("units")
    copies = (func.sum(func.coalesce(u.c.copy, 0)) if has_copy else literal_column("NULL")).label(
        "copies"
    )
    stmt = (
        select(un.c.node_id.label("node_id"), head, units, copies)
        .select_from(
            un.join(nd, nd.c.node_id == un.c.node_id)
            .join(u, u.c.unit_id == un.c.unit_id)
            .outerjoin(pt, pt.c.path_id == nd.c.op_path_id)
            .outerjoin(o, o.c.term_id == nd.c.op_term_id)
            .outerjoin(r, r.c.term_id == nd.c.role_id)
        )
        .where(nd.c.node_id.in_(select(node_child.c.node_id)))
        .group_by(un.c.node_id)
        .having(units >= bindparam("min_units"))
        .order_by(units.desc())
    )
    if limit is not None:
        stmt = stmt.limit(limit)  # int OR a bindparam (the two static variants below)
    return stmt


# ⟡q-reuse-rows-copy / ⟡q-reuse-rows-nocopy — the DYNAMIC sppf_query:71 `q_reuse_rows(has_copy(c), limit)`
# resolved into two STATIC named builders (the runtime picks by name, no SQLAlchemy). `limit` is a bindparam:
# pass lim=-1 for "no limit" (SQLite LIMIT -1 = unbounded ≡ the original no-LIMIT clause). VERIFIED: q_fanin
# already binds `LIMIT :lim` under sqlite3, so a parameterized LIMIT is safe.
def q_reuse_rows_copy():
    return q_reuse_rows(True, bindparam("lim"))


def q_reuse_rows_nocopy():
    return q_reuse_rows(False, bindparam("lim"))


# ════════════════════════════════════ M2 — VIEW models (interned for breadth, NOT executed) ═══════
# The compat VIEWS carry most of the path_text.path_id breadth (each joins it, often ×2). Modelled by their
# FROM/JOIN structure — the join predicates ARE the breadth signal; the GROUP_CONCAT fp/unhold_fp projections
# (structs) are correlated subqueries over _members/_member_heads (NO path_text), so they are simplified to a
# projected literal here — faithful for the index-breadth purpose (they add no path_text.path_id join).
def _a(t, n):
    return t.alias(n)


def v_structs():  # reuse_catalog `structs` — path_text ×2 (qname_pid, module_pid)
    s = _structs
    pq = _a(path_text, "pq")
    pm = _a(path_text, "pm")
    n = _a(terms, "n")
    k = _a(terms, "k")
    d = _a(terms, "d")
    return select(pq.c.text, n.c.text, k.c.text, pm.c.text, d.c.text, literal("fp")).select_from(
        s.join(pq, pq.c.path_id == s.c.qname_pid)
        .join(n, n.c.term_id == s.c.name_id)
        .join(k, k.c.term_id == s.c.kind_id)
        .join(pm, pm.c.path_id == s.c.module_pid)
        .join(d, d.c.term_id == s.c.desc_id)
    )


def v_members():  # `members` — path_text ×1
    x = _members
    psq = _a(path_text, "psq")
    n = _a(terms, "n")
    return select(psq.c.text, n.c.text, x.c.ord).select_from(
        x.join(psq, psq.c.path_id == x.c.struct_qname_pid).join(n, n.c.term_id == x.c.name_id)
    )


def v_refs():  # `refs` — path_text ×2
    x = _refs
    psq = _a(path_text, "psq")
    pr = _a(path_text, "pr")
    return select(psq.c.text, pr.c.text).select_from(
        x.join(psq, psq.c.path_id == x.c.struct_qname_pid).join(
            pr, pr.c.path_id == x.c.ref_qname_pid
        )
    )


def v_edges():  # `edges` — path_text ×2
    x = _edges
    ps = _a(path_text, "ps")
    pd = _a(path_text, "pd")
    return select(ps.c.text, pd.c.text).select_from(
        x.join(ps, ps.c.path_id == x.c.src_pid).join(pd, pd.c.path_id == x.c.dst_pid)
    )


def v_module_edges():  # `module_edges` — path_text ×2
    x = _module_edges
    ps = _a(path_text, "ps")
    pd = _a(path_text, "pd")
    return select(ps.c.text, pd.c.text).select_from(
        x.join(ps, ps.c.path_id == x.c.src_pid).join(pd, pd.c.path_id == x.c.dst_pid)
    )


def v_modules():  # `modules` — path_text ×1
    x = _modules
    pm = _a(path_text, "pm")
    p = _a(terms, "p")
    return select(pm.c.text, p.c.text, x.c.is_index).select_from(
        x.join(pm, pm.c.path_id == x.c.module_pid).join(p, p.c.term_id == x.c.purpose_id)
    )


# ⚑ `v_orbit` REMOVED 2026-08-23 with the orbit tier — the decoded-view twin of `v_node`
# over `orbit_node`. Found only via its registry entry `"view.orbit"`: `--calls v_orbit`
# reports 0 syntactic calls, and the tool's own warning (*"reached as a VALUE… no syntactic
# call is not no caller"*) is what kept it from reading as already-dead.


# ════════════════════════════════════ R2 — sppf_db projection reads (LOAD-BEARING) ════════════════
def q_event_ctor():
    return select(event.c.ekey, terms.c.text).select_from(
        event.join(terms, terms.c.term_id == event.c.ctor_id)
    )  # L198-199


def q_event_ctor_core():
    """`q_event_ctor` scoped to ONE core — the semi-join twin, same argument as
    `q_event_head_core`: `event` is content-addressed and carries no `core_id`, so the scope
    comes through `obs`. `project_sppf` read this one whole too (`sppf_db.py:1025`)."""
    return (
        select(event.c.ekey, terms.c.text)
        .select_from(event.join(terms, terms.c.term_id == event.c.ctor_id))
        .where(
            event.c.ekey.in_(
                select(obs.c.ekey).where(
                    obs.c.core_id == bindparam("core_id", value="", type_=String)
                )
            )
        )
    )


def q_obs_all():
    return select(obs.c.core_id, obs.c.local_id, obs.c.ekey)  # L200 / L324


def q_edge_all():
    return select(edge.c.core_id, edge.c.plid, edge.c.ord, edge.c.clid)  # L202 / L326


# ⚑⚑⚑ THE PER-CORE TWINS, AND THEY EXIST BECAUSE THE VERIFICATION GATE HAD NO REFERENCE ARM.
# `--equiv pack.sql pack.python` compares the SQL fold against `obs_node` — the PYTHON fold's
# output — but `project_sppf` takes no core parameter (`--forwards project_sppf core_id`: 0 of 2
# call sites), so producing a reference for ONE core meant folding all 152 and 6,274,182
# observations. A verification step that can only be satisfied by performing the whole run it is
# meant to gate is not a gate.
#
# ⚑⚑ SEPARATE BUILDERS RATHER THAN A `core_id=None` PARAMETER ON THE EXISTING TWO. The unscoped
# forms are LOAD-BEARING (this section's header says so) and compile to a plan the corpus path
# depends on; adding an always-present `WHERE core_id = :core_id` that binds `''` by default
# would silently return nothing for every existing caller — the baked-default trap `do_equiv`'s
# both-empty refusal was written for. Two builders, two plans, neither able to impersonate the
# other.
def q_obs_core():
    """`(core_id, local_id, ekey)` for ONE core — `q_obs_all` scoped."""
    return select(obs.c.core_id, obs.c.local_id, obs.c.ekey).where(
        obs.c.core_id == bindparam("core_id", value="", type_=String)
    )


def q_edge_core():
    """`(core_id, plid, ord, clid)` for ONE core — `q_edge_all` scoped."""
    return select(edge.c.core_id, edge.c.plid, edge.c.ord, edge.c.clid).where(
        edge.c.core_id == bindparam("core_id", value="", type_=String)
    )


def q_count_shared():
    return select(func.count()).select_from(shared_subtree)  # project_sppf return


def q_max_node_len():
    return select(func.max(func.length(_node.c.node_id)))  # project_sppf return


def q_project_stats():
    """`project_sppf`'s four totals as ONE statement — one snapshot, one round trip.

    ⚑⚑ FOUR EXECUTIONS WERE FOUR SNAPSHOTS, AND THE TUPLE REPORTED A STORE STATE THAT NEVER
    EXISTED (user, 2026-08-12: *"No; don't do a live query while preparing a query…"*). The
    return read `scalar("… _node"), scalar("… _unit"), scalar("… shared_subtree"),
    scalar("MAX(LENGTH…)")` — `_node` counted at one moment, `_unit` at another, the shared
    count at a third. That is this arc's core defect at its smallest scale: the same shape as
    `pin_persistent → lwm() → floor → DELETE`, six world-states composed into one decision.
    One statement, one snapshot, nothing composed across reads.

    ⚑⚑ AND IT IS WHY `QB.run(con, "count_shared").fetchone()[0]` WAS NOT THE FIX, though it
    removed the view name. A view was a FROZEN COMPOSITION — opaque, self-contained, only
    selectable-from — and giving the fragment its own round trip PRESERVES exactly that
    property under a new spelling. The fragment's whole gain is that it can be pushed INSIDE a
    larger statement, so here it is: `shared_subtree` enters as a scalar subquery in the select
    list, beside the other three, not beside the statement.

    ⚑ NO FROM CLAUSE, DELIBERATELY. Four independent aggregates have no common grain, so a
    join would invent one; four scalar subqueries in the select list is the composition that
    says "these are four numbers about one instant" without asserting a relation between them.
    """
    return select(
        select(func.count()).select_from(_node).scalar_subquery().label("nodes"),
        select(func.count()).select_from(_unit).scalar_subquery().label("units"),
        select(func.count()).select_from(shared_subtree).scalar_subquery().label("shared"),
        select(func.max(func.length(_node.c.node_id))).scalar_subquery().label("widest"),
    )


# ════════════════════════════════════ S1 — sppf_db ORBIT/argperm stat reads (⟡rewire-orbit-stats) ═
# ⚑ `q_max_orbit_len` / `q_orbit_node_count` / `q_orbit_packings` / `q_orbit_merged` REMOVED
# 2026-08-23 with the orbit tier they read (superseded by the compound-identity framing). All
# four were `count(*)`/`max(length)` reads over relations that held 0 rows; their sole caller
# was `sppf_db.project_orbit_sppf`, removed in the same change.
# ⚑ `q_orbit_def_stats` STAYS — it reads `_orbit_def`, which is the ARGPERM tier. The shared
# word "orbit" is the only thing it has in common with the tier just removed.
def q_orbit_def_stats():
    return select(
        func.count(),
        func.count(func.distinct(_orbit_def.c.type_key)),
        func.count(func.distinct(_orbit_def.c.graded_key)),
    ).select_from(_orbit_def)  # __main__ argperm L467-468


# ════════════════════════════════ ⟡L7 — recursion→parallel: the reachability closure as a WITH RECURSIVE CTE ═
# The declarative form of the eager python reachability DFS (_support jea_pysim.py:80 / _subnodes jea_pyalg.py:656
# / the unit_node builder sppf_db.py:270-278): the transitive closure of node_child from a root. UNION (not
# UNION ALL) dedups → distinct closure, O(V+E), matching the python seen-set (byte-exact: 59794 vs 59794). This
# is the recursion→parallel grade-transition made concrete — a greatest-fp recursion lifted to a least-fixpoint
# saturation SQLite evaluates in one pass, no python materialization. ⟡graded-relational-carrier / sql_lift ⟡L6.
def q_reach():
    anchor = select(bindparam("root", type_=String).label("node_id")).cte("reach", recursive=True)
    step = select(node_child.c.child_id).select_from(
        node_child.join(anchor, node_child.c.node_id == anchor.c.node_id)
    )
    reach = anchor.union(step)  # UNION = distinct closure (dedup ⇒ terminates)
    return select(reach.c.node_id)


#: ⚑⚑⚑ THE HEIGHT SOURCE, AS ONE SEAM — the four builders that need per-observation height all
#: spelled `q_obs_height().subquery(...)`, so each independently re-derived the recursive CTE.
#: MEASURED 2026-08-17 (`--explain pack_level_summary`, the 6,210-row trial core): **847ms of a
#: 1,000ms level is the CTE**, producing 57,368 rows to answer about a level of 50, with
#: `Rows Removed by Filter: 6,160`. The packing itself is ~30ms. Paid 23 times for that core,
#: 70 for the tail, then ×152 in the corpus run.
#:
#: ⚑⚑ MATERIALISED WHEN A CALLER HAS PROVIDED IT, DERIVED OTHERWISE. `pack_core_sql` builds a
#: TEMP `_ht_map` once per core; a builder run outside that context (a probe, `--explain`, a
#: selftest) has no such table and must still work. So the source is a parameter with the CTE as
#: its default rather than a mode switch — no caller is required to know which it got, and the
#: statement is IDENTICAL in shape either way, which is what keeps ⑤a/⑤b's verdicts applicable.
#:
#: ⚑ THE TEMP TABLE IS NOT DECLARED IN THE SCHEMA and must not be: it is per-connection,
#: per-core, and lives for one fold. Declaring it would put a disposable in the tier model that
#: `--census` would then report as a relation the store "holds".
#:
#: ⚑⚑⚑ AND A TEMP TABLE MAY BE THE WRONG MECHANISM — operator, 2026-08-17: *"If you're doing
#: _materialized, that sounds like something that OUGHT to be an INDEX."* Recorded as an open
#: question rather than acted on mid-verification, with what is already established about it:
#:
#:   * a GENERATED column (`GENERATED ALWAYS AS … STORED`, indexable) CANNOT express this —
#:     postgres requires the expression be row-local and IMMUTABLE, and height is a whole-core
#:     reachability fold over `edge`. Not a limitation to work around; a category difference.
#:   * a MATERIALIZED VIEW can: it is a real relation, takes `CREATE INDEX` on `(core_id, ht)`,
#:     and is refreshed explicitly. That is strictly better for the corpus run, where a temp
#:     table is rebuilt PER CONNECTION and a matview would be built once for all 152 cores.
#:   * a MATVIEW'S REFRESH IS ALL-OR-NOTHING, which looked like the deciding cost — one
#:     corpus-wide rebuild per ingest against 152 per-core builds, decided by a ratio nobody had
#:     measured.
#:
#: ⚑⚑⚑ AND THAT FRAMING WAS WRONG, BECAUSE THE REFRESH CAN MEMOIZE — operator, 2026-08-17:
#: *"Can't the refresh leverage the existing data as a memoization basis?"* It can, and the basis
#: is ALREADY BUILT AND ALREADY LOAD-BEARING:
#:
#:   * height is a pure function of ONE core's `edge` rows — no cross-core term, by the same
#:     forest-of-trees property that makes the recursion terminate without a cycle guard.
#:   * `write_events` is INCREMENTAL BY DEFAULT: unchanged cores' rows are kept VERBATIM and only
#:     mtime-advanced cores are deleted-and-rewritten (`_delete_core_rows`, per-core, atomic).
#:   * `core_fp` records per-core `mtime` — the exact staleness key, already the authority the
#:     ingest uses to decide what to re-decode.
#:
#: So a PERSISTENT `obs_height` relation refreshed PER CORE ON INGEST is strictly better than
#: both: no rebuild for unchanged cores (the overwhelming majority — the ingest's whole win is
#: that skipping them is cheap), an index on `(core_id, ht)`, and the promote path reads rather
#: than derives. All-or-nothing was a property of the MATVIEW MECHANISM, not of the problem —
#: reaching for `REFRESH MATERIALIZED VIEW` imported a constraint the data does not have.
#:
#: ⚑ THE TEMP TABLE IS STILL RIGHT FOR *THIS* STEP — ⑤a/⑤b verify a per-core fold and a per-core
#: disposable matches that unit exactly. What changed is that the ⑤c design is now decided rather
#: than open: a declared tier written by the ingest, keyed and indexed per core, not a matview.
_HT_MAP = "_ht_map"
#: The per-LEVEL signature table. Same seam as `_ht_map`, one stage later.
#:
#: ⚑⚑⚑ THE CTE `s` HAS NO STATISTICS, AND THAT — NOT THE SPILL — IS THE COST. MEASURED on
#: Cocycle height 0 (492,906 rows): the planner estimated **`rows=20`** for `s` and got 492,906, a
#: **24,000× underestimate**. It therefore sized the join back for 20 rows and pushed
#: **189,768,810 tuples** through the `IS NOT DISTINCT FROM` filter — ~28s of a 64.6s statement —
#: while the `HashAggregate` spilled 98,856kB across 33 batches. Raising `work_mem` would hide the
#: spill and leave the 190M-row filter untouched; it is also refused on this host (it multiplies
#: per-node-per-backend into a 0.93GiB floor).
#:
#: ⚑⚑ A CTE CANNOT BE ANALYZED; A TABLE CAN. `s` feeds BOTH the `GROUP BY` that mints ids and the
#: join that maps observations back to them, so its cardinality is the one number the whole plan
#: turns on — and postgres has to guess it. Materialising the level, then `ANALYZE`, replaces the
#: guess with a count. This is the operator's matview instinct (2026-08-17) applied one stage
#: further in than `_ht_map`: I fixed the height source and left the signature source guessing.
_SIG_TBL = "_sig_lvl"
#: The temp map's shape, as a Table so builders join it exactly as they join the CTE. Declared
#: against a PRIVATE MetaData: the shared one is the schema authority and `--census`/`--ddl` read
#: it, so registering a per-connection disposable there would make it look like a declared tier.
_ht_map_t = Table(
    _HT_MAP,
    MetaData(),
    Column("core_id", String),
    Column("local_id", Integer),
    Column("ht", Integer),
)
#: `s`'s shape as a Table, for the same reason `_ht_map_t` is one: the columns are typed objects
#: the join back references identically whether they came from a CTE or a materialised level.
_sig_t = Table(
    _SIG_TBL,
    MetaData(),
    Column("core_id", String),
    Column("local_id", Integer),
    Column("ctor_id", String),
    Column("qname_pid", String),
    Column("idx", Integer),
    Column("lit_id", String),
    Column("kids", ARRAY(String)),
)


def _height_src(materialised=False):
    """The `(core_id, local_id, ht)` source a level builder reads — CTE, or the temp map.

    ⚑⚑ `_`-PREFIXED, NOT `q_`, AND A GATE CAUGHT THE MISNAMING. `pipeflow`'s selftest asserts that
    every `q_`-named function reading a relation is REGISTERED in one of the two builder
    registries, and this one failed it — correctly. It is not a builder: it returns a SUBQUERY
    that builders embed, it takes no bindparams of its own, and registering it would put a
    fragment in a registry whose entries are all runnable statements. The `q_` prefix is a claim
    about what a function IS in this module, and I made that claim wrongly.

    ⚑ ONE SEAM, FOUR CONSUMERS. `q_pack_level`, `q_obs_heights_distinct`, `q_pack_discrimination`
    and `q_pack_partition_python` all need this; four independent `q_obs_height().subquery()`
    calls is the shape that made the per-level re-derivation invisible in the first place.

    ⚑⚑ A PARAMETER, NOT A MODE — AND THE NAMED VARIANTS ARE SEPARATE REGISTRY ENTRIES. The
    compiled cache keys on NAME (`SQL[name]` → one text, one default set), so a builder cannot
    carry two compiled forms under one key. `q_pack_level_mat` and its siblings are therefore
    their own entries that call this with `materialised=True`; this function is what keeps their
    BODIES from being a second spelling of the fold rather than the same fold over a different
    source.
    """
    # ⚑ A REAL `Table`, NOT `text("_ht_map")` — so the columns are typed objects the rest of the
    # builder joins against exactly as it joins the CTE's, and the two spellings stay
    # interchangeable at every call site. A raw-text source would force each consumer to know
    # which shape it received, which is the branch this seam exists to remove.
    if materialised:
        return _ht_map_t.select().subquery("m")
    return q_obs_height().subquery("m")


def q_ht_seed():  # ⟡converge-not-recurse: pass 0 — the leaves
    """`(core_id, local_id, ht)` for every LEAF of `:core_id` — height 0, no recursion.

    ⚑⚑⚑ ⟡converge-not-recurse — THE FIRST OF TWO PASSES THAT REPLACE A RECURSIVE TERM (operator,
    2026-08-22: *"Do we even need the CTE recursion at this point? Because we can do things in
    multiple passes and converge, rather than recurse (which forces a single pass)."*).

    ⚑⚑ THE RECURSION'S RESIDUAL COST IS AMPLIFICATION, AND `max_parents=1` DOES NOT PREVENT IT.
    `q_obs_height` emits **490,023 rows for 313,830 observations** (1.56×) on `wpk3blnvCNA`, and
    the outer `max(ht)` collapsing them is what spills: `HashAggregate  Batches: 5  Disk Usage:
    15200kB  Rows Removed by Filter: 137012`. The docstring there leans on `max_parents = 1`
    (re-verified 2026-08-22 over **138,351,403 edges**) to argue the walk is well-behaved — but
    that bounds parents PER CHILD. A parent whose children sit at heights 0 and 3 is emitted at
    ht 1 AND ht 4, because the recursive term propagates from each child INDEPENDENTLY. So the
    `max` is genuinely required by that formulation, and the 1.56× is structural to it.
    ⚑ Distinct from the earlier `UNION ALL`→`UNION` fix (7× fewer rows): that removed duplicate
    PATHS. This is a different residue underneath it.

    ⚑ A CONVERGING PASS HAS NEITHER. A node's height is computed ONCE, when all its children are
    known — no duplicate emission, no outer aggregate, no spill — and each pass commits, which
    is the lockless property the recursive single-pass form cannot offer.
    """
    _core = bindparam("core_id", value="", type_=String)
    return select(obs.c.core_id, obs.c.local_id, literal(0).label("ht")).where(
        and_(
            obs.c.core_id == _core,
            ~exists(
                select(literal(1)).where(
                    and_(edge.c.core_id == obs.c.core_id, edge.c.plid == obs.c.local_id)
                )
            ),
        )
    )


def q_ht_step():  # ⟡converge-not-recurse: one pass — parents now ready
    """`(core_id, local_id, ht)` for parents whose children are ALL in `_ht_map` — one round.

    ⚑⚑⚑ READINESS IS AN ANTI-JOIN, WHICH IS WHY THIS CONVERGES WITHOUT AN OUTER `max`. A parent
    is emitted only when NO child of it is missing from the map, so it is emitted EXACTLY ONCE
    and its `ht` is final on arrival: `1 + max(child ht)` over children that are all present.
    The recursive term cannot express this — it must fire on each child as that child arrives,
    which is precisely where the 1.56× amplification comes from.

    ⚑⚑ THE `max` HERE IS NOT THE `max` THAT WAS REMOVED. This one aggregates a parent's OWN
    CHILDREN inside the round (a handful of rows, by `--arity`), and it is the definition of
    height. The one retired aggregated *duplicate emissions of the same node across passes* —
    490,023 rows down to 313,830 — and existed only to undo the recursion's over-emission.

    ⚑ SHAPED ON `sppf_tree.run_rounds`, WHOSE LESSONS ARE PAID FOR AND NOT RE-LEARNED HERE: the
    schedule is READ from the work list rather than counted to a maximum (*"`range(0, max+1)`
    would issue up to 576,350 statements where ~115,300 rounds exist"*), each statement COMMITS
    (*"load-bearing rather than tidy: the next statement resolves its children by an ordinary PK
    lookup against a FRESH snapshot"*), and the scope is per-core (the whole-corpus form measured
    *"15+ minutes for a single round with no partial result and nothing to resume from"*).

    ⚑ SCOPED ON BOTH SIDES, for the reason `q_obs_height` records for its own step: bounding only
    one side lets the planner size the join against all 138M `edge` rows, because it cannot know
    the map holds one core.
    """
    _core = bindparam("core_id", value="", type_=String)
    m, mp = _ht_map_t.alias("m"), _ht_map_t.alias("mp")
    e2, m2 = edge.alias("e2"), _ht_map_t.alias("m2")
    # ⚑ CORRELATED VIA ALIASES, NOT `text()`. A raw-SQL correlation would sit outside the
    # compiler's view — the same "raw sql wearing a builder's clothes" the `ref_insert` note
    # records, where the text escapes `--check`'s drift gate and `--verify`.
    #
    # a child of THIS parent that is not yet in the map — one such child means not ready
    unready = exists(
        select(literal(1))
        .select_from(e2)
        .where(
            and_(
                e2.c.core_id == edge.c.core_id,
                e2.c.plid == edge.c.plid,
                ~exists(
                    select(literal(1))
                    .select_from(m2)
                    .where(and_(m2.c.core_id == e2.c.core_id, m2.c.local_id == e2.c.clid))
                ),
            )
        )
    )
    # already placed — a pass must not re-emit what an earlier pass settled
    placed = exists(
        select(literal(1))
        .select_from(mp)
        .where(and_(mp.c.core_id == edge.c.core_id, mp.c.local_id == edge.c.plid))
    )
    return (
        select(
            edge.c.core_id,
            edge.c.plid.label("local_id"),
            (literal(1) + func.max(m.c.ht)).label("ht"),
        )
        .select_from(edge.join(m, and_(m.c.core_id == edge.c.core_id, m.c.local_id == edge.c.clid)))
        .where(and_(edge.c.core_id == _core, ~placed, ~unready))
        .group_by(edge.c.core_id, edge.c.plid)
    )


def q_obs_height():  # ⟡sql-lift: the LEVEL SCHEDULE for project_sppf's packing fold
    """`(core_id, local_id, ht)` — height above the leaves, per observation.

    ⚑⚑⚑ THIS IS THE HALF THAT MAKES THE PACKING FOLD STAGEABLE, and it exists because the fold
    is **NOT** expressible as one `WITH RECURSIVE`. Postgres restricts a recursive TERM to a
    single non-aggregated reference to the working table: no `GROUP BY`, no `DISTINCT`, no
    aggregates, no window functions. `project_sppf`'s fold needs all three at once —
    `array_agg(child ORDER BY ord)` to build a signature, `GROUP BY signature` to dedup, and a
    dense counter to mint ids. So the audit's `WITH RECURSIVE + SUM` verdict for `project_sppf`
    is wrong on the mechanism, not merely unproven.

    ⚑⚑ WHAT IS RECURSIVE HERE IS ONLY THE **SCHEDULE**. Height is a pure reachability fold with a
    `max` at the end — legal, because the aggregate sits in the OUTER query over the CTE's output
    rather than inside the recursive term. Once every observation carries `ht`, the fold runs as
    one set-based statement PER LEVEL, and levels are disjoint so nothing within a level depends
    on anything else in it. That is the whole staging argument.

    ⚑ THE ROUND COUNT IS SMALL AND FRONT-LOADED (measured, sandbox tenant: 184,232 edges):
    max height 48, but **56% of observations are leaves (ht=0)** and 96% sit at ht ≤ 5; levels
    6–48 together touch under 4%. Round 0 alone collapses 103,251 leaf observations into **267
    distinct signatures** — a 387:1 sharing collapse that one `GROUP BY` performs and the python
    loop currently does with 103,251 dict lookups.

    ⚑ NO CYCLE GUARD, AND THAT IS MEASURED not assumed: every `(core_id, clid)` has exactly ONE
    parent (`max_parents=1` over 184,232 child slots), so each core is a FOREST OF TREES. Height
    is well-defined and the recursion terminates without a depth cap or a visited set.
    """
    # ⚑⚑⚑ SCOPED TO ONE `core_id`, AND THAT IS A MEASURED REQUIREMENT — the unbounded form
    # DID NOT COMPLETE IN 300s on the SANDBOX (184,232 edges), let alone the 6.27M corpus.
    # `dec_tree.chain_sql` records the same finding for the same reason (`dec_tree.py:721-724`):
    # *"the scope is a concrete core_id … an unestimable disjunction over an unbound parameter
    # would make the planner assume the corpus"*. A bindparam the planner cannot estimate turns
    # every per-step join into a corpus-sized hash, so the recursion re-walks shared structure
    # instead of one tree.
    #
    # ⚑ The caller iterates cores — which is also what makes the level loop resumable, since each
    # core's heights are independent and a kill loses at most the core in flight.
    # ⚑ A REPRESENTATIVE DEFAULT, per `INTERN_BUILDERS`' own contract (*"parameterized ones
    # bound with a representative shape; the bound value is a bindparam node, structure-only"*).
    # Without one, `_compile_one` emits `None` for the param and `--explain` would plan the
    # query for a NULL core — a plan that is fast, empty, and tells you nothing about the real
    # shape. The value is overridden per call; it exists so the compiled artifact is runnable.
    _core = bindparam("core_id", value="", type_=String)
    leaf = (
        select(obs.c.core_id, obs.c.local_id, literal(0).label("ht"))
        .where(
            and_(
                obs.c.core_id == _core,
                ~exists(
                    select(literal(1)).where(
                        and_(edge.c.core_id == obs.c.core_id, edge.c.plid == obs.c.local_id)
                    )
                ),
            )
        )
        .cte("h", recursive=True)
    )
    # ⚑⚑⚑ `UNION`, NOT `UNION ALL` — AND THE COMMENT THAT STOOD HERE ARGUED THE OPPOSITE FROM A
    # COST CLAIM THAT MEASUREMENT FALSIFIES. It read: *"UNION would dedup rows that differ only by
    # a path already counted — harmless — but it also costs a sort per step on a relation where
    # the `max` is doing the deduplication anyway."* Every clause is true in isolation. The
    # conclusion is wrong on this data, because the rows it declines to dedup are carried forward
    # into EVERY subsequent pass.
    #
    # MEASURED (sandbox corpus, 124,772 obs / 124,751 edges, same plan shape both ways —
    # 49 passes, hash join per pass, `edge` hashed once):
    #
    #     UNION ALL   1,482,584 rows emitted   28,832 rows/pass   1,285 ms
    #     UNION         210,400 rows emitted    4,279 rows/pass     270 ms
    #                   ── 7.0× fewer rows, 4.8× faster, IDENTICAL heights
    #
    # and per-core the blowup is worse: 7,013 nodes emitted 103,683 rows, **14.8×**.
    #
    # ⚑⚑ CORRECTNESS IS MEASURED, NOT ARGUED: both spellings' `max(ht)` compared over the whole
    # sandbox corpus — **124,772 compared, 0 differ**. The outer `max` still does the collapsing;
    # `UNION` only stops duplicate PATHS being dragged through the remaining passes.
    #
    # ⚑ THE FRAMING THAT FOUND IT (operator, 2026-08-17): *"what you're describing now is having
    # multiple passes of the flat fold … each pass does a further partial sort."* That is exactly
    # what a recursive term IS on this shape — a flat hash-join pass, iterated — and once it is
    # read that way the question stops being "how deep does it recurse" and becomes "how many rows
    # does each pass carry". The recursion was never the cost; the duplicate paths were.
    # ⚑ THE STEP CARRIES THE SCOPE TOO. Bounding only the anchor still lets the recursive term
    # plan against all 6.27M `edge` rows — the join predicate `edge.core_id = h.core_id` is
    # correct but the planner cannot know `h` holds one core, so it sizes the scan for the
    # corpus. Restating `core_id = :core_id` here is redundant SEMANTICALLY and load-bearing
    # for the PLAN, which is the same reason `ed.c.ord == literal("1")` is spelled as a literal
    # elsewhere in this file rather than left to a bindparam.
    step = (
        select(edge.c.core_id, edge.c.plid, (leaf.c.ht + literal(1)).label("ht"))
        .select_from(
            edge.join(leaf, and_(edge.c.core_id == leaf.c.core_id, edge.c.clid == leaf.c.local_id))
        )
        .where(edge.c.core_id == _core)
    )
    h = leaf.union(step)
    # ⚑ THE AGGREGATE IS OUTSIDE THE CTE — that placement is the legality of the whole builder.
    return select(h.c.core_id, h.c.local_id, func.max(h.c.ht).label("ht")).group_by(
        h.c.core_id, h.c.local_id
    )


# ════════════════════════════════════ S2 — reuse_catalog render_* view reads (⟡rewire-catalog-render) ═
# positional reads (reuse_catalog has no row_factory); SELECT straight from the physical compat views.
def q_structs_index():
    return select(
        structs_v.c.name, structs_v.c.kind, structs_v.c.module, structs_v.c["desc"]
    )  # render_index L491


def q_structs_namemod():
    return select(structs_v.c.name, structs_v.c.module)  # render_index L494


def q_structs_fpnamemod():
    return select(structs_v.c.fp, structs_v.c.name, structs_v.c.module)  # render_index L497


def q_modules_index():
    return select(modules_v.c.module, modules_v.c.purpose).where(
        modules_v.c.is_index == 1
    )  # render_index L500


def q_structs_qnamekind():
    return select(structs_v.c.qname, structs_v.c.kind)  # render_graph L547 / render_usage L666


def q_edges_all():
    return select(edges_v.c.src, edges_v.c.dst)  # render_graph L548


def q_sitemap():  # render_sitemap L617-618
    return select(
        structs_v.c.qname,
        structs_v.c.module,
        structs_v.c.name,
        func.coalesce(indegree_v.c.deg, 0).label("indeg"),
    ).select_from(structs_v.outerjoin(indegree_v, indegree_v.c.qname == structs_v.c.qname))


def q_structs_count():
    return select(func.count()).select_from(structs_v)  # render_usage L640


def q_edges_dst_distinct():
    return select(edges_v.c.dst).distinct()  # render_usage L641


def q_edges_src_distinct():
    return select(edges_v.c.src).distinct()  # render_usage L642


def q_structs_qname():
    return select(structs_v.c.qname)  # render_usage L643


def q_indegree_top():
    return (
        select(indegree_v.c.qname, indegree_v.c.deg)
        .order_by(indegree_v.c.deg.desc(), indegree_v.c.qname)
        .limit(20)
    )  # render_usage L647 ORDERED


def q_modedges_all():
    return select(modedges_v.c.src, modedges_v.c.dst)  # render_import L682


# ════════════════════════════════════ R1 — reuse_catalog deserialize base reads (positional) ══════
def q_pathtext_all():
    return select(path_text.c.path_id, path_text.c.text)  # L303


def q_terms_all():
    return select(terms.c.term_id, terms.c.text)  # L304


def q_unit_fields():
    return select(
        _unit.c.unit_id, _unit.c.name_pid, _unit.c.kind_id, _unit.c.module_pid, _unit.c.root_lid
    )  # L305-307


def q_unit_cod():
    return select(
        _unit_cod.c.unit_id, _unit_cod.c.cod_ctor_id, _unit_cod.c.cod_qname_pid
    )  # L308-309


def q_unit_member():
    return select(
        unit_member.c.unit_id,
        unit_member.c.ord,
        unit_member.c.member_name_pid,  # L311-312 ORDERED
        unit_member.c.member_unit_id,
    ).order_by(unit_member.c.unit_id, unit_member.c.ord)


def q_meta_failed():
    return select(meta.c.value).where(meta.c.key == "failed")  # L485


# ════════════════════════════════════ R1 — sppf_query read SELECTs (labels matter: sqlite3.Row) ═══
def _head(nd):
    return func.coalesce(func.nullif(nd.c.op, ""), nd.c.role, nd.c.kind).label("head")


def q_uid():  # sppf_query _uid L27 (view `unit`)
    return select(unit_v.c.unit_id).where(
        or_(unit_v.c.name == bindparam("name"), unit_v.c.name.like(bindparam("likep")))
    )


def q_support_count():  # sppf_query L33 / L61
    return (
        select(func.count().label("k"))
        .select_from(unit_node)
        .where(unit_node.c.unit_id == bindparam("uid"))
    )


# ── ⟡set1-rewrite — the Set₁ censuses as STRUCTURAL READS over the node tier ──────────
#
# ⚑⚑ THESE REPLACE A COLUMN READ THAT THE MODEL LEFT BEHIND. `set1_ratchet_cores` counts
# `unit_obs.level >= 1`, a per-defmark field from when defmarks WERE the SPPF. MEASURED
# 2026-08-22: `_unit.level` takes exactly two values corpus-wide — 0 (11,219 rows) and NULL
# (942) — while the node tier holds 238 `Univ` nodes over a level-1 `Max`. A field with no
# variation is not evidence of no debt.
#
# ⚑ TWO CENSUSES BECAUSE SET₁ IS ONE DEBT AT TWO GRADES, BOTH TARGETING ZERO (operator:
# *"Why not both?"* / *"Both will eventually be paid down to 0"*). `set1-is-grade-collapse`
# names the axis: INHABITING Set₁ is the grade collapsed, MENTIONING it is one step away.
# Both go to zero, so neither needs a denominator — the same reasoning the gate's own
# EMPTY-baseline branch uses (*"zero Set₁ is zero over any denominator"*).
#
# ⚑ KEYED BY UNIT, NOT COUNTED. A key set routes through `ratchet.set_ratchet` and inherits
# the write guard, the EMPTY reading, auto-lower and RELOCATED; a scalar inherits none of
# them, which is why the current gate hand-rolls all four. And a key says WHICH definition.


def _level_ge1_max():
    """`Max` nodes carrying a level literal ≥ 1 — the universe-level marker, as a subquery.

    ⚑ THE SHAPE IS AGDA'S, NOT OURS. 2.7+ unified Type/Prop/SSet into
    `Univ :: Univ -> Level -> Sort'`, so a closed sort is `Univ _ (Max n [])` and the level
    is a LITERAL LEAF child of the `Max`. `agdai_shim.hs:levelOf` matches exactly that.
    ⚑ MATCHED ON THE `#Integer:` PREFIX, NOT ON A LIST OF LEVELS. Enumerating
    `('#Integer:1','#Integer:2',…)` would silently miss level 3 the day one appears — the
    frozen-roster defect this repo keeps paying down. `substr` + a numeric test is total.
    """
    mx = _node.alias("mx")
    tm = terms.alias("tm")
    lc = node_child.alias("lc")
    lv = _node.alias("lv")
    tl = terms.alias("tl")
    return (
        select(mx.c.node_id.label("max_id"))
        .select_from(
            mx.join(tm, tm.c.term_id == mx.c.op_term_id)
            .join(lc, lc.c.node_id == mx.c.node_id)
            .join(lv, lv.c.node_id == lc.c.child_id)
            .join(tl, tl.c.term_id == lv.c.op_term_id)
        )
        .where(
            and_(
                tm.c.text == "Max", tl.c.text.like("#Integer:%"), func.substr(tl.c.text, 10) != "0"
            )
        )
    )


def q_set1_inhabits():
    """Units whose definition's CODOMAIN sort is `Univ` at level ≥ 1 — Set₁ INHABITED.

    ⚑⚑⚑ THIS IS `agdai_shim.hs:codomainSort` AS A QUERY, and reproducing it exactly is the
    whole difficulty. The Haskell is three lines:

        codomainSort t = case unEl t of
          Pi _ b -> codomainSort (unAbs b)     -- peel the telescope
          Sort s -> s                          -- the codomain IS a universe: return s…
          _      -> getSort t                  -- …otherwise the type's own sort

    and its note says why the middle case exists: *"When the codomain is itself a universe
    (`Sort s`) the definition INHABITS s, not getSort s, which is one universe up. This
    off-by-one bites every parameterized definition (a record former's type is `… → Set1`,
    whose own sort is Set2)."*

    ⚑⚑ THE PATH THROUGH THE NODE TIER, MEASURED rather than assumed (live, 2026-08-22):
        `_unit.root_id` → a `Defn` node          (3,512 of the roots)
        `Defn` child[0] → `El`                    (4,118)
        `El`   child[0] → `Univ` (21,375) or `Pi` (3,175)
    `Type = El Sort Term`, so `El`'s ord-0 child is where the sort/telescope decision is made.

    ⚑ THE RECURSION PEELS `Pi` ONLY, and terminates because the peel strictly descends the
    interned DAG (child ids are always lower — ⟡locals-are-emission-order, and post-order is
    corpus-verified at 130,915,197/130,915,197). No visited set, no depth cap, for the same
    reason `q_obs_height` needs none.

    ⚑ `UNION`, NOT `UNION ALL` — `q_obs_height` measured 7.0× fewer rows and 4.8× faster on
    the same plan shape, with identical results, because duplicate PATHS otherwise ride through
    every remaining pass. A shared subterm reached twice is the common case in an SPPF.

    ⚑⚑ NOT SCOPED TO A CORE, AND THAT IS A RISK I AM NAMING RATHER THAN HIDING.
    `q_obs_height` is per-core because its unbounded form DID NOT COMPLETE IN 300s over
    184,232 edges. This walks `_node`/`node_child` — 443,169 nodes, ~1.73M child edges, three
    orders smaller than `edge` — and the anchor is bounded by `_unit` (~12k roots), so the
    working set starts small and shrinks. That is an argument, not a measurement: **run
    `--scans` before trusting it on a full store**, and if it does not complete, the fix is to
    scope by `file_id` the way the height fold scopes by `core_id`.
    """
    # ── anchor: each unit's `El` node, reached through its `Defn` root ─────────────────
    u = _unit.alias("u")
    dn = _node.alias("dn")
    td = terms.alias("td")
    dc = node_child.alias("dc")
    el = _node.alias("el")
    tel = terms.alias("tel")
    anchor = (
        select(u.c.unit_id.label("unit_id"), dc.c.child_id.label("cur"))
        .select_from(
            u.join(dn, dn.c.node_id == u.c.root_id)
            .join(td, and_(td.c.term_id == dn.c.op_term_id, td.c.text == "Defn"))
            .join(dc, and_(dc.c.node_id == dn.c.node_id, dc.c.ord == 0))
            .join(el, el.c.node_id == dc.c.child_id)
            .join(tel, and_(tel.c.term_id == el.c.op_term_id, tel.c.text == "El"))
        )
        .cte("cod", recursive=True)
    )
    # ── step: while the current node is a `Pi`, descend to its CODOMAIN ────────────────
    # ⚑ THE CODOMAIN IS THE LAST CHILD, NOT ORD 0. `Pi (Dom Type) (Abs Type)` — ord 0 is the
    # DOMAIN (the hypothesis, which is exactly what `mentions` counts and `inhabits` must
    # not). Taking ord 0 here would walk into the argument type and turn this census into a
    # slower spelling of `q_set1_mentions`, which is the specific way this query fails
    # silently rather than loudly.
    pi = _node.alias("pi")
    tp = terms.alias("tp")
    pc = node_child.alias("pc")
    inner = _node.alias("inner")
    ti = terms.alias("ti")
    ic = node_child.alias("ic")
    step = (
        select(anchor.c.unit_id, ic.c.child_id)
        .select_from(
            anchor.join(pi, pi.c.node_id == anchor.c.cur)
            .join(tp, and_(tp.c.term_id == pi.c.op_term_id, tp.c.text == "Pi"))
            .join(pc, and_(pc.c.node_id == pi.c.node_id, pc.c.ord == 1))
            .join(inner, inner.c.node_id == pc.c.child_id)
            .join(ti, ti.c.term_id == inner.c.op_term_id)
            # `Abs`/`NoAbs` wrap the codomain; unwrap to its ord-0 child.
            .join(ic, and_(ic.c.node_id == inner.c.node_id, ic.c.ord == 0))
        )
        .where(ti.c.text.in_(["Abs", "NoAbs"]))
    )
    cod = anchor.union(step)
    # ── read the level off whatever the peel bottomed out on, if it is a `Univ` ────────
    uv = _node.alias("uv2")
    tuv = terms.alias("tuv")
    uc = node_child.alias("uc2")
    m = _level_ge1_max().subquery("m2")
    return (
        select(cod.c.unit_id)
        .distinct()
        .select_from(
            cod.join(uv, uv.c.node_id == cod.c.cur)
            .join(tuv, and_(tuv.c.term_id == uv.c.op_term_id, tuv.c.text == "Univ"))
            .join(uc, uc.c.node_id == uv.c.node_id)
            .join(m, m.c.max_id == uc.c.child_id)
        )
    )


def q_set1_mentions():
    """Units whose SUPPORT contains a `Univ` at level ≥ 1 — Set₁ MENTIONED anywhere.

    ⚑ THE `Univ` PARENT IS REQUIRED. A bare level-1 `Max` also occurs under `Level`, `Plus`
    and inside `Abs`/`Dom` (measured: 238 of the parents are `Univ`, the rest are not sorts).
    Dropping the `Univ` join would count arithmetic on levels as a universe mention.

    ⚑ MEASURED ON LIVE 2026-08-22 (store at 89% ingest, so the figure MOVES — it is a shape
    check, not a baseline): **2,109 units**, against `set1_count`'s **0** over the same store.
    `--scans` reports ~963k rows read, index scans throughout, no spill.

    ⚑⚑ THE DISAGREEMENT IS THE POINT AND IT IS NOW SETTLEABLE. `set1_count` reads
    `unit_obs.level >= 1`; this reads the node tier. Both are registered, so
    `query_defs --equiv` can put them side by side instead of the question being argued. Do
    NOT retire `set1_count` before that comparison: a reference arm deleted is a comparison
    that can never be made, which is why the registration comment keeps it deliberately.

    ⚑ THE INHABITS TWIN IS **NOT WRITTEN**, and its absence is the honest state rather than an
    oversight. It needs the codomain restriction `agdai_shim.hs:codomainSort` implements —
    *peel the Π telescope, take the codomain, and when that is itself `Sort s` take s, not
    `getSort s`* (the shim's own note: the off-by-one "bites every parameterized definition,
    a record former's type is `… → Set₁` whose own sort is Set₂"). Reproducing a telescope
    peel over `Pi`/`Abs` chains in SQL is a recursive walk, not a join, and writing it wrong
    turns inhabits into mentions — collapsing the two censuses into one and losing exactly the
    grade distinction they exist to separate.
    """
    un = unit_node.alias("un")
    uv = _node.alias("uv")
    tu = terms.alias("tu")
    uc = node_child.alias("uc")
    m = _level_ge1_max().subquery("m")
    return (
        select(un.c.unit_id)
        .distinct()
        .select_from(
            un.join(uv, uv.c.node_id == un.c.node_id)
            .join(tu, tu.c.term_id == uv.c.op_term_id)
            .join(uc, uc.c.node_id == uv.c.node_id)
            .join(m, m.c.max_id == uc.c.child_id)
        )
        .where(tu.c.text == "Univ")
    )


def q_support_hist():  # sppf_query L35-37
    un = unit_node.alias("un")
    nd = node_v.alias("nd")
    h = _head(nd)
    k = func.count().label("k")
    return (
        select(h, k)
        .select_from(un.join(nd, nd.c.node_id == un.c.node_id))
        .where(un.c.unit_id == bindparam("uid"))
        .group_by(h)
        .order_by(k.desc())
        .limit(12)
    )


def q_fanin():  # sppf_query L42-44
    nf = node_fanin.alias("nf")
    nd = node_v.alias("nd")
    return (
        select(nf.c.node_id, _head(nd), nf.c.fanin)
        .select_from(nf.join(nd, nd.c.node_id == nf.c.node_id))
        .order_by(nf.c.fanin.desc())
        .limit(bindparam("lim"))
    )


def q_extract():  # sppf_query L50-54
    un = unit_node.alias("un")
    nd = node_v.alias("nd")
    units = func.count(func.distinct(un.c.unit_id)).label("units")
    return (
        select(un.c.node_id, _head(nd), units)
        .select_from(un.join(nd, nd.c.node_id == un.c.node_id))
        .where(un.c.node_id.in_(select(node_child.c.node_id)))
        .group_by(un.c.node_id)
        .having(units >= bindparam("m"))
        .order_by(units.desc())
        .limit(20)
    )


# ⚑⚑ THE TWO `scratch/` DEMAND READS — LIFTED OUT OF RAW SQL 2026-08-12 (⟡view-purge), AND
# THE CENSUS THAT FOUND THEM IS THE POINT. `query_defs --touching unit` reports these NOWHERE
# (it models declared builders, and these were hand-written strings); `pycodemod --relname
# unit` found both, in `scratch/`, which is exactly the population a builder-scoped census
# misses. They read the `unit` VIEW, so the purge would have taken the Agda ban-decompose loop
# offline at RUNTIME — `scope_fix` calls `demand_imports` to extrude a module's import block.
#
# ⚑ AND THAT IS THE SECOND TIME ONE OF THESE STRINGS TOOK THE AGDA WRITE PATH DOWN. The first
# was a hardcoded `?` (⓺, 2026-08-11): *"`ph()`'s OWN DOCSTRING PREDICTED THIS EXACT FAILURE
# AND THIS SITE NEVER CALLED IT."* Same shape, different token — a site outside the layer that
# owns the spelling cannot be reached by fixing the layer. Routing them through a BUILDER is
# the fix that generalises: paramstyle, cursor and relation all become the layer's problem.
#
# ⚑ ONE PREDICATE APART, SO TWO BUILDERS AND NOT A FLAG. `demand_refs` matches a unit name
# EXACTLY (`demand_imports.demand`, one definition); `module_refs` matches a module PREFIX
# (`scope_store._demand_of`, every definition under `mod.`). A single builder with a
# `use_like=` switch would put the two predicates one keyword apart in a licence that feeds an
# automated rewriter, which is the `sandbox=` shape `store.connect` refuses by name.
def _demand_refs(pred):
    un = unit_node.alias("un")
    n = _node.alias("n")
    p = path_text.alias("p")
    u = unit_v.alias("u")  # the `unit` FRAGMENT, composed in
    return (
        select(p.c.text.label("ref"))
        .distinct()
        .select_from(
            u.join(un, un.c.unit_id == u.c.unit_id)
            .join(n, n.c.node_id == un.c.node_id)
            .join(p, p.c.path_id == n.c.op_path_id)
        )
        .where(and_(pred(u), u.c.copy == 0, n.c.op_path_id.isnot(None)))
        .order_by(p.c.text)
    )


def q_demand_refs():
    return _demand_refs(lambda u: u.c.name == bindparam("name"))


def q_module_refs():
    return _demand_refs(lambda u: u.c.name.like(bindparam("likep")))


def q_clusters_overlap():  # sppf_query L63-68
    a = unit_node.alias("a")
    b = unit_node.alias("b")
    v = unit_v.alias("v")
    shared = func.count().label("shared")
    return (
        select(v.c.name, shared, bindparam("sz").label("sz"))
        .select_from(a.join(b, a.c.node_id == b.c.node_id).join(v, v.c.unit_id == b.c.unit_id))
        .where(and_(a.c.unit_id == bindparam("uid"), b.c.unit_id != bindparam("uid")))
        .group_by(b.c.unit_id)
        .having((1.0 * func.count() / bindparam("sz")) >= bindparam("thr"))
        .order_by(shared.desc())
        .limit(15)
    )


# ════════════════════════════════════ R1 — reuse_tui remaining read SELECTs ═══════════════════════
def q_node_child_edges():  # reuse_tui L87 — ORDER-SENSITIVE (builds ordered child lists)
    return select(node_child.c.node_id, node_child.c.child_id).order_by(
        node_child.c.node_id, node_child.c.ord
    )


def q_shared_subtree():  # reuse_tui L98-99 — value binds via run(..., min_fanin=…)
    return select(shared_subtree.c.node_id, shared_subtree.c.fanin).where(
        shared_subtree.c.fanin >= bindparam("min_fanin")
    )


def q_defcopy_units():  # reuse_tui L153-154
    return select(_unit.c.unit_id).where(_unit.c.copy == "1")


def q_unit_node_all():  # reuse_tui L156
    return select(unit_node.c.unit_id, unit_node.c.node_id)


def q_core_count():  # reuse_tui L173
    return select(func.count(func.distinct(_unit.c.file_id)))


# ════════════════════════════════ ⟡gqs-nolawsql-sppf — sppf_db build/ingest/finalize READS (no raw SQL) ═
# The core_fp fingerprint + sqlite_master existence/type probes I added in ⟡gqs-S1/make-targets, routed
# through the runtime. (WRITES — INSERT/DELETE/DROP/PRAGMA — stay raw: query_builders is SELECT-only.)
def q_core_fp_ids():
    return select(core_fp.c.core_id)  # finalize_db prune / verify D


def q_core_fp_mtimes():
    return select(core_fp.c.core_id, core_fp.c.mtime)  # write_events incremental


def q_core_fp_mtime():
    return select(core_fp.c.mtime).where(
        core_fp.c.core_id == bindparam("core_id")
    )  # ingest self-skip


# ⚑⚑ `q_table_exists` / `q_object_type` ARE DELETED (⓺, 2026-08-11) AND THEY WERE POISONING
# THE POSTGRES CACHE. Both selected `FROM sqlite_master`, so `query_sql_postgres.py` — the
# cache the live runtime loads — carried two statements naming a relation postgres does not
# have. A compiled cache is not typechecked against the store, so this sat green: the text
# was only ever wrong at EXECUTION, and nothing executed it.
#
# ⚑ NOTHING EXECUTED IT BECAUSE THEY WERE DEAD (`pycodemod --calls q_table_exists`: 1 def,
# 0 calls; the two `ref` rows are the registry dict and the `--verify` table). Their comment
# claimed the consumer — *"ingest_core: unit_obs present?"* — and `ingest_core` reads
# `"unit_obs" in _schema.relations(con)` instead, with its own note saying `was table_exists
# + .fetchone()`. The capability was replaced and the builder was left behind, which is the
# `rewire_only` class: the reason to trust a comment naming a caller is that a census agrees.
#
# ⚑ AND `relations()` IS THE REPLACEMENT, NOT A NEW ONE TO WRITE. It already normalises both
# catalogues to {name: 'table'|'view'} — which answers `object_type` too — and its docstring
# records consolidating FIVE `sqlite_master` spellings into it. These two were a sixth,
# reached through the builder layer instead of directly, which is why that sweep missed them.
