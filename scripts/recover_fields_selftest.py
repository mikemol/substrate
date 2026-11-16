#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""The cases for `recover_fields` — the v2 generic-walk field recovery.

⚑ ITS OWN MODULE, THE WAY `ratchet_core_selftest` IS. A suite is a PAIR — the case bodies and
the dispatch that reaches them — and keeping the pair together in the module under test grew
that module past what one edit can leave clean. The cases are the larger half here: fourteen
records plus a twelve-node fixture against five short recovery functions.

⚑⚑ AND THE PRE-SPLIT CASES LIVED IN `sppf_db`, WHICH IS WHY THIS EXISTS AT ALL. The original
docstring recorded that as deliberate — the cases drove the names through `sppf_db`'s
re-import, exercising the real call path a consumer uses.

⚑⚑⚑ THAT RE-IMPORT ARM CANNOT LIVE HERE YET, AND THE REASON IS ⟡package-jea, MEASURED.
Importing `sppf_db` to check the delegating face made the type checker report **2,031
findings** against THIS file — `sppf_db` reaches `_content_addr`, `query_builders`,
`jea_agdai`, `store` and `schema` by BARE name under a `sys.path` prelude, so none of them
resolve as modules and every consequence lands on whoever imports it. The per-file gate is
transitive through imports, so a two-line arm inherits the monolith's whole debt.

⚑ SO THE COVERAGE GAP IS NAMED RATHER THAN QUIETLY DROPPED: nothing here proves `sppf_db` and
`sppf_decode` still resolve `recover_fields`/`leaf_value`/`FREE` through `sppf_recover`. That
is one arm, already written, blocked on packaging — not a property nobody thought to check.
`promote_frontier --closure` predicts exactly this class, and this is it landing.
"""

from __future__ import annotations

import sys

from scripts.decoded_node import NodeMap, Record, child
from scripts.recover_fields import FREE, recover_fields, recover_qname

# ⚑ THE MEASURED SHAPE, AS A FIXTURE. `QName [MName, Name]` with the module path two lists
# deep and the base name carrying a decimal-escaped `F₂` — sandbox, `Algebra/F2/F2.agdai`,
# 2026-08-07.
#
# ⚑⚑ KEY "6" IS A STRING DELIBERATELY. The producer writes JSON object keys as strings while
# `children` holds integers, and a reader that only tries one side misses every child
# silently — no error, just a `None` every caller reads as "absent" rather than "asked
# wrong". A fixture with uniform keys cannot catch that, which is the whole reason the
# int/str tolerance became its own module.
_NODES: NodeMap = {
    1: {"constructor": "#Int:7"},
    2: {"constructor": '#String:"F\\8322"'},
    3: {"constructor": "Id", "children": [2]},
    4: {"constructor": "[]", "children": [3]},
    5: {"constructor": "Name", "children": [4]},
    "6": {"constructor": '#String:"Substrate"'},
    7: {"constructor": "Id", "children": ["6"]},
    8: {"constructor": "[]", "children": [7]},
    9: {"constructor": "Name", "children": [8]},
    10: {"constructor": "[]", "children": [9]},
    11: {"constructor": "MName", "children": [10]},
    12: {"constructor": "QName", "children": [11, 5]},
}

_QN = "Substrate.F₂"

_Expected = tuple[str | None, int | None, str]

_CASES: list[tuple[str, Record, _Expected]] = [
    ("Var index from child[0]", {"constructor": "Var", "children": [1]}, (None, 7, "")),
    ("PVar index likewise", {"constructor": "PVar", "children": [1]}, (None, 7, "")),
    ("Var with no children", {"constructor": "Var", "children": []}, (None, None, "")),
    ("integer leaf is the lit", {"constructor": "#Integer:61"}, (None, None, "61")),
    ("string leaf is the lit", {"constructor": '#String:"V4"'}, (None, None, '"V4"')),
    ("Def qname from subtree", {"constructor": "Def", "children": [12]}, (_QN, None, "")),
    ("Con qname likewise", {"constructor": "Con", "children": [12]}, (_QN, None, "")),
    ("PDef — the pattern side", {"constructor": "PDef", "children": [12]}, (_QN, None, "")),
    ("a QName is its own answer", {"constructor": "QName", "children": [11, 5]}, (_QN, None, "")),
    ("a non-FREE ctor recovers nothing", {"constructor": "Lam", "children": [1]}, (None, None, "")),
    ("v1 fields win outright", {"qname": "A.B", "index": 3, "lit": "x"}, ("A.B", 3, "x")),
    # ⚑ THE MIXED RECORD PINS THE PRECEDENCE. Explicit qname and index but no lit — so v1
    # does NOT win outright and each field resolves on its own. A version check written as
    # one all-or-nothing branch passes every other case here and fails exactly this one.
    (
        "mixed record fills only the gap",
        {"qname": "A.B", "index": 3, "lit": "", "constructor": "Var", "children": [1]},
        ("A.B", 3, ""),
    ),
    ("FREE ctor with no children", {"constructor": "Def", "children": []}, (None, None, "")),
    (
        "FREE ctor whose child[0] is not a QName",
        {"constructor": "Def", "children": [1]},
        (None, None, ""),
    ),
]

# The referential set has eight members; see FREE's own note on how it drifted.
_FREE_SIZE = 8

# The case table plus the three invariant arms below.
_ARMS = 3


def _semantics(out: list[str]) -> int:
    """Check every record against its expected recovery. Returns the failure count."""
    bad = 0
    for label, rec, want in _CASES:
        got = recover_fields(dict(rec), _NODES)
        if got != want:
            out.append(f"selftest: {label}: expected {want!r}, got {got!r}")
            bad += 1
    return bad


def _invariants(out: list[str]) -> int:
    """Check the three properties the case table cannot state. Returns the failure count."""
    bad = 0

    # ⚑ THE ESCAPE ARM. `F₂` arrives as `"F\8322"`; left raw the qname is `Substrate.F\8322`,
    # which joins against nothing while still LOOKING like a name.
    if recover_qname(_NODES[12], _NODES) != _QN:
        out.append("selftest: the decimal codepoint escape was not undone")
        bad += 1

    # ⚑⚑ THE STRING-KEY ARM. Node "6" is reached only if the reader tries both spellings; if
    # it stops trying, every qname silently loses its module path.
    if child(_NODES, 6) is None:
        out.append("selftest: an int lookup missed a string-keyed node")
        bad += 1

    # ⚑ THE MEMBERSHIP ARM, and it exists because this set was once retyped from prose and
    # got five of eight members wrong in both directions. Each dropped member is a
    # constructor whose qname silently stops being recovered — the defect this module
    # repairs, reintroduced by the repair.
    if len(FREE) != _FREE_SIZE or "PProj" not in FREE:
        out.append(f"selftest: FREE is {sorted(FREE)}, not the eight-member set")
        bad += 1

    return bad


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = _semantics(out) + _invariants(out)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"recover_fields selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"recover_fields selftest: {len(_CASES) + _ARMS}/{len(_CASES) + _ARMS}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery):
# discovery keys on the literal `--selftest` appearing in the file, so a suite that runs
# unconditionally answers the runner's invocation correctly and is still never invoked.
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
