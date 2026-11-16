# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Order monoliths for decomposition: biggest first, unless a smaller file blocks it.

⚑⚑⚑ THE OPERATOR'S PRIORITY IS THE INVERSE OF THE DRAIN'S. A drain ranking asks what cleaning
a file RELEASES and therefore puts cheap high-release files first; decomposition asks what
carries the most debt and puts the MONOLITH first. Both orderings are honest and they disagree
almost everywhere, which is why this is a separate module rather than a flag on the other one:
a single ranker with a direction switch would let a caller read one ordering's rationale off
the other's output.

⚑⚑ AND THE "UNLESS BLOCKED" CLAUSE IS THE SUBSTANTIVE HALF, not a caveat. A monolith whose
decomposition requires editing a smaller file cannot be started until that file moves, so the
ordering must DEMOTE it behind its blocker rather than reporting it as the head and leaving the
operator to discover the wall. A ranking that named an unstartable file first would be
precisely the plan-that-cannot-begin this repo files against elsewhere.

⚑ BLOCKING IS AN IMPORT EDGE INTO A DIRTY FILE, and that is narrower than "depends on". If A
imports B at module scope and B is itself uneditable, then extracting anything from A that
touches B's surface needs B to be editable first. A deferred import does NOT block: it fires
only when called, so A can be decomposed without B moving. The distinction is `import_edges`'s
to make, and reading it as one relation would over-report blocking and stall everything.

⚑⚑ THE ORDER IS A TOPOLOGICAL ONE OVER SIZE, NOT A SORT WITH AN EXCEPTION. Sorting by size and
then patching the blocked rows down is order-dependent and produces different answers for
different starting orders; emitting a blocker before everything it blocks, largest-first within
what is available, is well-defined and stable. A cycle cannot be ordered that way and is
reported as a cycle rather than broken arbitrarily.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Monolith:
    """One dirty file, its debt, and the dirty files it must wait for."""

    path: str
    findings: int
    blocked_by: tuple[str, ...] = field(default_factory=tuple)

    @property
    def startable(self) -> bool:
        """Whether decomposition can begin on this file today."""
        return not self.blocked_by


def blockers_of(path: str, imports: dict[str, set[str]], dirty: set[str]) -> tuple[str, ...]:
    """Return the dirty files `path` imports at module scope, sorted.

    ⚑ A FILE NEVER BLOCKS ITSELF. A self-edge would make every file unstartable and the
    ordering empty — the failure mode that reads as "nothing can be done" when the truth is
    a reader counting a trivial cycle.
    """
    return tuple(sorted(dep for dep in imports.get(path, set()) if dep in dirty and dep != path))


def _largest_ready(remaining: dict[str, int], ready: list[str]) -> str:
    """Return the biggest of the emittable files, ties broken by path.

    ⚑ THE PAIRS ARE MATERIALISED RATHER THAN COMPARED BY A CLOSURE. A `key=` lambda closing
    over the dict is untyped at the boundary, and this module's whole job is to produce an
    order a reader can trust — the comparison is the wrong place to carry an unchecked shape.
    """
    return max((remaining[p], p) for p in ready)[1]


def order(files: dict[str, int], imports: dict[str, set[str]]) -> list[Monolith]:
    """Return the decomposition order: largest first, a blocker before what it blocks.

    `files` maps a dirty file to its finding count; `imports` maps a file to the files it
    imports at module scope.

    ⚑⚑ THE LOOP EMITS THE LARGEST FILE WHOSE BLOCKERS HAVE ALL BEEN EMITTED. That is a
    topological order refined by size rather than a size sort with corrections, so the result
    does not depend on the input's ordering and two runs over an unchanged tree agree.

    ⚑ A CYCLE STOPS PROGRESS AND IS REPORTED, NOT BROKEN. When nothing is emittable and files
    remain, every survivor is in or behind a cycle; they are appended largest-first with their
    blockers intact, so a reader sees WHY they could not be ordered instead of receiving an
    arbitrary linearisation that hides it.
    """
    dirty = set(files)
    remaining = dict(files)
    emitted: set[str] = set()
    out: list[Monolith] = []

    while remaining:
        ready = [p for p in remaining if all(b in emitted for b in blockers_of(p, imports, dirty))]
        if not ready:
            break
        pick = _largest_ready(remaining, ready)
        out.append(Monolith(pick, remaining[pick], blockers_of(pick, imports, dirty)))
        emitted.add(pick)
        del remaining[pick]

    # ⚑ THE SURVIVORS ARE CYCLE MEMBERS. Reporting them with their blockers is the honest
    # form: the ordering could not place them, and saying so beats inventing a position.
    stuck = sorted((-n, p) for p, n in remaining.items())
    out.extend(Monolith(p, remaining[p], blockers_of(p, imports, dirty)) for _neg, p in stuck)
    return out


