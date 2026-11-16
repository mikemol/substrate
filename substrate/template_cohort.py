# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Which files are instantiations of ONE template — a cohort, not N independent files.

⚑⚑⚑ A COHORT IS ONE DECISION WEARING N ROWS, AND EVERY COUNT OVER IT IS INFLATED. A census
listing fourteen files at fifty findings each reads as fourteen problems and eight hundred
findings; if they are one generated template with three substituted parameters, it is ONE
problem, and the fix is to the generator or to the template. Ranking, budgeting and
"cheapest first" all mislead in the same direction until the cohort is named.

⚑⚑ THE COMPARISON IS OVER THE NORMALISED AST, NOT THE TEXT. Two instantiations differ in
exactly the strings that were substituted, so a textual diff reports them as different files
and a hash reports them as unrelated. Erasing constant VALUES while keeping the structure is
what makes the shared template visible — and keeping the SHAPE is what stops it from calling
every short script the same.

⚑ CONSTANTS ARE ERASED BY POSITION, NOT BY VALUE. Replacing every constant with one token
would make `f(1, 2)` and `f("a", "b")` identical, which is correct here — the parameters ARE
the difference — but it also means this reader CANNOT distinguish two templates that differ
only in their literals. That is a real limit and it is why the skeleton is reported alongside
the verdict rather than hidden behind a boolean.

⚑ THIS FINDS EXACT STRUCTURAL TWINS, NOT NEAR-MISSES. A cohort whose members drifted apart —
one gained a branch, another lost a loop — will NOT group here, and reporting it as ungrouped
is honest: those members no longer share a template, whatever their filenames suggest.
`jea_pysim --clusters` is the reader for graded similarity, and it interns FUNCTIONS, so a
flat script with no `def` contributes nothing to it. Measured: pointing it at this cohort
returned clusters from a sibling module's functions and nothing from the scripts themselves.
"""

from __future__ import annotations

import ast
from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Cohort:
    """A set of files sharing one structural skeleton."""

    skeleton: str
    members: tuple[str, ...]

    @property
    def size(self) -> int:
        """How many files instantiate this template."""
        return len(self.members)

    @property
    def is_cohort(self) -> bool:
        """Whether this is a template with several instantiations.

        ⚑ A LONE FILE IS NOT A COHORT. Reporting every unique file as a one-member cohort
        would bury the finding in noise, which is the shape that gets a reader ignored.
        """
        return self.size > 1


class Erase(ast.NodeVisitor):
    """Blank every constant's value in place, keeping the tree's structure intact.

    ⚑ A VISITOR THAT MUTATES, NOT A TRANSFORMER THAT RETURNS. `NodeTransformer.visit` is
    typed `Any` — it may legally hand back a node, a list, or None — so its result crosses
    this module's boundary unchecked, and the value the whole verdict rests on would be the
    one thing not type-checked. Mutating in place keeps the tree's type known throughout.
    """

    def visit_Constant(self, node: ast.Constant) -> None:
        """Erase one constant's value, then descend."""
        node.value = None
        self.generic_visit(node)


def skeleton_of(source: str) -> str | None:
    """Return the structural skeleton of `source`, or None when it does not parse.

    ⚑ NAMES ARE KEPT, CONSTANTS ARE NOT. A template substitutes VALUES — a module name, a
    slug, a path — while the identifiers it binds stay the same; erasing names too would
    collapse genuinely different scripts that happen to share a control shape.
    """
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return None
    Erase().visit(tree)
    return ast.dump(tree, annotate_fields=False)


def _weight(cohort: Cohort) -> tuple[int, str]:
    """Return the sort key: largest cohort first, then by first member."""
    return (-cohort.size, cohort.members[0] if cohort.members else "")


def cohorts(sources: dict[str, str]) -> list[Cohort]:
    """Group files by shared skeleton, largest cohort first.

    `sources` maps a path to its text.

    ⚑ FILES THAT DO NOT PARSE ARE OMITTED, and that is a fact about this reader rather than
    about them. A caller wanting them accounted for must count its own input.
    """
    groups: dict[str, list[str]] = defaultdict(list)
    for path, text in sources.items():
        shape = skeleton_of(text)
        if shape is not None:
            groups[shape].append(path)
    out = [Cohort(shape, tuple(sorted(paths))) for shape, paths in groups.items()]
    return sorted(out, key=_weight)


def render(found: list[Cohort]) -> str:
    """Render the cohorts, largest first, singletons summarised."""
    real = [c for c in found if c.is_cohort]
    singles = [c for c in found if not c.is_cohort]
    grouped = sum(c.size for c in real)
    head = f"{len(real)} cohort(s) covering {grouped} file(s); {len(singles)} file(s) stand alone"
    out = [head]
    for cohort in real:
        out.append(f"\n  {cohort.size} file(s) share one template:")
        out.extend(f"      {m}" for m in cohort.members)
    if real:
        # ⚑ THE PLANNING CONSEQUENCE, STATED. A cohort is one decision, so a count over its
        # members is an inflated count of the work.
        out.append(
            f"\n  ⚑ each cohort is ONE decision — a per-file count over these "
            f"{grouped} file(s) overstates the work by {grouped - len(real)}."
        )
    return "\n".join(out) + "\n"
