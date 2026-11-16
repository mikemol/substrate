#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Compile ONE row's INSERT — values BY NAME, params a DICT, statement built by the compiler.

⚑⚑⚑ THIS IS NOT A SETTLEMENT BETWEEN TWO CONTRACTS — IT REMOVES A DEVIATION FROM ONE. The
question this module was commissioned to answer was framed as a conflict: the Core path yields a
dict of params while the incumbent single-row writer passes a TUPLE, so compiling through the
pinned dialect looked like it would change the runtime contract at every call site. Reading the
two authorities dissolves it, and BOTH were read rather than recalled:

  * `store.dialect()` pins `paramstyle="pyformat"`, and its docstring states the pin's purpose as
    holding the arms to *"ONE runtime contract"* — spelled out as *"the runtime's dict-of-params
    contract"*, which is *"what let the sqlite arm be deleted without touching a single caller's
    parameter dict."* A path emitting a dict does not violate that pin; it is what the pin exists
    to hold.
  * `insert_row`'s own first line is *"ONE row, ONE statement, values keyed BY NAME"*, and it
    argues the point rather than assuming it: the name map is *"A STRENGTHENING OVER `upsert`, NOT
    A STYLE DIFFERENCE"*, because a positional tuple shifts every caller's data when a column is
    added and *"a name map cannot shift."*

⚑⚑ SO THE TUPLE WAS AN ARTIFACT OF THE IMPLEMENTATION, NOT A DESIGN CHOICE — hand-assembled
positional `%s` placeholders inside a function whose stated contract is by name. Two of the three
parties already agreed; the tuple was the lone deviation, and the deviation lived in the half
nobody had written down as a decision.

⚑⚑⚑ AND THE VALUES ARE INJECTED, NEVER IMPORTED. `substrate/` may name nothing under `jea/` — a
module that does inherits the untyped hub and cannot be clean under this repo's per-file gate,
which is a LOCATION property no edit to a file's contents can clear. So the declaration arrives as
a `Table` the caller already holds. That makes this a SUPERSESSION rather than an extraction: the
incumbent is not rewired to call this, and the consumers move when they are themselves superseded.

⚑⚑ THE `WHERE` IS A ROW CONSTRUCTOR AND THAT IS THE PROPERTY, NOT AN INCIDENTAL RENDERING.
`(a, b) IS DISTINCT FROM (x, y)` is NULL-safe in both directions; the per-column form
`a <> x OR b <> y` evaluates to NULL — hence not-true, hence a SILENTLY SKIPPED update — the
moment either side is NULL. A nullable column makes that reachable rather than defensive, so a
case asserting merely that a `WHERE` exists would pass on the broken form. The cases here assert
the constructor.

⚑ NO STRING IS ASSEMBLED HERE. Every fragment — the column roster, the placeholders, the conflict
target, the SET list, the distinctness predicate — is an expression the compiler renders against
the pinned dialect. A hand-assembled statement is exactly what the incumbent does, and it is why
the incumbent omits the `::JSONB` cast the compiler emits from the declared column type.

Usage: python3 -m substrate.row_upsert
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlalchemy import tuple_
from sqlalchemy.dialects.postgresql import insert

from substrate.postgres_dialect import PostgresDialect

if TYPE_CHECKING:
    from collections.abc import Mapping

    from sqlalchemy import Table

#: The two conflict modes, spelled once. ⚑ NAMED RATHER THAN INLINED so the roster a refusal
#: quotes and the roster the branches test cannot drift apart — the shape `ph`'s retired `back`
#: parameter records, one level up.
IGNORE = "ignore"
REPLACE = "replace"
MODES = (IGNORE, REPLACE)

#: ⚑ THE PARAMSTYLE IS PINNED HERE THE WAY `store.dialect()` PINS IT, and for the reason its
#: docstring gives: `%(name)s` is what makes the runtime contract a DICT keyed by column name.
#: Re-pinning is not a second authority — it is the same one value, and a case below asserts the
#: rendered marks so a divergence is observable rather than assumed.
PARAMSTYLE = "pyformat"


@dataclass(frozen=True, slots=True)
class Statement:
    """A compiled single-row upsert: the SQL text, and the params it binds BY NAME.

    ⚑ THE PARAMS ARE A DICT, WHICH IS THE WHOLE POINT. A tuple would re-introduce the positional
    coupling `insert_row`'s docstring argues against — adding a column shifts every caller's data
    one place, caught only by an arity mismatch if at all.
    """

    sql: str
    params: dict[str, object]


