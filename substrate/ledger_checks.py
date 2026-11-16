#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Census the ledger bibs' `check` fields — delegation, duplicates, and who runs a tool (W40).

⚑⚑ THIS MODULE MEASURED THE ROSTER CLEANROOM, AND ITS ROSTER MODES ARE RETIRED. It compared each
bib `check` with the `WITNESSES` literal (`--versus`), measured which roster notes the bibs did not
carry (`--notes`), and showed one pair side by side (`--note-pair`). Their results are recorded in
the paths-forward ledger — 850 of 850 checks agree, 0 differ; 846 of 846 notes carried — and the
roster itself is retiring into the bibs, so a comparison against it would compare the bibs with
themselves. Each retired spelling REFUSES and names its recorded result, never silently vanishes.

⚑ READS THROUGH `bib_parse` and `witness_bibrows` — never a text filter over a tool's output.

    python -m substrate.ledger_checks <bib> [<bib> ...]                  non-delegating entries
    python -m substrate.ledger_checks --duplicates <bib> [<bib> ...]     multiply-homed keys
    python -m substrate.ledger_checks --invoking <roster> <word>         witnesses running <word>
    python -m substrate.ledger_checks --values <field> <bib> [...]       distinct values + counts
    python -m substrate.ledger_checks --lacking <field> <bib> [...]      entries without the field
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from substrate import bib_parse, witness_bibrows

if TYPE_CHECKING:
    from collections.abc import Callable

# The check spelling that delegates to the roster witness of the same key.
DELEGATE = "item:"

# How a brace is spelled when a moved note's braces do not balance. ⚑ DEFINED HERE and IMPORTED by
# the mover (`ledger_converge`), so the substitution has one spelling.
LBRACE = "⟨lbrace⟩"
RBRACE = "⟨rbrace⟩"

# The retired roster modes, and the recorded result each refusal names.
RETIRED = {
    "--versus": "850 of 850 bib checks agreed with the roster, 0 differed",
    "--notes": "846 of 846 roster notes are carried by the bibs (mode rows carry none)",
    "--note-pair": "the sample pair (gate-G57) showed a faithful paraphrase, not a summary",
}

# The exit a refused invocation returns.
_REFUSED = 2


def delegates(key: str, check: str) -> bool:
    """Report whether `check` is exactly `item:<key>` — a delegation to the roster witness."""
    return check == f"{DELEGATE}{key}"


def spelled(note: str) -> str:
    """Return `note` with its braces spelled as the declared tokens."""
    return note.replace("{", LBRACE).replace("}", RBRACE)


def _entries(paths: list[Path]) -> list[tuple[str, str, str]]:
    """Return `(bib, key, check)` for every entry across `paths`, sorted by key within each bib."""
    out: list[tuple[str, str, str]] = []
    for path in paths:
        entries = bib_parse.parse(path.read_text(encoding="utf-8"))
        out.extend(
            (path.name, key, fields.get("check", "")) for key, fields in sorted(entries.items())
        )
    return out


def census(paths: list[Path]) -> list[tuple[str, str, str]]:
    """Return `(bib, key, check)` for every entry whose `check` does not delegate to its witness."""
    return [row for row in _entries(paths) if not delegates(row[1], row[2])]


def duplicates(paths: list[Path]) -> list[tuple[str, list[str], dict[str, list[str]]]]:
    """Return `(key, bibs, {field: value-per-bib})` for every key declared in several `paths`.

    ⚑ A COMPOSED READ KEEPS THE LATER DECLARATION, SILENTLY. `bibstruct --orphans` names such keys
    but not whether the copies AGREE — and the choice of home differs completely between the two
    cases: identical copies need only one deleted; differing copies are two claims, and deleting
    either loses one. Only DIFFERING fields are returned, each with its value in every home (in
    `bibs` order); an empty mapping means the declarations are identical.
    """
    homes: dict[str, list[tuple[str, dict[str, str]]]] = {}
    for path in paths:
        for key, fields in bib_parse.parse(path.read_text(encoding="utf-8")).items():
            homes.setdefault(key, []).append((path.name, dict(fields)))
    out: list[tuple[str, list[str], dict[str, list[str]]]] = []
    for key, decls in sorted(homes.items()):
        if len(decls) == 1:
            continue
        names = sorted({field for _, fields in decls for field in fields})
        values = {n: [fields.get(n, "") for _, fields in decls] for n in names}
        differ = {n: vals for n, vals in values.items() if len(set(vals)) > 1}
        out.append((key, [bib for bib, _ in decls], differ))
    return out


