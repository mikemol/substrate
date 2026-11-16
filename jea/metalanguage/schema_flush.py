# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""`--flush TIER...` CLI dispatch -- `schema.py`'s resetting twin of `--establish`.

EXTRACTED 2026-10-02 (W63, incremental-extraction pass off the `mikemol-pycheck`
refusal on `schema.py`: *"this file cannot be made clean in one edit ...
extract the concern you need into a NEW module written clean in one pass,
then retire this file"*). Verified before extracting: `schema_selftest.py`
pins `schema.py`'s own source text in exactly one place -- `getsource(schema)`
sliced between the literal markers `'if "--holes" in sys.argv:'` and
`'if "--fibre"'`, which drives both the `--holes`/`--fibre` cases and the
whole-module bypass-finder for `_store.connect(`. Neither marker, and no
`_store.connect(` call, appears in this arm -- it reaches the store only
through `flush()` itself (which resolves its own connection), same as every
other dispatch branch -- so moving it leaves nothing the suite's text slice
depends on.

WHY THIS ARM. Self-contained the same way `--establish` was: it depends only
on `_TIERS` (for the usage message) and `flush` itself (already in
`schema_queue.py`, not in `schema.py`), plus the invocation's own `argv`. No
other dispatch branch, no module-level state in `schema.py`, nothing
`schema_selftest` reads out of this one by name or by source-slice.
"""

from __future__ import annotations

from schema_decl import _TIERS
from schema_queue import flush


def flush_dispatch(argv: list[str]) -> int:
    """Run `--flush`'s dispatch over `argv`; return the process exit code.

    `schema.py`'s `__main__` block calls this as
    `raise SystemExit(flush_dispatch(sys.argv))` when `"--flush" in sys.argv`
    -- the same call shape every other report-returning dispatch branch in
    that file already uses (`coverage_emit()`, `establish_dispatch(argv)`,
    ...), so the extraction changes where the branch's BODY lives, never how
    `__main__` reaches it.

    `--flush` DROPs and recreates named tiers from the declaration -- correct
    for resetting a tier, catastrophic for establishing one beside live data
    (that is what `--establish` exists for instead). Dry-run by default,
    `--apply` to write, exactly like its twin.
    """
    i = argv.index("--flush")
    want = [a for a in argv[i + 1 :] if not a.startswith("-")]
    if not want:
        print(f"--flush needs at least one tier: {' '.join(sorted(_TIERS))}")
        return 2
    apply_it = "--apply" in argv
    try:
        steps = flush(want, dry_run=not apply_it)
    except ValueError as e:
        print(str(e))
        return 2
    for s in steps:
        print(("  RAN  " if apply_it else "  plan ") + s)
    verb = "applied" if apply_it else "-- re-run with --apply"
    print(f"{len(steps)} step(s) {verb}; tiers recreated from the declaration")
    return 0
