# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""Segment Agda source into IMPORT / OPEN / VARIABLE statements, spans included.

⚑⚑⚑ THE THIRD UNIT OUT OF THE `agda_lex` PROMOTION, AND IT IS THE ONE FOUR GATES READ. That
module is reached from 91 BARE import sites across 63 files with ZERO dotted ones
(`module_importers agda_lex`), so the tree's most-shared reader is unimportable from any
packaged consumer. `mask_comments` came out as `substrate.agda_mask` and the naming trio as
`substrate.agda_naming`; this is statement segmentation, which `check_ban_ratchet`,
`check_discharge_ratchet`, `prune_imports` and `drop_dead_renames` all depend on.

⚑⚑ EVERY RULE HERE IS A MEASURED LOSS, WHICH IS WHY IT CANNOT BE REWRITTEN FROM MEMORY. The
origin's own comments record four, each with the input that produced it:

  * A bare `startswith(" ")` continuation test SWALLOWS the next import inside a nested
    `module M where`, because that import is indented too — and a caller that deletes the span
    deletes a valid unrelated import. Measured as the Discipline.agda loss.
  * A KEYWORD-ONLY guard is not enough either: inside `module M where` an import is followed by
    indented DEFINITIONS (`x : Nat`) that open no keyword, so the span absorbs them. Measured on
    the F17 fixture, which took span (2,4) where (2,3) was right.
  * INSIDE AN OPEN PAREN NOTHING OPENS A STATEMENT. A wrapped `using (…)` list may legitimately
    begin a later line with `module`, because `using (…; module WithTarget)` re-exports a
    submodule. Measured: over the whole corpus EXACTLY ONE statement diverges between the depth
    rule and a depth-blind keyword guard, and the keyword guard TRUNCATES the using-list and
    silently drops the re-export.
  * The module-name pattern is PERMISSIVE BY DESIGN: `(\S+)` over-accepts a trailing `;` and
    `[\w.'-]+` under-accepts, so it takes everything up to a delimiter. A wrong parse here is
    worse than a permissive one, and every caller filters on the `Substrate` prefix anyway.

⚑ THE INPUT IS EXPECTED COMMENT-MASKED, and that is the caller's job rather than this module's.
`substrate.agda_mask.mask_comments` is the authority; masking here would hide from the caller
that the masking happened and would re-mask text a caller has often already masked.

⚑⚑ AND THE SPAN IS HALF-OPEN, `lines[start:end]`, matching the origin exactly. Every consumer
slices with it, so an off-by-one would not fail here — it would delete a line somewhere else.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Literal, NamedTuple

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator, Sequence

# ⚑ THE ONE OPENER SET. A continuation is an indented line that is NOT itself a new statement,
# and this names every keyword that starts one.
NEXT = re.compile(
    r"\s*(?:open\s+import|import|open|module|private|"
    r"postulate|infix|infixl|infixr|record|data|\{-#)\b"
)

# ⚑ A KEYWORD SET IS NOT ENOUGH — see the module docstring's second bullet. A continuation also
# stops at any line that opens a DECLARATION, or the span absorbs the definitions following an
# import inside a nested module.
_DECL = re.compile(r"\s*[^\s:;{}()@|]+(?:\s+[^\s:;{}()@|]+)*\s*(?::(?!:)|=)")

_IMPORT = re.compile(r"^\s*(?:open\s+import|import)\s")
_OPEN = re.compile(r"^\s*open\s+(?!import\b)")
_VAR = re.compile(r"^\s*(?:private\s+)?variable\b")

# ⚑ PERMISSIVE BY DESIGN — see the module docstring's fourth bullet.
_MODNAME = re.compile(r"^\s*(?:open\s+import|import)\s+([^\s;(){}]+)")

#: What a segmented statement can be. ⚑ A TYPE ALIAS RATHER THAN A TUPLE OF STRINGS, so the
#: checker proves the kind reaching `Stmt` is one of these rather than trusting a runtime test.
Kind = Literal["import", "open", "variable", "other"]


class Stmt(NamedTuple):
    """One statement and the half-open line span it occupies."""

    kind: Kind
    module: str | None
    start: int
    end: int
    text: str


def depth_after(text: str, depth: int) -> int:
    """Return the paren depth after `text`, starting from `depth`.

    ⚑ EXPECTS COMMENT-MASKED INPUT. A paren inside a comment would otherwise open a depth that
    never closes, and every following line would read as a continuation.
    """
    for char in text:
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
    return depth


def continues(line: str, depth: int = 0) -> bool:
    """Report whether `line` continues the statement above it.

    ⚑⚑ INSIDE AN OPEN PAREN, NOTHING OPENS A NEW STATEMENT. A wrapped `using (…)` list may
    legitimately begin a line with `module`, since `using (…; module WithTarget)` re-exports a
    submodule. Over the whole corpus exactly ONE statement distinguishes this rule from a
    depth-blind keyword guard — and on that one the keyword guard truncates the using-list and
    silently drops the re-export. The depth test is the difference between the rules on real
    input, not defensive polish.
    """
    if not (line.startswith((" ", "\t")) and line.strip()):
        return False
    if depth > 0:
        return True
    return not NEXT.match(line) and not _DECL.match(line)


