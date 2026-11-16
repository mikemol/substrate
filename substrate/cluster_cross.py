# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Which structural clusters SPAN two trees — the reuse census between substrate and a peer.

⚑⚑⚑ BUILT BECAUSE A NAME-KEYED REUSE SEARCH MISSED WHAT THE OPERATOR COULD SEE. Asked to census
mtools for code substrate would otherwise reimplement, the first pass compared MODULE NAMES and
read five modules; the operator: *"There's more than just census. There's lots of reusable,
importable code there."* A capability spelled differently in each tree is invisible to a name
match — the `--calls emit` / `_emit_one` shape. `jea_pysim --clusters --json` groups units by
shared STRUCTURE, which is spelling-blind; this module reads that JSON and keeps only the clusters
with members in BOTH trees, because those are the candidate twins.

⚑ A SPANNING CLUSTER IS A CANDIDATE, NOT A VERDICT. Shared structure is evidence the two units do
one job; whether the peer's copy should replace substrate's is a judgement made per row, over the
bodies — the same rule `bibstruct`'s collapse audit followed.

⚑ THE TREES ARE PARAMETERS. Each root is a path prefix given at the CLI entry, never a constant.

    python -m substrate.cluster_cross <clusters.json> <root-a> <root-b>
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

# The exit a refused invocation returns.
USAGE_EXIT = 2

USAGE = "usage: python -m substrate.cluster_cross <clusters.json> <root-a> <root-b>"


@dataclass(frozen=True, slots=True)
class Span:
    """One cluster with members in both trees: its members on each side."""

    index: int
    a: tuple[str, ...]
    b: tuple[str, ...]


def _units(cluster: object) -> list[str]:
    """Return a cluster's unit names, narrowed at the JSON seam; empty when it carries none."""
    if not isinstance(cluster, dict):
        return []
    units: object = cluster.get("units")
    if not isinstance(units, list):
        return []
    return [u for u in units if isinstance(u, str)]


def spans(clusters: list[object], root_a: str, root_b: str) -> list[Span]:
    """Return every cluster whose units include at least one under EACH root.

    ⚑ PREFIX, NOT SUBSTRING: a unit belongs to a tree when its path STARTS with that root, so a
    peer tree nested under a directory whose name happens to contain the other root is not
    misfiled.
    """
    out: list[Span] = []
    for index, cluster in enumerate(clusters):
        units = _units(cluster)
        a = tuple(u for u in units if u.startswith(root_a))
        b = tuple(u for u in units if u.startswith(root_b))
        if a and b:
            out.append(Span(index=index, a=a, b=b))
    return out


def render(found: list[Span], total: int) -> list[str]:
    """Render the spanning clusters, with the denominator they were drawn from."""
    lines: list[str] = []
    for span in found:
        lines.append(f"cluster {span.index}: {len(span.a)} + {len(span.b)} unit(s)")
        lines.extend(f"  A  {u}" for u in span.a)
        lines.extend(f"  B  {u}" for u in span.b)
    lines.append(f"{len(found)} of {total} cluster(s) span both trees")
    return lines


def main(argv: list[str]) -> int:
    """Read the clusters JSON and print the spanning clusters."""
    expected = 4
    if len(argv) != expected:
        sys.stderr.write(USAGE + "\n")
        return USAGE_EXIT
    doc: object = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    clusters: object = doc.get("clusters") if isinstance(doc, dict) else None
    if not isinstance(clusters, list):
        sys.stderr.write("cluster_cross: the JSON carries no `clusters` list\n")
        return USAGE_EXIT
    for line in render(spans(clusters, argv[2], argv[3]), len(clusters)):
        sys.stdout.write(line + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
