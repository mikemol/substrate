# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""`--reclaim-core ID` CLI dispatch.

`schema.py`'s per-core, make-driven twin of `--reclaim`.

EXTRACTED 2026-10-02 (W63, incremental-extraction pass off the `mikemol-pycheck`
refusal on `schema.py`: *"this file cannot be made clean in one edit ...
extract the concern you need into a NEW module written clean in one pass,
then retire this file"*).

VERIFIED BEFORE EXTRACTING -- the one open question for this arm was whether
`schema_selftest.py` pins THIS dispatch block (by name, or by a `getsource(schema)`
text-slice) rather than the `reclaim_core`/`reclaim_verdict` FUNCTIONS it calls.
It does not: `schema_selftest.py` exercises `reclaim_verdict` via FOUR direct
calls (`schema_queue.reclaim_verdict(True, 1)`, `(False, 1)`, `(False, None)`,
`(True, None)`) and asserts the returned string -- never a textual match against
`schema.py`. `reclaim_core` itself is mentioned only in a comment, never called
by name or sliced; the suite instead exercises the shared `reclaim(...)` function
(a different name, already living in `schema_queue.py`). The ONLY marker-bounded
text-slice of `schema.py`'s own source in that file is `getsource(schema)` cut
between the literal markers `'if "--holes" in sys.argv:'` and `'if "--fibre"'`,
which is nowhere near this arm's dispatch lines. A second, unbounded
`getsource(schema)` whole-file scan (for `"_store.connect("` bypass sites) does
traverse every line of the file, but this arm's body contains no such call
(it resolves its connection through `_cli_connect`, like every sibling
dispatch branch), so moving it leaves that scan's findings unchanged. So moving
the `--reclaim-core` CLI block leaves nothing the suite's text-slice or its
direct calls depend on; `reclaim_core` and `reclaim_verdict` stay exactly where
they are, in `schema_queue.py`, untouched by this extraction.

WHY THIS ARM. Self-contained the same way `--reclaim`/`--flush`/`--establish`
were: it depends only on `reclaim_core` and `reclaim_verdict` (already in
`schema_queue.py`, not in `schema.py`), `_cli_connect`/`scalar` (already in
`schema_rows.py`), and the invocation's own `argv`. No other dispatch branch, no
module-level state in `schema.py`, nothing `schema_selftest` reads out of this
one by name or by source-slice.
"""

from __future__ import annotations

import sys
from typing import cast

from schema_queue import reclaim_core, reclaim_verdict
from schema_rows import _cli_connect, scalar

_STAGED_ANY_SQL = "SELECT 1 FROM obs WHERE core_id = %s LIMIT 1"


def reclaim_core_dispatch(argv: list[str]) -> int:
    """Run `--reclaim-core ID`'s dispatch over `argv`; return the process exit code.

    `schema.py`'s `__main__` block calls this as
    `raise SystemExit(reclaim_core_dispatch(sys.argv))` when
    `"--reclaim-core" in argv` -- the same call shape every other
    report-returning dispatch branch in that file already uses.

    ⚑⚑⚑ ⟡converge-scheduled -- THE LAST LINK IN THE PER-MODULE CHAIN.
    `--reclaim` sweeps the whole corpus; the `.drained` stamp needs one core at
    a time, so that a module is finished when the staged copy it no longer
    needs has been reclaimed rather than when someone remembers to run a
    sweep. Uses the SCOPED licence (`drainable_res.one_core`) so the corpus
    set is never computed to answer about one core.

    Dry by default, `--apply` to write -- a retire that runs bare is the shape
    `--establish`'s guard was built to prevent, and this one DELETES.
    """
    i = argv.index("--reclaim-core")
    rc_id = argv[i + 1] if i + 1 < len(argv) else None
    if rc_id is None:
        print("schema.py --reclaim-core <core_id> [--apply] (--live|--sandbox)", file=sys.stderr)
        print(
            "  retire ONE core IF the licence admits it. `--packed` names the candidates.",
            file=sys.stderr,
        )
        return 2
    apply_it = "--apply" in argv
    con = _cli_connect(mode="rw" if apply_it else "ro")
    r = reclaim_core(rc_id, con=con, dry_run=not apply_it)
    print(f"⟡reclaim-core — {rc_id}")
    # `staged_any` is asked of `obs` DIRECTLY, not derived from the dry run's counts --
    # those count rows MATCHING THE LICENCE, so a refused core reports 0 whatever its
    # staged size. `reclaim_verdict`'s docstring carries the measurement and the defect.
    # ⚑ THE SQL TEXT IS A MODULE CONSTANT, NEVER BUILT PER CALL -- `core_id` travels as
    # a bound PARAMETER (`(rc_id,)`), never spliced into the statement text.
    staged_any = scalar(con, _STAGED_ANY_SQL, (rc_id,))
    print(f"  licensed  {reclaim_verdict(bool(r['licensed']), staged_any)}")
    # `r["obs"]`/`r["edge"]` come back through `Mapping[str, object]` -- `cast` walls the
    # boundary at a concrete `int`, same discipline as every other narrowed read of this
    # dict (never trusting an untyped `object` further than this one conversion).
    obs_n = cast("int", r["obs"]) or 0
    edge_n = cast("int", r["edge"]) or 0
    print(f"  obs       {obs_n:,}")
    print(f"  edge      {edge_n:,}")
    print(f"  why       {r['why']}")
    # A refused core is not an error. The licence holding a core is the gate working --
    # `converge`'s own note: "a held core is not an error and must not stall the loop."
    # Exit 0 either way; the verdict is in the output, not the code.
    return 0
