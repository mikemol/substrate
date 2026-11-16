#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Find Scenario names in Gherkin features and in the test docstrings that quote them.

Split out of `check_feature_coverage` so the SCANNING is separable from the VERDICT: one
side reads two directory trees, the other decides whether the link between them holds.

⚑ THE PATTERN IS THE SUBTLE PART AND IT BELONGS WITH THE SCANNER. In a feature file the
line begins with the keyword; in a test docstring it is preceded by indentation AND the
docstring opener, and may be followed by a closing quote run on the same line. A pattern
anchored directly on the keyword matches the spec but NONE of the tests, which would
report every scenario as an orphan — a gate that is useless while looking green in
reverse.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

SCENARIO = re.compile(
    r'^[ \t]*(?:[ru]?["\']{1,3})?\s*Scenario(?: Outline)?:'
    r'\s*(.+?)\s*(?:["\']{1,3})?\s*$',
    re.MULTILINE,
)


def names_in(path: Path) -> list[str]:
    """Return every Scenario name the file declares or quotes.

    ⚑⚑ `re.findall` IS ANNOTATED `list[Any]`, AND A COMPREHENSION OVER IT DOES NOT
    NARROW IT. The obvious `[str(m) for m in SCENARIO.findall(...)]` still leaks: the
    iteration happens over an `Any`-typed sequence, so the checker refuses the expression
    before `str()` ever runs. Binding to a declared `object` and testing with a real
    `isinstance` is the narrowing — a CHECK, not an assertion.

    ⚑ THIS IS THE FIFTH `Any`-AT-A-BOUNDARY SHAPE IN THIS MIGRATION, after
    `argparse.Namespace`, `re.Match.group()`, `subprocess.run`'s overload and
    `collections.namedtuple`. Every one had the same cure and the same trap: annotating
    honestly at the seam is not the same as narrowing at the use, and only the second one
    the checker accepts.
    """
    found: object = SCENARIO.findall(path.read_text(encoding="utf-8"))
    if not isinstance(found, list):
        return []
    return [str(m) for m in found]


def declared(features: Path) -> dict[str, str]:
    """Map each declared scenario to the feature file declaring it."""
    if not features.is_dir():
        return {}
    return {name: p.name for p in sorted(features.glob("*.feature")) for name in names_in(p)}


def quoted(tests: Path) -> set[str]:
    """Return every Scenario name quoted inside a test module's docstrings."""
    if not tests.is_dir():
        return set()
    return {name for p in sorted(tests.glob("*.py")) for name in names_in(p)}
