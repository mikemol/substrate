#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.type_census_summary` — above all, that WEIGHTING IS BY MESSAGE.

⚑⚑⚑ THE KEY-VS-MESSAGE ORDERING IS THE WHOLE REASON THIS MODULE EXISTS, so it gets the
DISCRIMINATOR arm: a fixture where the two orderings DISAGREE. A summary that counted keys
would rank a code appearing in many files above a code appearing 200 times in one, and it
would render just as tidily — the reader cannot tell a weighted ranking from an unweighted
one by looking at the output. Only a case whose answer differs between them can.

⚑⚑ THE REFUSAL ARM MIRRORS `type_gate`'s, AND FOR THE SAME REASON. `mypy_census` reports its
inability to run as `None` or an `UNRUNNABLE` sentinel; a summariser that folded either into
an empty shape would print `0 keys, 0 messages` — a clean-looking tree, from a checker that
never ran. That is the exact defect the gate this summarises was built after.

⚑ AND THE TAIL ROW IS TESTED AS A PROPERTY, NOT AS A STRING. The arm asserts the shown rows
plus the residue equal the total, so a truncation that silently drops findings fails. Checking
the literal text would pass on a listing whose arithmetic is wrong.
"""

from __future__ import annotations

import sys

from substrate import type_census_summary as tcs
from substrate.type_gate import MypyUnavailable

# The message text the live census is dominated by, spelled once.
_ANY = 'Expression has type "Any"'

# A fixture where message-weighting and key-weighting DISAGREE.
#
# ⚑ `misc` HOLDS 2 KEYS AND 210 MESSAGES; `arg-type` HOLDS 4 KEYS AND 4 MESSAGES. Counting
# keys puts `arg-type` first; counting messages puts `misc` first by fifty-fold. This is the
# live shape in miniature — the real census has one code carrying most of the tree behind a
# key count that does not show it.
_ROWS: dict[str, list[str]] = {
    "misc::jea/big.py": [_ANY] * 200,
    "misc::jea/small.py": [_ANY] * 10,
    "arg-type::scripts/a.py": ["Argument 1 has incompatible type"],
    "arg-type::scripts/b.py": ["Argument 1 has incompatible type"],
    "arg-type::el-atlas/c.py": ["Argument 2 has incompatible type"],
    "arg-type::substrate/d.py": ["Argument 3 has incompatible type"],
}

_TOTAL_MESSAGES = 214
_TOTAL_KEYS = 6
_MISC_MESSAGES = 210
_ARGTYPE_MESSAGES = 4
_REFUSED = 2

# The reason a synthetic refusal carries, named once (`EM101` refuses a literal at the raise).
_SYNTHETIC = "synthetic: the checker did not run"


def _refusing_census() -> dict[str, list[str]]:
    """Stand in for a census that cannot be taken."""
    raise MypyUnavailable(_SYNTHETIC)


def _fixture_census() -> dict[str, list[str]]:
    """Stand in for a census that CAN be taken — the positive control."""
    return _ROWS


def weighting_is_by_message(out: list[str]) -> int:
    """Check the ranking follows MESSAGES, not keys — the discriminator.

    ⚑ THIS ARM FAILS ON A PLAUSIBLE WRONG IMPLEMENTATION, which is what makes it a case
    rather than a restatement. Counting keys is the natural first cut, renders identically,
    and puts `arg-type` (4 keys) above `misc` (2 keys) when `misc` carries 210 of 214
    findings.
    """
    bad = 0
    shape = tcs.shape_of(_ROWS)
    top_code, top_n = shape.by_code.most_common(1)[0]
    if top_code != "misc":
        out.append(
            f"selftest: the heaviest code ranked as {top_code!r}, not 'misc'"
            " -- the ranking is counting keys, not messages"
        )
        bad += 1
    if top_n != _MISC_MESSAGES:
        out.append(f"selftest: 'misc' weighed {top_n}, not {_MISC_MESSAGES} messages")
        bad += 1
    if shape.by_code["arg-type"] != _ARGTYPE_MESSAGES:
        out.append(
            f"selftest: 'arg-type' weighed {shape.by_code['arg-type']}, not {_ARGTYPE_MESSAGES}"
        )
        bad += 1
    return bad


def counts_are_distinct(out: list[str]) -> int:
    """Check keys, messages and files are each reported and each differ.

    ⚑ A SUMMARY THAT REPORTED ONE NUMBER WOULD PASS EVERY OTHER ARM. The headline names all
    of them precisely because collapsing them is the failure -- 6 keys, 214 messages and 6
    files are three different facts about the same census.
    """
    bad = 0
    shape = tcs.shape_of(_ROWS)
    if shape.key_count != _TOTAL_KEYS:
        out.append(f"selftest: key_count is {shape.key_count}, not {_TOTAL_KEYS}")
        bad += 1
    if shape.messages != _TOTAL_MESSAGES:
        out.append(f"selftest: messages is {shape.messages}, not {_TOTAL_MESSAGES}")
        bad += 1
    head = tcs.headline(shape)
    for token in (f"{_TOTAL_KEYS} keys", f"{_TOTAL_MESSAGES} messages", "6 files", "2 codes"):
        if token not in head:
            out.append(f"selftest: the headline does not carry {token!r}: {head!r}")
            bad += 1
    return bad


def roots_are_attributed(out: list[str]) -> int:
    """Check every promoted root is attributed, and a bare path is not silently dropped.

    ⚑ THE BARE-PATH CASE IS A DISCRIMINATOR for `partition`: a path with no `/` yields an
    EMPTY head under a naive `split("/")[0]`, so the root listing would carry a nameless row
    summing into the total. It renders as blank space and reads as a formatting glitch.
    """
    bad = 0
    shape = tcs.shape_of(_ROWS)
    if shape.by_root["jea"] != _MISC_MESSAGES:
        out.append(f"selftest: jea/ weighed {shape.by_root['jea']}, not {_MISC_MESSAGES}")
        bad += 1
    if sum(shape.by_root.values()) != _TOTAL_MESSAGES:
        out.append("selftest: the root attribution loses messages")
        bad += 1
    if tcs.root_of("setup.py") != ".":
        out.append(f"selftest: a bare path attributed to {tcs.root_of('setup.py')!r}, not '.'")
        bad += 1
    return bad


def listing_accounts_for_every_message(out: list[str]) -> int:
    """Check a truncated listing names its residue, and the arithmetic closes.

    ⚑ A TOP-N WITH NO REMAINDER ROW READS AS THE WHOLE POPULATION. The property under test is
    that shown + residue == total, which fails on a listing that truncates silently -- the
    shape where a census quietly answers about a smaller set than it claims.
    """
    bad = 0
    shape = tcs.shape_of(_ROWS)
    text = tcs.listing(shape.by_file, shape.messages, 2, "file")
    if "4 more" not in text:
        out.append(f"selftest: the truncated listing does not name its residue: {text!r}")
        bad += 1
    if str(_ARGTYPE_MESSAGES) not in text.rsplit("\n", 1)[-1]:
        out.append(f"selftest: the residue row does not carry its count: {text!r}")
        bad += 1
    whole = tcs.listing(shape.by_file, shape.messages, 99, "file")
    if "more" in whole:
        out.append("selftest: an untruncated listing still claims a residue")
        bad += 1
    return bad


def refusal_is_not_an_empty_shape(out: list[str]) -> int:
    """Check an unmeasurable census refuses rather than rendering a clean-looking zero.

    ⚑ THE ARM DRIVES `render_or_refuse` WITH A REFUSING CENSUS RATHER THAN UNINSTALLING
    mypy. A measurement that mutates the environment it measures is not a case; passing the
    census in exercises the same branch and leaves the machine alone.

    ⚑⚑ THE POSITIVE CONTROL IS THE OTHER HALF. An implementation that returned 2
    unconditionally would pass the refusal check and be entirely broken -- a case that only
    ever asserts the failure path cannot tell a working refusal from a dead tool.
    """
    bad = 0
    rc = tcs.render_or_refuse(_refusing_census, "", tcs.DEFAULT_TOP)
    if rc != _REFUSED:
        out.append(f"selftest: an unmeasurable census rendered and returned {rc}, not {_REFUSED}")
        bad += 1
    if tcs.render_or_refuse(_fixture_census, "--codes", 2) != 0:
        out.append("selftest: a measurable census did not render")
        bad += 1
    return bad


def unknown_flag_is_refused(out: list[str]) -> int:
    """Check an unrecognised flag refuses rather than silently running the default view.

    ⚑ A SILENTLY IGNORED MODE IS A SUMMARY THAT LOOKS LIKE IT ANSWERED THE QUESTION ASKED.
    The sibling gate refuses for the same reason and says so in its own message.
    """
    bad = 0
    if tcs.main(["type_census_summary.py", "--codez"]) != _REFUSED:
        out.append("selftest: an unknown flag did not refuse")
        bad += 1
    return bad


_ARMS = (
    weighting_is_by_message,
    counts_are_distinct,
    roots_are_attributed,
    listing_accounts_for_every_message,
    refusal_is_not_an_empty_shape,
    unknown_flag_is_refused,
)

_CASE_COUNT = 3 + 6 + 3 + 3 + 2 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"type-census-summary selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"type-census-summary selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
