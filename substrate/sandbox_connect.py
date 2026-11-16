#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Open the SANDBOX tenant's connection from the assembled target (Ⓝ94 ⟡the-psycopg-stub).

⚑⚑⚑ THIS MODULE IS THE PROOF THE STUB WORKS, AND THAT IS ITS FIRST JOB. `substrate/
sandbox_target.py` was measured correct and tested and COULD NOT BE WIRED TO ANYTHING: a clean
consumer passed ruff and was refused by mypy, because `dict_row` and `psycopg.Error` are
themselves `Any`-typed expressions under `disallow_any_expr`. No module in `substrate/` imported
psycopg as a result. `stubs/psycopg/` closes that, and a stub nothing imports is an unexercised
claim — so the wrapper and the stub land together or neither is established.

⚑⚑ IT IS A SEPARATE MODULE FROM THE TARGET, DELIBERATELY, AND THE SEAM IS THE DRIVER IMPORT.
`sandbox_target` documents that it opens no connection and imports no driver, so that assembly
stays pure, total and checkable with no server — and so that it stays importable on the
pre-commit path without pulling a database driver behind it. Adding `connect` there would take
both properties away from a module that argues for them at length. The split is the one that
file already drew; this module is the other half of it.

⚑ THE ROW TYPE IS A PARAMETER OF THE CONNECTION, NOT A CAST AT EACH CALL SITE. `connection()`
yields `Connection[DictRow]`, so `fetchall()` gives back mappings with no narrowing at the
caller. That is the whole benefit of typing THROUGH psycopg's generics rather than around them:
the parameter carries the answer from the row factory to the fetch.

⚑⚑ AND A ROW VALUE IS `object`, NOT `Any` — the stub's one substitution, and the place a caller
feels it. A column holds whatever the adapter produced, so a caller that wants a `str` must
narrow with an `isinstance` the checker verifies, instead of an `Any` it waves through.
`descriptor` below does exactly that, and the narrowing is not ceremony: its values flow into a
formatted `DROP ... CASCADE`, so a value that is not text must be refused before it is
interpolated. Under the library's own `dict[str, Any]` that check would have looked like
superstition and been dropped by the next reader.

⚑⚑⚑ THE FIELDS ARE PASSED AS EXPLICIT KEYWORDS AND `Target.keywords()` IS NOT UNPACKED HERE —
MEASURED, not preferred. `connect(**mapping, row_factory=...)` is refused: a `**`-unpacked
`dict[str, str | int]` cannot select an overload whose variable keywords are typed, so mypy
reports no matching variant AND an `Any` return. That is a real limitation of unpacking against
an overload set, not of this stub, and the honest response is to name the fields rather than to
widen the stub until the unpack is admitted. ⚑ `keywords()` KEEPS ITS OTHER CALLERS and is not
changed by this module — it renders the driver mapping for anything that consumes one.

⚑ A CONNECT FAILURE IS `OperationalError` AND A REFUSED QUERY IS NOT. They are separated here
because they are two different next actions — "the store is unreachable, check the port and the
cutover" versus "the statement was wrong" — and the connector this replaces collapsed them,
which is how a NodePort cutover read as a query problem for as long as it did.

