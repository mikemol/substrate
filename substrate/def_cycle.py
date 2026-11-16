# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Check whether a file-level import cycle is a def cycle or an artifact of co-location.

⚑⚑⚑ THE ANSWER DECIDES EXTRACT-VERSUS-CUT, AND THE TWO ARE NOT VARIANTS OF EACH OTHER. Cutting
an edge REMOVES a dependency someone genuinely has; extraction RELOCATES a shared definition so
no caller loses anything. Operator: *"def-level cycles can't possibly execute properly, so
decomposition should work — and even be the preferable solution."* That makes extraction the
default rather than the alternative.

⚑⚑ SO A FILE CYCLE WITH AN ACYCLIC DEF GRAPH IS ALWAYS RESOLVABLE BY LIFTING. MEASURED on this
repo's census knot: `gate_census.selftest` reaches `check_baseline_health.census`, and five defs
in `check_baseline_health` reach `gate_census.baseline_health` — a CHAIN, no def reaching
itself. The mutual file dependency exists only because `baseline_health` and `selftest` share a
file. Lift one and the cycle becomes a DAG with every dependency intact.

⚑⚑⚑ AND A REPORTED DEF-LEVEL CYCLE IS A DEFECT IN THIS READER, NOT A LEGITIMATE VERDICT.
Operator: *"If we detect a def-level cycle, that's a bug in our detector."* The argument is
sound by construction — a genuine cycle among module-scope definitions cannot execute, because
Python evaluates a module top to bottom and the second definition would reference a name that
does not yet exist. So whatever a reported cycle IS, it is not a running one, and the honest
verdicts are ARTIFACT (lift it and the graph becomes a DAG) or SUSPECT (this reader found
something it cannot justify, and the shape needs unrolling).

⚑ THE USUAL CULPRIT IS CALL-TIME RESOLUTION. `def f(): return g()` beside `def g(): return f()`
is a cycle in a reference graph and no cycle at all in execution — neither body runs at import,
and by call time both names are bound. A reader that called that a def cycle would be reporting
a property of its own graph as a property of the program. Naming it SUSPECT keeps the finding
without dressing it as a verdict about the code.

⚑ THE REACH TEST IS DELIBERATELY COARSE, AND ITS DIRECTION OF ERROR IS STATED. It matches a
def's used NAMES against the other file's def names, so a merely-shared spelling reads as an
edge. That OVER-reports, which makes SUSPECT more likely than ARTIFACT — the safe direction,
since a false suspect costs a look while a false artifact licenses an extraction that leaves
the knot tied.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass

from substrate import corpus

#: No def reaches itself — the file cycle exists only because defs share a file.
CO_LOCATION = "co-location"

#: This reader found a def reaching itself, which cannot execute at module scope.
#: ⚑ A FINDING ABOUT THE READER, NOT A VERDICT ABOUT THE CODE.
SUSPECT = "suspect"

#: The pair is not mutually dependent at def level at all — one direction has no edges.
#: ⚑ NOT A CYCLE, SO NOTHING TO LIFT. A first cut classified these as artifacts and then
#: rendered `LIFT one of: (none reached)` — a recommendation naming nothing, which reads as a
#: verdict and is an admission. If one direction is empty the file edge came from somewhere
#: this reader is not looking (a bare-name import, a runtime lookup), and saying so beats
#: proposing an extraction with no subject.
NOT_MUTUAL = "not-mutual"


@dataclass(frozen=True, slots=True)
class Verdict:
    """What kind of cycle a pair of files carries."""

    kind: str
    edges: tuple[tuple[str, str], ...]
    shared: tuple[str, ...] = ()

    @property
    def is_artifact(self) -> bool:
        """Whether lifting a shared definition would resolve this cycle."""
        return self.kind == CO_LOCATION

    @property
    def needs_investigation(self) -> bool:
        """Whether this reader produced something it cannot justify.

        ⚑ A SUSPECT IS NOT A CUT INSTRUCTION. It says the graph shows a loop the language
        would not have executed, so the shape — most often call-time resolution — has to be
        unrolled before anything is decided.
        """
        return self.kind == SUSPECT


