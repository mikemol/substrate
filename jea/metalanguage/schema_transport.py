# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""`--transport` CLI dispatch -- `schema.py`'s "ask the driver, don't assert" reader.

EXTRACTED 2026-10-02 (W63, incremental-extraction pass off the `mikemol-pycheck`
refusal on `schema.py`: *"this file cannot be made clean in one edit ... extract
the concern you need into a NEW module written clean in one pass, then retire
this file"*). Verified before extracting: `schema_selftest.py` pins `schema.py`'s
own source text in exactly one place -- `getsource(schema)` sliced between the
literal markers `'if "--holes" in sys.argv:'` and `'if "--fibre"'`, which drives
both the `--holes`/`--fibre` cases and the whole-module bypass-finder for
`_store.connect(`. Neither marker, and no `_store.connect(` call, appears in
this arm -- it is a PURE READ of `transport_report()`, already resident in
`schema_rows.py` (confirmed: `pycodemod.py --binding transport_report` finds
its one definition there, not in `schema.py`) -- so moving the eight-line
dispatch leaves nothing the suite's text slice depends on.

`schema_rows` is also quoted BY NAME, in prose, inside `transport_report`'s own
docstring: *"'psycopg's executemany does not batch' ... which `schema.py
--transport` refuted"* (`schema_selftest.py`, the bulk-transport case block).
That citation names the CLI FLAG, not this module, so it stays accurate
whichever file the flag's eight-line dispatch body lives in.
"""

from __future__ import annotations

from schema_rows import transport_report


def transport_dispatch(argv: list[str]) -> int:
    """Run `--transport`'s dispatch; return the process exit code.

    `argv` is unused -- the mode takes no operand -- but is accepted for the
    same call shape every other dispatch module in this split uses
    (`establish_dispatch(argv)`, ...).

    THE WRITE PATH'S OWN PROPERTIES, READ FROM THE DRIVER -- not asserted about it.
    This mode exists because "psycopg's executemany does not batch" was once stated
    as fact, built on, and refuted by five minutes reading `cursor.py`. A claim about
    a dependency belongs in a mode that re-derives it on every run, not in a comment
    that ages.
    """
    del argv  # no operand; accepted for the shared dispatch-function shape
    for k, v in transport_report().items():
        print(f"  {k:<22} {v}")
    return 0
