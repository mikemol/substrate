#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Pin the dict locator, and DIFFERENCE it against the live ledger's text anchor.

⚑⚑⚑ THE LOAD-BEARING CASE IS THE DIFFERENTIAL, AND NOTHING ELSE SUBSTITUTES FOR IT. This
module exists to replace a source-text anchor in `.claude/agents/findings.py`. If the parse
lands on a different byte than that anchor does, every future witness is spliced somewhere
else — and the result still PARSES, so no syntax check and no round-trip would notice. The
case therefore computes BOTH offsets against the real file and asserts they are equal.

⚑⚑ AND A FIXTURE CANNOT ANSWER THAT QUESTION. A fixture proves the locator agrees with my
model of the ledger's shape; only the ledger proves it agrees with the ledger. The fixtures
below carry the cases the real file cannot exhibit — a missing roster, two rosters, a
non-dict binding, unparseable source — which are the refusal paths.

⚑ THE REFUSAL PATHS ARE ASSERTED TO REFUSE *AND* TO LEAVE THE SOURCE UNCHANGED. A locator
that returned a wrong offset would fail loudly here, but one that returned the input with a
reason a caller ignores would corrupt silently — so `splice` is asserted byte-identical to
its input on every failure.
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import dict_extent as de

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / ".claude" / "agents" / "findings.py"

# ⚑ THE ORIGIN'S ANCHOR, REPRODUCED EXACTLY. Built from parts rather than pasted so the
#   escape sequence is visible: a closing brace, two blank lines, then the next def.
ORIGIN_ANCHOR = "}\n\n\ndef _bib_keys():"

_SIMPLE = 'X = {\n    "a": 1,\n}\n\n\ndef after():\n    pass\n'
_TWO = 'X = {\n    "a": 1,\n}\nX = {\n    "b": 2,\n}\n'
_NOT_A_DICT = "X = [1, 2, 3]\n"
_IN_FUNC = 'def f():\n    X = {\n        "a": 1,\n    }\n    return X\n'
_BROKEN = "X = {\n    'a': 1,\n"
_AT_EOF = 'X = {\n    "a": 1,\n}\n'

Case = tuple[str, bool]


def _found_cases() -> list[Case]:
    """Return the cases where an extent SHOULD be established."""
    got = de.find(_SIMPLE, "X")
    at_eof = de.find(_AT_EOF, "X")
    return [
        ("a simple module-level dict is found", isinstance(got, de.Extent)),
        (
            "the open offset lands on a brace",
            isinstance(got, de.Extent) and _SIMPLE[got.open_at] == "{",
        ),
        (
            "the close offset lands on a brace",
            isinstance(got, de.Extent) and _SIMPLE[got.close_at] == "}",
        ),
        # ⚑ THE ANCHOR CANNOT DO THIS ONE. A roster that ends the file has no following
        #   def, so the origin's anchor matches nothing and refuses a legitimate write.
        ("a dict at END OF FILE is still found", isinstance(at_eof, de.Extent)),
        (
            "the end-of-file close offset lands on a brace",
            isinstance(at_eof, de.Extent) and _AT_EOF[at_eof.close_at] == "}",
        ),
    ]


def _refusal_cases() -> list[Case]:
    """Return the cases where an extent must be REFUSED with a reason."""
    two = de.find(_TWO, "X")
    missing = de.find(_SIMPLE, "NOPE")
    not_dict = de.find(_NOT_A_DICT, "X")
    in_func = de.find(_IN_FUNC, "X")
    broken = de.find(_BROKEN, "X")
    return [
        ("two module-level bindings are REFUSED", isinstance(two, de.NotFound)),
        (
            "the ambiguity refusal names both lines",
            isinstance(two, de.NotFound) and "1, 4" in two.reason,
        ),
        ("an absent name is REFUSED", isinstance(missing, de.NotFound)),
        ("a non-dict binding is REFUSED", isinstance(not_dict, de.NotFound)),
        # ⚑ A DICT INSIDE A FUNCTION IS A DIFFERENT OBJECT. Finding it would splice an
        #   entry into a local nobody reads, which parses and is wrong.
        ("a function-local dict is NOT found at module level", isinstance(in_func, de.NotFound)),
        ("unparseable source is REFUSED", isinstance(broken, de.NotFound)),
        (
            "the parse refusal says the source does not parse",
            isinstance(broken, de.NotFound) and "does not parse" in broken.reason,
        ),
    ]


def _splice_cases() -> list[Case]:
    """Return the cases pinning that a failed splice changes NOTHING."""
    ok, why = de.splice(_SIMPLE, "X", '    "b": 2,\n')
    bad, bad_why = de.splice(_TWO, "X", '    "c": 3,\n')
    missing, missing_why = de.splice(_NOT_A_DICT, "X", '    "c": 3,\n')
    return [
        ("a good splice reports no reason", why is None),
        ("a good splice inserts the entry", '"b": 2,' in ok),
        ("a good splice still parses", _parses(ok)),
        ("a good splice keeps the original entry", '"a": 1,' in ok),
        ("an ambiguous splice returns a reason", bad_why is not None),
        ("an ambiguous splice leaves the source BYTE-IDENTICAL", bad == _TWO),
        ("a missing-dict splice returns a reason", missing_why is not None),
        ("a missing-dict splice leaves the source BYTE-IDENTICAL", missing == _NOT_A_DICT),
    ]


def _parses(src: str) -> bool:
    """Whether `src` is valid Python."""
    import ast  # noqa: PLC0415

    try:
        ast.parse(src)
    except SyntaxError:
        return False
    return True


def _differential() -> list[Case]:
    """Assert the parse lands on the SAME byte the live ledger's text anchor does.

    ⚑ THIS IS THE CASE THE SWAP RESTS ON. A different offset relocates every future
    witness into a file that still parses, so nothing downstream would report it.
    """
    if not LEDGER.exists():
        return [("the origin ledger is present to difference against", False)]

    src = LEDGER.read_text(encoding="utf-8")
    got = de.find(src, "WITNESSES")
    hits = src.count(ORIGIN_ANCHOR)

    if not isinstance(got, de.Extent):
        return [
            ("the live WITNESSES roster is located by parse", False),
            (f"  (refused: {got.reason[:80]})", False),
        ]

    return [
        ("the live WITNESSES roster is located by parse", True),
        ("the origin's text anchor occurs exactly once", hits == 1),
        # The anchor's match begins AT the closing brace, so the origin inserts at that
        # index — which must be the byte the parse reports as the close.
        (
            "the parse and the text anchor agree on the insertion byte",
            hits == 1 and src.index(ORIGIN_ANCHOR) == got.close_at,
        ),
        ("the located byte is actually a closing brace", src[got.close_at] == "}"),
        # ⚑ A CONTROL: the roster must be large, or an equality above could hold on a
        #   trivially small dict and prove nothing about the real one.
        ("the located roster spans most of the file", got.close_at - got.open_at > len(src) // 2),
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = _found_cases() + _refusal_cases() + _splice_cases() + _differential()
    bad = [label for label, holds in cases if not holds]
    print(f"dict_extent: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
