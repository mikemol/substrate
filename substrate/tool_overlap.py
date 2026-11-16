#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Where the toolkit's vocabulary collides or converges — enumerated, never scored.

⚑⚑⚑ THE COLLISION IS NOT THE FINDING; THE DIVERGENCE IS. Two tools spelling a mode the same way
is only dangerous when they answer DIFFERENT questions, because that is when the wrong tool
returns a PLAUSIBLE ANSWER instead of an error. So a shared name is reported with the shared
gloss vocabulary and the argument signatures beside it, and the verdict is about whether the two
agree — not about the coincidence.

⚑⚑ AND THE DECLARED LAYER IS NOT WHERE THE COLLISIONS ARE. One mode name is documented twice; the
UNDOCUMENTED dispatch layer collides repeatedly, and those are strictly worse — a flag two tools
both accept that no usage line mentions cannot be checked against anything before it is typed.
Reported with no divergence verdict, because an undocumented flag has no gloss to compare: the
absence IS the finding.

⚑⚑ ENUMERATED, NOT THRESHOLDED. A similarity cutoff is a number someone tuned; *"which content
word do two different tools' glosses both use"* is a membership test over the whole population,
and it is the query that puts `--prose`, `--source` and `--grep-content` in one family — the exact
cluster that makes an operator reach for the wrong tool. Every pair is examined and the
denominator is reported, so a reader sees what was CONSIDERED rather than what survived a cut.

⚑ THREE SIGNALS, DELIBERATELY DIFFERENT IN GRAIN. An identical argument SIGNATURE is the tightest
(same shape, so plausibly the same question); a shared argument KIND is coarser and matches how a
reader holding an artifact actually searches; a shared gloss WORD is coarsest and is what catches
a reinvention whose author chose different words for everything else.

⚑ EXTRACTED FROM `scratch/toolmodes.py` (⟡toolmodes-layers), 2,196 findings, refused whole by the
per-file gate. This module COMPUTES; rendering is the caller's.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import tool_similarity

if TYPE_CHECKING:
    from substrate.tool_census import Tool

# Shared content words needed to call two glosses aligned. ⚑ TWO, matching the sibling threshold:
# one shared word pairs almost anything.
ALIGNED = 2

# The verdicts a name collision can carry.
DIVERGENT = "DIVERGENT"
ALIGNED_WORD = "aligned"
WEAK = "weakly aligned"
DIFFERENT_ARGS = ", DIFFERENT ARGUMENTS"

# One declared mode, flattened: where it lives, what it is called, what it says, what it takes.
Declared = tuple[str, str, str, tuple[str, ...]]


@dataclass(frozen=True, slots=True)
class Collision:
    """One mode name declared by several tools, and whether they agree about it."""

    mode: str
    owners: tuple[tuple[str, tuple[str, ...], str], ...]
    shared: frozenset[str]
    union: frozenset[str]
    signatures: frozenset[tuple[str, ...]]

    @property
    def verdict(self) -> str:
        """Return whether the tools agree — the finding, of which the collision is only a hint."""
        base = (
            DIVERGENT if not self.shared else ALIGNED_WORD if len(self.shared) >= ALIGNED else WEAK
        )
        return base + (DIFFERENT_ARGS if len(self.signatures) > 1 else "")

    @property
    def divergent(self) -> bool:
        """Report whether these tools share a name while answering different questions."""
        return not self.shared


@dataclass(frozen=True, slots=True)
class Sibling:
    """Two modes on different tools that share gloss vocabulary — a wrong-tool candidate."""

    left: tuple[str, str]
    right: tuple[str, str]
    shared: frozenset[str]

    def rank(self) -> tuple[int, tuple[str, str], tuple[str, str]]:
        """Return the sort key: most shared words first, then stably by tool and mode.

        ⚑ A NAMED METHOD RATHER THAN A LAMBDA, because an untyped sort key makes every element it
        touches `Any` — the untyped-boundary defect arriving through a one-line convenience.
        """
        return (-len(self.shared), self.left, self.right)


def _stems(rows: tuple[Tool, ...]) -> tuple[str, ...]:
    """Return every tool's basename, so a gloss's own tool name is not a content word."""
    return tuple(tool.relpath.rsplit("/", 1)[-1] for tool in rows)


def _flat(rows: tuple[Tool, ...]) -> tuple[Declared, ...]:
    """Return `(relpath, mode, gloss, sig)` for every declared mode."""
    return tuple(
        (tool.relpath, mode, rec.gloss, rec.sig)
        for tool in rows
        for mode, rec in tool.modes.items()
    )


