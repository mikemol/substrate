#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Move a LINE SPAN out of one markdown document and into a named section of another.

⚑⚑⚑ THIS IS THE MODE THE Ⓝ60 SPLIT NEEDED AND DID NOT HAVE. `doc_split` SLICES a span out of an
origin and `md_write` APPENDS a body into a section, but nothing performed the pair as ONE
operation — so re-routing a misfiled entry meant a slice, an append, and a hand-excision of the
origin, with the conservation argument living in whoever's turn was running. `doc_split`'s own
guard exists because a partition is only trustworthy when a machine compares the halves; a MOVE
has exactly the same exposure and had no such check.

⚑⚑ THE EXCISION IS THE HALF THAT WAS MISSING, AND IT IS THE DANGEROUS ONE. An append that fails
is loud — the text is simply absent from the destination. An excision that removes the wrong
lines is SILENT: the destination looks right, the origin still parses, and the loss is a few
lines nobody is counting. So this module never excises by line arithmetic alone. It slices the
span, appends that exact text, removes those exact lines, and then asserts the moved text is
present in the destination and absent from the origin before either file is written.

⚑ CONSERVATION IS CHECKED ON CONTENT, NOT ON COUNTS. A line tally passes while content is
mangled — the failure mode `doc_split` was written against — so the check compares the moved
BLOCK, and it runs against the text that would be written rather than against the intent.

⚑ BOTH WRITES OR NEITHER. The two documents are written only after both new texts are derived
and the conservation check has passed, so a refusal cannot leave an entry duplicated in one file
and deleted from the other. There is no partial state to recover from.

⚑ THE SPAN IS THE OPERAND BECAUSE THE UNIT IS AN ENTRY, NOT A SECTION. These worklist shards hold
ONE `## Residue` section containing hundreds of bullet entries; a section-granular mover could
not address any of them. Spans come from `mdstruct --headers` / `doc_split --slice`, which is how
the rest of this toolkit already names a region.
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import md_sections, ratchet_flags

_USAGE = """\
md_move — move a line span from one markdown document into a section of another

    python3 -m substrate.md_move <from.md> <to.md> <heading> --span START-END
                                 [--exact] (--apply | --dry-run)

    --span START-END   1-indexed, INCLUSIVE, against <from.md> as it is on disk
    --exact            match the destination heading WHOLE, for one contained in another
    --apply            write BOTH files; without it, report what would move

⚑ The moved text is appended to the END of the named section, and removed from the origin, as
  ONE operation — verified present at the destination and absent from the origin before writing.
⚑ REFUSES when the destination ALREADY holds the text: that is a duplication, not a move.

    python3 -m substrate.md_move --drop <from.md> <to.md> --span START-END (--apply | --dry-run)

    --drop   remove the span from <from.md>, having VERIFIED <to.md> already holds it

⚑ `--drop` IS THE OTHER HALF OF A MOVE THAT ARRIVED IN TWO STEPS — a `doc_split --part` copy, or
  an interrupted run — and it is NOT a delete: it refuses unless the destination can be shown to
  hold the text, so the span is dropped only where it demonstrably survives elsewhere.
"""

_OPERANDS = 3
_DROP_OPERANDS = 2
_BOUNDS = 2


def parse_span(text: str) -> tuple[int, int]:
    """Return the 1-indexed inclusive bounds named by a `START-END` operand.

    ⚑ IT REFUSES A REVERSED OR ZERO-BASED SPAN RATHER THAN NORMALISING ONE. A silently
    reordered span moves a region the caller did not name, and a 0 start would take the
    document's first line along with whatever was meant — both are the caller's intent being
    guessed at, which on a write is the thing to refuse.
    """
    parts = text.split("-")
    if len(parts) != _BOUNDS or not all(p.isdigit() for p in parts):
        msg = f"span must read START-END, got {text!r}"
        raise ValueError(msg)
    start, end = int(parts[0]), int(parts[1])
    if start < 1 or end < start:
        msg = f"span {text!r} must be 1-indexed with END >= START"
        raise ValueError(msg)
    return start, end


