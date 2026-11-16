#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Rostered paydown sites - which named definitions have not yet reached the store they should.

THE FIFTH CUT OF THE DRAIN'S FIFTH FILE (`catalog/library/figures.py:1003-1102`, W4 tick 62).
Two figures shared one shape and hand-inlined it twice: a ROSTER of `(file, def)` sites that
re-derive a relation the catalog already holds (the import DAG, `_module_edges`) or store a
parsed tree whole where the node tables hold it as rows, and a PREDICATE - the site is PAID
when its source reaches the store, named by tokens (`module_edges`, `node_child`...). An
earlier cut of the DAG figure tested for `yield` and would have reported the item paid for a
generator that still re-derives the relation; the tokens name the store, not the shape.

THE ROSTERS ARE DATA, THE READER IS ONE FUNCTION. `source_of` is a parameter - the origin
reaches `pycodemod.source_of` through a sys.path insert - so a suite drives the predicate over
literal sources, and a site whose source cannot be read is SKIPPED, not reported: an unreadable
site is unmeasured, and reporting it as unpaid would bank a defect the reader never saw.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

# (repo-relative file, def name, what it holds) - the sites and the store tokens that pay them.
Site = tuple[str, str, str]
# The source of a def in a file, or None when it cannot be read.
SourceOf = Callable[[str, str], str | None]

DAG_SITES: tuple[Site, ...] = (
    ("scripts/gen_build_makefiles.py", "parse_tree", "the source-parsed import DAG"),
    ("scratch/split_pipeline.py", "_import_dag", "the memoised import DAG"),
)
DAG_PAID = ("module_edges", "catalog_db")

CST_SITES: tuple[Site, ...] = (
    ("scratch/pycodemod.py", "_cached_defs", "pickled parse cache"),
    ("scratch/cache_probe.py", "probe", "pickled CST measurement"),
)
CST_PAID = ("node_child", "unit_node")


def unpaid(
    sites: Iterable[Site], paid: Iterable[str], source_of: SourceOf
) -> list[tuple[str, str, str]]:
    """Return the readable sites whose source names none of the store tokens."""
    tokens = tuple(paid)
    out: list[tuple[str, str, str]] = []
    for rel, fn, what in sites:
        src = source_of(rel, fn)
        if not src:
            continue
        if not any(t in src for t in tokens):
            out.append((rel, fn, what))
    return out
