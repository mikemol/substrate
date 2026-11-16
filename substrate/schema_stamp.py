# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Stamp a freshly established store with the schema version its ingester requires.

⚑⚑⚑ THE MISSING MODE, AND WHY NOTHING ELSE CAN FILL IT (trap B, 2026-09-22). `schema.py
--establish event` creates `schema_version` EMPTY, and `sppf_db`'s ingest refuses any store whose
`schema_version` does not read `SCHEMA_VERSION` (`_schema_current`, sppf_db.py:222-231). Its only
stamping calls (:461 and :2198-2199) each sit AFTER that stale guard (:443-449, :2139-2162) — so
an established-but-unstamped tier can NEVER be ingested, and no existing mode stamps one. The
three owning files (`schema.py`, `schema_decl.py`, `schema_rows.py`) are frozen by the per-file
gate, so the mode is this clean module rather than a flag on them.

⚑⚑ IT READS THE VERSION FROM ITS ONE AUTHORITY AND WRITES THROUGH THE ONE WRITER. The number is
parsed out of `scripts/sppf_db.py` (`SCHEMA_VERSION = <int>`) as structure, never restated here
and never obtained by importing that frozen module and its side effects. The write goes through
`schema_rows.set_schema_version`, loaded the way the jea scripts load it (their directory on the
path, bare names), never a hand-typed INSERT that would be a second spelling of that fact.

⚑ SANDBOX ONLY, AND THE TENANT IS NAMED. The store is being rebuilt tenant by tenant; the live
tenant is not stamped until the sandbox has carried a real ingest. `--live` is refused rather
than defaulted to, and a bare run with no tenant is refused too. Dry by default: it prints the
current and target versions and writes only with `--apply`, then re-reads to prove the write
landed.
"""

from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, cast

from substrate import sandbox_connect

if TYPE_CHECKING:
    from collections.abc import Callable

ROOT = Path(__file__).resolve().parent.parent
#: The file that OWNS the version constant, and the constant's name.
AUTHORITY = ROOT / "scripts" / "sppf_db.py"
CONSTANT = "SCHEMA_VERSION"
#: Where the owning writer lives; its module imports siblings by bare name.
WRITER_DIR = ROOT / "jea" / "metalanguage"

USAGE = (
    "usage: python3 -m substrate.schema_stamp --sandbox [--apply]\n"
    "  stamps schema_version with sppf_db.SCHEMA_VERSION; dry unless --apply;"
    " --live is refused until the sandbox has carried an ingest\n"
)


class NoAuthorityError(RuntimeError):
    """The version constant could not be read from its authority."""

    def __init__(self, path: Path) -> None:
        """Name the file and the constant looked for."""
        super().__init__(f"no integer `{CONSTANT} = <int>` at module level in {path}")


class _Rows(Protocol):
    """The two members of `schema_rows` this module calls."""

    schema_version: Callable[[object], int | None]
    set_schema_version: Callable[[object, int], None]


def authority_version(path: Path = AUTHORITY) -> int:
    """Return `SCHEMA_VERSION` as DECLARED in its owning file — parsed, not imported."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target, value = node.targets[0], node.value
        if (
            isinstance(target, ast.Name)
            and target.id == CONSTANT
            and isinstance(value, ast.Constant)
            and isinstance(value.value, int)
        ):
            return value.value
    raise NoAuthorityError(path)


def plan(current: int | None, target: int) -> str:
    """Render what a stamp would do — or that it has nothing to do."""
    if current == target:
        return f"schema_version is already {target}; nothing to stamp\n"
    shown = "EMPTY" if current is None else str(current)
    return f"schema_version {shown} → {target}\n"


def _rows_module() -> _Rows:
    """Load the owning writer the way the jea scripts do: their directory first, bare names."""
    if str(WRITER_DIR) not in sys.path:
        sys.path.insert(0, str(WRITER_DIR))
    return cast("_Rows", importlib.import_module("schema_rows"))


def main(argv: list[str]) -> int:
    """Dry-run or apply the stamp on the sandbox tenant."""
    if "--live" in argv or "--sandbox" not in argv:
        sys.stderr.write(USAGE)
        return 2
    target = authority_version()
    rows = _rows_module()
    with sandbox_connect.connection() as conn:
        current = rows.schema_version(conn)
        sys.stdout.write("tenant : sandbox\n" + plan(current, target))
        if current == target or "--apply" not in argv:
            if current != target:
                sys.stdout.write("dry run — re-run with --apply to write it\n")
            return 0
        rows.set_schema_version(conn, target)
        conn.commit()
        after = rows.schema_version(conn)
    if after != target:
        sys.stderr.write(f"schema-stamp: wrote {target} but read back {after!r}\n")
        return 1
    sys.stdout.write(f"stamped and read back: {after}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
