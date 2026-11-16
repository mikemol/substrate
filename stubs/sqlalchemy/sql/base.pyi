"""`ColumnCollection` and `ReadOnlyColumnCollection` — the two-parameter generic at the centre.

⚑⚑⚑ THIS GENERIC IS THE WHOLE ARGUMENT THAT THE LIBRARY'S `Any` IS INCIDENTAL. Upstream returns
`ReadOnlyColumnCollection[str, Column[Any]]` from `Table.c`, and the prior reading of that was
that a dynamic string key FORCES the value to be `Any`. It does not: `ColumnCollection` is
`Generic[_COLKEY, _COL_co]` — the key is `_COLKEY` and the value is a SEPARATE parameter. The
key being a runtime string says nothing about the element type, so the `Any` is a parameter the
library declined to thread, not one the design requires.

⚑ `_COLKEY` IS CONSTRAINED, NOT BOUND, and the difference is upstream's. It admits exactly
`None | str` or `str` — a value type must be one of the listed constraints rather than any
subtype of a bound. Restating it as a bound would widen what the collection accepts as a key.

⚑ `_COL_co` IS COVARIANT AND BOUNDED, and both halves were forced by findings. Without the
BOUND, mypy refuses `ReadOnlyColumnCollection[str, Column[object]]` outright (*must be a subtype
of ColumnElement*); without COVARIANCE, a collection of `Column` cannot be read where a
collection of the wider element is expected, which is precisely how `Table.c` and
`Insert.excluded` relate to each other.

⚑ THE BOUND IS SPELLED `ColumnElement[object]`, NOT `ColumnElement[Any]` AS UPSTREAM SPELLS IT.
`object` is the honest top type for a bound whose parameter is genuinely unconstrained, and it
carries no `Any` into a file whose purpose is removing two of them.
"""

from collections.abc import Iterable, Iterator
from typing import Generic, TypeVar

from sqlalchemy.sql.elements import ColumnElement

_COLKEY = TypeVar("_COLKEY", None, str)
_COL_co = TypeVar("_COL_co", bound=ColumnElement[object], covariant=True)

class ColumnCollection(Generic[_COLKEY, _COL_co]):
    def __init__(
        self, columns: Iterable[tuple[_COLKEY, _COL_co]] | None = None
    ) -> None: ...
    def __getitem__(self, key: _COLKEY) -> _COL_co: ...
    def __contains__(self, key: str) -> bool: ...
    def __iter__(self) -> Iterator[_COL_co]: ...
    def __bool__(self) -> bool: ...
    def keys(self) -> list[_COLKEY]: ...
    def values(self) -> list[_COL_co]: ...
    def items(self) -> list[tuple[_COLKEY, _COL_co]]: ...

class ReadOnlyColumnCollection(ColumnCollection[_COLKEY, _COL_co]):
    """A read-only facade over a `ColumnCollection` — what `Table.c` and `.excluded` return.

    ⚑⚑ ITS CONSTRUCTOR IS NOT THE INHERITED ONE, AND STUBTEST CAUGHT THE DIFFERENCE AS A RENAMED
    PARAMETER. Inheriting `ColumnCollection.__init__` gave this class a `columns:
    Iterable[...] | None = None`; the runtime takes a REQUIRED `collection: ColumnCollection`.
    Two breaks in one: a keyword call would raise `TypeError`, and an argument-less construction
    would type-check clean and fail.

    ⚑ THIS IS THE `panflute.load` SHAPE — the one real DRIFT `check_stub_authority` has caught in
    this tree, where a stub named a parameter `source` and the runtime spelled it
    `input_stream`. It survived there only because both call sites passed positionally. Recorded
    because it is the same class arriving again, in a stub written after reading that incident.
    """

    def __init__(self, collection: ColumnCollection[_COLKEY, _COL_co]) -> None: ...
