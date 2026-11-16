#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.import_reach` — and the parity check that expires with the origin.

⚑⚑⚑ THE PARITY ARM IS THE ITEM, AND ITS WINDOW IS CLOSING. `store_reach` still exists inside
`scripts/run_selftests.py`, which is frozen (1,832 findings; every edit refused, including a
deletion) and can only be retired WHOLE. While both are on disk, the extracted walk can be
compared against the one it replaces; after the retirement that instrument is gone and only these
cases remain. A rewritten reader that DISAGREES with the original is invisible to a suite written
against the rewrite — cases pin whatever the rewrite happens to do.

⚑⚑ THE ARMS ASSERT WHAT THE WALK MUST NOT COLLAPSE, because every one of those distinctions was a
measured defect before it was a case:

    module-level vs function-local     a first cut walked every `Import` node and reported 54 of
                                       99 suites as store-reaching, through lazy imports that
                                       importing never executes
    a route, not a boolean             a bare True cannot be acted on — the fix differs by WHICH
                                       seed and by what route
    deferred hops MARKED, not merged   `through_cuts=True` answers a different question, and
                                       collapsing the two answers the import GRAPH where the
                                       question was about what RUNS
    an unparseable file is EMPTY       never an exception: a walk that raises on one bad file
                                       reports nothing about the other 262

⚑ AND THE FIXTURES ARE WRITTEN TO THE SHAPES REAL MODULES HAVE, not the shapes the walk finds
convenient — a `TYPE_CHECKING` block, a conditional import at module scope, an import inside a
`try`. A suite whose fixtures all have the author's imagined shape is the weaker suite
(⟡per-binding-is-not-per-shape), which cost thirteen files earlier in this same session.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import import_reach

# A module whose store import is at module scope — the walk must SEE this.
_DIRECT = """import store

VALUE = 1
"""

# A module whose store import is inside a function — the walk must NOT see it by default.
_DEFERRED = '''def connect():
    """Open a connection."""
    import store
    return store
'''

# A module whose import sits inside a `try` at module scope — it still executes on import.
_IN_TRY = """try:
    import store
except ImportError:
    store = None
"""

# A module whose import sits under an `if` at module scope — likewise.
_IN_IF = """import sys

if sys.version_info >= (3, 11):
    import store
"""

# A module whose only store reference is under `TYPE_CHECKING` — a module-level import.
_IN_TYPE_CHECKING = """from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import store
"""

# A module importing something that itself imports a store — the transitive case.
_INDIRECT = "import middle\n"
_MIDDLE = "import store\n"

# A file that does not parse. ⚑ The walk must report EMPTY, never raise.
_BROKEN = "def (:\n"


def _written(directory: Path, name: str, source: str) -> Path:
    """Write one fixture module and return its path."""
    path = directory / f"{name}.py"
    path.write_text(source, encoding="utf-8")
    return path


def a_module_level_import_is_seen(out: list[str]) -> int:
    """Check an import at module scope is found."""
    with tempfile.TemporaryDirectory() as raw:
        path = _written(Path(raw), "direct", _DIRECT)
        if "store" not in import_reach.local_imports(path):
            out.append(
                f"selftest: module-level import missed: {sorted(import_reach.local_imports(path))}"
            )
            return 1
    return 0


def a_function_local_import_is_not_seen(out: list[str]) -> int:
    """Check a deferred import is excluded — THE 54-OF-99 ARM.

    ⚑⚑ A FIRST CUT WALKED EVERY `Import` NODE and reported 54 of 99 suites as store-reaching,
    through lazy, exception-swallowed imports that importing never executes. This is the
    narrowing that fixed it, and it is the one an `ast.walk` would silently undo.
    """
    with tempfile.TemporaryDirectory() as raw:
        path = _written(Path(raw), "deferred", _DEFERRED)
        if "store" in import_reach.local_imports(path):
            out.append("selftest: a function-local import was read as module-level")
            return 1
    return 0


def an_import_inside_a_try_is_seen(out: list[str]) -> int:
    """Check a `try` body at module scope is descended into — it executes on import."""
    with tempfile.TemporaryDirectory() as raw:
        path = _written(Path(raw), "in_try", _IN_TRY)
        if "store" not in import_reach.local_imports(path):
            out.append("selftest: an import inside a module-scope `try` was missed")
            return 1
    return 0


def an_import_inside_an_if_is_seen(out: list[str]) -> int:
    """Check an `if` body at module scope is descended into."""
    with tempfile.TemporaryDirectory() as raw:
        path = _written(Path(raw), "in_if", _IN_IF)
        if "store" not in import_reach.local_imports(path):
            out.append("selftest: an import inside a module-scope `if` was missed")
            return 1
    return 0


def a_type_checking_import_is_seen(out: list[str]) -> int:
    """Check a `TYPE_CHECKING` block is descended into — the shape real modules have.

    ⚑ IT IS AN `if` AT MODULE SCOPE, so the walk must reach it. A reader who special-cased
    `TYPE_CHECKING` would answer a different question than "what does importing execute".
    """
    with tempfile.TemporaryDirectory() as raw:
        path = _written(Path(raw), "in_tc", _IN_TYPE_CHECKING)
        if "store" not in import_reach.local_imports(path):
            out.append("selftest: an import inside a TYPE_CHECKING block was missed")
            return 1
    return 0


def a_deferred_seed_is_reported_separately(out: list[str]) -> int:
    """Check the third lens finds what the first excludes — the cut in the graph."""
    with tempfile.TemporaryDirectory() as raw:
        path = _written(Path(raw), "deferred", _DEFERRED)
        if "store" not in import_reach.deferred_seed_imports(path):
            out.append("selftest: the deferred lens missed a function-local seed")
            return 1
    return 0