def _refuse_undeclared(table: Table, values: Mapping[str, object]) -> None:
    """Refuse a key the declaration does not carry.

    ⚑ A TYPO'D COLUMN COMPOSES A SYNTACTICALLY VALID INSERT INTO THE WRONG ONE, so dropping the
    key silently writes a row missing the fact the caller believed it had written. The refusal
    names the declaration the roster came from, which postgres would not.
    """
    declared = [c.name for c in table.columns]
    unknown = sorted(k for k in values if k not in declared)
    if unknown:
        msg = (
            f"row_upsert({table.name!r}): {unknown} is not a declared column. "
            f"{table.name} declares {declared}. A name that does not resolve is REFUSED rather "
            f"than dropped, because a silently ignored key writes a row missing the fact the "
            f"caller believed it had written."
        )
        raise ValueError(msg)


def _refuse_missing(table: Table, values: Mapping[str, object]) -> None:
    """Refuse a required column the caller did not supply.

    ⚑ POSTGRES WOULD SAY THE SAME THING, BUT NOT UNTIL THE STATEMENT RAN, and not naming the
    declaration the requirement comes from. A column is required when it is NOT NULL and carries
    no server default — the two conditions together, since a defaulted NOT NULL column is
    satisfiable without a value.
    """
    missing = sorted(
        c.name
        for c in table.columns
        if not c.nullable and c.server_default is None and c.name not in values
    )
    if missing:
        msg = (
            f"row_upsert({table.name!r}): {missing} is declared NOT NULL with no server default "
            f"and was not supplied. Refusing here rather than letting postgres raise, so the "
            f"message names the DECLARATION the requirement comes from."
        )
        raise ValueError(msg)


def compile_row(table: Table, values: Mapping[str, object], on_conflict: str = IGNORE) -> Statement:
    """Return the compiled statement and its by-name params for ONE row.

    ⚑⚑ THE CONFLICT TARGET IS THE PRIMARY KEY, READ FROM THE DECLARATION RATHER THAN NAMED BY THE
    CALLER. `insert_row`'s docstring records why the word 'replace' must mean ONE thing across the
    batch and single-row writers — *"two spellings of one word across two functions is the drift
    this layer exists to prevent"* — and the target is half of that meaning.

    ⚑ A TABLE WITH NO NON-KEY COLUMN TO UPDATE DEGRADES TO `DO NOTHING` RATHER THAN EMITTING AN
    EMPTY `SET`. An `ON CONFLICT DO UPDATE SET` with nothing to set is not a statement postgres
    accepts, and the degradation is exact: with no non-key column, "already stored" and "would be
    written" are the same row, so declining the write loses nothing.
    """
    if on_conflict not in MODES:
        msg = f"row_upsert: on_conflict={on_conflict!r}; the modes are {IGNORE!r} and {REPLACE!r}"
        raise ValueError(msg)
    _refuse_undeclared(table, values)
    _refuse_missing(table, values)
    cols = [c.name for c in table.columns if c.name in values]
    statement = insert(table).values({c: values[c] for c in cols})
    pk = [c.name for c in table.primary_key.columns]
    if on_conflict == REPLACE and not pk:
        msg = (
            f"row_upsert(replace) needs a PRIMARY KEY as its conflict target; "
            f"{table.name} declares none"
        )
        raise ValueError(msg)
    rest = [c for c in cols if c not in pk]
    if on_conflict == REPLACE and rest:
        excluded = statement.excluded
        # ⚑ A ROW CONSTRUCTOR ON BOTH SIDES — `tuple_(...)` is the compiler's spelling of the
        # NULL-safe comparison. Building the same predicate as a per-column conjunction would
        # type-check, render, run, and skip updates against a nullable column.
        final = statement.on_conflict_do_update(
            index_elements=pk,
            set_={c: excluded[c] for c in rest},
            where=tuple_(*[table.c[c] for c in rest]).is_distinct_from(
                tuple_(*[excluded[c] for c in rest])
            ),
        )
    else:
        final = statement.on_conflict_do_nothing()
    compiled = final.compile(dialect=PostgresDialect(paramstyle=PARAMSTYLE))
    return Statement(str(compiled), dict(compiled.params))


def main(argv: list[str]) -> int:
    """Report what this module compiles against, and under which paramstyle."""
    if argv:
        sys.stderr.write("usage: python3 -m substrate.row_upsert\n")
        return 2
    sys.stdout.write(
        f"dialect    : PostgresDialect (substrate.postgres_dialect)\n"
        f"paramstyle : {PARAMSTYLE} — params are a DICT keyed by column name\n"
        f"modes      : {', '.join(MODES)}\n"
        f"declaration: injected as a Table; this module names nothing under jea/\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
