# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""`Cursor`, at the module psycopg defines it in.

⚑ THE ROW PARAMETER IS WHAT MAKES A FETCH CONCRETE. `Cursor[DictRow].fetchall()` returns
`list[dict[str, object]]` — the row factory's answer carried through the connection to here.
Erasing that parameter would return a list of unknowns and put a cast at every call site, which
is the shape this stub exists to not produce.
"""

from collections.abc import Iterable
from types import TracebackType
from typing import Self

from psycopg._cursor_base import BaseCursor
from psycopg.abc import Params, Query
from psycopg.connection import Connection
from psycopg.rows import RowFactory

class Cursor[Row](BaseCursor[Connection[Row], Row]):
    """A cursor over one result set, yielding rows of the type its factory produces."""

    def __init__(
        self, connection: Connection[Row], *, row_factory: RowFactory[Row] | None = None
    ) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
        /,
    ) -> None: ...
    def close(self) -> None: ...
    @property
    def row_factory(self) -> RowFactory[Row]: ...
    @row_factory.setter
    def row_factory(self, row_factory: RowFactory[Row]) -> None: ...
    def execute(
        self,
        query: Query,
        params: Params | None = None,
        *,
        prepare: bool | None = None,
        binary: bool | None = None,
    ) -> Self: ...
    def executemany(
        self, query: Query, params_seq: Iterable[Params], *, returning: bool = False
    ) -> None: ...
    def fetchone(self) -> Row | None:
        """The next record, or `None` once the result set is exhausted.

        ⚑ `None` IS EXHAUSTION, NOT AN ERROR, and a caller must keep that apart from a query
        that legitimately returned nothing. A cursor holding NO result at all raises instead, so
        the three states stay three.
        """
        ...

    def fetchmany(self, size: int = 0) -> list[Row]: ...
    def fetchall(self) -> list[Row]: ...
    def __iter__(self) -> Self: ...
    def __next__(self) -> Row: ...
    def scroll(self, value: int, mode: str = "relative") -> None: ...