def a_seed_imported_at_both_scopes_is_not_a_cut(out: list[str]) -> int:
    """Check a seed already visible at module scope is not also reported as deferred.

    ⚑ NOISE IN A CENSUS WHOSE VALUE IS THAT EVERY ROW NEEDS ADJUDICATING. A module importing a
    seed at both scopes is already visible to the reach lens; listing it again would dilute the
    rows that mark a genuine blind spot.
    """
    both = _DIRECT + _DEFERRED
    with tempfile.TemporaryDirectory() as raw:
        path = _written(Path(raw), "both", both)
        if import_reach.deferred_seed_imports(path):
            out.append("selftest: a seed imported at both scopes was reported as a cut")
            return 1
    return 0


def a_direct_reach_returns_its_route(out: list[str]) -> int:
    """Check reach returns the seed it found, not merely True."""
    with tempfile.TemporaryDirectory() as raw:
        directory = Path(raw)
        path = _written(directory, "direct", _DIRECT)
        found = import_reach.store_reach(path, index={})
        if not found.reaches:
            out.append("selftest: a direct store import did not read as reaching")
            return 1
        if found.via != ("store",):
            out.append(f"selftest: the route is {found.via!r}, expected ('store',)")
            return 1
    return 0


def a_transitive_reach_records_every_hop(out: list[str]) -> int:
    """Check the route names the whole chain — TRANSITIVE, because the incident was.

    ⚑ ONE TOOL REACHED THE STORE THROUGH ITS OWN IMPORTS and a degree-1 census read it as clean.
    Under-admitting certifies a suite that WILL abort as not needing a tenant.
    """
    with tempfile.TemporaryDirectory() as raw:
        directory = Path(raw)
        outer = _written(directory, "outer", _INDIRECT)
        middle = _written(directory, "middle", _MIDDLE)
        found = import_reach.store_reach(outer, index={"middle": middle})
        if not found.reaches:
            out.append("selftest: a transitive store reach was missed")
            return 1
        if found.via != ("middle", "store"):
            out.append(f"selftest: the route is {found.via!r}, expected ('middle', 'store')")
            return 1
    return 0


def a_deferred_reach_is_marked_and_opt_in(out: list[str]) -> int:
    """Check `through_cuts` changes the answer AND marks the hop — the two-question arm.

    ⚑⚑ COLLAPSING THE TWO would answer the import GRAPH where the question was about what RUNS.
    The mark is what keeps both askable from one walk.
    """
    with tempfile.TemporaryDirectory() as raw:
        path = _written(Path(raw), "deferred", _DEFERRED)
        closed = import_reach.store_reach(path, index={})
        if closed.reaches:
            out.append("selftest: a deferred seed reached without --through-cuts")
            return 1
        opened = import_reach.store_reach(path, index={}, through_cuts=True)
        if not opened.reaches:
            out.append("selftest: a deferred seed did not reach WITH through_cuts")
            return 1
        if not opened.through_cut:
            out.append(f"selftest: the route {opened.via!r} does not mark the deferred hop")
            return 1
    return 0


def an_unparseable_file_is_empty_not_an_exception(out: list[str]) -> int:
    """Check a syntax error yields no imports rather than raising.

    ⚑⚑ A WALK THAT RAISES ON ONE BAD FILE REPORTS NOTHING ABOUT THE OTHER 262. The honest failure
    is an empty reading for that file, which the caller can see, not an abort nobody can read.
    """
    with tempfile.TemporaryDirectory() as raw:
        path = _written(Path(raw), "broken", _BROKEN)
        try:
            found = import_reach.local_imports(path)
        except SyntaxError:
            out.append("selftest: an unparseable file raised instead of reading empty")
            return 1
        if found:
            out.append(f"selftest: an unparseable file yielded {sorted(found)}")
            return 1
    return 0


def a_missing_file_is_empty_not_an_exception(out: list[str]) -> int:
    """Check an absent path yields no imports rather than raising."""
    try:
        found = import_reach.local_imports(Path("/nonexistent/nothing.py"))
    except OSError:
        out.append("selftest: a missing file raised instead of reading empty")
        return 1
    if found:
        out.append(f"selftest: a missing file yielded {sorted(found)}")
        return 1
    return 0


def the_index_finds_this_package(out: list[str]) -> int:
    """Check the resolution table is populated and keyed by BASENAME.

    ⚑ FLAT BY BASENAME, because that is how these files import each other. A package-qualified
    index would resolve NOTHING and report every file as store-free — a false ZERO.
    """
    index = import_reach.module_index()
    if "import_reach" not in index:
        out.append(f"selftest: the index holds {len(index)} module(s) and not this one")
        return 1
    return 0


_ARMS = (
    a_module_level_import_is_seen,
    a_function_local_import_is_not_seen,
    an_import_inside_a_try_is_seen,
    an_import_inside_an_if_is_seen,
    a_type_checking_import_is_seen,
    a_deferred_seed_is_reported_separately,
    a_seed_imported_at_both_scopes_is_not_a_cut,
    a_direct_reach_returns_its_route,
    a_transitive_reach_records_every_hop,
    a_deferred_reach_is_marked_and_opt_in,
    an_unparseable_file_is_empty_not_an_exception,
    a_missing_file_is_empty_not_an_exception,
    the_index_finds_this_package,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 1 + 1 + 1 + 2 + 2 + 3 + 2 + 2 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"import-reach selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"import-reach selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
