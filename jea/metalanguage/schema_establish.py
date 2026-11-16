# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""`--establish TIER...` CLI dispatch -- `schema.py`'s non-resetting twin of `--flush`.

EXTRACTED 2026-10-02 (W63, incremental-extraction pass off the `mikemol-pycheck`
refusal on `schema.py`: *"this file cannot be made clean in one edit ... extract
the concern you need into a NEW module written clean in one pass, then retire
this file"*). Verified before extracting: `schema_selftest.py` pins `schema.py`'s
own source text in exactly one place -- `getsource(schema)` sliced between the
literal markers `'if "--holes" in sys.argv:'` and `'if "--fibre"'`, which drives
both the `--holes`/`--fibre` cases and the whole-module bypass-finder for
`_store.connect(`. Neither marker, and no `_store.connect(` call, appears in
this arm -- it reaches the store only through `_cli_connect`, same as every
other dispatch branch -- so moving it leaves nothing the suite's text slice
depends on.

WHY THIS ARM. It is the first FULL CLI dispatch block extracted (the two prior
cuts, `schema_modes.py` and `schema_probe.py`, were a pure-data roster and a
library function respectively -- neither had a `sys.argv` branch of its own).
`--establish` is self-contained the same way: it depends only on `_TIERS` (the
tier -> relation-set declaration), `apply`/`relations`/`_cli_connect` (all three
already live in `schema_rows.py`, not in `schema.py` itself), and the
invocation's own `argv` -- no other dispatch branch, no module-level state in
`schema.py`, nothing `schema_selftest` reads out of this one by name or by
source-slice. `--migrate-views`, by contrast, deliberately SHARES its `if` line
with `--migrate-queue` (see that block's own note: *"a second block would be a
second copy of the empty-plan reading"*), so extracting it alone would mean
either splitting a fused conditional the design argues for keeping fused, or
dragging `--migrate-queue` out with it -- a larger, riskier cut than this pass
is scoped to.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from schema_decl import _TIERS
from schema_rows import _cli_connect, apply, relations

if TYPE_CHECKING:
    from store import Connection


def establish_dispatch(argv: list[str]) -> int:
    """Run `--establish`'s dispatch over `argv`; return the process exit code.

    `schema.py`'s `__main__` block calls this as
    `raise SystemExit(establish_dispatch(sys.argv))` when
    `"--establish" in sys.argv` -- the same call shape every other
    report-returning dispatch branch in that file already uses
    (`coverage_emit()`, `coverage_reap(...)`, `_selftest()`, ...), so the
    extraction changes where the branch's BODY lives, never how `__main__`
    reaches it.

    THIS EXISTS BECAUSE `--establish` IS `--flush`'s IDEMPOTENT TWIN, AND ITS
    ABSENCE FORCED AN INLINE SCRIPT. `--flush` DROPs and recreates: correct
    for resetting a tier, catastrophic for establishing one beside live data.
    The only route to `apply(con, only=TIER)` -- the declared, additive
    `CREATE TABLE ... IF NOT EXISTS` that 28 call sites already use
    internally -- was `python3 -c`, which this repo's own no-chaining hook
    refuses BY DESIGN: a live DDL write is exactly the judgement that must
    live in a program rather than evaporate with the turn.

    MEASURED 2026-08-17: `--equiv pack.sql pack.python` stalled twice at 600s
    and 300s against `relation "obs_node" does not exist`. The verification
    gate reads a tier only the FOLD establishes, so on a clean tenant the gate
    cannot run before the thing it verifies -- an ordering gap in the arc, not
    a missing table. This mode is what lets the precondition be met
    explicitly, by name, instead of as a side effect of the first write.

    IT IS STILL A WRITE, so it honours `--apply` exactly as `--flush` does:
    bare prints the plan. `IF NOT EXISTS` means a present tier costs nothing
    and an absent one is created, so re-running is a no-op rather than a
    reset -- the distinction the two modes exist to keep.
    """
    i = argv.index("--establish")
    # ARITY READ FROM THE BRANCH, AND THE FIRST ROSTER ENTRY FOR THIS MODE
    # GUESSED IT WRONG. `--establish` was first declared nullary from the
    # NAME; the branch below takes one-or-more TIER names and exits 2
    # without them. That is precisely the undeclared-arity defect
    # `schema_modes.MODES` exists to catch -- it binds the operand from the
    # branch, not from the name.
    want = [a for a in argv[i + 1 :] if not a.startswith("-")]
    if not want:
        print(f"--establish needs at least one tier: {' '.join(sorted(_TIERS))}")
        return 2
    unknown = [t for t in want if t not in _TIERS]
    if unknown:
        known = " ".join(sorted(_TIERS))
        print(f"unknown tier(s): {' '.join(unknown)}\n  known: {known}")
        return 2
    apply_it = "--apply" in argv
    # `mode="rw"` ONLY UNDER `--apply`, and the read-only default is a GATE
    # that fired: the first run of this mode died with
    # `ReadOnlySqlTransaction: cannot execute CREATE TABLE`, which is
    # `_cli_connect`'s `ro` default correctly refusing a write from a tool
    # whose other twenty modes are diagnostics. A dry run must not be able to
    # acquire a writable connection at all -- otherwise the plan/apply split
    # is a convention rather than a bound.
    con: Connection = _cli_connect("rw" if apply_it else "ro")
    # `relations()` IS THE EXISTING PRESENCE READER -- `--relations` already
    # routes through it, so a second spelling here would be the
    # fourth-parser shape this tree keeps paying for. Read BEFORE, so
    # "created" can be told from "already present".
    before = set(relations(con))
    if not apply_it:
        for t in want:
            for rel in _TIERS[t]:
                print(f"  plan  CREATE TABLE IF NOT EXISTS {rel}")
        print(f"{len(want)} tier(s) -- re-run with --apply; additive, nothing is dropped")
        return 0
    for t in want:
        apply(con, only=t)
    con.commit()
    # REPORT PRESENCE, AND REPORT WHETHER THIS CALL IS WHAT ESTABLISHED IT.
    # "created" and "already present" are different facts and collapsing
    # them is how a no-op reads as work.
    after = set(relations(con))
    for t in want:
        for rel in _TIERS[t]:
            state = "CREATED" if rel in after - before else "present" if rel in after else "ABSENT"
            print(f"  {state:<8} {rel}")
    return 0
