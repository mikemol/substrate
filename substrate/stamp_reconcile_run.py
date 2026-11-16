# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Run the tenant-aware stamp reconcile against a store: read it, judge the stamps, report.

⚑⚑ THE STORE HALF OF `stamp_reconcile`, AND THE CLI `Flat.mk`'s `reconcile` RECIPE CALLS. The
judgements live in `stamp_reconcile` and never touch a database; this module does the three reads
the judgements need and nothing else, so the driver import stays out of the pure half.

⚑ THE READS ARE THE ORIGIN'S, UNCHANGED (`sppf_decode.reconcile_stamps` + `_staged_probe`):
  · `core_fp ⋈ terms` — ONE read giving both `backed` (path → mtime) and `ids_by_rel` (path → id),
    so the `.ingested` and `.promoted` passes can never disagree about which id a path has;
  · `SELECT DISTINCT core_id FROM obs_node` — only when the relation exists; absent means nothing
    is promoted, which is correct, not degenerate;
  · `SELECT 1 FROM obs WHERE core_id = %s LIMIT 1` — an index-only existence probe PER DRAINED
    STAMP, because `obs` is the largest relation and enumerating it is a 128M-row seq scan.

⚑ THE TENANT PICKS THE TARGET, AND BOTH GO THROUGH THE CLEAN CONNECTOR. `sandbox_connect.connection`
takes any assembled target; `live_target.target()` and `sandbox_target.target()` are the two. No
path here reaches `jea/metalanguage/store.py`, whose built-in host is the retired listener.

⚑ DRY BY DEFAULT. Without `--apply` it reports exactly what `--apply` would delete — `Walk.apply`
changes only whether a false stamp is unlinked, never the verdict. A reconcile deletes STAMP FILES,
never rows, so it does not move the store's row counts.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from substrate import live_target, sandbox_connect, sandbox_target
from substrate import stamp_reconcile as sr

if TYPE_CHECKING:
    from collections.abc import Callable

    from psycopg import Connection
    from psycopg.rows import DictRow

FP_QUERY = (
    "SELECT t.text AS text, t.term_id AS term_id, f.mtime AS mtime "
    "FROM core_fp f JOIN terms t ON t.term_id = f.core_id"
)
PROMOTED_QUERY = "SELECT DISTINCT core_id AS core_id FROM obs_node"
STAGED_QUERY = "SELECT 1 AS hit FROM obs WHERE core_id = %s LIMIT 1"
#: How many dropped cores the report names before truncating, visibly.
SHOWN = 8
#: Flags that take a value, so their operand is not read as the positional STAMPDIR.
VALUED = frozenset({"--tenant", "--base"})

USAGE = (
    "usage: python3 -m substrate.stamp_reconcile_run STAMPDIR --tenant live|sandbox"
    " [--base DIR] [--apply]\n"
    "  judges every stamp under STAMPDIR against that tenant's store; DRY unless --apply;\n"
    "  --base defaults to STAMPDIR/Substrate (the root core_fp keys are relative to)\n"
)


class RowTypeError(TypeError):
    """A column did not hold the type the reconcile needs."""


def _mtime(row: DictRow) -> int:
    """Read `mtime` as an int, refusing any other type."""
    value = row.get("mtime")
    if not isinstance(value, int):
        msg = f"core_fp.mtime is {type(value).__name__}, expected int"
        raise RowTypeError(msg)
    return value


def read(conn: Connection[DictRow]) -> tuple[dict[str, int], sr.Promotion]:
    """Return `(backed, promotion)` — the two answers the stamp judgements need."""
    names = {name for name, _ in sandbox_connect.relations(conn)}
    backed: dict[str, int] = {}
    ids_by_rel: dict[str, str] = {}
    if "core_fp" in names:
        for row in conn.execute(FP_QUERY).fetchall():
            text, term_id = sandbox_connect.descriptor(row, "text", "term_id")
            backed[text] = _mtime(row)
            ids_by_rel[text] = term_id
    promoted: set[str] = set()
    if "obs_node" in names:
        for row in conn.execute(PROMOTED_QUERY).fetchall():
            promoted.add(sandbox_connect.descriptor(row, "core_id")[0])
    return backed, sr.Promotion(promoted_ids=frozenset(promoted), ids_by_rel=ids_by_rel)


def staged_probe(conn: Connection[DictRow]) -> Callable[[str], bool]:
    """Return `core_id → bool`: does `obs` still hold rows for this core? One indexed probe."""

    def probe(cid: str) -> bool:
        return conn.execute(STAGED_QUERY, (cid,)).fetchone() is not None

    return probe


def target_for(tenant: str) -> sandbox_target.Target:
    """Return the assembled target for `tenant`, refusing an unknown one."""
    sr.stamp_suffix("ingested", tenant)  # the ONE tenant check; raises UnknownTenantError
    return live_target.target() if tenant == "live" else sandbox_target.target()


def report(walk: sr.Walk, counts: dict[str, tuple[int, list[str]]]) -> str:
    """Render the verdict: kept and dropped per kind, the denominator, and what dry means."""
    verb = "dropped" if walk.apply else "WOULD drop"
    lines = [f"stamp reconcile — tenant {walk.tenant}, {walk.stampdir}"]
    for kind, (kept, dropped) in counts.items():
        total = kept + len(dropped)
        lines.append(f"  .{kind:<9} kept {kept}, {verb} {len(dropped)} of {total}")
        lines.extend(f"      - {rel}" for rel in dropped[:SHOWN])
        if len(dropped) > SHOWN:
            lines.append(f"      … and {len(dropped) - SHOWN} more")
    if not walk.apply:
        lines.append("dry run — re-run with --apply to delete the stamps listed")
    return "\n".join(lines) + "\n"


def run(walk: sr.Walk) -> str:
    """Read the tenant's store once, judge every stamp kind, return the report."""
    with sandbox_connect.connection(target_for(walk.tenant)) as conn:
        backed, promotion = read(conn)
        counts = {
            "ingested": sr.ingested(backed, walk),
            "promoted": sr.promoted(promotion, walk),
            "drained": sr.drained(promotion, walk, staged_probe(conn)),
        }
        conn.rollback()
    return report(walk, counts)


def parse(argv: list[str]) -> sr.Walk | None:
    """Return the `Walk` argv describes, or None when it is malformed."""
    positional = [
        a
        for i, a in enumerate(argv)
        if not a.startswith("--") and (i == 0 or argv[i - 1] not in VALUED)
    ]
    known = VALUED | {"--apply"}
    if len(positional) != 1 or any(a.startswith("--") and a not in known for a in argv):
        return None
    if "--tenant" not in argv or argv.index("--tenant") + 1 >= len(argv):
        return None
    tenant = argv[argv.index("--tenant") + 1]
    if tenant not in sr.TENANTS:
        return None
    stampdir = Path(positional[0])
    base = Path(argv[argv.index("--base") + 1]) if "--base" in argv else stampdir / "Substrate"
    return sr.Walk(stampdir, base, tenant, apply="--apply" in argv)


def main(argv: list[str]) -> int:
    """Reconcile, or refuse malformed argv with usage."""
    walk = parse(argv)
    if walk is None or not walk.stampdir.is_dir():
        sys.stderr.write(USAGE)
        return 2
    try:
        sys.stdout.write(run(walk))
    except sandbox_connect.UnreachableError as exc:
        sys.stderr.write(f"stamp-reconcile: {exc}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
