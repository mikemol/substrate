#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.row_upsert` — the row constructor, the two refusals, the dict params.

⚑⚑⚑ THE ROW-CONSTRUCTOR ARM IS THE ONE A PLAUSIBLE IMPLEMENTATION PASSES WHILE BEING BROKEN, and
that is why it is spelled as an EXACT predicate rather than a presence check. The obvious cheap
assertion — *"a WHERE clause is emitted"* — is satisfied by the per-column conjunction
`a <> excluded.a OR b <> excluded.b`, which renders, parses, runs, and then evaluates to NULL the
moment either side is NULL. NULL is not TRUE, so the `DO UPDATE` is SKIPPED, silently, and the
caller reads `rowcount == 0` as "already current". A nullable column makes that reachable, so this
arm asserts the tuple form on BOTH sides and asserts the conjunction spelling is ABSENT.

⚑⚑ THE TWO REFUSAL ARMS PIN GUARANTEES POSTGRES ALSO OFFERS, WHICH IS NOT A REASON TO DROP THEM.
An undeclared key is caught by postgres only when the statement runs, and the error names a column
rather than the declaration the roster came from; a missing NOT-NULL column likewise. The value of
refusing here is the LOCATION and the MESSAGE, and a case is the only thing that keeps both.

⚑ THE DECLARATION IS BUILT HERE RATHER THAN IMPORTED, and the module under test takes it by
injection — so every arm runs with postgres unreachable, and none of them names anything under
`jea/`. That is the constraint the module exists under, exercised rather than asserted.

⚑⚑ THE FIXTURE'S COLUMN TYPE IS A LOCAL `TypeEngine` SUBCLASS, NOT `sqlalchemy.Text`. The
top-level stub types `Text` as `TypeEngine[str]` and `Integer` as `TypeEngine[int]`, and
`Column`'s type parameter is INVARIANT, so a `Table` holding mixed column types cannot be spelled
by naming those classes directly. A subclass at `TypeEngine[object]` is the honest carrier for a
fixture whose values are deliberately heterogeneous.

⚑⚑⚑ AND THE INVARIANCE IS THE LIBRARY'S, NOT THE STUB'S — MEASURED 2026-09-03 (Ⓝ128d),
CORRECTING WHAT THIS PARAGRAPH USED TO SAY. It read *"a fact about the STUB's precision, not
about the library"*, which invited the repair of widening our own declaration. Read from source:
`sqlalchemy/sql/type_api.py:62` declares `_T = TypeVar("_T", bound=Any)` and line 63 declares
`_T_co = TypeVar("_T_co", bound=Any, covariant=True)` immediately beside it; `TypeEngine`
(line 118) and `Column` (`sql/schema.py:1497`, via `ColumnClause[_T]`) both take the INVARIANT
`_T`. Upstream has the covariant TypeVar in hand and does not use it here. Our stub transcribed
the library correctly.

⚑⚑ SO THERE IS NO VARIANCE DECISION TO MAKE ON SOMEONE ELSE'S GENERIC — which is a sharper
result than the earlier caution that we should not make one. Widening our stub to covariant would
not be a repair but a FORK: it would type-check call sites that the library's own annotations
refuse, which is the `agda_lex.pyi` failure one level up (a signature reconstructed from how we
wish to use a symbol). The subclass below IS the honest spelling, and it is the documented
pattern rather than a workaround awaiting removal.

