#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Why someone reaches for the wrong tool — gloss tokens, argument shapes, near-miss spellings.

⚑⚑⚑ EDIT DISTANCE HERE IS A THRESHOLD INPUT, NOT A SIMILARITY SCORE, and the difference is the
whole design. A score invites ranking and a cutoff chosen to make a list look right; a threshold
asks one yes/no question — *is this spelling within reach of a declared flag* — and the answer is
the same next week. The origin says so in six words on the function itself, which is exactly the
kind of distinction a transcription drops.

⚑⚑ STOPWORDS ARE A MEASUREMENT PARAMETER, NOT A VOCABULARY. They exist so gloss similarity
reflects the CAPABILITY rather than English connective tissue, and they are domain-free on
purpose: a repo-specific word list here would rot the way a hardcoded suffix roster did.

⚑⚑ AND THE STEMMER IS DELIBERATELY CRUDE, WITH A MEASURED MOTIVATING CASE. `cli_flags` was
written as a reinvention of `literal_flags`; their gloss vocabularies share `tool` plus
`flag`/`flags` — **2 shared tokens under stemming and 1 without**, which fails the `>= 2`
threshold the pairwise arm uses. A capability search that cannot pair the reinvention it was
built for is reporting method rather than substrate. Plural `-s`/`-es` and `-ing`/`-ed` are the
inflections a one-line gloss actually varies on; over-stemming would merge distinct capabilities,
so the rules stay conservative and short words are left alone.

⚑⚑⚑ THE NEAR-MISS GUARD REPLACED A FROZEN TABLE, AND THAT IS THE POINT. Three tools spelled
no-write as `--dry`, none validated argv, and all three WROTE by default — so a typo'd
`--dry-run` fell through to the writing branch. The first fix was a table of seven spellings
someone had already met, which is a frozen ALLOW-list wearing a DENY-list's clothes: tool #4
spelling it `--dryish` is caught by NOTHING. The predicate is distance-to-a-declared-pair-flag
over the LIVE census, so a spelling nobody has met yet is caught the day it lands.

⚑ AND A PROPER PREFIX IS A NEAR MISS BY CONSTRUCTION, WHICH DISTANCE ALONE MISSES. `--dry` to
`--dry-run` is distance 4 — past any threshold tight enough to avoid false positives — yet it is
the exact incident the guard exists for: the author typed the beginning of the right word and
stopped.

⚑ WHAT THIS CANNOT DECIDE, and it is a real bound: a tool spelling no-write as `--report`,
`--check` or `--preview` is UNREACHABLE from here. Those are not near misses of anything, they
are different words for the same intent, and only an undeclared-recurrence report can surface
them. This closes the TYPO class, not the SYNONYM class, and saying so is the difference between
a guard and a claim of coverage.

