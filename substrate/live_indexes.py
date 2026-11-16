#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""What the engine ACTUALLY indexes — the ground truth a contour nomination is checked against.

From one `pg_index` read: the leading two columns of every multi-column index, and the
`table.column` keys a single-column UNIQUE or PRIMARY KEY index already serves.

⚑⚑⚑ THE ABSENT READ IS THE FAILURE MODE, AND IT IS SILENT. The sqlite predecessor did
`os.path.exists(CATALOG)` on a deleted file and returned an EMPTY map, so every contour was
reported as "no composite index" and the tool's whole output became a list of gaps that are not
gaps. Absent-read-as-finding, in the instrument that exists to nominate work. So nothing here
swallows a failure into an empty result: a caller that cannot reach the store gets the store's
exception, because an empty map and an unread one are indistinguishable downstream and only the
connection site can tell them apart.

⚑⚑ THE ROW READER IS INJECTED, NOT IMPORTED, and that is forced as well as right. Forced: the
row contract lives in a module carrying hundreds of findings, and this repo's per-file gate
stages a new module's TRANSITIVE imports — so importing it by package path refuses a file that
is itself clean. Right: the reader is what carries the TENANT. A module that reaches for its own
connection has already chosen `--live` or `--sandbox` on the caller's behalf, and a wrong-tenant
read returns plausible rows nobody can distinguish. Making it a parameter puts that choice where
the operator states it.

⚑⚑ ONE QUERY, NOT THREE NESTED LOOPS. The sqlite form issued `sqlite_master`, then
`PRAGMA table_info` and `PRAGMA index_list` per table, then `PRAGMA index_info` per index —
round trips proportional to tables times indexes, with a `try/except OperationalError`
swallowing whatever failed. `pg_index` carries the column vector (`indkey`) directly, so
unnesting it WITH ORDINALITY gives (table, index, column, position, is_unique, is_primary) as
ROWS, and the ordering that makes the first two columns meaningful is the ENGINE's rather than a
per-index re-query's.

⚑ A SINGLE-COLUMN NON-UNIQUE INDEX IS NEITHER. It is not a composite (nothing to lead with) and
it is not a key seek (it does not identify a row), so it appears in neither return value. That
is not an omission: a contour whose predicate has a plain single-column index is still a real
covering-index candidate, because the index cannot supply the projected column.

⚑ EXTRACTED FROM `scripts/query_topo.py` (⟡drain-query-topo), which held the last live sqlite
read in the tree before the port.
"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

    # One result row, readable by column name — the shape `schema_rows.rows` yields.
    IndexRow = Mapping[str, object]

# ⚑ `current_schemas(false)` — the SEARCH PATH the connection actually resolves against, never a
# hardcoded `public`. A sandbox fixture lives in a private schema, so pinning `public` would read
# the WRONG TENANT and return plausible rows nobody could distinguish from the live ones.
INDEX_SQL = """
    SELECT t.relname AS tbl, i.relname AS idx, a.attname AS col,
           x.indisunique AS uniq, x.indisprimary AS pk, k.ord AS ord
      FROM pg_index x
      JOIN pg_class i ON i.oid = x.indexrelid
      JOIN pg_class t ON t.oid = x.indrelid
      JOIN pg_namespace n ON n.oid = t.relnamespace
      CROSS JOIN LATERAL unnest(x.indkey) WITH ORDINALITY AS k(attnum, ord)
      JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = k.attnum
     WHERE n.nspname = ANY (current_schemas(false))
     ORDER BY t.relname, i.relname, k.ord
"""

# The smallest column count that makes an index a COMPOSITE.
_COMPOSITE_MIN = 2

# The key of one index in the grouped reading: table, index name, unique, primary.
IndexKey = tuple[str, str, bool, bool]


def group_by_index(rows: Iterable[IndexRow]) -> dict[IndexKey, list[str]]:
    """Group `INDEX_SQL` rows into each index's columns, IN THE ORDER THEY ARRIVE.

    ⚑ THE ORDER IS THE POINT, AND IT IS THE QUERY'S, NOT THIS FUNCTION'S. `indkey` is a vector
    and the leading column is the only one a predicate can seek; the `ORDER BY … k.ord` is what
    makes append-order correct. A caller feeding rows from anywhere else must preserve it — a
    set-valued or re-sorted feed would make every composite look order-free and turn a correct
    nomination into a coin flip.
    """
    cols: dict[IndexKey, list[str]] = defaultdict(list)
    for r in rows:
        key = (str(r["tbl"]), str(r["idx"]), bool(r["uniq"]), bool(r["pk"]))
        cols[key].append(str(r["col"]))
    return dict(cols)


def composites(
    by_index: Mapping[IndexKey, Sequence[str]],
) -> dict[str, list[tuple[str, str, str]]]:
    """Return `{table: [(first_col, second_col, index_name)]}` for multi-column indexes."""
    out: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for (tbl, idx, _uniq, _pk), cs in by_index.items():
        if len(cs) >= _COMPOSITE_MIN:
            out[tbl].append((cs[0], cs[1], idx))
    return dict(out)


def key_columns(by_index: Mapping[IndexKey, Sequence[str]]) -> frozenset[str]:
    """Return the `table.column` keys served by a single-column UNIQUE or PRIMARY index.

    These are the predicates a covering-index nomination must SUPPRESS: a key predicate is
    already an index seek, so the composite it would suggest buys the projection only.
    """
    return frozenset(
        f"{tbl}.{cs[0]}"
        for (tbl, _idx, uniq, pk), cs in by_index.items()
        if len(cs) == 1 and (uniq or pk)
    )
