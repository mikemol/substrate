#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Which modules import a module that imports them back — the import cycles, any length.

⚑⚑⚑ THE CYCLE IS THE DIRECT CAUSE OF A MEASURED PER-FILE-GATE DEADLOCK. The `--selftest`
convention gives a module `M` a trailer that imports `M_selftest`, and `M_selftest` imports `M`
to exercise it. The gate checks an edited file's whole import closure, so when either half
carries a stale name BOTH become unwritable and neither can move first. Deleting one does not
break the tie: a refused write leaves NO file, so the survivor then fails on a missing import.
Operator's reading — *"modules in question need to be decomposed until they become a DAG-shaped
dependency, not a tangled mesh"* — makes this reader the measurement of that population.

⚑⚑ THREE EXISTING PROBES REPORT A FALSE ZERO ON THIS QUESTION, and each is honest about a
different thing. `pycodemod --importers substrate.edge_census_selftest` reads 0 because it keys
on module-SCOPE spellings while the trailer import sits inside `if __name__ == "__main__"`; a
`--literal` search reads 0 because an import statement is not a string literal. Both report the
boundary of the METHOD. `import_edges` already descends into `ast.If`, so it is the reader that
can see this edge at all — which is why this module REUSES it rather than parsing imports a
fourth time.

⚑ WHAT HAD TO BE EXTENDED, AND WHY IT IS AN EXTENSION RATHER THAN A COPY. `import_edges._named`
truncates every name to its top-level package, so `from substrate import edge_census_selftest`
reads as `substrate` — under which EVERY file in the package imports the package, EVERY pair is
a cycle, and the census reports the package instead of the edge. So `import_edges` gained
`module_level_dotted` / `deferred_dotted`: the same measured descent rules, parameterised by
which spelling of a name they report. The descent is the part that was expensive to get right
(it already carries a corrected false positive about deferred edges); duplicating it to change
the naming would have forked exactly that.

⚑ AN EAGER EDGE AND A DEFERRED ONE ARE BOTH REPORTED, AND THE DEADLOCK NEEDS BOTH. The gate
reads the file's imports statically — it does not care whether the statement would ever
execute — so a function-local `import M` closes the loop for the gate just as a trailer does.
That is the opposite of the reading `import_edges` takes for its store-reachability census, and
saying so here is the point: the same edge set answers two questions differently.

⚑⚑ TWO HONEST BOUNDS OF THE FIRST CUT ARE NOW CLOSED, AND BOTH WERE FACTS ABOUT THE METHOD.
It measured `substrate/` only and it found LENGTH-2 CYCLES ONLY. A 3-cycle deadlocks the gate
exactly as a pair does and the pair reader printed 0 for it; a cycle spanning two trees was
invisible for a subtler reason — the far half was not in the population, so the existence test
that keeps attributes from becoming edges deleted the edge, and the census reported a confident
zero. `loops()` walks any length; `modules()` is variadic so every tree can be ONE population.
Widening also forced `dotted()`: the old name was `f"{PACKAGE}.{stem}"`, a constant prefix that
mislabels every other tree and a bare stem that collides same-named files across subpackages.

⚑ `from X import Y` IS AMBIGUOUS AND THE EXISTENCE TEST IS THIS MODULE'S JOB. A name is kept
only when a file of that name is in the population, so `from substrate import corpus` counts and
`from substrate import ROOT` (an attribute) does not. Guessing inside the parser would put
attributes into an edge census wearing module names.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import NamedTuple

from mikemol.corpus import import_edges

from substrate import corpus

# The package this reader measures. Its modules are addressed `<PACKAGE>.<stem>`.
PACKAGE = "substrate"

# The convention's suffix. A pair whose second half ends in this is a module/suite trailer pair
# — the EXPECTED population. Anything else is the interesting kind.
SUITE_SUFFIX = "_selftest"


class Cycle(NamedTuple):
    """One unordered 2-cycle between two modules of the package."""

    low: str
    high: str
    eager: bool

    @property
    def is_suite_pair(self) -> bool:
        """Report whether this is a module and its own `*_selftest` sibling.

        ⚑ THE DISCRIMINATOR, NOT A COSMETIC LABEL. A suite pair is expected debt with a known
        retirement (the pytest port); any OTHER 2-cycle is an unexplained tangle, and reporting
        one number over both would bury the second population inside the first.
        """
        return self.high == self.low + SUITE_SUFFIX


