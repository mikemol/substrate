# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The Agda import DAG as a MODEL — the parse and the topological walk, with no emitter.

⚑⚑⚑ THIS IS THE HALF THAT SURVIVES A BACKEND CHANGE. `gen_build_makefiles.py` holds two
concerns that have nothing to do with each other: a model of the import graph (~90 lines) and
two string emitters that write `make` syntax (`flat_text` at 392 lines, `root_text` at 128 —
between them more than half the file). The model is what any build backend needs; the emitters
are make-specific and do not outlive it. Cutting along that seam is the drain's first move and
also the migration's, which is why it goes first.

⚑⚑ AND FIVE CONSUMERS ALREADY TREAT THE MODEL AS A LIBRARY, reaching into a file the per-file
gate refuses every edit to. `pycodemod --calls parse_tree` finds call sites in
`scratch/fix_notinscope.py`, `scratch/split_census.py`, `scripts/build_census.py` and
`substrate/agda_import_dag.py` — the last of which is ALREADY IN THIS PACKAGE and imports the
generator by BARE NAME (`from gen_build_makefiles import parse_tree`). That resolves only under
the sibling-finder path, which is why `tests/test_agda_census_drain.py` fails with
`ModuleNotFoundError: No module named 'gen_build_makefiles'` in a plain run. The model was
already wanted here; it was reachable only through a scripts-directory accident.

⚑⚑ THE WALK RETURNS A VERDICT AND DOES NOT EXIT. The origin's `kahn_depth` calls `sys.exit(2)`
on a cycle — a model function terminating the process — so no caller can ask "is this acyclic"
without being killed by the answer. A gate may still exit; that decision belongs to the gate,
not to the graph. `Cycle` carries the members so a caller can report them.