⚑ EXTRACTED FROM `scratch/toolmodes.py` (⟡toolmodes-layers), 2,196 findings, refused whole by the
per-file gate. ⚑⚑ `_selftest_only` DID NOT COME WITH IT: it reaches `_pycodemod_query` through a
`sys.path` insert, which is ruled out, and the capability it needs (a literal's ENCLOSING DEF) is
not on `pycodemod`'s public surface. That is a seam to build, not to smuggle — so `near_misses`
takes the fixture set as an ARGUMENT and the caller supplies it. → ⟡fixture-site-seam
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

# A content word: three or more characters, so `a`/`of` never reach the stemmer.
WORD = re.compile(r"[A-Za-z][A-Za-z0-9_-]{2,}")

# ⚑ A MEASUREMENT PARAMETER, NOT A VOCABULARY. Domain-free on purpose — a repo-specific list here
# would rot the way a hardcoded roster does, and these exist only so similarity reflects the
# capability rather than English connective tissue.
STOP = frozenset(
    {
        "the",
        "and",
        "or",
        "of",
        "to",
        "in",
        "for",
        "is",
        "it",
        "its",
        "that",
        "this",
        "what",
        "which",
        "who",
        "whom",
        "whose",
        "does",
        "do",
        "not",
        "are",
        "was",
        "were",
        "will",
        "would",
        "can",
        "could",
        "should",
        "may",
        "might",
        "must",
        "shall",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "an",
        "as",
        "at",
        "by",
        "on",
        "from",
        "into",
        "over",
        "under",
        "with",
        "without",
        "than",
        "then",
        "when",
        "where",
        "why",
        "how",
        "each",
        "every",
        "any",
        "some",
        "all",
        "both",
        "few",
        "more",
        "most",
        "other",
        "such",
        "only",
        "own",
        "same",
        "so",
        "too",
        "very",
        "just",
        "also",
        "but",
        "if",
        "else",
        "while",
        "about",
        "against",
        "between",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "out",
        "off",
        "again",
        "further",
        "once",
        "here",
        "there",
        "you",
        "your",
        "they",
        "them",
        "their",
        "we",
        "our",
        "us",
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
        "ten",
        "n",
        "m",
        "per",
        "it's",
        "a",
    }
)

# ⚑⚑ A DEFAULT, NOT THE AUTHORITY — the records are, and `tool_convention_audit.pair_flags()`
# derives the pair from them. This layer sits BELOW the convention records and must not import
# upward, so `near_misses` takes the pair as an argument and a caller that has the records passes
# it. Three copies of these two strings existed before that argument; the origin's own comment
# forbids the copy directly above the line that makes one. → ⟡pair-flags-derived
PAIR_FLAGS = ("--apply", "--dry-run")

# ⚑ THE THRESHOLD, AND IT IS TIGHT ON PURPOSE. Two edits catches a typo; three starts catching
# unrelated short flags, and a guard that cries wolf is one people learn to bank rather than fix.
NEAR = 2

# Stemming rules: (suffix, characters to drop). Conservative — the inflections a one-line gloss
# actually varies on, and nothing more.
SUFFIXES = (("ies", 3), ("es", 2), ("s", 1), ("ing", 3), ("ed", 2))

# A word must exceed its suffix by this much before the suffix is stripped, so short words survive.
KEEP = 2


def stem(word: str) -> str:
    """Return a crude English stem — enough to make `flags` and `flag` one token.

    ⚑ DELIBERATELY NOT A REAL STEMMER: no Porter, no dependency. Over-stemming merges distinct
    capabilities, which is the failure a capability index cannot afford — it would report two
    different tools as the same one.
    """
    for suffix, drop in SUFFIXES:
        if len(word) > len(suffix) + KEEP and word.endswith(suffix):
            if suffix == "ies":
                return word[:-3] + "y"
            if suffix == "s" and word.endswith("ss"):
                return word
            return word[:-drop]
    return word


def tokens(gloss: str, stems: Iterable[str] = ()) -> frozenset[str]:
    """Return the content words of a gloss — the capability, minus English and tool names.

    ⚑ THE TOOL'S OWN NAME IS DROPPED, because every gloss mentions it and a token every row
    shares discriminates nothing.
    """
    drop = {name.replace(".py", "").lower() for name in stems}
    return frozenset(
        stem(word)
        for word in (found.group(0).lower() for found in WORD.finditer(gloss))
        if word not in STOP and word not in drop and not word.startswith("--")
    )


def edit_distance(left: str, right: str) -> int:
    """Return the Levenshtein distance between two short strings.

    ⚑ NOT A SIMILARITY SCORE — A THRESHOLD INPUT. Nothing ranks by this; one comparison asks
    whether a spelling is within reach of a declared flag, and that answer does not drift.
    """
    if left == right:
        return 0
    prev = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        cur = [i]
        for j, b in enumerate(right, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a != b)))
        prev = cur
    return prev[-1]


