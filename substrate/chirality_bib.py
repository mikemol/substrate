#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Run the chirality solver over a LIVE bib corpus — the wiring `substrate.chirality` lacked.

⚑⚑⚑ THIS EXISTS BECAUSE THE SOLVER WAS BUILT AND NEVER POINTED AT DATA. `module_importers` reported
exactly one import site for `substrate.chirality`, and that site was its own selftest: a solved
theorem with no reading. A reader that cannot be run against the corpus answers no question about
the corpus, however green its cases are.

⚑⚑ THE EDGE SET IS NOT RE-DERIVED HERE. `substrate.bib_corpus` already owns what an edge IS — the
`EDGE_FIELDS` roster and the comma-split — and re-spelling that here would make a second authority
for the same question, which is the defect the one-roster comment in that module records. This
module composes `bib_parse.read` into `bib_corpus.compose`, its `edges` into `chirality.solve`.

⚑⚑ THE NODE POPULATION IS THE WHOLE ENTRY SET, NOT THE EDGE ENDPOINTS. An entry declaring no edge
constrains nothing, but it is still corpus — so it belongs in the denominator. `solve` counts it as
population without inflating the component count, and that distinction is exactly why the entries
are passed in separately rather than left implicit in the edges.

⚑⚑ AND "DETERMINED" IS A QUESTION ABOUT THE COMPONENT, NOT ABOUT MEMBERSHIP. The free bit is per
component, so two keys each carrying a perspective are still jointly undetermined when they sit in
different components — their RELATIVE chirality is a choice the graph declines to make. `component`
is therefore computed here rather than read off `perspective`, whose keys say only "placed".

⚑ THE VERDICT PRINTED IS THE THREE-WAY ONE, unchanged. `chirality.render` owns the causes roster;
this module does not summarise it, because a caller rendering two of three causes is the
census-green failure and the roster is data precisely to stop that.
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import bib_corpus, chirality
from substrate.bib_parse import read

# The corpus this reader defaults to — the worklist whose darts the closure is asked about.
DEFAULT_BIB = "catalog/worklist/warrants.bib"


def read_graph(paths: list[str]) -> tuple[tuple[tuple[str, str, str], ...], tuple[str, ...]]:
    """Return the `(kind, source, target)` edges and the full entry population of `paths`."""
    corpus = bib_corpus.compose([Path(p) for p in paths], read)
    return bib_corpus.edges(corpus), tuple(sorted(corpus.entries))


def solve_bib(paths: list[str]) -> chirality.Assignment:
    """Solve the chirality assignment the given bibs force."""
    edges, nodes = read_graph(paths)
    return chirality.solve(edges, nodes)


def components(edges: tuple[tuple[str, str, str], ...]) -> dict[str, int]:
    """Return `node -> component id` over the undirected edge graph.

    Only nodes carrying an edge appear: an isolated entry is population, not a component, which is
    the same distinction `chirality.solve` draws when it counts `solutions`.
    """
    neighbours: dict[str, list[str]] = {}
    for _kind, source, target in edges:
        neighbours.setdefault(source, []).append(target)
        neighbours.setdefault(target, []).append(source)
    seen: dict[str, int] = {}
    ident = 0
    for start in sorted(neighbours):
        if start in seen:
            continue
        seen[start] = ident
        frontier = [start]
        while frontier:
            here = frontier.pop()
            for there in neighbours[here]:
                if there not in seen:
                    seen[there] = ident
                    frontier.append(there)
        ident += 1
    return seen


def determined(
    assignment: chirality.Assignment,
    edges: tuple[tuple[str, str, str], ...],
    keys: tuple[str, ...],
) -> bool:
    """Whether `keys` all sit in ONE component of a consistent assignment."""
    if assignment.conflicts or not keys:
        return False
    where = components(edges)
    ids = {where.get(key) for key in keys}
    return None not in ids and len(ids) == 1


def darts(paths: list[str], keys: tuple[str, ...]) -> tuple[tuple[str, str | None, str], ...]:
    """Return `(key, kind, target)` for each dart the closure CONSTRUCTS, `None` when it declines.

    ⚑ A `None` HERE IS THE ANSWER, NOT A GAP. `chirality.derive` returns nothing when the graph does
    not force one dart — a refuted assignment, an unplaced endpoint, an already-declared mate, or
    darts naming more than one target. Materialising something anyway would be the hand-picked
    direction the whole module refuses, so this reports the decline as the finding it is.
    """
    edges, nodes = read_graph(paths)
    assignment = chirality.solve(edges, nodes)
    out: list[tuple[str, str | None, str]] = []
    for key in keys:
        have = [(kind, target) for kind, src, target in edges if src == key]
        got = chirality.derive(assignment, key, have)
        out.append((key, got[0], got[1]) if got else (key, None, ""))
    return tuple(out)


def report(paths: list[str]) -> int:
    """Print the live verdict for `paths` and return its exit code."""
    edges, nodes = read_graph(paths)
    assignment = chirality.solve(edges, nodes)
    sys.stdout.write(f"corpus: {', '.join(paths)}\n")
    for line in chirality.render(assignment):
        sys.stdout.write(line + "\n")
    return assignment.code


def report_darts(paths: list[str], keys: tuple[str, ...]) -> int:
    """Print what the closure constructs for `keys`, and return the corpus's own verdict code."""
    assignment = solve_bib(paths)
    for key, kind, target in darts(paths, keys):
        if kind is None:
            sys.stdout.write(f"  — {key}: UNDETERMINED — the graph does not force one dart\n")
        else:
            sys.stdout.write(f"  ✓ {key}: {kind} -> {target}\n")
    sys.stdout.write(f"darts: {len(keys)} key(s) asked, {assignment.summary()}\n")
    return assignment.code


def main(argv: list[str]) -> int:
    """Run the reader over the bibs named on `argv`, or the default worklist."""
    operands = [a for a in argv if not a.startswith("-")]
    if "--darts" in argv:
        bibs = [a for a in operands if a.endswith(".bib")]
        keys = tuple(a for a in operands if not a.endswith(".bib"))
        return report_darts(bibs or [DEFAULT_BIB], keys)
    return report(operands or [DEFAULT_BIB])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
