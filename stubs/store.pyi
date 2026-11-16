"""`store` - narrowed to what its two `jea/metalanguage` consumers need.

CONSUMER 1 (W63, the `schema.py` decomposition arc): `jea/metalanguage/schema_probe.py`
calls `store.tenant(...)` to resolve a connection when its caller passes none, then
drives it through `Cursor`'s `execute`/`description`/iteration contract (shared across
psycopg and sqlite3). `description` is narrowed to "first element is the column name"
(true of both DBAPI2 drivers this repo targets) rather than the full 7-tuple shape, and
a row is narrowed to "a mapping or a plain sequence" (psycopg's `dict_row` vs a bare
tuple), because those are the only shapes this consumer reads.

CONSUMER 2 (W63, same arc): `jea/metalanguage/schema_establish.py`'s `--establish`
dispatch also calls `_cli_connect` (which itself returns `store.tenant(...)`) and, under
`--apply`, calls `con.commit()` once its DDL loop completes - `Connection.commit` is
added for this reader; `schema_probe.py` never writes, so it never needed it.

CONSUMER 3 (W63, same arc): `jea/metalanguage/schema_reclaim.py`'s `--reclaim`
dispatch calls `store.sandbox_connect(reset=False)` under `--sandbox` to route the
sweep at the throwaway tenant instead of the live one - `sandbox_connect` is added
for this reader.

Everything else `store` defines (`connect`, `backend`, the credential resolver, ...)
is declined - no consumer here reads it.
"""

from collections.abc import Iterator, Mapping, Sequence
from typing import Protocol

class Cursor(Protocol):
    description: Sequence[tuple[str, ...]] | None
    def execute(self, sql: str, params: object = ...) -> None: ...
    def __iter__(self) -> Iterator[Mapping[str, object] | Sequence[object]]: ...

class Connection(Protocol):
    def cursor(self) -> Cursor: ...
    def commit(self) -> None: ...

def tenant(
    argv: Sequence[str] | None = ...,
    mode: str = ...,
    label: str = ...,
    require: str | None = ...,
) -> Connection: ...
def sandbox_connect(reset: bool = ...) -> Connection: ...
