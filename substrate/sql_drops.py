#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""⟡no-automated-drop — every `DROP TABLE` in the SQL-writing modules, with its CALLER.

⚑⚑⚑ THE FIRST CUT OF THE DRAIN'S SECOND FILE. `query_defs.drops` is a pure text census with
no SQLAlchemy in it, and it sat inside a 2095-line module the per-file gate refuses whole. It
moves here verbatim in logic, typed at the seams, with a row-for-row differential against the
origin's `--drops` mode over the live tree.

⚑⚑⚑ THE RULE THIS EXISTS TO CHECK (operator, 2026-08-22): **"We should not have any drop-table
statements that are not part of singleton operations. Drop-table statements should not be
automated."** A `DROP TABLE` takes `AccessExclusiveLock` — the strongest lock postgres has,
blocking every other access including reads — so a drop reachable from a per-item or automated
path is an exclusive lock taken at whatever concurrency the caller happens to run at.

⚑ THE ENCLOSING FUNCTION IS THE WHOLE POINT, not the line. *"Is this drop automated?"* is a
question about the CALLER — `init_db` dropping a tier once at setup is the sanctioned shape,
while the same statement inside a projection that runs per core is not. A file:line cannot tell
those apart; a function name can, and the reviewer supplies the singleton/automated judgement.
The enclosing `def` is the nearest preceding one — a LINE SCAN rather than an AST walk, kept
from the origin: exact for this corpus's flat function layout, and stated rather than hidden.

⚑ VERB-SCANNED, SO IT REPORTS PRESENCE AND NEVER ABSENCE. A drop spelled through a variable, an
f-string, or a helper is invisible here. A clean result means "no drop found under these
spellings", not "no drop".

⚑⚑ THREE MEASURED CORRECTIONS ARE KEPT AS RULES, NOT COMMENTS:
  - A COMMENTED-OUT DROP IS NOT A DROP. `write_events` holds a removed tier-drop QUOTED in a
    block explaining the removal, and the scan reported it live. A line whose first non-space
    character is `#` is prose about code. (A drop inside a docstring is still counted: that
    string IS reachable text, and over-reporting is the safe direction for a destructive verb.)
  - `IF EXISTS` IS OPTIONAL AND CASE-VARYING. A first cut reported relations named `IF` and
    `with` — the extractor's failure reported as a fact about the schema. A `%s` placeholder or
    an f-string brace yields `?` rather than a wrong name.
  - THE CENSUS MUST NOT COUNT ITSELF. `touching`, `drops` and `main` in `query_defs` hold the
    literal as a SEARCH TERM; those three functions are excluded by NAME in that file, so any
    real drop added to it stays visible.

⚑ THE ORDER IS ON THE TYPE, NOT A WRAPPER. The origin returned `sorted_stream.Sorted`, which
lives only in `jea/metalanguage/` and is reachable by a bare import alone (one consumer, this
one); carrying it here would add the very `sys.path` coupling the drain removes. `drops()`
returns a tuple sorted by `(relation, path, line, function)` and says so; a consumer that needs
the declared-order wrapper wraps it at the boundary.

⚑ THE TREE IS A REQUIRED ARGUMENT (2026-09-24, operator: "We should not have things [like]
corpus.ROOT"). `drops` used to default `root` to `corpus.ROOT`; the caller now says which tree.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

# The trees the SQL-writing modules live in, relative to the repo root.
TREES = ("scripts", "jea/metalanguage")

# The file whose search-term functions are excluded from their own census.
_INSTRUMENT = "query_defs.py"
_INSTRUMENT_FUNCTIONS = frozenset({"touching", "drops", "main"})

# A quoted string holding the verb, on one line.
_LITERAL = re.compile(r"[\"'][^\"'\n]*\bdrop\s+table\b[^\"'\n]*[\"']", re.IGNORECASE)
# The relation the verb names, when it names one.
_RELATION = re.compile(r"drop\s+table\s+(?:if\s+exists\s+)?[\"'`]?([A-Za-z_]\w*)", re.IGNORECASE)
# The enclosing-def approximation.
_DEF = re.compile(r"^\s*def\s+(\w+)", re.MULTILINE)
# Captures that are the clause, not the relation.
_NOT_A_NAME = frozenset({"if", "with", "exists"})
UNNAMED = "?"


@dataclass(frozen=True, slots=True, order=True)
class Drop:
    """One `DROP TABLE` site: the relation (or `?`), where, and the function that holds it."""

    relation: str
    path: str
    line: int
    function: str


def _relation_of(literal: str) -> str:
    """Return the relation a literal drops, or `?` when the name is a placeholder or clause."""
    found = _RELATION.search(literal)
    if found is None:
        return UNNAMED
    name = str(found.group(1))
    return UNNAMED if name.lower() in _NOT_A_NAME else name


def _enclosing(defs: list[tuple[int, str]], offset: int) -> str:
    """Return the nearest `def` name declared before `offset`, or `` at module level."""
    name = ""
    for pos, found in defs:
        if pos >= offset:
            break
        name = found
    return name


def scan_text(src: str, relpath: str) -> list[Drop]:
    """Return every live `DROP TABLE` literal in one file's text."""
    defs = [(m.start(), str(m.group(1))) for m in _DEF.finditer(src)]
    lines = src.splitlines()
    out: list[Drop] = []
    for m in _LITERAL.finditer(src):
        lineno = src[: m.start()].count("\n")
        if lineno < len(lines) and lines[lineno].lstrip().startswith("#"):
            continue
        function = _enclosing(defs, m.start())
        if relpath.endswith(_INSTRUMENT) and function in _INSTRUMENT_FUNCTIONS:
            continue
        out.append(Drop(_relation_of(str(m.group(0))), relpath, lineno + 1, function))
    return out


def _files(root: Path) -> list[Path]:
    """Return every `.py` directly under each tree, sorted — the origin's glob."""
    return sorted(p for tree in TREES for p in (root / tree).glob("*.py"))


def drops(root: Path) -> tuple[Drop, ...]:
    """Return every distinct drop site under the SQL-writing trees of `root`, sorted."""
    found: set[Drop] = set()
    for path in _files(root):
        try:
            src = path.read_text(encoding="utf-8")
        except OSError:
            continue
        found.update(scan_text(src, str(path.relative_to(root))))
    return tuple(sorted(found))


def render(found: tuple[Drop, ...]) -> list[str]:
    """Render the `--drops` report in the origin's words."""
    lines = [f"  {d.relation:<16} {d.path}:{d.line}  in {d.function or '<module>'}" for d in found]
    lines.append("")
    lines.append(
        f"{len(found)} `DROP TABLE` site(s) — ⟡no-automated-drop: a drop takes AccessExclusiveLock,"
    )
    lines.append("so each must belong to a SINGLETON operation (setup/teardown), never to an")
    lines.append("automated or per-item path. The enclosing function is the reviewable unit.")
    lines.append("⚑ VERB-SCANNED: reports what it FOUND under these spellings, never that there")
    lines.append("  are no others — a drop built from a variable or an f-string is invisible here.")
    return lines