⚑ NO CREDENTIAL IS NAMED, READ, OR LOGGED IN THIS FILE. It receives an assembled `Target` and
hands its fields to the driver; the keyring lookup lives in `sandbox_target` and the printed
form is `redacted()`. Nothing here writes a credential to stdout — `main` prints the redacted
form, and the unreachable error carries the redacted form for the same reason.
"""

from __future__ import annotations

import sys
from contextlib import contextmanager
from typing import TYPE_CHECKING

import psycopg
from psycopg.rows import dict_row

from substrate.sandbox_target import RELATIONS_QUERY, Target, reset_statements, target

if TYPE_CHECKING:
    from collections.abc import Iterator

    # ⚑⚑ `DictRow` MOVED HERE FROM `from psycopg import ...` IN Ⓝ128c, AND THE OLD SPELLING WAS
    # A LATENT `ImportError` RATHER THAN A STYLE POINT. `psycopg` does not export `DictRow` from
    # its root; the stub falsely claimed it did, so this line type-checked green and would have
    # raised the moment it ran. It never ran only because it sits under `TYPE_CHECKING` —
    # dropping that guard, or a `get_type_hints` call on anything in this module, would have
    # surfaced it. `Connection` IS genuinely exported, which is why the two could share one
    # statement undetected. `substrate/stub_reexport` is what found it.
    from psycopg import Connection
    from psycopg.rows import DictRow

#: Seconds to wait for the store before giving up.
#:
#: ⚑ A CEILING ON WAITING, NOT A PREDICTION — the same reading the observability discipline
#: gives its verify deadline. Too generous costs nothing when the connection succeeds; too tight
#: reports a reachable store as unreachable, which is the more expensive wrong answer.
CONNECT_TIMEOUT_S = 10


class UnreachableError(Exception):
    """The sandbox store could not be reached — a fact about TRANSPORT, not about a query.

    ⚑ IT IS A DISTINCT TYPE BECAUSE THE REPAIR IS DISTINCT. A caller catching this knows to
    check the host, the port and whether the listener moved; a caller catching a query error
    knows to check the statement. The predecessor raised one kind for both, so a cutover that
    retired the host listener surfaced looking like a data problem.
    """


class RowShapeError(TypeError):
    """A row did not carry the text columns the caller was promised.

    ⚑ IT IS A `TypeError` BECAUSE THAT IS WHAT IT IS — the adapter produced a value of a type
    the caller cannot use. Raising it as its own class rather than a bare `TypeError` lets a
    caller tell "the store answered in an unexpected shape" from any other type fault nearby.
    """


def descriptor(row: DictRow, *keys: str) -> tuple[str, ...]:
    """Read the named columns out of one row, refusing any that is not text.

    ⚑⚑ THIS IS THE NARROWING, IN ONE PLACE, AND THAT MATTERS MORE THAN IT LOOKS. A first draft
    had the `isinstance` checks inline in the reader and again in the selftest — two spellings
    of one rule, which is the drift this tree keeps recording. The rule lives here; the reader
    calls it and the cases call the same function, so a case cannot pass against a copy of the
    logic the reader no longer runs.

    ⚑ AN ABSENT COLUMN AND A NON-TEXT ONE ARE THE SAME ANSWER HERE, deliberately: both mean the
    result set is not the one this code was written against, and both send a reader to the
    query. The message names the column and what arrived, so they stay distinguishable to a
    person without being two exception types a caller would handle identically.
    """
    out: list[str] = []
    for key in keys:
        value = row.get(key)
        if not isinstance(value, str):
            msg = f"column {key!r} is {type(value).__name__}, expected str"
            raise RowShapeError(msg)
        out.append(value)
    return tuple(out)


def _connect(tgt: Target) -> Connection[DictRow]:
    """Open one connection to the assembled target, rows rendered as mappings.

    ⚑ THE TIMEOUT IS PASSED AS A CONNECTION KEYWORD, not enforced by a wrapper around the call.
    libpq owns the attempt loop — it may try several addresses for one host — and a timeout
    imposed from outside would cut across that, reporting a timeout on a host the driver had
    already moved past.

    ⚑ THE PASSWORD IS PASSED AS `None` WHEN THERE IS NONE, which libpq treats as unset — the
    same distinction `Target.keywords` preserves by OMITTING the key. A present-but-empty
    password is an ATTEMPT, so the server would report a wrong credential where none was ever
    supplied, and two absences needing different repairs would collapse into one message.
    """
    try:
        return psycopg.connect(
            host=tgt.host,
            port=tgt.port,
            dbname=tgt.dbname,
            user=tgt.user,
            password=tgt.password,
            connect_timeout=CONNECT_TIMEOUT_S,
            row_factory=dict_row,
        )
    except psycopg.OperationalError as exc:
        msg = f"sandbox store unreachable at {tgt.redacted()}"
        raise UnreachableError(msg) from exc


@contextmanager
def connection(tgt: Target | None = None) -> Iterator[Connection[DictRow]]:
    """Yield a connection to the sandbox, closed on the way out whatever happened.

    `tgt` defaults to a freshly assembled target, re-read from the environment and the keyring
    on every call — a cached target cannot notice a cutover, which is the defect the target
    module exists to repair, and caching one here would reintroduce it one layer up.

    ⚑⚑ IT CLOSES BUT DOES NOT COMMIT, WHICH IS THE OPPOSITE OF `psycopg`'s OWN BLOCK. Entering a
    `Connection` as a context manager COMMITS on a clean exit; that is a reasonable default for
    a driver and a bad one for a wrapper whose callers include a destructive reset. A caller
    here commits when it means to. The stub declares psycopg's behaviour in its `__exit__` for
    exactly this reason — so the difference is readable rather than surprising.
    """
    conn = _connect(tgt if tgt is not None else target())
    try:
        yield conn
    finally:
        conn.close()


def relations(conn: Connection[DictRow]) -> list[tuple[str, str]]:
    """Read every relation a reset would drop, as `(name, kind)` pairs."""
    pairs: list[tuple[str, str]] = []
    for row in conn.execute(RELATIONS_QUERY).fetchall():
        name, kind = descriptor(row, "table_name", "table_type")
        pairs.append((name, kind))
    return pairs


def reset(conn: Connection[DictRow]) -> list[str]:
    """Drop every relation in the sandbox, returning the statements that were run.

    ⚑ IT RETURNS WHAT IT RAN. A reset that reports only success leaves an operator unable to
    tell an already-empty sandbox from a reset that found nothing to do — two states with
    different next actions, and the `absent`-versus-`empty` collapse this tree refuses elsewhere.

    ⚑ IT COMMITS EXPLICITLY, because `connection()` deliberately does not. A destructive
    operation relying on an implicit commit at block exit would be undone by any later change to
    how that block ends.
    """
    statements = reset_statements(relations(conn))
    for stmt in statements:
        conn.execute(stmt)
    conn.commit()
    return statements


#: Who the connection authenticated as, and where it landed — read from the server, not the target.
IDENTITY_QUERY = "SELECT current_user AS role, current_database() AS db"


def probe_report(
    role: str, db: str, relations: list[tuple[str, str]], counts: dict[str, int] | None = None
) -> str:
    """Render what a read-only probe saw: the SERVER's identity and the relation census.

    ⚑⚑ THE IDENTITY IS THE SERVER'S ANSWER, NOT THE TARGET'S. A target names who we MEANT to be;
    `current_user`/`current_database()` is who the server ACCEPTED — the two differ exactly when a
    tenant is mis-wired, which is the failure this probe exists to catch before anything writes.
    ⚑ AN EMPTY DATABASE PRINTS ITS DENOMINATOR, `0 relation(s)`, never a bare nothing: a freshly
    provisioned tenant IS empty, and silence would read as a probe that failed.
    ⚑ EVERY COUNTED TABLE PRINTS ITS COUNT, ZERO INCLUDED: the question the counts answer is
    whether a write LANDED, and an omitted zero is indistinguishable from a table never read.
    """
    kinds: dict[str, int] = {}
    for _name, kind in relations:
        kinds[kind] = kinds.get(kind, 0) + 1
    by_kind = ", ".join(f"{n} {k}" for k, n in sorted(kinds.items())) or "empty"
    head = f"connected as {role} to {db}\n{len(relations)} relation(s) — {by_kind}\n"
    if counts is None:
        return head
    rows = "".join(f"  {counts[name]:>12}  {name}\n" for name in sorted(counts))
    return head + rows + f"{sum(counts.values())} row(s) over {len(counts)} table(s)\n"


def row_counts(conn: Connection[DictRow], relations: list[tuple[str, str]]) -> dict[str, int]:
    """Count the rows of every BASE TABLE — the witness that a write landed.

    ⚑ THE NAME IS QUOTED AS AN IDENTIFIER, never interpolated bare: it comes from the server's
    catalogue, but a relation name is data, and a quoted identifier cannot become a statement.
    """
    out: dict[str, int] = {}
    for name, kind in relations:
        if kind != "BASE TABLE":
            continue
        ident = '"' + name.replace('"', '""') + '"'
        row = conn.execute(f"SELECT count(*) AS n FROM {ident}").fetchone()  # noqa: S608
        value = None if row is None else row.get("n")
        if not isinstance(value, int):
            msg = f"count of {name!r} is {type(value).__name__}, expected int"
            raise RowShapeError(msg)
        out[name] = value
    return out


def probe() -> str:
    """Connect to the sandbox READ-ONLY and report identity + relations; write nothing."""
    with connection() as conn:
        row = conn.execute(IDENTITY_QUERY).fetchone()
        if row is None:
            msg = "the identity query returned no row"
            raise RowShapeError(msg)
        role, db = descriptor(row, "role", "db")
        rels = relations(conn)
        counts = row_counts(conn, rels)
        conn.rollback()
    return probe_report(role, db, rels, counts)


def _raises(row: DictRow) -> bool:
    """Report whether the narrowing refuses this row."""
    try:
        descriptor(row, "table_name", "table_type")
    except RowShapeError:
        return True
    else:
        return False


def main(argv: list[str]) -> int:
    """Report the sandbox target.

    ⚑⚑ `--selftest` IS DISPATCHED FROM THE `__main__` GUARD, NOT FROM HERE. A branch inside this
    function returns, and `return` is invalid at module level — so `module_trim` could not re-home
    the cases while their dispatch lived in a function body (gate-G327). Rewriting the branch to
    `sys.exit` was refused for a better reason: a reachable `SystemExit` takes the exit decision
    from anything that imports this module (gate-G329). Moving the dispatch into the guard, where
    the block never runs on import, is the repair that costs neither property.
    """
    if argv == ["--probe"]:
        # ⚑ READ-ONLY: identity + relation census, rolled back, nothing written (2026-09-22,
        # the first contact with luthen's provisioned tenant).
        try:
            sys.stdout.write("tenant : sandbox\n" + probe())
        except UnreachableError as exc:
            sys.stderr.write(f"sandbox-connect: {exc}\n")
            return 1
        return 0
    if argv:
        sys.stderr.write("usage: python3 -m substrate.sandbox_connect [--probe | --selftest]\n")
        return 2
    sys.stdout.write(f"tenant : sandbox\ntarget : {target().redacted()}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
