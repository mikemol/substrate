# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.edge_weight` — what an import edge costs to cut.

⚑⚑⚑ THE CLASSIFICATION DECIDES WHERE A CUT LANDS, so calling a structural edge cheap is a
production break and calling a test-only edge expensive leaves a knot tied. Both directions are
pinned. The failure that matters more is the first: a cut aimed at a module-scope import that a
caller genuinely consumes breaks the importer, and the ordering that recommended it looks
exactly as confident as one that got it right.

⚑⚑ AN UNCLASSIFIABLE EDGE COSTS THE MOST, DELIBERATELY. A reader that could not place an edge
must not make it look cheap, or the cut lands on the one edge nobody understood — the same
direction of caution `editable` takes with UNKNOWN.

⚑ AND THE SELFTEST NAMES ARE A ROSTER, NOT A PATTERN. Admitting anything containing "test"
would sweep in a production function that merely tests a condition, and that edge would then
read as free to cut.
"""

from __future__ import annotations

import ast

from substrate import edge_weight

_MODULE_SCOPE = """
import peer
"""

_IN_SELFTEST = """
def selftest():
    import peer
    return peer.census()
"""

_IN_ORDINARY = """
def run():
    import peer
    return peer.census()
"""

_FROM_IMPORT = """
from peer import census
"""


def _costs(src: str) -> list[edge_weight.EdgeCost]:
    """Classify the `peer` edges in one source."""
    return edge_weight.classify(ast.parse(src), "a.py", {"peer"})


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the three kinds ─────────────────────────────────────────────────────
    check(
        "a module-scope import is structural",
        passed=_costs(_MODULE_SCOPE)[0].kind == edge_weight.STRUCTURAL,
    )
    # ⚑ THE CHEAP CASE THE COUNT-MINIMISING SOLVER CANNOT SEE.
    check(
        "an import inside a selftest is test-only",
        passed=_costs(_IN_SELFTEST)[0].kind == edge_weight.TEST_ONLY,
    )
    check(
        "an import inside an ordinary function is deferred",
        passed=_costs(_IN_ORDINARY)[0].kind == edge_weight.DEFERRED,
    )
    # ⚑ A `from` IMPORT IS STILL AN EDGE — missing it would under-report the graph.
    check(
        "a from-import at module scope is structural",
        passed=bool(_costs(_FROM_IMPORT))
        and _costs(_FROM_IMPORT)[0].kind == edge_weight.STRUCTURAL,
    )

    # ── the ordering, which is what a cut consumes ─────────────────────────
    cheap = _costs(_IN_SELFTEST)[0]
    dear = _costs(_MODULE_SCOPE)[0]
    check("test-only is cheaper than structural", passed=cheap.weight < dear.weight)
    check("and only test-only counts as cheap", passed=cheap.is_cheap and not dear.is_cheap)
    check(
        "deferred sits between them",
        passed=cheap.weight < _costs(_IN_ORDINARY)[0].weight < dear.weight,
    )

    # ⚑ AN UNKNOWN KIND MUST COST THE MOST, or a cut lands on an edge nobody classified.
    unknown = edge_weight.EdgeCost("a.py", "b", "something-new")
    check("an unrecognised kind costs as much as structural", passed=unknown.weight == dear.weight)
    check("and is not cheap", passed=not unknown.is_cheap)

    # ── the selftest roster is a roster ────────────────────────────────────
    # ⚑ A PRODUCTION FUNCTION THAT MERELY TESTS A CONDITION MUST NOT READ AS TEST-ONLY.
    tester = "def test_connection():\n    import peer\n    return peer.ping()\n"
    check(
        "a production function named for testing is not test-only",
        passed=_costs(tester)[0].kind != edge_weight.TEST_ONLY,
    )

    # ── the site is carried, so a reader can find the edge ─────────────────
    check(
        "a scoped edge names its enclosing function",
        passed=_costs(_IN_SELFTEST)[0].site == "selftest",
    )
    check("and a module-scope edge names none", passed=_costs(_MODULE_SCOPE)[0].site == "")

    # ── cheapest picks the lowest weight ───────────────────────────────────
    both = _costs(_IN_SELFTEST) + _costs(_MODULE_SCOPE)
    picked = edge_weight.cheapest(both)
    check("cheapest returns the test-only edge", passed=picked is not None and picked.is_cheap)
    check("and returns None on an empty set", passed=edge_weight.cheapest([]) is None)

    # ── the rendering warns about the solver's blind spot ──────────────────
    text = edge_weight.render(both)
    check("the rendering names the cheap kind", passed="test-only" in text)
    # ⚑ THE READING'S WHOLE POINT: a count-minimising solver cannot see this column.
    check(
        "and warns that a count-minimiser cannot see the column",
        passed="cannot see this column" in text,
    )

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
