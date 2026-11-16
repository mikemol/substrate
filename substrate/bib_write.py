# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The write protocol every bib-mutating verb follows: diff, gate, snapshot, write, verify.

⚑⚑⚑ ONE PROTOCOL, SPELLED THREE TIMES IN THE ORIGIN, AND THE COPIES HAD ALREADY DRIFTED. `--add`,
`--addfield` and `--set` each run the same seven steps — render the new text, print a unified diff,
stop unless `--apply`, arm the snapshot guard, write, re-parse, report. MEASURED in the origin:
`--add` verifies the key READS BACK after writing; `--addfield` and `--set` do not. Three copies of
one sequence, and the strongest verification arm exists in exactly one of them.

⚑⚑ THE READ-BACK IS THE ARM THAT MATTERS, AND ITS OWN COMMENT SAYS WHY: *"writing text that
round-trips is not the same as writing the entry asked for — the mis-sliced `--set` produced a file
that parsed fine and had the wrong content."* So the arm was written BECAUSE `--set` failed that
way, and `--set` is one of the two verbs that never got it. A protocol with one owner cannot drift
like that: every verb inherits every arm, including the one added for a defect it did not have.

⚑⚑ AND THE PER-FILE GATE NAMED THE SEAM THIS FILE NEEDED. A first cut took all nine parameters
flat and was refused at `PLR0913`; the nine are two kinds. An `Edit` is what this call writes —
different every time. A `Bench` is how writes are snapshotted and verified — fixed for a whole
session, and the thing a test swaps wholesale. Reading the refusal as a limit to satisfy would have
produced a tuple; reading it as a design signal produced the split the callers actually want.

⚑ AND THE ORDER IS LOAD-BEARING, NOT INCIDENTAL. The diff prints BEFORE the dry-run gate, so a
preview shows what would happen; the snapshot is armed BEFORE the write, so recovery exists for the
write that breaks the file; verification runs AFTER, on what was actually written rather than on
what was intended. Each step is where it is because the step after it can fail.

⚑ EXTRACTED, NOT EDITED IN PLACE. `scratch/bibstruct.py` carries enough findings that the per-file
gate refuses every write to it, so this is rebuilt whole and the origin is left alone until it can
be swapped — decompose and replace, never patch behind a gate that cannot pass.
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

# Exit codes. ⚑ WROTE-BUT-BROKEN IS 1, NOT 2: the file changed, so this is a failure to REPAIR,
# not a usage error to correct. Collapsing them would tell an author to fix their command line
# when what they need is `edit_snapshot --from-snapshot`.
OK = 0
BROKEN = 1
REFUSED = 2

# How a caller recovers a write that broke the file. ⚑ NAMED ONCE — the origin spelled this
# sentence in all three arms, which is three chances for one of them to name a stale command.
RECOVER = "Recover with edit_snapshot --from-snapshot."

# The flag that turns a preview into a write. ⚑ THERE IS NO `--dry-run`: the preview IS the absence
# of this flag, which is why a stated `dry-run` intent never reaches the snapshot guard.
APPLY_FLAG = "--apply"


@dataclass(frozen=True, slots=True)
class Outcome:
    """What a write attempt did, and what the caller should print and return."""

    code: int
    lines: tuple[str, ...] = ()

    @property
    def wrote(self) -> bool:
        """Whether the file on disk was changed."""
        return self.code != REFUSED


@dataclass(frozen=True, slots=True)
class Edit:
    """One verb's proposed change: what it is called, where it goes, and both texts.

    ⚑ `expect_key` IS THE READ-BACK ARM, MADE A DECLARATION. It was the origin's `--add`-only
    step; naming it here means a verb either states the key it expects to appear or declares by
    omission that it edits an existing entry. The choice is visible in the call rather than being
    the silent difference between three copied blocks.
    """

    verb: str
    label: str
    target: Path
    old: str
    new: str
    expect_key: str | None = None
    # ⚑ THE MIRROR ARM, for `--delete`: the key must NOT read back. A delete that round-trips
    # cleanly while its key is still there has removed the wrong span.
    gone_key: str | None = None

    @property
    def changes_nothing(self) -> bool:
        """Whether the render is byte-identical to what is already on disk."""
        return self.new == self.old


@dataclass(frozen=True, slots=True)
class Bench:
    """How writes are recovered and checked — fixed for a session, swapped wholesale by a test.

    ⚑⚑ `roundtrip` AND `read_back` ARE TWO QUESTIONS, AND THE ORIGIN'S COMMENT SEPARATES THEM.
    `roundtrip` asks whether the parser can still read everything it wrote — the totality probe a
    diff cannot see. `read_back` asks whether the specific key is THERE, which a passing
    round-trip does not imply: a mis-sliced write produced a file that parsed cleanly and held the
    wrong content.
    """

    snapshot: Callable[[str, list[Path]], None]
    roundtrip: Callable[[Path], list[tuple[str, str, str]]]
    read_back: Callable[[Path], dict[str, object]]


def diff_lines(old: str, new: str) -> tuple[str, ...]:
    """Return the indented unified diff the origin prints before every write."""
    return tuple(
        "  " + line
        for line in difflib.unified_diff(
            old.split("\n"), new.split("\n"), "before", "after", lineterm="", n=1
        )
    )


def _report(rows: list[tuple[str, str, str]]) -> tuple[str, ...]:
    """Format the round-trip failures the way the origin does."""
    return tuple(f"  ⚠ {kind:<16} {what:<24} {detail}" for kind, what, detail in rows)


def apply_write(edit: Edit, bench: Bench, *, applying: bool) -> Outcome:
    """Run the whole protocol for one edit, returning what to print and what to exit with.

    ⚑ A NO-OP IS REPORTED, NOT WRITTEN. The origin's `--set` alone checks whether the render
    changed anything; writing an identical file would arm a snapshot and re-verify for nothing,
    and tell the author their edit landed when there was nothing to land.
    """
    if edit.changes_nothing:
        return Outcome(OK, (f"  {edit.label} is already what was asked — nothing to write.",))

    lines = diff_lines(edit.old, edit.new)

    if not applying:
        return Outcome(OK, (*lines, f"{edit.verb}: DRY RUN — pass {APPLY_FLAG} to write."))

    # ⚑ THE SNAPSHOT IS ARMED BEFORE THE WRITE, because the write is what it exists to undo.
    bench.snapshot(f"bibstruct {edit.verb} {edit.label}", [edit.target])
    edit.target.write_text(edit.new, encoding="utf-8")

    broken = bench.roundtrip(edit.target)
    if broken:
        return Outcome(
            BROKEN,
            (
                *lines,
                *_report(broken),
                f"{edit.verb}: WROTE, but the result does NOT round-trip. {RECOVER}",
            ),
        )

    back = bench.read_back(edit.target)
    if edit.expect_key is not None and edit.expect_key not in back:
        return Outcome(
            BROKEN,
            (*lines, f"{edit.verb}: WROTE, but {edit.expect_key!r} does not read back. {RECOVER}"),
        )
    if edit.gone_key is not None and edit.gone_key in back:
        return Outcome(
            BROKEN,
            (*lines, f"{edit.verb}: WROTE, but {edit.gone_key!r} STILL reads back. {RECOVER}"),
        )

    return Outcome(
        OK,
        (*lines, f"{edit.verb}: ✓ wrote {edit.label}; the file round-trips ({len(back)} entries)."),
    )
