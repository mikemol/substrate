# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""Read WHICH characters a checker objects to, and WHERE — string, docstring, or comment.

⚑⚑⚑ THE ESCAPE SET MUST BE THE CHECKER'S, NOT MINE (gate-G203). `substrate.glyph_escape` takes
the characters to escape as an argument, deliberately — but a caller that HAND-WROTE that set
would be a second authority on a rule ruff owns, and it would drift in both directions at once.
Measured (gate-G205): an authored set held seven where the checker names nineteen, missing the
multiplication sign, the minus sign, the en dash and logical or.

⚑⚑⚑ AND THE POSITION MATTERS AS MUCH AS THE CHARACTER, WHICH A FIRST CUT COLLAPSED. A named
escape denotes its character only INSIDE a string literal; the same spelling in a COMMENT is
literal backslash-N text that turns the comment into noise — and the round-trip check cannot
catch it, because both sides decode identically. So the three rules are kept apart:

  * `RUF001` — a string literal. ESCAPABLE.
  * `RUF002` — a docstring. ESCAPABLE, since a docstring is a string.
  * `RUF003` — a comment. NOT ESCAPABLE, and a caller must be told rather than left to discover
    it in a corrupted record.

⚑⚑ A COMMENT-FLAGGED CHARACTER IS A BLOCKING THIRD OUTCOME, not an error and not something to
filter out silently. Dropping it would shrink the escape set without saying why, leaving a write
refused for a reason nobody can see; raising would lose the escapable set the caller can still
act on. It is reported beside the others so the caller can decide.

⚑⚑ A CHECKER'S OUTPUT IS A STRUCTURED ARTIFACT WITH NO READER, WHICH IS WORK RATHER THAN A
LICENCE TO GREP. The messages have an exact shape — a rule code, then ``ambiguous `<char>`
(<UNICODE NAME>)`` — so both the position and the character are recoverable by a program.
Eyeballing them in a turn is a judgement that evaporates when the turn ends.

⚑ AND THE NAME IN THE MESSAGE IS A CROSS-CHECK, NOT DECORATION. The checker states both the
character and what it calls it, so a reader can verify it resolved the same character the checker
meant. A parse that got the wrong character would otherwise be silently plausible, and it would
escape the wrong thing in a record nobody re-reads.
"""

from __future__ import annotations

import re
import unicodedata
from typing import NamedTuple

#: The shape of a confusable-character finding: the rule code, then the character between
#: backticks and the Unicode name between parentheses. ⚑ THE RULE CODE IS CAPTURED because it is
#: what says whether the character sits somewhere a named escape can reach.
AMBIGUOUS = re.compile(r"(RUF00[123])[^`\n]*ambiguous `(.)` \(([A-Z0-9 \-]+)\)")

#: Rules whose finding sits inside a string, where a named escape denotes the character.
ESCAPABLE_RULES = frozenset({"RUF001", "RUF002"})

#: The rule whose finding sits in a comment, where a named escape would become literal text.
COMMENT_RULE = "RUF003"


class Flagged(NamedTuple):
    """The characters a checker objected to, split by whether an escape can reach them.

    ⚑ A CHARACTER APPEARING IN BOTH POSITIONS LANDS IN BOTH SETS, which is correct and is the
    case a caller must handle: the string occurrences can be escaped while the comment ones
    cannot, so the file is not fully clearable by escaping alone.

    ⚑ `mismatched` IS NOT AN ERROR LIST — it is the reader admitting a gap. A row where the
    parsed character's own Unicode name differs from the name the checker printed means the two
    disagree about what was said, and a caller must resolve that before escaping anything.
    """

    escapable: frozenset[str]
    comment_only: frozenset[str]
    mismatched: tuple[tuple[str, str], ...]

    @property
    def clearable(self) -> bool:
        """Report whether escaping alone can clear every confusable finding.

        ⚑ DERIVED, NEVER STORED. A flag held beside the sets could disagree with them, which is
        how a green verdict outlives the fact it summarised.
        """
        return not self.comment_only and not self.mismatched

    def why(self) -> str:
        """Return a one-line account naming the components, never a bare count.

        ⚑ THE COMPONENTS ARE PRINTED BECAUSE THE VERDICT IS ASSERTED ON (gate-G204): a caller
        that reads only a number cannot tell an empty finding list from a failed parse.
        """
        names = sorted(unicodedata.name(c, "?") for c in self.escapable)
        parts = [f"{len(self.escapable)} escapable ({names})"]
        if self.comment_only:
            blocked = sorted(unicodedata.name(c, "?") for c in self.comment_only)
            parts.append(f"⚑ {len(self.comment_only)} in COMMENTS, not escapable: {blocked}")
        if self.mismatched:
            parts.append(
                f"⚑ {len(self.mismatched)} row(s) UNCONFIRMED: {list(self.mismatched)[:3]}"
            )
        if self.clearable:
            parts.append("escaping alone clears every confusable finding")
        return " — ".join(parts)


def flagged_in(report: str) -> Flagged:
    """Return the characters `report` flags, split by position and confirmed against their names.

    ⚑⚑ EACH ROW IS CROSS-CHECKED AGAINST THE NAME THE CHECKER PRINTED. A regex that captured the
    wrong character — an off-by-one in the backtick span, a multi-byte glyph split — would
    otherwise yield a plausible set that escapes the wrong things.

    ⚑ AN UNCONFIRMED ROW IS CARRIED, NOT DROPPED AND NOT RAISED. Dropping it would shrink the
    escape set silently, which is the direction that leaves a write refused for a reason the
    caller cannot see.

    ⚑ THE MATCH GROUPS ARE NARROWED AT EXTRACTION, because `Match.group` is `Any` and every
    comparison downstream would then type-check against nothing — including the rule test that
    decides whether a character is escapable at all.
    """
    escapable: set[str] = set()
    comment: set[str] = set()
    bad: list[tuple[str, str]] = []
    for found in AMBIGUOUS.finditer(report):
        rule, char, claimed = str(found.group(1)), str(found.group(2)), str(found.group(3))
        if unicodedata.name(char, "") != claimed:
            bad.append((char, claimed))
        elif rule in ESCAPABLE_RULES:
            escapable.add(char)
        elif rule == COMMENT_RULE:
            comment.add(char)
    return Flagged(frozenset(escapable), frozenset(comment), tuple(bad))
