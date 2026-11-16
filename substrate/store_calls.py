#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The store-opening call NAMES a file mentions, at any depth — a CALL census, not imports.

⚑⚑ THE SECOND, DECORRELATED SIGNAL. `import_edges` walks IMPORT EDGES; this walks CALL SITES.
They are wrong in OPPOSITE directions and that is the point — coverage is the UNION of blind
spots, so a reader needs both readings and needs to see where they disagree. Two instruments
that agree have told you about one blind spot, not none.

⚑ AT ANY DEPTH, DELIBERATELY, AND THAT IS THE OPPOSITE CHOICE FROM THE IMPORT WALK. There the
question is what executes ON IMPORT, so descending into a `def` would be a false positive. Here
the question is whether this file can open a store AT ALL, and a call inside a function is
exactly the case the import walk misses by design.

⚑⚑ WHY IMPORT CLOSURE ALONE CANNOT BE A GATE'S SIGNAL, MEASURED NOT ARGUED. `query_defs.
_cost_connect` holds an inlined `sandbox_connect(…) if … else connect(…)` and declares no
`--live` at all — a store-reacher whose tenant was UNSAYABLE. And `scratch/scope_store.py`
calls `store.sandbox_connect` from a FUNCTION BODY, so the import walk correctly excludes it
(a deferred import is a different edge) while the suite genuinely opens a store. Import-reach
is not wrong; it answers *what does importing this execute*, where the tenant question is
*does this open a connection*. One instrument, two questions, and the gap is a suite.

⚑ NAME-KEYED, SO IT OVER-REPORTS, AND IT SAYS SO. `connect` is a common verb — a socket, an
MCP client, a graph edge. This cannot resolve which `connect` is the store's without importing
the module, which is what a subprocess-per-suite design exists to avoid. The output is
CANDIDATES for a reader to adjudicate, never a verdict.

⚑⚑ `tenant` IS IN THE ROSTER, AND THAT IS LOAD-BEARING RATHER THAN INCIDENTAL. The hand
adjudications this lens exists beside ask exactly *"does the executed path reach `store.tenant`
or a live connect"* — a question this census can answer for the SAME file, which is why the two
lenses joined are a candidate replacement for adjudicating those rows by hand.

⚑⚑⚑ AND IT SPEAKS WHEN RUN, BECAUSE SILENCE-AND-EXIT-0 IS INDISTINGUISHABLE FROM "NO MATCHES".
MEASURED: `store_calls.py` and `store_calls.py <name>` both printed NOTHING and exited 0 while an
operator was looking for call sites, and the silence read as *your query matched nothing* — a
false zero in the CLI surface rather than in a census. The name made it worse: this is a
STORE-CONNECTION reader over a three-name roster, not a general call census, so the capability
the name suggests would return empty for most inputs even when working perfectly.

⚑⚑ THE REFUSAL EXITS 2 AND STATES WHAT THIS DOES *NOT* DO. Printing "modes" would be a fiction —
this module HAS no modes; it is a library whose one function takes a path. So the honest
bare-invocation answer is *"this is a library, here is its one entry point, and here is the
capability its name suggests but does not have"*. `substrate.suite_emit` refuses on the same
grounds, and this repo's own agda-codemod skill records the identical defect for four tools where
*"run the tool bare to read its modes"* fails silently on exactly the tools where it matters most.

⚑ AN OPERAND IS REFUSED RATHER THAN INTERPRETED, and that is the sharper half of the measured
defect. `store_calls.py <some-name>` looked like a query and answered like one; there is no
name-search here to route it to, so accepting it in any form would rebuild the false zero. A
missing capability is WORK, not a mode to fake.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

# ⚑ THE THREE NAMES THAT OPEN OR DEMAND A TENANT. `tenant` is the resolver that `sys.exit(2)`s
# on an unstated tenant, so reaching it is as consequential as reaching a connect.
CONNECT_CALLS = frozenset({"sandbox_connect", "connect", "tenant"})

# Parsed call names, keyed by path.
_CACHE: dict[str, frozenset[str]] = {}


def _called_name(node: ast.Call) -> str | None:
    """Return the bare name a call invokes, whether attribute or plain."""
    func = node.func
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return None


def connect_sites(path: str) -> frozenset[str]:
    """Return the store-opening call names this file mentions, at any depth."""
    if path in _CACHE:
        return _CACHE[path]
    try:
        tree = ast.parse(Path(path).read_text(encoding="utf-8", errors="replace"), filename=path)
    except (OSError, SyntaxError):
        _CACHE[path] = frozenset()
        return _CACHE[path]
    found = {
        name
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        for name in [_called_name(node)]
        if name in CONNECT_CALLS
    }
    _CACHE[path] = frozenset(found)
    return _CACHE[path]


def speak() -> str:
    """Return what this module is, what it answers, and the capability it does NOT have.

    ⚑ THE ROSTER IS READ FROM `CONNECT_CALLS` RATHER THAN RESTATED. A usage text that lists the
    three names in prose is a second spelling that drifts the day a fourth is added — the
    census-keyed-on-one-spelling defect in the help text of the tool that warns about it.
    """
    roster = ", ".join(sorted(CONNECT_CALLS))
    return (
        "store_calls is a LIBRARY — it reads which STORE-OPENING calls a file makes.\n"
        "\n"
        f"  connect_sites(path) -> the subset of {{{roster}}} this file calls, at any depth\n"
        "\n"
        "⚑ IT IS NOT A GENERAL CALL CENSUS. It matches only the roster above, so it cannot\n"
        "  answer 'where is <name> called'. Running it bare, or with a name, once printed\n"
        "  NOTHING and exited 0 — silence a reader could not distinguish from 'no matches'.\n"
        "  That is why this refuses instead.\n"
        "\n"
        "usage: store_calls.py --selftest\n"
    )


# ⚑ `--selftest` DELEGATES TO THE SIBLING SUITE (⟡selftest-discovery); ANY other invocation —
# bare, or with an operand that looks like a query — refuses with exit 2 rather than exiting 0
# in silence. Accepting a name would rebuild exactly the false zero this entry point retires.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        from substrate import store_calls_selftest

        sys.exit(store_calls_selftest.selftest())
    sys.stderr.write(speak())
    sys.exit(2)