def top_level_defs(rel: str) -> dict[str, ast.AST]:
    """Return the top-level definitions of `rel`, by name.

    ⚑ TOP LEVEL ONLY. A method is reached through its class, so the class is the unit a lift
    moves; treating methods as movable would propose an extraction nobody can perform without
    also moving their class.
    """
    try:
        tree = ast.parse((corpus.ROOT / rel).read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return {}
    return {
        n.name: n
        for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }


def names_used(node: ast.AST) -> set[str]:
    """Return every name a definition reaches — bare names and attribute leaves.

    ⚑ ATTRIBUTE LEAVES MATTER because a cross-file call is spelled `peer.census()`, and a
    reader collecting only bare names would see the receiver and miss the callee — reporting
    no edge exactly where the dependency is.
    """
    out: set[str] = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Attribute):
            out.add(sub.attr)
        elif isinstance(sub, ast.Name):
            out.add(sub.id)
    return out


def def_edges(a_rel: str, b_rel: str) -> list[tuple[str, str]]:
    """Return `(a_def, b_def)` for every definition in `a_rel` reaching one in `b_rel`."""
    a_defs, b_defs = top_level_defs(a_rel), top_level_defs(b_rel)
    return [
        (name, hit)
        for name, node in sorted(a_defs.items())
        for hit in sorted(names_used(node) & set(b_defs))
    ]


def _reaches(start: str, target: str, reach: dict[str, set[str]]) -> bool:
    """Whether `target` is reachable from `start` by following def edges."""
    seen: set[str] = set()
    todo = list(reach.get(start, ()))
    while todo:
        node = todo.pop()
        if node == target:
            return True
        if node in seen:
            continue
        seen.add(node)
        todo.extend(reach.get(node, ()))
    return False


def classify(a_rel: str, b_rel: str) -> Verdict:
    """Return whether the cycle between two files is an artifact or a suspect reading.

    ⚑⚑ THE TEST IS WHETHER ANY DEF REACHES ITSELF across the pair. Two one-way chains in
    opposite directions are not a cycle — `x → y` in one file and `p → q` in the other look
    mutual at file granularity and compose to nothing at def granularity. Reading the file
    edge as the def edge is exactly the collapse this module exists to undo.
    """
    forward = def_edges(a_rel, b_rel)
    backward = def_edges(b_rel, a_rel)

    reach: dict[str, set[str]] = {}
    for src, dst in forward:
        reach.setdefault(f"a:{src}", set()).add(f"b:{dst}")
    for src, dst in backward:
        reach.setdefault(f"b:{src}", set()).add(f"a:{dst}")

    looping = [n for n in reach if _reaches(n, n, reach)]
    edges = (*forward, *backward)
    if looping:
        return Verdict(SUSPECT, edges, tuple(sorted(looping)))
    # ⚑ AN EMPTY DIRECTION IS NOT A CYCLE. Classifying it as an artifact produced a lift
    # recommendation naming nothing, which reads as advice and is an admission that the file
    # edge came from somewhere this reader cannot see.
    if not forward or not backward:
        return Verdict(NOT_MUTUAL, edges)
    # ⚑ THE SHARED DEFS ARE THE LIFT CANDIDATES — what the other file actually reaches.
    return Verdict(CO_LOCATION, edges, tuple(sorted({dst for _src, dst in backward})))


def render(a_rel: str, b_rel: str, verdict: Verdict) -> str:
    """Render the verdict and what it licenses."""
    out = [f"{a_rel}  <->  {b_rel}", f"  verdict: {verdict.kind}"]
    out.extend(f"    {src} -> {dst}" for src, dst in verdict.edges)
    if verdict.kind == NOT_MUTUAL:
        out.append(
            "  ⚑ NOT MUTUAL at def level — one direction carries no edges, so there "
            "is no cycle here to lift."
        )
        out.append(
            "  ⚑ The file edge came from something this reader does not see — a "
            "bare-name import or a runtime lookup. Find it before acting."
        )
    elif verdict.is_artifact:
        out.append(
            "  ⚑ ARTIFACT — no def reaches itself, so the file cycle exists only "
            "because these share a file."
        )
        out.append(
            f"  ⚑ LIFT one of: {', '.join(verdict.shared) or '(none reached)'}"
            " into its own module and the cycle becomes a DAG with every "
            "dependency intact."
        )
    else:
        out.append(f"  ⚑ SUSPECT — this reader shows a loop through: {', '.join(verdict.shared)}")
        out.append(
            "  ⚑ A module-scope def cycle CANNOT EXECUTE, so this is a defect in "
            "the reading, not a property of the code. Unroll the shape — most "
            "often call-time resolution — before deciding anything."
        )
    return "\n".join(out) + "\n"
