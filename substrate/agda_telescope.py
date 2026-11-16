# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""Find a module header's span and read its parameter groups — the telescope authority.

⚑⚑⚑ THE FOURTH UNIT OUT OF THE `agda_lex` PROMOTION. That module is reached from 91 BARE import
sites across 63 files with ZERO dotted ones (`module_importers agda_lex`), so the tree's most
shared reader is unimportable from any packaged consumer. `mask_comments` came out as
`substrate.agda_mask`, the naming trio as `substrate.agda_naming`, statement segmentation as
`substrate.agda_statements`; this is the telescope group, read by `split_lemmas`,
`split_telescoped`, `hoist_telescope_imports` and the `check_discharge_ratchet` gate.

⚑⚑ `span` AND `groups` ARE ONE AUTHORITY IN TWO PARTS, and the origin says so outright: a
single-line header puts its groups on the header LINE, so widening the span reader without the
group reader hands a caller a span whose groups read as `[]` — *"a worse failure than the old
None, because a caller would believe it had a parameter-free telescope rather than knowing it
had none."* They are drained together for that reason.

⚑⚑⚑ EVERY RULE HERE COST A MISDIAGNOSIS, WHICH IS WHY IT CANNOT BE REWRITTEN FROM MEMORY:

  * A ONE-LINE HEADER CAN STILL CARRY A TELESCOPE. The old guard read `\bwhere\s*$` as "no
    telescope", stating a DEFINITION where a CHECK was needed. Measured on a real module with
    one parameter and ten imports above the header: a splitter asked whether to decline, got
    None, split anyway, and emitted thirteen leaves carrying neither the parameter nor the
    above-header imports — misdiagnosed as an import-seed bug THREE times before the header was
    read. The test is *are there parameter groups*, never *does it span lines*.
  * AN ARBITRARY CONTINUATION BOUND SILENTLY DROPS DECLARATIONS. Two census tools capped the
    header walk at six lines and then skipped when no `where` was found. Measured over the
    corpus: 401 multi-line headers, 136 needing MORE than six, the deepest needing forty. A
    census that skips a third of its own population reports a low number and looks healthy.
  * THE GROUP SCAN IS DEPTH-TRACKED. A nested group inside a parameter's type must not
    terminate the outer group; a naive scan truncated real parameters mid-type.
  * AND FLATTENING IS THE WRONG QUESTION. A scope reader returns a parameter's name AND the
    locals bound inside its type — right for *is this name bound here*, wrong for *which
    parameters does this leaf need*, which is about GROUPS. A splitter using the flat list
    emits a local as a parameter.

⚑ THE SPAN IS A PARAMETER TO `groups` BECAUSE THE PARSING WAS NEVER THE FILE-SCOPED PART. The
span reader deliberately skips an indented or non-column-0 header, since an inner `module _ (…)`
obeys ordinary import rules — so a file whose telescope lives on an inner module reads as having
none. The group parser is already correct there; only the span was wrong, and adding a second
group parser for inner modules would be the one-capability-several-bodies defect.

