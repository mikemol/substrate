#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.tool_similarity` — a threshold, not a score.

⚑⚑⚑ THE STOPWORD SET WAS TRANSCRIBED PROSE AND I LOST FIVE WORDS IN THE REWRITE — `a`, `n`, `m`,
`we`, `it's`. The parity run caught it; **no case here would have**, because a case tests the
words its author thought of and the whole failure was not noticing an absence. That is the
strongest argument in this arc for comparing against the origin BEFORE writing cases, and it is
recorded here because the instrument dies when the origin is retired.

⚑⚑ THE FIVE WERE HARMLESS TODAY AND THE FIX STILL MATTERED. Four are shorter than the tokeniser's
three-character minimum, so they could never have been tokens; `it's` splits before it reaches the
set. A transcription that silently changes a MEASUREMENT PARAMETER is the defect whether or not it
currently bites, because the next reader tunes against the wrong baseline.

⚑ AND EDIT DISTANCE IS A THRESHOLD INPUT, NOT A SIMILARITY SCORE. Nothing ranks by it. An arm
below pins the two arms of the near-miss test separately, because the PREFIX arm is the one the
guard was actually built for and distance alone misses it by two.
"""

from __future__ import annotations

import sys

from substrate import tool_similarity

# The incident this guard exists for: a prefix of a declared flag, at distance 4.
_PREFIX_MISS = "--dry"

# A one-character typo — the class distance catches.
_TYPO = "--aply"

# A different word for the same intent — explicitly OUT of reach, and saying so is the point.
_SYNONYM = "--preview"

# Distance from `--dry` to `--dry-run`, which no safe threshold reaches.
_PREFIX_DISTANCE = 4

# The inflection pair the stemmer's measured motivating case turns on.
_SINGULAR, _PLURAL = "flag", "flags"

# A word ending in `ss`, which must not lose its tail.
_DOUBLE_S = "class"


def the_stemmer_pairs_its_motivating_case(out: list[str]) -> int:
    """Check `flag` and `flags` stem together — THE MEASURED CASE.

    ⚑⚑ WITHOUT STEMMING THE GLOSS ARM MISSES ITS OWN MOTIVATING CASE BY ONE WORD. `cli_flags` was
    a reinvention of `literal_flags`; their glosses share `tool` plus `flag`/`flags` — 2 tokens
    stemmed, 1 unstemmed, and the pairwise arm needs 2. A capability search that cannot pair the
    reinvention it was built for reports method rather than substrate.
    """
    if tool_similarity.stem(_SINGULAR) != tool_similarity.stem(_PLURAL):
        out.append(f"selftest: {_SINGULAR!r} and {_PLURAL!r} do not stem together")
        return 1
    return 0


def a_double_s_word_keeps_its_tail(out: list[str]) -> int:
    """Check `class` does not become `clas` — the over-stemming control.

    ⚑ OVER-STEMMING MERGES DISTINCT CAPABILITIES, which is the failure a capability index cannot
    afford: it would report two different tools as the same one.
    """
    if tool_similarity.stem(_DOUBLE_S) != _DOUBLE_S:
        out.append(f"selftest: {_DOUBLE_S!r} stemmed to {tool_similarity.stem(_DOUBLE_S)!r}")
        return 1
    return 0


def a_short_word_is_left_alone(out: list[str]) -> int:
    """Check the length guard protects short words from their own suffixes."""
    for word in ("is", "as", "us"):
        if tool_similarity.stem(word) != word:
            out.append(f"selftest: {word!r} stemmed to {tool_similarity.stem(word)!r}")
            return 1
    return 0


def stopwords_are_dropped_from_a_gloss(out: list[str]) -> int:
    """Check English connective tissue does not reach the token set."""
    got = tool_similarity.tokens("the census of every tool in the tree")
    if "the" in got or "of" in got:
        out.append(f"selftest: stopwords survived: {sorted(got)!r}")
        return 1
    if "censu" not in got and "census" not in got:
        out.append(f"selftest: the content word was dropped: {sorted(got)!r}")
        return 1
    return 0


def the_tools_own_name_is_dropped(out: list[str]) -> int:
    """Check a token every row shares discriminates nothing.

    ⚑ EVERY GLOSS MENTIONS ITS TOOL, so keeping the name would make every pair look related.
    """
    got = tool_similarity.tokens("mdstruct reads markdown tables", ("mdstruct.py",))
    if "mdstruct" in got:
        out.append(f"selftest: the tool's own name survived: {sorted(got)!r}")
        return 1
    return 0


def a_prefix_is_a_near_miss(out: list[str]) -> int:
    """Check `--dry` is caught — THE INCIDENT, and the arm distance cannot reach.

    ⚑⚑⚑ THREE TOOLS SPELLED NO-WRITE AS `--dry`, NONE VALIDATED ARGV, AND ALL THREE WROTE BY
    DEFAULT — so a typo'd `--dry-run` fell through to the writing branch. `--dry` sits at distance
    4 from `--dry-run`, past any threshold tight enough to avoid false positives, so the prefix
    arm is not redundancy: without it this guard misses the case it was built for.
    """
    if not tool_similarity.is_near_miss(_PREFIX_MISS, "--dry-run"):
        out.append(f"selftest: {_PREFIX_MISS!r} was not read as a near miss")
        return 1
    if tool_similarity.edit_distance(_PREFIX_MISS, "--dry-run") <= tool_similarity.NEAR:
        out.append("selftest: the fixture no longer needs the prefix arm — distance reaches it")
        return 1
    return 0


def a_typo_is_a_near_miss(out: list[str]) -> int:
    """Check a one-character slip is caught by distance."""
    if not tool_similarity.is_near_miss(_TYPO, "--apply"):
        out.append(f"selftest: {_TYPO!r} was not read as a near miss")
        return 1
    return 0


def a_synonym_is_not_a_near_miss(out: list[str]) -> int:
    """Check a different word for the same intent is OUT of reach — THE STATED BOUND.

    ⚑⚑ THIS GUARD CLOSES THE TYPO CLASS, NOT THE SYNONYM CLASS, and saying so is the difference
    between a guard and a claim of coverage. A tool spelling no-write as `--preview` is
    unreachable from here and only an undeclared-recurrence report can surface it.
    """
    if any(tool_similarity.is_near_miss(_SYNONYM, pair) for pair in tool_similarity.PAIR_FLAGS):
        out.append(f"selftest: {_SYNONYM!r} was read as a near miss — the bound is overstated")
        return 1
    return 0


def a_declared_pair_flag_is_not_its_own_miss(out: list[str]) -> int:
    """Check the correct spelling is never reported."""
    got = tool_similarity.near_misses(tool_similarity.PAIR_FLAGS)
    if got:
        out.append(f"selftest: a declared flag was reported as a near miss: {got!r}")
        return 1
    return 0


def a_fixture_flag_is_excluded(out: list[str]) -> int:
    """Check a caller-supplied fixture set removes a spelling — THE UNPAYABLE-ROW GUARD.

    ⚑⚑ THE FIRST LIVE RUN BANKED TWO FIXTURE FLAGS: a deliberate typo driving a refusal case and a
    toy flag from a branch-bounds fixture. Neither is a spelling any caller can type, and banking
    them puts a permanent, unpayable row in a paydown-only baseline.
    """
    if tool_similarity.near_misses((_TYPO,), (_TYPO,)):
        out.append("selftest: a declared fixture flag was still reported")
        return 1
    if not tool_similarity.near_misses((_TYPO,)):
        out.append("selftest: the flag is not reported even without the exclusion")
        return 1
    return 0


def the_default_pair_matches_the_declared_contracts(out: list[str]) -> int:
    """Check this layer's default pair equals what the records declare — ⟡pair-flags-derived.

    ⚑⚑ THREE COPIES OF TWO STRINGS EXISTED, and the origin's own comment forbids the copy
    directly above the line that makes one. This module keeps a DEFAULT because it sits below the
    convention records and must not import upward — so the default and the derivation must be
    pinned against each other, or the copy rots exactly as the comment warns.

    ⚑ THE IMPORT IS LOCAL BECAUSE THE DEPENDENCY IS THE CASE'S, NOT THE MODULE'S. Importing the
    audit layer at module scope would create the upward edge the argument exists to avoid.
    """
    from substrate import tool_convention_audit  # noqa: PLC0415 — see the docstring

    derived = tool_convention_audit.pair_flags()
    if set(derived) != set(tool_similarity.PAIR_FLAGS):
        out.append(
            f"selftest: the default pair {list(tool_similarity.PAIR_FLAGS)!r} "
            f"has drifted from the declared {list(derived)!r}"
        )
        return 1
    return 0


def a_caller_may_supply_the_pair(out: list[str]) -> int:
    """Check the target set is overridable, so a renamed convention is still measured."""
    got = tool_similarity.near_misses(("--wrte",), against=("--write",))
    if not got:
        out.append("selftest: a caller-supplied pair was not used")
        return 1
    return 0


def modes_group_by_argument_shape(out: list[str]) -> int:
    """Check two modes taking the same shape are one family.

    ⚑ THE SHAPE IS THE QUESTION, NOT THE NAME — which is what makes this a wrong-tool predictor
    rather than a synonym list.
    """
    got = tool_similarity.signature_families(
        (("a.py", "--x", ("<name>",)), ("b.py", "--y", ("<name>",)), ("c.py", "--z", ("<file>",)))
    )
    if len(got.get(("<name>",), ())) != len(("a", "b")):
        out.append(f"selftest: the signature families read as {got!r}")
        return 1
    return 0


def modes_group_by_placeholder_kind(out: list[str]) -> int:
    """Check the coarser grouping collects every mode taking a kind."""
    got = tool_similarity.kind_families(
        (("a.py", "--x", ("<file>", "<name>")), ("b.py", "--y", ("<file>",)))
    )
    if len(got.get("<file>", ())) != len(("a", "b")):
        out.append(f"selftest: the kind families read as {got!r}")
        return 1
    return 0


_ARMS = (
    the_stemmer_pairs_its_motivating_case,
    a_double_s_word_keeps_its_tail,
    a_short_word_is_left_alone,
    stopwords_are_dropped_from_a_gloss,
    the_tools_own_name_is_dropped,
    a_prefix_is_a_near_miss,
    a_typo_is_a_near_miss,
    a_synonym_is_not_a_near_miss,
    a_declared_pair_flag_is_not_its_own_miss,
    a_fixture_flag_is_excluded,
    the_default_pair_matches_the_declared_contracts,
    a_caller_may_supply_the_pair,
    modes_group_by_argument_shape,
    modes_group_by_placeholder_kind,
)

_CASE_COUNT = 1 + 1 + 3 + 2 + 1 + 2 + 1 + 1 + 1 + 2 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"tool-similarity selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"tool-similarity selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
