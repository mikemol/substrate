# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Typed SQL comparison for the cleanroomed builders: `eq(col, value)` in place of `col == value`.

⚑⚑ WHY A HELPER (operator ruling, 2026-09-25: *"Typed eq() helper"*). SQLAlchemy overloads `==` on
a column to BUILD a SQL expression, but its stub cannot say so without overriding `object.__eq__`,
which needs a line-level `# type: ignore[override]` — refused here, as is a
`[[tool.mypy.overrides]]` relief (`pyproject.toml` forbids both). Under `strict_equality`,
`col == 1` is then a "non-overlapping equality check". So one function owns the seam: it calls the
column's own `__eq__` — the same method `==` dispatches to, hence the SAME SQL — and NARROWS what
comes back.

⚑ THE NARROWING IS A CHECK, NOT A CAST. The runtime result of a column's `__eq__` is a
`ColumnElement`; if it ever were not (a plain `bool` from comparing two non-SQL values), this
raises rather than handing a `bool` to a `WHERE` that would render it as a literal TRUE/FALSE.
"""

from __future__ import annotations

from sqlalchemy import ColumnElement


def eq(left: ColumnElement[object], right: object) -> ColumnElement[object]:
    """Return the SQL expression `left = right`, exactly as `left == right` builds it."""
    built: object = left.__eq__(right)
    if not isinstance(built, ColumnElement):
        msg = f"{left!r} == {right!r} built {type(built).__name__}, not a SQL expression"
        raise TypeError(msg)
    return built
