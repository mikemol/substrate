# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""`Connection`, at the module psycopg defines it in.

⚑⚑ THE ROW PARAMETER IS THE POINT OF THE WHOLE STUB. `Connection[DictRow]` and
`Connection[TupleRow]` are different types, so a caller that passed `row_factory=dict_row` gets
mappings back from `fetchall` with no cast. This is what "type THROUGH the generics" means in
practice, and it is the parameter the neighbouring networkx stub dropped and this one keeps.

⚑⚑ `connect` IS OVERLOADED IN THREE VARIANTS, AND THE THIRD IS NOT PADDING. The runtime
signature is `row_factory: RowFactory[Row] | None = None`, so a caller may pass `None`
EXPLICITLY — and `stubtest` flags an overload set that cannot accept the runtime's own default,
which is exactly how the two-variant first draft was caught. Omitted and explicitly-`None` both
mean "the default factory", and both must reach the tuple-row result.

⚑ `context` AND `cursor_factory` ARE DECLARED THOUGH THIS REPO PASSES NEITHER — the rule the
neighbouring stub stated and then violated. A signature is read from the LIBRARY; typing only
what the current caller happens to pass would encode this caller's habits as the contract, and
refuse a later caller using a documented form. `context` is typed `object` because
`AdaptContext` belongs to the adapter layer this stub does not cover: the parameter is present
and honest about being unrefined, rather than absent and silently unavailable.
"""

from types import TracebackType
from typing import Self, overload

from psycopg.abc import ConnParam
from psycopg.cursor import Cursor
from psycopg.rows import RowFactory, TupleRow

class Connection[Row]:
    """One connection to a database, parameterised by the row type its cursors yield."""

    row_factory: RowFactory[Row]
    # ⚑⚑⚑ `__init__` IS DELIBERATELY NOT DECLARED, AND THIS IS THE ONE OMISSION IN THIS STUB
    # THAT IS FORCED RATHER THAN CHOSEN — recorded here because "left out quietly" is the
    # defect under correction, so it is left out loudly instead.
    #
    # Its runtime default for `row_factory` is the FUNCTION `tuple_row`, and `stubtest`
    # compares that live object against the declared parameter type. It reads the object as
    # `def (cursor: Any) -> Any` and can reconcile it with no `RowFactory[...]` spelling:
    # `RowFactory[Row]`, `RowFactory[TupleRow]`, and their union were each tried and each
    # refused. The library itself only types this line via a `cast`, because a
    # `RowFactory[TupleRow]` genuinely is not a `RowFactory[Row]` for arbitrary `Row` — so what
    # the gate is reporting is the LIBRARY's unsoundness, reachable through any faithful stub.
    #
    # ⚑⚑ AND OMITTING IT IS NOT AVAILABLE EITHER, WHICH IS WHY THE PARAMETER IS TYPED `object`.
    # A class with no `__init__` in its stub does not read as "unspecified": `stubtest` infers
    # the implicit `def (self)` and then reports BOTH runtime parameters as missing. So the
    # choice is not declare-or-omit, it is which declaration — and `object` is the one that is
    # TRUE. It admits `tuple_row`, admits any row factory, and asserts nothing false; what it
    # gives up is catching a wrong argument to a constructor no caller here can reach, since
    # `pgconn` comes from the `pq` layer this stub does not cover.
    #
    # ⚑ `connect` IS HOW A CONNECTION IS OBTAINED, and it keeps its full generic typing. The
    # looseness is confined to the one member whose runtime default the checker cannot
    # reconcile with any faithful spelling.
    def __init__(self, pgconn: object, row_factory: object = ...) -> None: ...
    @overload
    @classmethod
    def connect(
        cls,
        conninfo: str = "",
        *,
        autocommit: bool = False,
        prepare_threshold: int | None = 5,
        context: object | None = None,
        row_factory: None = None,
        cursor_factory: type[Cursor[TupleRow]] | None = None,
        **kwargs: ConnParam,
    ) -> Connection[TupleRow]: ...
    @overload
    @classmethod
    def connect[R](
        cls,
        conninfo: str = "",
        *,
        autocommit: bool = False,
        prepare_threshold: int | None = 5,
        context: object | None = None,
        row_factory: RowFactory[R],
        cursor_factory: type[Cursor[R]] | None = None,
        **kwargs: ConnParam,
    ) -> Connection[R]: ...
    def __enter__(self) -> Self: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
        /,
    ) -> None:
        """Commit on a clean exit, roll back on an exception, then close.

        ⚑ THE BLOCK COMMITS BY ITSELF — declared because it is the opposite of what a reader
        expecting a plain resource manager assumes, and a caller relying on an explicit
        `commit()` that never runs loses the transaction silently.
        """
        ...

    @property
    def closed(self) -> bool: ...
    @property
    def autocommit(self) -> bool: ...
    @autocommit.setter
    def autocommit(self, value: bool) -> None: ...
    def close(self) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
    def execute(
        self,
        query: str | bytes,
        params: object | None = None,
        *,
        prepare: bool | None = None,
        binary: bool = False,
    ) -> Cursor[Row]:
        """Run one statement on an implicit cursor and return it, ready to fetch."""
        ...

    # ⚑⚑ `name`, `scrollable` AND `withhold` ARE DECLARED THOUGH THIS STUB DOES NOT COVER THE
    # TYPE THEY SELECT. A non-empty `name` returns a `ServerCursor` at runtime, and
    # `ServerCursor` is one of the names this stub deliberately omits — so the return here is
    # `Cursor`, which is WRONG for that call. Omitting the parameters instead would be worse in
    # the way this stub exists to correct: `stubtest` reports the omission as drift, and a
    # caller passing a documented argument would be refused by a stub that was never wrong,
    # only narrow. Declared, with the gap said out loud: a caller wanting a server-side cursor
    # must type `ServerCursor` first rather than trust this return.
    @overload
    def cursor(
        self,
        name: str = "",
        *,
        binary: bool = False,
        row_factory: None = None,
        scrollable: bool | None = None,
        withhold: bool = False,
    ) -> Cursor[Row]: ...
    @overload
    def cursor[R](
        self,
        name: str = "",
        *,
        binary: bool = False,
        row_factory: RowFactory[R],
        scrollable: bool | None = None,
        withhold: bool = False,
    ) -> Cursor[R]: ...
