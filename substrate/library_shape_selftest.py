#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.library_shape` — the reads, and the two false populations they fix.

⚑⚑⚑ THE SELF-REFERENCE CASE IS WHY THIS READS NAMES AND NOT TEXT. The original predicate scanned
source for the string `SIZES`, so a census SEARCHING for that name necessarily contained it and
flagged ITSELF — repaired by hand-listing six owners to exclude. That list is the allow-list
shape: it rots, and nothing says when. A name-load read cannot have the defect, so the list is
not needed rather than being maintained.

⚑⚑ AND THE OTHER HALF OF THE PAIR IS THE MISSED SPELLING. A first cut counted only ATTRIBUTE
reads (`I.SIZES` from another module), so a bare in-module `SIZES` was invisible and the claim
closed at 0 **on a defect that had just been written** — a witness passing because its query
cannot see the thing it measures. Both spellings need a case, or one of them silently returns to
being unread.

⚑ THE FIXTURES ARE SOURCE STRINGS, NOT THE LIVE TREE. A case reading `items.py` measures today's
dispatch module, so it would report the corpus rather than the reader — and would go green the
moment that file changed for unrelated reasons.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import library_shape

# A function that READS shared state, bare — the spelling the attribute-only query missed.
_BARE_READ = '''def a_witness() -> int:
    """No mention here."""
    return len(SIZES)
'''

# The same read spelled as an attribute off another module.
_ATTR_READ = '''def a_witness() -> int:
    """No mention here."""
    return len(I.SIZES)
'''

# ⚑ THE SELF-REFERENCE FIXTURE. It NAMES the watched globals in prose and in a string literal,
# and reads none of them — exactly the shape that made the original census flag itself.
_MENTIONS_ONLY = '''def a_census() -> int:
    """Count witnesses that read SIZES, WHY or PARTS.

    ⚑ A docstring naming PARTS is not a read of PARTS.
    """
    watched = ("SIZES", "WHY", "PARTS")
    return len(watched)
'''

# A witness that takes its inputs — parametric by signature.
_TAKES_ARGS = '''def a_witness(key: str) -> int:
    """Takes what it needs."""
    return len(key)
'''

# A zero-argument witness reaching for nothing — parametric because nothing reaches out.
_INLINE = '''def a_witness() -> int:
    """Data inline; nothing reaches out."""
    return 3
'''

_TWO_READS = 2


def _read(where: str, text: str) -> tuple[library_shape.Witness, ...]:
    """Write a fixture module and read its witnesses back."""
    path = Path(where) / "fixture.py"
    path.write_text(text, encoding="utf-8")
    return library_shape.witnesses(path)


def a_bare_global_read_is_seen(out: list[str]) -> int:
    """Check an in-module `SIZES` load is counted.

    ⚑⚑ THE MEASURED MISS. An attribute-only query could not see this, so the claim closed at 0
    on a defect that had just been written — a witness passing because its query cannot see the
    thing it measures.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _read(where, _BARE_READ)
    if not got or got[0].reads_state != ("SIZES",):
        out.append(f"selftest: a bare global read was not seen: {got!r}")
        return 1
    return 0


def an_attribute_read_is_seen(out: list[str]) -> int:
    """Check `I.SIZES` from another module is counted — the other spelling.

    ⚑ THE PAIR IS THE POINT. Either query alone leaves half the population unread, and which
    half depends on where the witness happens to live.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _read(where, _ATTR_READ)
    if not got or got[0].reads_state != ("SIZES",):
        out.append(f"selftest: an attribute read was not seen: {got!r}")
        return 1
    return 0


def a_mention_is_not_a_read(out: list[str]) -> int:
    """Check naming a watched global in prose or a string is NOT a read.

    ⚑⚑⚑ THE SELF-REFERENCE THE `owners` LIST WAS PATCHING. A census that searches for `SIZES`
    contains the word, and a text predicate therefore flags the census itself — which the
    original repaired by hand-excluding six names. Reading `ast.Name` loads makes the defect
    impossible rather than excluded, so this fixture mentions all three watched names, in a
    docstring AND in a string literal, and must read as clean.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _read(where, _MENTIONS_ONLY)
    if not got or got[0].reads_state != ():
        out.append(f"selftest: a mention was counted as a read: {got!r}")
        return 1
    return 0


def a_witness_taking_arguments_is_parametric(out: list[str]) -> int:
    """Check a witness with a signature is not reported as reaching."""
    with tempfile.TemporaryDirectory() as where:
        got = _read(where, _TAKES_ARGS)
    if not got or not got[0].parametric or not got[0].takes_args:
        out.append(f"selftest: an argument-taking witness read as non-parametric: {got!r}")
        return 1
    return 0


def a_zero_argument_witness_reaching_for_nothing_is_parametric(out: list[str]) -> int:
    """Check zero-argument is not itself the defect.

    ⚑ THE ORIGINAL SAID SO AND IT IS EASY TO LOSE: a witness with its data INLINE is parametric
    in the sense that matters, because nothing reaches out. Counting zero-arg as the defect would
    flag every honest inline witness and make the sub-item unclosable.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _read(where, _INLINE)
    if not got or not got[0].parametric:
        out.append(f"selftest: an inline witness read as non-parametric: {got!r}")
        return 1
    return 0


