#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""May a consumed barrel be deleted - the decision, with both predicates' answers supplied.

THE ELEVENTH CUT OF THE DRAIN'S FOURTH FILE (`scratch/split_pipeline.py:613-694`, W4 tick 52):
the decision half of `retire`, stage 7 of the split. The stage exists because its absence left
a barrel mis-labelled for a day: `rewire_only` moves consumers onto the leaves and sweeps, but
never retires the file, so after a successful rewire the barrel STILL STANDS, still declares
its names, and shows up in the census as a duplicate of its own leaf. Eight barrels were once
retired by hand-checking each precondition and running `rm`; that judgement is what a stage
owns, and this module is the judgement without the `rm`.

TWO PREDICATES, BOTH MUST PASS, AND NEITHER IS RE-DERIVED HERE. Zero LIVE references
(`check_indented_imports.sweep`, the verifier the pipeline already trusts - it sees the
`where open import` class a column-0 scan structurally cannot) and every declared name COVERED
by a leaf (`collapse_carrier_nesting.classify_occupied`). Zero references alone is not enough:
an unreferenced module that still owns a name is dead code to investigate, not a barrel to
delete. The caller runs both predicates and hands their answers in; this module orders the
refusals and names each one, so the operator is sent to the right next command.

TWO OF THE ORIGIN'S READINGS ARE KEPT AS RULES. "Already retired" is NOT "already settled":
an absent file still owes the derived-artifact refresh, so re-running CONVERGES instead of
no-op'ing. And a directory's existence is not its content: an empty leaf directory is an
abandoned or renamed split, never a retirable barrel.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# One live reference as the sweep reports it: (path, line, kind, text).
Hit = tuple[str, int, str, str]
# How many hits or uncovered names a refusal lists before eliding.
LIST_CAP = 20
NAME_CAP = 10


@dataclass(frozen=True)
class Inputs:
    """The five facts the decision reads, gathered by the caller."""

    exists: bool
    hits: tuple[Hit, ...] = ()
    has_leaf_dir: bool = False
    leaves: tuple[str, ...] = ()
    # `classify_occupied`'s answer: (kind, uncovered names); None when it was not consulted.
    occupied: tuple[str, tuple[str, ...]] | None = None


@dataclass(frozen=True)
class Verdict:
    """What to do: refresh only, refuse with a reason, or delete then refresh."""

    action: str
    lines: list[str] = field(default_factory=list)
    remedy: str | None = None


ALREADY_RETIRED = "already-retired"
REFUSE = "refuse"
DELETE = "delete"


def _live(modname: str, hits: tuple[Hit, ...]) -> Verdict:
    """Refuse: consumers still reach the barrel - rewire them first."""
    lines = [f"✗ {len(hits)} LIVE reference(s) — not dead yet:"]
    lines.extend(f"   [{kind}] {p}:{i}: {line.strip()}" for p, i, kind, line in hits[:LIST_CAP])
    if len(hits) > LIST_CAP:
        lines.append(f"   … {len(hits) - LIST_CAP} more")
    return Verdict(
        REFUSE,
        lines,
        f"rewire them first:  python3 scratch/split_pipeline.py {modname} --rewire-only --apply",
    )


def _refuse(*lines: str) -> Verdict:
    """Refuse with the given lines."""
    return Verdict(REFUSE, list(lines))


def _leaves_verdict(modname: str, leafdir: str, inp: Inputs) -> Verdict | None:
    """Refuse on the leaf directory's absence, emptiness, or an unconsulted coverage."""
    if not inp.has_leaf_dir:
        return _refuse(
            f"{leafdir}/ does not exist — {modname} has no leaves, so it is not a "
            f"consumed barrel.  Nothing here to retire."
        )
    if not inp.leaves:
        return _refuse(
            f"{leafdir}/ is EMPTY — a directory's existence is not its content; "
            f"this is an abandoned or renamed split, not a retirable barrel."
        )
    if inp.occupied is None:
        return _refuse(f"{modname}: coverage not consulted — cannot say the barrel owns nothing")
    return None


def verdict(modname: str, rel: str, inp: Inputs) -> Verdict:
    """Order the refusals: absent, live, no leaves, empty leaves, still owning, else delete."""
    if not inp.exists:
        return Verdict(ALREADY_RETIRED, [f"{modname}: already retired (no {rel})"])
    if inp.hits:
        return _live(modname, inp.hits)
    refused = _leaves_verdict(modname, rel.removesuffix(".agda"), inp)
    if refused is not None:
        return refused
    kind, uncovered = inp.occupied or ("", ())
    if kind != "barrel":
        lines = [f"✗ {modname} still OWNS {len(uncovered)} name(s) no leaf provides:"]
        lines.extend(f"     {n}" for n in uncovered[:NAME_CAP])
        lines.append(
            "this is a REAL MODULE, not a consumed barrel — deleting it would lose a definition."
        )
        return Verdict(REFUSE, lines)
    covered = f"✓ every name it declares is covered by a leaf ({len(inp.leaves)} leaves)."
    return Verdict(DELETE, ["✓ zero live references.", covered])