def module_name(head: str) -> str | None:
    """Return the dotted module an import head names, or None.

    ⚑ ONE ACCEPTANCE LANGUAGE, where the tree once had six. Permissive on purpose: callers
    filter on the `Substrate` prefix, so over-accepting a delimiter costs nothing and
    under-accepting drops a real edge.
    """
    found = _MODNAME.match(head)
    return found.group(1) if found else None


def _kind_of(line: str) -> Kind | None:
    """Return which kind of statement `line` opens, or None when it opens none.

    ⚑ RETURNS THE LITERAL TYPE ITSELF rather than a bare string checked against a roster later.
    A runtime membership test does not narrow a type, so the checker refused the roster form —
    correctly: it could not prove the kind reaching `Stmt` was one the field admits.
    """
    if _IMPORT.match(line):
        return "import"
    if _OPEN.match(line):
        return "open"
    if _VAR.match(line):
        return "variable"
    return None


def statements(lines: Sequence[str]) -> Iterator[Stmt]:
    r"""Yield every import/open/variable statement with its half-open span.

    ⚑ THE SPAN IS `lines[start:end]`, EXCLUSIVE AT THE END, matching the origin exactly. Every
    consumer slices with it, so an off-by-one would not fail here — it would delete a line in
    somebody else's tool.

    ⚑ INDENT-TOLERANT: the openers match at `^\s*`, because this scans a whole FILE and decides
    for itself what opens a statement. `group_statements` is the other shape, for a caller that
    already holds a prelude and its own opener.
    """
    i = 0
    n = len(lines)
    while i < n:
        head = lines[i]
        kind = _kind_of(head)
        if kind is None:
            i += 1
            continue
        j = i + 1
        depth = depth_after(head, 0)
        while j < n and continues(lines[j], depth):
            depth = depth_after(lines[j], depth)
            j += 1
        yield Stmt(
            kind,
            module_name(head) if kind == "import" else None,
            i,
            j,
            " ".join(x.strip() for x in lines[i:j]),
        )
        i = j


def span_end(lines: Sequence[str], i: int) -> int:
    """Return the EXCLUSIVE end of the statement starting at `lines[i]`.

    ⚑⚑⚑ THIS IS THE SPAN AUTHORITY, AND ITS HISTORY IS THE ARGUMENT FOR HAVING ONE. The origin
    records it being lifted out of an import-rewriting tool where it was a LEADING-UNDERSCORE
    name imported by SEVEN other files — *"a `_`-name consumed across module boundaries is
    public API wearing a private label."* The home was wrong twice over: the rule is LEXICAL, a
    two-line wrapper over the continuation predicates, while the tool it lived in declares its
    job as modifying import blocks. A tool that only needed to know where a statement ends had
    to import an import-rewriter to find out.

    ⚑⚑ AND IT WAS STILL BEING RE-DERIVED. `scripts/check_ban_ratchet.py` — a BLOCKING gate —
    defines its own `_span_end` reaching two private names, one line below importing the module
    that already exports this. Its own comment says *"span via the ONE authority, not
    re-derived"* while re-deriving it, and ruff flags the reach three times as `SLF001`. Homing
    it here, where `continues` and `depth_after` are public, makes that a one-line call.

    ⚑ IT MASKS EACH LINE ITSELF, unlike `statements`, because a caller holding raw source lines
    is the shape every consumer of this function actually has. `statements` takes pre-masked
    text because it scans a whole file; this answers about one statement in a list a caller
    already holds.
    """
    from substrate import agda_mask  # noqa: PLC0415

    j = i + 1
    depth = depth_after(agda_mask.mask_comments(lines[i]), 0)
    while j < len(lines) and continues(lines[j], depth):
        depth = depth_after(agda_mask.mask_comments(lines[j]), depth)
        j += 1
    return j


def group_statements(lines: Sequence[str], opener: Callable[[str], bool]) -> list[list[str]]:
    r"""Group an ALREADY-COLLECTED prelude into statements, by the caller's own opener.

    ⚑⚑ DISTINCT FROM `statements`, AND THE DIFFERENCE IS LOAD-BEARING. That one scans a whole
    file and decides for itself what opens a statement, indent-tolerantly. This takes a caller's
    opener over a list already known to be prelude-only — the shape a splitter needs, whose
    openers are COLUMN-0-ANCHORED on purpose, since only a col-0 `open`/`import`/`variable` is
    file-scoped there and an indented one is body. Widening this to `^\s*` would hoist body
    lines into the prelude.

    ⚑ A CONTINUATION IS ANY LINE THE OPENER DOES NOT MATCH, exactly as the four byte-identical
    copies this replaced had it.
    """
    out: list[list[str]] = []
    cur: list[str] | None = None
    for line in lines:
        if opener(line):
            if cur:
                out.append(cur)
            cur = [line]
        elif cur is not None:
            cur.append(line)
    if cur:
        out.append(cur)
    return out
