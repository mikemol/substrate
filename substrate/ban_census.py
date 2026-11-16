# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""Census the banned import directives on `Substrate.*` imports — the ban gate's key set.

⚑⚑⚑ THE FIRST CONSUMER-SIDE UNIT OF THE `agda_lex` PROMOTION, AND THAT IS THE POINT (gate-F72).
Five units were drained and `module_importers substrate.agda_mask` reported five sites, ALL of
them the drain's own siblings, while the origin held at 91 bare imports. Building a replacement
and repointing a consumer are different acts, and only the first was happening. This is the
census half of `scripts/check_ban_ratchet.py`, lifted so a BLOCKING gate stops re-deriving what
the package already owns.

⚑⚑ THE GATE REACHED TWO PRIVATE NAMES TO DO WHAT `span_end` DOES. Its local `_span_end` called
`agda_lex._depth_after` and `agda_lex._continues` — flagged three times by ruff as `SLF001` —
one line below importing the module that exports `span_end` publicly, under a comment reading
*"span via the ONE authority, not re-derived"* while re-deriving it. Here the span comes from
`substrate.agda_statements.span_end`, so the sentence is true.

⚑⚑⚑ AND THE SPAN RULE IS LOAD-BEARING IN A WAY UNIQUE TO A RATCHET. The naive
every-indented-line-continues rule absorbs the telescope of a following parameterized module
header. In a WRITE tool that deletes source — 33 files gutted in one arc. In a GATE it corrupts
the CENSUS, and *a mis-parsing gate launders its own bug into a paydown-only baseline, where it
can never be un-banked.* The origin measured the two rules across the whole corpus and found
they disagree on ZERO import statements, which is the only safe condition for changing a gate.

⚑ THE KEY SHAPE IS THE BASELINE'S, AND IT MAY NOT DRIFT. `<relpath>::<module>::<directive>` is
what the committed baseline holds; a key spelled differently reads as a NEW offender and the
ratchet refuses the commit, so this is a contract with a file on disk rather than an internal
convention.

⚑ WHAT STAYS BEHIND, DELIBERATELY. The gate's `main` binds the ratchet machinery and the file
walk, both of which live in unpackaged `scripts/` modules. That is the same line drawn for
`agda_root_from` and `agda_files`: the filesystem and the baseline are the application's, and
this is the pure function over lines.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from substrate import agda_mask, agda_statements

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

# ⚑ THE IMPORT HEAD, ANCHORED ON `Substrate` — the ban is about this tree's own modules, since
# a stdlib import carries no splitting obligation.
IMPORT_HEAD = re.compile(r"^(\s*)(open\s+import|import)\s+(Substrate[\w.'-]*)")

#: The bracketed directives the ban forbids. `as` is separate — it takes a bare name, not a
#: parenthesised list, so one pattern cannot cover both without over-matching.
DIRECTIVES = ("using", "renaming", "hiding")

_AS = re.compile(r"\bas\s+\S")


def directives_in(tail: str) -> list[str]:
    """Return which banned directives `tail` carries, in declaration order.

    ⚑ `as` IS MATCHED SEPARATELY because its syntax differs: the others open a parenthesised
    list, `as` takes a bare name. A single pattern admitting both would over-match, and an
    inflated census manufactures false new keys that a paydown-only baseline then defends.
    """
    found = [d for d in DIRECTIVES if re.search(r"\b" + d + r"\s*\(", tail)]
    if _AS.search(tail):
        found.append("as")
    return found


def keys_for(rel: str, lines: Sequence[str]) -> set[str]:
    """Return every `<relpath>::<module>::<directive>` key one file's lines carry.

    ⚑⚑ STATEMENT-AWARE, NOT LINE-WISE. An import's `using (…)` clause may sit on an indented
    continuation, and a line-wise scan misses it — the same blindness that once let 158 narrowed
    re-exports escape a different census. The span comes from the authority rather than a local
    rule, which is what this module exists to correct.

    ⚑ THE LINES ARE EXPECTED COMMENT-STRIPPED by the caller, matching the origin: a
    commented-out import is not an import, and masking here would re-mask what the walk already
    masked.
    """
    keys: set[str] = set()
    i = 0
    n = len(lines)
    while i < n:
        head = IMPORT_HEAD.match(lines[i])
        if not head:
            i += 1
            continue
        end = agda_statements.span_end(lines, i)
        text = " ".join(s.strip() for s in lines[i:end])
        mod = head.group(3)
        # ⚑ THE TAIL IS WHAT FOLLOWS THE MODULE NAME. Searching the whole statement would match
        # a directive spelled inside the module path itself.
        tail = text.split(mod, 1)[1] if mod in text else ""
        keys.update(f"{rel}::{mod}::{d}" for d in directives_in(tail))
        i = end
    return keys


def census(sources: Iterable[tuple[str, str]]) -> set[str]:
    """Return the ban census over `(relpath, source_text)` pairs.

    ⚑⚑ THE WALK IS THE CALLER'S, AND THAT IS THE PACKAGING LINE. Enumerating the tree needs a
    filesystem root and an `_build` exclusion, both of which belong to the application — the
    same boundary drawn for the naming module's root-finder. Taking pairs keeps this a pure
    function of text, so a case can drive it without a tree.

    ⚑ COMMENTS ARE MASKED HERE rather than assumed, because a caller passing raw source is the
    likely mistake and a commented-out import would then be censused as a live offender — which
    in a paydown-only ratchet is a key nobody can ever remove.
    """
    keys: set[str] = set()
    for rel, text in sources:
        keys |= keys_for(rel, agda_mask.mask_comments(text).split("\n"))
    return keys