⚑⚑ WHETHER A ONE-LINE SPAN INCLUDES ITS OWN HEAD IS THE CALLER'S FACT, NOT THE TEXT'S, and no
inspection of the line can settle it: an inner parameterized head and a root parameterized head
are the same shape at column 0. A DERIVED span may read its head line; an EXPLICIT span keeps
the older contract, where `(0,1)` includes a one-line inner head and `(1,1)` deliberately reads
nothing. Conflating them silently redefined a splitter's inner path.
"""

from __future__ import annotations

import re

from substrate import agda_mask, agda_statements

# ⚑ ONE HEAD PATTERN FOR ALL THREE KEYWORDS. A `record … where` telescope binds parameters the
# same way a `module` one does — measured, where a positional-scope reader reported
# `no-candidate` for names that are BOUND rather than defined, and that class dominated the
# census tail. The keyword differs; the binding form does not, so a second scanner would be a
# rival authority for one relation.
MODULE_HEAD = re.compile(r"^(\s*)(?:module|record|data)\s+(\S+)")

_WHERE_TAIL = re.compile(r"\bwhere\s*$")
_BRACKET = re.compile(r"[({]")


def head_span(lines: list[str], i: int, limit: int | None = None) -> int:
    """Return the EXCLUSIVE end index of the header starting at `lines[i]`.

    ⚑⚑ `limit` IS A TERMINATION BOUND, NOT A CAPABILITY BOUND, and the difference is the whole
    point. It exists only as a runaway guard for a malformed file with no `where` at all, and
    defaults to the rest of the file so a legitimate header of any length is found. Two census
    tools once capped this at six continuations and skipped when they found no `where`: measured
    over the corpus, 401 multi-line headers of which 136 need more than six and the deepest
    needs forty. A census dropping a third of its own population reports a low number and looks
    healthy — the failure a paydown-only ratchet must never have.
    """
    n = len(lines)
    stop = n if limit is None else min(n, i + limit)
    j = i
    while j < stop and "where" not in lines[j]:
        j += 1
    return j + 1 if j < stop else i + 1


def _one_line_span(line: str, at: int, end: int) -> tuple[int, int] | None:
    """Return the span for a header whose `where` closes its own line, or None.

    ⚑⚑⚑ THE TEST IS FOR PARAMETER GROUPS, NEVER FOR LINE COUNT. Reading `where` at end-of-line
    as "no telescope" states a definition where a check is needed, and it returned None for
    every single-line parameterized header in the tree.
    """
    mid = line[end:]
    mid = mid[: mid.rfind("where")]
    return (at, at) if _BRACKET.search(mid) else None


def telescope_span(src: str) -> tuple[int, int] | None:
    """Return the INCLUSIVE `(start, end)` of the file's own top-level module header.

    Returns None when that header carries no telescope.

    ⚑⚑ THE TELESCOPE IS PARSED BEFORE THE MODULE BODY EXISTS, so a name it mentions must be in
    scope from an import placed BEFORE the header. An import after the header is too late even
    though the file plainly imports it — measured live, where a module used an equality operator
    in its telescope with the import on the file's LAST line and failed to parse, because the
    operator's fixity was not yet in the grammar. The mechanism is POSITIONAL, and an earlier
    reading of it as a fixity-across-the-parameter-boundary problem was retracted.

    ⚑ ONLY THE FILE'S OWN TOP-LEVEL MODULE COUNTS. An anonymous inner `module _ (…)` is inside
    the body, where ordinary import rules already apply — so an indented or non-column-0 header
    is skipped. Pass an explicit span to `telescope_groups` to read one of those.
    """
    lines = agda_mask.mask_comments(src).split("\n")
    for i, line in enumerate(lines):
        found = MODULE_HEAD.match(line)
        if not found or found.start() != 0 or len(line) - len(line.lstrip()):
            continue
        if _WHERE_TAIL.search(line):
            return _one_line_span(line, i, found.end())
        j = i
        depth = agda_statements.depth_after(line, 0)
        head = line
        n = len(lines)
        while (
            "where" not in head
            and j + 1 < n
            and (depth > 0 or agda_statements.continues(lines[j + 1], depth))
        ):
            j += 1
            depth = agda_statements.depth_after(lines[j], depth)
            head += " " + lines[j].strip()
        return (i, j) if "where" in head else None
    return None


def _group_text(lines: list[str], span: tuple[int, int], *, derived: bool) -> str:
    """Return the text the parameter groups live in, for one span.

    ⚑⚑ A SINGLE-LINE HEADER PUTS ITS GROUPS ON THE HEAD LINE, where the `start+1` slice is empty
    — so a derived one-line span must read its head. But ONLY when that line is itself a header:
    an EXPLICIT `(1,1)` is the inner-module convention meaning *read nothing*, and reading the
    head unconditionally silently redefined what an explicit span means for a splitter's inner
    path. Keying on the head pattern keeps the two readings apart.
    """
    start, end = span
    head = lines[start] if 0 <= start < len(lines) else ""
    found = MODULE_HEAD.match(head) if (derived and start == end) else None
    if found is None:
        return "\n".join(lines[start + 1 : end + 1])
    text = head[found.end() :]
    return text[: text.rfind("where")] if "where" in text else text


def telescope_groups(src: str, span: tuple[int, int] | None = None) -> list[tuple[list[str], str]]:
    """Return `[(names, verbatim_text)]` for each binder group of a module telescope.

    `span` defaults to the file's own top-level header. Pass one explicitly to read an INNER
    `module M (…) where` with this same parser.

    ⚑⚑ THE GROUP IS RETURNED VERBATIM so a leaf can re-declare it exactly, alongside the names
    it BINDS so a caller can select groups by what a body uses. Flattening to names alone is the
    wrong question: a scope reader also returns the locals bound inside a parameter's TYPE, and
    a splitter using that list emits a local as a parameter.

    ⚑ DEPTH-TRACKED, so a nested group inside a parameter's type does not terminate the outer
    one. A naive scan truncated real parameters mid-type.
    """
    derived = span is None
    if span is None:
        span = telescope_span(src)
    if span is None:
        return []
    lines = agda_mask.mask_comments(src).split("\n")
    text = _group_text(lines, span, derived=derived)

    out: list[tuple[list[str], str]] = []
    depth = 0
    start: int | None = None
    for i, char in enumerate(text):
        if char in "({":
            if depth == 0:
                start = i
            depth += 1
        elif char in ")}":
            depth -= 1
            if depth == 0 and start is not None:
                group = text[start : i + 1]
                head = group[1:-1].split(":", 1)[0]
                out.append(([t for t in head.split() if t], group))
    return out
