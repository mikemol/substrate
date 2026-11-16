#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read where a module's bulk sits — per file, or across the corpus. A READING, not a verdict.

⚑⚑⚑ THE SIZE BUDGET IS RETIRED (Ⓝ80), AND THAT CHANGES WHAT THIS PRINTS RATHER THAN WHETHER IT
RUNS. Line-length paydown is superseded by n-splitting, the lint hooks and single-responsibility;
the operator's reason is that a paydown record kept as comments is *"exactly as toxic as a file
doing too much, from an LLM attention/integrity perspective"*. So the cap is retained as a
REFERENCE MARK a reading is stated against — where the bulk is, and how it compares to a line
this corpus once drew — and is no longer a finding a reader must act on. A reading that stops
being a verdict does not stop being a reading.

⚑⚑⚑ AND THE OPERAND USED TO BE DISCARDED IN SILENCE, WHICH IS THE WORSE HALF OF THAT. `module_size
scripts/sppf_db.py` returned the FULL corpus census, byte-identical to the bare call. A reader who
passes a path and finds their file in the output believes they scoped the query — a true line for
the wrong reason, which is worse than an error, and it was used to scope a dispatch wave twice.
`substrate.tool_cli` records the identical defect one layer up and REFUSES the operand there,
because its census predicates are CORPUS-RELATIVE and scoping would be a different statistic
wearing the same mode name.

⚑⚑ HERE THE OPPOSITE RESOLUTION IS THE HONEST ONE, AND THE REASON IS IN `size_budget`, NOT IN
TASTE. `budget_for` is keyed on the PATH ALONE — a base right-shifted once per recorded incident
for that file — so every column of a row (`code`, `physical`, `defs`, `cap`, `why`) is FILE-LOCAL.
Scoping computes the same numbers over fewer files; it is not a second statistic. Only the
denominator line is corpus-wide, and a scoped run says how many files it read, so no reader can
mistake one for the other. ⚑ THE TWO MODULES DIFFER IN WHAT THEIR STATISTIC DEPENDS ON, and
copying `tool_cli`'s refusal here would refuse a question this tool can answer exactly.

⚑ `--size` COULD NOT REPORT A FILE THAT PASSES, AND THAT IS THE QUESTION A SPLIT ASKS. The
origin appended a row only when there was a finding, so a decomposition that had just cut a
module got back an empty list — indistinguishable from "no file was read". The next question
after every cut is *how far under did it land*, and the fallback was running a second mode to
recover a number the first one had computed and thrown away. Here `census` returns EVERY row and
`over_budget` is a FILTER over it — one body, one predicate.

