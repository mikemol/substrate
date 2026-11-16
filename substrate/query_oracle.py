# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The differential ORACLE for the W39c cleanroom: the origin builders, loaded for comparison.

⚑⚑ TEST INSTRUMENT ONLY — NO PRODUCTION MODULE IMPORTS THIS (operator, 2026-09-25: a suite may load
the origin as the differential oracle; production code never wraps it). The cleanroomed builders
are verified by CALLING each origin builder and the replica and requiring the rendered SQL to be
IDENTICAL, since that text is exactly what the committed query cache stores.

⚑ ONE COPY OF THE COMPARISON. The first suites each carried their own loader and loop; a fourth
copy is how a check drifts, so the suites share this one. It retires with the origin.
"""

from __future__ import annotations

import importlib.util
import sys
from typing import TYPE_CHECKING

from substrate import corpus

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

# The origin module, relative to the tree.
ORIGIN = ("jea", "metalanguage", "query_decl.py")

# How many rendered builders the negative control compares.
_CONTROL_PAIR = 2


def load() -> object | None:
    """Load the origin module by path, or None when it cannot be loaded."""
    path = corpus.ROOT.joinpath(*ORIGIN)
    spec = importlib.util.spec_from_file_location("_query_decl_origin", path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def origin_sql(origin: object, name: str) -> str:
    """Return the SQL text of the origin's builder `name`, or a marker when it is not callable."""
    builder: object = getattr(origin, name, None)
    if not callable(builder):
        return f"<origin has no builder {name}>"
    stmt: object = builder()
    return str(stmt)


def differential(replica: Mapping[str, Callable[[], object]]) -> list[tuple[str, bool]]:
    """Return `(label, passed)` per builder: its SQL equals the origin's, printing any diff.

    ⚑ A NEGATIVE CONTROL IS INCLUDED: the first two replica builders must render differently, or
    an equality could be passing on a rendering that ignores its input.
    """
    origin = load()
    if origin is None:
        return [("the origin loads", False)]
    out: list[tuple[str, bool]] = [("the origin loads", True)]
    rendered: list[str] = []
    for name, builder in replica.items():
        theirs = origin_sql(origin, name)
        mine = str(builder())
        rendered.append(mine)
        if theirs != mine:
            sys.stdout.write(f"  {name}:\n    origin:  {theirs}\n    replica: {mine}\n")
        out.append((f"{name} renders the origin's SQL", theirs == mine))
    distinct = len(rendered) < _CONTROL_PAIR or rendered[0] != rendered[1]
    out.append(("two different builders render differently (negative control)", distinct))
    return out


def report(label: str, cases: list[tuple[str, bool]]) -> int:
    """Print failing cases and the `label: ok/n` line; return an exit code."""
    ok = sum(1 for _, passed in cases if passed)
    for name, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {name}\n")
    sys.stdout.write(f"{label} selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1
