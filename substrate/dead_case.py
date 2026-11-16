#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Find suite cases that cannot fail — a green row asserting nothing.

⚑⚑⚑ WHY THIS EXISTS, AND IT WAS FOUND BY HAND THREE TIMES BEFORE IT WAS MECHANIZED
(gate-G21, gate-G22, gate-G23). A case in this repo is a `(prose, expr)` tuple, and a case
whose `expr` is a LITERAL cannot fail for any reason connected to the module under test. It
prints green, occupies a slot in the `n/m`, and reads as a control.

⚑⚑ THE TEMPLATE IS THE CAUSE, NOT CARELESSNESS. Every `_live_cases` opens with an early
return reporting an absent fixture, then opens its success list with the SAME ROW SPELLED THE
SAME WAY — `("<fixture> is present", True)`. After the early return that row is unreachable
as a failure. Three of three audited arms carried it, because the failure list names the
fixture and symmetry suggests the success list should too. **Presence is a PRECONDITION of
the arm, not one of its findings.**

⚑ AND A PEER FOUND THE DEEPER FORM FIRST: a control validates ONE predicate, so a changed
predicate ORPHANS it in place while it keeps printing. A literal-True case is that with the
predicate removed entirely — it validates nothing and never did.

⚑⚑⚑ WHAT THIS DOES NOT CLAIM, STATED SO A GREEN IS NOT OVER-READ. A case whose expression is
a CALL may still be unfailable — `("x", isinstance(x, object))` is a literal in disguise, and
nothing here can see it. This reports the shapes it can decide and counts the rest as
UNDECIDED rather than clean, because a reader that called them clean would be the defect it
is built to find, one level up.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import corpus

if TYPE_CHECKING:
    from pathlib import Path

# How many rows to spell out before summarising. The counts are always stated.
SAMPLE = 12

# A case is a two-element tuple: the prose, then the truth value.
_CASE_ARITY = 2


@dataclass(frozen=True, slots=True)
class Case:
    """One case, and whether this reader could decide that it can fail."""

    suite: str
    func: str
    prose: str
    verdict: str

    @property
    def dead(self) -> bool:
        """Whether this case cannot fail."""
        return self.verdict == "literal"

    @property
    def undecided(self) -> bool:
        """Whether this reader could not decide — a fact about the reader."""
        return self.verdict == "undecided"


def _prose_of(node: ast.expr) -> str:
    """Return a case's prose, or a placeholder when it is not a plain string."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return "<computed prose>"


def _verdict(node: ast.expr) -> str:
    """Classify a case's truth expression, or refuse the tuple as not-a-case.

    ⚑ ONLY A BOOLEAN LITERAL IS CALLED DEAD, and the narrowing is MEASURED rather than
    fastidious. The first cut called every `ast.Constant` dead and reported 80 across the
    tree — but `("rests-on", "from")` in a bib fixture is a two-element tuple of strings,
    matches the arity, and was classified `literal`. **A false POSITIVE population, carried
    with an instrument's authority, is the census-green defect inverted**: the three
    hand-found instances were real and the number around them was not.

    ⚑ SO A NON-BOOLEAN CONSTANT IN THE TRUTH SLOT MEANS THE TUPLE IS DATA, not a case that
    cannot fail. A NAME alone is UNDECIDED, because deciding it needs the binding traced and
    this reader does not trace bindings. Everything else is live.
    """
    if isinstance(node, ast.Constant):
        return "literal" if isinstance(node.value, bool) else "not-a-case"
    if isinstance(node, ast.Name):
        return "undecided"
    return "live"


def _case_pairs(node: ast.AST) -> list[tuple[str, str]]:
    """Return `(prose, verdict)` for the case tuples directly inside one list or tuple.

    ⚑ TAKES `AST` RATHER THAN `expr` BECAUSE `ast.walk` YIELDS `AST`, and narrowing at the
    call site would put an isinstance check in the caller that this function already makes.
    One guard, in the place that uses it.
    """
    if not isinstance(node, (ast.List, ast.Tuple)):
        return []
    out: list[tuple[str, str]] = []
    for elt in node.elts:
        if not isinstance(elt, ast.Tuple) or len(elt.elts) != _CASE_ARITY:
            continue
        if not isinstance(elt.elts[0], (ast.Constant, ast.JoinedStr)):
            continue
        verdict = _verdict(elt.elts[1])
        # ⚑ A REFUSED TUPLE IS NOT A CASE THIS READER DECLINED TO CLASSIFY — it is not a case.
        #   Counting it as UNDECIDED would move a false positive into the honest-gap column
        #   rather than removing it.
        if verdict == "not-a-case":
            continue
        out.append((_prose_of(elt.elts[0]), verdict))
    return out


def _cases_in(func: ast.FunctionDef) -> list[tuple[str, str]]:
    """Return `(prose, verdict)` for every case tuple this function builds."""
    return [pair for node in ast.walk(func) for pair in _case_pairs(node)]


def read_source(src: str, suite: str) -> tuple[Case, ...]:
    """Return every case this SOURCE TEXT declares, with its verdict.

    ⚑ PUBLIC, AND THE SUITE IS ITS FIRST CONSUMER. A caller holding source rather than a path
    would otherwise reach for the private walk — and a test reaching past a module's surface
    pins an implementation detail rather than the behaviour, which is the shape that makes a
    later repair read as a regression.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return ()
    out: list[Case] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        out.extend(Case(suite, node.name, prose, verdict) for prose, verdict in _cases_in(node))
    return tuple(out)


