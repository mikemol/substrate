# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Refuse a glob that means different things to different matchers, and list what one does match.

⚑⚑⚑ A PATTERN IS NOT PORTABLE JUST BECAUSE IT WORKS. `glob` and `fnmatch` disagree in three ways
that are silent at the call site, and a caller who only ever tested against disk arms a trap for
whoever later reads the same pattern against a git revision. **A six-module drop shipped exactly
that way** — the pattern selected one depth on disk and every depth at the revision, and the
smaller result read as a smaller corpus rather than as a bug.

⚑⚑ THE THREE DISAGREEMENTS, EACH ITS OWN REFUSAL:

  * `**` INSIDE A SEGMENT is not a segment wildcard at all — `glob` reads `src**` as a plain `*`
    and `fnmatch` has no `**` concept whatever.
  * `**/` CANNOT MATCH ZERO SEGMENTS in either matcher, so every depth-0 path is dropped. That is
    the silent one: the drop looks like a smaller corpus.
  * A BARE `*` OR `?` crosses `/` under `fnmatch` and does not under `glob`, so a multi-segment
    pattern selects one depth on disk and every depth at a revision.

⚑ THE CHECK IS A PROPERTY OF THE PATTERN ALONE — no filesystem, no revision. That is what makes it
testable without a corpus AND what makes the refusal deterministic rather than a function of what
happens to be on disk.

⚑⚑ AND THE REFUSAL IS SOURCE-INDEPENDENT ON PURPOSE. It fires on the working tree too, where the
pattern happens to be exact. A check that only fired on the lossy branch would let the trap be
armed by a caller who never touched the other source — which is precisely how the drop shipped.
Opting out is possible and is NOT a way to make a pattern portable: it is a caller ESTABLISHING
that it only ever reads one source.

⚑ THIS DOES NOT BECOME A FILE-DISCOVERY AUTHORITY. It answers *what paths exist here*, which is a
narrower question than *which files matter* — that stays with the corpus readers that own it.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from collections.abc import Sequence

#: The segment wildcard, meaningful only as a WHOLE segment.
DEEP = "**"

#: The characters that make a segment a pattern rather than a literal.
WILDCARDS = ("*", "?", "[")


class AmbiguousPatternError(ValueError):
    """Raised for a pattern whose meaning depends on which matcher reads it.

    ⚑ A DISTINCT TYPE, so a caller can tell *this pattern is a trap* from *this pattern matched
    nothing*. Collapsing them would make the refusal indistinguishable from an empty corpus, which
    is the shape the refusal exists to prevent.
    """


class Ambiguity(NamedTuple):
    """Why one pattern is not portable, and what to write instead.

    ⚑ THE REMEDY IS PART OF THE FINDING. A refusal naming only the defect leaves a caller to guess
    a replacement, and the guess is usually the same pattern with one more star — which is how the
    second and third disagreements above get reached from the first.
    """

    pattern: str
    reason: str
    remedy: str

    def why(self) -> str:
        """Return a one-line account naming the pattern, the reason and the remedy."""
        return f"{self.pattern!r}: {self.reason} — {self.remedy}"


def _segment_deep(segments: Sequence[str]) -> Ambiguity | None:
    """Return the ambiguity when `**` appears inside a segment rather than as one."""
    for seg in segments:
        if DEEP in seg and seg != DEEP:
            return Ambiguity(
                "/".join(segments),
                f"`{seg}` uses `**` inside a segment, where it is only a segment wildcard when it "
                f"is a WHOLE segment",
                "glob reads it as a plain `*` here and fnmatch has no `**` at all, so split the "
                "segment or use a whole `**`",
            )
    return None


def _leading_deep(segments: Sequence[str]) -> Ambiguity | None:
    """Return the ambiguity when a non-final `**` silently drops the shallowest paths."""
    if DEEP in segments and segments[-1] != DEEP:
        prefix = "/".join(segments[: segments.index(DEEP) + 1])
        return Ambiguity(
            "/".join(segments),
            "`**/` cannot match ZERO segments in either matcher, so every depth-0 path is dropped",
            f"the drop is silent because it looks like a smaller corpus — use the depth-agnostic "
            f"`{prefix}` and filter by suffix, which both matchers read identically",
        )
    return None


def _crossing_star(segments: Sequence[str]) -> Ambiguity | None:
    """Return the ambiguity when a bare wildcard crosses `/` under one matcher only."""
    if DEEP in segments or len(segments) <= 1:
        return None
    if not any(w in seg for seg in segments for w in WILDCARDS):
        return None
    return Ambiguity(
        "/".join(segments),
        "`*` and `?` cross `/` under fnmatch and do not under glob",
        f"so this selects one depth on disk and every depth at a revision — use "
        f"`{'/'.join(segments[:-1])}/**` and filter by suffix",
    )


def ambiguity(pattern: str) -> Ambiguity | None:
    """Return why `pattern` is not portable across matchers, or None when it is.

    ⚑ THE ORDER IS DELIBERATE: the malformed-segment case is reported before the zero-segment one,
    because a pattern with both is fixed by addressing the segment first and reporting the second
    would send a reader to the wrong end of it.
    """
    segments = pattern.split("/")
    for check in (_segment_deep, _leading_deep, _crossing_star):
        found = check(segments)
        if found is not None:
            return found
    return None


def listdir(pattern: str, root: Path | str, *, strict: bool = True) -> list[str]:
    """Return the root-relative paths matching `pattern`, sorted, refusing an ambiguous one.

    ⚑ SORTED BY ONE NAMED ORDER, because a caller diffing this listing against another source's
    depends on the two being comparable — and two separate incidental sorts are an agreement
    nobody stated.

    ⚑⚑ `strict=False` IS AN ESTABLISHED FACT, NOT A CONVENIENCE. It says the caller has determined
    it reads exactly one source; it does not make the pattern portable, and a caller passing it to
    silence a refusal has moved the trap rather than removed it.
    """
    if strict:
        found = ambiguity(pattern)
        if found is not None:
            raise AmbiguousPatternError(found.why())

    base = Path(root)
    return sorted(str(hit.relative_to(base)) for hit in base.glob(pattern))