⚑ AND THE DEPTH IS A CAPABILITY THE ORIGIN COMPUTED AND DISCARDED, recorded in its own
docstring: the longest chain is the honest lower bound on a parallel build's wall time, and
`buildtime.py --predict` instead divides by a HARDCODED J unrelated to the RAM-derived
concurrency the build actually reaches. The data existed on every run and was thrown away.
"""

from __future__ import annotations

import re
from collections import deque
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from substrate import corpus

if TYPE_CHECKING:
    from collections.abc import Iterator

# Where the Agda tree and its include root sit, relative to the repo.
AGDA_DIR = corpus.ROOT / "agda"
SRC = AGDA_DIR / "Substrate"

# An in-tree import. ⚑ SOURCE-PARSED, so this is a SOUND SUPER-SET of the build's real deps:
# a module named in an `open import` line is a dependency even if the compiler would elide it.
# Over-approximating the graph is the safe direction — it orders too much, never too little.
#
# ⚑⚑⚑ THE CHARACTER CLASS WAS ASCII-ONLY HERE, AND THAT DEFECT WAS ALREADY FIXED IN THE ORIGIN.
# `[A-Za-z0-9_.'-]+` truncates at the first non-ASCII letter, so `open import …IsAñeléTerminal`
# parsed as a SHORTER name that matches no module and contributed NO edge. `gen_build_makefiles`
# measured it — 8 edges missing across 5 modules — and switched to take-everything-up-to-a-
# delimiter; this drain copied the pre-fix pattern (found t103, porting `flat_text`, whose
# byte-for-byte differential against `agda/Flat.mk` would have failed on exactly those edges).
# A MISSING edge is the unsafe direction: an edit to `PriorAñelé.agda` would not mark its importer
# stale. So the pattern is now the origin's, delimiter-bounded.
IMPORT_RE = re.compile(r"^\s*(?:open\s+import|import)\s+([^\s;(){}]+)", re.MULTILINE)

# The directory whose presence in a path means a build artefact, never a source.
BUILD_DIR = "_build"

# The source suffix, named once so the name-derivation and the walk cannot disagree.
SUFFIX = ".agda"


class Stripper(Protocol):
    """Removes comments from Agda source.

    ⚑ A PROTOCOL RATHER THAN `object`, because an untyped callback leaks `Any` into the parsed
    text and from there into every downstream set operation — which the zero-tolerance type gate
    refuses, correctly. The shape is the contract: text in, text out.
    """

    def __call__(self, text: str, /) -> str:
        """Return `text` with comments removed."""


@dataclass(frozen=True, slots=True)
class Cycle:
    """An import cycle: the modules that never reached in-degree zero.

    ⚑ A VALUE, NOT AN EXIT. The origin killed the process here, so the acyclicity question
    could not be ASKED — only survived. A gate that wants to refuse still can; it now chooses to.
    """

    members: tuple[str, ...]

    @property
    def message(self) -> str:
        """Return a one-line report naming the size and a sample."""
        return (
            f"import CYCLE among {len(self.members)} module(s) "
            f"(a make build would hang): {list(self.members[:8])}"
        )


@dataclass(frozen=True, slots=True)
class Dag:
    """The parsed import graph: modules on disk and their direct in-tree imports."""

    disk: dict[str, str]
    deps: dict[str, frozenset[str]]

    @property
    def rdeps(self) -> dict[str, frozenset[str]]:
        """Return the reverse relation — module to the modules importing it."""
        out: dict[str, set[str]] = {m: set() for m in self.disk}
        for module, imports in self.deps.items():
            for imported in imports:
                out.setdefault(imported, set()).add(module)
        return {m: frozenset(v) for m, v in out.items()}

    @property
    def src_to_mod(self) -> dict[str, str]:
        """Return the inverse of `disk` — source relpath to module name."""
        return {rel: module for module, rel in self.disk.items()}


def _module_name(rel: str) -> str:
    """Return the module name a source relpath declares.

    ⚑ PATH-DERIVED, AND THAT IS EXACT RATHER THAN A HEURISTIC. Agda requires the declared name
    to match the path under the include root, so this equals both the `module X where` name and
    every `open import X` string. Only the separator is rewritten — a `-` is legal in a module
    name and must survive.
    """
    return rel[: -len(SUFFIX)].replace("/", ".")


def _sources() -> Iterator[str]:
    """Yield every source relpath under the include root, `_build` excluded."""
    for found in sorted(SRC.rglob(f"*{SUFFIX}")):
        if BUILD_DIR in found.parts:
            continue
        yield found.relative_to(AGDA_DIR).as_posix()


def _imported(text: str) -> set[str]:
    """Return every module name an `import` line in `text` mentions.

    ⚑ THE UNTYPED BOUNDARY ENDS HERE. `Match.group` is typed `Any`, so reading it inline would
    carry `Any` into the graph's every set operation and the type gate refuses — correctly, since
    an untyped module name silently degrades each downstream comparison.
    """
    return {str(found.group(1)) for found in IMPORT_RE.finditer(text)}


def parse(strip: Stripper | None = None) -> Dag:
    """Return the import DAG parsed from the tree.

    `strip` removes comments before scanning; None scans the raw text.

    ⚑⚑ THE COMMENT STRIPPER IS AN ARGUMENT BECAUSE IT IS SOMEONE ELSE'S AUTHORITY.
    `agda_lex.mask_comments` owns what an Agda comment is, and this module must not become a
    second opinion on it — the `agda_files()`-had-four-bodies shape. A caller that has the lexer
    hands it in; one that does not gets a sound over-approximation, since an import mentioned in
    a comment adds an edge the build already respects.

    ⚑ IMPORTS ARE RESTRICTED TO MODULES PRESENT ON DISK, which is what makes the graph closed:
    a stdlib import names no in-tree module and contributes no edge.
    """
    disk = {_module_name(rel): rel for rel in _sources()}
    deps: dict[str, frozenset[str]] = {}
    for module, rel in disk.items():
        text = (AGDA_DIR / rel).read_text(encoding="utf-8", errors="replace")
        found = _imported(strip(text) if strip is not None else text)
        deps[module] = frozenset(d for d in found if d in disk and d != module)
    return Dag(disk=disk, deps=deps)


def topo(dag: Dag) -> tuple[int, tuple[str, ...]] | Cycle:
    """Return `(critical_path_depth, order)`, or a `Cycle` when one exists.

    ⚑⚑ THE DEPTH IS THE HONEST LOWER BOUND ON A PARALLEL BUILD'S WALL TIME — the longest chain
    in the DAG, which no `-j` width can beat. The origin computed it on every run and returned
    it into a call that discarded it, while `buildtime.py --predict` divided a CPU total by a
    hardcoded J unrelated to the concurrency the RAM semaphore actually admits.

    ⚑ A CYCLE IS RETURNED, NOT RAISED AND NOT EXITED. Agda modules are acyclic in practice, so
    this doubles as an acyclicity check — but a check whose failure mode is process death cannot
    be composed into a reader that wants to report on several trees.
    """
    rdeps = dag.rdeps
    indegree = {m: len(dag.deps[m]) for m in dag.disk}
    level = dict.fromkeys(dag.disk, 1)
    queue = deque(m for m in dag.disk if indegree[m] == 0)
    order: list[str] = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for downstream in rdeps.get(node, frozenset()):
            level[downstream] = max(level[downstream], level[node] + 1)
            indegree[downstream] -= 1
            if indegree[downstream] == 0:
                queue.append(downstream)

    if len(order) != len(dag.disk):
        return Cycle(members=tuple(sorted(m for m in dag.disk if indegree[m] > 0)))
    return (max(level.values()) if level else 0), tuple(order)


def is_acyclic(dag: Dag) -> bool:
    """Report whether the graph has no import cycle."""
    return not isinstance(topo(dag), Cycle)
