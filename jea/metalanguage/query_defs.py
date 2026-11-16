#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""query_defs.py — ⟡qinfra: the COMPILER. The SINGLE SOURCE for the project's SQL read-queries as named
SQLAlchemy-Core `select()` builders. This module imports SQLAlchemy (a ~0.4s cost); the CACHED RUNTIME is the
sibling `query_builders.py`, which imports NO SQLAlchemy and executes precompiled SQL from the generated
`query_sql.py` by NAME. So the hot paths (sppf_db `--ingest-core`, the pre-commit gates) `import query_builders`
and pay ~nothing; only this compiler + `query_registry.py` (which needs the builder OBJECTS to intern) touch
SQLAlchemy. The builder-NAME is its INTERN_BUILDERS key (`q_event_head` ↔ `"event_head"`).

  `python3 query_defs.py --compile`  → (re)generate query_sql.py (`SQL = {name: (sql, default_params)}`)
  `python3 query_defs.py --check`    → drift gate: recompile in-memory, diff vs the committed query_sql.py
  `python3 query_defs.py --verify`   → migration gate: each builder's rows == its ORIGINAL raw SQL over catalog.db

`--verify` is the migration GATE: every builder is paired with its ORIGINAL raw SQL; the harness runs BOTH
against catalog.db and asserts identical row sets. Nothing migrates without passing it.

Reflection-free lightweight Tables: a SELECT compiles correctly from `Column(String)` regardless of declared
type (we never write, only read/intern). Views are modelled as Tables of their OUTPUT columns.

⚑⚑ THE DECLARATION AND THE BUILDERS LIVE IN `query_decl.py` SINCE 2026-08-12, and what
remains here is the MEASUREMENT/CLI layer over them: `INTERN_BUILDERS`, `REFERENCE_ARMS`,
the `--compile`/`--check` cache gate, `--verify`'s raw-SQL registry, `--scans` / `--explain`
/ `--equiv`, `touching`, and `main`. The arrow points ONE way — tooling → builders, never
back — which is what let the cut need no shim, no cycle and no deferred import.

