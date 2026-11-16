# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Whether a claim-graph admits a consistent chirality assignment, and whether it is unique.

⚑⚑⚑ PARITY IS NOT A PROPERTY OF AN EDGE. Both English readings of *"A supersedes B"* pick opposite
chiralities, so a reader that decides orientation edge by edge is guessing. The sign is fixed
GLOBALLY: the assignment is the one that makes entailment compose consistently over the whole graph.
This module solves for that assignment rather than reading it off one edge at a time.

⚑⚑⚑ THE MODEL, AND WHAT IS UNKNOWN IN IT. Each entry carries a PERSPECTIVE `phi(v)` in Z/2 — which
of the two entailment directions that node was authored from. Each edge KIND carries a fixed
chirality bit `k(kind)`: a `rests-on` is a COMPLETER dart (detail entails goal) and a `from` is its
PREDICTOR counterpart (goal entails detail). Consistency demands, for every edge `u -> v`:

    phi(u) XOR phi(v) == k(kind)

so the unknowns are the PERSPECTIVES, not the edges, and the edge kinds are the PINNED data. That is
exactly a 2-colouring: the system is solvable iff every cycle's kind-bits sum to zero mod 2, and the
solutions form a torsor over one free bit PER CONNECTED COMPONENT.

⚑⚑⚑ SO UNIQUENESS IS ALWAYS UP TO A PER-COMPONENT GLOBAL FLIP, AND SAYING "UNIQUE" WITHOUT THAT
QUALIFIER WOULD BE FALSE. A graph with `c` edge-bearing components admits `2**c` assignments; the
honest report is *unique up to the component flips*, and `c > 1` is the finding that the graph does
not yet tie its segments to each other. Collapsing that into "underconstrained" or into "unique"
both lose the shape.

⚑⚑⚑ AND A NO-CONSISTENT-ASSIGNMENT VERDICT IS THREE-WAY, NEVER TWO (operator's ruling, recorded
before the reader existed). An odd cycle means one of: the graph is GENUINELY inconsistent; two
segments were authored from different perspectives and a sigma-shift repairs it; or THIS READER is
wrong. Nothing in the arithmetic distinguishes them, so the verdict names all three and the reader
does not pick. That is the census-green failure at graph scale: a red light read as a fact about the
subject when it is first a fact about the instrument.

⚑ THE DENOMINATOR TRAVELS WITH EVERY NUMBER. A zero conflict count over an unread edge set and a
zero over the whole corpus are the same string without the population beside them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

# The chirality each edge kind pins, as a bit in Z/2.
#
# ⚑⚑ 0 = COMPLETER (detail entails goal), 1 = PREDICTOR (goal entails detail). The two are tau-mates
# of ONE entailment relation, not two relations — which is why a bit suffices and why the bit is
# attached to the KIND rather than guessed per edge.
#
# ⚑ `enables` IS THE PREDICTOR SPELLING OF `rests-on` READ FROM THE OTHER END, so it carries the
# opposite bit from `rests-on` even though both read as "supports" in English. That is precisely the
# local ambiguity this module exists to stop resolving by ear.
KIND_CHIRALITY: dict[str, int] = {
    "rests-on": 0,
    "entails": 0,
    "reads": 0,
    "consumes": 0,
    "from": 1,
    "enables": 1,
}

# Which kind is the TAU-MATE of which — the same relation read from the opposite chirality, with
# the ENDPOINTS UNCHANGED.
#
# ⚑⚑⚑ A BIT IS NOT ENOUGH TO NAME THE MATE, AND THE SELFTEST CAUGHT THE READER GUESSING. Two kinds
# carry chirality 1 (`from` and `enables`), so deriving "the predictor spelling" from the bit table
# alone made the reader pick between them by SORT ORDER — a hand-decision wearing a program's
# clothes, and precisely what this module refuses. They are not interchangeable: `from` is the
# TAU-mate of `rests-on` (same endpoints, other chirality) while `enables` is its SIGMA-mate (other
# endpoints). Only the tau-mate is the dart the closure constructs.
#
# ⚑ THE MAP IS AN INVOLUTION AND THE SELFTEST PINS THAT, because a mate relation that is not
# symmetric is two different claims sharing one name.
TAU_MATE: dict[str, str] = {
    "rests-on": "from",
    "from": "rests-on",
}

