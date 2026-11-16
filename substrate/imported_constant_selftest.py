#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Pin the cross-module constant resolver, against fixtures and against the live tree.

⚑⚑⚑ THE LIVE CASE IS THE ONE THE FINDING RESTS ON. gate-F90 claims the drain ranking's
opaque-target sites are one imported constant, and the claim is only worth anything if this
module actually resolves it: `wg_engine.LIBRARY` must come back as `library`, read from the
real `scripts/wg_engine.py` rather than a fixture of what I think it says.

⚑⚑ AND THE REFUSAL CASES CARRY EQUAL WEIGHT, BECAUSE THE FAILURE DIRECTION IS ASYMMETRIC.
The value this replaces is UNKNOWN — honest and useless. A resolver that guesses produces a
CONFIDENT WRONG DIRECTORY, which the ranking would then treat as fact. So every shape the
AST cannot settle is asserted to refuse: no binding, two bindings, a non-literal expression,
unparseable source.

⚑ IT PARSES AND NEVER IMPORTS, AND THE LIVE CASE EXISTS TO KEEP IT THAT WAY. `wg_engine`
mutates `sys.path` at import time — the behaviour being censused — so a reader that imported
it would perform the defect it measures. The live case reads the file as TEXT.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from substrate import imported_constant as ic

ROOT = Path(__file__).resolve().parent.parent

_JOINED = (
    "import os\n"
    "ROOT = os.path.dirname(__file__)\n"
    'LIBRARY = os.path.join(ROOT, "catalog", "library")\n'
)
_BARE = 'LIBRARY = "catalog/library"\n'
_TWICE = 'A = "one"\nA = "two"\n'
_COMPUTED = "import os\nA = os.environ['WHATEVER']\n"
_BROKEN = "A = (\n"

Case = tuple[str, bool]


def _resolved_cases() -> list[Case]:
    """Return the cases where a constant SHOULD resolve."""
    joined = ic.resolve(_JOINED, "LIBRARY")
    bare = ic.resolve(_BARE, "LIBRARY")
    return [
        ("a join over literals resolves", isinstance(joined, ic.Named)),
        (
            "the directory is the LAST segment",
            isinstance(joined, ic.Named) and joined.directory == "library",
        ),
        # ⚑ THE SEGMENTS ARE CARRIED so a caller can tell `catalog/library` from a bare
        #   `library` that happens to share a leaf name.
        (
            "the segments are carried, not just the leaf",
            isinstance(joined, ic.Named) and joined.segments == ("catalog", "library"),
        ),
        ("a bare string literal resolves", isinstance(bare, ic.Named)),
    ]


def _refusal_cases() -> list[Case]:
    """Return the cases where resolution must REFUSE rather than guess."""
    missing = ic.resolve(_BARE, "NOPE")
    twice = ic.resolve(_TWICE, "A")
    computed = ic.resolve(_COMPUTED, "A")
    broken = ic.resolve(_BROKEN, "A")
    return [
        ("an absent binding is REFUSED", isinstance(missing, ic.Unnamed)),
        ("two module-level bindings are REFUSED", isinstance(twice, ic.Unnamed)),
        (
            "the ambiguity refusal says a wrong attribution is worse",
            isinstance(twice, ic.Unnamed) and "worse than" in twice.reason,
        ),
        # ⚑ THE FALSE-ATTRIBUTION DIRECTION. A value built from something unread must not be
        #   named from whatever literals happen to be nearby.
        ("a computed value with no literal segments is REFUSED", isinstance(computed, ic.Unnamed)),
        ("unparseable source is REFUSED", isinstance(broken, ic.Unnamed)),
    ]


def _shape_cases() -> list[Case]:
    """Return the cases pinning which insert calls carry an attribute target."""
    attr = ast.parse("sys.path.insert(0, wg_engine.LIBRARY)").body[0]
    lit = ast.parse('sys.path.insert(0, "scratch")').body[0]
    if not isinstance(attr, ast.Expr) or not isinstance(lit, ast.Expr):
        return [("the fixtures parse as expressions", False)]
    if not isinstance(attr.value, ast.Call) or not isinstance(lit.value, ast.Call):
        return [("the fixtures parse as calls", False)]
    got = ic.attribute_target(attr.value)
    return [
        ("an attribute target is recognised", got is not None),
        ("it names the module and the constant", got == ("wg_engine", "LIBRARY")),
        # ⚑ A LITERAL TARGET IS NOT THIS MODULE'S BUSINESS — `target_of` already reads it,
        #   and claiming it here would put one question under two authorities.
        ("a literal target is NOT claimed", ic.attribute_target(lit.value) is None),
    ]


def _live_cases() -> list[Case]:
    """Resolve the real constant that gate-F90 rests on, against the real tree."""
    engine = ROOT / "scripts" / "wg_engine.py"
    if not engine.is_file():
        return [("scripts/wg_engine.py is present to resolve against", False)]
    got = ic.resolve_in(ROOT, "wg_engine", "LIBRARY")
    found = ic.resolve_in(ROOT, "wg_engine", "PROJECT")
    missing = ic.resolve_in(ROOT, "no_such_module_at_all", "X")
    return [
        # ⚑ NO `(…, True)` ROW HERE (gate-G21, gate-G22). The early return above already
        # reports an absent fixture, so a literal-True case in the success path asserts
        # nothing — it cannot fail, and it occupied a case slot while looking like a control.
        # Presence is a PRECONDITION of this arm, not one of its findings.
        # ⚑ THE CASE gate-F90 RESTS ON.
        ("the live wg_engine.LIBRARY resolves", isinstance(got, ic.Named)),
        (
            "it names the library directory",
            isinstance(got, ic.Named) and got.directory == "library",
        ),
        (
            "it carries the catalog parent",
            isinstance(got, ic.Named) and got.segments == ("catalog", "library"),
        ),
        # A sibling constant in the same module, so the resolution is not a one-off.
        (
            "the sibling PROJECT also resolves",
            isinstance(found, ic.Named) and found.directory == "worklist",
        ),
        (
            "PROJECT and LIBRARY are DIFFERENT directories",
            isinstance(got, ic.Named)
            and isinstance(found, ic.Named)
            and got.directory != found.directory,
        ),
        ("an absent module is REFUSED by name", isinstance(missing, ic.Unnamed)),
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = _resolved_cases() + _refusal_cases() + _shape_cases() + _live_cases()
    bad = [label for label, holds in cases if not holds]
    print(f"imported_constant: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
