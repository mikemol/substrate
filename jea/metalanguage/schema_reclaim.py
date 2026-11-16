# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""`--reclaim` CLI dispatch -- `schema.py`'s corpus-wide GC sweep.

EXTRACTED 2026-10-02 (W63, incremental-extraction pass off the `mikemol-pycheck`
refusal on `schema.py`: *"this file cannot be made clean in one edit ...
extract the concern you need into a NEW module written clean in one pass,
then retire this file"*).

VERIFIED BEFORE EXTRACTING -- the one open question for this arm was whether
`schema_selftest.py`'s `_inspect.getsource(...)` introspection pins THIS
dispatch block or the `reclaim()` FUNCTION it calls. It is the latter:
`schema_selftest.py` runs `_inspect.getsource(reclaim)` (the function bound
via `from schema import *`, defined in `schema_queue.py:490`) and asserts
substrings of ITS BODY (`"obs_node"`, `"UNMEASURED"`,
`"DELETE FROM obs WHERE core_id"`, ...) -- never `getsource(schema)` sliced
around a `"--reclaim"` marker. The ONLY module-source text-slice in that file
is `getsource(schema)` cut between the literal markers
`'if "--holes" in sys.argv:'` and `'if "--fibre"'`, which this arm's dispatch
line is nowhere near. So moving the `--reclaim` CLI block leaves nothing the
suite's text-slice depends on; `reclaim()` itself stays exactly where it is,
in `schema_queue.py`, untouched by this extraction.

WHY THIS ARM. Self-contained the same way `--flush`/`--establish` were: it
depends only on `reclaim` itself (already in `schema_queue.py`, not in
`schema.py`), `store.sandbox_connect` for the `--sandbox` override, and the
invocation's own `argv`. No other dispatch branch, no module-level state in
`schema.py`, nothing `schema_selftest` reads out of this one by name or by
source-slice.
"""

from __future__ import annotations

import store as _store
from schema_queue import reclaim


def reclaim_dispatch(argv: list[str]) -> int:
    """Run `--reclaim`'s dispatch over `argv`; return the process exit code.

    `schema.py`'s `__main__` block calls this as
    `raise SystemExit(reclaim_dispatch(sys.argv))` when `"--reclaim" in argv`
    -- the same call shape every other report-returning dispatch branch in
    that file already uses.

    Retires every core the durable tier can rebuild -- the per-core licence,
    no floor and no pin. Dry-run by default, `--apply` to write.

    `reclaim()` already takes a connection; the original dispatch simply
    never passed one, so the only reachable target was the live store. The
    `--sandbox` flag routes to `store.sandbox_connect` instead, since the
    drain has never run and the first place to run it is the tenant that
    exists to be harmed.
    """
    apply_it = "--apply" in argv
    rc = _store.sandbox_connect(reset=False) if "--sandbox" in argv else None
    r = reclaim(con=rc, dry_run=not apply_it)
    floor = "none" if r["floor"] is None else format(r["floor"], ",")
    print(f"floor   {floor}")
    print(f"obs     {r['obs']:,}")
    # `edge` is reported beside `obs` because it is the larger half (⑹, 2026-08-12):
    # `edge` held 627,077 rows -- 46% of the store -- while `obs` held 0, so a report
    # naming only `obs` describes the smaller relation and reads as the whole sweep.
    # `.get` rather than `[...]`: the `obs_node`-absent REFUSAL returns before either
    # count exists, and that branch must stay printable rather than raising a KeyError
    # over a held sweep.
    edge = "-" if r.get("edge") is None else format(r["edge"], ",")
    print(f"edge    {edge}")
    events = "-" if r["events"] is None else format(r["events"], ",")
    print(f"events  {events}")
    print(f"why     {r['why']}")
    return 0