# Which kinds are SIGMA-mates — the same relation read from the OTHER ENDPOINT, so the pair must be
# REVERSED before its chirality bit applies.
#
# ⚑⚑⚑ THE MODULE DECLARED THIS ABOVE AND THE WALK DID NOT HONOUR IT. `TAU_MATE`'s comment already
# says `enables` is the SIGMA-mate of `rests-on` (other endpoints) while `from` is the TAU-mate
# (endpoints unchanged) — and `_adjacency` added every kind at its declared endpoints regardless.
# So `u enables v` was constrained as if it read `u rests-on v` with the opposite bit, which is the
# bit INVERTED for every sigma-mate edge in the corpus.
#
# ⚑⚑ MEASURED, AND THE WITNESS IS AN AGREEMENT RATHER THAN A CONTRADICTION: the worklist declares
# BOTH `A5-as rests-on A5-as-reach` and `A5-as-reach enables A5-as`. Those are ONE constraint stated
# twice from opposite ends and must agree — and they were reported as a conflict, because the reader
# read the second as a claim about the unswapped pair.
#
# ⚑ THE NORMAL FORM IS THE TAU/SIGMA-FREE SPELLING, so a sigma-mate contributes its PARTNER's bit at
# the reversed endpoints. That keeps one relation as one constraint however an author spelled it,
# which is the whole reason chirality is not decided per edge.
SIGMA_MATE: dict[str, str] = {
    "enables": "rests-on",
}

# The three things a no-consistent-assignment verdict can mean. ⚑ THE ROSTER IS DATA so that a
# caller cannot render two of them and forget the third.
AMBIGUOUS_CAUSES: tuple[str, ...] = (
    "the graph is GENUINELY inconsistent",
    "segments were authored from different perspectives (a sigma-shift, repairable)",
    "a defect in THIS reader — its kind-chirality table or its edge set",
)

CONSISTENT = "CONSISTENT"
INCONSISTENT = "INCONSISTENT"
UNREAD = "UNREAD"

# One exit code per verdict, all distinct: a caller must not have to parse prose.
CODES: dict[str, int] = {CONSISTENT: 0, INCONSISTENT: 1, UNREAD: 2}


@dataclass(frozen=True, slots=True)
class Conflict:
    """One edge whose kind-bit contradicts the perspectives already forced on its endpoints.

    ⚑ THIS IS A WITNESS, NOT A CULPRIT. The edge reported is the one that CLOSED an odd cycle during
    the walk, which depends on traversal order; every edge on that cycle is equally implicated. The
    row says where the contradiction became visible, and `AMBIGUOUS_CAUSES` says what it may mean.
    """

    kind: str
    source: str
    target: str
    source_perspective: int
    target_perspective: int
    # ⚑⚑⚑ THE IMPLICATED SET, AND IT IS THE INVARIANT THE COUNT IS NOT. Which edge surfaced depends
    # on traversal order; WHICH NODES the odd cycle runs through does not. Two repairs to this
    # reader moved the conflict population in opposite directions — a de-duplication down, a correct
    # sigma-normalisation UP — so the number measures the walk as much as the corpus, and no arm of
    # the three-way verdict can be asked of an integer. A cycle can be asked: whether its members
    # span one authorship segment (a sigma-shift, repairable by flipping that segment) or several
    # (a genuine inconsistency) is a property OF THE MEMBERS.
    cycle: tuple[str, ...] = ()

    def line(self) -> str:
        """Return the row this conflict prints."""
        return (
            f"  ⚠ {self.kind:<9} {self.source} -> {self.target}   "
            f"(phi {self.source_perspective}/{self.target_perspective}, "
            f"needs {KIND_CHIRALITY.get(self.kind, 0)})"
            + (f"   cycle {' '.join(self.cycle)}" if self.cycle else "")
        )


@dataclass(frozen=True, slots=True)
class Assignment:
    """A solved (or refuted) chirality reading of one claim-graph, with its population.

    ⚑ EVERY COUNT HERE HAS ITS DENOMINATOR IN THE SAME OBJECT. `conflicts` is meaningless without
    `edges_read`, and `components` is meaningless without `nodes_read`.
    """

    perspective: Mapping[str, int]
    conflicts: tuple[Conflict, ...]
    components: int
    nodes_read: int
    edges_read: int
    unknown_kinds: tuple[str, ...] = ()

    @property
    def verdict(self) -> str:
        """Return CONSISTENT, INCONSISTENT, or UNREAD."""
        if self.edges_read == 0:
            return UNREAD
        return INCONSISTENT if self.conflicts else CONSISTENT

    @property
    def code(self) -> int:
        """Return the exit code for this verdict."""
        return CODES[self.verdict]

    @property
    def solutions(self) -> int:
        """How many distinct consistent assignments exist — `2**components`, or 0 when refuted.

        ⚑⚑ NEVER 1, AND THAT IS THE POINT. A connected consistent graph has TWO solutions, swapped
        by the global sigma flip, because nothing in the graph says which end of the entailment the
        reader stands at. Reporting `1` would be claiming an absolute orientation the structure does
        not carry; reporting `2**c` with `c` beside it says exactly how much is undetermined.
        """
        return 0 if self.conflicts else 1 << self.components

    @property
    def unique_up_to_flip(self) -> bool:
        """Whether the whole graph is tied together — one component, so one free bit total."""
        return not self.conflicts and self.components == 1

    def summary(self) -> str:
        """Return the `n of m` line for this read."""
        return (
            f"chirality: {self.verdict} — {len(self.conflicts)} conflict(s) over "
            f"{self.edges_read} edge(s), {self.components} component(s) over "
            f"{self.nodes_read} node(s)"
        )