def invoking(roster: Path, word: str) -> list[tuple[str, str, str]]:
    """Return `(key, kind, command)` for every ledger witness whose command argv holds `word`.

    ⚑ THE QUESTION A TOOL'S DEPARTURE ASKS OF THE LEDGER: which witnesses stop running when the
    tool leaves the tree. A witness's command is DATA, so this reads the parsed argv — never a text
    filter over a file, which would also count every note that merely MENTIONS the tool. The
    command travels with the key, because re-homing a witness needs to know WHAT it runs.

    ⚑ READ FROM THE BIBS (`witness_bibrows`), not the `WITNESSES` literal: the roster file names
    the ledger PROJECT (its directory), whose warrant bibs now carry every witness as its `check`.
    """
    out: list[tuple[str, str, str]] = []
    for row in witness_bibrows.rows(roster.parent):
        first = row.args[0] if row.args else None
        if isinstance(first, list) and any(word in str(arg) for arg in first):
            out.append((row.key, row.kind, " ".join(str(arg) for arg in first)))
    return out


def _main_census(argv: list[str]) -> int:
    """Print every entry whose `check` does not delegate to its roster witness."""
    paths = [Path(a) for a in argv]
    rows = census(paths)
    for bib, key, check in rows:
        sys.stdout.write(f"  {bib}  {key}  {check or '(no check)'}\n")
    total = len(_entries(paths))
    sys.stdout.write(f"{len(rows)} of {total} entries do not delegate to their roster witness\n")
    return 0


def _main_duplicates(argv: list[str]) -> int:
    """Print each multiply-declared key, where it lives, and whether its copies agree."""
    rows = duplicates([Path(a) for a in argv])
    for key, bibs, differ in rows:
        said = "IDENTICAL" if not differ else "DIFFER in " + ", ".join(differ)
        sys.stdout.write(f"  {key}\n      in {' and '.join(bibs)} — {said}\n")
        for field, vals in differ.items():
            for bib, val in zip(bibs, vals, strict=True):
                sys.stdout.write(f"      {field} [{bib}]: {val}\n")
    sys.stdout.write(f"{len(rows)} key(s) declared in more than one bib\n")
    return 0


def _main_invoking(argv: list[str]) -> int:
    """Print every witness whose command invokes `argv[1]`, then the count by kind."""
    rows = invoking(Path(argv[0]), argv[1])
    for key, kind, command in rows:
        sys.stdout.write(f"  {kind:<10} {key}\n      runs: {command}\n")
    kinds = sorted({kind for _, kind, _ in rows})
    split = ", ".join(f"{sum(1 for _, k, _ in rows if k == kind)} {kind}" for kind in kinds)
    sys.stdout.write(f"{len(rows)} witness(es) invoke {argv[1]!r} ({split or 'none'})\n")
    return 0


def values(field_name: str, paths: list[Path]) -> dict[str, tuple[int, list[str]]]:
    """Return `{value: (entries holding it, bibs it appears in)}` for one field across `paths`.

    ⚑ THE QUESTION A RUBRIC ASKS OF ITS WARRANTS: which section keys are actually in use, how
    heavily, and where. `--field` lists one row per entry; the distinct set with counts is an
    aggregation, and aggregating a tool's output in the shell is the judgement-in-the-turn this
    repo forbids — so it is a mode. An entry without the field counts under the empty value, so a
    missing section is visible rather than silently absent.
    """
    seen: dict[str, tuple[int, list[str]]] = {}
    for path in paths:
        for fields in bib_parse.parse(path.read_text(encoding="utf-8")).values():
            value = fields.get(field_name, "")
            count, bibs = seen.get(value, (0, []))
            seen[value] = (count + 1, bibs if path.name in bibs else [*bibs, path.name])
    return dict(sorted(seen.items()))


