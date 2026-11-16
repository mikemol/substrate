#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read the worklist warrants THROUGH THE ENGINE — the half that needs paperkit installed.

⚑⚑⚑ THIS EXISTS SO THE DEPENDENCY IS VISIBLE IN THE IMPORT GRAPH RATHER THAN HIDDEN BEHIND A
CHAIN (gate-G209). A peer measured that `scratch/bibstruct.py` was unreachable in EVERY mode for
a consumer without a paperkit venv — not one mode, all of them — because the chain
`bibstruct -> bibstruct_main -> bib_handlers -> warrant_bib -> paperkit.bib` runs at MODULE LOAD.
Both of us had reasoned about which modes touch the engine; the answer was that importing the CLI
at all does.

⚑⚑ AND THE TOP-LEVEL IMPORT IS KEPT, NOT MADE LAZY. `warrant_bib`'s docstring argues for it
against a recorded ruling — *"NOO. No sys.path modification"* — and a declared dependency at
module scope is what paperkit's packaging exists to support. Deferring the import into a function
would have weakened that to *declared where used*, and hidden the dependency one level deeper
rather than one level shallower. The split does the opposite: a module that needs the engine says
so in its own imports, and a module that does not never pulls it.

⚑⚑⚑ SO THE SEAM IS THE ENGINE, NOT A FILE SIZE. `consumer_fields` reads the project's TOML with
the standard library and needs nothing installed; `records` calls the engine's parser. Those are
two different reachability classes that happened to share a module, and every consumer of the
first was paying the second's cost.

⚑ THE PARSER'S RETURN IS NARROWED AT THIS SEAM, which is why the narrowing lives here rather than
in a caller. The engine ships no `py.typed`, so a raw return would carry `Any` into every field
read downstream — one assertion at the boundary keeps the readers concretely typed.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import paperkit.bib
from mikemol.witness.warrant_bib import WarrantError, consumer_fields

from substrate import warrant_bib

if TYPE_CHECKING:
    from pathlib import Path


class BibError(RuntimeError):
    """The bib could not be read as a mapping of warrants."""


def records(path: Path | None = None) -> dict[str, dict[str, str]]:
    """Return `{key: record}` for the warrants, parsed by the engine.

    ⚑ THE PARSER'S RETURN IS NARROWED HERE, AT THE SEAM. The engine ships no `py.typed`, so a
    raw return would carry `Any` into every field read downstream. One assertion at the boundary
    — beside the stub that types the import — keeps the readers concretely typed.

    ⚑⚑ AND THE PROJECT'S CONSUMER FIELDS ARE PASSED, which is what stops the engine dropping
    `enables` and saying so fourteen times per read. The declaration was already in `paper.toml`;
    what was missing was this argument. mtools' reader takes the config EXPLICITLY; substrate's
    `warrant_bib.CONFIG` supplies it (root debt, W36).
    """
    parsed: object = paperkit.bib.parse(
        path or warrant_bib.BIB, consumer_fields(warrant_bib.CONFIG)
    )

    if not isinstance(parsed, dict):
        msg = f"the engine's parser returned {type(parsed).__name__}, not a mapping"
        raise BibError(msg)

    out: dict[str, dict[str, str]] = {}
    for key, rec in parsed.items():
        if isinstance(key, str) and isinstance(rec, dict):
            out[key] = {k: str(v) for k, v in rec.items() if isinstance(k, str)}
    return out


def claim_of(key: str, path: Path | None = None) -> str:
    """Return one warrant's `claim` prose, whitespace-collapsed.

    ⚑ THE WITNESS READS THE CLAIM, NOT A COPY OF IT. A witness carrying its own copy of the
    figure is two derived views of one fact with nothing reconciling them — the defect this repo
    has paid for in four `agda_files()` bodies.
    """
    rec = records(path).get(key)
    if rec is None:
        msg = f"no warrant @{key} in {path or warrant_bib.BIB}"
        raise WarrantError(msg)
    if "claim" not in rec:
        msg = f"warrant @{key} has no claim field"
        raise WarrantError(msg)
    return " ".join(rec["claim"].split())


def tag(key: str, name: str, path: Path | None = None) -> int:
    """Return the integer in the claim's own `[name=N]` marker.

    ⚑ REFUSES WHEN ABSENT. An unanchored figure is a number nobody can audit, and defaulting it
    to zero would let a witness compare against a bound the claim never made.
    """
    prose = claim_of(key, path)
    found = re.search(rf"\[{re.escape(name)}=(-?\d+)\]", prose)
    if not found:
        msg = f"claim {key} is UNANCHORED: no [{name}=N] tag in its prose"
        raise WarrantError(msg)
    return int(found.group(1))
