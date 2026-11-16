# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The relations the compiled query builders read, as SQLAlchemy `Table` handles (W39c, cut 1).

⚑⚑ CLEANROOMED FROM `jea/metalanguage/query_decl.py`, NOT WRAPPED (operator, 2026-09-25: *"This is
the kind of file that we cleanroom, decomposing as we do so … first we have to replicate the
functionality"*). The origin carries 317 findings and the per-file gate refuses every edit to it,
so the query-cache gate cannot be repaired there. This is the bottom layer every builder stands on:
one `MetaData`, and one `Table` per relation. `query_tables_selftest` checks it against the
origin, relation by relation, so the replica is verified rather than believed.

⚑ EVERY COLUMN IS A STRING, BY THE ORIGIN'S RULE: this layer READS and interns, never writes
through these handles, so the declared type only has to compile to the right SQL text. The real
types are `schema_decl`'s to state. A `dec_node` reader who learns the child space from these
handles alone learns it wrong: under `LEAF(s, 0)` the `c1` slot holds a `dec_scalar.id`, under
every other head a `dec_node.id`. That pun is documented at `schema_decl`, its authority.

⚑ NO `sys.path` INSERT AND NO `store` IMPORT. The origin reaches `store` by prepending its own
directory to `sys.path`; nothing on this layer needs a connection, so the replica needs neither.
"""

from __future__ import annotations

from sqlalchemy import Column, MetaData, Table
from sqlalchemy.sql.type_api import TypeEngine

# ⚑ THE REFERENTIAL CTORS. The origin records this as the THIRD spelling (`jea_agdai` holds a
# function-local `FREE`, `sppf_db` a module copy, `scope_fix` imports `_FREE_CTORS` elsewhere);
# a shared NAME is not a shared authority, and consolidating them onto one is still owed.
FREE_CTORS = frozenset({"Def", "Con", "Prim", "PrimSort", "Proj", "PCon", "PDef", "PProj"})

# The one catalogue every handle below is registered in.
METADATA = MetaData()


class StringType(TypeEngine[object]):
    """The origin's `String` column type, parameterised at the top type so a table type-checks.

    ⚑ `Table` takes `Column[object]` and `Column` is invariant, so a `Column[str]` from the real
    `String` cannot be passed (mypy, measured). `sql_statement_selftest` records the same seam and
    this is its precedent: a `TypeEngine[object]` that COMPILES as the real type, because the
    compiler dispatches on `__visit_name__`, not on the Python class.
    """

    __visit_name__ = "string"
    # ⚑ READ BY THE DDL COMPILER (`visit_string` renders `VARCHAR(length) COLLATE …`), so they
    # exist with the real `String`'s defaults; without them a `CREATE TABLE` raises.
    length: int | None = None
    collation: str | None = None


class IntegerType(TypeEngine[object]):
    """The origin's `Integer`, at the top type for the same invariance reason as `StringType`."""

    __visit_name__ = "integer"


class ArrayType(TypeEngine[object]):
    """The origin's `ARRAY(String)`: postgres compiles it as `item_type` + `[]` per dimension.

    ⚑ `item_type` AND `dimensions` ARE WHAT `visit_ARRAY` READS (`dialects/postgresql/base.py`),
    so the stand-in carries exactly those; `dimensions=None` renders one `[]`, as the origin's does.
    """

    __visit_name__ = "ARRAY"

    def __init__(self, item_type: TypeEngine[object], dimensions: int | None = None) -> None:
        """Hold the element type and the dimension count the compiler reads."""
        self.item_type = item_type
        self.dimensions = dimensions


def table(name: str, *columns: str) -> Table:
    """Declare relation `name` with `columns`, each a string column, in `METADATA`."""
    return Table(name, METADATA, *[Column(c, StringType()) for c in columns])


# ── base tables ─────────────────────────────────────────────────────────────────────────────────
path_text = table("path_text", "path_id", "text")
terms = table("terms", "term_id", "text")
path_seg = table("path_seg", "path_id", "ord", "seg_term_id")
unit = table(
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
unit_cod = table("_unit_cod", "unit_id", "cod_ctor_id", "cod_qname_pid")
node = table("_node", "node_id", "kind_id", "role_id", "op_term_id", "op_path_id", "lit_id")
node_child = table("node_child", "node_id", "ord", "child_id")
unit_node = table("unit_node", "unit_id", "node_id")
unit_member = table("unit_member", "unit_id", "ord", "member_name_pid", "member_unit_id")
# ⚑ `seq` IS THE QUEUE'S ENTIRE COORDINATE; a model omitting it forced every queue-shaped
# question into raw SQL elsewhere (the origin's note).
obs = table("obs", "core_id", "local_id", "ekey", "seq")
event = table("event", "ekey", "ctor_id", "qname_pid", "idx", "lit_id")
unit_obs = table(
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
edge = table("edge", "core_id", "plid", "ord", "clid")
meta = table("meta", "key", "value")
orbit_def = table("_orbit_def", "unit_id", "type_key", "graded_key", "residue", "stab")
core_fp = table("core_fp", "core_id", "mtime")
# ⚑ THE ADDRESSING INDEX + THE CHILD FIBRE (Ⓒ1): what makes `determined` a query.
obs_node = table("obs_node", "core_id", "local_id", "node_id", "ch")
ref = table("ref", "core_id", "plid", "qname_pid", "arg_ord", "arg_lit_id")

# ── the DECODE TIERS (⟡dec-model): tree / treestage / valstage / vocab ──────────────────────
dec_node = table("dec_node", "head", "c1", "c2", "id")
dec_root = table("dec_root", "core_id", "relpath", "mtime", "producer", "root")
dec_stage = table(
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
dec_ref = table("dec_ref", "core_id", "sid", "ord", "kind", "head", "c1", "c2")
dec_val = table("dec_val", "id", "v")
dec_scalar = table("dec_scalar", "id", "v")
# ⚑ `core_decoded` IS THE TIER BEING RETIRED, declared because the drain licence is a statement
# ABOUT it; `core_decoded_shadow` is a VIEW declared in `schema_decl.SHADOWS`, modelled here as a
# table of its output columns.
core_decoded = table("core_decoded", "core_id", "relpath", "mtime", "producer", "dec")
core_decoded_shadow = table("core_decoded_shadow", "core_id", "relpath", "mtime", "producer", "dec")

# ── the reuse catalogue (cut 2a) ────────────────────────────────────────────────────────────────
# Base tables backing the compat VIEWS — where the `path_text.path_id` breadth lives.
structs = table("_structs", "qname_pid", "name_id", "kind_id", "module_pid", "desc_id", "root")
members = table("_members", "struct_qname_pid", "struct_root", "name_id", "ord")
member_heads = table("_member_heads", "struct_qname_pid", "struct_root", "head_id")
refs = table("_refs", "struct_qname_pid", "ref_qname_pid")
edges = table("_edges", "src_pid", "dst_pid")
module_edges = table("_module_edges", "src_pid", "dst_pid")
modules = table("_modules", "module_pid", "purpose_id", "is_index")
# ⚑ THE COMPAT VIEWS AS OUTPUT-COLUMN TABLES, so a builder can SELECT straight from them to
# reproduce render rows (⟡rewire-catalog-render) — distinct from the simplified `v_*` interning
# models, which rebuild the same answers over the base tables above.
structs_v = table("structs", "qname", "name", "kind", "module", "fp", "desc", "root", "unhold_fp")
edges_v = table("edges", "src", "dst")
modedges_v = table("module_edges", "src", "dst")
modules_v = table("modules", "module", "purpose", "is_index")
indegree_v = table("in_degree", "qname", "deg")

# ── per-connection scratch shapes (cut 2c) ──────────────────────────────────────────────────────
# ⚑ ON A PRIVATE `MetaData`, NEVER `METADATA`, as in the origin: the shared catalogue is what
# `--census`/`--ddl` read, and registering a per-connection, per-core disposable there would make it
# read as a declared tier the store "holds". Typed columns, because builders join them exactly as
# they join the CTEs they stand in for.

# The per-core height map `pack_core_sql` materialises once per core.
HT_MAP = "_ht_map"
ht_map = Table(
    HT_MAP,
    MetaData(),
    Column("core_id", StringType()),
    Column("local_id", IntegerType()),
    Column("ht", IntegerType()),
)

# The per-LEVEL signature table: a CTE cannot be ANALYZEd and a table can, which is the whole cost
# (the origin measured a 24,000x cardinality underestimate on the CTE form).
SIG_TBL = "_sig_lvl"
sig_level = Table(
    SIG_TBL,
    MetaData(),
    Column("core_id", StringType()),
    Column("local_id", IntegerType()),
    Column("ctor_id", StringType()),
    Column("qname_pid", StringType()),
    Column("idx", IntegerType()),
    Column("lit_id", StringType()),
    Column("kids", ArrayType(StringType())),
)