⚑⚑ ONE BODY, BECAUSE TWO IS HOW `agda_files()` BECAME FOUR. The origin's `module_size` and
`module_size_all` each counted lines; only the predicate differed, so only the predicate is
written twice here. And the origin's count was the NAIVE one — `strip() and not
startswith("#")` — which reads every docstring line as bulk. `substrate.code_lines` is the
authority for that question and this module does not re-derive it.

⚑ `physical` IS APPENDED, NOT INSERTED BESIDE `code`. Three selftest cases in the origin index
these rows positionally, and widening in the middle would have shifted every field under every
existing reader at once — the positional-read defect reproduced in the census that reports it.
This module returns a NAMED record instead, which retires the hazard rather than working
around it.

⚑ NO UNTYPED LAMBDA AS A SORT KEY. `sorted(rows, key=lambda r: r.headroom)` types as
`Callable[[Any], Any]` under this repo's checker and taints every expression downstream — the
`Any`-leak class the promotion exists to clear. A named, annotated accessor costs two lines.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path

from mikemol.corpus import tree_root

from substrate import corpus, size_budget
from substrate.code_lines import code_count, physical_count


@dataclass(frozen=True)
class SizeRow:
    """One module's size reading: its counts, its reference mark, and where its bulk sits."""

    path: str
    code: int
    physical: int
    defs: int
    entrypoints: int
    cap: int
    incidents: int
    why: str

    @property
    def headroom(self) -> int:
        """Report how many code lines this module has left against its reference mark."""
        return self.cap - self.code


def _headroom_of(row: SizeRow) -> int:
    """Return a row's headroom as a sort key — named and typed, never an inline lambda."""
    return row.headroom


def _entrypoint_lines(tree: ast.Module) -> list[int]:
    """Return the line of each top-level `if __name__ == "__main__"` guard, in order."""
    return [n.lineno for n in tree.body if isinstance(n, ast.If) and "__main__" in ast.dump(n.test)]


def _definition_count(tree: ast.Module) -> int:
    """Count every def and class anywhere in the tree — nested ones included.

    ⚑ REPORTED ALONGSIDE THE LINE COUNT because 1,200 lines over 40 small functions is a
    different object from 1,200 lines over 3, and the cap alone cannot tell them apart.
    """
    return sum(
        1
        for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    )


def read_one(path: Path, label: str, base: int = size_budget.OVERLARGE_LINES) -> SizeRow | None:
    """Return the size reading for one file, or None when it cannot be read or parsed.

    ⚑ NONE IS "NOT MEASURED", NOT "MEASURED AS ZERO". A file that will not parse has no honest
    line census, and emitting a row of zeros for it would let an unparseable module read as the
    smallest in the corpus — a fact about the reader reported as a fact about the file.
    """
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return None
    code = code_count(source)
    entry = _entrypoint_lines(tree)
    cap, hits = size_budget.budget_for(label, base)
    why = [
        w
        for w in (size_budget.entrypoint_finding(entry), size_budget.explain(label, code, base))
        if w
    ]
    return SizeRow(
        path=label,
        code=code,
        physical=physical_count(source),
        defs=_definition_count(tree),
        entrypoints=len(entry),
        cap=cap,
        incidents=hits,
        why="; ".join(why),
    )


def census(
    root: Path | None = None, base: int = size_budget.OVERLARGE_LINES
) -> tuple[list[SizeRow], int]:
    """Return `(rows, files scanned)` for the whole corpus — passing modules included.

    ⚑ THE DENOMINATOR IS RETURNED EVEN WHEN NOTHING IS FLAGGED. `0 findings` and `0 findings
    over 998 files` are the same finding; only the second lets a reader see the scan happened.

    ⚑⚑ AND THE LABEL RAISED FROM A BORROWING CHECKOUT (gate-G245 / gate-G249 / gate-G252) —
    the walk followed the caller's CWD by design while the label measured against SUBSTRATE's
    root, so the census died on its first foreign row. `tree_root` carries one root and does
    both, so the tree that was walked is the tree that labels.
    """
    where = root if root is not None else corpus.ROOT
    tree = tree_root.of(where)
    paths = [Path(p) for p in corpus.py_files(root=where)]
    rows = []
    for path in paths:
        row = read_one(path, tree.label(path), base)
        if row is not None:
            rows.append(row)
    return rows, len(paths)


class UnreadableOperandError(ValueError):
    """A named operand could not be measured — refused rather than dropped from the reading.

    ⚑ THE DEFECT THIS MODULE IS BEING REPAIRED FOR IS AN OPERAND THAT VANISHES. Silently omitting
    an unreadable file from a scoped reading would reproduce it one layer down: the caller named
    N paths, got fewer rows, and nothing said which went missing or why.
    """


def scoped(
    operands: tuple[str, ...], root: Path | None = None, base: int = size_budget.OVERLARGE_LINES
) -> tuple[list[SizeRow], int]:
    """Return `(rows, files read)` for exactly the named paths — the operand, honoured.

    ⚑⚑ THE SAME NUMBERS OVER FEWER FILES, WHICH IS WHY THIS IS SCOPING RATHER THAN A SECOND
    STATISTIC. `size_budget.budget_for` reads the path alone, so a row computed here is
    byte-identical to that file's row in the full census. Contrast `substrate.tool_cli`, which
    refuses its operand precisely because its predicates are corpus-relative and the scoped
    answer would NOT match.

    ⚑ AN UNREADABLE OPERAND REFUSES RATHER THAN THINNING THE ROSTER, because a reading whose
    denominator quietly shrinks is the vanishing-operand defect wearing a smaller hat.

    ⚑ THE LABEL IS THE REPO-RELATIVE PATH WHEN THE FILE IS UNDER THE ROOT, because that is the
    key `size_budget.INCIDENT_HALVINGS` matches on. Labelling a scoped row by its bare argument
    would silently miss a recorded halving and print a WIDER reference mark than the full census
    gives the same file — two readings of one file that disagree.
    """
    where = root if root is not None else corpus.ROOT
    tree = tree_root.of(where.resolve())
    rows = []
    for operand in operands:
        path = Path(operand)
        # ⚑ THE TOLERANT LABEL HAD FIVE SPELLINGS AND NOW HAS ONE. This site already caught the
        # `ValueError` by hand — correct, and invisible to the crash census precisely BECAUSE it
        # did — while `census` above raised. One tree, one labeller, one behaviour.
        row = read_one(path, tree.label(path.resolve()), base)
        if row is None:
            msg = (
                f"{operand}: cannot be read or parsed — refusing to drop it silently from a "
                "scoped reading. A roster that thins without saying so is the discarded "
                "operand this mode exists to retire."
            )
            raise UnreadableOperandError(msg)
        rows.append(row)
    return rows, len(operands)


def over_budget(rows: list[SizeRow]) -> list[SizeRow]:
    """Filter `rows` to the ones sitting past their reference mark — one body, one predicate."""
    return [r for r in rows if r.why]


def render(rows: list[SizeRow], scanned: int) -> str:
    """Return the reading: the modules past their reference mark, then the denominator.

    ⚑ THE WORDING IS A READING'S, NOT A VERDICT'S (Ⓝ80). "over budget" named an action a reader
    was expected to take; the budget is retired, so the line now says where the bulk SITS and
    against which mark. The numbers are unchanged — only the claim they make about the reader's
    obligations is.
    """
    flagged = over_budget(rows)
    lines = [
        f"  {r.path}: {r.code} code / {r.physical} physical, {r.defs} def(s) — {r.why}"
        for r in flagged
    ]
    lines.append(
        f"{len(flagged)} past the reference mark of {len(rows)} read "
        f"({scanned} file(s) scanned) "
        f"— ⚑ a READING (Ⓝ80: the size budget is retired), not a verdict"
    )
    return "\n".join(lines) + "\n"


_USAGE = (
    "module_size.py — where a module's bulk sits. A READING, not a verdict (Ⓝ80).\n"
    "\n"
    "usage: module_size.py [--all]                 the whole corpus\n"
    "       module_size.py <path.py> [<path.py>…]  exactly the named files\n"
    "       module_size.py --all <path.py> […]     the named files, with headroom\n"
    "\n"
    "  --all   also print every row's headroom against its reference mark, tightest first\n"
)


def _headroom_lines(rows: list[SizeRow]) -> str:
    """Return each row's headroom against its reference mark, tightest first."""
    return "".join(
        f"  {row.path}: {row.code}/{row.cap} ({row.headroom:+d} headroom)\n"
        for row in sorted(rows, key=_headroom_of)
    )


def main(argv: list[str]) -> int:
    """Read the corpus, or exactly the paths named — never both, and never silently one.

    ⚑⚑ AN OPERAND IS HONOURED OR REFUSED; IT IS NEVER DISCARDED. That is the whole repair: the
    previous body computed the corpus census and dropped `argv`'s paths on the floor, returning
    an answer that read as scoped. An unknown FLAG refuses too, for the same reason — a flag this
    tool does not implement, accepted and ignored, is the same defect spelled with a dash.
    """
    operands = tuple(a for a in argv if not a.startswith("-"))
    unknown = [a for a in argv if a.startswith("-") and a != "--all"]
    if unknown:
        sys.stderr.write(f"module_size: unknown flag(s) {' '.join(unknown)}\n{_USAGE}")
        return 2
    try:
        rows, scanned = scoped(operands) if operands else census()
    except UnreadableOperandError as refused:
        sys.stderr.write(f"module_size: {refused}\n")
        return 2
    sys.stdout.write(render(rows, scanned))
    if "--all" in argv:
        sys.stdout.write(_headroom_lines(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
