#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.query_tables` — a DIFFERENTIAL against the origin, table by table.

⚑⚑ THE REPLICA IS VERIFIED, NOT BELIEVED. `query_tables` is cleanroomed from
`jea/metalanguage/query_decl.py`, so the only honest check is the origin itself: it is loaded HERE,
in the suite and nowhere else, and its `_MD` catalogue and its two scratch shapes are compared
with this module's. Loading the origin by path is a test instrument, not a dependency — the
module under test never touches it, and the load retires with the origin.

⚑ THREE THINGS PER RELATION, because each can drift independently: the relation's NAME, its
columns IN ORDER (order is the `SELECT *` projection), and each column's compiled type (the
compiler dispatches on `__visit_name__`, which is how the `*Type` stand-ins replace the real
types; an ARRAY's element type is compared too).

⚑ AND BOTH DIRECTIONS. A relation the origin declares that the replica lacks is a builder that
cannot be ported; one the replica declares that the origin lacks is an invention.
"""

from __future__ import annotations

import importlib.util
import sys

from sqlalchemy import MetaData, Table

from substrate import corpus, query_tables

# The origin module, relative to the tree.
_ORIGIN = ("jea", "metalanguage", "query_decl.py")

# How many relations the replica ports into `METADATA`. Cut 1 (origin lines 107-227): 18 base
# tables, the six `dec_*` tiers and the two `core_decoded` relations = 26 (⚑ first written as 27
# from a miscount; this case caught it). Cut 2a (lines 356-369): 7 reuse-catalogue base tables +
# 5 compat-view shapes = 12. The scratch shapes (cut 2c) are on private catalogues, cased apart.
_CATALOGUED = 26 + 12

# A relation's shape: its column names in order, each with its type's name.
Shape = tuple[tuple[str, str], ...]


def _origin() -> object | None:
    """Load the origin module by path, or None when it cannot be loaded."""
    path = corpus.ROOT.joinpath(*_ORIGIN)
    spec = importlib.util.spec_from_file_location("_query_decl_origin", path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _type_name(type_: object) -> str:
    """Return a column type's visit name, with an ARRAY's element type appended."""
    visit: object = getattr(type_, "__visit_name__", "")
    name = visit if isinstance(visit, str) else ""
    item: object = getattr(type_, "item_type", None)
    return f"{name}[{_type_name(item)}]" if item is not None else name


def _shape(tbl: Table) -> Shape:
    """Return `((column, type name), ...)` for one table, in column order."""
    return tuple((col.name, _type_name(col.type)) for col in tbl.columns)


def _shapes(metadata: MetaData) -> dict[str, Shape]:
    """Return `{relation: shape}` for every table in `metadata`."""
    return {name: _shape(tbl) for name, tbl in metadata.tables.items()}


def _scratch_cases(origin: object) -> list[tuple[str, bool]]:
    """Compare the per-connection scratch shapes, which live outside the shared catalogue."""
    pairs = (("_ht_map_t", query_tables.ht_map), ("_sig_t", query_tables.sig_level))
    out: list[tuple[str, bool]] = []
    for attr, replica in pairs:
        theirs: object = getattr(origin, attr, None)
        same = (
            isinstance(theirs, Table)
            and theirs.name == replica.name
            and _shape(theirs) == _shape(replica)
        )
        out.append((f"the scratch shape {replica.name} matches the origin's {attr}", same))
    return out


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    module = _origin()
    found: object = getattr(module, "_MD", None)
    if module is None or not isinstance(found, MetaData):
        return [("the origin's catalogue loads", False)]
    origin = _shapes(found)
    replica = _shapes(query_tables.METADATA)
    # ⚑ ONLY THE RELATIONS THE REPLICA COVERS. A relation it has not reached yet is pending, not a
    # mismatch; the count case below says how many are covered.
    ported = {name: shape for name, shape in origin.items() if name in replica}
    mismatched = sorted(name for name, shape in ported.items() if replica[name] != shape)
    invented = sorted(set(replica) - set(origin))
    for name in mismatched:
        sys.stdout.write(f"  {name}: origin {origin[name]} != replica {replica[name]}\n")
    return [
        ("the origin's catalogue loads", True),
        ("every replica relation exists in the origin", not invented),
        ("every ported relation matches name, column order and type", not mismatched),
        ("the catalogue ports every relation cuts 1 and 2a cover", len(ported) == _CATALOGUED),
        *_scratch_cases(module),
    ]


def selftest() -> int:
    """Run every case, reporting failures by name, and return an exit code."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"query-tables selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 1)
