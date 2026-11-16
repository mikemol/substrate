# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""`--plan SQL` CLI dispatch.

`schema.py`'s live `EXPLAIN`-only planner -- "what would this query cost,
without paying it."

EXTRACTED 2026-10-02 (W63, incremental-extraction pass off the `mikemol-pycheck`
refusal on `schema.py`: *"this file cannot be made clean in one edit ...
extract the concern you need into a NEW module written clean in one pass,
then retire this file"*).

VERIFIED BEFORE EXTRACTING -- the one open question for this arm was whether
`schema_selftest.py` pins THIS dispatch block (by name, or by a `getsource(schema)`
text-slice) rather than functions it calls. A `--calls getsource` census of
`schema_selftest.py` returns ten sites; none names `--plan`, `plan`, or any
function this block calls. The ONLY marker-bounded text-slice of `schema.py`'s
own source in that file is `getsource(schema)` cut between the literal markers
`'if "--holes" in sys.argv:'` and `'if "--fibre"'`, nowhere near this arm's
lines. A second, unbounded `getsource(schema)` whole-file scan (for
`"_store.connect("` bypass sites) does traverse every line of the file, but
this arm's body contains no such call (it resolves its connection through
`_cli_connect`, like every sibling dispatch branch), so moving it leaves that
scan's findings unchanged. So moving the `--plan` CLI block leaves nothing the
suite's text-slice or its direct calls depend on.

WHY THIS ARM. Self-contained the same way `--reclaim-core`/`--transport` were:
it depends only on `_cli_connect` (already in `schema_rows.py`) and the
invocation's own `argv`. No other dispatch branch, no module-level state in
`schema.py`, nothing `schema_selftest` reads out of this one by name or by
source-slice.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from schema_rows import _cli_connect

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


def _first_value(r: object) -> object:
    """Return the first column of one `EXPLAIN` output row, whatever shape the driver gave it."""
    if isinstance(r, dict):
        return next(iter(cast("Mapping[str, object]", r).values()))
    return cast("Sequence[object]", r)[0]


def plan_dispatch(argv: list[str]) -> int:
    """Run `--plan SQL`'s dispatch over `argv`; return the process exit code.

    `schema.py`'s `__main__` block calls this as
    `raise SystemExit(plan_dispatch(sys.argv))` when `"--plan" in argv` -- the
    same call shape every other report-returning dispatch branch in that file
    already uses.

    ⚑⚑⚑ "MEASURE WHAT THIS COSTS" AND "INCUR WHAT THIS COSTS" WERE THE SAME
    OPERATION, AND THAT IS WHY THIS MODE EXISTS. `query_defs --scans` is
    documented as "which relations a builder READS" -- which reads as
    plan-only -- and it runs `EXPLAIN (ANALYZE, FORMAT JSON)`. `ANALYZE`
    EXECUTES the query to collect actual row counts. MEASURED 2026-08-18:
    reaching for it as a SAFETY probe during a disk incident took the volume
    76G -> 65G before it was killed, and the backend survived the kill and
    kept spilling. A reader reaching for the safe instrument got the hazard.

    ⚑ `EXPLAIN` WITHOUT `ANALYZE` IS THE WHOLE FIX, and it needs no new
    machinery: postgres plans from `pg_statistic` and executes NOTHING.
    Verified against the exact query that spilled -- returned instantly, `df`
    unchanged to the byte. The estimated rows and the node types
    (`HashAggregate`, `Parallel Hash Anti Join`, `Seq Scan`) are what say
    "this will spill" BEFORE it does.

    ⚑⚑ AND IT MUST BE THE LIVE TENANT, WHICH IS WHY IT IS NOT A `--probe`
    FLAG. `probe()` is sandbox-only by design, and the sandbox holds ~4 cores
    against the live store's 93.4M `obs` rows -- so a plan taken there
    reports costs three orders of magnitude too small while looking exactly
    like an answer. `_cli_connect` resolves the tenant once and the footer
    names it.

    ⚑ ESTIMATES, NOT MEASUREMENTS, AND THE FOOTER SAYS SO. A planner estimate
    can be wrong by orders of magnitude on stale statistics; it is a fact
    about what postgres BELIEVES, which is the fact that determines the plan
    it will actually run.
    """
    i = argv.index("--plan")
    if len(argv) <= i + 1:
        print("usage: schema.py --plan <SQL>   (EXPLAIN only — executes nothing)")
        return 2
    sql = argv[i + 1]
    # Refuse an operand that already says `ANALYZE` -- the one input that would
    # turn this mode into the hazard it exists to replace, and a caller pasting
    # a statement from `--scans` would do exactly that.
    if "analyze" in sql.lower():
        print(
            "⚑ REFUSED — the SQL names ANALYZE, which EXECUTES. This mode plans only;\n"
            "  strip it, or use --probe if you genuinely mean to run against the sandbox."
        )
        return 2
    con = _cli_connect()
    cur = con.cursor()
    cur.execute("EXPLAIN " + sql)
    for r in cur:
        print(_first_value(r))
    print(
        "plan only — NOTHING was executed; rows are ESTIMATES from pg_statistic [%s]"
        % ("sandbox" if "--sandbox" in argv else "live")
    )
    return 0
