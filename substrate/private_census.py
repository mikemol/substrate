# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The private-block census — every definition hidden inside a `private` block, as debt.

⚑ POLICY. Under one-definition-per-file there is no module surface to narrow, so a `private`
helper is not a hidden name: it is a SECOND definition living in a file that should hold one.
The repair is to extract it and bind it at its owner, never to delete the keyword and leave
the definition in place.

⚑⚑ `private variable` IS DELIBERATELY NOT CENSUSED, and this is the distinction the predicate
exists to make. It is a BINDING FORM — `private variable a b c : Level` introduces
implicit-argument variables and stops the variable itself leaking as an export — not a hidden
helper. Sweeping the two together would bank false keys into a paydown-only baseline, which is
debt that can never legitimately be paid. The predicate must match the POLICY, not the keyword.

⚑⚑⚑ AND THE MEASUREMENT REQUIRES DE-INDENTING THE BLOCK, which is the recurring bug of this
arc. The declaration scanners expect COLUMN-0 declarations while a `private` block's contents
are indented under it, so two earlier censuses returned ZERO hidden definitions from
ninety-three real blocks — the fifth occurrence of indent-blindness in this arc. `dedent`
before scanning is what makes the number real, and a case pins it.

⚑ EXTRACTED FROM `scripts/check_private_ratchet.py` SO IT CAN BE READ WITHOUT RUNNING THE
GATE. That file does three jobs in a hundred lines — census, gate entry, selftest — and opens
with two `sys.path.insert` calls, so it carries enough findings to refuse every edit. The
census is the half other tools need, and it is the half that can be clean.

⚑⚑ THE SCRATCH DEPENDENCIES LOAD BY LOCATION, NOT BY PATH MUTATION. `agda_lex` (the span and
comment-mask authority) and `split_lemmas` (the declaration scanner) live in `scratch/`, which
is not a package. The origin reached them by inserting two directories onto `sys.path` — an
ambient change that outlives the call and is exactly what this package is draining. The shared
loader names the location instead, so resolution is an INPUT to this module's load.

⚑ AND EVERY DYNAMIC CALL GOES THROUGH `census_call`, whose boundaries are typed by RETURN
SHAPE. `mask_comments` returns text and the scanners return name sets; running the masker
through the set narrower would iterate its string into single CHARACTERS — a plausible value
that is not the answer. Reaching them by hand instead leaks `Any` into every expression that
touches them, which is what pushed a first cut of this file to twenty-six findings with no
defect in its logic.
"""

from __future__ import annotations

import re
import textwrap
from pathlib import Path
from typing import TYPE_CHECKING

from substrate import census_call, corpus, scratch_module

if TYPE_CHECKING:
    from types import ModuleType

# `private` opening a block. ⚑ The `private variable` idiom matches this too and is excluded
# by yielding no definitions, not by a special case — a block that binds nothing contributes
# nothing, so the exclusion falls out of the predicate rather than sitting beside it.
PRIVATE = re.compile(r"^([ \t]*)private\b")

_LEX = "agda_lex"
_SCANNER = "split_lemmas"


def block(lines: list[str], i: int) -> list[str]:
    """Return the indented run under the `private` at `lines[i]`, de-indented.

    ⚑ THE DEDENT IS LOAD-BEARING, NOT TIDINESS. Without it the declaration scanners see
    indented text and report nothing, which is how two censuses read zero against
    ninety-three real blocks.
    """
    ind = len(lines[i]) - len(lines[i].lstrip())
    out: list[str] = []
    for line in lines[i + 1 :]:
        if line.strip() and (len(line) - len(line.lstrip())) <= ind:
            break
        out.append(line)
    return textwrap.dedent("\n".join(out)).splitlines()


def names_in(scanner: ModuleType, block_lines: list[str]) -> set[str]:
    """Return every name a `private` block defines, via both declaration scanners.

    ⚑ BOTH SCANNERS, BECAUSE A RECORD FIELD IS A DEFINITION TOO. `defined_names` misses
    fields and `field_names` misses ordinary declarations; a census running only the first
    under-reports a record-shaped block to zero.
    """
    defined, _defined_why = census_call.str_set_call(
        scanner, "defined_names", block_lines, _SCANNER
    )
    fields, _fields_why = census_call.str_set_call(scanner, "field_names", block_lines, _SCANNER)
    return {n for n in defined | fields if n}


def keys_in(scanner: ModuleType, rel: str, lines: list[str]) -> set[str]:
    """Return `{rel::name}` for every `private` block in one already-masked file."""
    out: set[str] = set()
    for i, line in enumerate(lines):
        if PRIVATE.match(line):
            out |= {f"{rel}::{name}" for name in names_in(scanner, block(lines, i))}
    return out


def census() -> set[str]:
    """Return `{relpath::name}` for every definition hidden in a `private` block.

    ⚑ A LOADER FAILURE RETURNS AN EMPTY SET AND THAT IS A KNOWN LIMIT, not a clean tree.
    A gate must prefer `census_or_why`, which says which of the two happened.
    """
    keys, _why = census_or_why()
    return keys


def census_or_why() -> tuple[set[str], str | None]:
    """Return `(census, None)`, or `(empty, why)` when a scanner could not be loaded.

    ⚑⚑ AN UNLOADABLE SCANNER MUST NOT READ AS A CLEAN TREE. An empty census and a census
    that could not run render identically as a number, and the second one banked into a
    paydown-only baseline would absolve every existing violation permanently.
    """
    lex, why = scratch_module.scratch_module(_LEX)
    if lex is None:
        return set(), why or f"could not load {_LEX}"
    scanner, why = scratch_module.scratch_module(_SCANNER)
    if scanner is None:
        return set(), why or f"could not load {_SCANNER}"

    root = corpus.ROOT
    files, why = census_call.str_set_call(lex, "agda_files", str(root / "agda"), _LEX)
    if why is not None:
        return set(), why

    out: set[str] = set()
    for path in sorted(files):
        text = Path(path).read_text(encoding="utf-8", errors="replace")
        masked, why = census_call.text_call(lex, "mask_comments", text, _LEX)
        if why is not None:
            return set(), why
        out |= keys_in(scanner, str(Path(path).relative_to(root)), masked.splitlines())
    return out, None
