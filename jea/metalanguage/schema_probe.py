# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""`probe()` - run one read against the tenant THIS INVOCATION NAMED.

Split out of `schema.py` (W63, the schema.py decomposition arc) as the next
self-contained unit after `schema_modes.py`. `probe` has no `getsource`-slice
dependency anywhere in the tree (unlike `--holes`, which `schema_selftest`
pins in place by slicing `schema.py`'s own source text between two literal
markers) - `--binding probe` finds exactly one definition, here, and nothing
reads this module's source as data. So the function moves outright.
"""

from collections.abc import Sequence
from typing import TYPE_CHECKING

from schema_queue import _require_pg
from schema_rows import Row

if TYPE_CHECKING:
    from store import Connection


def probe(
    sql: str,
    params: Sequence[object] = (),
    con: "Connection | None" = None,
    require: str | None = None,
) -> list[Row]:
    """Run one read against the tenant THIS INVOCATION NAMED and return its rows.

    This is the "ask postgres rather than assert" instrument.

    THIS EXISTS SO A DESIGN QUESTION IS MEASURED, NOT REMEMBERED. Deciding whether
    `pg_visible_in_snapshot` exists, what `xmin` compares as, or how a plan degrades was
    otherwise a `python3 -c` against the LIVE store -- a composition, and one pointed at
    the source of truth. The sandbox was enrolled for exactly this and had no reader.

    IT USED TO HARDCODE THE SANDBOX (`sandbox=True`), AND THAT MADE IT UNUSABLE FOR THE
    QUESTIONS IT EXISTS TO ANSWER. Measured 2026-08-22: three separate structural
    questions about the LIVE corpus -- the widest event document, whether
    `UnknownFVs`/`KnownFVs` both intern, what a `QName` node's children are -- each came
    back `0 row(s) [sandbox]` against an empty tenant, and the honest-looking output gave
    no hint that the question had been redirected. `--plan` does not execute and
    `--probe` could not reach live, so the reader was routed to composing shell instead,
    which is the shape the standing rule forbids.

    THE OLD DEFAULT'S ARGUMENT WAS ABOUT WRITES AND DID NOT REACH READS. It read: "a
    probe is a question, and a question should not be able to mutate the corpus by
    forgetting a flag." Sound about mutation, and the protection it actually bought was
    `store.sandbox_connect` keeping the entry points distinct -- which is unchanged.
    What the default ADDED was a silent tenant redirect on the read path, and a read
    against the wrong tenant returns plausible rows nobody can distinguish (memory:
    `wrong-tenant-read-is-silent`). That is the worse failure of the two.

    SO THE CHOICE MOVES TO THE INVOCATION, resolved by `store.tenant` like every other
    mode: `--live` or `--sandbox`, STATED, with a refusal when neither is. Callers
    passing their own `con` are unaffected; there is no tenant default left to forget.
    """
    # A NON-RETURNING STATEMENT IS A SUCCESS, NOT AN ERROR. `rows()` demands a result
    # set, so a sandbox `CREATE TABLE` raised ProgrammingError AFTER the DDL had already
    # run -- an exception reporting a completed operation, which is the worst kind: the
    # reader concludes it failed and re-runs. Probing a design question needs DDL as much
    # as SELECT, so the distinction is handled here rather than pushed onto the caller.
    _require_pg("probe()")
    # ONE RESOLVER, the same one `_cli_connect` routes through. `store.tenant` reads
    # `--live`/`--sandbox` from the invocation and REFUSES when neither is stated, so the
    # "nobody chose" case is representable here instead of silently meaning sandbox.
    # `mode="ro"` ON THE LIVE ROUTE: a probe is a question. The sandbox route opens
    # read-write by design (it exists to be mutated), which is why DDL probes still work
    # there and are refused against live -- see `store.sandbox_connect`'s note.
    # `require=` IS NOT OPTIONAL POLISH -- WITHOUT IT THIS CHANGE POINTED THE SUITE'S DDL
    # PROBES AT THE CORPUS. `schema_selftest` calls `probe("CREATE TABLE _rc_probe(i int)")`
    # and `probe("CREATE TABLE _prune_probe(...)")`; under argv resolution those inherited
    # the invocation's tenant -- and `--selftest` names none, so `store.tenant`'s advisory
    # branch defaulted them to LIVE. Caught because the suite hung after four tenant
    # warnings, not because anything checked. A fixture's tenant is NOT the operator's to
    # choose, which is precisely the case `store.tenant(require=...)` exists for (same
    # escape as `edit_snapshot.guard(intent=...)`).
    if con is None:
        import store as _store

        con = _store.tenant(mode="ro", label="probe", require=require)
    cur = con.cursor()
    cur.execute(sql, params or None)
    if cur.description is None:
        return []
    return [
        Row(
            tuple(d[0] for d in cur.description),
            list(r.values()) if isinstance(r, dict) else list(r),
        )
        for r in cur
    ]