def dotted(path: str, base: Path) -> str:
    """Return the dotted module name `path` carries when read as living under `base`.

    ⚑⚑⚑ THE ORIGINAL SPELLING WAS `f"{PACKAGE}.{stem}"` — A CONSTANT PREFIX AND A BARE STEM —
    AND BOTH HALVES ARE WRONG THE MOMENT THE READER LEAVES `substrate/`. The constant made
    every tree's modules answer to `substrate.<stem>`, so pointing `cycles()` at `scripts/`
    would have produced names that no import statement in the repo can ever spell, and every
    edge would have been filtered away — a reader returning 0 for a structural reason, wearing
    the appearance of a measurement. The bare stem is the second half: `substrate/` is FLAT, so
    a stem is a whole name there, while `jea/metalanguage/jea_pysim.py` is `jea.metalanguage.
    jea_pysim` and collapsing it to `jea_pysim` would collide every same-named file across
    subpackages into one node and INVENT cycles between unrelated files.

    ⚑ THE NAME IS DERIVED FROM THE PATH, NOT DECLARED. A declared prefix is a second place the
    truth lives, and this module already carries the record of what a stale constant costs.
    """
    rel = Path(path).relative_to(base).with_suffix("")
    return ".".join(rel.parts)


def modules(*roots: str, base: Path | None = None) -> dict[str, str]:
    """Return `{dotted module name: path}` for every module under the given roots.

    ⚑⚑⚑ VARIADIC, AND THAT IS WHAT MAKES A CROSS-TREE CYCLE DETECTABLE AT ALL. A reader
    enumerating ONE root cannot see a `scripts/` ↔ `substrate/` loop: the far half is not in
    the population, so the edge is filtered out by the very existence test that keeps
    attributes from becoming edges — and the census then prints a confident 0. That zero would
    be a fact about the METHOD reported as a fact about the substrate, which is the class this
    repo has a standing rule against. Passing every tree in ONE call puts both halves in one
    population, so a spanning cycle is an ordinary find rather than an undetectable one.

    ⚑ `base` IS THE FRAME THE DOTTED NAMES ARE READ IN, and it defaults to the repo root
    because that is the frame `from substrate import x` and `from jea.metalanguage import y`
    are written in. A caller naming a root OUTSIDE that frame (a fixture in a temp directory)
    gets the root's PARENT, which reproduces the package-qualified reading locally.
    """
    picked = roots or (PACKAGE,)
    out: dict[str, str] = {}
    for r in picked:
        resolved = corpus.resolve_root(r)
        frame = (
            base
            if base is not None
            else (corpus.ROOT if resolved.is_relative_to(corpus.ROOT) else resolved.parent)
        )
        out.update(
            {
                dotted(path, frame): path
                for path in corpus.py_files(r)
                if not Path(path).name.startswith("__")
            }
        )
    return out


def edges(names: dict[str, str], *, eager_only: bool) -> dict[str, frozenset[str]]:
    """Return `{module: the package modules it names}`, filtered to the population.

    ⚑ FILTERED AGAINST `names`, WHICH IS WHAT MAKES THE AMBIGUOUS `from X import Y` SAFE. A
    candidate that is not a file in the population is an attribute, not an edge.
    """
    by_dir = siblings(names)
    out: dict[str, frozenset[str]] = {}
    for name, path in names.items():
        got = set(import_edges.module_level_dotted(path))
        if not eager_only:
            got |= set(import_edges.deferred_dotted(path))
        local = by_dir.get(str(Path(path).parent), {})
        out[name] = frozenset(
            {c for c in got if c in names} | {local[c] for c in got if c in local}
        ) - {name}
    return out


