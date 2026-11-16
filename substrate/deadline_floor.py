#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read each verify deadline and the authority it resolves through.

⚑⚑⚑ THE ORIGIN'S PREDICATE WENT INERT WHEN THE PRODUCER IMPROVED. It walked for a
`--deadline` argparse call and read `default=` only when that default was an `_ast.Constant`.
`membudget_otlp.py:267` now declares `default=_probe.DEFAULT_DEADLINE` — a NAME — so the branch
never matches, `under` stays empty, and the item reports every deadline clear no matter what value
sits behind the name. **The witness went green BECAUSE the producer stopped hardcoding**, which is
the one direction a checker must never mistake for a repair.

⚑⚑ AND THE FLOOR IT COMPARED AGAINST IS NOT OURS TO STATE. The origin hardcodes `FLOOR = 30.0`
as *"the store's own latency floor"*. That number is an operational parameter of cassian's
VictoriaMetrics (`-search.latencyOffset`), retuned to 1.5 times their ingest-buffer flush interval
— so a constant frozen here ages into a false claim the moment they tune it, and an operator
sizing against it sizes against a number that is not one. **A deadline is checkable against the
DECLARATION it resolves through; it is not checkable against someone else's knob.**

⚑ SO WHAT IS MEASURED HERE IS THE RESOLUTION, NOT A COMPARISON. For each declared verify deadline:
does it name a shared authority, or does it type a literal at the call site? A literal is the
finding — it is the spelling that drifts from the authority silently, and it is the only half of
this a checker in THIS repo can honestly own.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split), rewritten rather than moved.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import corpus

if TYPE_CHECKING:
    from pathlib import Path

# The producers declaring a poll deadline for a read-your-write verify.
PRODUCERS = ("scripts/membudget_otlp.py",)

# The flag whose default is the deadline.
FLAG = "--deadline"


@dataclass(frozen=True, slots=True)
class Deadline:
    """One declared verify deadline and how its default is spelled."""

    path: str
    line: int
    # The dotted name the default resolves through, or None when it is a literal.
    authority: str | None
    # The literal seconds, when the default is typed at the call site.
    literal: float | None

    @property
    def resolved(self) -> bool:
        """Report whether the default names an authority rather than a literal."""
        return self.authority is not None


def _authority(node: ast.expr) -> str | None:
    """Return the dotted name an expression reads, or None when it is not a name read."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        head = _authority(node.value)
        return f"{head}.{node.attr}" if head else None
    return None


def _literal(node: ast.expr) -> float | None:
    """Return a numeric constant's value, or None when the node is not one."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    return None


def declarations(path: Path, label: str) -> tuple[Deadline, ...]:
    """Read every deadline declaration in one file.

    ⚑ BOTH SPELLINGS ARE READ, WHICH IS THE WHOLE POINT. The origin read only the literal one, so
    a default that moved to a shared name became invisible rather than becoming a row.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return ()

    found: list[Deadline] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        flags = [a.value for a in node.args if isinstance(a, ast.Constant) and a.value == FLAG]
        if not flags:
            continue
        for kw in node.keywords:
            if kw.arg != "default":
                continue
            found.append(
                Deadline(
                    path=label,
                    line=node.lineno,
                    authority=_authority(kw.value),
                    literal=_literal(kw.value),
                )
            )
    return tuple(found)


def population(root: Path | None = None) -> tuple[Deadline, ...]:
    """Read every declared verify deadline across the producers."""
    where = root if root is not None else corpus.ROOT
    found: list[Deadline] = []
    for rel in PRODUCERS:
        found.extend(declarations(where / rel, rel))
    return tuple(found)


def unresolved(rows: tuple[Deadline, ...]) -> tuple[Deadline, ...]:
    """Return the deadlines typed as a literal rather than read from an authority."""
    return tuple(row for row in rows if not row.resolved)


def render(rows: tuple[Deadline, ...]) -> str:
    """Render the census, naming what an empty population means.

    ⚑ ZERO DECLARATIONS IS NOT ZERO FINDINGS. No producer declaring a deadline reads as clean and
    means UNMEASURED — the origin's own failure, arrived at from the other side.
    """
    if not rows:
        return (
            f"  no {FLAG} declaration found in {len(PRODUCERS)} producer(s) — UNMEASURED, not clean"
        )
    out = []
    for row in rows:
        if row.authority is not None:
            out.append(f"  {row.path}:{row.line}  default={row.authority}  (resolved)")
        else:
            out.append(
                f"  ⚑ {row.path}:{row.line}  default={row.literal:.0f}s  "
                f"(a literal at the call site — it cannot track its authority)"
            )
    return "\n".join(out)


if __name__ == "__main__":
    import sys

    _rows = population()
    sys.stdout.write(render(_rows) + "\n")
    sys.stdout.write(f"  {len(unresolved(_rows))} of {len(_rows)} unresolved\n")
    sys.exit(0)
