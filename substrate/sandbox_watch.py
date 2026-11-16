# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Watch the sandbox's row counts and EXIT the moment one falls (operator, 2026-09-23).

⚑⚑ AN ALARM, NOT A POLL. A long build against the sandbox (the full `make … TENANT=sandbox
promote`) was being checked by hand each tick. This runs in the background instead and exits:

    exit 1  a count FELL, or a table VANISHED — the run deleted something it should not have;
            the tables are named, which is the first thing to read.
    exit 0  the counts have not moved for `--idle` consecutive reads — the run finished, or it
            stalled; either way it is time to look.

The harness notifies when a background process exits, so either outcome arrives as a notice
rather than waiting for the next tick to ask.

⚑ THE INVARIANT IS luthen's, CHECKED HERE FIRST: every count except `schema_version` (a stamp, not
an accumulation) only rises. A NEW table is fine — establishing a tier adds relations.
"""

from __future__ import annotations

import sys
import time

from substrate import sandbox_connect

#: The one counted table that is a stamp, not an accumulation — luthen exempts it too.
EXEMPT = frozenset({"schema_version"})
DEFAULT_EVERY_S = 60
DEFAULT_IDLE = 15

USAGE = (
    "usage: python3 -m substrate.sandbox_watch [--every SECONDS] [--idle READS]\n"
    f"  exit 1 when a sandbox count falls or a table vanishes; exit 0 after --idle reads\n"
    f"  with no change (defaults: every {DEFAULT_EVERY_S}s, idle {DEFAULT_IDLE})\n"
)


def falls(before: dict[str, int], after: dict[str, int]) -> list[str]:
    """Return every non-exempt table whose count fell or that vanished, as `name before→after`."""
    out = []
    for name, n in sorted(before.items()):
        if name in EXEMPT:
            continue
        now = after.get(name)
        if now is None:
            out.append(f"{name} {n}→(gone)")
        elif now < n:
            out.append(f"{name} {n}→{now}")
    return out


def read() -> dict[str, int]:
    """Read every table's row count, read-only and rolled back."""
    with sandbox_connect.connection() as conn:
        counts = sandbox_connect.row_counts(conn, sandbox_connect.relations(conn))
        conn.rollback()
    return counts


def _flag(argv: list[str], name: str, default: int) -> int | None:
    """Return `--name N` as an int, the default when absent, or None when malformed."""
    if name not in argv:
        return default
    at = argv.index(name)
    if at + 1 >= len(argv) or not argv[at + 1].isdigit() or int(argv[at + 1]) < 1:
        return None
    return int(argv[at + 1])


def watch(every_s: int, idle: int) -> int:
    """Poll until a count falls (1) or nothing moves for `idle` reads (0)."""
    last = read()
    sys.stdout.write(
        f"watching {len(last)} tables, {sum(last.values())} rows; "
        f"every {every_s}s, idle after {idle} still reads\n"
    )
    still = 0
    while still < idle:
        time.sleep(every_s)
        now = read()
        fell = falls(last, now)
        if fell:
            sys.stdout.write(f"FELL: {', '.join(fell)}\n")
            return 1
        if now == last:
            still += 1
        else:
            still = 0
            grew = sum(now.values()) - sum(last.values())
            sys.stdout.write(f"+{grew} rows → {sum(now.values())}\n")
        last = now
    sys.stdout.write(f"idle: no change in {idle} reads; {sum(last.values())} rows\n")
    return 0


def main(argv: list[str]) -> int:
    """Parse the flags and watch."""
    every = _flag(argv, "--every", DEFAULT_EVERY_S)
    idle = _flag(argv, "--idle", DEFAULT_IDLE)
    unknown = [a for a in argv if a.startswith("--") and a not in {"--every", "--idle"}]
    if every is None or idle is None or unknown:
        sys.stderr.write(USAGE)
        return 2
    try:
        return watch(every, idle)
    except sandbox_connect.UnreachableError as exc:
        sys.stderr.write(f"sandbox-watch: {exc}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