def siblings(names: dict[str, str]) -> dict[str, dict[str, str]]:
    """Return `{directory: {bare module name: its dotted name}}` over the population.

    ⚑⚑⚑ A SECOND NAMING FRAME EXISTS AND IGNORING IT PRODUCED 507 MODULES WITH ZERO EDGES.
    `scratch/` runs its tools as SCRIPTS, so `pycodemod.py` spells `import _pycodemod_core` —
    a bare sibling that python resolves against the importing file's own DIRECTORY, not
    against any package root. Matching only repo-frame dotted names filtered every one of
    those away, and `scratch/`, `jea/`, `el-atlas/` and `catalog/` each came back a confident
    `0 cycles` — over a tree whose own source prose says *"the cycle is what places these in
    the core"*. That zero was a fact about the METHOD wearing a measurement's clothes, and the
    printed denominator is what exposed it.

    ⚑ IT IS THE EXISTENCE TEST WIDENED, NOT A THIRD NAMER. `_named_dotted` already reports the
    bare name as a candidate; what was missing is the layer that knows which corpus is being
    asked about — and this module already owns that test for `from X import Y`. Resolution
    stays HERE, where the filesystem is known, exactly as that case argued.

    ⚑ SCOPED PER DIRECTORY, NEVER FLATTENED. A single bare-name map over the whole corpus
    would make `scratch/foo.py`'s `import util` resolve to `jea/util.py` — an edge between
    files that cannot see each other, and the invented-cycle failure the dotted naming was
    introduced to stop in the first place.
    """
    out: dict[str, dict[str, str]] = {}
    for name, path in names.items():
        out.setdefault(str(Path(path).parent), {})[Path(path).stem] = name
    return out


def cycles(*roots: str, base: Path | None = None) -> tuple[Cycle, ...]:
    """Return every 2-cycle among the modules under the given roots, sorted.

    ⚑ THE PAIR IS UNORDERED AND EMITTED ONCE. Reporting `(a, b)` and `(b, a)` as two rows would
    double the population — a census inflating its own subject is the class this tree keeps
    catching.
    """
    names = modules(*roots, base=base)
    everything = edges(names, eager_only=False)
    eager = edges(names, eager_only=True)

    return tuple(
        sorted(
            Cycle(low=a, high=b, eager=b in eager[a] and a in eager[b])
            for a, reaches in everything.items()
            for b in reaches
            if a < b and a in everything[b]
        )
    )


def rotate(members: tuple[str, ...]) -> tuple[str, ...]:
    """Return the canonical rotation of a cycle: the one starting at its lowest member.

    ⚑⚑ A CYCLE IS A LOOP, NOT A LIST, AND WITHOUT THIS THE SAME TANGLE IS REPORTED ONCE PER
    MEMBER. A DFS entered from each of a 3-cycle's three nodes finds `(A,B,C)`, `(B,C,A)` and
    `(C,A,B)` — three rows for one defect, and a retirement plan sized against a number that is
    N times the work. It is the same over-count `a_pair_is_emitted_once` already guards for
    length two, generalised.

    ⚑ ROTATION ONLY, NEVER `sorted()`. Sorting the members would erase the DIRECTION, and the
    edge order is the thing a reader needs to break the loop — `A → B → C → A` says which
    import to cut, `(A, B, C)` as a set says only that something is wrong.
    """
    at = members.index(min(members))
    return members[at:] + members[:at]


def _shortest_first(members: tuple[str, ...]) -> tuple[int, tuple[str, ...]]:
    """Return the sort key that orders cycles by length, then by member names.

    ⚑ A NAMED FUNCTION BECAUSE A LAMBDA'S PARAMETER IS UNANNOTATED, so its type is `Any` and
    the gate refuses it. That refusal is correct here rather than pedantic: the key IS the
    reading order the census presents, and the shortest tangles are the ones a reader can act
    on first.
    """
    return (len(members), members)