def is_near_miss(flag: str, pair: str) -> bool:
    """Report whether `flag` is a mis-spelling of the declared `pair` flag.

    ⚑ TWO ARMS, AND THE PREFIX ONE IS THE INCIDENT. A proper prefix of a declared flag is a near
    miss BY CONSTRUCTION — the author typed the beginning of the right word and stopped — and it
    sits at distance 4, past any threshold tight enough to avoid false positives.
    """
    return pair.startswith(flag) or edit_distance(flag, pair) <= NEAR


def near_misses(
    flags: Iterable[str], fixtures: Iterable[str] = (), against: tuple[str, ...] = PAIR_FLAGS
) -> tuple[tuple[str, str], ...]:
    """Return `((spelling, the pair flag it misses), …)` for one tool's dispatched flags.

    ⚑⚑ THE TARGET PAIR IS AN ARGUMENT SO IT CAN BE DERIVED RATHER THAN RETYPED
    (⟡pair-flags-derived). A spelling is a near miss BECAUSE a declared required-pair flag is what
    the author meant, so the guard's targets must be whatever the CONTRACTS currently declare —
    `tool_convention_audit.pair_flags()` reads them out of the records. The module constant
    remains as the default because this layer sits BELOW the convention records and must not
    import upward; the caller that has them passes them.

    ⚑ THE ORIGIN'S OWN COMMENT ASKED FOR THIS AND THE LINE BELOW IT RETYPED THE PAIR ANYWAY —
    *"read from CONVENTIONS, never retyped; hardcoding the two words here would put the contract
    in two places"*. There were three copies before this argument existed.

    ⚑⚑ THE FIXTURE SET IS AN ARGUMENT FOR A DIFFERENT REASON — a SEAM rather than a preference.
    Deciding it needs a literal's ENCLOSING DEF, which lives in a private `pycodemod` helper
    reachable only through a `sys.path` insert. The caller supplies what it can prove; passing
    nothing over-reports, which is conservative ONLY because the consuming ratchet refuses on a
    new key rather than banking it.

    ⚑ A FIXTURE FLAG IS NOT AN INTERFACE, AND THE FIRST LIVE RUN BANKED TWO. A deliberate typo
    driving a refusal case and a pair of toy flags in a branch-bounds fixture — neither is a
    spelling any caller can type, and banking them puts a permanent, unpayable row in a
    paydown-only baseline.
    """
    excluded = set(fixtures)
    out: list[tuple[str, str]] = []
    for flag in sorted(set(flags)):
        if flag in against or not flag.startswith("--") or flag in excluded:
            continue
        match = next((one for one in against if is_near_miss(flag, one)), None)
        if match is not None:
            out.append((flag, match))
    return tuple(out)


def signature_families(
    signatures: Iterable[tuple[str, str, tuple[str, ...]]],
) -> dict[tuple[str, ...], tuple[tuple[str, str], ...]]:
    """Return `{signature: ((tool, mode), …)}` — same argument shape, any tool.

    ⚑ THE SHAPE IS THE QUESTION, NOT THE NAME. Two modes taking `<name> [paths]` answer
    structurally similar questions however differently they are spelled, which is what makes this
    a wrong-tool predictor rather than a synonym list.
    """
    out: dict[tuple[str, ...], list[tuple[str, str]]] = {}
    for tool, mode, sig in signatures:
        if sig:
            out.setdefault(sig, []).append((tool, mode))
    return {sig: tuple(members) for sig, members in out.items()}


def kind_families(
    signatures: Iterable[tuple[str, str, tuple[str, ...]]],
) -> dict[str, tuple[tuple[str, str], ...]]:
    """Return `{placeholder kind: ((tool, mode), …)}` — every mode taking a `<kind>`.

    ⚑ COARSER THAN THE FULL SIGNATURE, DELIBERATELY. `<file>` groups every mode that answers a
    question about a file regardless of what else it takes, which is the granularity a reader
    holding an artifact actually searches at.
    """
    out: dict[str, list[tuple[str, str]]] = {}
    for tool, mode, sig in signatures:
        for kind in sig:
            out.setdefault(kind, []).append((tool, mode))
    return {kind: tuple(members) for kind, members in out.items()}
