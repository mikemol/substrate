# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Compose several bibs into one read: the entry map, and what collides across files.

⚑⚑⚑ THE COMPOSED CORPUS IS THE UNIT, AND READING ONE FILE AT A TIME PRODUCED FALSE DANGLING EDGES.
A premise declared in a sibling bib is UNRESOLVABLE when that bib is not passed and RESOLVES when it
is — same edge, opposite verdict, decided entirely by what the reader was given. The origin measured
this against a peer's twelve-bib corpus: reading eleven of twelve produced an unstable entry count
and eighteen dangling reports for premises that resolve. **Over-reporting is the dangerous
direction** — it tells an author a sound claim is broken.

⚑⚑ A DUPLICATE KEY ACROSS FILES IS REPORTED, NEVER MERGED SILENTLY, AND THE GAP IT OPENS IS THE
FINDING. A composed read counts DISTINCT KEYS; a record-counting parser counts DECLARATIONS. Both
numbers are right and an unexplained gap between them reads as a parse defect — the origin's note
records a peer ruling exactly that out by hand, at 77 versus 84. So the gap is NAMED in the output
rather than left for a reader to rediscover, and the later declaration is the one that wins.

⚑ COLLISIONS ARE RETURNED, NOT STASHED. The origin held them in a module-level list, so a stale
collision from one read could leak into the next — a defect that only shows up when a colliding read
is followed by a clean one, and never when the clean read runs first. A value cannot leak.

⚑ EXTRACTED, NOT EDITED IN PLACE. `scratch/bibstruct.py` carries enough findings that the per-file
gate refuses every write to it, so this is rebuilt whole and the origin is left alone until it can
be swapped — decompose and replace, never patch behind a gate that cannot pass.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from pathlib import Path

# The fields whose values name another entry. ⚑ ONE ROSTER — the origin spelled the edge kinds at
# each site that walked them, which is how a new edge kind reaches one reader and not another.
EDGE_FIELDS = ("from", "rests-on", "entails", "enables", "reads", "consumes")


@dataclass(frozen=True, slots=True)
class Collision:
    """One key declared in more than one bib, and which declaration won."""

    key: str
    homes: tuple[str, ...]

    @property
    def winner(self) -> str:
        """The declaration that survives composition — the last one read."""
        return self.homes[-1]


@dataclass(frozen=True, slots=True)
class Corpus:
    """Every entry across the bibs read, plus what collided while composing them."""

    entries: dict[str, dict[str, str]]
    collisions: tuple[Collision, ...] = ()
    sources: tuple[str, ...] = field(default_factory=tuple)

    @property
    def declared(self) -> int:
        """How many DECLARATIONS were read, counting a re-declared key once per home.

        ⚑ THIS IS THE OTHER NUMBER, AND CARRYING BOTH IS THE POINT. `len(entries)` counts distinct
        keys. A reader comparing a distinct count against a record-counting parser sees a gap and
        has no way to tell a duplicate from a dropped entry — which is the reading that cost a peer
        a hand audit.
        """
        return len(self.entries) + sum(len(c.homes) - 1 for c in self.collisions)

    def gap_line(self) -> str | None:
        """Return the sentence naming the distinct-vs-declared gap, or None when there is none."""
        if not self.collisions:
            return None
        n = len(self.collisions)
        return (
            f"⚑ {n} key(s) declared in more than one bib — {self.declared} declaration(s) "
            f"read, {len(self.entries)} distinct key(s) kept (later wins): "
            + ", ".join(sorted(c.key for c in self.collisions))
        )


