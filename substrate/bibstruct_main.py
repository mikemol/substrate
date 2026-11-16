# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The bib tool, assembled: the real parser, the real engine, the real snapshot guard.

⚑⚑⚑ THIS IS THE ONLY MODULE THAT CHOOSES CONCRETE COLLABORATORS, AND THAT IS WHY EVERY OTHER ONE
IS TESTABLE. `bib_handlers` and `bib_write_handlers` take their reader, bench and grammar as
CONTEXT, so their suites drive the whole CLI over in-memory bibs. The origin hardcoded its parser,
its default bib and its snapshot guard inside `main`, which is why its own suite had to write real
files — and why a refusal reached through the CLI killed the run at the first `--add` case, taking
twenty-four cases with it while still printing a count that read as full coverage.

⚑⚑ THE SNAPSHOT GUARD IS BOUND HERE AND NOWHERE ELSE. `edit_snapshot.guard` reads the PROCESS argv
to enforce the explicit-mutation contract, so a module that armed it would be unusable from a suite.
Binding it at the entry point keeps the contract where the process actually is.

⚑ AND THE TABLES ARE MERGED, NOT CHOSEN. A read table and a write table with one dispatch over
both is what lets `bib_modes.unbound` report completeness across the whole roster — a split
dispatch would need two censuses and could disagree.

⚑ EXTRACTED, NOT EDITED IN PLACE. `scratch/bibstruct.py` carries enough findings that the per-file
gate refuses every write to it, so this is rebuilt whole and the origin is left alone until it can
be swapped — decompose and replace, never patch behind a gate that cannot pass.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from substrate import (
    bib_cli,
    bib_handlers,
    bib_parse,
    bib_roundtrip,
    bib_write,
    bib_write_handlers,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from substrate import bib_argv

# What the assembled dispatch table maps a mode to.
Table = dict[str, "Callable[[bib_argv.Parsed], bib_cli.Result]"]


def _snapshot(label: str, targets: list[Path]) -> None:
    """Arm the recovery snapshot before a write.

    ⚑⚑ IMPORTED AT THE CALL SITE, DELIBERATELY. `edit_snapshot` lives in `scratch/` and is reached
    by leaf name, so importing it at module scope would make every consumer of this package — a
    suite included — depend on that resolution. Here the dependency is paid only by a run that
    actually writes.

    ⚑ AND A MISSING GUARD IS A REFUSAL, NOT A SILENT WRITE. The snapshot is what makes a bad write
    recoverable; proceeding without one would trade the whole recovery story for convenience.
    """
    import edit_snapshot  # noqa: PLC0415 — paid only by a run that writes

    edit_snapshot.guard(label, [str(p) for p in targets])


def _roundtrip(target: Path) -> list[tuple[str, str, str]]:
    """Return the totality probe's losses for one written file."""
    text = target.read_text(encoding="utf-8") if target.exists() else ""
    return [
        (loss.kind, loss.what, loss.detail)
        for loss in bib_roundtrip.probe(text, bib_parse.parse(text))
    ]


def _read_back(target: Path) -> dict[str, object]:
    """Re-parse a written file, so a write can be checked against what landed."""
    return dict(bib_parse.read(target).items())


def bench() -> bib_write.Bench:
    """Return the REAL write bench: snapshot, totality probe, read-back.

    ⚑ PUBLIC SO A BATCH WRITER SHARES IT. A second assembly elsewhere would be a second place the
    recovery story could silently lose an arm — the three-copies drift `bib_write` exists to end.
    """
    return bib_write.Bench(snapshot=_snapshot, roundtrip=_roundtrip, read_back=_read_back)


def handlers() -> Table:
    """Return the full dispatch table: every read and every write verb.

    ⚑ ONE TABLE OVER BOTH HALVES, so `bib_modes.unbound` can report completeness for the whole
    roster in one call. Two tables would need two censuses, and two censuses can disagree about
    which verb is missing.
    """
    reads = bib_handlers.bind(bib_handlers.Context(parse=bib_parse.read))
    writes = bib_write_handlers.bind(
        bib_write_handlers.Context(read=bib_parse.read, bench=bench(), grammar=bib_parse.GRAMMAR)
    )
    return {**reads, **writes}


def main(argv: list[str]) -> int:
    """Run one invocation, printing what it produced."""
    lines, code = bib_cli.run(argv, handlers())
    for line in lines:
        sys.stdout.write(line + "\n")
    return code


# ⚑ WITHOUT THIS GUARD `python -m substrate.bibstruct_main` IMPORTED THE MODULE AND EXITED 0 IN
# SILENCE on every invocation — measured by a peer following summit's filing instructions, who
# then had to validate a bib by hand. A tool that says nothing reads as a tool that found nothing.
if __name__ == "__main__":
    sys.exit(main(sys.argv))