def excise(text: str, start: int, end: int) -> tuple[str, str]:
    """Return `(remaining, removed)` splitting `text` at the 1-indexed inclusive span.

    ⚑ `splitlines(keepends=True)` IS LOAD-BEARING. Splitting without the endings and rejoining
    would rewrite every line terminator in the document — a whole-file diff for a few-line
    change, and a silent normalisation of any file not already in the joiner's convention.
    """
    lines = text.splitlines(keepends=True)
    if end > len(lines):
        msg = f"span ends at line {end}, past the document's {len(lines)}"
        raise ValueError(msg)
    return "".join(lines[: start - 1] + lines[end:]), "".join(lines[start - 1 : end])


def unconserved(origin_after: str, dest_after: str, moved: str) -> str:
    """Return the reason the move is unsafe, or the empty string when it conserves.

    ⚑ IT CHECKS BOTH DIRECTIONS, because each catches a different defect. Absent-from-destination
    is a failed append; still-present-in-origin is a failed excision. Checking only the first
    reports a DUPLICATION as a success, which is the direction that silently doubles an entry.

    ⚑⚑ IT IS PUBLIC BECAUSE ITS CASES ARE THE POINT. Written private, its arms could only be
    reached through `SLF001` — and the gate refusing that said the predicate carrying the whole
    safety argument should be nameable. A conservation check no caller can invoke is a promise.

    ⚑⚑⚑ IT COMPARES THE STRIPPED BLOCK, AND THE FIRST CUT DID NOT — WHICH MADE IT REFUSE EVERY
    CORRECT MOVE OF A SPAN ENDING ON A BLANK LINE. `append_to_section` normalises the blank run
    at a section's tail, so a block carrying a trailing newline arrives with it collapsed and a
    byte-exact `in` test reports a SUCCESSFUL move as a loss. The defect was in the CHECK, not
    in the move — caught because the refusal fired on a span whose content was demonstrably
    intact. ⚑ Stripping only the OUTER whitespace keeps every interior line significant, so a
    genuinely mangled block still fails; what is discarded is exactly what the destination is
    entitled to reflow.
    """
    block = moved.strip()
    if block and block not in dest_after:
        return "the moved text is not present in the destination"
    if block and block in origin_after:
        return "the moved text is still present in the origin"
    return ""


def move(
    src: Path, dst: Path, heading: str, bounds: tuple[int, int], *, exact: bool = False
) -> tuple[str, str, str]:
    """Return `(origin_after, dest_after, moved)` for one span move, writing nothing.

    ⚑ IT RETURNS TEXT AND DOES NOT WRITE, so `--dry-run` and `--apply` share ONE derivation
    rather than being two paths that can disagree — the contract `md_write` established for the
    bounded write, which is the same reason it holds here.
    """
    start, end = bounds
    origin_after, moved = excise(src.read_text(encoding="utf-8"), start, end)
    # ⚑⚑⚑ THE ALREADY-THERE CHECK RUNS BEFORE THE APPEND, AND ITS ABSENCE WAS A MEASURED HOLE.
    # `unconserved` asks whether the moved text is present at the destination AFTERWARDS — which
    # a block the destination ALREADY held satisfies without the append doing anything. So a
    # re-run, or a span copied there earlier by `doc_split --part`, passed every check while
    # DUPLICATING the entry. The post-check cannot see it: present-because-appended and
    # present-already are identical in the result. Only the BEFORE state distinguishes them.
    if moved.strip() and moved.strip() in dst.read_text(encoding="utf-8"):
        msg = (
            "refusing to move: the destination already holds this text — "
            "moving it would duplicate the entry, not relocate it"
        )
        raise ValueError(msg)
    dest_after, _ = md_sections.append_to_section(dst, heading, moved, exact=exact)
    reason = unconserved(origin_after, dest_after, moved)
    if reason:
        msg = f"refusing to move: {reason}"
        raise ValueError(msg)
    return origin_after, dest_after, moved