def _main_values(argv: list[str]) -> int:
    """Print each distinct value of `argv[0]` across the bibs, with its count and homes."""
    rows = values(argv[0], [Path(a) for a in argv[1:]])
    for value, (count, bibs) in rows.items():
        sys.stdout.write(f"  {count:>5}  {value or '(field absent)'}  in {', '.join(bibs)}\n")
    total = sum(count for count, _ in rows.values())
    sys.stdout.write(f"{len(rows)} distinct {argv[0]!r} value(s) over {total} entries\n")
    return 0


def lacking(field_name: str, paths: list[Path]) -> list[tuple[str, str, str]]:
    """Return `(bib, key, claim)` for every entry that does NOT carry `field_name`.

    ⚑ THE COMPLEMENT `--field` CANNOT GIVE: it lists one row per entry that HOLDS the field, so an
    entry missing it is simply absent from the output — the very entries a rubric cannot place.
    The claim travels with the key so the missing value can be decided from the content.
    """
    out: list[tuple[str, str, str]] = []
    for path in paths:
        for key, fields in sorted(bib_parse.parse(path.read_text(encoding="utf-8")).items()):
            if field_name not in fields:
                out.append((path.name, key, fields.get("claim", "")))
    return out


def _main_lacking(argv: list[str]) -> int:
    """Print every entry lacking `argv[0]`, with its claim."""
    rows = lacking(argv[0], [Path(a) for a in argv[1:]])
    for bib, key, claim in rows:
        sys.stdout.write(f"  {bib}  {key}\n      claim: {claim[:140] or '(no claim)'}\n")
    sys.stdout.write(f"{len(rows)} entr(ies) carry no {argv[0]!r}\n")
    return 0


def _every(operands: list[str]) -> list[str]:
    """Select every operand as a path."""
    return operands


def _first(operands: list[str]) -> list[str]:
    """Select only the first operand as a path (the rest are words)."""
    return operands[:1]


def _rest(operands: list[str]) -> list[str]:
    """Select every operand but the first as a path (the first is a field name)."""
    return operands[1:]


# mode -> (fewest operands, most operands or None, which operands are paths, handler).
# ⚑ A TABLE, NOT AN `if`-CHAIN: the per-file gate refused the chain at seven returns — the signal
# that each mode was a branch where it should be a row.
_MODES: dict[
    str,
    tuple[int, int | None, Callable[[list[str]], list[str]], Callable[[list[str]], int]],
] = {
    "--duplicates": (1, None, _every, _main_duplicates),
    "--invoking": (2, 2, _first, _main_invoking),
    "--values": (2, None, _rest, _main_values),
    "--lacking": (2, None, _rest, _main_lacking),
}

# The bare invocation: a census over the bibs named.
_CENSUS = (1, None, _every, _main_census)


def main(argv: list[str]) -> int:
    """Dispatch a mode from `_MODES`, refuse a RETIRED one by name, or run the bare census.

    ⚑ A FLAG-SHAPED OR MISSING PATH IS REFUSED BY NAME, NOT READ — measured when a guessed
    `--summary-only` was taken as a bib path and died in `read_text` with a traceback.
    """
    args = argv[1:]
    if args and args[0] in RETIRED:
        sys.stderr.write(
            f"ledger_checks: {args[0]} is RETIRED with the roster it compared against. Its result "
            f"is recorded in .claude/paths-forward.ledger: {RETIRED[args[0]]}.\n"
        )
        return _REFUSED
    moded = bool(args) and args[0] in _MODES
    lo, hi, select, handler = _MODES[args[0]] if moded else _CENSUS
    operands = args[1:] if moded else args
    for operand in select(operands):
        if operand.startswith("-") or not Path(operand).is_file():
            sys.stderr.write(f"ledger_checks: {operand!r} is not a file this mode can read\n")
            sys.stderr.write(__doc__ or "")
            return _REFUSED
    if len(operands) < lo or (hi is not None and len(operands) > hi):
        sys.stderr.write(__doc__ or "")
        return _REFUSED
    return handler(operands)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
