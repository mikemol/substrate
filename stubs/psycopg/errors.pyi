# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The exception hierarchy, at the module psycopg defines it in.

⚑⚑ THE WHOLE REASON THESE CLASSES ARE RESTATED IS ONE CONSTRUCTOR. psycopg's own types are
concrete throughout this hierarchy except for `Error.__init__`, which is `*args: Sequence[Any]`,
and `__reduce__`, which returns `tuple[Any, ...]`. Referring to the CLASS drags its constructor
signature along, so the bare expression `psycopg.Error` in an `except` clause is an `Any`
expression and is REFUSED under `disallow_any_expr` — measured, not predicted. Nothing about
catching an error needs that latitude, and this is a `Any` in pickling and varargs machinery
that a caller never touches.

⚑ THE KEYWORD PARAMETERS ARE DECLARED, NOT DROPPED. `info`, `encoding` and `pgconn` are on the
runtime constructor; omitting them would be the retreat this stub was commissioned to avoid, and
`stubtest` reports it as an inconsistent signature besides. `info` and `pgconn` are typed
`object` because their real types (`ErrorInfo`, `PGconn`) belong to the `pq` layer this stub
does not cover — a caller constructing an `Error` with them needs that layer typed, which is
work, and is said here rather than hidden by leaving the parameters out.

⚑ THE HIERARCHY IS THE DBAPI ONE AND ITS SHAPE IS LOAD-BEARING. `OperationalError` is what a
connect failure arrives as; a caller distinguishing "cannot reach the store" from "the store
refused the statement" depends on that being a distinct class rather than a message.
"""

class Warning(Exception):  # noqa: A001, N818
    """Defined for DBAPI compatibility; psycopg never raises it."""

class Error(Exception):
    """Base of every error psycopg raises — catch this to catch them all."""

    sqlstate: str | None
    def __init__(
        self,
        *args: object,
        info: object = None,
        encoding: str = "utf-8",
        pgconn: object | None = None,
    ) -> None: ...

class InterfaceError(Error):
    """A fault in the interface rather than the database — a closed connection, say."""

class DatabaseError(Error):
    """A fault the database itself reported.

    ⚑ `__init_subclass__` IS DECLARED BECAUSE psycopg USES IT AS A REGISTRATION HOOK, not as
    boilerplate. Every sqlstate-specific error class below is registered by passing `code` and
    `name` in its class statement, which is how `lookup()` resolves a five-character sqlstate to
    a class. A stub omitting it reports as drift — and hides the mechanism that makes the
    hierarchy self-populating.
    """

    def __init_subclass__(cls, code: str | None = None, name: str | None = None) -> None: ...

class DataError(DatabaseError):
    """The processed data was wrong — a bad cast, a value out of range."""

class OperationalError(DatabaseError):
    """A fault in the database's operation: the connection dropped, the server is gone.

    ⚑ THIS IS WHAT A CONNECT FAILURE ARRIVES AS, which is why a wrapper around `connect` catches
    this rather than `Error` when it means to separate transport from query.
    """

class IntegrityError(DatabaseError):
    """A constraint was violated."""

class InternalError(DatabaseError):
    """The database reached an inconsistent internal state."""

class ProgrammingError(DatabaseError):
    """The statement was wrong: bad syntax, an undefined table, the wrong parameter count."""

class NotSupportedError(DatabaseError):
    """The operation is not supported by the database."""

class ConnectionTimeout(OperationalError):
    """The connection attempt exceeded its `connect_timeout`."""