def collisions(rows: tuple[Tool, ...]) -> tuple[Collision, ...]:
    """Return every mode name several tools declare, with the divergence verdict.

    ⚑ THE SHARED VOCABULARY IS AN INTERSECTION OVER ALL OWNERS, not a pairwise one. Three tools
    where two agree and the third does not is DIVERGENT, because a reader reaching for the name
    can land on any of them.
    """
    stems = _stems(rows)
    by_mode: dict[str, list[tuple[str, tuple[str, ...], str]]] = {}
    for relpath, mode, gloss, sig in _flat(rows):
        by_mode.setdefault(mode, []).append((relpath, sig, gloss))

    out: list[Collision] = []
    for mode in sorted(by_mode):
        owners = tuple(sorted(by_mode[mode]))
        if len(owners) < ALIGNED:
            continue
        vocab = [tool_similarity.tokens(gloss, stems) for _rel, _sig, gloss in owners]
        shared = frozenset.intersection(*vocab) if all(vocab) else frozenset()
        out.append(
            Collision(
                mode=mode,
                owners=owners,
                shared=shared,
                union=frozenset().union(*vocab) if vocab else frozenset(),
                signatures=frozenset(sig for _rel, sig, _gloss in owners),
            )
        )
    return tuple(out)


def undocumented_collisions(rows: tuple[Tool, ...]) -> dict[str, tuple[str, ...]]:
    """Return flags SEVERAL tools accept that none declares — strictly worse than the above.

    ⚑⚑ NO VERDICT IS OFFERED, AND THAT IS THE POINT. An undocumented flag has no gloss to compare,
    so there is nothing to call aligned or divergent — and a reader cannot check the spelling
    against anything before typing it. The absence is the finding.
    """
    by_flag: dict[str, list[str]] = {}
    for tool in rows:
        for flag in tool.accepted - set(tool.modes):
            by_flag.setdefault(flag, []).append(tool.relpath)
    return {
        flag: tuple(sorted(owners)) for flag, owners in sorted(by_flag.items()) if len(owners) > 1
    }


def signature_families(
    rows: tuple[Tool, ...],
) -> dict[tuple[str, ...], tuple[tuple[str, str], ...]]:
    """Return cross-tool families sharing an identical argument shape — the tightest signal."""
    families = tool_similarity.signature_families(
        (relpath, mode, sig) for relpath, mode, _gloss, sig in _flat(rows)
    )
    return {
        sig: members
        for sig, members in families.items()
        if len({tool for tool, _mode in members}) > 1
    }


def kind_families(rows: tuple[Tool, ...]) -> dict[str, tuple[tuple[str, str], ...]]:
    """Return cross-tool families sharing an argument KIND — the grain a reader searches at."""
    families = tool_similarity.kind_families(
        (relpath, mode, sig) for relpath, mode, _gloss, sig in _flat(rows)
    )
    return {
        kind: members
        for kind, members in families.items()
        if len({tool for tool, _mode in members}) > 1
    }


def vocabulary_families(rows: tuple[Tool, ...]) -> dict[str, tuple[tuple[str, str], ...]]:
    """Return cross-tool families sharing one gloss word — the coarsest signal.

    ⚑ THE COARSEST IS THE ONE THAT CATCHES A REINVENTION. An author who chose different words for
    everything else still reaches for the same noun once, and a membership test over every word
    finds it where a whole-gloss similarity score would not.
    """
    stems = _stems(rows)
    vocab: dict[str, set[tuple[str, str]]] = {}
    for relpath, mode, gloss, _sig in _flat(rows):
        for word in tool_similarity.tokens(gloss, stems):
            vocab.setdefault(word, set()).add((relpath, mode))
    return {
        word: tuple(sorted(members))
        for word, members in sorted(vocab.items())
        if len({tool for tool, _mode in members}) > 1
    }


def siblings(rows: tuple[Tool, ...]) -> tuple[Sibling, ...]:
    """Return every cross-tool mode pair sharing two or more gloss words.

    ⚑ EVERY PAIR IS EXAMINED. The criterion is a membership test, so the population is the full
    cross product and the caller can report the denominator — which is what lets a reader see what
    was CONSIDERED rather than only what survived.
    """
    stems = _stems(rows)
    flat = [
        (relpath, mode, tool_similarity.tokens(gloss, stems))
        for relpath, mode, gloss, _sig in _flat(rows)
    ]

    out: list[Sibling] = []
    for i, (left_tool, left_mode, left_words) in enumerate(flat):
        for right_tool, right_mode, right_words in flat[i + 1 :]:
            if left_tool == right_tool:
                continue
            shared = left_words & right_words
            if len(shared) >= ALIGNED:
                out.append(
                    Sibling(
                        left=(left_tool, left_mode), right=(right_tool, right_mode), shared=shared
                    )
                )
    return tuple(sorted(out, key=Sibling.rank))


def cross_pairs(rows: tuple[Tool, ...]) -> int:
    """Return how many cross-tool mode pairs exist — the denominator `siblings` is drawn from."""
    flat = _flat(rows)
    return sum(1 for i, left in enumerate(flat) for right in flat[i + 1 :] if left[0] != right[0])
