# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Ingest built Agda cores into the SANDBOX tenant, serially, in import order (W10).

⚑⚑⚑ THE MAKE CHAIN CANNOT DO THIS, AND THAT IS WHY THIS FILE EXISTS. `gen_build_makefiles`
emits `python3 sppf_db.py --ingest-core $< --live --apply` (measured t91): the tenant is
hard-coded LIVE, the bare interpreter bypasses `store_launch` so the store dials the retired
`127.0.0.1` listener, and it runs `-j` wide against a tenant no concurrency was ever measured on.
This driver is the sandbox's path until the live rebuild has one of its own.

⚑⚑ EACH CORE RUNS THROUGH THE COMMAND ALREADY MEASURED TO LAND, AS A SUBPROCESS. The single-core
`store_launch … --ingest-core <core> --apply --sandbox` wrote Foundation/{Eq,Unit,Level}; this
module adds only an ORDER and a GUARD, and re-derives nothing about the store. `sppf_db` is
frozen by the per-file gate, so importing it would pull its findings into this clean module.

⚑⚑ THE GUARD IS LUTHEN'S INVARIANT, CHECKED ON OUR SIDE FIRST. luthen-observability witnesses
the sandbox's row counts every tick (their 350ae40) and REFUSES a reading where any count other
than `schema_version` fell. So after every core this re-counts, and the first drop STOPS the run
naming the table — a drop means something deleted rows, and continuing would bury the cause
under more ingests.

⚑ NO SKIP LIST, MEASURED RATHER THAN ASSUMED. Re-ingesting Foundation/Eq left every count
unchanged (t93): `core_fp` keys a core by its path's term id plus its mtime, so `ingest_core`
is already idempotent per core. A second record of what was ingested would be a second store.

⚑ THE ORDER IS `agda_dag.topo`'s, NOT A NEW ONE. Importers after their imports, so a module's
dependencies are present before it is. A cycle refuses rather than guessing an order.
"""

from __future__ import annotations

import subprocess
import sys
from typing import TYPE_CHECKING

from substrate import agda_dag, corpus, sandbox_connect

if TYPE_CHECKING:
    from pathlib import Path

#: The frozen ingester, run through `store_launch` so its store module is rewired.
SPPF_DB = corpus.ROOT / "scripts" / "sppf_db.py"
#: Where compiled cores land, one directory per Agda version.
BUILD_GLOB = "_build/*/agda"
#: The core suffix beside a module's relpath.
CORE_SUFFIX = ".agdai"
#: The one counted table that is a stamp, not an accumulation — luthen excludes it too.
EXEMPT = frozenset({"schema_version"})
#: Cores per run when `--limit` is not given — a bound, so a mistake costs a batch, not a tree.
DEFAULT_LIMIT = 10

USAGE = (
    "usage: python3 -m substrate.sandbox_ingest [--apply] [--limit N]\n"
    "  dry by default: prints the next N built cores in import order;\n"
    "  --apply ingests them into the SANDBOX, stopping at the first row count that falls\n"
)


class NoBuildRootError(RuntimeError):
    """The build root is absent or ambiguous — a fact about the tree, not a guess to make."""


def build_root(agda_dir: Path = agda_dag.AGDA_DIR) -> Path:
    """Return the one directory compiled cores live under, refusing none or several."""
    found = sorted(p for p in agda_dir.glob(BUILD_GLOB) if p.is_dir())
    if len(found) != 1:
        msg = f"expected exactly one {BUILD_GLOB} under {agda_dir}, found {len(found)}"
        raise NoBuildRootError(msg)
    return found[0]


def plan(order: tuple[str, ...], root: Path) -> list[Path]:
    """Return the built core for each module in `order` that has one, preserving the order.

    ⚑ AN UNBUILT MODULE IS OMITTED, NOT AN ERROR: the sandbox is filled from what the build has
    produced, and a later run picks up whatever has been built since.
    """
    cores = (root / (module.replace(".", "/") + CORE_SUFFIX) for module in order)
    return [core for core in cores if core.is_file()]


#: The directory under the build root that `ingest_core` keys a core relative to.
KEY_BASE = "Substrate"


def key(core: Path, root: Path) -> str:
    """Return the text `ingest_core` interns a core under — its path below `<root>/Substrate`.

    ⚑ READ FROM THE STORE, NOT GUESSED: `--present` printed `Foundation/Eq.agdai` for the core at
    `<root>/Substrate/Foundation/Eq.agdai` (t95), and this is that relation, stated once.
    """
    return core.relative_to(root / KEY_BASE).as_posix()


def unseen(cores: list[Path], root: Path, present: set[str]) -> list[Path]:
    """Return the cores whose key is not already present, preserving order.

    ⚑ THIS IS WHAT MAKES `--limit` BOUND NEW WORK. Without it every batch re-spawned each done
    core as a no-op subprocess (t94: 5 of 15), a cost that grew with every batch landed.
    """
    return [core for core in cores if key(core, root) not in present]


def drops(before: dict[str, int], after: dict[str, int]) -> list[str]:
    """Return every non-exempt table whose count fell, or that vanished, between two readings."""
    return sorted(
        name for name, n in before.items() if name not in EXEMPT and after.get(name, -1) < n
    )


def counts() -> dict[str, int]:
    """Read the sandbox's per-table row counts, read-only and rolled back."""
    with sandbox_connect.connection() as conn:
        found = sandbox_connect.row_counts(conn, sandbox_connect.relations(conn))
        conn.rollback()
    return found