def read(path: Path) -> tuple[Case, ...]:
    """Return every case this suite declares, with its verdict."""
    try:
        src = path.read_text(encoding="utf-8")
    except OSError:
        return ()
    return read_source(src, path.name)


def census(root: Path | None = None) -> tuple[Case, ...]:
    """Return every case across the promoted package's suites."""
    where = (root if root is not None else corpus.ROOT) / "substrate"
    out: list[Case] = []
    for path in sorted(where.glob("*_selftest.py")):
        out.extend(read(path))
    return tuple(out)


def dead(found: tuple[Case, ...]) -> tuple[Case, ...]:
    """Return only the cases that cannot fail."""
    return tuple(c for c in found if c.dead)


def render(found: tuple[Case, ...]) -> str:
    """Render the census: how many cases can fail, how many cannot, how many are unread.

    ⚑ THE UNDECIDED ROW IS PRINTED EVEN AT ZERO. A case this reader could not classify is a
    different fact from a case it cleared, and a suite audited by an instrument that silently
    skipped what it could not read would be the defect this exists to find.
    """
    if not found:
        return "dead-case: no cases read — a fact about the WALK, not the suites\n"

    bad = dead(found)
    unread = [c for c in found if c.undecided]
    suites = {c.suite for c in found}

    rows = [
        f"  {len(found)} case(s) across {len(suites)} suite(s)",
        f"    can fail                              : {len(found) - len(bad) - len(unread)}",
        f"    ⚑ CANNOT FAIL (a literal truth value) : {len(bad)}",
        f"    UNDECIDED (a fact about this reader)  : {len(unread)}",
    ]
    rows.extend(f"      dead  {c.suite}::{c.func}  {c.prose[:60]}" for c in bad[:SAMPLE])
    if len(bad) > SAMPLE:
        rows.append(f"      … and {len(bad) - SAMPLE} more unfailable case(s)")
    rows.extend(f"      ⚑ unread  {c.suite}::{c.func}  {c.prose[:52]}" for c in unread[:SAMPLE])
    if len(unread) > SAMPLE:
        rows.append(f"      … and {len(unread) - SAMPLE} more undecided case(s)")
    return "\n".join(rows) + "\n"


def main(argv: list[str]) -> int:
    """Print the dead-case census for the promoted package's suites."""
    if argv:
        sys.stderr.write("usage: dead_case.py\n")
        return 2
    sys.stdout.write(render(census()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
