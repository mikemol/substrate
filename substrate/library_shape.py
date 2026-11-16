#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Where the witnesses live, and what they reach for — the T25 family's parameterized body.

⚑⚑⚑ THE THREE SUB-ITEMS ARE ONE QUESTION AT THREE GRAINS, which is what makes them a family
rather than three witnesses. `T25-library` asks WHERE a witness is defined; `T25-parametric` asks
whether it TAKES its inputs; `T25-globals` asks whether it READS a sibling's module state. All
three are answered by the same walk — defs per file, signature per def, names read per body — so
one body parameterized over the roster replaces three that each re-derived it.

⚑⚑ EVERY ONE OF THE THREE CARRIES A RECORDED FALSE-POPULATION INCIDENT, AND THEY SHARE A CAUSE:
each predicated over SOURCE TEXT rather than over the relation. `T25-globals` searched for the
string `SIZES` and so counted ITSELF; `T25-parametric` flagged every witness that called `_tag`,
which is all 17 — *"when a census returns exactly the whole population, suspect the predicate
before the tree."* Both were repaired with a hand-maintained `owners` exclusion set, which is the
allow-list shape: it rots, and nothing says when.

⚑ SO THIS READS THE RELATION, NOT THE TEXT, AND NEEDS NO EXCLUSION LIST. A witness's reach is
`ast.Name` loads resolved against the module's own globals — so a module that MENTIONS a name in
a string literal or a docstring is not reaching for it, and a census scanning its own source
cannot flag itself. The `owners` set disappears because the defect it was patching does not
occur.

⚑ WHAT THIS DOES NOT DO: decide. It reports where defs live and what they read; which of those
facts is OPEN is the witness's job, and `warrant_bib.tag` supplies the figure each claim declares.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split), rewritten rather than moved.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import corpus

if TYPE_CHECKING:
    from pathlib import Path

# Where the keyed library must live, per T25-library's claim. ⚑ ONE SPELLING: the witness, the
# render and the selftest all cite this rather than repeating the path.
LIBRARY = ("catalog", "library", "concepts.py")

# The dispatch module the witnesses are being moved OUT of.
DISPATCH = ("catalog", "library", "items.py")

# Module state a witness must not read from a sibling. ⚑ THE NAMES ARE THE RETIRED CONTRACT:
# a witness deposited its figures in these as a side effect and a caller read them back out.
SHARED_STATE = ("SIZES", "WHY", "PARTS")

# The dispatch module's own machinery — not witnesses, and never was.
#
# ⚑⚑⚑ "EVERY TOP-LEVEL FUNCTION IS A WITNESS" WAS TRUE WHEN WRITTEN AND THE SPLIT IS WHAT MADE IT
# FALSE. While the roster and the claims shared a file, that predicate was exact; the moment the
# witnesses moved out, the roster's own dispatch — the row builders, the drain, `main` — became
# the entire remaining population, and the item reported TEN witnesses in a file holding none.
# **A predicate that measured its subject perfectly can be falsified by the subject's repair**,
# which is the shape that reads as *the work made it worse*.
#
# ⚑ NAMED RATHER THAN INFERRED, because the alternative is worse. A leading underscore would
# exempt `_drain` and admit `main`; "takes no arguments" describes a witness AND `roster()`. What
# these have in common is not a shape — it is that they are the dispatch's own parts, which is a
# fact about ROLE, and role is declared.
#
# ⚑⚑ THE WALK IS MACHINERY TOO, AND THE ITEM'S OWN CLAIM SAYS SO: *"items.py is reduced to roster
# + dispatch."* `_drain` consumes a row stream, `_rows` translates records, `_run` returns a code
# — none of them answers a worklist key, which is what a witness IS. Leaving them in would make
# the item unclosable by its own definition: the dispatch cannot dispatch without them.
MACHINERY = (
    "library",
    "part",
    "verdict",
    "as_row",
    "item_keys",
    "roster",
    "main",
    "_rows",
    "_drain",
    "_run",
)