def drop(src: Path, dst: Path, bounds: tuple[int, int]) -> tuple[str, str]:
    """Return `(origin_after, dropped)` for a span already present in `dst`.

    ⚑ IT IS A DELETION WITH A WITNESS REQUIREMENT, WHICH IS WHAT MAKES IT SAFE TO OFFER. The
    span is removed only after the destination is shown to hold the same text, so the content
    is never destroyed — it is being un-duplicated. A bare "remove these lines" mode would be
    the same operation with the safety argument left to the caller's turn.
    """
    origin_after, dropped = excise(src.read_text(encoding="utf-8"), *bounds)
    if not dropped.strip():
        msg = "refusing to drop: the span is empty"
        raise ValueError(msg)
    if dropped.strip() not in dst.read_text(encoding="utf-8"):
        msg = (
            "refusing to drop: the destination does NOT hold this text, so dropping it "
            "would delete the only copy — use a move instead"
        )
        raise ValueError(msg)
    return origin_after, dropped


def _drop_main(argv: list[str], span_arg: str, *, apply_it: bool) -> int:
    """Run the `--drop` half of the dispatch and return an exit code."""
    operands = [
        a
        for i, a in enumerate(argv)
        if not a.startswith("--") and not (i and argv[i - 1] == "--span")
    ]
    if len(operands) != _DROP_OPERANDS or not span_arg:
        sys.stderr.write("md_move --drop: need <from.md> <to.md> and --span START-END\n")
        return 2
    src, dst = Path(operands[0]), Path(operands[1])
    try:
        origin_after, dropped = drop(src, dst, parse_span(span_arg))
    except ValueError as exc:
        sys.stderr.write(f"md_move: {exc}\n")
        return 2
    if apply_it:
        src.write_text(origin_after, encoding="utf-8")
    verb = "dropped" if apply_it else "would drop"
    sys.stdout.write(
        f"{verb} {len(dropped.splitlines())} line(s) from {src} — verified present in {dst}\n"
    )
    return 0


def _move_main(argv: list[str], span_arg: str, *, apply_it: bool) -> int:
    """Run the move half of the dispatch and return an exit code."""
    operands = [
        a
        for i, a in enumerate(argv)
        if not a.startswith("--") and not (i and argv[i - 1] == "--span")
    ]
    if len(operands) != _OPERANDS or not span_arg:
        sys.stderr.write("md_move: need <from.md> <to.md> <heading> and --span START-END\n")
        sys.stderr.write(_USAGE)
        return 2

    src, dst, heading = Path(operands[0]), Path(operands[1]), operands[2]
    try:
        bounds = parse_span(span_arg)
        origin_after, dest_after, moved = move(src, dst, heading, bounds, exact="--exact" in argv)
    except (LookupError, ValueError) as exc:
        sys.stderr.write(f"md_move: {exc}\n")
        return 2

    if apply_it:
        # ⚑ BOTH, AFTER BOTH DERIVED. Writing the origin first would, on a destination write
        # failure, leave the entry deleted and unfiled — the one outcome a move must not have.
        dst.write_text(dest_after, encoding="utf-8")
        src.write_text(origin_after, encoding="utf-8")
    verb = "moved" if apply_it else "would move"
    sys.stdout.write(
        f"{verb} lines {bounds[0]}-{bounds[1]} ({len(moved.splitlines())} line(s)) "
        f"from {src} into {heading!r} in {dst}\n"
    )
    return 0


def main(argv: list[str]) -> int:
    """Read argv, route to the move or drop half, and return an exit code.

    ⚑ THE TWO HALVES ARE SEPARATE FUNCTIONS BECAUSE THE GATE SAID SO — `PLR0911` fired the
    moment `--drop` joined `main`, which is the per-file gate reporting that the dispatch had
    grown a second job. Split rather than relieved.
    """
    if not argv or "--help" in argv or "-h" in argv:
        sys.stdout.write(_USAGE)
        return 0

    span_arg = ratchet_flags.arg_after(argv, "--span")
    apply_it = "--apply" in argv
    if apply_it == ("--dry-run" in argv):
        sys.stderr.write("md_move: state exactly one of --apply / --dry-run\n")
        return 2
    if "--drop" in argv:
        return _drop_main(argv, span_arg, apply_it=apply_it)
    return _move_main(argv, span_arg, apply_it=apply_it)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