def normalise_sigma(edge: tuple[str, str, str]) -> tuple[str, str, str]:
    """Return `edge` in its sigma-free spelling — a sigma-mate becomes its partner, pair reversed.

    ⚑⚑⚑ ONE RELATION MUST BE ONE CONSTRAINT HOWEVER IT WAS SPELLED, and without this it was two
    contradictory ones. `SIGMA_MATE` records that `enables` reads a `rests-on` from the opposite
    endpoint, so `u enables v` denotes `v rests-on u` — and the walk was applying `enables`' bit at
    the UNSWAPPED pair, which inverts it. Measured on the worklist, where `A5-as rests-on
    A5-as-reach` and `A5-as-reach enables A5-as` are the same constraint stated from both ends and
    were reported as a conflict.

    ⚑ THE PAIR IS REVERSED EVEN THOUGH THE WALK IS UNDIRECTED. Only the bit changes the arithmetic,
    but a conflict row that cites an unnormalised direction sends the next reader after a spelling
    the corpus does not declare.
    """
    kind, source, target = edge
    partner = SIGMA_MATE.get(kind)
    return (kind, source, target) if partner is None else (partner, target, source)


def fold_tau_pairs(
    edges: Iterable[tuple[str, str, str]],
) -> tuple[tuple[str, str, str], ...]:
    """Return `edges` sigma-seated, each DECLARED tau-mate pair folded to the one dart it names.

    ⚑⚑⚑ A TAU-MATE IS A SECOND NAME FOR ONE DART, AND `derive` ALREADY SAID SO: *"the closure names
    the missing TAU-MATE: the same relation to the same target, read from the opposite chirality"*,
    returning None when it is already declared because **the closure is then COMPLETE**.
    `_adjacency` read those two edges as two independent constraints with opposite bits, so every
    completed closure in the corpus refuted the graph. The solver and the closure disagreed about
    one relation, and the closure was right.

    ⚑⚑⚑ AND THE FIRST CUT COLLAPSED FAR TOO MUCH — CAUGHT BY THIS CASE'S OWN CONTROL. It re-spelled
    EVERY predictor edge as its completer mate, so nothing anywhere carried bit 1, no graph could
    refute, and the suite went from one failure to eight. **A tau pair is one dart only when BOTH
    spellings are declared on the same pair**; a lone `from` is a genuine predictor dart and keeps
    its bit. The fold is a property of the EDGE SET, not of an edge — which is exactly why it
    cannot live in the per-edge normaliser beside `normalise_sigma`.

    ⚑⚑ OPERATOR, SETTLING WHAT THIS READER WAS ABOUT TO DECIDE WRONGLY: *"All chain edges are. The
    DAG is a lattice of darts."* The repair proposed instead — filtering document-chain `from`
    edges out of the parity graph — would have removed real darts and called the result consistent.
    **A false green bought by deleting evidence.**

    ⚑ TAU REVERSES THE READING, NOT THE ENDPOINTS. So `rests-on u v` beside `from v u` folds, while
    `rests-on u v` beside `from u v` does NOT — same orientation, two distinct constraints, and it
    must still refute.
    """
    seated = [normalise_sigma(edge) for edge in edges]
    present = set(seated)
    folded: list[tuple[str, str, str]] = []
    for kind, source, target in seated:
        mate = TAU_MATE.get(kind)
        # ⚑ THE PREDICTOR HALF IS THE ONE DROPPED, so the surviving spelling is deterministic and a
        # fold cannot depend on declaration order.
        if mate is not None and KIND_CHIRALITY.get(kind) == 1 and (mate, target, source) in present:
            continue
        folded.append((kind, source, target))
    return tuple(folded)