def a_zero_argument_witness_that_reaches_is_not_parametric(out: list[str]) -> int:
    """Check the reaching case IS caught — the POSITIVE CONTROL.

    ⚑ WITHOUT THIS, A PREDICATE CALLING EVERYTHING PARAMETRIC would pass both cases above. The
    trio says it discriminates on the reach rather than on the signature.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _read(where, _BARE_READ)
    if not got or got[0].parametric:
        out.append(f"selftest: a reaching zero-arg witness read as parametric: {got!r}")
        return 1
    return 0


def every_watched_name_is_reported(out: list[str]) -> int:
    """Check a witness reading two watched globals names both.

    ⚑ A COUNT WOULD LOSE WHICH. The repair differs per name — a figure passed in versus a route
    passed in — so a reader reporting only how many were read sends the caller back to the body.
    """
    text = '''def a_witness() -> int:
    """Two reads."""
    return len(SIZES) + len(PARTS)
'''
    with tempfile.TemporaryDirectory() as where:
        got = _read(where, text)
    if not got or len(got[0].reads_state) != _TWO_READS:
        out.append(f"selftest: a two-read witness reported {got!r}")
        return 1
    return 0


def the_library_and_dispatch_paths_are_named_once(out: list[str]) -> int:
    """Check both paths resolve under the corpus root.

    ⚑ ONE SPELLING, SO THE WITNESS AND ITS CASES CANNOT DISAGREE about where the library must
    live. A path typed at two call sites is the shape that lets a claim close against a file
    nobody else is looking at.
    """
    bad = 0
    if not str(library_shape.library()).endswith("catalog/library/concepts.py"):
        out.append(f"selftest: the library path is {library_shape.library()}")
        bad += 1
    if not str(library_shape.dispatch()).endswith("catalog/library/items.py"):
        out.append(f"selftest: the dispatch path is {library_shape.dispatch()}")
        bad += 1
    return bad


def an_unreadable_file_yields_nothing(out: list[str]) -> int:
    """Check a missing or unparseable file returns no witnesses rather than raising.

    ⚑ THE LIBRARY DOES NOT EXIST YET — that is the open state `T25-library` reports. A reader
    that raised on the absent path would make the witness unable to describe its own subject.
    """
    got = library_shape.witnesses(Path("/no/such/module.py"))
    if got != ():
        out.append(f"selftest: an absent file yielded {got!r}")
        return 1
    return 0


def an_empty_census_says_so(out: list[str]) -> int:
    """Check the render names its own emptiness rather than printing nothing.

    ⚑ SILENCE AND SUCCESS ARE THE SAME BYTES — the false-zero shape every census in this tree
    prints its denominator to avoid.
    """
    if "no witness" not in library_shape.render(()):
        out.append("selftest: an empty census does not name its emptiness")
        return 1
    return 0


def the_render_names_what_each_witness_reads(out: list[str]) -> int:
    """Check a reaching witness is listed with the names it reads, not just counted."""
    rows = (
        library_shape.Witness(name="a_witness", takes_args=False, reads_state=("PARTS", "SIZES")),
    )
    text = library_shape.render(rows)
    if "PARTS" not in text or "a_witness" not in text:
        out.append(f"selftest: the render omits the witness or its reads:\n{text}")
        return 1
    return 0


_ARMS = (
    a_bare_global_read_is_seen,
    an_attribute_read_is_seen,
    a_mention_is_not_a_read,
    a_witness_taking_arguments_is_parametric,
    a_zero_argument_witness_reaching_for_nothing_is_parametric,
    a_zero_argument_witness_that_reaches_is_not_parametric,
    every_watched_name_is_reported,
    the_library_and_dispatch_paths_are_named_once,
    an_unreadable_file_yields_nothing,
    an_empty_census_says_so,
    the_render_names_what_each_witness_reads,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 1 + 1 + 1 + 2 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"library-shape selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"library-shape selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
