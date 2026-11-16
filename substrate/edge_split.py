#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Split a declared consumer edge field into its targets — the re-split the engine requires.

⚑⚑⚑ A DECLARED CONSUMER FIELD ARRIVES AS A STRING, NOT A LIST, AND THE OWNING DOCUMENT SAYS SO.
`catalog/worklist/paper.toml` records it measured on a real parse by paperkit's own owner:

    enables  = {A, B}   declared consumer field  ->  str   'A, B'
    rests-on = {A, B}   built-in _LIST field     ->  list  ['A', 'B']

*"`consumer_fields` joins `_SCALAR`; `_LIST` is hardcoded and closed to per-project extension.
**Any consumer MUST re-split.**"* This module is that re-split, in one place.

⚑⚑ THE FAILURE IS SILENT AND SHAPED LIKE SUCCESS. A consumer that does not re-split does not
crash — it reads ONE target whose name is `"A, B"`, a key matching no entry. So a multi-target
edge degrades to a single dangling one, and a dangling-edge report names a key nobody wrote. The
count stays plausible; only the membership is wrong.

⚑ AND IT IS A SECOND SPELLING OF ONE VOCABULARY, WHICH IS WHY IT IS ITS OWN MODULE. The built-in
edge fields need no splitting and the declared one does; a caller that has to remember which is
which will eventually forget, and the forgetting is invisible. `targets` takes either and returns
the same shape.

⚑ EXTRACTED FOR ⟡items-n-split, on top of the promoted `raw_bib`.
"""

from __future__ import annotations

# ⚑ THE SEPARATOR THE DECLARATION ITSELF SHOWS: `{A, B}` renders as `'A, B'`. Comma-plus-optional
# -space, with each target stripped — a consumer splitting on `","` alone keeps a leading space
# on every target after the first, which is the same dangling-key defect one character narrower.
SEPARATOR = ","


def targets(raw: object) -> tuple[str, ...]:
    """Return the targets a raw edge value names, whether it arrived as a string or a list.

    ⚑ BOTH SHAPES, DELIBERATELY. The engine hands a built-in `_LIST` field as a list and a
    declared consumer field as a string, and a caller holding a field name cannot tell which it
    has without knowing the engine's internals. Accepting either is what makes the re-split
    impossible to forget at a call site.

    ⚑⚑ AN EMPTY OR BLANK VALUE YIELDS NO TARGETS, NOT ONE BLANK TARGET. `enables = {}` is an
    entry declaring no enablement; returning `('',)` would put an unnameable key into every
    downstream edge set and report it as dangling.
    """
    if isinstance(raw, (list, tuple)):
        found = [str(item).strip() for item in raw]
    else:
        found = [part.strip() for part in str(raw).split(SEPARATOR)]
    return tuple(name for name in found if name)


def edges(fields: dict[str, str], names: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    """Return `{field: targets}` for each named edge field the entry carries."""
    return {name: targets(fields[name]) for name in names if name in fields}


def render(key: str, found: dict[str, tuple[str, ...]]) -> str:
    """Return one entry's edges as text, naming the field each target came from."""
    if not found:
        return f"  {key}: no edges\n"
    lines = [f"  {key}:"]
    lines.extend(f"    {field:<9} -> {', '.join(names)}" for field, names in sorted(found.items()))
    return "\n".join(lines) + "\n"


def speak() -> str:
    """Return what this module is, its entry points, and the capability its name lacks.

    ⚑ THE SEPARATOR IS READ FROM THE CONSTANT, NEVER RESPELLED IN THE PROSE. A usage text that
    types the comma is a second spelling of `SEPARATOR`, and the two disagree the day the
    declaration's rendering changes — the same drift this module exists to absorb at the parse.
    """
    return (
        "edge_split is a LIBRARY — it re-splits a declared consumer edge field into targets.\n"
        "\n"
        f"  targets(raw)         -> the targets a raw value names, split on {SEPARATOR!r},\n"
        "                          taking EITHER a string (declared field) or a list (_LIST)\n"
        "  edges(fields, names) -> {field: targets} for each named edge field an entry carries\n"
        "  render(key, found)   -> one entry's edges as text\n"
        "\n"
        "⚑ IT DOES NOT READ A BIB, AND THE NAME SUGGESTS IT MIGHT. There is no path argument\n"
        "  and no parse here: it splits a value a caller already holds. `substrate.warrant_bib`\n"
        "  is what reads the entries whose fields these are.\n"
        "\n"
        "usage: edge_split.py --selftest\n"
    )


# ⚑ `--selftest` DELEGATES TO THE SIBLING SUITE (⟡selftest-discovery); ANY other invocation
# REFUSES with exit 2 rather than exiting 0 in silence (⟡the-three-silent). The prior guard
# returned 0 for a bare run, which prints nothing — indistinguishable from a query that matched
# nothing, the false zero `store_calls` was repaired for and this module reproduced.
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        from substrate import edge_split_selftest

        sys.exit(edge_split_selftest.selftest())
    sys.stderr.write(speak())
    sys.exit(2)