@dataclass(frozen=True, slots=True)
class Witness:
    """One witness definition, and what it reaches for."""

    name: str
    takes_args: bool
    reads_state: tuple[str, ...]

    @property
    def parametric(self) -> bool:
        """Report whether the witness takes its inputs rather than reaching for them.

        ⚑ ZERO-ARGUMENT IS NOT THE DEFECT BY ITSELF, and the original said so: a witness with its
        data INLINE is parametric in the sense that matters, because nothing reaches out. What
        disqualifies is reaching — so a zero-arg witness that reads no shared state still counts
        as parametric here.
        """
        return self.takes_args or not self.reads_state


def _reads(node: ast.FunctionDef, watched: frozenset[str]) -> tuple[str, ...]:
    """Return the watched names this function LOADS, bare or by attribute.

    ⚑⚑ NAME LOADS, NOT TEXT MATCHES, AND THAT REMOVES THE EXCLUSION LIST. The original scanned
    `inspect.getsource` for a substring, so a census searching for `SIZES` necessarily contained
    it and flagged itself — repaired by hand-listing the owners. An `ast.Name` in a Load context
    is the actual read; a mention in a docstring or a string literal is not a node, so the
    self-reference cannot occur and the list is unnecessary.

    ⚑ BOTH SPELLINGS, because the original missed one. Its first predicate counted only ATTRIBUTE
    reads (`I.SIZES` from another module), so a bare in-module `SIZES` was invisible and the
    claim closed at 0 on a defect that had just been written.
    """
    found: set[str] = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load) and sub.id in watched:
            found.add(sub.id)
        elif (
            isinstance(sub, ast.Attribute) and isinstance(sub.ctx, ast.Load) and sub.attr in watched
        ):
            found.add(sub.attr)
    return tuple(sorted(found))


def witnesses(path: Path, watched: tuple[str, ...] = SHARED_STATE) -> tuple[Witness, ...]:
    """Return every witness defined in `path`, with its signature and its reaches.

    ⚑⚑ THE DISPATCH'S OWN MACHINERY IS EXCLUDED, and forgetting that made this reader report ten
    witnesses in a file holding none. Every top-level function WAS a witness while the roster and
    the claims shared a home; the split is precisely what ended that, so the predicate had to
    learn the difference its subject had just acquired.

    ⚑ A LEADING UNDERSCORE IS NOT THE TEST. It would exempt `_drain` and admit `main`, and what
    the machinery shares is a ROLE rather than a shape — which is why `MACHINERY` names them.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return ()

    watch = frozenset(watched)
    machinery = frozenset(MACHINERY)
    return tuple(
        Witness(
            name=node.name,
            takes_args=bool(node.args.args or node.args.kwonlyargs),
            reads_state=_reads(node, watch),
        )
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name not in machinery
    )


def library(root: Path | None = None) -> Path:
    """Return the keyed library's path — where the witnesses must live."""
    return (root if root is not None else corpus.ROOT).joinpath(*LIBRARY)


def dispatch(root: Path | None = None) -> Path:
    """Return the dispatch module's path — where they must no longer be defined."""
    return (root if root is not None else corpus.ROOT).joinpath(*DISPATCH)


def render(found: tuple[Witness, ...]) -> str:
    """Return the shape census — where the population sits against the three questions."""
    if not found:
        return "  no witness definitions found\n"

    nonparametric = [w for w in found if not w.parametric]
    reaching = [w for w in found if w.reads_state]
    lines = [
        f"  {len(found)} witness definition(s)",
        f"    non-parametric (reach, take nothing): {len(nonparametric)}",
        f"    reading shared state               : {len(reaching)}",
    ]
    lines.extend(f"      {w.name}  reads {', '.join(w.reads_state)}" for w in reaching)
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.stdout.write(render(witnesses(dispatch())))
    sys.exit(0)
