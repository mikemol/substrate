"""`schema_queue` - narrowed to the names its extracted CLI-dispatch consumers need.

DECLARED FOR FOUR CONSUMERS (W63, the `schema.py` decomposition arc):
`jea/metalanguage/schema_probe.py` imports `_require_pg` to refuse a non-postgres
backend before issuing a probe read, `schema_flush.py` imports `flush` for
the `--flush TIER...` dispatch, `schema_reclaim.py` imports `reclaim` for
the `--reclaim` dispatch, and `schema_reclaim_core.py` imports `reclaim_core`
and `reclaim_verdict` for the `--reclaim-core ID` dispatch. Everything else
`schema_queue` defines (`hwm`, `activity`, ...) is declined — no consumer here
reads it.

`reclaim`'s and `reclaim_core`'s returns are narrowed to a `Mapping[str, object]`
rather than a typed dict: the dispatches only ever read a handful of keys
(`r["floor"]`, `r["obs"]`, `r.get("edge")`, `r["events"]`, `r["why"]`, and for
`reclaim_core` also `r["licensed"]`), each already guarded at the read site for
a possible `None`/falsy value.
"""

from collections.abc import Mapping

from store import Connection

def _require_pg(what: str) -> None: ...
def flush(
    tiers: list[str], con: Connection | None = ..., dry_run: bool = ...
) -> list[str]: ...
def reclaim(
    con: Connection | None = ...,
    chunk: int = ...,
    budget: int | None = ...,
    dry_run: bool = ...,
) -> Mapping[str, object]: ...
def reclaim_core(
    core_id: str, con: Connection | None = ..., dry_run: bool = ...
) -> Mapping[str, object]: ...
def reclaim_verdict(licensed: bool, staged_any: object) -> str: ...
