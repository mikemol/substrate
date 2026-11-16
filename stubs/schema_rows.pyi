"""`schema_rows` - narrowed to what its `jea/metalanguage` consumers need.

CONSUMER 1 (W63, the `schema.py` decomposition arc): `jea/metalanguage/schema_probe.py`
builds and returns `Row` instances.

CONSUMER 2 (W63, same arc): `jea/metalanguage/schema_establish.py`'s `--establish`
dispatch calls `_cli_connect` to resolve a connection (the same resolver `probe()`
used to call directly, now re-exported for this second caller), `relations` to read
the store's current relation set before/after a write, and `apply` to create one
tier's tables. All three are read from `jea/metalanguage/schema_rows.py:927`,
`:323` and `:810` respectively.

CONSUMER 3 (W63, same arc): `jea/metalanguage/schema_transport.py`'s `--transport`
dispatch calls `transport_report`, a no-argument reader of the write path's own
driver properties (`jea/metalanguage/schema_rows.py:411`). It takes no connection
and no tier - it imports `psycopg` itself and returns a plain `dict[str, object]`.

CONSUMER 4 (W63, same arc): `jea/metalanguage/schema_reclaim_core.py`'s
`--reclaim-core ID` dispatch calls `_cli_connect` (shared with consumer 2) and
`scalar` to ask `obs` directly whether a core has any staged rows at all, since
`reclaim_core`'s own dry-run counts answer a different question (rows matching
the licence, not rows present).

Everything else `schema_rows` defines (`rows`, `upsert`, `ph`, `execute`, ...)
is declined - no consumer here reads it.
"""

from collections.abc import Sequence
from typing import TYPE_CHECKING, SupportsIndex, overload

if TYPE_CHECKING:
    from store import Connection

def _cli_connect(mode: str = ...) -> Connection: ...
def relations(con: Connection, back: str | None = ...) -> dict[str, str]: ...
def apply(con: Connection, back: str | None = ..., only: str | None = ...) -> int: ...
def transport_report() -> dict[str, object]: ...
def scalar(con: Connection, sql: str, params: tuple[object, ...] = ...) -> object: ...

class Row(tuple[object, ...]):
    def __new__(cls, keys: Sequence[str], values: Sequence[object]) -> Row: ...
    @overload
    def __getitem__(self, k: SupportsIndex) -> object: ...
    @overload
    def __getitem__(
        self, k: slice[SupportsIndex | None, SupportsIndex | None, SupportsIndex | None]
    ) -> tuple[object, ...]: ...
    @overload
    def __getitem__(self, k: str) -> object: ...
    def keys(self) -> Sequence[str]: ...
    def get(self, k: str, default: object = ...) -> object: ...
    def as_dict(self) -> dict[str, object]: ...