def cycles(ordered: list[Monolith]) -> list[Monolith]:
    """Return the rows the ordering could not place — those still blocked when emitted.

    ⚑ A ROW IS UNPLACED WHEN IT CARRIES BLOCKERS THAT APPEAR LATER. Everything the topological
    pass emitted had its blockers already out, so a late blocker is the signature of the pass
    having given up.

    ⚑⚑⚑ AND THIS RETURNS MORE THAN THE CYCLE — THE NAME OVERCLAIMS, MEASURED. A file that
    merely SITS BEHIND a cycle also carries a late blocker, so it appears here while being on
    nobody's cut list. Live: twelve rows came back, of which two (`gate_census` at 741 findings
    and `build_census` at 389) carry NO edge to another member — an order of magnitude cheaper
    than the rest, and stranded rather than knotted. A reader taking this list as "the cycle"
    would weigh a cut against files that are not in it.

    ⚑ THE TRUE MEMBERS ARE THE ROWS WITH AN EDGE TO ANOTHER UNPLACED ROW, which `knot` returns.
    Both readings are wanted — the unplaced set is what the ordering could not schedule, the
    knot is what must be cut — and conflating them sends the cut at the wrong file.

    ⚑⚑⚑ THE UNPLACED SET IS FOUND BY REPLAYING THE PASS, NOT BY COMPARING EMITTED POSITIONS.
    A position test asks "does a blocker appear later", which is FALSE for most of a cycle: in
    a two-file knot the second member's blocker sits at index 0, earlier, so only one of the
    two was ever flagged. MEASURED: a live run reported twelve rows where the position test
    happened to fire, and a three-file fixture returned exactly one of its three. Replaying the
    emission — which rows had every blocker already out — is the question the pass itself
    answered, so it cannot disagree with the pass.
    """
    emitted: set[str] = set()
    unplaced: list[Monolith] = []
    for row in ordered:
        if all(b in emitted for b in row.blocked_by):
            emitted.add(row.path)
        else:
            unplaced.append(row)
    return unplaced


def knot(ordered: list[Monolith]) -> list[Monolith]:
    """Return the unplaced rows that block EACH OTHER — the cycle proper.

    ⚑ A ROW STRANDED BEHIND A CYCLE IS NOT IN IT, and only this distinction makes a cut
    decidable: cutting a stranded file frees nothing, because the knot it waits on is still
    tied. Membership is therefore MUTUAL REACHABILITY — a row that can reach itself by
    following blockers — not merely "has an unplaced blocker".

    ⚑⚑ AND "HAS AN UNPLACED BLOCKER" IS NOT ENOUGH, WHICH A FIXTURE CAUGHT. A stranded file's
    blocker IS unplaced (it is in the knot), so that weaker test admits the stranded file too
    and returns the same set as `cycles`. The distinction the caller needs — who must be cut —
    survives only under reachability.
    """
    rows = {m.path: m for m in cycles(ordered)}
    edges = {p: [b for b in m.blocked_by if b in rows] for p, m in rows.items()}

    def reaches_self(start: str) -> bool:
        """Whether following blockers from `start` returns to `start`."""
        seen: set[str] = set()
        todo = list(edges.get(start, []))
        while todo:
            node = todo.pop()
            if node == start:
                return True
            if node in seen:
                continue
            seen.add(node)
            todo.extend(edges.get(node, []))
        return False

    return [m for p, m in rows.items() if reaches_self(p)]


def hub(ordered: list[Monolith]) -> str:
    """Return the knot member the most other members wait on, or empty when none.

    ⚑ THE MOST-DEPENDED-ON MEMBER IS THE CHEAPEST CUT, because breaking it frees every row
    that waits on it at once. This reports the candidate; whether the cut is feasible is a
    judgement about the file, which no ordering can make.
    """
    members = knot(ordered)
    counts: dict[str, int] = dict.fromkeys({m.path for m in members}, 0)
    for member in members:
        for blocker in member.blocked_by:
            if blocker in counts:
                counts[blocker] += 1
    if not counts:
        return ""
    return max((n, p) for p, n in counts.items())[1]


def render(ordered: list[Monolith], show: int = 25) -> str:
    """Render the decomposition order, largest-first within what is startable."""
    stuck = cycles(ordered)
    head = (
        f"{len(ordered)} dirty file(s), decomposition order "
        f"(largest first, blockers ahead of what they block)"
    )
    out = [head, ""]
    out.append(f"  {'findings':>8}  {'blocked by':>10}  file")
    for m in ordered[:show]:
        mark = "—" if m.startable else str(len(m.blocked_by))
        out.append(f"  {m.findings:>8}  {mark:>10}  {m.path}")
        out.extend(f"              waits on: {b}" for b in m.blocked_by)
    if len(ordered) > show:
        out.append(f"  … {len(ordered) - show} more")
    if stuck:
        out.append(
            f"\n  ⚑ {len(stuck)} file(s) sit in an import CYCLE among dirty files — "
            f"the ordering could not place them, and one of them must be cut first."
        )
    return "\n".join(out) + "\n"
