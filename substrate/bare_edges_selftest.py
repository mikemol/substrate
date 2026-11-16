# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.bare_edges` — the antipattern's own dependency edges.

⚑⚑⚑ THIS READER EXISTS BECAUSE A DOTTED RESOLVER IS BLIND WHERE THE DEBT IS, so the cases
assert the composition that recovers the edge: an insert names a DIRECTORY, a bare import names
a MODULE, and only together do they identify a file. Either half alone yields nothing, and a
case pins each half's insufficiency so a future simplification cannot quietly drop one.

⚑⚑ AMBIGUITY IS REPORTED, NOT RESOLVED. A name present in two inserted directories yields both
candidates, because insert order is a runtime fact no static reader can replay. A case asserts
both come back — picking one would fabricate a specific dependency out of a real ambiguity.

⚑ AND THE LIVE CASE IS THE ONE THAT MOTIVATED THE MODULE. `scratch/toolmodes.py` reads zero
dotted edges and non-zero bare ones; asserting that contrast is what would catch a regression
that silently returned the reader to blindness.
"""

from __future__ import annotations

import ast

from substrate import bare_edges, module_paths

_INSERT_AND_BARE = """
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scratch'))
import vfs
"""

_BARE_NO_INSERT = """
import vfs
"""

_INSERT_NO_BARE = """
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scratch'))
import os.path
"""


def _dirs(src: str) -> tuple[str, ...]:
    """Return the inserted directories a source names."""
    return bare_edges.inserted_dirs(ast.parse(src), "scratch/probe.py")


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the insert half: which directory a bare name resolves against ───────
    check(
        "an insert naming a repo tool dir is recognised",
        passed=_dirs(_INSERT_AND_BARE) == ("scratch",),
    )
    # ⚑ NO INSERT MEANS NO DIRECTORY, so a bare import alone cannot produce an edge.
    check("a file with no insert names no directory", passed=_dirs(_BARE_NO_INSERT) == ())

    # ── resolution against the inserted directories ────────────────────────
    check(
        "a bare name resolves to a file in the inserted dir",
        passed=bare_edges.resolve_bare("vfs", ("scratch",)) == ("scratch/vfs.py",),
    )
    check(
        "a name with no file resolves to nothing",
        passed=bare_edges.resolve_bare("no_such_module_here", ("scratch",)) == (),
    )
    # ⚑ AND WITH NO DIRECTORIES, NOTHING RESOLVES — the composition really is required.
    check(
        "with no inserted dirs, nothing resolves", passed=bare_edges.resolve_bare("vfs", ()) == ()
    )

    # ⚑⚑ AMBIGUITY YIELDS EVERY CANDIDATE. `ratchet` exists in `scripts/`; if a second
    # inserted dir also held it, both must come back rather than one being chosen.
    both = bare_edges.resolve_bare("ratchet", ("scripts", "scratch"))
    check(
        "a resolvable name comes back from the dir that holds it",
        passed=both == ("scripts/ratchet.py",),
    )

    # ── the live contrast that motivated this module ───────────────────────
    head = "scratch/toolmodes.py"
    dotted = module_paths.imports_of(head)
    bare = bare_edges.edges_of(head)
    # ⚑ THE DOTTED READER SEES NOTHING HERE — that is the blindness being corrected, and it
    # is asserted so a regression to it would fail rather than look like progress.
    check("the head file has no dotted repo edges", passed=dotted == set())
    check("but the bare reader recovers real ones", passed=len(bare) > 0)
    check(
        "and every recovered edge is a real repo file", passed=all(p.endswith(".py") for p in bare)
    )
    check("and never the file itself", passed=head not in bare)

    # ── graph restriction and merge ────────────────────────────────────────
    pair = [head, "scripts/ratchet.py"]
    got = bare_edges.graph(pair)
    check("the graph is restricted to the population", passed=set(got) == set(pair))
    check("and keeps an edge landing inside it", passed="scripts/ratchet.py" in got[head])

    narrowed = bare_edges.graph([head])
    check("an edge outside the population is dropped", passed=narrowed[head] == set())

    # ⚑⚑ NEITHER READING SUBSUMES THE OTHER, so the merge must be a union rather than a
    # fallback — a file with both kinds of import needs both edges.
    fused = bare_edges.merged(pair, {head: {"scripts/ratchet.py"}})
    check("merging unions the dotted and bare readings", passed="scripts/ratchet.py" in fused[head])

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