def _adjacency(
    edges: Iterable[tuple[str, str, str]],
    table: Mapping[str, int],
) -> tuple[dict[str, list[tuple[str, int, str]]], list[str], int]:
    """Return the undirected walk structure, the kinds absent from `table`, and the edge count.

    ⚑ AN UNKNOWN KIND IS CARRIED, NOT DEFAULTED SILENTLY. A kind the table does not name is walked
    as chirality 0, which is a GUESS; it is returned so the report can say the reader may be the
    defect — the third arm of the three-way verdict, made reachable rather than rhetorical.
    """
    adjacency: dict[str, list[tuple[str, int, str]]] = {}
    unknown: list[str] = []
    count = 0
    # ⚑ THE UNKNOWN CHECK READS THE DECLARED KIND, because a spelling the table does not name must
    # be confessed as AUTHORED, not as whatever it normalised to.
    declared_edges = list(edges)
    for declared in declared_edges:
        count += 1
        if declared[0] not in table and declared[0] not in unknown:
            unknown.append(declared[0])

    # ⚑⚑ THE DENOMINATOR COUNTS DECLARED EDGES AND THE WALK USES FOLDED ONES — deliberately.
    # `edges_read` answers *how much of the corpus was read*, so folding two spellings of one dart
    # must not make the population look smaller than what the author actually wrote.
    for kind, source, target in fold_tau_pairs(declared_edges):
        bit = table.get(kind, 0)
        adjacency.setdefault(source, []).append((target, bit, kind))
        adjacency.setdefault(target, []).append((source, bit, kind))
    return adjacency, unknown, count


def _cycle_through(parent: Mapping[str, str], here: str, there: str) -> tuple[str, ...]:
    """Return the nodes of the odd cycle closed by the edge `here`—`there`.

    ⚑⚑ THE CYCLE IS THE TREE PATHS UP TO THE COMMON ANCESTOR, PLUS THE CLOSING EDGE — never the
    component. A refuted graph may have an arbitrarily long tail hanging off its odd cycle, and
    reporting the component would make every conflict in a connected graph look identical, which is
    the count's failure restated as a set.

    ⚑ THE ANCESTOR IS FOUND BY WALKING ONE SIDE TO THE ROOT AND THEN THE OTHER UNTIL IT MEETS THAT
    path — both endpoints are in the same BFS tree by construction, since a conflict is only
    recorded when both are already coloured.
    """
    climb: list[str] = [here]
    while climb[-1] in parent:
        climb.append(parent[climb[-1]])
    seen = {node: rank for rank, node in enumerate(climb)}

    other: list[str] = [there]
    while other[-1] not in seen and other[-1] in parent:
        other.append(parent[other[-1]])
    meet = other[-1]
    return (*climb[: seen.get(meet, len(climb) - 1) + 1], *reversed(other[:-1]))


