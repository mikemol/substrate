# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""A package's INTERNAL import graph: its modules, the edges between them, and the in-degrees.

    python -m substrate.package_graph PACKAGE_DIR [--top N]

⚑ BUILT FOR mtools' N-h (2026-09-24), which asked substrate to re-measure its reconcile study's
figures — 415 non-selftest modules, 564 module-to-module edges, an in-degree table — on the tree
as it stands. No mode answered that: `toolmodes --find edges` found only Agda-side and
`scripts/`-scoped readers. A figure re-derived by hand is the one the next reader re-derives
differently, so the census is a tool.

⚑ THE PACKAGE IS A REQUIRED ARGUMENT, never a module constant (operator ruling 2026-09-24,
"We should not have things [like] corpus.ROOT"). Its NAME is the directory's name.

⚑ EAGER AND DEFERRED ARE COUNTED SEPARATELY and summed only in a labelled total. A function-local
import is the edge that closed this package's one live cycle; a count that folded it in silently
would describe a different graph than the one that imports at load time.
"""

from __future__ import annotations

import collections
import sys
from dataclasses import dataclass, field
from pathlib import Path

from mikemol.corpus import import_edges

_SUITE = "_selftest"
_DEFAULT_TOP = 10
USAGE = "usage: python -m substrate.package_graph PACKAGE_DIR [--top N]\n"


@dataclass(slots=True)
class Graph:
    """Modules, and the edges between them split by when they fire."""

    modules: list[str] = field(default_factory=list)
    suites: list[str] = field(default_factory=list)
    eager: set[tuple[str, str]] = field(default_factory=set)
    deferred: set[tuple[str, str]] = field(default_factory=set)

    @property
    def edges(self) -> set[tuple[str, str]]:
        """Every distinct `(importer, imported)` pair, eager or deferred."""
        return self.eager | self.deferred

    def in_degree(self) -> collections.Counter[str]:
        """Return how many distinct modules import each module."""
        return collections.Counter(target for _src, target in self.edges)


def _targets(names: set[str], package: str, known: set[str], self_name: str) -> set[str]:
    """Return the package modules a set of dotted import names reaches, excluding self."""
    prefix = package + "."
    out: set[str] = set()
    for name in names:
        if not name.startswith(prefix):
            continue
        leaf = name[len(prefix) :].split(".", 1)[0]
        if leaf in known and leaf != self_name:
            out.add(leaf)
    return out


def build(package_dir: Path) -> Graph:
    """Read every module under `package_dir` (one level) and its intra-package edges.

    Suites (`*_selftest`) are listed separately and are NOT graph nodes — the study counted
    non-selftest modules, and a suite importing its subject is not a dependency of the package.
    """
    package = package_dir.name
    graph = Graph()
    files = sorted(p for p in package_dir.glob("*.py") if p.is_file())
    for path in files:
        (graph.suites if path.stem.endswith(_SUITE) else graph.modules).append(path.stem)
    known = set(graph.modules)
    for path in files:
        if path.stem not in known:
            continue
        where = str(path)
        for target in _targets(
            set(import_edges.module_level_dotted(where)), package, known, path.stem
        ):
            graph.eager.add((path.stem, target))
        for target in _targets(set(import_edges.deferred_dotted(where)), package, known, path.stem):
            graph.deferred.add((path.stem, target))
    return graph


def render(graph: Graph, top: int) -> list[str]:
    """Render the census: denominators first, then the in-degree table."""
    mods = graph.modules
    no_init = len([m for m in mods if m != "__init__"])
    importing = {s for s, _t in graph.edges}
    out = [
        f"modules (non-selftest, incl. __init__): {len(mods)}   excl. __init__: {no_init}",
        f"suites (*_selftest, not graph nodes): {len(graph.suites)}",
        (
            f"edges: {len(graph.edges)} distinct   = eager {len(graph.eager)}"
            f" + deferred-only {len(graph.deferred - graph.eager)}"
        ),
        f"modules importing nothing in-package: {len(set(mods) - importing)}",
        f"modules nothing in-package imports: {len(set(mods) - set(graph.in_degree()))}",
        f"\nin-degree, top {top}:",
    ]
    out.extend(f"  {n:4d}  {m}" for m, n in graph.in_degree().most_common(top))
    return out


def main(argv: list[str]) -> int:
    """Parse `PACKAGE_DIR [--top N]` and print the census."""
    args = list(argv)
    top = _DEFAULT_TOP
    if "--top" in args:
        at = args.index("--top")
        value = args[at + 1] if at + 1 < len(args) else ""
        if not value.isdigit():
            sys.stderr.write(USAGE)
            return 2
        top = int(value)
        del args[at : at + 2]
    if len(args) != 1 or not Path(args[0]).is_dir():
        sys.stderr.write(USAGE)
        return 2
    sys.stdout.write("\n".join(render(build(Path(args[0])), top)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