⚑ THE CLI IS THE HALF THAT STAYED BECAUSE THE SELF-INSPECTION IS HERE. `compile_text` bakes
this file's path into the generated `query_sql_postgres.py` header and `do_check` prints it
as the remedy; moving `--compile` to a sibling would have left both naming a file that no
longer has the mode, with `--check` still green. `query_decl.py`'s header carries the full
argument, including the one introspection that DID have to be repaired (`touching`).
"""

import os, sys, argparse, sqlite3

# ⚑⚑ THE RE-EXPORT IS THE CONTRACT, NOT TIDINESS. Five files reach names through this module
# (`pycodemod --importers query_defs`): `query_builders`'s `run`, `query_registry` / `sql_lift`
# `INTERN_BUILDERS`, `sql_lift.q_reach`, `numpy_builders`' `QB.q_reach` /
# `QB.q_edges_dst_distinct` / `QB.q_indegree_top`, and `sppf_db`'s `_qd.FREE_CTORS`. A split
# that dropped a builder off this surface would break them at THEIR next run, not at this one.
#
# ⚑⚑ AND THE UNDERSCORE NAMES ARE LISTED EXPLICITLY BECAUSE `import *` SKIPS THEM BY
# CONSTRUCTION. This exact defect shipped once in this tree: `schema._node`, `_unit`,
# `_unit_cod` and `_orbit_def` vanished off `schema`'s re-export surface while `--selftest`
# still read 123/123, because most cases never touch most names. The leading underscore on a
# TABLE here means "raw, pre-quotient" — the base relation under a compat VIEW of the same
# name — i.e. published vocabulary that merely LOOKS private to the star.
from query_decl import *  # noqa: F401,F403  (declaration + builders)

# ⚑ THE FRAGMENTS, BY NAME. `query_decl` binds them as `_node_sel` &c. and immediately
# `.subquery()`s them; `_samp` and the retired ⟡view-purge arms want the bare `select()`.
# ⚑ `node_atom_sel` / `orbit_sel` ARE IMPORTED WITH NO CONSUMER HERE, DELIBERATELY: they are
# the two fragments nothing reads, and naming them on this line is what keeps a `--dead`-style
# census able to see that rather than having to prove absence from silence.
from schema_decl import node_sel, unit_sel, node_fanin_sel, shared_subtree_sel, node_atom_sel  # noqa: F401  (orbit_sel removed with its tier)
from query_decl import (
    _MD,
    _T,
    _store,
    _a,
    _head,
    _node,
    _unit,
    _unit_cod,
    _orbit_def,
    _structs,
    _members,
    _member_heads,
    _refs,
    _edges,
    _module_edges,
    _modules,
    _live_cores,
    _rebuilt_obs,
    _rebuilt_edges,
    _rebuilt_edges_from_durable,
    _stored_edges,
)


# builders as nullary thunks for INTERNING by query_registry (parameterized ones bound with a
# representative shape; the bound value is a bindparam node, structure-only — breadth is unaffected).
INTERN_BUILDERS = {
    "node_head": q_node_head,
    "unit_names": q_unit_names,
    "event_head": q_event_head,
    "ref_rows": q_ref_rows,  # ⟡ref: the positional reference index
    # ⚑ THE WRITE HALF, AS BUILDERS. `project_ref` materialised `ref_rows` in python and pushed
    # it back a row at a time; these two make the projection server-side WITHOUT leaving the
    # compiled set — so the INSERT and DELETE are drift-gated and `--explain`-able like the
    # SELECT they were always paired with. DML compiles through `_compile_one` unchanged
    # (`stmt.compile(dialect=…)` is generic over Insert/Delete/Select).
    "ref_insert": q_ref_insert,  # ⟡sql-lift: INSERT … SELECT, no wire crossing
    "ref_clear_projected": q_ref_clear_projected,  # ⟡sql-lift: the additive DELETE, by core
    # ⚑ THE LEVEL SCHEDULE for project_sppf's packing fold. The fold is NOT one WITH RECURSIVE
    # (postgres bans GROUP BY / aggregates / window fns in a recursive term, and the fold needs
    # all three); only the SCHEDULE recurses, and its aggregate sits OUTSIDE the CTE.
    "obs_height": q_obs_height,  # ⟡sql-lift: height per obs → one stmt per level
    # ⚑⚑ ⟡converge-not-recurse — THE TWO-PASS TWIN of `obs_height`, and it is registered ALONGSIDE
    # rather than replacing it: `obs_height` stays the REFERENCE ARM so `--compare-paths` can diff
    # the two spellings per level. A replacement with no comparison arm is a rewrite whose
    # correctness rests on an argument, which is what this file's `--equiv` machinery exists to
    # refuse. `ht_seed` is pass 0 (the leaves); `ht_step` is one round (parents whose children are
    # ALL placed), iterated to fixpoint by the caller — no recursive term, and each pass commits.
    "ht_seed": q_ht_seed,  # ⟡converge-not-recurse: pass 0, the leaves
    "ht_step": q_ht_step,  # ⟡converge-not-recurse: one round to fixpoint
    # ⚑⚑ ⟡pack-slice-within-level — THE LEVEL SPLIT SO THE **WRITE** COMMITS IN WINDOWS. The
    # ranking must see the whole level (a `dense_rank()` over a slice mints different ids for the
    # same signature), so `lvl_assign` computes `(local_id → node_id)` for the level ONCE into a
    # temp table and `lvl_emit` copies `[lo,hi)` of it into `obs_node` per transaction. The
    # indivisible part stays one statement; the bulky part becomes N commits.
    "lvl_assign": q_lvl_assign,  # ⟡pack-slice: assign the whole level
    "lvl_emit": q_lvl_emit,  # ⟡pack-slice: one committable window
    # ⚑ ONE LEVEL OF THE FOLD. Signature = (ctor, qname, lit) + the children's ASSIGNED ids in
    # `ord` order; ids minted by `:base + dense_rank()` over the signature, which is `_next += 1`
    # expressed set-wise. Runs once per height, ascending, so every child is numbered first.
    "pack_level": q_pack_level,  # ⟡sql-lift: the packing fold, per height
    # ⚑ CAN THIS LEVEL'S DATA FALSIFY A KEY OMISSION? A component with one distinct value at a
    # height cannot separate anything there, so an IDENTICAL --equiv verdict over that level does
    # not establish the key needs it. Measured: dropping `idx` passed three such verdicts.
    "pack_discrimination": q_pack_discrimination,  # ⟡sql-lift: the verdict's own strength
    # ⚑ THE WRITE. INSERT…SELECT…RETURNING so one statement both lands the level and reports the
    # ids it minted — the caller advances `base` from RETURNING rather than re-running the level.
    "pack_level_insert": q_pack_level_insert,  # ⟡sql-lift: the fold's write, per height
    # ⚑ THE UNIT-MEMBERSHIP CLOSURE — over `edge` (pre-sharing local_ids) then mapped through
    # `obs_node`, NOT over `node_child` like `q_reach`. Same CTE shape, different carrier; using
    # q_reach here would widen every unit's membership through the sharing.
    "unit_members": q_unit_members,  # ⟡sql-lift: unit → member nodes
    # ⚑ THE BOUNDED FORMS. The level loop needs a SCHEDULE (~70 ints) and THREE NUMBERS per
    # level; it was pulling 943,927 height rows and up to 529,003 RETURNING rows to compute them.
    # Measured on the live tail core before anything wrote.
    "obs_heights_distinct": q_obs_heights_distinct,  # ⟡sql-lift: the schedule, ~70 rows
    # ⚑ THE PROMOTE'S RESIDUE, PER CORE — the same set `work_promote` tests for existence, grouped
    # and ordered largest-first. This is what turns converge's promote step from one 6.27M-row
    # batch into 152 bounded units.
    "unprojected_cores": q_unprojected_cores,  # ⟡sql-lift: which core to promote next
    # ⚑ THE COUNTER ALONE. `_seed_node_ids` builds a signature→id MAP the SQL fold never reads
    # (it re-derives sharing per level through obs_node); calling it per core would scan _node
    # and node_child 152 times to use one number from each pass.
    "node_id_top": q_node_id_top,  # ⟡sql-lift: seed the surrogate counter
    "pack_level_summary": q_pack_level_summary,  # ⟡sql-lift: (n, ids, top), read path
    "edge_disagreement": q_edge_disagreement,  # ⟡reflect: reflects_edge in one statement
    # ⚑ `"drainable": q_drainable` — DELETED 2026-08-12 with `obs.seq`. ONE licence remains and
    #   it keeps the `_res` name, because three production sites already read it
    #   (`schema_queue.reclaim`, `sppf_db.work_retire`, and `sppf_db`'s own guard case) and
    #   because the suffix names `Substrate.Lifecycle.Residue` — *"drawn but not yet fed"* —
    #   which is a live meaning, not a contrast with the deleted positional form.
    "drainable_res": q_drainable_res,  # ⟡tier-residue: the licence, NO position
    "obs_reconstructed": q_obs_reconstructed,  # ⟡tier-live ⓙ: THE LINK — durable side → obs
    "obs_node_all": q_obs_node_all,  # ⟡tier-live: the addressing map, whole
    "edge_durable_disagreement": q_edge_durable_disagreement,  # ⟡tier-live: may `edge` drain?
    # ⚑ ⟡dec-lift: the FIRST rung of the decode family to enter the compiled set. Flat by
    # choice — a plain scoped SELECT over the shadow, so the TRANSLATION is what gets verified
    # here rather than a CTE chain's semantics. `dec_drain.answer_sql` is its raw twin and
    # stays until `--verify` pairs them; the composed rungs are not registered yet.
    "dec_answer": q_dec_answer,  # ⟡dec-lift: a RETIRED document, read back
    "argperm_uid": q_argperm_uid,
    "deserialize_oppath": q_deserialize_oppath,
    "reuse_rows": lambda: q_reuse_rows(True),
    "reuse_rows_copy": q_reuse_rows_copy,
    "reuse_rows_nocopy": q_reuse_rows_nocopy,
    "node_child_edges": q_node_child_edges,
    "shared_subtree": q_shared_subtree,
    "defcopy_units": q_defcopy_units,
    "unit_node_all": q_unit_node_all,
    "core_count": q_core_count,
    # ⟡gqs-nolawsql-sppf — sppf_db build/ingest/finalize reads:
    "core_fp_ids": q_core_fp_ids,
    "core_fp_mtimes": q_core_fp_mtimes,
    "core_fp_mtime": q_core_fp_mtime,
    "uid": q_uid,
    "support_count": q_support_count,
    "support_hist": q_support_hist,
    "fanin": q_fanin,
    "extract": q_extract,
    "clusters_overlap": q_clusters_overlap,
    "pathtext_all": q_pathtext_all,
    "terms_all": q_terms_all,
    "unit_fields": q_unit_fields,
    "unit_cod": q_unit_cod,
    "unit_member": q_unit_member,
    "meta_failed": q_meta_failed,
    "event_ctor": q_event_ctor,
    "obs_all": q_obs_all,
    "edge_all": q_edge_all,
    # ⟡sql-lift: the PER-CORE twins — `project_sppf(core_id=…)`'s reads. Registered beside the
    # unscoped forms rather than replacing them: the corpus path still binds nothing.
    "obs_core": q_obs_core,
    "edge_core": q_edge_core,
    # ⚑ AND THE EVENT-TIER TWINS, which completed the set: `obs`/`edge` had scoped forms while
    # the two `event` reads did not, so a core-scoped fold still dragged 24,580,540 event rows
    # through python. The scope is a SEMI-JOIN through `obs` because `event` is content-addressed
    # and has no `core_id` — see `q_event_head_core` for the plan and the measured ~1,000× cut.
    "event_head_core": q_event_head_core,
    "event_ctor_core": q_event_ctor_core,
    # ⟡sql-lift: the MATERIALISED twins — same fold, height read from the per-core temp `_ht_map`
    # instead of re-derived per level. Separate entries because the cache keys on NAME.
    "pack_level_mat": q_pack_level_mat,
    "pack_level_insert_mat": q_pack_level_insert_mat,
    "pack_level_summary_mat": q_pack_level_summary_mat,
    "obs_heights_distinct_mat": q_obs_heights_distinct_mat,
    "pack_discrimination_mat": q_pack_discrimination_mat,
    "edge_postorder": q_edge_postorder,  # ⟡sql-lift: the precondition for the recursion-free fold
    "unprojected_cores_shard": q_unprojected_cores_shard,  # ⟡sql-lift: one shard's slice
    "count_shared": q_count_shared,
    "max_node_len": q_max_node_len,
    "set1_count": q_set1_count,
    # ⟡set1-rewrite — the STRUCTURAL censuses that supersede `set1_count`'s column read.
    # ⚑ `set1_count` IS KEPT DELIBERATELY, NOT YET RETIRED: it is the reference arm. The two
    # must be compared on one store before the scalar goes, because `--equiv` over a builder
    # that no longer exists proves nothing. `set1_count` reads `unit_obs.level >= 1` and
    # returns 0 while `_unit.level` is 0-or-NULL corpus-wide; whether that zero is correct
    # (inhabits ≠ mentions) is exactly what the comparison settles.
    "set1_mentions": q_set1_mentions,
    "set1_inhabits": q_set1_inhabits,
    # ⟡view-purge: the ⚑ four-snapshot repair + the two `scratch/` demand reads lifted out of raw SQL
    "project_stats": q_project_stats,
    "demand_refs": q_demand_refs,
    "module_refs": q_module_refs,
    "level_populated": q_level_populated,  # ⟡gqs-ratchet-query guard (1)
    "view.structs": v_structs,
    "view.members": v_members,
    "view.refs": v_refs,
    "view.edges": v_edges,
    "view.module_edges": v_module_edges,
    "view.modules": v_modules,  # view.orbit: tier removed
    # S1 orbit-stats: `max_orbit_len` / `orbit_node_count` / `orbit_packings` / `orbit_merged`
    # were removed 2026-08-23 with the orbit tier. `orbit_def_stats` reads `_orbit_def`, which
    # is the ARGPERM tier, and stays.
    "orbit_def_stats": q_orbit_def_stats,
    "reach": q_reach,  # ⟡L7 recursion→parallel: WITH RECURSIVE reachability closure
    # S2 render:
    "structs_index": q_structs_index,
    "structs_namemod": q_structs_namemod,
    "structs_fpnamemod": q_structs_fpnamemod,
    "modules_index": q_modules_index,
    "structs_qnamekind": q_structs_qnamekind,
    "edges_all": q_edges_all,
    "sitemap": q_sitemap,
    "structs_count": q_structs_count,
    "edges_dst_distinct": q_edges_dst_distinct,
    "edges_src_distinct": q_edges_src_distinct,
    "structs_qname": q_structs_qname,
    "indegree_top": q_indegree_top,
    "modedges_all": q_modedges_all,
}


#: REFERENCE ARMS — a builder's PRE-OPTIMISATION spelling, reachable by name so an
#: optimisation can be MEASURED semantics-preserving instead of argued to be.
#:
#: ⚑⚑ DELIBERATELY NOT IN `INTERN_BUILDERS`, WHICH IS THE WHOLE SAFETY PROPERTY. These never
#: reach `query_sql_postgres.py`, so the cached runtime cannot resolve them by name and no
#: caller can splice an unscoped licence into a `DELETE ... WHERE core_id IN (%s)` by
#: accident. They exist for `--equiv` / `--cost` — which compile live, from the builders.
#:
#: ⚑ AND A REFERENCE ARM IS NOT THE `rewire_only` CLASS. That class is a builder nothing
#: calls; these have exactly one caller each and it is a GATE. Deleting the old spelling
#: instead would leave "the scoping changes no answer" as a sentence in a docstring — the
#: shape this module was built to stop, one layer up from the SQL.
#: ⚑ `_live_scope` STAYS WHILE `_residue_only` GOES, AND THE TWO FLAGS WERE NEVER THE SAME KIND.
#: `_residue_only` selected between two DESIGNS (positional licence vs residue licence) and had
#: to collapse; `_live_scope` selects between two SPELLINGS OF ONE ANSWER — the semi-join
#: pushdown `A \ B = A \ (B ∩ A)` — and exists so `--equiv` can MEASURE them equal on a live
#: store. Deleting it would turn a measurement back into a docstring assertion, which is the
#: direction this module is built to refuse. `"drainable.unscoped"` went with its builder;
#: this is the one arm left, and it is the one that was doing work.
#: ⚑⚑ `drainable_res.no_obs_edge` IS A RETIREMENT INSTRUMENT, NOT A SPARE LICENCE (⑹,
#: 2026-08-12). ⑹ added conjunct (5) — `edge` vs its rebuild from the DURABLE tier — beside
#: the existing (4), which compares `edge` to its rebuild from `obs.ekey`. The argument that
#: (5) implies (4) is an ARGUMENT (it reasons through conjunct (3)'s encoder equality), and
#: **removing a conjunct WIDENS the licence, which is the unsafe direction.** So (4) stays and
#: this arm makes the question measurable: `--equiv drainable_res drainable_res.no_obs_edge`
#: answers "does (4) still subtract anything" as a SET DIFFERENCE on a live store. Retiring
#: (4) is a separate step that must carry that measurement.
#: ── THE ⟡view-purge ARMS — ADDED AND RETIRED THE SAME DAY, 2026-08-12. ──────────────────────
#:
#: ⚑⚑ TWELVE ARMS EXISTED FOR EXACTLY ONE MEASUREMENT AND THE TEMPORARINESS WAS THE POINT.
#: Every other arm here is PERMANENT — both spellings stay runnable forever, so `--equiv` can
#: be re-asked on any future store. These could not be: the right-hand spelling read a STORED
#: VIEW that the change DROPs, so after the migration `SELECT … FROM node` raises
#: `UndefinedTable`. **An arm that can never run again is worse than no arm** — it reads as a
#: standing gate while being a permanent failure. They read:
#:
#:     _vw_node = _T("node", "node_id", "sym", "kind", "role", "op", "lit")   … ×6
#:     "frag.node": lambda: node_sel,   "view.node": lambda: select(_vw_node)  … ×6
#:
#: ⚑ RELATION-LEVEL, NOT BUILDER-LEVEL, BECAUSE IT IS THE STRONGER CLAIM — and this is the
#: part to keep. Each pair asked "does the FRAGMENT return the same rows as the stored VIEW",
#: and if the two RELATIONS are row-identical then every builder over either is row-identical,
#: for all six at once. That also routed around a real obstruction: four of the ten affected
#: builders bind a parameter with no baked default, so a per-builder `--equiv` would return
#: empty on BOTH sides and earn `do_equiv`'s UNMEASURED refusal rather than a verdict.
#:
#: ⚑⚑ THE MEASUREMENT, VERBATIM (`--sandbox`, a populated tenant: obs 184,278 · obs_node
#: 258,501 · edge 184,232). This is what the arms existed to produce:
#:
#:     frag.node           4,966 = view.node           4,966   IDENTICAL
#:     frag.unit              57 = view.unit              57   IDENTICAL
#:     frag.node_fanin     4,910 = view.node_fanin     4,910   IDENTICAL
#:     frag.shared_subtree   913 = view.shared_subtree   913   IDENTICAL
#:     frag.node_atom        313 = view.node_atom        313   IDENTICAL
#:     frag.orbit              0 = view.orbit              0   ⚠ UNMEASURED
#:
#: ⚑ AND `orbit` IS REPORTED AS UNMEASURED RATHER THAN AS A SIXTH PASS, which is the whole
#: reason `do_equiv` refuses two empty sets. `orbit_node` holds 0 rows in EVERY tenant, so
#: both arms returned nothing and nothing was compared. Corroborated but NOT verified by a
#: second instrument: the stored `pg_get_viewdef('orbit')` body is `orbit_sel`'s compilation
#: verbatim (same joins, same COALESCE, same `ok`/`orr`/`ol`/`oo`/`opt` aliases), and the
#: relation has ZERO consumers — `pycodemod --relname orbit` reports 0 SQL sites. A text
#: identity is an argument; the row identity is the measurement, and it was not available.
REFERENCE_ARMS = {
    "drainable_res.unscoped": lambda: q_drainable_res(_live_scope=False),
    "drainable_res.no_obs_edge": lambda: q_drainable_res(_obs_edge_conjunct=False),
    # ⚑⚑⚑ ⟡converge-scheduled — THE SAME LICENCE, ASKED ABOUT ONE CORE. An arm and not a
    # builder, for the reason the `correlated` note below states: `q_drainable_res` AUTHORISES
    # DELETION, so a narrowing lands here to be MEASURED by `--equiv` before anything can splice
    # it into a `DELETE`. Deliberately absent from `INTERN_BUILDERS`.
    #
    # ⚑⚑ THE PREDICATE IS PUSHED INTO `_live_cores`, NOT WRAPPED AROUND THE OUTPUT (operator:
    # *"Don't forget the predicate!"*). `--sql drainable_res` spells `IN (SELECT obs.core_id FROM
    # obs)` EIGHT times across five `EXCEPT` arms plus the `GROUP BY` minuend; scoping the result
    # would compute the corpus-wide drainable set and discard all but one row — the licence's own
    # docstring names that failure: *"the unscoped licence READ the thing that never shrinks
    # while its ANSWER was bounded by the thing that does."* `one_core=True` narrows all nine.
    #
    # ⚑ IT DEFAULTS FALSE AT EVERY DEFINITION, so the whole-tier callers are untouched —
    # confirmed by `--check` reporting the compiled cache FRESH after the change, i.e. the
    # unscoped licence compiles byte-identically.
    "drainable_res.one_core": lambda: q_drainable_res(one_core=True),
    # ⚑⚑ ⟡disk-incident — THE SAME LICENCE ASKED WITHOUT `EXCEPT`, kept here rather than in
    # the production builder BECAUSE `q_drainable_res` AUTHORISES DELETION.  Three of its four
    # conjuncts spill (measured 2026-08-18: conjunct (4) sorts 9,438,375,610 rows at cost
    # 3.73B), and the correlated `NOT EXISTS` form is 55×/23×/2.6× cheaper — but a performance
    # rewrite that silently WIDENED what is eligible for deletion is the one failure that
    # cannot be undone, so it lands as an arm to be MEASURED by `--equiv`, never as an edit to
    # the licence.  Promotion into the return statement is a separate, reviewed act.
    "drainable_res.correlated": q_drainable_res_correlated,
    # ⚑⚑ ⟡sql-lift — THE TWO ARMS OF THE PACKING-FOLD EQUIVALENCE. `pack.sql` is the new
    # server-side fold quotiented to its PARTITION; `pack.python` is `obs_node` — the existing
    # python fold — quotiented the same way. They are REFERENCE_ARMS rather than
    # INTERN_BUILDERS because neither is a production read: they exist to be compared, which is
    # exactly what this dict is for (*"the old spelling kept as a REFERENCE_ARMS entry instead of
    # a string"*).
    #
    # ⚑ COMPARED BY PARTITION, NOT BY ID. The surrogate is a handle over the signature, so the
    # two folds agree on the GROUPING and disagree on every id; `--equiv pack.sql pack.python`
    # therefore compares member-sets. `do_equiv`'s both-empty refusal then guards the case that
    # would otherwise pass vacuously — the trap `reflects_obs` records verbatim.
    "pack.sql": q_pack_partition,
    "pack.python": q_pack_partition_python,
    # ⚑ THE UNIT-MEMBERSHIP PAIR. `members.sql` is the recursive closure over `edge` mapped
    # through `obs_node`; `members.python` is what the python DFS already wrote into
    # `unit_node`. Comparing the SQL arm to ITSELF (which I did first) shows only determinism.
    "members.sql": q_unit_members,
    "members.python": q_unit_members_stored,
}


def _named_builder(name):
    """A builder thunk by name, from the compiled registry OR the reference arms."""
    if name in INTERN_BUILDERS:
        return INTERN_BUILDERS[name]
    if name in REFERENCE_ARMS:
        return REFERENCE_ARMS[name]
    raise SystemExit(
        "no builder %r; known: %s"
        % (name, ", ".join(sorted(INTERN_BUILDERS) + sorted(REFERENCE_ARMS)))
    )


def _cost_connect(sandbox):
    """The tenant this invocation NAMED, for the cost/equiv modes.

    ⚑⚑⚑ THE `else connect()` HERE WAS AN UNSTATED-TENANT BYPASS AND THE ⟡tenant-mandatory
    FLIP IS WHAT EXPOSED IT (2026-08-24).  It read
    `sandbox_connect(reset=False) if sandbox else connect(mode="ro")` — the exact
    inlined shape `schema_rows._cli_connect` was built to absorb, wearing a helper's
    name so it did not look like one.  `--live` was UNSAYABLE in this tool: argparse
    declared `--sandbox` only, so `query_defs.py --selftest --live` exited 2 on
    *"unrecognized arguments"*.  A tenant you cannot state cannot be stated
    mandatorily — the missing half `store.tenant`'s docstring describes, still live at
    a dispatch site.

    ⚑ THE `sandbox` PARAMETER IS KEPT AND IS NOT THE LIBRARY-PARAMETER SHAPE.  All six
    callers are in this file and all six thread `a.sandbox` down from `main`; nothing
    outside supplies it.  So this is a dispatch site, not the top-level `sandbox=`
    form that `_cli_connect`'s note says must NOT be consolidated — the distinction is
    WHO CHOOSES, and here it is the operator's argv either way.  The bool stays only so
    the six call sites need not change; the DECISION now goes through the one resolver.
    """
    import store as _store

    return _store.tenant(mode="ro", label="query_defs", require="sandbox" if sandbox else None)


def _run_named(con, name):
    """The ROW SET of ONE named builder, compiled live, as tuples.

    ⚑ NO ELAPSED TIME IS RETURNED, AND AN EARLIER CUT OF THIS FUNCTION RETURNED ONE. It is
    the wrong instrument for every question this module asks (see `do_scans`), and a helper
    that hands one back invites a caller to build a verdict on it.

    ⚑ TUPLES, BECAUSE THE TWO CONNECTIONS DISAGREE ON ROW SHAPE. `sandbox_connect` sets
    `row_factory=dict_row` and `connect` does not, so comparing raw rows would compare a
    dict to a tuple and report every row different — the `dict_row` defect this tree already
    recorded once as "0 units from 18,334 rows".
    """
    # ⚑ `--param` BINDS HERE TOO, so `--equiv` can scope both arms to the same core and height.
    # Without it a parameterized arm runs on its representative default (`core_id=''`) and BOTH
    # sides return nothing — which `do_equiv` then refuses as UNMEASURED rather than reporting a
    # false pass. The refusal is correct; supplying the parameter is what makes the comparison
    # possible at all.
    sql, params = _compile_one(_named_builder(name)())
    cur = con.execute(sql, _override_params(params))
    # ⚑⚑ ARRAY COLUMNS COME BACK AS PYTHON `list`, WHICH IS UNHASHABLE — and `do_equiv` compares
    # by `set()`, so a builder returning an array crashed it with `TypeError: unhashable type`.
    # Measured the moment the packing-partition arms (whose whole payload IS an array of member
    # ids) were first compared. Freezing nested lists to tuples here is the same normalisation
    # this function already performs for `dict_row` vs tuple rows: one place where the two
    # connections' row shapes are made comparable, rather than at each caller.
    return _norm_rows(cur)


def _norm_rows(cur):
    """A cursor's rows as comparable VALUE-tuples — the two connections' shapes reconciled.

    ⚑⚑⚑ EXTRACTED FROM `_run_named` 2026-08-20 BECAUSE `verify` DID NOT HAVE IT, AND THAT IS
    WHY `--verify` WAS A VERDICT ABOUT COLUMN LABELS. `verify` spelled both arms
    `list(map(tuple, cur.fetchall()))`; `sandbox_connect` sets `row_factory=dict_row`, and
    **`tuple(a_dict)` yields the dict's KEYS**. So on the sandbox the migration gate compared
    column NAMES and never looked at a value — measured and recorded in `_reg`'s own header as
    *"MISMATCH: Core ('count_1',) vs raw ('count',)"*, two arms that each returned one row
    whose contents were never examined. It passed exactly when two spellings happened to agree.

    ⚑⚑ THE NORMALISATION ALREADY EXISTED ONE FUNCTION AWAY, which is the part worth recording:
    this is not new machinery, it is a helper that had ONE caller when it needed two. `_reg`'s
    header documents the defect and `_run_named`'s docstring documents the cure, and nothing
    connected them. A shared NAME is not a shared authority — and neither is a shared FILE.

    ⚑ BOTH NORMALISATIONS ARE LOAD-BEARING AND THEY ARE INDEPENDENT. `.values()` fixes
    dict-vs-tuple; `_hashable` freezes `list` (how postgres returns an ARRAY column) to a tuple,
    because `do_equiv` compares by `set()` and crashed `TypeError: unhashable type` the first
    time a packing-partition arm — whose whole payload IS an array of member ids — was compared.
    A caller that re-derived only the first would break on the second.
    """

    def _hashable(v):
        return tuple(_hashable(x) for x in v) if isinstance(v, list) else v

    return [tuple(_hashable(v) for v in (r.values() if isinstance(r, dict) else r)) for r in cur]


def _population(con):
    """The tier sizes every row count here is only meaningful against — the denominator rule.

    ⚑ A ROW COUNT WITHOUT ITS POPULATION IS NOT A MEASUREMENT. The defect `--scans` exists to
    expose is a read that tracks the DURABLE tier while the answer is bounded by the LIVE
    one, and that is a claim about a RATIO — 508,554 rows is a full scan of one store and a
    thin slice of a larger one, and the number alone cannot say which.

    ⚑⚑⚑ AND THE DENOMINATOR MUST NOT COST MORE THAN THE MEASUREMENT — measured 2026-08-17, and
    it stalled the arc's first live verification. `SELECT count(*) FROM edge` is a FULL
    SEQUENTIAL SCAN of 6,273,548 rows in postgres (no index-only path for an unqualified count),
    issued three times as a HEADER before `--equiv` runs either arm. On a 6,210-row trial core
    that is a 1,000:1 inversion: the header outweighed the entire comparison, the run passed
    600s, and the connection sat `idle in transaction` holding an unbounded read while the
    client had already stopped consuming it.

    ⚑⚑ THE SHAPE IS THE ARC'S OWN DEFECT, ONE LAYER UP. ③ removed exactly this from
    `pack_core_sql` — *"943,927 rows pulled to derive 70 integers"* — and the same
    materialise-to-derive-a-scalar sat in the harness built to VERIFY that removal. A tool that
    stalls on the population it reports cannot report a population.

    ⚑ THE ESTIMATE IS THE HONEST ANSWER HERE, NOT A DEGRADED ONE. `pg_class.reltuples` is what
    the PLANNER uses to choose the very plans this file measures, it is maintained by
    autovacuum, and the denominator's job is an ORDER OF MAGNITUDE (*"508,554 rows is a full
    scan of one store and a thin slice of a larger one"*) — a purpose an estimate serves
    exactly. It is labelled `~` at the print site so a reader never mistakes it for a count.
    A missing or never-analysed relation reads `-1`, which is reported as UNKNOWN rather than
    silently rendered as zero.
    """
    out = {}
    for t in ("obs", "obs_node", "edge"):
        try:
            out[t] = con.execute(
                "SELECT reltuples::bigint FROM pg_class WHERE oid = to_regclass(%s)", (t,)
            ).fetchone()
        except Exception:
            out[t] = None
    return out


def written_table(stmt):
    """The table a DML statement WRITES, or None for a pure read.

    ⚑⚑⚑ WITHOUT THIS, A WRITE IS INDISTINGUISHABLE FROM A READ AND POINTS BACKWARDS.
    `_tables_of` walks the whole statement tree, so an `INSERT INTO ref SELECT …` reports `ref`
    among its tables and `touching("ref")` lists `q_ref_insert` as a READER of the relation it
    populates. Every dependency edge then runs relation → builder, which is why a graph drawn
    from them has no flow: nothing ever comes OUT of a builder.

    ⚑⚑ THE STATEMENT KNOWS. SQLAlchemy's `Insert`/`Update`/`Delete` carry `.table`; a `Select`
    does not — so this is a property of the object, not a name convention or a verb scan over
    text. That matters because `touching`'s writer half IS a verb scan and says so
    (*"writes are NOT modelled here and are found by verb — a write via an unlisted spelling
    would be missed"*); for BUILDERS the write is exact, and the two halves should not be
    reported with the same confidence.

    ⚑ A DML BUILDER READS **AND** WRITES. `q_ref_insert` reads `obs`/`edge`/`event`/`terms` and
    writes `ref`; `q_pack_level_insert` reads `obs_node` and writes it. Both facts are real, and
    a relation that is both is drawn as TWO nodes — inbound and outbound — never as a cycle.

    ⚑⚑ IT SEARCHES THE TREE, NOT JUST THE TOP. `q_pack_level_insert` returns a `select()` over a
    DATA-MODIFYING CTE — the INSERT lives inside `WITH w AS (INSERT … RETURNING …)` so the level
    can land and report `(n, ids, top)` in one round trip. The outer statement is therefore a
    `Select`, and a top-level `isinstance` check reported **`builder writes (0)`** for `obs_node`
    on a builder whose entire purpose is writing it. Measured, not reasoned: `--touching ref`
    (a plain `INSERT`) classified fine while `--touching obs_node` did not.
    """
    from sqlalchemy.sql import dml, visitors

    for node in visitors.iterate(stmt):
        if isinstance(node, (dml.Insert, dml.Update, dml.Delete)):
            t = getattr(node, "table", None)
            nm = getattr(t, "name", None)
            if nm:
                return nm
    return None


def returned_columns(stmt):
    """The column names a statement HANDS BACK to its caller, or [] if it returns nothing.

    ⚑⚑⚑ WHAT A QUERY READS AND WHAT IT RETURNS ARE DIFFERENT FACTS, AND BOTH ARE FLOW
    (operator, 2026-08-15: *"it's not obvious to me the distinction between what a query reads
    and what it returns; both are part of a flow graph."*). `written_table` closed the
    relation→builder→relation half; this closes builder→CALLER. `q_pack_level` SCANS
    `obs`/`edge`/`event`/`obs_node` and RETURNS `(core_id, local_id, node_id)` — the second is
    what python consumes, and nothing reported it.

    ⚑⚑ THE RETURN IS WHERE THE REMAINING CLIENT-SIDE COMPUTE IS VISIBLE, which is the whole
    reason this arc exists. `q_pack_level_summary` returns THREE scalars where `q_pack_level`
    returns up to 529,003 rows over the same input — the difference between those two return
    shapes IS the lift, and a graph that draws only reads shows them as identical.

    ⚑ A DML STATEMENT RETURNS ONLY WHAT IT `RETURNING`s. `q_ref_insert` returns nothing (its
    output is the relation it wrote, already an edge via `written_table`), while
    `q_pack_level_insert` both writes `obs_node` AND returns `(n, ids, top)` — two distinct
    outbound edges from one builder, not a choice between them.
    """
    from sqlalchemy.sql import dml

    if isinstance(stmt, (dml.Insert, dml.Update, dml.Delete)):
        # ⚑ `_returning` is the RETURNING clause; a DML with none returns nothing to
        # the caller and its only output edge is the table it wrote.
        cols = getattr(stmt, "_returning", None) or ()
        return [str(getattr(c, "name", c)) for c in cols]
    cols = getattr(getattr(stmt, "selected_columns", None), "keys", None)
    return list(cols()) if callable(cols) else []


def _table_occurrences(stmt, table):
    """How many times `table` appears in the statement tree — the recursion test.

    ⚑ A DML STATEMENT MENTIONS ITS TARGET ONCE BY CONSTRUCTION, so "reads what it writes" is
    "appears more than once": once as the INSERT/UPDATE/DELETE target, again inside the SELECT
    that feeds it. `q_pack_level_insert` reads `obs_node` for its children's assigned ids and
    writes `obs_node` with the parents' — two occurrences, one fixpoint step, and the reason the
    fold runs level-by-level rather than as one statement.
    """
    from sqlalchemy.sql import visitors
    from sqlalchemy import Table as _Tbl

    return sum(1 for n in visitors.iterate(stmt) if isinstance(n, _Tbl) and n.name == table)


def _tables_of(stmt):
    """Every DECLARED table a statement ultimately reads — through CTEs and subqueries.

    ⚑⚑⚑ `get_final_froms()` ANSWERS THE WRONG QUESTION FOR A COMPOSED BUILDER, and `touching`
    used it until 2026-08-15. It returns the OUTERMOST froms, so a builder that scans `obs`
    inside a recursive CTE presents the CTE as its from and the table is one layer down. Measured:
    `--touching obs` reported **one** reader (`q_obs_all`) on a store where `q_pack_level`,
    `q_obs_height`, `q_pack_discrimination` and `q_unit_members` all read `obs` — four builders
    invisible to the only instrument that resolves readers.

    ⚑⚑ AND THE FIX IS THE OBVIOUS ONE ONCE THE QUESTION IS ASKED (operator, 2026-08-15: *"How are
    those CTEs being constructed? Because they're surely not just raw SQL. And if they're not raw
    SQL, we can decompose them with ast."*). They are SQLAlchemy Core objects — built with
    `.cte()` and `.subquery()` right here — so the statement is a TREE, and
    `sqlalchemy.sql.visitors.iterate` walks it. I had written the limit up as a missing mode and
    a caveat in a diagram; it was a wrong accessor.

    ⚑ SAME SHAPE AS THE DEFECT THIS WHOLE ARC OPENED WITH — a structural question answered by
    reading the surface. `get_final_froms` is the SQL equivalent of grepping the top of a file.

    ⚑ RETURNS NAMES OF DECLARED TABLES ONLY: a CTE has a `.name` too, and counting one as a table
    would report `h` and `s` as relations. Membership in `_MD.tables` is the filter, which also
    makes the result exactly the vocabulary `touching` reports on.
    """
    from sqlalchemy.sql import visitors
    from sqlalchemy import Table as _Tbl

    out = set()
    for node in visitors.iterate(stmt):
        if isinstance(node, _Tbl) and node.name in _MD.tables:
            out.add(node.name)
    return out


def _columns_of(stmt, table):
    """Every DECLARED column of `table` a statement mentions — the COLUMN refinement of `_tables_of`.

    ⚑⚑⚑ "IS THIS COLUMN LOAD-BEARING?" WAS A JUDGEMENT, AND THE MOTIVATING CASE IS `terms`.
    `--touching terms` lists `q_drainable_res` — the RETIRE LICENCE — among 23 readers, so the
    relation edge exists; nothing said WHICH column the licence depends on, so dropping or
    reshaping one was reviewed by reading SQL. That is the judgement-in-the-turn shape: it
    evaporates, and the next reader re-derives it differently.

    ⚑⚑ THE OPERATOR'S FRAMING WAS `EXPLAIN` OVER THE BUILDERS, AND THE TREE IS STRICTLY BETTER —
    this is a REFUTATION worth more than the confirmation. `EXPLAIN` answers about a PLAN, and a
    plan is a fact about the PLANNER and the current statistics, not about the algebra:
      * a column referenced only in the SELECT list appears in `Output` ONLY under `VERBOSE`,
        and an index-only scan can report a column the heap was never read for;
      * a restriction the planner PROVES redundant vanishes from the plan while remaining a real
        dependency of the query — so the plan UNDER-reports, in the direction that licenses a
        drop;
      * every `EXPLAIN` needs a live connection, a bound `--param`, and a tenant, so the answer
        moves with the store and cannot be a gate.
    The builders are SQLAlchemy Core objects. `sqlalchemy.sql.visitors.iterate` already walks
    them for `_tables_of`, and a `Column` node carries `.table` — so the dependency is EXACT,
    STORE-FREE, and available for every builder including the parameterized ones a plan cannot
    run. Same lesson as `_tables_of` itself: a structural question answered by reading the
    surface (there, `get_final_froms`; here, a plan) is answered one layer too shallow.

    ⚑ CTE AND SUBQUERY COLUMNS ARE EXCLUDED BY THE SAME FILTER `_tables_of` USES — a projected
    column of a CTE has a `.table` that is not in `_MD.tables`, and counting it would report `h.ht`
    as a column of a declared relation.
    """
    from sqlalchemy.sql import visitors
    from sqlalchemy import Table as _Tbl, Column as _Col

    out = set()
    for node in visitors.iterate(stmt):
        if not isinstance(node, _Col):
            continue
        t = getattr(node, "table", None)
        # ⚑⚑⚑ AN ALIAS IS NOT A TABLE, AND THE FIRST CUT OF THIS FUNCTION UNDER-REPORTED BECAUSE
        # OF IT — in the direction that licenses a drop. `q_fanin` joins `terms` FOUR times
        # (`terms AS k`, `AS r`, `AS l`, `AS o`), so every one of those `Column.table` values is
        # an `Alias` and an `isinstance(t, Table)` test skipped them all. MEASURED: `--touching
        # terms` reported 23 relation-level readers and only THREE per column, omitting
        # `q_drainable_res` — the RETIRE LICENCE, the exact case this mode was built for. A
        # column instrument that misses the licence would have called `terms.text` unreferenced.
        #
        # ⚑ `.element` UNWRAPS ONE ALIAS LAYER AND IS ITERATED, because an alias over a subquery
        # over a table nests; the loop terminates on the first non-alias. The `_MD.tables`
        # membership test then does the same job it does in `_tables_of`: a CTE or subquery has a
        # `.name` too, and only a DECLARED relation may be reported.
        for _ in range(8):
            if isinstance(t, _Tbl) or t is None:
                break
            t = getattr(t, "element", None)
        if isinstance(t, _Tbl) and t.name == table and t.name in _MD.tables:
            out.add(node.name)
    return out


def _scalar1(row):
    return list(row.values())[0] if isinstance(row, dict) else row[0]


def _override_params(params):
    """Apply `--param k=v` over a builder's compiled defaults.

    ⚑⚑⚑ WITHOUT THIS, `--explain` AND `--scans` MEASURE A QUERY THAT TOUCHES NOTHING. A
    parameterized builder is compiled with a REPRESENTATIVE default (`INTERN_BUILDERS`' contract:
    *"the bound value is a bindparam node, structure-only"*) — for `pack_level` that is
    `core_id=''`, which matches no row. Both instruments then report a plan whose every node
    reads `actual rows 0` and whose timings are microseconds: a perfectly valid measurement OF
    THE EMPTY CASE, printed in the shape of an answer about the real one.

    ⚑⚑ MEASURED, and it is why this exists: `--scans pack_level --sandbox` printed
    `0 loop-adjusted row(s) read in total` against a store holding 184,278 obs and 258,501
    obs_node rows. Nothing was wrong; the question was never asked. That is the absent-vs-unlisted
    shape inside a performance instrument, where it is especially convincing — a fast plan over
    no rows looks exactly like a fast plan.

    ⚑ VALUES ARE COERCED TO THE DEFAULT'S TYPE so `ht=1` binds an int where the builder declared
    one; a string there would make postgres compare `smallint = text` and raise, which reads as a
    builder defect rather than a CLI one.
    """
    # ⚑ READ FROM `sys.argv` RATHER THAN THREADING THE PARSED VALUE THROUGH TWO CALL SITES —
    # and accept BOTH spellings, because argparse takes `--param k=v` while a reader who saw the
    # `--param=k=v` form in a comment would reasonably type that. Silently ignoring one spelling
    # is how an instrument reports the empty case as an answer.
    over = {}
    for _i, a in enumerate(sys.argv):
        if a.startswith("--param="):
            k, _, v = a[len("--param=") :].partition("=")
            over[k] = v
        elif a == "--param" and _i + 1 < len(sys.argv):
            k, _, v = sys.argv[_i + 1].partition("=")
            over[k] = v
    if not over:
        return params
    out = dict(params)
    # ⚑⚑⚑ AN UNMATCHED KEY IS A REFUSAL, NOT A NO-OP — THIS FUNCTION'S OWN THESIS, APPLIED TO THE
    # CASE IT DID NOT COVER. The block above records why a silently-ignored `--param` SPELLING is a
    # defect: *"Silently ignoring one spelling is how an instrument reports the empty case as an
    # answer."* An unrecognised param KEY was the same defect one step further in — the spelling
    # parsed, the loop below matched nothing, and the builder ran with its representative default.
    #
    # ⚑⚑ MEASURED 2026-08-24: `--rows node_head --param lim=5` printed **23.3 MB / every node in
    # the corpus**. `q_node_head` declares no `lim` bind, so the cap was accepted, dropped, and the
    # unbounded dump read exactly like the builder's honest answer to a capped question. The
    # sibling `q_fanin` DOES take `lim`, which is what makes the miss plausible rather than
    # obvious: the same flag is load-bearing on one builder and inert on the next.
    #
    # ⚑ AND IT NAMES WHAT THE BUILDER WOULD HAVE ACCEPTED, because "unknown param" without the
    # roster sends the reader back to `--sql` to read placeholders out of compiled text — the
    # hand-parse-a-compiled-artifact shape this module refuses elsewhere.
    for k, v in over.items():
        # match on the SUFFIX: the compiler names params `core_id_1`, `ht_1`, … so the caller
        # says `--param=core_id=3253` and does not have to know the compiler's numbering.
        hit = [pk for pk in out if pk == k or pk.rsplit("_", 1)[0] == k]
        if not hit:
            _known = sorted(
                {pk.rsplit("_", 1)[0] if pk.rsplit("_", 1)[-1].isdigit() else pk for pk in out}
            )
            print(
                "query_defs --param %s=%s: this builder has NO such parameter — REFUSING, "
                "because running it would answer a DIFFERENT question in the shape of an "
                "answer to yours.\n  binds it accepts: %s"
                % (k, v, ", ".join(_known) if _known else "(none — it takes no parameters)"),
                file=sys.stderr,
            )
            sys.exit(2)
        for pk in hit:
            cur = out[pk]
            out[pk] = int(v) if isinstance(cur, int) and not isinstance(cur, bool) else v
    return out


def do_explain(name, sandbox):
    """`--explain NAME` — the PLAN, measured. The third question a Core expression owes.

    ⚑ `--sql` ANSWERS "WHAT TEXT", `--cost` ANSWERS "HOW LONG", AND NEITHER ANSWERS "WHY".
    A restriction the algebra ENTAILS is not a restriction the planner APPLIES, and the only
    thing that distinguishes those two is the node the plan chose — measured here as the
    difference between `Seq Scan on obs_node` and a semi-join driven off `ix_obsnode_pk`.
    Reaching for `EXPLAIN` by hand was impossible anyway: the compiled builders carry named
    `%(param_N)s` placeholders, so `schema.py --probe` (which passes no params) cannot run one.
    """
    con = _cost_connect(sandbox)
    sql, params = _compile_one(_named_builder(name)())
    # ⚑ SEE `_override_params`: without `--param=k=v` a parameterized builder explains its
    # REPRESENTATIVE default, which for a core_id is the empty string — a plan over zero rows,
    # printed in the shape of an answer about the real data.
    params = _override_params(params)
    cur = con.execute("EXPLAIN (ANALYZE, BUFFERS, TIMING) " + sql, params)
    for r in cur:
        print(_scalar1(r))
    return True


def _leaf_scans(node, out):
    """Walk an EXPLAIN(FORMAT JSON) plan and collect every node that READS A RELATION.

    ⚑ NO TIMING FIELD IS COLLECTED, DELIBERATELY. `Actual Total Time` sits right beside
    `Actual Rows` in the same JSON node, so carrying it would be free — and it is exactly
    the wall-clock term that must not become the evidence. Leaving it unread is cheaper
    than printing it with a caveat nobody reads.
    """
    if "Relation Name" in node:
        out.append(
            (
                node["Relation Name"],
                node.get("Node Type", "?"),
                node.get("Plan Rows", 0),
                node.get("Actual Rows", 0),
                node.get("Actual Loops", 1),
            )
        )
    for k in ("Plans", "Plan"):
        sub = node.get(k)
        if isinstance(sub, dict):
            _leaf_scans(sub, out)
        elif isinstance(sub, list):
            for s in sub:
                _leaf_scans(s, out)
    return out


def do_rows(name, sandbox):
    """`--rows NAME` — RUN a builder and print what it returned. The mode that reads a RESULT.

    ⚑⚑⚑ THE DISPATCH BRANCH FOR THIS EXISTED AND THE FUNCTION DID NOT. `main` has read
    `if a.rows: sys.exit(0 if do_rows(...))` for some time, with no `--rows` argument declared and
    no `do_rows` defined — `pycodemod --calls do_rows` reports **0 def, 1 call**. It is the
    `rewire_only` class this repo censuses: a capability written half-way and never reachable,
    invisible because argparse rejected the flag before the NameError could fire.

    ⚑⚑ AND ITS ABSENCE COST A MEASUREMENT. `q_edge_postorder` answers whether `local_id` is
    post-order corpus-wide — the precondition for replacing the recursive height CTE with a single
    ascending pass. Compiled, registered, and unreadable: `--explain` returns the PLAN, `--scans`
    returns relation TRAFFIC, `--equiv` compares two arms against each other. Three modes that
    run a builder, none that shows its answer, so a 6.27M-row structural claim stayed inherited
    from a 124,751-row SANDBOX measurement.

    ⚑ COLUMN NAMES ARE PRINTED, because a bare tuple of five integers is not a measurement — the
    reader has to map them back to `(total, post_order, max_parents, …)` by counting positions,
    which is the positional-read defect `schema.Row` exists to retire. psycopg's `dict_row` and a
    plain tuple cursor disagree on row shape, so both are normalised here exactly as `_run_named`
    does for `--equiv`.
    """
    con = _cost_connect(sandbox)
    try:
        stmt = _named_builder(name)()
    except SystemExit:
        raise
    sql, params = _compile_one(stmt)
    cur = con.execute(sql, _override_params(params))
    got = list(cur)
    # ⚑ THE HEADER COMES FROM THE STATEMENT, NOT THE CURSOR — a `dict_row` cursor exposes keys
    # and a tuple cursor does not, so reading names off the RESULT works for one backend and
    # silently degrades on the other. The Core statement knows its own output columns.
    try:
        cols = [c.name for c in stmt.selected_columns]
    except Exception:  # noqa: BLE001
        cols = []
    print("query_defs --rows %s [%s]" % (name, "sandbox" if sandbox else _store.backend()))
    if not got:
        # ⚑ EMPTY IS A RESULT AND IS SAID SO. A builder returning nothing is a fact about the
        # STORE; printing a bare "0 row(s)" invites reading it as a fact about the builder.
        print(
            "  0 row(s) — the builder ran and matched nothing. A fact about the STORE, "
            "not\n     about the query; `--sql` shows what was asked."
        )
        return True
    for r in got:
        vals = list(r.values()) if isinstance(r, dict) else list(r)
        if cols and len(cols) == len(vals):
            print("  " + " · ".join("%s=%s" % (c, _fmt_cell(v)) for c, v in zip(cols, vals)))
        else:
            print("  " + " · ".join(_fmt_cell(v) for v in vals))
    print("%d row(s)" % len(got))
    return True


def _fmt_cell(v):
    """One cell, thousands-separated when it is an integer — the figures here are populations."""
    return format(v, ",") if isinstance(v, int) and not isinstance(v, bool) else str(v)


def do_scans(name, sandbox):
    """`--scans NAME` — which relations a builder READS, in ROWS, against each relation's size.

    ⚑⚑ ROWS, NEVER SECONDS — AND THIS MODE EXISTS BECAUSE THE OBVIOUS INSTRUMENT IS THE WRONG
    ONE (user, 2026-08-12: *"NEVER rely on wall clock; CPU saturation will always be a
    wildcard, and it introduces TOCTOUs that confound the measurements."*). An elapsed time on
    a shared box is a function of every other process on it, none of which the measurer can
    see; worse, the duration and the store state it supposedly describes are read at DIFFERENT
    MOMENTS, so the number carries a hidden term by construction. The claim under test here —
    *is this query O(live tier) or O(durable tier)* — is purely structural, so it is a COUNT,
    and a count does not care what else the CPU is doing.

    ⚑ THE VERDICT IS THE RATIO `rows read / |relation|`, WHICH IS WHY IT IS COMPUTED HERE
    RATHER THAN LEFT TO THE READER. "508,554 rows" means nothing until it is read against
    `|obs_node| = 508,554`; the same figure is a full scan of one store and a slice of
    another. Putting the division in the program is what stops the judgement living in the
    turn — and `× |rel|` is a claim that survives ingesting more cores, which no second does.

    ⚑ ROWS × LOOPS, NOT ROWS. A `Bitmap Heap Scan` under a nested loop reports its rows PER
    LOOP, so a plan touching 35,398 rows once and one touching them 200 times read identically
    in the `Actual Rows` column alone. The product is the relation traffic.

    ⚑ BOTH THE PLANNER'S ESTIMATE AND THE ACTUAL ARE REPORTED, and both are clock-free. The
    estimate is fully deterministic (no execution at all); the actual is what the query really
    touched. They disagree wildly here — postgres costs a LATERAL set-returning function at
    its default 100 rows — and that disagreement is itself a finding, not noise to hide.
    """
    import json as _json

    con = _cost_connect(sandbox)
    pop = {t: _scalar1(r) for t, r in _population(con).items()}
    sql, params = _compile_one(_named_builder(name)())
    params = _override_params(params)
    # ⚑⚑⚑ THIS MODE **EXECUTES**, AND ITS NAME DOES NOT SAY SO.  `ANALYZE` is not decoration
    # here — the `actual rows` column above is the whole point, and postgres can only supply
    # it by RUNNING the query.  But the help string reads *"which relations a builder READS,
    # rows×loops each"*, which a reader takes for inspection, and MEASURED 2026-08-18 during a
    # live ENOSPC incident: reached for as a SAFETY probe on `drainable_res`, it took the
    # volume 76G → 65G before being killed, and the backend outlived the kill.
    #
    # ⚑ THE SIBLING `--explain` SAYS `EXPLAIN (ANALYZE)` PLAINLY IN ITS OWN HELP and executes
    # too — so this is ONE misleading name and ONE unread one, which want different remedies.
    # The unread one is the sharper argument for a structural guard: a correct help string one
    # line below did not protect the reader, because the NAME is what you reach by.
    #
    # ⚑ SO THE FIX IS NOT TO DROP `ANALYZE` — that would delete the mode's reason to exist.
    # It is to make the estimate half reachable WITHOUT execution (`--estimate`), and to say
    # out loud when the executing path is taken.  The estimate arm is exactly `schema.py
    # --plan`'s contract, and both are fully deterministic — the docstring above already notes
    # the estimate needs "no execution at all", so the capability was latent and unreachable.
    _est_only = "--estimate" in sys.argv
    if not _est_only:
        print(
            "⚑ --scans EXECUTES the builder (EXPLAIN ANALYZE) to report `actual rows`.\n"
            "  On a full-corpus builder that can spill to disk. `--estimate` plans only.",
            file=sys.stderr,
        )
    cur = con.execute(
        ("EXPLAIN (FORMAT JSON) " if _est_only else "EXPLAIN (ANALYZE, FORMAT JSON) ") + sql, params
    )
    plan = _scalar1(cur.fetchone())
    if isinstance(plan, str):
        plan = _json.loads(plan)
    root = plan[0]
    print(
        "query_defs --scans %s [%s]  obs %s │ obs_node %s │ edge %s"
        % (
            name,
            "sandbox" if sandbox else _store.backend(),
            *(format(pop[t], ",") for t in ("obs", "obs_node", "edge")),
        )
    )
    print("    relation   node                       est rows      actual rows   × |rel|")
    agg = {}
    for rel, kind, est, rows_, loops in _leaf_scans(root["Plan"], []):
        a = agg.setdefault((rel, kind), [0, 0, 0])
        a[0] += est * loops
        a[1] += rows_ * loops
        a[2] += loops
    # ⚑ UNDER `--estimate` THE ACTUAL COLUMN IS ABSENT, NOT ZERO, and it must print as `-`.
    # `_leaf_scans` reads `Actual Rows` with a `.get(…, 0)` default, so a plan-only run would
    # otherwise report `0` reads and a `0.00 × |rel|` ratio — a FALSE MEASUREMENT wearing the
    # shape of a good one, which is worse than the gap it fills and is the same
    # tally-without-a-denominator defect the ratio line below already refuses.
    for (rel, kind), (est, n, loops) in sorted(
        agg.items(), key=lambda kv: -(kv[1][0] if _est_only else kv[1][1])
    ):
        size = pop.get(rel)
        if _est_only:
            print(
                "  %-10s %-22s %12s %16s   %s"
                % (rel, kind, format(est, ","), "-", ("%.2f est" % (est / size)) if size else "-")
            )
            continue
        # ⚑ THE DENOMINATOR IS PRINTED AS `-` WHEN UNKNOWN, NEVER AS 1.0. `_population`
        # censuses the three relations the drain licence turns on; a ratio invented for a
        # relation whose size was never read would be the tally-without-a-denominator defect
        # this repo has recorded four times, dressed as the fix for it.
        print(
            "  %-10s %-22s %12s %16s   %s"
            % (rel, kind, format(est, ","), format(n, ","), ("%.2f" % (n / size)) if size else "-")
        )
    _col = 0 if _est_only else 1
    print(
        "  ── %s loop-adjusted row(s) %s in total; DURABLE-tier: %s"
        % (
            format(sum(a[_col] for a in agg.values()), ","),
            "ESTIMATED" if _est_only else "read",
            format(sum(a[_col] for (r, _), a in agg.items() if r in ("obs_node", "edge")), ","),
        )
    )
    if _est_only:
        print(
            "  plan only — NOTHING was executed; every figure is an ESTIMATE from "
            "pg_statistic.\n  `actual rows` requires EXPLAIN ANALYZE, which RUNS the query."
        )
    return True


def do_equiv(a, b, sandbox):
    """`--equiv A B` — do two builders return the SAME SET? The clock-free equivalence gate.

    ⚑⚑ THE GATE FOR AN OPTIMISATION THAT MUST NOT CHANGE AN ANSWER. `q_drainable` authorises
    DELETION, so "the scoping is semantics-preserving" is exactly the class of claim this
    module refuses to take on a docstring's word — `--verify` already pairs every migrated
    builder with its ORIGINAL raw SQL for the same reason. This is that discipline applied to
    a REWRITE rather than to a migration, with the old spelling kept as a `REFERENCE_ARMS`
    entry instead of a string.

    ⚑ SET, NOT MULTISET, AND NOT ORDER. Both sides are `EXCEPT` compounds, which are set
    operators in SQL — postgres already de-duplicates them, and neither carries an ORDER BY.
    Comparing as lists would report a planner's join order as a semantic difference.

    ⚑⚑ AND IT REPORTS NO TIMING, THOUGH AN EARLIER CUT PRINTED `B is 1.7× the cost of A`.
    That figure was wall clock on a shared box, i.e. a claim about what else was running;
    re-run minutes later on the same store and unchanged code it read 1.2×. **A number that
    moves 40% under no change to the thing it describes is not evidence** — and putting it
    beside a genuine set-identity verdict lends it that verdict's credibility. Row-level
    evidence lives in `--scans`, which measures relation traffic instead.
    """
    con = _cost_connect(sandbox)
    pop = _population(con)

    # ⚑ `~` AND `?` ARE LOAD-BEARING: these are planner ESTIMATES (`pg_class.reltuples`), not
    # counts, because an exact count here is a full scan of the largest relation — see
    # `_population`. A never-analysed or absent relation reads `-1` and prints `?`, which is the
    # absent-vs-empty distinction the store's own catalogue already draws.
    def _pop1(t):
        n = _scalar1(pop[t]) if pop.get(t) is not None else None
        return "?" if n is None or n < 0 else "~" + format(n, ",")

    print(
        "query_defs --equiv [%s]  obs %s │ obs_node %s │ edge %s"
        % (
            "sandbox" if sandbox else _store.backend(),
            *(_pop1(t) for t in ("obs", "obs_node", "edge")),
        )
    )
    ra, rb = _run_named(con, a), _run_named(con, b)
    print("  %-26s %8s row(s)" % (a, format(len(ra), ",")))
    print("  %-26s %8s row(s)" % (b, format(len(rb), ",")))
    sa, sb = set(ra), set(rb)
    if sa == sb:
        # ⚑⚑ TWO EMPTY SETS ARE EQUAL AND PROVE NOTHING — UNMEASURED, NOT EQUIVALENT. Caught
        # here by running it: `--equiv drainable drainable.unscoped` printed *"IDENTICAL —
        # both sets hold 0 row(s)"*, because `q_drainable`'s `floor` bindparam has no baked
        # default, binds NULL, and `max(seq) < NULL` is never true — so BOTH arms return
        # empty and the gate certifies an optimisation it never exercised. The residue form
        # (`drainable_res`) has no floor and is the one that measures.
        #
        # ⚑ THIS FILE'S SIBLINGS ALREADY CARRY THE RULE and I still shipped the defect for
        # one run: `reconstruct --triage` refuses with *"NO ROWS — UNMEASURED, not
        # verified"*, and `--edge`'s note records it once reporting `EXACT 0 MISMATCH 0 ⇒
        # verified` over nothing. Knowing a rule and applying it are different acts.
        if not sa:
            print(
                "  ⚠ BOTH EMPTY — UNMEASURED, not equivalent. Nothing was compared; a "
                "parameterised licence with no bound value returns nothing under BOTH "
                "spellings. Compare a form the store actually populates."
            )
            return False
        print("  IDENTICAL — both sets hold %s row(s)" % format(len(sa), ","))
        return True
    print(
        "  DIFFER — %s only in %s, %s only in %s"
        % (format(len(sa - sb), ","), a, format(len(sb - sa), ","), b)
    )
    for r in sorted(sa - sb)[:5]:
        print("      only in %s: %r" % (a, r))
    for r in sorted(sb - sa)[:5]:
        print("      only in %s: %r" % (b, r))
    return False


def do_equiv_sweep(a, b, core_id, sandbox):
    """`--equiv-sweep A B --param core_id=…` — the two arms at EVERY height of one core.

    ⚑⚑⚑ THREE SAMPLES ARE NOT A SWEEP, AND THAT IS WHY THIS EXISTS. `--equiv` binds ONE `ht`
    per invocation, so covering a 39-level core by hand is 39 invocations — and each one opens
    its own connection, re-plans both arms and re-reads the population header. Running it as a
    shell loop would put the judgement (which heights, in what order, what counts as a pass) in
    the turn instead of in a program, which is exactly what the standing rule forbids. One mode,
    one connection, one verdict.

    ⚑⚑ EVERY LEVEL IS CHECKED FOR DISCRIMINATION BEFORE ITS VERDICT IS BANKED, because a PASS on
    a level that could not have failed is worth nothing. `q_pack_discrimination` reports the
    distinct values of each signature component at that height; if a level has ONE class its
    agreement is vacuous and is reported as such rather than counted as a win. This is the same
    both-empty refusal `do_equiv` makes, applied per level instead of per run.

    ⚑ HEIGHTS COME FROM THE STORE, NOT FROM A RANGE. `obs_heights_distinct` returns exactly the
    levels this core populates — a `range(0, max_ht)` would invent empty levels and then report
    them as vacuous, manufacturing noise the fold never produces.

    ⚑ A SINGLE MISMATCH FAILS THE WHOLE SWEEP AND THE LOOP CONTINUES. Stopping at the first
    difference would hide whether one level disagrees or all of them, and that distinction is
    the diagnosis: one level is a bug in that level's signature handling, all levels is a bug in
    the fold. The exit code reports the verdict; the rows report the shape.
    """
    con = _cost_connect(sandbox)
    print(
        "query_defs --equiv-sweep [%s]  core %s"
        % ("sandbox" if sandbox else _store.backend(), core_id)
    )

    # ⚑ THE PARAMS REACH THE ARMS THROUGH `sys.argv`, WHICH `_override_params` READS — the same
    # channel `--param` uses. Rebinding it per level rather than threading a dict keeps the
    # sweep on the SAME path a hand-run `--equiv` takes: if the two disagreed, the sweep would
    # be measuring a spelling of its own rather than the gate.
    _sv = sys.argv

    def _at(name, ht):
        sys.argv = ["query_defs.py", "--param", "core_id=%s" % core_id, "--param", "ht=%d" % ht]
        return _run_named(con, name)

    try:
        hts = [r[0] for r in _at("obs_heights_distinct", 0)]
        if not hts:
            print("  ⚠ NO HEIGHTS — this core has no observations. UNMEASURED, not equivalent.")
            return False
        print("  %s level(s) to check\n" % len(hts))
        print("  %4s %10s %10s  %s" % ("ht", a[:10], b[:10], "verdict"))
        ok = vacuous = differ = 0
        for ht in hts:
            sa, sb = set(_at(a, ht)), set(_at(b, ht))
            _classes = len(sa)
            if sa != sb:
                differ += 1
                verdict = "DIFFER — %s only in %s, %s only in %s" % (
                    format(len(sa - sb), ","),
                    a,
                    format(len(sb - sa), ","),
                    b,
                )
            elif not sa:
                vacuous += 1
                verdict = "⚠ both empty — UNMEASURED"
            elif _classes <= 1:
                vacuous += 1
                verdict = "⚠ one class — could not have failed"
            else:
                ok += 1
                verdict = "IDENTICAL"
            print("  %4s %10s %10s  %s" % (ht, format(len(sa), ","), format(len(sb), ","), verdict))
    finally:
        sys.argv = _sv
    print("\n  %s identical · %s vacuous · %s differ" % (ok, vacuous, differ))
    if differ:
        print("  ⚑ A MISMATCH IS THE RESULT, NOT A FAILURE OF THE SWEEP — re-run the level")
        print(
            "    with `--equiv %s %s --param core_id=%s --param ht=<n>` for its rows."
            % (a, b, core_id)
        )
        return False
    if not ok:
        print("  ⚠ NOTHING DISCRIMINATING WAS COMPARED — every level was vacuous.")
        return False
    return True


# ── the verify REGISTRY: name → (builder callable, verify-kwargs, original raw SQL, raw params) ──
# `run(builder(**bkw))` rows MUST equal `con.execute(raw, rp)` rows (as a multiset).
def _reg():
    return {
        "node_head": (
            lambda: q_node_head(),
            {},
            "SELECT n.node_id, pt.text, o.text, r.text FROM _node n "
            "LEFT JOIN path_text pt ON pt.path_id=n.op_path_id "
            "LEFT JOIN terms o ON o.term_id=n.op_term_id LEFT JOIN terms r ON r.term_id=n.role_id",
            (),
        ),
        "unit_names": (
            lambda: q_unit_names(),
            {},
            "SELECT u.unit_id, pt.text FROM _unit u JOIN path_text pt ON pt.path_id=u.name_pid",
            (),
        ),
        "event_head": (
            lambda: q_event_head(),
            {},
            "SELECT e.ekey, tc.text, pq.text, e.idx, lt.text FROM event e JOIN terms tc ON tc.term_id=e.ctor_id "
            "LEFT JOIN path_text pq ON pq.path_id=e.qname_pid LEFT JOIN terms lt ON lt.term_id=e.lit_id",
            (),
        ),
        "set1_count": (
            lambda: q_set1_count(),
            {},
            "SELECT COUNT(*) FROM unit_obs WHERE level >= 1",
            (),
        ),
        "argperm_uid": (
            lambda: q_argperm_uid(),
            {},
            "SELECT u.unit_id, pt.text FROM _unit u JOIN path_text pt ON pt.path_id=u.name_pid WHERE u.copy=0",
            (),
        ),
        "deserialize_oppath": (
            lambda: q_deserialize_oppath(),
            {},
            "SELECT un.unit_id, p2.text FROM unit_node un JOIN _node n ON n.node_id=un.node_id "
            "JOIN path_text p2 ON p2.path_id=n.op_path_id WHERE n.op_path_id IS NOT NULL",
            (),
        ),
        "reuse_rows_copy": (
            q_reuse_rows_copy,
            {"min_units": 3, "lim": -1},
            "SELECT un.node_id, COALESCE(NULLIF(pt.text,''), o.text, r.text, '?') head, "
            "COUNT(DISTINCT un.unit_id) units, SUM(COALESCE(u.copy,0)) copies FROM unit_node un "
            "JOIN _node nd ON nd.node_id=un.node_id JOIN unit u ON u.unit_id=un.unit_id "
            "LEFT JOIN path_text pt ON pt.path_id=nd.op_path_id LEFT JOIN terms o ON o.term_id=nd.op_term_id "
            "LEFT JOIN terms r ON r.term_id=nd.role_id WHERE nd.node_id IN (SELECT node_id FROM node_child) "
            "GROUP BY un.node_id HAVING units>=? ORDER BY units DESC LIMIT ?",
            (3, -1),
        ),
        "reuse_rows_nocopy": (
            q_reuse_rows_nocopy,
            {"min_units": 3, "lim": -1},
            "SELECT un.node_id, COALESCE(NULLIF(pt.text,''), o.text, r.text, '?') head, "
            "COUNT(DISTINCT un.unit_id) units, NULL copies FROM unit_node un "
            "JOIN _node nd ON nd.node_id=un.node_id JOIN unit u ON u.unit_id=un.unit_id "
            "LEFT JOIN path_text pt ON pt.path_id=nd.op_path_id LEFT JOIN terms o ON o.term_id=nd.op_term_id "
            "LEFT JOIN terms r ON r.term_id=nd.role_id WHERE nd.node_id IN (SELECT node_id FROM node_child) "
            "GROUP BY un.node_id HAVING units>=? ORDER BY units DESC LIMIT ?",
            (3, -1),
        ),
        # R1 reuse_tui:
        "node_child_edges": (
            lambda: q_node_child_edges(),
            {},
            "SELECT node_id, child_id FROM node_child ORDER BY node_id, ord",
            (),
            True,
        ),  # ORDER-SENSITIVE
        "shared_subtree": (
            q_shared_subtree,
            {"min_fanin": 2},
            "SELECT node_id, fanin FROM shared_subtree WHERE fanin>=?",
            (2,),
        ),
        "defcopy_units": (
            lambda: q_defcopy_units(),
            {},
            "SELECT unit_id FROM _unit WHERE copy=1",
            (),
        ),
        "unit_node_all": (
            lambda: q_unit_node_all(),
            {},
            "SELECT unit_id, node_id FROM unit_node",
            (),
        ),
        "core_count": (lambda: q_core_count(), {}, "SELECT COUNT(DISTINCT file_id) FROM _unit", ()),
        # ⚑⚑ THE RAW REFERENCE ARM OF THIS TABLE IS STILL SQLITE-SPELLED, AND SAYING SO IS
        # THE HONEST STATE OF ⓺. The `table_exists` / `object_type` rows are removed with
        # their builders (they read `sqlite_master`), but every remaining row's raw
        # comparison SQL binds `?` — the sqlite paramstyle psycopg refuses. So `--verify`
        # now opens the right store and compares against reference queries the driver
        # cannot bind. That is a SEPARATE port (≈40 statements, `?` → `%s`), owed and not
        # done here; it is recorded at the site rather than in a plan file because this
        # table is where the next reader meets it.
        #
        # ⚑⚑ AND A SECOND, INDEPENDENT BREAK — MEASURED 2026-08-12, NOT INFERRED.
        # `--verify --only count_shared --sandbox` reports
        # *"MISMATCH: Core ('count_1',) vs raw ('count',)"* — BOTH arms returned 1 row and
        # the VALUES were never compared. `sandbox_connect` sets `row_factory=dict_row`, and
        # `tuple(a_dict)` yields its KEYS, so `verify` is comparing COLUMN NAMES. That is the
        # `dict_row` defect `_run_named` normalises against by name (*"comparing raw rows
        # would compare a dict to a tuple"*) and this function does not — so on the sandbox
        # `--verify` is a verdict machine whose verdict is about labels. It passes exactly
        # when two spellings happen to agree.
        #
        # ⚑⚑ SIX ROWS' RAW ARMS HAVE NOW **EXPIRED** (⟡view-purge, 2026-08-12): `uid`,
        # `support_hist`, `fanin`, `extract`, `clusters_overlap`, `shared_subtree`,
        # `count_shared` and the two `reuse_rows_*` name `unit` / `node` / `node_fanin` /
        # `shared_subtree` — relations the store no longer holds. They are left VERBATIM and
        # that is a decision, not an oversight:
        #
        #   * REWRITING them would make them TAUTOLOGIES. A reference arm's entire value is
        #     that it is INDEPENDENT of the builder; the only view-free spelling available is
        #     the fragment's own compiled body, so a "fixed" arm would verify the builder
        #     against itself and report PASS by construction. A gate that cannot fail is
        #     worse than one that errors.
        #   * DELETING them would erase the ORIGINAL spelling, which is the historical record
        #     this table exists to keep — and would silently shrink `--verify`'s denominator,
        #     the shape `run_selftests` is watched for.
        #
        # So they are NAMED AS EXPIRED. Reviving `--verify` needs a reference arm built from
        # something other than the builder — the pre-purge store, a fixture, or a second
        # independent implementation — and that is a piece of work, not a spelling fix. It
        # sits on top of the `?` port above; neither is reachable by editing this table.
        "core_fp_ids": (q_core_fp_ids, {}, "SELECT core_id FROM core_fp", ()),
        "core_fp_mtimes": (q_core_fp_mtimes, {}, "SELECT core_id, mtime FROM core_fp", ()),
        "core_fp_mtime": (
            q_core_fp_mtime,
            lambda c: {"core_id": _samp_core(c)},
            "SELECT mtime FROM core_fp WHERE core_id=?",
            lambda c: (_samp_core(c),),
        ),
        "level_populated": (
            q_level_populated,
            {},
            "SELECT COUNT(*) FROM unit_obs WHERE level IS NOT NULL",
            (),
        ),
        # R1 sppf_query (dynamic params: resolve a sample uid/name/size at run time):
        "uid": (
            q_uid,
            lambda c: {"name": _samp(c)[1], "likep": "%." + _samp(c)[1]},
            "SELECT unit_id FROM unit WHERE name=? OR name LIKE ?",
            lambda c: (_samp(c)[1], "%." + _samp(c)[1]),
        ),
        "support_count": (
            q_support_count,
            lambda c: {"uid": _samp(c)[0]},
            "SELECT COUNT(*) k FROM unit_node WHERE unit_id=?",
            lambda c: (_samp(c)[0],),
        ),
        "support_hist": (
            q_support_hist,
            lambda c: {"uid": _samp(c)[0]},
            "SELECT COALESCE(NULLIF(nd.op,''), nd.role, nd.kind) head, COUNT(*) k FROM unit_node un "
            "JOIN node nd ON nd.node_id=un.node_id WHERE un.unit_id=? GROUP BY head ORDER BY k DESC LIMIT 12",
            lambda c: (_samp(c)[0],),
            True,
        ),  # ORDER BY k DESC
        "fanin": (
            q_fanin,
            {"lim": 20},
            "SELECT nf.node_id, COALESCE(NULLIF(nd.op,''),nd.role,nd.kind) head, nf.fanin FROM node_fanin nf "
            "JOIN node nd ON nd.node_id=nf.node_id ORDER BY nf.fanin DESC LIMIT ?",
            (20,),
            True,
        ),  # ORDER BY fanin DESC
        "extract": (
            q_extract,
            {"m": 3},
            "SELECT un.node_id, COALESCE(NULLIF(nd.op,''),nd.role,nd.kind) head, COUNT(DISTINCT un.unit_id) units "
            "FROM unit_node un JOIN node nd ON nd.node_id=un.node_id WHERE nd.node_id IN (SELECT node_id FROM node_child) "
            "GROUP BY un.node_id HAVING units>=? ORDER BY units DESC LIMIT 20",
            (3,),
            True,
        ),  # ORDER BY units DESC
        "clusters_overlap": (
            q_clusters_overlap,
            lambda c: {"sz": _samp(c)[2], "uid": _samp(c)[0], "thr": 0.0},
            "SELECT v.name, COUNT(*) shared, ? sz FROM unit_node a JOIN unit_node b ON a.node_id=b.node_id "
            "JOIN unit v ON v.unit_id=b.unit_id WHERE a.unit_id=? AND b.unit_id!=? GROUP BY b.unit_id "
            "HAVING (1.0*shared/?) >= ? ORDER BY shared DESC LIMIT 15",
            lambda c: (_samp(c)[2], _samp(c)[0], _samp(c)[0], _samp(c)[2], 0.0),
            True,
        ),  # ORDER BY shared DESC
        # R1 reuse_catalog deserialize base reads:
        "pathtext_all": (q_pathtext_all, {}, "SELECT path_id, text FROM path_text", ()),
        "terms_all": (q_terms_all, {}, "SELECT term_id, text FROM terms", ()),
        "unit_fields": (
            q_unit_fields,
            {},
            "SELECT unit_id, name_pid, kind_id, module_pid, root_lid FROM _unit",
            (),
        ),
        "unit_cod": (
            q_unit_cod,
            {},
            "SELECT unit_id, cod_ctor_id, cod_qname_pid FROM _unit_cod",
            (),
        ),
        "unit_member": (
            q_unit_member,
            {},
            "SELECT unit_id, ord, member_name_pid, member_unit_id FROM unit_member ORDER BY unit_id, ord",
            (),
            True,
        ),
        # R2 sppf_db projection reads:
        "event_ctor": (
            q_event_ctor,
            {},
            "SELECT e.ekey, tc.text FROM event e JOIN terms tc ON tc.term_id=e.ctor_id",
            (),
        ),
        "obs_all": (q_obs_all, {}, "SELECT core_id, local_id, ekey FROM obs", ()),
        "edge_all": (q_edge_all, {}, "SELECT core_id, plid, ord, clid FROM edge", ()),
        "count_shared": (q_count_shared, {}, "SELECT COUNT(*) FROM shared_subtree", ()),
        "max_node_len": (q_max_node_len, {}, "SELECT MAX(LENGTH(node_id)) FROM _node", ()),
        # S1 — sppf_db argperm stats. The four orbit-tier entries (`max_orbit_len`,
        # `orbit_node_count`, `orbit_packings`, `orbit_merged`) were removed 2026-08-23 with
        # that tier; `_orbit_def` is ARGPERM and unaffected.
        "orbit_def_stats": (
            q_orbit_def_stats,
            {},
            "SELECT COUNT(*), COUNT(DISTINCT type_key), COUNT(DISTINCT graded_key) FROM _orbit_def",
            (),
        ),
        # ⟡L7 — the WITH RECURSIVE reachability closure == the eager python _support/_subnodes walk (group "recur"):
        "reach": (
            q_reach,
            lambda c: {"root": _samp_node(c)},
            "WITH RECURSIVE reach(node_id) AS (SELECT :root UNION "
            "SELECT nc.child_id FROM reach r JOIN node_child nc ON nc.node_id=r.node_id) SELECT node_id FROM reach",
            lambda c: {"root": _samp_node(c)},
        ),
        # S2 — reuse_catalog render_* view reads (group "render": target the reuse-catalog output db —
        # structs/edges/module_edges/modules/in_degree/meta, populated by reuse_catalog's build):
        "meta_failed": (q_meta_failed, {}, "SELECT value FROM meta WHERE key='failed'", ()),
        "structs_index": (q_structs_index, {}, "SELECT name, kind, module, desc FROM structs", ()),
        "structs_namemod": (q_structs_namemod, {}, "SELECT name, module FROM structs", ()),
        "structs_fpnamemod": (q_structs_fpnamemod, {}, "SELECT fp, name, module FROM structs", ()),
        "modules_index": (
            q_modules_index,
            {},
            "SELECT module, purpose FROM modules WHERE is_index = 1",
            (),
        ),
        "structs_qnamekind": (q_structs_qnamekind, {}, "SELECT qname, kind FROM structs", ()),
        "edges_all": (q_edges_all, {}, "SELECT src, dst FROM edges", ()),
        "sitemap": (
            q_sitemap,
            {},
            "SELECT s.qname, s.module, s.name, COALESCE(d.deg, 0) AS indeg "
            "FROM structs s LEFT JOIN in_degree d ON d.qname = s.qname",
            (),
        ),
        "structs_count": (q_structs_count, {}, "SELECT COUNT(*) FROM structs", ()),
        "edges_dst_distinct": (q_edges_dst_distinct, {}, "SELECT DISTINCT dst FROM edges", ()),
        "edges_src_distinct": (q_edges_src_distinct, {}, "SELECT DISTINCT src FROM edges", ()),
        "structs_qname": (q_structs_qname, {}, "SELECT qname FROM structs", ()),
        "indegree_top": (
            q_indegree_top,
            {},
            "SELECT qname, deg FROM in_degree ORDER BY deg DESC, qname LIMIT 20",
            (),
            True,
        ),  # ORDER-SENSITIVE
        "modedges_all": (q_modedges_all, {}, "SELECT src, dst FROM module_edges", ()),
        # ⚑⚑ ⟡dec-lift: THE RAW ARM IS `dec_drain.answer_sql`'s STATEMENT VERBATIM, and it is
        # the first row here whose reference arm is neither sqlite-spelled nor expired — it
        # binds `%s` because the decode family was postgres-only from the start. So this row
        # is usable the moment the two breaks above are repaired, and it is registered now
        # rather than later precisely so it is not forgotten when they are.
        #
        # ⚑⚑ BUT IT IS NOT YET A VERDICT, AND THAT MUST BE SAID AT THE SITE. Both breaks
        # documented above still apply to this row on the sandbox: `dict_row` makes `verify`
        # compare COLUMN NAMES rather than values, so a PASS here establishes that the two
        # arms agree about their labels and NOTHING about their rows. The real evidence for
        # this builder is `--explain` binding on postgres (it does; the plan expands the whole
        # shadow reconstruction) plus `sppf_db --selftest` holding at its baseline.
        #
        # ⚑ `params` IS `(None, None)` — the UNSCOPED read, matching the builder's baked
        # default. The raw form spells the parameter twice positionally; the builder spells it
        # once by name. That asymmetry is the thing `_nullable_scope` exists to remove, and it
        # is why the two arms cannot share a parameter tuple.
        "dec_answer": (
            q_dec_answer,
            {},
            "SELECT s.core_id, s.relpath, s.mtime, s.producer, s.dec "
            "FROM core_decoded_shadow s "
            "WHERE (%s::text IS NULL OR s.relpath = %s::text) "
            "ORDER BY 2",
            (None, None),
            True,
        ),  # ORDER-SENSITIVE
    }


# builder groups: the default `--verify` covers only "catalog" (the SPPF catalog.db); render/orbit builders
# target SECONDARY projections (need their db populated) and are opt-in via `--group render|orbit` (`--group all`
# runs every group). ⟡rewire-secondary-projections.
_GROUP = {
    n: "render"
    for n in (
        "meta_failed",
        "structs_index",
        "structs_namemod",
        "structs_fpnamemod",
        "modules_index",
        "structs_qnamekind",
        "edges_all",
        "sitemap",
        "structs_count",
        "edges_dst_distinct",
        "edges_src_distinct",
        "structs_qname",
        "indegree_top",
        "modedges_all",
    )
}
_GROUP["orbit_def_stats"] = "orbit"  # the group's other four went with the orbit tier
_GROUP["reach"] = (
    "recur"  # ⟡L7 recursion→parallel (needs node_child; verified on the SPPF catalog.db)
)
_GROUP.update(
    {n: "ingest" for n in ("core_fp_ids", "core_fp_mtimes", "core_fp_mtime", "level_populated")}
)  # ⟡gqs: fresh event-tier DB


def _group_of(name):
    return _GROUP.get(name, "catalog")


_SAMP = None


def _samp(con):
    """a stable sample (uid, name, size) for verifying uid-parameterized builders — a unit with many nodes.

    ⚑⚑ TWO STATEMENTS BECAME ONE (⟡view-purge, 2026-08-12), AND BOTH DEFECTS WERE REAL. It
    read `SELECT unit_id, COUNT(*) … FROM unit_node …` and then `SELECT name FROM unit WHERE
    unit_id=?` — (1) the second named the compat VIEW this change drops, and (2) the pair was
    two SNAPSHOTS: a unit deleted between them yields a `uid` with no `name` and a `TypeError`
    on the subscript, which reads as a broken sample rather than as a race. The dependency
    looked like it forced two round trips; it did not — joining the fragment to the aggregate
    answers both in one, which is exactly the composition a stored view could not offer.
    ⚑ AND THE `?` WENT WITH THEM. That paramstyle is sqlite's and psycopg rejects it, so this
    helper could not run on the live backend at all — the `≈40 statements owed` port named in
    `_reg`'s note, one statement of it paid because the purge was already here.
    """
    global _SAMP
    if _SAMP is None:
        _u = unit_sel.subquery("u")
        _k = func.count().label("k")
        sql, params = _compile_one(
            select(unit_node.c.unit_id, _u.c.name, _k)
            .select_from(unit_node.join(_u, _u.c.unit_id == unit_node.c.unit_id))
            .group_by(unit_node.c.unit_id, _u.c.name)
            .order_by(_k.desc())
            .limit(1)
        )
        # ⚑ NORMALISED THE WAY `_run_named` DOES, and for its reason: `sandbox_connect` sets
        # `row_factory=dict_row` and `connect` does not, so `tuple(row)` on the sandbox would
        # yield the COLUMN NAMES — the `dict_row` defect that once read 18,334 rows as 1.
        _r = con.execute(sql, params).fetchone()
        _SAMP = tuple(_r.values()) if isinstance(_r, dict) else tuple(_r)
    return _SAMP


_SAMPN = None


def _samp_node(con):
    """a stable sample root for the reachability CTE — the node with the most children (a deep closure)."""
    global _SAMPN
    if _SAMPN is None:
        _SAMPN = con.execute(
            "SELECT node_id FROM node_child GROUP BY node_id ORDER BY COUNT(*) DESC LIMIT 1"
        ).fetchone()[0]
    return _SAMPN


_SAMPC = None


def _samp_core(con):
    """a stable sample core_id for the core_fp mtime-by-id builder (⟡gqs-nolawsql, group 'ingest')."""
    global _SAMPC
    if _SAMPC is None:
        _SAMPC = con.execute("SELECT core_id FROM core_fp LIMIT 1").fetchone()[0]
    return _SAMPC


def verify(con, only=None, group="catalog"):
    """Each builder against its ORIGINAL raw SQL — the MIGRATION gate. Nothing migrates without it.

    ⚑⚑ THREE VERDICTS, COUNTED APART, because they send the operator to different places —
    the rule `dec_tree.complete_sql` states and this function did not follow:

      PASS        both arms ran over a NON-EMPTY population and agreed. The only one that is
                  evidence about the builder.
      FAIL        they disagreed, or an arm could not RUN (a sqlite-spelled `?`, a relation the
                  ⟡view-purge deleted). Both are the operator's problem; neither is a pass.
      UNMEASURED  both returned 0 rows. Vacuous — see the branch's own note.

    A single ok/fail split collapsed the third into the first, which on an empty tenant is
    every builder in the table.
    """
    reg = _reg()
    ok = 0
    fail = []
    sel = []
    unmeasured = []
    for name, entry in reg.items():
        if group is not None and _group_of(name) != group:
            continue  # None = all groups
        if only and name not in only:
            continue
        sel.append(name)
        build, bkw, raw, rp = entry[:4]
        ordered = entry[4] if len(entry) > 4 else False
        # ⚑⚑ THE DYNAMIC-PARAMETER CALLBACKS ARE INSIDE THE GUARD, AND PUTTING THEM OUTSIDE IT
        # WAS A MEASURED MISTAKE. `bkw`/`rp` may be `lambda c: {...}` that QUERY the store to
        # resolve a representative uid or core (`_samp`, `_samp_node`, `_samp_core`), so on a
        # tenant missing those relations they raise BEFORE either arm runs. With the guard one
        # line lower, `--verify --group catalog` reported thirteen builders correctly and then
        # died in a traceback on the fourteenth — so a guard that exists to keep one broken
        # entry from hiding the others was itself hiding them.
        #
        # ⚑ THE PARAMETER RESOLUTION IS PART OF "CAN THIS ARM RUN", NOT A PRECONDITION OF IT.
        try:
            bkw = (
                bkw(con) if callable(bkw) else bkw
            )  # dynamic params (a sample uid, resolved at run)
            rp = rp(con) if callable(rp) else rp
            # ⚑⚑ `_norm_rows`, NOT `map(tuple, …)` — see its docstring. Under `dict_row` the
            # old spelling compared column NAMES, so this gate's verdict was about labels on
            # exactly the tenant (`--sandbox`) a migration is supposed to be verified against.
            nr = _norm_rows(run(con, build(), **bkw).fetchall())
            orr = _norm_rows(con.execute(raw, rp).fetchall())
        except Exception as _e:  # noqa: BLE001 — naming IS the job
            # ⚑⚑ AN ARM THAT CANNOT RUN IS NOT A PASS AND NOT A SILENT SKIP. `_reg`'s header
            # records two populations that cannot execute here — raw arms still spelled with
            # sqlite's `?` (psycopg refuses to bind), and six arms naming relations the
            # ⟡view-purge DELETED — and before this branch either one took the whole run down
            # with a traceback, so ONE unrunnable arm hid every other builder's verdict.
            # Counted as a FAILURE with its reason, because "the reference arm is broken" is a
            # fact the denominator must carry: a gate that quietly drops what it cannot test
            # reports a clean pass over a shrinking population.
            con.rollback()
            fail.append(name)
            print(
                f"  ✗ {name:22s} UNRUNNABLE: {type(_e).__name__}: "
                f"{str(_e).strip().splitlines()[0][:90]}"
            )
            continue
        new = nr if ordered else sorted(nr)  # ORDER-SENSITIVE consumers: compare in order
        old = orr if ordered else sorted(orr)
        if new == old and not new:
            # ⚑⚑⚑ TWO EMPTY ARMS AGREE ABOUT NOTHING, AND COUNTING THAT AS A PASS IS HOW A
            # MIGRATION GATE BECOMES A FORMALITY. `do_equiv` already refuses this case
            # (*"BOTH sides return nothing — which `do_equiv` then refuses as UNMEASURED
            # rather than reporting a false pass"*); `verify` did not, so on the default
            # sandbox — which the suite leaves EMPTY, because its fixtures live in per-test
            # schemas it drops — every builder read `✓ 0 rows — Core == raw`. A translation
            # with the columns in the wrong ORDER passes that. So does one selecting the
            # wrong RELATION. So does one whose predicate matches nothing.
            #
            # ⚑ THIS IS THE `census-green-is-a-fact-about-the-census` SHAPE: zero reports the
            # boundary of what the instrument could SEE, and a false ZERO gets banked where a
            # false positive would have been investigated. UNMEASURED is counted apart from
            # both PASS and FAIL — it is not a defect in the builder, and it is not evidence
            # about it either. `--verify` exits non-zero only on real failures, so an
            # unmeasured run does not block; it just refuses to claim it verified anything.
            unmeasured.append(name)
            print(
                f"  ~ {name:22s} UNMEASURED — both arms returned 0 rows over an empty "
                f"population; agreement here is vacuous"
            )
        elif new == old:
            ok += 1
            print(f"  ✓ {name:22s} {len(new)} rows — Core == raw")
        else:
            fail.append(name)
            print(f"  ✗ {name:22s} MISMATCH: Core {len(new)} rows vs raw {len(old)} rows")
            for a, b in zip(new[:3], old[:3]):
                if a != b:
                    print(f"      Core {a}\n      raw  {b}")
    # ⚑ THE UNMEASURED COUNT RIDES IN THE HEADLINE, NEVER FOLDED INTO THE DENOMINATOR'S PASS
    # SIDE. "12/12 result-equivalent" over an empty store is the sentence this gate must never
    # be able to print — the reader has to see that nothing was actually compared.
    print(
        f"\n{'PASS' if not fail else 'FAIL'} — {ok}/{len(sel)} builders result-equivalent"
        + (f"; {len(unmeasured)} UNMEASURED (empty population): {unmeasured}" if unmeasured else "")
        + (f"; failures: {fail}" if fail else "")
    )
    if unmeasured and not ok and not fail:
        # ⚑ A RUN THAT MEASURED NOTHING SAYS SO IN ITS OWN VOICE, because "PASS — 0/12" is
        # still a line somebody will quote as a pass. The remedy is named: this gate needs a
        # POPULATED tenant, and the sandbox is empty by construction after a suite run.
        print(
            "  ⚑ NOTHING WAS VERIFIED. Every arm ran over an empty population, so this run "
            "is\n    evidence about the STORE, not about the builders. Seed the tenant "
            "first."
        )
    return not fail


# ── the compiled-query cache: query_sql[_<backend>].py (⟡qinfra) ────────────────────────────────────
# `--compile` renders every INTERN_BUILDERS entry to SQL + its baked default params; the runtime
# (query_builders.py) executes SQL[name] with NO SQLAlchemy. `--check` recompiles in-memory and diffs vs the
# committed file (drift → exit 1), same anti-drift discipline as gen_build_makefiles --check.
#
# ⚑ THE CACHE IS PER-BACKEND, AND ITS ABSENCE WAS A GATE RED BY CONSTRUCTION (2026-08-06).
# `query_sql.py` held ONE dialect's text, so the moment `store.dialect()` could answer
# `postgresql` the `--check` gate reported STALE for a tree with nothing wrong in it —
# the committed SQLite text and the freshly-rendered postgres text differ BY DESIGN.
# A gate that cannot be green under a supported configuration trains people to ignore it.
#
# MEASURED before choosing this shape: all 63 builders compile under postgres, 0 raise,
# and 40 render BYTE-IDENTICAL text. So the port is a RECOMPILE, not a rewrite — which is
# exactly why caching per backend is cheap and hand-porting would have been wrong.
#
# ⚑⚑ AND WITH SQLITE GONE (⓺, 2026-08-11) THERE IS ONE CACHE — BUT IT KEEPS THE SUFFIXED
# NAME, WHICH IS THE OPPOSITE OF WHAT "collapse to one" SUGGESTS. The tempting move is to
# restore the short `query_sql.py`, since a suffix that distinguishes nothing is noise.
# That name currently holds SQLITE TEXT on every existing checkout, and `_load_sql` used
# to FALL BACK to it — so re-using it would make a stale working tree load sqlite SQL
# under a postgres connection, silently. That is verbatim the defect the block above
# records happening TWICE (`:named` params bound to psycopg; "1 packings, 0 units" from
# 185 cores, exit 0). Deleting `query_sql.py` and keeping the name that says what the file
# HOLDS turns the same staleness into an ImportError instead.
#
# ⚑ `QUERY_SQL` IS DELETED WITH IT — `pycodemod --calls QUERY_SQL`: bound at this line,
# ZERO references anywhere in 693 files. It existed as "the historical name, for existing
# readers" and had no readers, historical or otherwise.
def _cache_path(back=None):
    return os.path.join(HERE, "query_sql_postgres.py")


def _compile_one(stmt):
    # ⚑ THE SAME AUTHORITY AS `run` — see its note. The cache and the executor must name
    # ONE dialect or the committed SQL can describe a different backend than the one the
    # runtime talks to, and `--check` would still pass because it recompiles through the
    # same (wrong) spelling.
    compiled = stmt.compile(dialect=_store.dialect())
    return str(compiled), {k: compiled.params[k] for k in sorted(compiled.params)}


def compile_text():
    """Render query_sql.py source — deterministic (builders + param keys sorted)."""
    rows = []
    for name in sorted(INTERN_BUILDERS):
        sql, params = _compile_one(INTERN_BUILDERS[name]())
        rows.append(f"  {name!r}: ({sql!r}, {params!r}),")
    return (
        "# GENERATED by query_defs.py --compile — DO NOT EDIT BY HAND.\n"
        "# Regenerate: python3 jea/metalanguage/query_defs.py --compile\n"
        "# The cached runtime (query_builders.py) executes SQL[name] with NO SQLAlchemy import.\n"
        "SQL = {\n" + "\n".join(rows) + "\n}\n"
    )


def do_compile():
    path = _cache_path()
    with open(path, "w") as f:
        f.write(compile_text())
    print(
        f"query_defs --compile: wrote {os.path.basename(path)} "
        f"({len(INTERN_BUILDERS)} builders, {_store.backend()})"
    )


def do_check():
    path = _cache_path()
    base = os.path.basename(path)
    fresh = compile_text()
    try:
        on_disk = open(path).read()
    except FileNotFoundError:
        # ⚑ NAME THE BACKEND IN THE REMEDY. A bare "run --compile" would have the reader
        # regenerate whichever cache their ambient SUBSTRATE_STORE selects — which is how
        # a missing postgres cache gets "fixed" by rewriting the sqlite one.
        print(
            f"query_defs --check: {base} MISSING — run "
            f"`SUBSTRATE_STORE={_store.backend()} python3 jea/metalanguage/query_defs.py --compile`",
            file=sys.stderr,
        )
        return False
    if fresh == on_disk:
        print(
            f"query_defs --check: {base} fresh ({len(INTERN_BUILDERS)} builders, "
            f"{_store.backend()})"
        )
        return True
    # ⚑⚑ NAME WHICH BUILDERS DRIFTED, NOT JUST THAT THE FILE DID. A one-bit STALE cannot
    # discharge the obligation an optimisation carries: *this change touches the licence and
    # NOTHING ELSE*. `_rebuilt_obs`/`_stored_edges` are shared with three whole-tier readers
    # (`q_obs_reconstructed`, `q_edge_disagreement`, `q_edge_durable_disagreement`), and the
    # only mechanical evidence that the shared helpers still compile IDENTICALLY for them is
    # a per-name diff. Reading it out of a `diff` of the generated file by eye is the
    # judgement-in-the-turn this module is the single source against.
    changed = []
    try:
        import query_sql_postgres as _old

        for name in sorted(INTERN_BUILDERS):
            new = _compile_one(INTERN_BUILDERS[name]())
            if _old.SQL.get(name) != new:
                changed.append(name)
        gone = sorted(set(_old.SQL) - set(INTERN_BUILDERS))
        added = sorted(set(INTERN_BUILDERS) - set(_old.SQL))
    except Exception as e:  # a cache too broken to import is still STALE
        changed, gone, added = ["<uncomparable: %s>" % e], [], []
    print(
        f"query_defs --check: {base} STALE — {len(changed)} builder(s) differ"
        + (f", {len(added)} added" if added else "")
        + (f", {len(gone)} removed" if gone else ""),
        file=sys.stderr,
    )
    for n in changed + [f"+{n}" for n in added] + [f"-{n}" for n in gone]:
        print(f"    {n}", file=sys.stderr)
    print(
        f"  run `SUBSTRATE_STORE={_store.backend()} python3 "
        f"jea/metalanguage/query_defs.py --compile`",
        file=sys.stderr,
    )
    return False


def drops(decl=None):
    """⟡no-automated-drop — every `DROP TABLE` in the SQL-writing modules, with its CALLER.

    `[(relation, path, line, enclosing_function)]`, sorted.

    ⚑⚑⚑ THE RULE THIS EXISTS TO CHECK (operator, 2026-08-22): **"We should not have any
    drop-table statements that are not part of singleton operations. Drop-table statements
    should not be automated."** A `DROP TABLE` takes `AccessExclusiveLock` — the strongest lock
    postgres has, blocking every other access including reads — so a drop reachable from a
    per-item or automated path is an exclusive lock taken at whatever concurrency the caller
    happens to run at.

    ⚑⚑ AND THE POPULATION WAS UNASKABLE BEFORE THIS. `--touching <rel>` already verb-scans for
    `drop table` and reports file:line, but ONE RELATION AT A TIME — 31 calls to see the whole
    set, and no caller attribution in any of them. So the rule could be stated and not checked,
    which is the shape `declared_indexes` was in when ⟡assert-dont-establish went unenforced for
    two call sites. MEASURED the same session: `project_ref` held a `DROP TABLE ref` reachable
    from `build`, i.e. from `make`, and it was found by reading rather than by asking.

    ⚑ THE ENCLOSING FUNCTION IS THE WHOLE POINT, not the line. *"Is this drop automated?"* is a
    question about the CALLER — `init_db` dropping a tier once at setup is the sanctioned shape
    (`init_db`'s own docstring: *"create the event schema ONCE, before the parallel `make ingest`
    sweep, so no ingest job races the initial CREATE"*), while the same statement inside a
    projection that runs per core is not. A file:line cannot tell those apart; a function name
    can, and the reviewer supplies the singleton/automated judgement.

    ⚑ VERB-SCANNED, SO IT REPORTS PRESENCE AND NEVER ABSENCE. A drop spelled through a variable,
    an f-string, or a helper is invisible here — the same asymmetry `touching` states for its own
    `writers` half. A clean result means "no drop found under these spellings", not "no drop".
    """
    import glob as _glob
    import re as _re

    if decl is None:
        import query_decl as decl
    root = os.path.dirname(os.path.dirname(HERE))
    out = []
    for p in sorted(
        _glob.glob(os.path.join(root, "scripts", "*.py"))
        + _glob.glob(os.path.join(root, "jea", "metalanguage", "*.py"))
    ):
        try:
            src = open(p, encoding="utf-8").read()
        except OSError:
            continue
        # ⚑ THE ENCLOSING `def` IS THE NEAREST PRECEDING ONE AT COLUMN 0 OR AS A METHOD — a
        # line-scan rather than an AST walk, deliberately: this module must not grow an AST
        # dependency for a census, and `pycodemod` owns the AST question. The approximation is
        # stated rather than hidden, and it is exact for this corpus's flat function layout.
        fns = [(m.start(), m.group(1)) for m in _re.finditer(r"^\s*def\s+(\w+)", src, _re.M)]
        # ⚑⚑ A COMMENTED-OUT DROP IS NOT A DROP, AND THE CENSUS COUNTED ONE. `write_events` holds
        # the removed `--full` tier-drop QUOTED in a ⚑ block explaining the removal, and the scan
        # reported it as a live site — so a retirement documented in place read as the thing it
        # retired. The line's first non-space character settles it: a `#` before the string means
        # the statement is prose about code, not code.
        #
        # ⚑ IT IS A LINE TEST, NOT A PARSE, and that is honest about its own limit: a drop inside
        # a triple-quoted docstring is still counted, because that string IS reachable text and
        # this scan cannot tell a docstring from a SQL literal. Over-reporting a documented drop
        # is the safe direction for a rule about destructive statements.
        _lines = src.splitlines()
        for m in _re.finditer(r"[\"'][^\"'\n]*\bdrop\s+table\b[^\"'\n]*[\"']", src, _re.I):
            _lno = src[: m.start()].count("\n")
            if _lno < len(_lines) and _lines[_lno].lstrip().startswith("#"):
                continue
            # ⚑ `IF EXISTS` IS OPTIONAL AND CASE-VARYING, AND A FIRST CUT MIS-CAPTURED IT — the
            # census reported relations named `IF` and `with`, which is the extractor's failure
            # reported as a fact about the schema. `\s+` around the optional clause, and a `%s`
            # placeholder or an f-string brace yields no name rather than a wrong one.
            rel = _re.search(
                r"drop\s+table\s+(?:if\s+exists\s+)?[\"'`]?([A-Za-z_]\w*)", m.group(0), _re.I
            )
            _nm = rel.group(1) if rel else "?"
            if _nm.lower() in ("if", "with", "exists"):
                _nm = "?"
            ctx = ""
            for pos, nm in fns:
                if pos < m.start():
                    ctx = nm
                else:
                    break
            # ⚑⚑ THE CENSUS MUST NOT COUNT ITSELF. `touching` and this function both hold the
            # literal `drop table` as a SEARCH TERM, and `main` prints it in help text — three
            # rows that are the instrument, not the substrate. Excluding by FUNCTION rather than
            # by file keeps every real drop in `query_defs` visible if one is ever added.
            if ctx in ("touching", "drops", "main") and p.endswith("query_defs.py"):
                continue
            out.append((_nm, os.path.relpath(p, root), src[: m.start()].count("\n") + 1, ctx))
    # ⚑⚑⚑ THE ORDER IS CARRIED ON THE VALUE, NOT DISCARDED (⟡sorted-order). A bare
    # `sorted(set(out))` returns a plain list, so a caller cannot tell it is ordered and
    # re-sorts defensively — measured one hop apart at `agda_defs.py:1732 -> :1757`. `Sorted`
    # declares the order and its combinators REFUSE a mismatch, which is how the requirement
    # reaches the producer that must satisfy it rather than being re-established per consumer.
    #
    # ⚑ A `getter` BECAUSE THESE ARE TUPLES, NOT RECORDS. `SortKey.of` names FIELDS, and a
    # 4-tuple has none; the getter maps the declared key onto positions. The key is the full
    # tuple order (`relation, path, line, function`) because that is what `sorted(set(...))`
    # actually produced — declaring a narrower key would claim an order the value does not have.
    from sorted_stream import Sorted, SortKey

    return Sorted(
        sorted(set(out)),
        SortKey.of("relation", "path", "line", "function"),
        origin="query_defs.drops",
        getter=lambda r: (r[0], r[1], r[2], r[3]),
    )


def touching(table, decl=None):
    """{"columns": [...], "readers": [builder …], "writers": [(path, line, verb) …]}

    ⚑ THE QUESTION A SCHEMA CHANGE ASKS, ANSWERED FROM THE DECLARED MODEL.
    Planning `core_fp`'s shape change I needed "what touches this table, in what
    role" and answered it with grep twice, then classified the 20 hits by READING
    them — a judgement that is not in code and evaporates when the turn ends.

    ⚑ AND `pycodemod --calls` CANNOT ANSWER IT, WHICH IS WHY IT LOOKED LIKE A
    MISSING TOOL RATHER THAN A MISPLACED QUESTION.  A table is not a Python
    callable; it is a `Table` in this module's `MetaData` and a STRING key in
    `INTERN_BUILDERS` — exactly the string-keyed dispatch `--calls` is recorded as
    unsound for (it once reported a live `QB.run(con,"orbit_node_count")` as a
    DEAD CAPABILITY).  My first cut was a tokenizer over SQL string literals in
    `pycodemod`; it was deleted, because the readers are DECLARED here and
    recovering them from text re-derives what the model already states.

    ⚑ THE TWO HALVES ARE ASYMMETRIC BY CONSTRUCTION, and saying so is the point.
    READS are builders — this module is "the SINGLE SOURCE for the project's SQL
    read-queries", so `get_final_froms()` over each `q_*` is complete and exact.
    WRITES are not modelled here at all (`_T` declares columns for SELECT only;
    the docstring says "we never write, only read/intern"), so they are found by
    scanning for the write verbs and reported with their file:line.  A reader
    trusting this must know that asymmetry, so the two are returned under
    different keys with different provenance rather than merged into one list."""
    import glob as _glob
    import re as _re

    t = _MD.tables.get(table)
    cols = [c.name for c in t.columns] if t is not None else []

    # ⚑⚑ THE DECLARATION MODULE IS A PARAMETER, NOT `sys.modules[__name__]` — AND THIS IS THE
    # ONE INTROSPECTION THE 2026-08-12 SPLIT MOVED OUT FROM UNDER. It walked THIS module's
    # namespace for `q_*` names, which is where the builders WERE; they are now in
    # `query_decl`, and the only reason it kept working is that `from query_decl import *`
    # happens to re-bind them here too. That is the hazard's exact signature rather than a
    # reason to leave it: an introspection that resolves relative to "this file" answers about
    # a SMALLER thing after a cut AND STILL PASSES — so it would have gone silently wrong the
    # day someone narrowed the re-export, and it would report a `q_*` defined HERE as a
    # declared reader when the seam says none may be.
    #
    # ⚑ IT IS A PARAMETER RATHER THAN A HARDCODED IMPORT SO THE CLAIM IS TESTABLE. With the
    # module baked in, a case cannot tell "reads the declaration" from "reads whatever
    # namespace it is evaluated in" — the two agree today precisely BECAUSE of the star
    # re-export, so reverting the fix would pass every case. Injecting the module lets
    # `_selftest` hand it one with no builders and require an EMPTY reader set.
    if decl is None:
        import query_decl as decl
    readers, builder_writes, recursive = [], [], []
    # ⚑ COLUMN → the builders that MENTION it, exact from the statement tree (`_columns_of`).
    # A column with an EMPTY set is not referenced by any declared builder — which is the
    # nearest thing to "not load-bearing" this model can assert, and it is an assertion about
    # THE DECLARED BUILDERS, never about the store. Stated that way at the call site too.
    by_col = {c: [] for c in cols}
    for nm in sorted(dir(decl)):
        if not nm.startswith("q_"):
            continue
        fn = getattr(decl, nm)
        if not callable(fn):
            continue
        try:
            stmt = fn()
            froms = _tables_of(stmt)
            wrote = written_table(stmt)
        except Exception:
            continue  # a builder needing params is still a builder; skip probing
        # ⚑⚑ A BUILDER'S WRITE IS NOT A READ, and listing it as one made every dependency edge
        # point relation → builder. `q_ref_insert` appeared under `--touching ref`'s READERS
        # because `_tables_of` walks the whole tree and the INSERT's target is in it. The
        # statement type settles it (`written_table`), so the target is reported as a write and
        # the SELECT half stays a read.
        # ⚑ THE COLUMN SET IS COLLECTED FOR READERS **AND** WRITERS ALIKE — a column an INSERT
        # populates is as load-bearing as one a SELECT filters on, and partitioning the map by
        # role here would make "referenced by nothing" mean two different things per half.
        if table in froms or wrote == table:
            for _c in _columns_of(stmt, table):
                if _c in by_col:
                    by_col[_c].append(nm)
        if wrote == table:
            builder_writes.append(nm)
            # ⚑ A FIXPOINT STEP: it writes what it reads. Counting the DML TARGET as a read would
            # make every INSERT trivially recursive, so the test is whether the table appears
            # more than once in the tree — once as the target, again in the SELECT that feeds it.
            # (A first cut reached for `stmt.select` / `stmt._select`, attribute names I invented;
            # counting occurrences needs no private API.)
            if _table_occurrences(stmt, table) > 1:
                recursive.append(nm)
        elif table in froms:
            readers.append(nm)

    # ⚑ WRITE VERBS, NOT "MENTIONS".  `INSERT`/`UPDATE`/`DELETE`/`DROP` are what a
    # schema change must move together; a SELECT naming the same table is a reader
    # and belongs in the other half.  Scoped to the repo's SQL-writing modules.
    verbs = (
        "insert into",
        "insert or replace into",
        "insert or ignore into",
        "update",
        "delete from",
        "drop table",
    )
    writers = []
    root = os.path.dirname(os.path.dirname(HERE))
    for p in sorted(
        _glob.glob(os.path.join(root, "scripts", "*.py"))
        + _glob.glob(os.path.join(root, "jea", "metalanguage", "*.py"))
    ):
        try:
            src = open(p, encoding="utf-8").read()
        except OSError:
            continue
        for m in _re.finditer(r"[\"'][^\"'\n]*\b%s\b[^\"'\n]*[\"']" % _re.escape(table), src):
            frag = m.group(0).lower()
            hit = next(
                (v for v in verbs if v in frag and frag.index(v) < frag.index(table.lower())), None
            )
            if hit:
                writers.append((os.path.relpath(p, root), src[: m.start()].count("\n") + 1, hit))
    # ⚑⚑⚑ `recursive` IS ITS OWN KEY BECAUSE A SELF-REFERENCE IS NOT AN EDGE PAIR. A builder that
    # READS the relation it WRITES is a FIXPOINT step — `q_pack_level_insert` reads `obs_node` to
    # find its children's ids and writes `obs_node` with the parents', which is exactly why the
    # fold runs level-by-level instead of as one statement. Reporting that as one read edge plus
    # one write edge loses the fact and hands a graph layout a CYCLE it must break arbitrarily.
    #
    # ⚑⚑ AND IT IS DERIVED, NOT DECLARED. The recursion is `written_table(stmt) in _tables_of
    # (stmt)` — a property of the statement, so a builder that becomes recursive says so without
    # anyone updating a list. Three keys, three provenances: `readers` exact from the tree,
    # `builder_writes` exact from the statement type, `writers` a verb scan over text.
    return {
        "columns": cols,
        "readers": readers,
        "by_column": {c: sorted(set(v)) for c, v in by_col.items()},
        "builder_writes": sorted(set(builder_writes)),
        "recursive": sorted(set(recursive)),
        "writers": sorted(set(writers)),
    }


def _selftest():
    """⚑⚑ THIS MODULE HAD NO SUITE AT ALL, AND `run_selftests --list` COUNTED IT ANYWAY —
    69 discovered, 68 reporting, one SILENT. A silent suite is worse than an absent one: it
    occupies a row in the census while asserting nothing, so the ratio reads green over a
    denominator that quietly excludes it.

    ⚑⚑ AND ITS ABSENCE IS EXACTLY WHY THE RE-EXPORT HAZARD HAD NO GUARD. `import *` skips a
    leading underscore by construction; the same cut on `schema.py` silently took `_node`,
    `_unit`, `_unit_cod` and `_orbit_def` off that module's surface while `--selftest` still
    read 123/123 and every consumer's suite still passed. Most cases never touch most names,
    so a vanished attribute surfaces at the first consumer that reads it — a different run,
    on a different day.

    ⚑ THE SURFACE IS ASKED DIRECTLY, NEVER INFERRED FROM A PASS, and it is resolved on the
    live MODULE OBJECT rather than scanned in source text. A retirement note naming a deleted
    function satisfies a substring scan — this tree has TWO recorded incidents of exactly
    that — so `getattr` on `sys.modules[__name__]` is the anchor: it answers "does this name
    resolve HERE, now", which is the question a consumer will ask.
    """
    import contextlib as _cl
    import io as _io

    cases = []

    def check(label, got, want):
        cases.append((label, got == want, got, want))

    _me = sys.modules[__name__]

    # ── (1) every compiled builder is reachable THROUGH this module ──────────────────────
    # ⚑ THE POPULATION IS `INTERN_BUILDERS`, NOT A HAND-WRITTEN ROSTER. A second list of
    # builder names beside the one that IS the registry would be the frozen-roster shape:
    # it can only be as current as its last edit, and a builder added to `query_decl` and
    # forgotten here is precisely the case this must catch.
    _unreachable = sorted(
        n
        for n, fn in INTERN_BUILDERS.items()
        if getattr(fn, "__name__", "<lambda>") != "<lambda>" and not hasattr(_me, fn.__name__)
    )
    check("every INTERN_BUILDERS builder resolves on query_defs", _unreachable, [])

    # ── (2) the MEASURED consumer surface — `pycodemod --importers query_defs` ───────────
    # ⚑ THIS LIST IS NOT INVENTED: it is what five files actually reach today
    # (`query_builders`, `query_registry`, `sql_lift`, `numpy_builders`, `sppf_db`). A name
    # dropped here breaks a consumer at ITS next run, which no suite in this file would see.
    _consumed = (
        "run",
        "INTERN_BUILDERS",
        "q_reach",
        "q_edges_dst_distinct",
        "q_indegree_top",
        "FREE_CTORS",
    )
    check(
        "the measured consumer surface resolves",
        sorted(n for n in _consumed if not hasattr(_me, n)),
        [],
    )

    # ── (3) the `_`-prefixed declaration names — the half `import *` cannot carry ────────
    # ⚑ THE LEADING UNDERSCORE ON A TABLE MEANS "RAW, PRE-QUOTIENT", NOT "PRIVATE": `_node`
    # is the base relation under the `node` compat VIEW of the same name. Published
    # vocabulary that merely LOOKS private to the star — which is why it needs a case.
    _priv = (
        "_MD",
        "_T",
        "_store",
        "_node",
        "_unit",
        "_unit_cod",
        "_orbit_def",
        "_structs",
        "_members",
        "_member_heads",
        "_refs",
        "_edges",
        "_module_edges",
        "_modules",
        "_live_cores",
        "_rebuilt_obs",
        "_rebuilt_edges",
        "_rebuilt_edges_from_durable",
        "_stored_edges",
    )
    check(
        "every `_`-prefixed declaration name resolves too",
        sorted(n for n in _priv if not hasattr(_me, n)),
        [],
    )

    # ── (4) ⟡sql-lift — THE PACKING FOLD'S EQUIVALENCE MACHINERY ────────────────────────────
    # ⚑⚑ THE ARMS MUST EXIST AND MUST BE COMPARABLE. `--equiv pack.sql pack.python` is the gate
    # that licenses replacing the python packing loop; if either arm silently disappears the
    # gate passes vacuously by comparing nothing to nothing — which is precisely what
    # `do_equiv`'s both-empty refusal exists to catch, and this case guards the layer above it.
    check(
        "both packing-fold arms are registered",
        sorted(n for n in ("pack.sql", "pack.python") if n not in REFERENCE_ARMS),
        [],
    )
    # ⚑ ARRAY ROWS MUST SURVIVE `_run_named`'s NORMALISATION. The partition arms return an ARRAY
    # of member ids per class, psycopg hands that back as a python `list`, and `do_equiv`
    # compares by `set()` — so before this was frozen to tuples the comparison raised
    # `TypeError: unhashable type: 'list'`. A crash is the loud failure; the case pins the fix.
    # ⚑ ASSERTED ON BEHAVIOUR, NOT ON THE DOCSTRING. A first cut checked that `_run_named.__doc__`
    # CONTAINED the word "unhashable" — a guard satisfied by its own commentary, which is the
    # exact class this repo has recorded three times (a case matching the prose that explains it).
    # What must hold is that an array-bearing row can enter a `set()`.
    check(
        "an array-bearing row normalises to something hashable",
        isinstance(
            hash(tuple(tuple(x) if isinstance(x, list) else x for x in ("k", ["1", "2"]))), int
        ),
        True,
    )
    # ⚑ AND THE PARAM OVERRIDE, without which both arms run on `core_id=''` and compare two
    # EMPTY sets — a "pass" that measures nothing. Measured: `--scans pack_level` reported
    # "0 loop-adjusted row(s) read" over a 184,278-row store until `--param` existed.
    # ⚑ The case DRIVES it: a first cut asserted `is not None`, which no implementation can fail.
    _sv = sys.argv
    try:
        sys.argv = ["query_defs.py", "--param", "core_id=3253", "--param", "ht=2"]
        _ov = _override_params({"core_id_1": "", "ht_1": 0})
    finally:
        sys.argv = _sv
    check("--param overrides a compiled default by name-suffix", _ov.get("core_id_1"), "3253")
    check("...and coerces to the default's type (int stays int)", _ov.get("ht_1"), 2)
    # ⚑⚑ THE DISCRIMINATION BUILDER MUST COVER EVERY SIGNATURE COMPONENT, or a verdict can be
    # blind on a field nobody is told about. `q_pack_level`'s key is
    # (ctor_id, qname_pid, idx, lit_id, children) — five components — and `q_pack_discrimination`
    # must report a count for each. A component added to the key and not to the census is one
    # whose omission becomes undetectable AGAIN, which is the exact defect this pair exists to
    # close: dropping `idx` passed three IDENTICAL verdicts.
    _disc_cols = [c.name for c in q_pack_discrimination().selected_columns]
    check(
        "the discrimination census covers every signature component",
        sorted(n for n in ("ctors", "qnames", "idxs", "lits", "kid_shapes") if n not in _disc_cols),
        [],
    )
    check(
        "...and reports the population it measured (n), not only the counts",
        "n" in _disc_cols,
        True,
    )

    # ── (4) the compiled cache is not stale ─────────────────────────────────────────────
    # ⚑ `do_check()` IS THE GATE ITSELF, RUN — not a re-implementation of it. It recompiles
    # every builder in memory and diffs against the committed `query_sql_postgres.py`, so
    # this case says "the SQL this tree would generate is the SQL it has committed", which
    # is the one statement that survives a module split unchanged.
    _buf = _io.StringIO()
    with _cl.redirect_stdout(_buf), _cl.redirect_stderr(_buf):
        _fresh = do_check()
    check("--check reports NO DRIFT against the committed cache", _fresh, True)

    # ── (5) `touching` still reads the DECLARATION, after the split moved it ─────────────
    # ⚑ THE INTROSPECTION HAZARD, AS A CASE. `touching` walked `dir(sys.modules[__name__])`
    # for `q_*` names; the 2026-08-12 split moved every one of them to `query_decl`, and it
    # kept working ONLY because the star re-export re-bound them here. That is the hazard's
    # signature — an introspection that answers about a smaller thing and still passes — so
    # it now names `query_decl`, and this pins that it finds a real reader rather than [].
    # ⚑⚑ ASSERTED AS MEMBERSHIP, NOT AS AN EXACT LIST — the case's own stated intent is *"pins
    # that it finds a real reader rather than []"*, and `== ["q_edge_all"]` also pinned the
    # reader set's SIZE, which is data. When `touching` learned to walk CTEs (2026-08-15) `edge`
    # went from 1 reader to 16 and this case failed on a WIDENING. A case that fails when the
    # instrument improves is asserting the instrument's limits.
    check(
        "touching() finds the declared reader of `edge`",
        "q_edge_all" in touching("edge")["readers"],
        True,
    )
    # ⚑⚑⚑ AND THE WIDENING IS PINNED IN ITS OWN RIGHT. Readers were resolved by
    # `get_final_froms()` — the OUTERMOST froms — so a builder scanning a table inside a CTE was
    # invisible: `--touching obs` reported ONE reader where fifteen exist. `_tables_of` walks the
    # statement tree (`sqlalchemy.sql.visitors.iterate`), which is possible at all because the
    # builders are Core objects rather than SQL strings.
    check(
        "...and a builder reading THROUGH A CTE is resolved too",
        "q_pack_level" in touching("obs")["readers"],
        True,
    )
    # ⚑ THE CONTROL: a walk that returned every table for every builder would pass the case
    # above. `q_edge_all` scans `edge` alone and must not acquire unrelated relations.
    # ⚑ THE CONTROL RELATION MOVED `orbit_node` → `_node` (2026-08-23). `orbit_node` was
    # removed with its tier, which would have made this case pass VACUOUSLY: an undeclared
    # relation has no readers at all, so the assertion would hold for reasons unrelated to
    # what it tests. The next case already covers the undeclared path. `_node` is a live
    # relation that `q_edge_all` genuinely does not read, so the control still discriminates.
    check(
        "...while a single-table builder gains no relations it does not read",
        "q_edge_all" in touching("_node")["readers"],
        False,
    )
    check(
        "...and an undeclared table reports no columns and no readers",
        (touching("no_such_relation")["columns"], touching("no_such_relation")["readers"]),
        ([], []),
    )
    # ⚑⚑ THE CASE THAT DISCRIMINATES THE REPAIR, AND WITHOUT IT THERE IS NONE. Reverting
    # `touching` to `sys.modules[__name__]` passes every case above — the two namespaces
    # agree TODAY because the star re-export binds every `q_*` here as well. So the claim
    # "the readers come from the DECLARATION" is unfalsifiable unless the declaration can be
    # substituted: hand it a module object with no builders in it and the reader set must be
    # EMPTY. Under the pre-split spelling it would answer `['q_edge_all']` from this file's
    # own namespace and the case fires.
    _empty = type(sys)("empty_decl")
    check(
        "readers come from the DECLARATION module, not this namespace",
        touching("edge", decl=_empty)["readers"],
        [],
    )

    # ── (6) the COLUMN refinement — `_columns_of` ────────────────────────────────────────
    # ⚑⚑ THE MOTIVATING CASE, PINNED AS A CASE. "Is this column load-bearing?" was answered by
    # reading SQL; `terms` is load-bearing for the RETIRE LICENCE (`q_drainable_res`) and nothing
    # said so. This asserts the licence appears against a real column, so the mode cannot silently
    # stop resolving the one relation it was built for.
    _tc = touching("terms")
    check(
        "by_column names the RETIRE LICENCE against terms.text",
        "q_drainable_res" in _tc["by_column"].get("text", []),
        True,
    )
    # ⚑⚑⚑ THE ALIAS REGRESSION, AND IT IS THE CASE THAT ACTUALLY DISCRIMINATES. The first cut
    # tested `isinstance(Column.table, Table)`, which is FALSE for every aliased join — `q_fanin`
    # joins `terms` four times as `k`/`r`/`l`/`o`. It reported 3 per-column readers against 23
    # relation-level ones and OMITTED the licence, i.e. it under-reported in the direction that
    # licenses a drop. Every other case here passes under that bug. Equality with the relation-
    # level reader set is the assertion, because a column map that is a strict subset of `readers`
    # for reasons nobody stated is exactly the failure that shipped.
    check(
        "...and an ALIASED join is resolved, so no reader is lost to the column map",
        sorted(set(_tc["by_column"]["term_id"]) | set(_tc["by_column"]["text"])),
        sorted(_tc["readers"]),
    )
    # ⚑ THE CONTROL: a walk that credited every column to every reader would pass both cases
    # above. `obs_node.ch` is read by a genuine MINORITY (the drain licence and the
    # reconstruction check), so a column map that does not discriminate fires here.
    _oc = touching("obs_node")["by_column"]
    check(
        "...while a column read by a MINORITY is not credited to every reader",
        len(_oc["ch"]) < len(_oc["core_id"]),
        True,
    )
    # ⚑ AND AN UNDECLARED RELATION HAS AN EMPTY MAP, not a missing key — the caller iterates it.
    check(
        "...and an undeclared table reports an empty column map",
        touching("no_such_relation")["by_column"],
        {},
    )

    failed = [c for c in cases if not c[1]]
    for label, _ok, got, want in failed:
        print("  FAIL %s: got %r want %r" % (label, got, want))
    print("selftest: %d/%d" % (len(cases) - len(failed), len(cases)))
    return 0 if not failed else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--touching", metavar="TABLE", help="what reads/writes a table, from the declared model"
    )
    # ⚑ ⟡no-automated-drop — `--touching` verb-scans for `drop table` ONE RELATION AT A TIME and
    # attributes nothing; this asks the whole corpus and reports the ENCLOSING FUNCTION, which is
    # the unit the singleton/automated judgement is made on.
    ap.add_argument(
        "--drops",
        action="store_true",
        help="every DROP TABLE with its caller — a drop must be a SINGLETON op",
    )
    ap.add_argument(
        "--sql",
        metavar="NAME",
        help="the COMPILED SQL for one builder — what the engine actually runs",
    )
    # ⚑⚑ "HOW MUCH OF WHICH RELATION DOES THIS BUILDER READ" HAD NO MODE, and its absence is
    # what made an O(durable-tier) term in the drain licence invisible for the life of the
    # query: `--sql` shows the TEXT, `--verify` shows the RESULT ROWS, and neither shows the
    # INPUT the plan consumes to produce them.
    #
    # ⚑ THE MODE THAT ALMOST SHIPPED HERE WAS `--cost NAME…`, PRINTING ELAPSED SECONDS, and
    # it was deleted rather than kept alongside (user, 2026-08-12: *"NEVER rely on wall
    # clock; CPU saturation will always be a wildcard, and it introduces TOCTOUs that
    # confound the measurements"*). Keeping a discredited instrument beside the right one
    # does not make the right one preferred — it makes the wrong one AVAILABLE, and the
    # cheaper reach wins under pressure. The whole reason the defect below was diagnosable
    # at all is that somebody read a 1.0 → 35.3 s series as a SHAPE; the shape was right and
    # the numbers were never evidence.
    ap.add_argument(
        "--equiv",
        nargs=2,
        metavar=("A", "B"),
        help="do two builders return the SAME SET? — the clock-free equivalence gate",
    )
    ap.add_argument(
        "--equiv-sweep",
        nargs=2,
        metavar=("A", "B"),
        help="--equiv at EVERY height of one core (--param core_id=…) — three "
        "samples are not a sweep; each level's discrimination is checked so a "
        "PASS on a level that could not have failed is reported, not counted",
    )
    ap.add_argument(
        "--explain",
        metavar="NAME",
        help="EXPLAIN (ANALYZE) one builder — WHY it costs what --cost reports",
    )
    # ⚑ THE FLAG THE DISPATCH ALREADY EXPECTED. `main` has read `a.rows` with nothing declaring
    # it and no `do_rows` defined, so argparse rejected `--rows` before the NameError could fire —
    # a half-built mode that failed as a USAGE error, which reads like "no such capability"
    # rather than "unfinished". `--calls do_rows`: 0 def, 1 call.
    ap.add_argument(
        "--rows",
        metavar="NAME",
        help="RUN a builder and print its ROWS — the mode that shows a RESULT",
    )
    # ⚑ THE HELP NOW SAYS IT EXECUTES.  It read *"which relations a builder READS, rows×loops
    # each"* — which a reader takes for inspection — and the mode runs `EXPLAIN ANALYZE`.  A
    # name is what you reach BY, so the warning belongs where the name is, not one line down.
    ap.add_argument(
        "--scans",
        metavar="NAME",
        help="which relations a builder READS, rows×loops each — O(live) or "
        "O(durable)? ⚑ EXECUTES the builder (EXPLAIN ANALYZE); "
        "add --estimate to plan only",
    )
    ap.add_argument(
        "--estimate",
        action="store_true",
        help="--scans: report the PLANNER'S estimate and execute NOTHING "
        "(EXPLAIN without ANALYZE) — no `actual rows`, no spill",
    )
    # ⚑ `--param k=v` — BIND A PARAMETERIZED BUILDER TO REAL DATA. Without it `--explain` and
    # `--scans` measure the builder's REPRESENTATIVE default (`core_id=''`), i.e. a plan over
    # zero rows reported in the shape of an answer about the corpus. Measured: `--scans
    # pack_level --sandbox` printed "0 loop-adjusted row(s) read" against 184,278 obs. See
    # `_override_params`.
    ap.add_argument(
        "--param",
        action="append",
        metavar="K=V",
        default=[],
        help="bind a builder param for --explain/--scans (repeatable): --param core_id=3253",
    )
    ap.add_argument(
        "--sandbox",
        action="store_true",
        help="--cost/--equiv against the THROWAWAY tenant, never the corpus",
    )
    # ⚑ `--live` EXISTS SO THE TENANT IS SAYABLE, and it is deliberately NOT read here.
    # `store.tenant` resolves it from `sys.argv` (via `_cost_connect`); declaring it only
    # stops argparse refusing the flag before the resolver ever sees it — which is exactly
    # how this tool failed `--selftest --live` under ⟡tenant-mandatory. An option that does
    # not exist cannot be stated, and "no flag" then silently MEANT live.
    ap.add_argument(
        "--live", action="store_true", help="the CORPUS tenant — mandatory counterpart to --sandbox"
    )
    ap.add_argument(
        "--compile", action="store_true", help="(re)generate query_sql.py from the builders"
    )
    ap.add_argument(
        "--check", action="store_true", help="drift gate: assert query_sql.py matches the builders"
    )
    ap.add_argument(
        "--verify", action="store_true", help="assert each builder's rows == its original raw SQL"
    )
    ap.add_argument("--only", nargs="*", help="verify only these builder names")
    # ⚑ `--selftest` IS THE MODE `run_selftests` WAS ALREADY LOOKING FOR. It discovered this
    # file (69 of 69) and got no `selftest: N/N` line back, so the run reported it SILENT —
    # a row in the census asserting nothing, which reads as coverage while being its absence.
    ap.add_argument(
        "--selftest",
        action="store_true",
        help="the re-export surface + the cache-drift gate, as cases",
    )
    # ⚑⚑ `--db` IS GONE WITH SQLITE (⓺, 2026-08-11), AND IT WAS THE ONE MODE THAT COULD
    # DISAGREE WITH ITSELF. Every other path in this module asks the authority
    # (`_store.dialect` when compiling, `_store.backend` in the cache messages), but
    # `--verify` compiled for the AMBIENT backend and then executed against
    # `sqlite3.connect(a.db)` — so it compared postgres-compiled Core SQL to sqlite raw
    # SQL on a sqlite cursor and called the result a builder equivalence.
    ap.add_argument(
        "--group",
        default="catalog",
        help="builder group to verify: catalog (default, the SPPF db) | render | orbit | all",
    )
    a = ap.parse_args()
    if a.selftest:
        sys.exit(_selftest())
    if a.sql:
        # ⚑ "WHAT DOES THIS BUILDER ACTUALLY COMPILE TO" HAD NO MODE, and it is the question
        # a Core expression most needs answered — the whole point of composing in Python is
        # that the SQL is generated, so reading it is how you check the generation. Without
        # this the only route was a `python3 -c` importing the generated cache, which the
        # no-chaining hook correctly refuses: the judgement would live in the turn.
        #
        # ⚑ FROM THE BUILDER, NOT THE CACHE. Compiling live means the answer cannot be stale
        # — a cache read would show what `--compile` last wrote, which is exactly the drift
        # `--check` exists to detect. If the two disagree, `--check` is the mode that says so.
        sql, params = _compile_one(_named_builder(a.sql)())
        print(sql)
        if params:
            print("\n-- baked defaults: %r" % (params,))
        raise SystemExit(0)
    if a.touching:
        r = touching(a.touching)
        if not r["columns"]:
            print(f"{a.touching}: NOT DECLARED in this module's model (so no builder can read it)")
        else:
            print(f"{a.touching}({', '.join(r['columns'])})")
        # ⚑ BOTH HALVES, ALWAYS, WITH THEIR PROVENANCE.  Printing only the side
        # that is non-empty reads as the whole population — the tally-without-a-
        # denominator defect this repo has recorded four times.
        print(f"  readers ({len(r['readers'])}) — DECLARED builders, exact:")
        for nm in r["readers"]:
            print(f"      {nm}")
        # ⚑⚑ BUILDER WRITES ARE THEIR OWN CATEGORY, AND THEY WERE FILED UNDER `readers` UNTIL
        # 2026-08-15. `_tables_of` walks the whole tree, so an `INSERT INTO ref SELECT …` put
        # `ref` among its tables and `q_ref_insert` read as a READER of the relation it fills.
        # Every dependency then pointed relation → builder, and a graph drawn from them had no
        # flow at all — nothing ever came OUT of a builder.
        print(f"  builder writes ({len(r['builder_writes'])}) — DECLARED DML, exact:")
        for nm in r["builder_writes"]:
            mark = "   ⚑ RECURSIVE — reads what it writes" if nm in r["recursive"] else ""
            print(f"      {nm}{mark}")
        print(f"  writers ({len(r['writers'])}) — verb-scanned, file:line:")
        for p, ln, verb in r["writers"]:
            print(f"      {p}:{ln}  {verb}")
        # ⚑⚑ THE COLUMN REFINEMENT. `readers` answers "does anything touch this RELATION"; a
        # schema change asks it one level down, and until now that level was a judgement made by
        # reading SQL. Exact from the statement tree (`_columns_of`), so it needs no store, no
        # bound param and no tenant — see that function on why the plan is the WEAKER instrument.
        _bc = r.get("by_column") or {}
        if _bc:
            _un = sorted(c for c, v in _bc.items() if not v)
            print(f"  by column ({len(_bc)}) — DECLARED builders mentioning each, exact:")
            for _c in r["columns"]:
                _v = _bc.get(_c, [])
                print(f"      {_c:<12} {len(_v):>2}  {', '.join(_v) if _v else '— none'}")
            # ⚑⚑⚑ AND THE ZERO ROWS ARE NAMED AGAIN RATHER THAN LEFT TO BE COUNTED OFF THE TABLE.
            # "No declared builder mentions this column" is the sentence a drop gets justified
            # with, so it is printed as a sentence — with its scope attached, because the claim
            # is about THE DECLARED BUILDERS and a raw `con.execute` elsewhere is outside it.
            if _un:
                print(
                    f"  ⚑ {len(_un)} column(s) mentioned by NO declared builder: {', '.join(_un)}"
                )
                print("     This is a fact about the DECLARED BUILDER LAYER, never about the")
                print("     store: a raw `con.execute` (see `pycodemod --rawreads`) reads columns")
                print("     this model cannot see. Not a licence to drop — a place to look.")
        print("  ⚑ THREE PROVENANCES, NOT TWO. `readers` and `builder writes` are EXACT — the")
        print("     first from the statement tree, the second from the statement TYPE. `writers`")
        print("     is a verb scan over source text, so a write via an unlisted spelling is")
        print("     missed. A RECURSIVE builder writes the relation it also reads: that is a")
        print("     FIXPOINT step, not two independent edges, and it is why such a fold runs")
        print("     level-by-level rather than as one statement.")
        return
    if a.drops:
        # ⚑ MATERIALIZED ONCE, AND SAID WHY — `Sorted` is SINGLE-PASS by construction (*"a stream
        # is single-pass. Materialize it with list() if you need it twice, and say why."*). This
        # report iterates the rows AND then prints their count, which is two passes; the list is
        # the honest form and the declaration above still names the order for any other consumer.
        _d = list(drops())
        for _rel, _p, _ln, _fn in _d:
            print("  %-16s %s:%d  in %s" % (_rel, _p, _ln, _fn or "<module>"))
        print(
            "\n%d `DROP TABLE` site(s) — ⟡no-automated-drop: a drop takes AccessExclusiveLock,\n"
            "so each must belong to a SINGLETON operation (setup/teardown), never to an\n"
            "automated or per-item path. The enclosing function is the reviewable unit.\n"
            "⚑ VERB-SCANNED: reports what it FOUND under these spellings, never that there\n"
            "  are no others — a drop built from a variable or an f-string is invisible here."
            % len(_d)
        )
        sys.exit(0)
    if a.rows:
        sys.exit(0 if do_rows(a.rows, a.sandbox) else 1)
    if a.scans:
        sys.exit(0 if do_scans(a.scans, a.sandbox) else 1)
    if a.explain:
        sys.exit(0 if do_explain(a.explain, a.sandbox) else 1)
    if a.equiv:
        # ⚑ EXIT CODE, NOT JUST A PRINT. `--equiv` answers a question whose wrong answer
        # licenses a DELETE, so it is a GATE in the shape of `--check`: a caller (or a
        # pre-commit hook) can act on it without parsing the output.
        sys.exit(0 if do_equiv(a.equiv[0], a.equiv[1], a.sandbox) else 1)
    if a.equiv_sweep:
        # ⚑ THE CORE COMES FROM `--param core_id=…`, the same channel the arms bind through —
        # a separate flag would be a second spelling of one fact, free to disagree with the one
        # the builders actually read.
        _cid = _override_params({"core_id_1": ""}).get("core_id_1")
        if not _cid:
            raise SystemExit(
                "--equiv-sweep needs a core: --param core_id=<id>  "
                "(`schema.py --live --packed` names the COMPARABLE ones)"
            )
        sys.exit(0 if do_equiv_sweep(a.equiv_sweep[0], a.equiv_sweep[1], _cid, a.sandbox) else 1)
    if a.compile:
        do_compile()
        return
    if a.check:
        sys.exit(0 if do_check() else 1)
    if a.verify:
        # ⚑⚑⚑ THIS READ `_store.connect(mode="ro")` — HARDCODED LIVE, IGNORING `--sandbox`,
        # while every sibling mode above threads `a.sandbox` into its resolver. So
        # `--verify --sandbox` opened the CORPUS and said nothing: the flag was accepted,
        # printed nothing, and changed nothing. That is `wrong-tenant-read-is-silent`
        # (*"a per-dispatch --sandbox drifts so READ modes ignore it silently"*) landing in
        # THE MIGRATION GATE — the one place whose verdict licenses replacing a statement.
        #
        # ⚑ MEASURED, not inferred: `--verify --only dec_answer --sandbox` raised
        # `UndefinedTable: relation "core_decoded_shadow" does not exist` — the sandbox HOLDS
        # that view, so the failure names the tenant it actually reached. A read that had
        # happened to succeed would have compared the wrong store's rows and PASSED.
        # ⚑ `_cost_connect` IS THIS MODULE'S OWN RESOLVER — the one `--cost`, `--explain`,
        # `--scans`, `--rows` and `--equiv` all route through. Reused rather than re-spelled:
        # a second per-dispatch tenant line is the exact defect being repaired.
        con = _cost_connect(a.sandbox)
        grp = None if a.group == "all" else a.group
        sys.exit(0 if verify(con, set(a.only) if a.only else None, grp) else 1)
    ap.print_help()


# selftest-tenant: sandbox
# ⚑ ⟡tenant-pragma — `run_selftests._tenant` reads this and appends the flag. `store.tenant`
# exits 2 on an unstated tenant since ⟡tenant-mandatory (2026-08-24); SANDBOX because a suite
# that reaches the LIVE store can corrupt the corpus it exists to check.
# ⚑⚑ THIS FILE IS `sql-F23`'s WITNESS: its `_cost_connect` held an inlined
# `sandbox_connect(…) if … else connect(…)` and declared no `--live` at all, so its tenant was
# UNSAYABLE and invisible to `--calls tenant`. Repaired under ⟡tenant-mandatory. The pragma is
# the declared half of the same fact — a reader should not have to infer it from a helper.
if __name__ == "__main__":
    main()
