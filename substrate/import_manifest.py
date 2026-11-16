#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report the imports no manifest accounts for, split by what would account for them.

⚑⚑⚑ THE ORIGIN'S CARVE-OUT NEVER FIRED, AND BOTH BRANCHES AGREED. It read
`tool.substrate.environment-provided` out of `pyproject.toml` to excuse Blender's embedded
modules, falling back to an empty set on any error. MEASURED, two ways: `--literal substrate
pyproject.toml` returns **0 sites**, and the only mention of the key anywhere in the corpus is
the witness reading it. **There is no such table**, so `env_provided` was always empty and the
successful parse produced exactly what the failure produced — a carve-out that reads as active
policy and subtracts nothing.

⚑⚑ AND THE UNACCOUNTED POPULATION IS NOT ONE KIND, WHICH IS WHY A COUNT MISLEADS. Live it is 15
MISSING and 0 UNDECLARED, and those 15 hold at least three different remedies: `bpy`/`bmesh`/
`mathutils` ship inside Blender's interpreter and CANNOT be pip dependencies (declaring them
would make the manifest assert something false); `matplotlib`/`scipy`/`pyvista` are real optional
dependencies; and names like `applied_grammar` resolve in-tree under a spelling the classifier's
first-party test did not match. **One number over three remedies tells an operator to do nothing
in particular.**

⚑ THE CLASSIFICATION IS THE TOOL'S, NEVER RESTATED HERE. `pycodemod.imports()` already grades the
corpus six ways, and its own docstring records why a second classifier is the rival-implementation
shape: the two disagree the first time either is fixed. This module reads that verdict and groups
it; it does not re-derive it.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split), rewritten rather than moved.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Protocol, cast

from substrate import scratch_module

# The tool that owns the import classification.
CLASSIFIER = "pycodemod"

# The verdicts naming an import nothing accounts for. ⚑ BOTH, NOT ONE: `UNDECLARED` works today
# and breaks on a fresh clone; `MISSING` does not import at all. Different remedies, both owed.
UNACCOUNTED = ("UNDECLARED", "MISSING")


class Classifier(Protocol):
    """The part of the codemod tool this reader consults."""

    def imports(self) -> list[tuple[str, str, int, str]]:
        """Return `(top_module, verdict, n_files, example)` over the corpus."""
        ...


@dataclass(frozen=True, slots=True)
class Unaccounted:
    """One import in no manifest."""

    module: str
    verdict: str
    files: int
    example: str

    def line(self) -> str:
        """Render this row as one indented line."""
        return f"    {self.module}  ({self.files} file(s), e.g. {self.example})"


def classifier() -> tuple[Classifier | None, str]:
    """Load the import classifier, narrowed to the one call this reader makes."""
    found, why = scratch_module.scratch_module(CLASSIFIER)
    if found is None:
        return None, f"{CLASSIFIER} will not load: {why}"
    return cast("Classifier", found), ""


def population() -> tuple[tuple[Unaccounted, ...], str]:
    """Read every import the manifests do not account for.

    ⚑ THE FAILURE IS RETURNED, NOT RAISED, AND IT IS NOT AN EMPTY POPULATION. A classifier that
    will not load means the census did not happen — reporting zero unaccounted imports would be
    the false green this whole family exists to refuse.
    """
    api, missing = classifier()
    if api is None:
        return (), missing

    rows = tuple(
        Unaccounted(module=top, verdict=verdict, files=count, example=example)
        for top, verdict, count, example in api.imports()
        if verdict in UNACCOUNTED
    )
    return rows, ""


def by_verdict(rows: tuple[Unaccounted, ...]) -> dict[str, tuple[Unaccounted, ...]]:
    """Group the unaccounted imports by the verdict that named them.

    ⚑ THE GROUPING IS THE REPORT. `UNDECLARED` is a manifest edit; `MISSING` is either a missing
    install, an environment-provided module that cannot be declared, or a first-party name the
    classifier could not resolve — and an operator reading one total cannot tell which they have.
    """
    out: dict[str, list[Unaccounted]] = {}
    for row in rows:
        out.setdefault(row.verdict, []).append(row)
    return {verdict: tuple(found) for verdict, found in sorted(out.items())}


def render(rows: tuple[Unaccounted, ...], why: str = "") -> str:
    """Render the census, keeping unmeasured distinct from clean."""
    if why:
        return f"  UNMEASURED — {why}"
    if not rows:
        return "  every third-party import is accounted for"

    out: list[str] = []
    for verdict, found in by_verdict(rows).items():
        out.append(f"  {verdict}: {len(found)}")
        out.extend(row.line() for row in found)
    return "\n".join(out)


if __name__ == "__main__":
    _rows, _why = population()
    sys.stdout.write(render(_rows, _why) + "\n")
    sys.exit(0)
