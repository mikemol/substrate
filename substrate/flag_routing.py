#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report which gates route their flags through the shared argv authority.

⚑⚑⚑ THE ORIGIN'S PREDICATE WAS A SUBSTRING TEST OVER THE WHOLE FILE — `"check_argv" not in
_read(path)` — so a gate that only MENTIONS the authority reads as one that USES it. A docstring
explaining why a gate does not route its flags satisfies it; so does a comment, and so does an
`import` that merely re-exports the name. MEASURED: `scripts/ratchet.py` holds `check_argv` on an
import line and never calls it, and the substring test cannot tell that from a call.

⚑⚑ SO THE READ IS STRUCTURAL: a CALL, not an occurrence. That distinction is the whole item —
the same use-versus-mention defect the closure-delegation reader was rewritten to remove, and the
one the bib probe hit when a `%`-comment was parsed as a header.

⚑ AND PRESENCE IS STILL NOT CONSUMPTION, WHICH THIS READER DELIBERATELY DOES NOT CLAIM TO ANSWER.
A `check_argv` call was once present and INERT because the authority sliced argv wrongly, so the
guard never fired. This counts the call SITE; that it FIRES is a mutation question, and stating
the boundary here is what keeps the two from being read as one.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split), rewritten rather than moved.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import corpus

if TYPE_CHECKING:
    from pathlib import Path

# The shared authority every gate's flag handling must route through.
AUTHORITY = "check_argv"

# Where gates live, and which files there are gates.
GATE_DIR = "scripts"
GATE_GLOB = "check_*.py"


@dataclass(frozen=True, slots=True)
class Routing:
    """How one gate reaches the shared authority, if at all."""

    gate: str
    # Lines carrying a real call.
    calls: tuple[int, ...]
    # Lines that only NAME the authority — an import, a comment, prose.
    mentions: tuple[int, ...]

    @property
    def routes(self) -> bool:
        """Report whether the gate actually calls the authority."""
        return bool(self.calls)

    @property
    def mentions_only(self) -> bool:
        """Report the case a substring test gets wrong.

        ⚑ THE FALSE COMPLIANT. A file naming the authority without calling it passes a text
        search and fails the property — and it is the only row where the two readings disagree.
        """
        return bool(self.mentions) and not self.calls


def _call_name(node: ast.Call) -> str | None:
    """Return the called name, whether spelled bare or through a module."""
    target = node.func
    if isinstance(target, ast.Name):
        return target.id
    if isinstance(target, ast.Attribute):
        return target.attr
    return None


def _called_at(tree: ast.Module) -> tuple[int, ...]:
    """Return the lines where the authority is CALLED."""
    return tuple(
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and _call_name(node) == AUTHORITY
    )


def _named_at(tree: ast.Module) -> tuple[int, ...]:
    """Return the lines where the authority is named.

    ⚑ THE IMPORT IS THE INTERESTING MENTION. A re-export binds the name and forwards it, which
    reads as adoption to any text search and is not — `scripts/ratchet.py` is exactly that.

    ⚑ THE THREE BRANCHES STAY SEPARATE because each narrows a different node type, and the line
    number is only reachable through that narrowing. A shared `bool` predicate reads tidier and
    hands back an `ast.AST` with no `lineno` — measured, refused.
    """
    found: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            found.extend(node.lineno for alias in node.names if alias.name == AUTHORITY)
        elif isinstance(node, ast.Name):
            if node.id == AUTHORITY:
                found.append(node.lineno)
        elif isinstance(node, ast.Attribute) and node.attr == AUTHORITY:
            found.append(node.lineno)
    return tuple(found)


def routing(path: Path, label: str) -> Routing | None:
    """Read how one gate reaches the authority, or None when it cannot be parsed."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except (OSError, SyntaxError):
        return None

    calls = _called_at(tree)
    named = _named_at(tree)
    # ⚑ A CALL'S OWN NAME NODE IS NOT A SEPARATE MENTION. Counting it would make every routing
    # gate look like it also mentions the authority, and the mentions-only row would never fire.
    mentions = tuple(line for line in named if line not in set(calls))
    return Routing(gate=label, calls=calls, mentions=mentions)


def gates(root: Path | None = None) -> tuple[str, ...]:
    """Return the gate filenames, read from the tree rather than listed."""
    where = (root if root is not None else corpus.ROOT) / GATE_DIR
    return tuple(sorted(found.name for found in where.glob(GATE_GLOB)))


def population(names: tuple[str, ...], root: Path | None = None) -> tuple[Routing, ...]:
    """Read the routing of every named gate."""
    where = (root if root is not None else corpus.ROOT) / GATE_DIR
    out = []
    for name in names:
        found = routing(where / name, name)
        if found is not None:
            out.append(found)
    return tuple(out)


def unrouted(rows: tuple[Routing, ...]) -> tuple[Routing, ...]:
    """Return the gates that do not call the authority."""
    return tuple(row for row in rows if not row.routes)


def render(rows: tuple[Routing, ...]) -> str:
    """Render the census, marking the rows a text search would misread."""
    if not rows:
        return f"  no gate read — UNMEASURED, not clean (authority: {AUTHORITY})"

    missing = unrouted(rows)
    if not missing:
        return f"  every one of {len(rows)} gate(s) calls {AUTHORITY}"

    # ⚑⚑⚑ EVERY UNROUTED ROW IS MARKED, AND THE UNMARKED HALF WAS A MEASURED UNDER-REPORT. The
    # mentions-only rows carried the flag and the plain ones did not, so a consumer reading marked
    # lines as the population saw ZERO findings here while this census held six — and its sibling
    # `universal_flags`, built from the same gates one item later, marks every row and reported
    # all six. **The under-report is the direction that reads as clean**, which is why the
    # convention has to be uniform rather than expressive: the marker says *this row is a
    # finding*, and the prose after it says which kind.
    out = [f"  {len(missing)} of {len(rows)} gate(s) do not call {AUTHORITY}:"]
    for row in missing:
        if row.mentions_only:
            out.append(
                f"    ⚑ {row.gate} — NAMES it at line {row.mentions[0]} without calling "
                f"it (a text search reads this as compliant)"
            )
        else:
            out.append(f"    ⚑ {row.gate}")
    return "\n".join(out)


if __name__ == "__main__":
    sys.stdout.write(render(population(gates())) + "\n")
    sys.exit(0)