class Walk:
    """The mutable state of one depth-first sweep over the edge relation.

    ⚑ THE PER-FILE GATE REFUSED THE THREADED FORM, AND IT WAS RIGHT. Passing `stack`, `on`,
    `done` and `found` alongside the graph made a six-argument recursion — the gate's reading
    is that four of those are ONE THING, the walk's own state, and naming it removes the
    parameter bag rather than raising a threshold to admit it.

    ⚑ `on` IS THE CURRENT STACK AS A SET, NOT A SECOND TRUTH. It exists only so the back-edge
    test is a hash lookup instead of a scan of `stack`; it is maintained in lockstep, which is
    why both live in one object rather than in two callers' locals.
    """

    def __init__(self, reach: dict[str, frozenset[str]]) -> None:
        """Start an empty sweep over `reach`."""
        self.reach = reach
        self.stack: list[str] = []
        self.on: set[str] = set()
        self.done: set[str] = set()
        self.found: set[tuple[str, ...]] = set()

    def descend(self, node: str) -> None:
        """Walk from `node`, recording every elementary cycle closed on the current stack.

        ⚑⚑⚑ A BACK EDGE IS A CYCLE; A CROSS EDGE INTO A FINISHED NODE IS NOT — AND THAT IS THE
        POSITIVE CONTROL'S WHOLE SUBJECT. A walk reporting a cycle whenever it re-reached a
        node it had already seen would call the diamond `A→B→D`, `A→C→D` a cycle, and a DAG of
        any width is full of diamonds: it would report the entire corpus as tangled while
        passing every case that only asks *is the known cycle found*. The discriminator is
        membership of the CURRENT STACK (`on`), never of `done`.

        ⚑ `done` PRUNES, IT DOES NOT DECIDE. It stops re-descending a subtree whose cycles are
        already recorded; every verdict is still read off `on`.
        """
        self.stack.append(node)
        self.on.add(node)
        for nxt in sorted(self.reach.get(node, frozenset())):
            if nxt in self.on:
                self.found.add(rotate(tuple(self.stack[self.stack.index(nxt) :])))
            elif nxt not in self.done:
                self.descend(nxt)
        self.on.discard(node)
        self.done.add(node)
        self.stack.pop()


def loops(
    *roots: str, base: Path | None = None, eager_only: bool = False
) -> tuple[tuple[str, ...], ...]:
    """Return every import cycle of ANY length among the modules under the given roots.

    ⚑⚑⚑ THE 2-CYCLE READER REPORTS 0 FOR A 3-CYCLE, AND A 3-CYCLE DEADLOCKS THE PER-FILE GATE
    IDENTICALLY. `A → B → C → A` makes all three files unwritable the moment any one carries a
    stale name, and deleting a member is the same trap: the refused write leaves no file and
    the survivors then fail on a missing import. So a census restricted to length two answers a
    question narrower than the defect it exists to size, and prints a zero for the rest.

    ⚑ IT REUSES `edges`, WHICH IS THE POINT. The naming, the descent, the deferred/eager split
    and the existence test that keeps `from X import <attribute>` from inventing an edge were
    all expensive to get right and already carry corrected false positives. A second edge
    reader would fork exactly those.

    ⚑ THE 2-CYCLES ARE INCLUDED, NOT EXCLUDED. A length-2 loop IS a loop; making this the
    strictly-longer population would leave a reader unable to ask one question and get the
    whole answer. `cycles()` remains the split-by-suite-pair reading of the same relation.
    """
    walk = Walk(edges(modules(*roots, base=base), eager_only=eager_only))
    for start in sorted(walk.reach):
        if start not in walk.done:
            walk.descend(start)
    return tuple(sorted(walk.found, key=_shortest_first))


def render(found: tuple[Cycle, ...]) -> str:
    """Return the census as text, splitting the suite pairs from everything else.

    ⚑ IT PRINTS ITS DENOMINATOR AND BOTH POPULATIONS. An empty result must name its own
    emptiness; silence and success are the same bytes.
    """
    if not found:
        return "  no 2-cycle among the modules read\n"

    pairs = [c for c in found if c.is_suite_pair]
    other = [c for c in found if not c.is_suite_pair]
    lines = [
        f"  {len(found)} 2-cycle(s)",
        f"  module/suite trailer pairs             : {len(pairs)}",
        f"  ⚑ OTHER (not a trailer pair)           : {len(other)}",
    ]
    lines.extend(
        f"    ⚑ {c.low} <-> {c.high}{' (eager both ways)' if c.eager else ''}" for c in other
    )
    lines.extend(f"    {c.low} <-> {c.high}" for c in pairs)
    return "\n".join(lines) + "\n"


