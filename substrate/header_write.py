#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Add the two licence-header lines to a file that lacks them — the writer `file_header` is not.

⚑⚑⚑ THE READER AND THE WRITER ARE SEPARATE MODULES ON PURPOSE. `file_header` answers *does this
file conform*, and 709 of 1596 files do. Nothing answers *make it conform*, so 87 modules are held
out of the distribution by the single most mechanical blocker in the manifest — and paying it by
hand across 87 files is how a uniform edit acquires 87 chances to differ.

⚑⚑ THE SOLE COLUMN IS WHY THIS BLOCKER AND NOT THE BIGGER ONE. `intake_manifest --sole` reports
`no-header` holding 87 modules ALONE against a TOTAL of 887, and `not-promotable` holding 800 with
a SOLE of **zero** — paying the larger blocker by itself would release nothing at all. A ranking
by TOTAL picks the one that moves nothing; the manifest carries both columns precisely so that
mistake is visible rather than plausible.

⚑⚑⚑ THE SHEBANG IS THE HARD CASE, AND IT IS HARD BECAUSE IT IS A COMMENT. `file_header.prologue`
collects comment lines before the first statement, so a `#!` line is INSIDE the prologue and the
naive repair — prepend the two lines at byte zero — reads as conforming while destroying the
executable bit's meaning: a shebang is only a shebang on line one. The insert therefore goes AFTER
a leading shebang and at the top otherwise, which is one branch and the only one that matters.

⚑⚑ AND THIS WRITES NOTHING WITHOUT `--apply`. The repair is uniform and therefore easy to run
over the wrong population; the default prints what it would do. ⚑ A file that already carries both
lines is SKIPPED rather than rewritten, so a second run is a no-op and the operation is idempotent
by construction rather than by care.

⚑ THE CONFORMANCE VERDICT IS NEVER RE-DERIVED HERE. Whether a file needs the repair is
`file_header.read(...).complete`, asked of the owning reader — a second predicate would be a
second authority on one question, and the two would disagree the first time either moved.
"""

from __future__ import annotations

import sys
from typing import NamedTuple

from substrate import file_header

#: The mode this module has, named so a bare run prints the spelling a reader needs next.
MODE = "--headers"

#: The flag that turns a preview into a write. ⚑ ABSENT MEANS PREVIEW, never a silent write.
APPLY = "--apply"

#: What a bare or unknown invocation exits with — usage, not a verdict about the tree.
USAGE_EXIT = 2

#: How a shebang opens. ⚑ ONLY MEANINGFUL ON LINE ONE, which is the whole reason this module
#: cannot simply prepend.
SHEBANG = "#!"


class Repair(NamedTuple):
    """One file's repair: the lines to add and where they go."""

    label: str
    at: int
    lines: tuple[str, ...]

    def why(self) -> str:
        """Return a one-line account naming the file and the insertion point."""
        where = "after the shebang" if self.at else "at the top"
        return f"{self.label}  + {len(self.lines)} line(s) {where}"


def header_lines() -> tuple[str, ...]:
    """Return the two lines a conforming file carries, built from the reader's own prefixes.

    ⚑⚑ THE PREFIXES COME FROM THE READER, NOT FROM A STRING HERE. A second spelling would pass
    this module's own cases and fail the census — a writer that produces text its own reader
    rejects, which is the shape that makes a repair look applied and leave the blocker in place.
    """
    return (f"{file_header.SPDX_PREFIX}Apache-2.0", f"{file_header.COPYRIGHT_PREFIX} 2026 Mike Mol")


def insert_at(text: str) -> int:
    """Return the line index the header belongs at — after a shebang, else the top.

    ⚑⚑⚑ THIS IS THE ONE BRANCH THAT MATTERS. A shebang is a comment, so it sits inside the
    prologue the reader scans, and prepending above it moves it off line one — where it stops
    being a shebang at all. The file would then read as CONFORMING while having lost the property
    its executable bit asserts, which is a repair that trades a visible defect for an invisible one.
    """
    first = text.splitlines()[:1]
    return 1 if first and first[0].startswith(SHEBANG) else 0


def repair(text: str, label: str) -> Repair | None:
    """Return the repair this file needs, or None when it already conforms.

    ⚑ CONFORMANCE IS ASKED OF THE READER. Re-deriving it here would be a second authority on the
    one question this module exists to act on.
    """
    if file_header.read(text, label).complete:
        return None
    return Repair(label=label, at=insert_at(text), lines=header_lines())


def applied(text: str, found: Repair) -> str:
    """Return the source with the header inserted.

    ⚑ THE ORIGINAL LINES ARE NEVER REWRITTEN, only split around. A writer that reflows what it did
    not come to change makes every repair a review of the whole file.
    """
    lines = text.splitlines(keepends=True)
    head = lines[: found.at]
    rest = lines[found.at :]
    added = [f"{line}\n" for line in found.lines]
    return "".join(head + added + rest)


class Census(NamedTuple):
    """The repair population, with the denominator that makes a zero readable."""

    repairs: tuple[Repair, ...]
    scanned: int
    wrote: bool

    def lines(self) -> list[str]:
        """Return the report: each repair, then the denominator and the mode."""
        out = [f"  {found.why()}" for found in self.repairs]
        verb = "repaired" if self.wrote else "would repair"
        out.append(f"{verb} {len(self.repairs)} file(s) of {self.scanned} scanned")
        if not self.wrote and self.repairs:
            # ⚑ A PREVIEW THAT DOES NOT SAY IT IS A PREVIEW reads as a completed run, and the
            # next census then contradicts it.
            out.append(f"⚑ PREVIEW — nothing was written. Pass {APPLY} to apply.")
        if not self.scanned:
            out.append("⚑ NOTHING WAS SCANNED — this zero is a fact about the invocation.")
        return out


def census(*, apply: bool) -> Census:
    """Return every corpus file needing the header, writing them when asked.

    ⚑ THE FLAG IS KEYWORD-ONLY. `census(True)` at a call site says nothing about what is true, and
    this one decides whether the corpus is written to — the gate refused the positional form and
    was right to.
    """
    found: list[Repair] = []
    scanned = 0
    for path, label in file_header.population():
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        scanned += 1
        needed = repair(text, label)
        if needed is None:
            continue
        found.append(needed)
        if apply:
            path.write_text(applied(text, needed), encoding="utf-8")
    return Census(tuple(found), scanned, apply)


def run(argv: list[str]) -> int:
    """Print the repairs the corpus needs, applying them when asked."""
    if not argv or argv[0] != MODE:
        print(__doc__)  # noqa: T201 - the usage, for a bare or unknown invocation
        print(
            f"    header_write.py {MODE} [{APPLY}]   "  # noqa: T201
            f"# add the licence header to every file lacking it"
        )
        return USAGE_EXIT
    found = census(apply=APPLY in argv)
    for line in found.lines():
        print(line)  # noqa: T201 - this module IS the report
    if not found.scanned:
        return USAGE_EXIT
    return 0


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