def compose(
    paths: Iterable[Path],
    read: Callable[[Path], dict[str, dict[str, str]]],
) -> Corpus:
    """Read every path into one entry map, recording keys that more than one bib declares.

    ⚑ EVERY PATH IS READ, WHICH IS THE WHOLE DEFECT THIS REPLACES. The origin's CLI collected every
    positional and then passed `paths[0]` to the parser, so a widened input produced a
    byte-identical count and the silent drop read as *"the finding survives"*.
    """
    entries: dict[str, dict[str, str]] = {}
    homes: dict[str, list[str]] = {}
    sources: list[str] = []

    for path in paths:
        sources.append(str(path))
        for key, fields in read(path).items():
            homes.setdefault(key, []).append(str(path))
            entries[key] = fields

    collisions = tuple(
        Collision(key=key, homes=tuple(where))
        for key, where in sorted(homes.items())
        if len(where) > 1
    )
    return Corpus(entries=entries, collisions=collisions, sources=tuple(sources))


def _edges_of(key: str, fields: dict[str, str]) -> list[tuple[str, str, str]]:
    """Return one entry's declared edges, one per comma-separated target."""
    return [
        (kind, key, target)
        for kind in EDGE_FIELDS
        for target in (t.strip() for t in fields.get(kind, "").split(","))
        if target
    ]


def edges(corpus: Corpus) -> tuple[tuple[str, str, str], ...]:
    """Return every `(kind, source, target)` edge declared across the composed corpus."""
    out: list[tuple[str, str, str]] = []
    for key, fields in sorted(corpus.entries.items()):
        out.extend(_edges_of(key, fields))
    return tuple(out)


# How much text either side of a mention is shown as context.
_CONTEXT = 40


def mentions(corpus: Corpus, key: str) -> tuple[tuple[str, str, str], ...]:
    """Return `(other, field, context)` where another entry's PROSE names `key`.

    ⚑⚑⚑ THIS REPORTS EVIDENCE, NEVER A VERDICT, AND THAT DISTINCTION IS THE WHOLE REASON IT
    EXISTS. Deciding that two claims are related — and which way the edge runs — was a judgement
    being made by reading them side by side, which is the reasoning-not-codified shape. An edge is
    WARRANTED, not chosen, when one entry's prose already names the other's subject: the relation
    is asserted in the document and merely not yet declared as a field. Naming the DIRECTION is a
    separate act, and the prose usually settles it.

    ⚑⚑ SUBSTRING, NOT WORD-BOUNDARY, AND THAT IS MEASURED RATHER THAN LAX. Warrant keys carry
    hyphens and digits (`R14-v2`, `T12-rederive`, `R2-SWEEP`), and a regex word boundary is a
    word-character transition — the same boundary defect `agda_lex.word` exists to fix, where 1269
    of 10831 names were invisible to it.

    ⚑ A LONGER KEY THAT CONTAINS THIS ONE IS A DIFFERENT SUBJECT. Without that test `R14-v1`'s
    prefix reads as a mention of `R14`, so a key would be reported as naming itself through every
    sibling that extends it.

    ⚑ AND A DECLARED EDGE IS NOT A MENTION. `EDGE_FIELDS` are skipped: those relations are already
    declared, and reporting them here would offer as evidence exactly what the author has done.
    """
    out: list[tuple[str, str, str]] = []
    longer = [k for k in corpus.entries if k != key and key in k]
    for other, fields in sorted(corpus.entries.items()):
        if other == key:
            continue
        for name, raw in sorted(fields.items()):
            if name.startswith("_") or name in EDGE_FIELDS:
                continue
            at = raw.find(key)
            if at < 0 or any(k in raw for k in longer):
                continue
            lo = max(0, at - _CONTEXT)
            hi = min(len(raw), at + len(key) + _CONTEXT)
            out.append(
                (other, name, ("…" if lo else "") + raw[lo:hi] + ("…" if hi < len(raw) else ""))
            )
    return tuple(out)


def orphans(corpus: Corpus) -> tuple[tuple[str, str, str], ...]:
    """Return the edges whose target is not an entry ANYWHERE in the composed corpus.

    ⚑⚑ THE POPULATION IS THE WHOLE CORPUS, AND THAT IS THE FIX. Resolving an edge against its own
    file alone is what turned a sibling premise into a dangling report — so the membership test
    reads `corpus.entries`, which spans every bib that was passed.
    """
    return tuple((kind, src, dst) for kind, src, dst in edges(corpus) if dst not in corpus.entries)
