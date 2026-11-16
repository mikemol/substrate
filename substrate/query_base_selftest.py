#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.query_base` — a DIFFERENTIAL on each builder's rendered SQL.

⚑ Every builder is called on both sides through `query_oracle` (the origin loaded by path in the
suite only) and must render the origin's SQL exactly; `q_shared_subtree` also exercises
`query_views`, and `q_core_fp_mtime` a caller-bound `bindparam`.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from substrate import query_base, query_oracle

if TYPE_CHECKING:
    from collections.abc import Callable

    from sqlalchemy.sql.selectable import Select

# The replica's builders, by the name the origin defines each under.
_REPLICA: dict[str, Callable[[], Select]] = {
    "q_pathtext_all": query_base.q_pathtext_all,
    "q_terms_all": query_base.q_terms_all,
    "q_unit_fields": query_base.q_unit_fields,
    "q_unit_cod": query_base.q_unit_cod,
    "q_unit_member": query_base.q_unit_member,
    "q_meta_failed": query_base.q_meta_failed,
    "q_node_child_edges": query_base.q_node_child_edges,
    "q_shared_subtree": query_base.q_shared_subtree,
    "q_defcopy_units": query_base.q_defcopy_units,
    "q_unit_node_all": query_base.q_unit_node_all,
    "q_core_count": query_base.q_core_count,
    "q_core_fp_ids": query_base.q_core_fp_ids,
    "q_core_fp_mtimes": query_base.q_core_fp_mtimes,
    "q_core_fp_mtime": query_base.q_core_fp_mtime,
}


def selftest() -> int:
    """Run the differential and return an exit code."""
    return query_oracle.report("query-base", query_oracle.differential(_REPLICA))


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 1)
