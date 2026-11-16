#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report which gates accept the universal flags, by asking the authority that admits them.

⚑⚑⚑ THE ORIGIN'S FIRST PREDICATE REPORTED 10 OF 11 GATES AS DEBT, AND EVERY ONE WAS COMPLIANT.
It searched each gate's source for the flag STRING, so a gate that never mentions `--dry-run` read
as missing it. The flag is resolved AT THE AUTHORITY — `set_ratchet` reads it from `sys.argv`, and
`check_argv` admits it via `UNIVERSAL_FLAGS` — **precisely so ten call sites do NOT each forward
it**. Threading one flag through ten files is the N-call-sites shape that was deliberately
retired, and the eleventh gate written next month would silently lack it again.

⚑⚑ VERIFIED BEHAVIOURALLY AT THE TIME: `check_private_ratchet.py --dry-run`, a gate on the old
*"missing"* list, previews the write and records nothing. **The gates were compliant; the figure
was measuring mentions.**

⚑⚑ SO THE QUESTION IS WHAT A GATE *ACCEPTS*, AND THE ANSWER COLLAPSES ONTO ONE PROPERTY. Accepting
`--dry-run` without also accepting a TYPO is what `check_argv` provides, so a gate accepts the
universal flags exactly when it routes through the authority. **This is not a second population:
it is `flag_routing`'s, read for a different consequence** — which is why the routing read is
reused rather than re-derived, and why a gate declaring a universal flag literally is ALSO
accepted (it answers for itself).

⚑ AND THE ONE FLAG IS READ, NEVER RESTATED. `UNIVERSAL_FLAGS` lives in `substrate.ratchet_flags`;
a local copy would go stale in the direction that reports a NEW universal flag as debt across
every gate at once.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split), rewritten rather than moved.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import corpus, flag_routing
from substrate.ratchet_flags import UNIVERSAL_FLAGS

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True, slots=True)
class Acceptance:
    """Whether one gate accepts the universal flags, and how."""

    gate: str
    # The gate routes through the authority, which admits the universal flags for it.
    routes: bool
    # Universal flags the gate names literally — it answers for itself.
    declared: tuple[str, ...]

    @property
    def accepts(self) -> bool:
        """Report whether the gate accepts the universal flags at all.

        ⚑ EITHER ROUTE COUNTS. A gate reaching the authority inherits every universal flag; one
        declaring the flag itself accepts that flag. Requiring both would report a self-sufficient
        gate as debt; requiring neither would report the population as clean.
        """
        return self.routes or bool(self.declared)


def _literals(tree: ast.Module) -> set[str]:
    """Return the flag-shaped string literals a gate names."""
    return {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and node.value.startswith("--")
    }


def acceptance(path: Path, label: str) -> Acceptance | None:
    """Read how one gate accepts the universal flags, or None when it cannot be parsed."""
    routed = flag_routing.routing(path, label)
    if routed is None:
        return None

    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except (OSError, SyntaxError):
        return None

    declared = tuple(sorted(UNIVERSAL_FLAGS & _literals(tree)))
    return Acceptance(gate=label, routes=routed.routes, declared=declared)


def population(names: tuple[str, ...], root: Path | None = None) -> tuple[Acceptance, ...]:
    """Read the acceptance of every named gate."""
    where = (root if root is not None else corpus.ROOT) / flag_routing.GATE_DIR
    out = []
    for name in names:
        found = acceptance(where / name, name)
        if found is not None:
            out.append(found)
    return tuple(out)


def lacking(rows: tuple[Acceptance, ...]) -> tuple[Acceptance, ...]:
    """Return the gates that accept the universal flags by neither route."""
    return tuple(row for row in rows if not row.accepts)


def render(rows: tuple[Acceptance, ...]) -> str:
    """Render the census, naming what an empty population means."""
    flags = ", ".join(sorted(UNIVERSAL_FLAGS))
    if not rows:
        return f"  no gate read — UNMEASURED, not clean (universal flags: {flags})"

    missing = lacking(rows)
    if not missing:
        return f"  all {len(rows)} ratchet gate(s) accept the universal flags ({flags})"

    out = [f"  {len(missing)} of {len(rows)} gate(s) accept neither {flags} nor the authority:"]
    out.extend(f"    ⚑ {row.gate}" for row in missing)
    return "\n".join(out)


if __name__ == "__main__":
    sys.stdout.write(render(population(flag_routing.gates())) + "\n")
    sys.exit(0)
