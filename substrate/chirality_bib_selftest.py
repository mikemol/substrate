#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.chirality_bib` — the wiring, not the theorem.

⚑⚑ THE THEOREM IS ALREADY GATED NEXT DOOR and is not re-tested here. What this suite pins is the
part the solver's own suite CANNOT see: that the bib edge roster reaches the solver unchanged, that
the denominator is the whole entry population rather than the edge endpoints, and that "determined"
is answered per COMPONENT rather than per membership.

⚑ THE LIVE CORPUS IS READ AS A SMOKE ARM, NOT PINNED TO A VERDICT. Asserting today's verdict would
freeze a reading of a file that moves and would fail on the very repair the reader exists to
prompt; the arm asserts that the read HAPPENS and carries its denominator.
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import chirality, chirality_bib

# Two components: a-b, and the unlinked pair x-y. `z` carries no edge at all.
_EDGES: tuple[tuple[str, str, str], ...] = (
    ("rests-on", "a", "b"),
    ("rests-on", "x", "y"),
)
_NODES = ("a", "b", "x", "y", "z")

# What `_EDGES` must yield: two free bits, and `z` in the denominator but in neither component.
_WANT_COMPONENTS = 2


def the_edge_roster_reaches_the_solver(out: list[str]) -> int:
    """Check every field `bib_corpus` calls an edge is a kind the chirality table pins."""
    from substrate import bib_corpus  # noqa: PLC0415 — only this arm compares the two rosters

    missing = [k for k in bib_corpus.EDGE_FIELDS if k not in chirality.KIND_CHIRALITY]
    if missing:
        out.append(f"selftest: edge kind(s) the chirality table does not pin: {missing}")
        return 1
    return 0


def isolated_entries_are_population_not_components(out: list[str]) -> int:
    """Check an edge-free entry widens the denominator without adding a free bit."""
    got = chirality.solve(_EDGES, _NODES)
    if got.nodes_read != len(_NODES):
        out.append(f"selftest: nodes_read {got.nodes_read}, wanted {len(_NODES)}")
        return 1
    if got.components != _WANT_COMPONENTS:
        out.append(f"selftest: components {got.components}, wanted {_WANT_COMPONENTS}")
        return 1
    return 0


def keys_in_different_components_are_not_determined(out: list[str]) -> int:
    """Check `determined` asks about the component, not about membership in `perspective`."""
    got = chirality.solve(_EDGES, _NODES)
    if chirality_bib.determined(got, _EDGES, ("a", "x")):
        out.append("selftest: two components reported as jointly determined")
        return 1
    if not chirality_bib.determined(got, _EDGES, ("a", "b")):
        out.append("selftest: one component reported as undetermined")
        return 1
    if chirality_bib.determined(got, _EDGES, ("z",)):
        out.append("selftest: an edge-free entry reported as determined")
        return 1
    return 0


def a_refuted_graph_determines_nothing(out: list[str]) -> int:
    """Check no key is called determined when the assignment does not exist."""
    odd = (("rests-on", "a", "b"), ("rests-on", "b", "c"), ("from", "a", "c"))
    got = chirality.solve(odd)
    if chirality_bib.determined(got, odd, ("a", "b")):
        out.append("selftest: a refuted graph reported a determined key")
        return 1
    return 0


def the_live_corpus_is_readable(out: list[str]) -> int:
    """Check the default bib reads into a graph carrying both its denominators."""
    if not Path(chirality_bib.DEFAULT_BIB).exists():
        out.append(f"selftest: default bib absent at {chirality_bib.DEFAULT_BIB}")
        return 1
    got = chirality_bib.solve_bib([chirality_bib.DEFAULT_BIB])
    if got.verdict == chirality.UNREAD:
        out.append("selftest: the live corpus read ZERO edges — a fact about the reader")
        return 1
    if got.nodes_read < got.components:
        out.append(f"selftest: {got.components} component(s) over {got.nodes_read} node(s)")
        return 1
    return 0


def a_refuted_corpus_derives_no_dart(out: list[str]) -> int:
    """Check the darts mode DECLINES on a refuted graph rather than naming a direction.

    ⚑ THIS IS THE Ⓑ20b-prime PRECONDITION AS A CASE. The three retraction entries may only get a
    dart materialised when the graph determines one; a reader emitting a direction off a refuted
    assignment would be hand-picking, which is the failure the solver exists to prevent.
    """
    odd = (("rests-on", "a", "b"), ("rests-on", "b", "c"), ("from", "a", "c"))
    got = chirality.solve(odd)
    if chirality.derive(got, "a", [("rests-on", "b")]) is not None:
        out.append("selftest: a dart was derived from a refuted assignment")
        return 1
    return 0


_ARMS = (
    the_edge_roster_reaches_the_solver,
    isolated_entries_are_population_not_components,
    keys_in_different_components_are_not_determined,
    a_refuted_graph_determines_nothing,
    the_live_corpus_is_readable,
    a_refuted_corpus_derives_no_dart,
)

_CASE_COUNT = 1 + 2 + 3 + 1 + 3 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"chirality_bib selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"chirality_bib selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