#: A core's id is the term id of the text `ingest_core` interned for it (schema_decl.core_fp),
#: so the text is read back through `terms` rather than re-derived here.
PRESENT_QUERY = "SELECT t.text AS text FROM core_fp c JOIN terms t ON t.term_id = c.core_id"


def ingested() -> set[str]:
    """Return the text every ingested core was interned under, read-only and rolled back."""
    with sandbox_connect.connection() as conn:
        rows = conn.execute(PRESENT_QUERY).fetchall()
        conn.rollback()
    return {sandbox_connect.descriptor(row, "text")[0] for row in rows}


def ingest_one(core: Path) -> int:
    """Run the measured single-core sandbox ingest on `core`; return its exit code."""
    argv = [
        sys.executable,
        "-m",
        "substrate.store_launch",
        str(SPPF_DB),
        "--ingest-core",
        str(core),
        "--apply",
        "--sandbox",
    ]
    return subprocess.run(argv, cwd=corpus.ROOT, check=False).returncode


def parse_limit(argv: list[str]) -> int | None:
    """Return `--limit N` as an int, the default when absent, or None when malformed."""
    if "--limit" not in argv:
        return DEFAULT_LIMIT
    at = argv.index("--limit")
    if at + 1 >= len(argv) or not argv[at + 1].isdigit():
        return None
    return int(argv[at + 1])


def run(cores: list[Path]) -> int:
    """Ingest `cores` in order, re-counting after each; stop at a failure or a falling count."""
    before = counts()
    for core in cores:
        code = ingest_one(core)
        after = counts()
        fell = drops(before, after)
        if code != 0 or fell:
            sys.stderr.write(
                f"sandbox-ingest: STOPPED at {core.name} "
                f"(exit {code}; fell: {', '.join(fell) or 'none'})\n"
            )
            return 1
        grew = sum(after.values()) - sum(before.values())
        sys.stdout.write(f"  +{grew:>7} rows  {core.relative_to(corpus.ROOT)}\n")
        before = after
    total = sum(before.values())
    sys.stdout.write(f"{len(cores)} core(s) ingested; {total} row(s) in the sandbox\n")
    return 0


def main(argv: list[str]) -> int:
    """Dry-run or apply one bounded batch of sandbox ingests."""
    if argv == ["--present"]:
        for text in sorted(ingested()):
            sys.stdout.write(f"  {text}\n")
        return 0
    limit = parse_limit(argv)
    known = {"--apply", "--limit"}
    stray = [a for a in argv if a.startswith("--") and a not in known]
    if limit is None or stray:
        sys.stderr.write(USAGE)
        return 2
    walked = agda_dag.topo(agda_dag.parse())
    if isinstance(walked, agda_dag.Cycle):
        sys.stderr.write(f"sandbox-ingest: {walked.message}\n")
        return 2
    root = build_root()
    cores = unseen(plan(walked[1], root), root, ingested())[:limit]
    if "--apply" not in argv:
        for core in cores:
            sys.stdout.write(f"  plan  {core.relative_to(corpus.ROOT)}\n")
        sys.stdout.write(f"{len(cores)} core(s) planned — re-run with --apply\n")
        return 0
    return run(cores)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
