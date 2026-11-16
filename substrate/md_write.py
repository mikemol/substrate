#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The CLI for a BOUNDED markdown write — replace or append inside ONE named section.

⚑⚑⚑ THIS EXISTS BECAUSE THE CAPABILITY WAS UNREACHABLE, NOT BECAUSE IT WAS MISSING.
`substrate.md_sections` has performed bounded section writes since the ⟡mdstruct-n-split, and
`md_spans.find_section` grew an `exact=` escape on 2026-09-02 for headings wholly contained in
another. But the only command-line route to either is `scratch/mdstruct.py`, which is FROZEN at
~1525 findings under the per-file gate: its duplicate `find_section` cannot be retired and its
dispatch cannot be extended until the monolith drains. So the escape existed in the package and
could not be invoked, and the document that motivated it stayed unwritable.

⚑⚑ AND AN INLINE `python3 -c` IS NOT THE WAY AROUND THAT — `hook_no_chaining` refuses it, and is
right to: a script that dies with the turn puts the judgement in the turn. A capability reachable
only by retyping its wiring each time is not reachable. **A missing mode is WORK.**

⚑ THE WRITE IS A LINE SPLICE performed by `md_sections`, which returns TEXT and does not write —
so a dry run and an apply share one derivation rather than being two paths that can disagree.
This module owns only the argv reading, the `--apply` gate, and what gets reported.

⚑ `--exact` IS AN ESCAPE, NOT A DEFAULT. Substring matching lets a caller name a section without
reproducing its punctuation, which is right for the common case; exact matching is for the case
where NO substring separates two headings, and the ambiguity refusal would otherwise be permanent.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from substrate import md_sections, ratchet_flags

if TYPE_CHECKING:
    from mikemol.mdstruct import spans as md_spans

_USAGE = """\
md_write — a bounded write into ONE section of a markdown document

    python3 -m substrate.md_write <file> <heading> --body-file <f> [--append|--replace]
                                  [--exact] (--apply | --dry-run)

    --append     add to the END of the section, before the next heading (default)
    --replace    swap the section's BODY, heading untouched
    --exact      match the heading WHOLE, for one contained in another
    --apply      write the file; without it, report what would change

⚑ AMBIGUITY AND ABSENCE BOTH REFUSE, naming the candidates — the target is a write.
"""

_OPERANDS = 2


def _report(path: Path, span: md_spans.Span, *, applied: bool) -> str:
    """Return the one line describing what was hit.

    ⚑ IT NAMES THE SECTION, NEVER JUST "done". A write that reports only success leaves the
    reader to re-derive which section moved — and the whole point of a bounded write is that
    the bound is observable. ⚑ The span is passed WHOLE rather than destructured: it is one
    value, and splitting it into four parameters is how a signature grows past reading.
    """
    verb = "wrote" if applied else "would write"
    return (
        f"{verb} into {'#' * span.level} {span.text!r} (lines {span.start}-{span.end}) in {path}\n"
    )


def main(argv: list[str]) -> int:
    """Read argv, perform or preview one bounded section write, and return an exit code."""
    if not argv or "--help" in argv or "-h" in argv:
        sys.stdout.write(_USAGE)
        return 0

    body_file = ratchet_flags.arg_after(argv, "--body-file")
    apply_it = "--apply" in argv
    # ⚑ A FLAG'S VALUE IS NOT AN OPERAND, and reading argv as "everything without a leading
    # `--`" counts it twice — the file, the heading, AND the body path, so a correct invocation
    # is refused for having three operands. The value is CONSUMED by the flag that named it.
    operands = [
        a
        for i, a in enumerate(argv)
        if not a.startswith("--") and not (i and argv[i - 1] == "--body-file")
    ]

    if len(operands) != _OPERANDS or not body_file:
        sys.stderr.write("md_write: need <file> <heading> and --body-file\n")
        sys.stderr.write(_USAGE)
        return 2
    if apply_it == ("--dry-run" in argv):
        # ⚑ NEITHER DEFAULTS. A default-dry silently does nothing when you meant to write; a
        # default-apply silently writes when you meant to look. Intent must be STATED — the
        # contract `drop_dead_renames` converged on and this toolkit is adopting.
        sys.stderr.write("md_write: state exactly one of --apply / --dry-run\n")
        return 2

    path, heading = Path(operands[0]), operands[1]
    body = Path(body_file).read_text(encoding="utf-8")
    edit = md_sections.replace_section if "--replace" in argv else md_sections.append_to_section
    try:
        new, span = edit(path, heading, body, exact="--exact" in argv)
    except LookupError as exc:
        sys.stderr.write(f"md_write: {exc}\n")
        return 2

    if apply_it:
        path.write_text(new, encoding="utf-8")
    sys.stdout.write(_report(path, span, applied=apply_it))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