def solve(
    edges: Iterable[tuple[str, str, str]],
    nodes: Iterable[str] = (),
    table: Mapping[str, int] | None = None,
) -> Assignment:
    """Solve for the perspective assignment a graph's edge kinds force, or report what refutes it.

    `edges` are `(kind, source, target)` triples; `nodes` widens the population so that entries
    carrying NO edge are still counted in the denominator.

    ⚑ ISOLATED NODES ARE POPULATION, NOT COMPONENTS. An entry with no edge constrains nothing, so
    counting it as a component would inflate `solutions` with bits that are not choices about
    chirality at all. It is counted in `nodes_read` and given perspective 0.
    """
    pinned = KIND_CHIRALITY if table is None else table
    adjacency, unknown, edges_read = _adjacency(edges, pinned)

    perspective: dict[str, int] = {}
    conflicts: list[Conflict] = []
    components = 0

    # ⚑⚑⚑ ONE VIOLATED CONSTRAINT IS ONE CONFLICT, AND WITHOUT THIS IT WAS TWO. `_adjacency` stores
    # every edge in BOTH directions — correct, because `phi(u) XOR phi(v) == k` is symmetric — so
    # the walk meets each edge once from each endpoint. Recording on every meeting reported a
    # single unsatisfiable edge twice, and the live worklist read `58 conflict(s) over 125 edge(s)`
    # from an undirected population that cannot double that way.
    #
    # ⚑⚑ THE COST WAS THE THREE-WAY VERDICT ITSELF. A red whose MEMBERS are duplicated cannot be
    # partitioned into genuinely-inconsistent / sigma-shifted / reader-defect, because every arm is
    # inflated by an unknown factor — so the instrument built to keep those three separable was
    # collapsing them. **A false RED banks exactly as confidently as a false green.**
    #
    # ⚑ THE KEY IS THE UNORDERED PAIR, NOT THE EDGE'S DECLARED DIRECTION. A pair may carry several
    # declared edges of different kinds (`OBS-DEADLINE from OBS` alongside `enables OBS`), and those
    # are genuinely distinct constraints on one pair — but each must report once, from whichever end
    # the walk reached first. `seen` is keyed on (pair, kind) for exactly that reason.
    seen: set[tuple[frozenset[str], str]] = set()
    # ⚑ THE SPANNING TREE, KEPT SO THE ODD CYCLE CAN BE RECOVERED. Without it a conflict knows only
    # the edge that closed it, and the implicated set — the thing that partitions the three-way
    # verdict — is discarded at the moment it is computed.
    parent: dict[str, str] = {}

    for start in sorted(adjacency):
        if start in perspective:
            continue
        components += 1
        perspective[start] = 0
        frontier = [start]
        while frontier:
            here = frontier.pop()
            for there, bit, kind in adjacency[here]:
                wanted = perspective[here] ^ bit
                if there not in perspective:
                    perspective[there] = wanted
                    parent[there] = here
                    frontier.append(there)
                elif perspective[there] != wanted:
                    mark = (frozenset((here, there)), kind)
                    if mark in seen:
                        continue
                    seen.add(mark)
                    conflicts.append(
                        Conflict(
                            kind=kind,
                            source=here,
                            target=there,
                            source_perspective=perspective[here],
                            target_perspective=perspective[there],
                            cycle=_cycle_through(parent, here, there),
                        )
                    )

    population = dict.fromkeys(sorted(nodes), 0)
    population.update(perspective)
    return Assignment(
        perspective=population,
        conflicts=tuple(conflicts),
        components=components,
        nodes_read=len(population),
        edges_read=edges_read,
        unknown_kinds=tuple(unknown),
    )


def derive(
    assignment: Assignment,
    key: str,
    have: Sequence[tuple[str, str]],
    mates: Mapping[str, str] | None = None,
) -> tuple[str, str] | None:
    """Return the `(kind, target)` dart the closure constructs for `key`, or None when it cannot.

    `have` is the edges `key` already declares, as `(kind, target)`. The closure names the missing
    TAU-MATE: the same relation to the same target, read from the opposite chirality, spelled by
    `TAU_MATE` rather than inferred from a bit.

    ⚑⚑ THIS DERIVES, IT DOES NOT DECIDE. When the graph does not force one answer — the assignment
    is refuted, the endpoints are not both placed, the mate is already declared, or the entry's
    mated darts name more than one target — this returns None rather than picking. A hand-decided
    direction is exactly the local reading the module exists to refuse.
    """
    pairing = TAU_MATE if mates is None else mates
    if assignment.conflicts or not have:
        return None
    declared = {(kind, target) for kind, target in have}
    wanted = {
        (pairing[kind], target)
        for kind, target in declared
        if kind in pairing and (pairing[kind], target) not in declared
    }
    if len(wanted) != 1:
        return None
    mate_kind, target = wanted.pop()
    phi = assignment.perspective
    if key not in phi or target not in phi:
        return None
    return (mate_kind, target)


def render(assignment: Assignment) -> tuple[str, ...]:
    """Return the report lines for one solved graph, causes included when it is refuted."""
    lines: list[str] = []
    if assignment.verdict == UNREAD:
        lines.append("⚠ no edges read — this is a fact about the INPUT, not about the graph")
    lines.extend(c.line() for c in assignment.conflicts)
    if assignment.conflicts:
        lines.append(
            "⚑ a no-consistent-assignment verdict is THREE-WAY, and this reader "
            "does not choose between:"
        )
        lines.extend(f"    - {cause}" for cause in AMBIGUOUS_CAUSES)
    elif assignment.verdict == CONSISTENT:
        scope = "the whole graph" if assignment.unique_up_to_flip else "each component separately"
        lines.append(
            f"⚑ {assignment.solutions} consistent assignment(s) — unique up to the global "
            f"sigma flip, over {scope}"
        )
        if not assignment.unique_up_to_flip:
            lines.append(
                "⚑ MORE THAN ONE COMPONENT IS THE FINDING: the graph does not tie its "
                "segments to each other, so their relative chirality is undetermined."
            )
    if assignment.unknown_kinds:
        lines.append(
            "⚑ edge kind(s) absent from the chirality table, walked as 0 (a GUESS — the "
            "reader may be the defect): " + ", ".join(assignment.unknown_kinds)
        )
    lines.append(assignment.summary())
    return tuple(lines)