⚑ THE COST IS STATED WITH THE PATTERN: a heterogeneous `Table` loses per-column value types, and
that is what invariance means rather than something this file gave up. A fixture whose columns
each had a settled type would name `Text` and `Integer` directly and keep them.
"""

from __future__ import annotations

import sys

from mikemol.witness import witness_family
from sqlalchemy import Column, MetaData, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.type_api import TypeEngine

from substrate import row_upsert, suite_emit


class _AnyText(TypeEngine[object]):
    """A textual column type parameterised at the top type, so one table may mix types."""

    __visit_name__ = "text"


def _fixture() -> Table:
    """Build the declaration every arm compiles against: key, required JSONB, nullable column.

    ⚑ `mtime` IS NULLABLE ON PURPOSE AND IT IS THE WHOLE POINT OF THE ROW-CONSTRUCTOR ARM. The
    incumbent's own comment names `core_decoded.mtime` as the reachable case — an unreadable
    `stat` writes NULL there — so the fixture reproduces the shape rather than a generic one.
    """
    return Table(
        "core_decoded",
        MetaData(),
        Column("path", _AnyText(), primary_key=True),
        Column("dec", JSONB(), nullable=False),
        Column("mtime", _AnyText(), nullable=True),
    )


_ROW = {"path": "/a", "dec": {"x": 1}, "mtime": 5}

# The exit code a mode returns when refusing a usage it does not implement.
_REFUSED = 2


def the_replace_where_is_a_row_constructor(out: list[str]) -> int:
    """Check the distinctness test compares one TUPLE to another, not column by column.

    ⚑⚑ BOTH HALVES ARE ASSERTED. Checking only that the tuple form is PRESENT would pass on an
    implementation that emitted both; checking only that `OR` is absent would pass on a statement
    with no WHERE at all. The pair is what pins the predicate.
    """
    sql = row_upsert.compile_row(_fixture(), _ROW, row_upsert.REPLACE).sql
    want = (
        "WHERE (core_decoded.dec, core_decoded.mtime) IS DISTINCT FROM "
        "(excluded.dec, excluded.mtime)"
    )
    if want not in sql:
        out.append(f"selftest: the WHERE is not a row constructor: {sql}")
        return 1
    if " OR " in sql:
        out.append(f"selftest: the WHERE is a per-column conjunction, which goes NULL: {sql}")
        return 1
    return 0


def an_undeclared_key_refuses(out: list[str]) -> int:
    """Check a name the declaration does not carry is refused rather than dropped.

    ⚑ THE MESSAGE IS ASSERTED, NOT JUST THE RAISE. A refusal that did not name the offending key
    and the declared roster would leave the caller doing the same lookup by hand, which is the
    reason for refusing here rather than at the server.
    """
    try:
        row_upsert.compile_row(_fixture(), {**_ROW, "mtiem": 5})
    except ValueError as exc:
        if "mtiem" in str(exc) and "core_decoded" in str(exc):
            return 0
        out.append(f"selftest: the undeclared-key refusal does not name the key: {exc}")
        return 1
    out.append("selftest: an undeclared key was accepted")
    return 1


def a_required_column_with_no_value_refuses(out: list[str]) -> int:
    """Check a NOT-NULL column with no server default and no value is refused.

    ⚑ THE NULLABLE COLUMN IS OMITTED IN THE SAME CALL, and that is the discriminator. An
    implementation testing only `nullable` would refuse `mtime` too; one testing only presence
    would refuse nothing. Omitting both at once separates the two.
    """
    try:
        row_upsert.compile_row(_fixture(), {"path": "/a"})
    except ValueError as exc:
        if "dec" in str(exc) and "mtime" not in str(exc):
            return 0
        out.append(f"selftest: the required-column refusal names the wrong columns: {exc}")
        return 1
    out.append("selftest: a missing NOT-NULL column was accepted")
    return 1


def ignore_renders_do_nothing(out: list[str]) -> int:
    """Check `on_conflict='ignore'` renders `ON CONFLICT DO NOTHING` with no target and no SET."""
    sql = row_upsert.compile_row(_fixture(), _ROW, row_upsert.IGNORE).sql
    if not sql.endswith("ON CONFLICT DO NOTHING") or "DO UPDATE" in sql:
        out.append(f"selftest: 'ignore' did not render DO NOTHING: {sql}")
        return 1
    return 0


def replace_renders_do_update_on_the_primary_key(out: list[str]) -> int:
    """Check `on_conflict='replace'` targets the declared key and sets every non-key column.

    ⚑ THE CONFLICT TARGET IS READ FROM THE DECLARATION, so this arm pins that the key column is
    the target AND that it is absent from the SET list — updating a row's own key on conflict is
    a no-op at best and a corruption at worst.
    """
    sql = row_upsert.compile_row(_fixture(), _ROW, row_upsert.REPLACE).sql
    if "ON CONFLICT (path) DO UPDATE SET dec = excluded.dec, mtime = excluded.mtime" not in sql:
        out.append(f"selftest: 'replace' did not render the expected DO UPDATE: {sql}")
        return 1
    if "path = excluded.path" in sql:
        out.append(f"selftest: the conflict key appears in the SET list: {sql}")
        return 1
    return 0


def the_params_are_a_dict_keyed_by_column_name(out: list[str]) -> int:
    """Check the params are a name map and the marks are `%(name)s`, not positional `%s`.

    ⚑⚑ THE MARKS AND THE PARAMS ARE ASSERTED TOGETHER, because either alone is satisfiable by a
    broken pair. A dict of params rendered against a positional paramstyle binds nothing; named
    marks with a tuple of params is what psycopg refuses at runtime. The two halves ARE the
    contract `store.dialect()`'s pin exists to hold.
    """
    made = row_upsert.compile_row(_fixture(), _ROW, row_upsert.REPLACE)
    if made.params != _ROW:
        out.append(f"selftest: the params are not the by-name row: {made.params}")
        return 1
    if "%(path)s" not in made.sql:
        out.append(f"selftest: the placeholders are not named: {made.sql}")
        return 1
    return 0


def an_unknown_mode_refuses(out: list[str]) -> int:
    """Check a conflict mode outside the roster is refused and the roster is named."""
    try:
        row_upsert.compile_row(_fixture(), _ROW, "upsert")
    except ValueError as exc:
        if row_upsert.IGNORE in str(exc) and row_upsert.REPLACE in str(exc):
            return 0
        out.append(f"selftest: the mode refusal does not name the roster: {exc}")
        return 1
    out.append("selftest: an unknown conflict mode was accepted")
    return 1


def the_reporter_runs_and_refuses_arguments(out: list[str]) -> int:
    """Check the reporter runs, and refuses an argument rather than ignoring it."""
    if row_upsert.main([]) != 0:
        out.append("selftest: the reporter exited non-zero")
        return 1
    if row_upsert.main(["--anything"]) != _REFUSED:
        out.append("selftest: the reporter accepted an argument it does not implement")
        return 1
    return 0


FAMILY = witness_family.of(
    key="row_upsert",
    apex="a single-row upsert compiled against the pinned dialect binds its values BY NAME and "
    "conditions its update on a NULL-safe row-constructor comparison, refusing an "
    "undeclared key and an unsupplied required column at the declaration rather than at "
    "the server",
    subject="`substrate.row_upsert.compile_row` over an injected three-column declaration whose "
    "third column is nullable",
    members=(
        witness_family.Member(
            name="the_replace_where_is_a_row_constructor",
            claim="the DO UPDATE's WHERE compares one tuple to another, with no OR conjunction",
        ),
        witness_family.Member(
            name="an_undeclared_key_refuses",
            claim="a key the declaration does not carry is refused, naming the key and the table",
        ),
        witness_family.Member(
            name="a_required_column_with_no_value_refuses",
            claim="a NOT-NULL column with no server default and no value is refused; a nullable "
            "one is not",
        ),
        witness_family.Member(
            name="ignore_renders_do_nothing",
            claim="on_conflict='ignore' renders ON CONFLICT DO NOTHING",
        ),
        witness_family.Member(
            name="replace_renders_do_update_on_the_primary_key",
            claim="on_conflict='replace' targets the declared key and sets only non-key columns",
            premises=("the_replace_where_is_a_row_constructor",),
        ),
        witness_family.Member(
            name="the_params_are_a_dict_keyed_by_column_name",
            claim="the params are a by-name dict and the marks are named, not positional",
        ),
        witness_family.Member(
            name="an_unknown_mode_refuses",
            claim="a conflict mode outside the roster is refused and the roster is named",
        ),
        witness_family.Member(
            name="the_reporter_runs_and_refuses_arguments",
            claim="the reporter runs, and refuses an argument rather than silently ignoring it",
        ),
    ),
)

_ARMS = (
    the_replace_where_is_a_row_constructor,
    an_undeclared_key_refuses,
    a_required_column_with_no_value_refuses,
    ignore_renders_do_nothing,
    replace_renders_do_update_on_the_primary_key,
    the_params_are_a_dict_keyed_by_column_name,
    an_unknown_mode_refuses,
    the_reporter_runs_and_refuses_arguments,
)

_CASE_COUNT = FAMILY.count

_SELF_KEY = "substrate/row_upsert_selftest.py"


def selftest() -> int:
    """Run every arm, report by typed record, and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(_SELF_KEY, _CASE_COUNT - failures, _CASE_COUNT)


if __name__ == "__main__":
    raise SystemExit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