# The length the ORIGINAL reader could see. ⚑ NAMED SO THE BOUND IS A FACT ABOUT THE OLD
# METHOD RATHER THAN A NUMBER IN A COMPARISON: everything above it is the population that
# reader reported as absent, and the split is the whole point of the extension.
PAIR = 2


def render_loops(found: tuple[tuple[str, ...], ...]) -> str:
    """Return the any-length census, splitting the longer cycles from the pairs.

    ⚑⚑ THE LONGER POPULATION IS PRINTED SEPARATELY OR IT DISAPPEARS INTO THE PAIRS. Ten
    expected trailer pairs and one unexplained 3-cycle summed to `11 cycle(s)` would read as
    the known debt having grown by one, and the interesting row is exactly the one a single
    total hides.

    ⚑ IT NAMES ITS OWN EMPTINESS, AND SAYS SO AS A MEASUREMENT. `0 longer` is the reader
    REPORTING what it walked, not a claim that no longer cycle can exist — the same distinction
    the 2-cycle render already prints its denominator for.
    """
    longer = [c for c in found if len(c) > PAIR]
    lines = [
        f"  {len(found)} cycle(s) of any length",
        f"  length 2                               : {len(found) - len(longer)}",
        f"  ⚑ LONGER THAN 2 (walked, not assumed)  : {len(longer)}",
    ]
    lines.extend("    ⚑ " + " → ".join((*c, c[0])) for c in longer)
    return "\n".join(lines) + "\n"


def trees() -> tuple[str, ...]:
    """Return the roots this census sweeps, one per tree.

    ⚑ DISCOVERED FROM `corpus.roots()`, NOT LISTED. A frozen roster is why `catalog/` sat
    outside the corpus for three separate tools in this repo; the walk that finds the trees is
    the same one the population comes from, so a new tree is measured the day it appears.
    """
    return corpus.roots()


def denominator(*roots: str) -> str:
    """Return how many modules were read and how many edges were resolved among them.

    ⚑⚑⚑ WITHOUT THIS, A ZERO IS UNREADABLE, AND THE WIDENING PRODUCED EXACTLY THAT SHAPE:
    every tree but `substrate/` came back `0 cycles` on the first run. Two causes fit that
    output — the tree really is acyclic, or its modules are named in a frame no import
    statement there spells, so EVERY edge is filtered out by the existence test and the walk
    is handed an edgeless graph. **A cycle count alone cannot tell them apart.** Printing the
    edge count beside it can: `0 cycles over 0 edges` is a reader that saw nothing, and `0
    cycles over 900 edges` is a measurement.

    ⚑ IT IS A KNOWN LIVE GAP, NOT A HYPOTHETICAL. `scratch/` runs its tools as scripts, so
    `pycodemod.py` spells `import _pycodemod_core` — a bare sibling name that resolves by
    directory, not by package. `dotted()` reads it in the repo frame as `scratch.pycodemod`,
    the import names `_pycodemod_core`, and the two do not meet. The tree that documents its
    own strongly-connected component in prose is therefore the one this reader can say least
    about, and the honest form of that is a printed denominator rather than a confident 0.
    """
    names = modules(*roots)
    reach = edges(names, eager_only=False)
    return (
        f"  read {len(names)} module(s), resolved "
        f"{sum(len(v) for v in reach.values())} intra-population edge(s)\n"
    )


def main() -> int:
    """Print the census per tree, then over every tree at once."""
    for tree in trees():
        sys.stdout.write(f"{tree}/\n")
        sys.stdout.write(denominator(tree))
        sys.stdout.write(render(cycles(tree)))
        sys.stdout.write(render_loops(loops(tree)))
    sys.stdout.write("ALL TREES AT ONCE (the reading that can see a cross-tree cycle)\n")
    sys.stdout.write(denominator(*trees()))
    sys.stdout.write(render(cycles(*trees())))
    sys.stdout.write(render_loops(loops(*trees())))
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        from substrate import self_import_selftest

        sys.exit(self_import_selftest.selftest())
    sys.exit(main())
