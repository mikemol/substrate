# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The `excludes:` witness — CLOSED while a function's source does not reach a needle (W40).

⚑⚑ CLEANROOMED FROM `.claude/agents/findings.py:_excludes`, whose rationale is the design: a
corpus-population claim (*"gate G's census is blind to directory D"*) is neither a `refuses:`
(nothing refuses — the gate passing IS the defect) nor a `selftest:`, and filing it `standing`
would bank a false zero. So it reads the function's SOURCE, which is the only place the claim
lives: a green run over a narrow corpus and one over a wide corpus are byte-identical. It flips
when someone widens the glob, which is exactly when the finding stops being true.

⚑ A MISS IS UNWITNESSED, NEVER HOLDING — a definition that cannot be read (renamed, moved, two
of them) is a fact about this reader, not evidence the exclusion persists.

⚑⚑ TWO DELIBERATE DIVERGENCES FROM THE ORIGIN:
- THE BODY IS READ WITH `ast`, NOT BY SHELLING TO `pycodemod --source`. That tool is being
  ported out of this repo (operator, 2026-09-25), and a witness should not depend on a tool in
  transit.
- ONLY THE DEFINITION'S OWN SOURCE IS SEARCHED. The origin searched pycodemod's whole output,
  whose header line names the file and function — so a needle occurring in the PATH read as the
  function reaching it: an OPEN manufactured by the reader's rendering.
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from mikemol.ledger import finding_kinds

if TYPE_CHECKING:
    from pathlib import Path

_DEFS = (ast.FunctionDef, ast.AsyncFunctionDef)


def definition(source: str, func: str) -> str | None:
    """Return the source of the ONE definition named `func` in `source`, else None."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    found = [n for n in ast.walk(tree) if isinstance(n, _DEFS) and n.name == func]
    if len(found) != 1:
        return None
    return ast.get_source_segment(source, found[0])


def verdict(mod_path: str, func: str, needle: str, root: Path) -> finding_kinds.Verdict:
    """Return the `excludes:` verdict for `func` in `mod_path` (relative to `root`)."""
    where = f"{mod_path}:{func}"
    try:
        source = root.joinpath(mod_path).read_text(encoding="utf-8")
    except OSError as exc:
        return finding_kinds.UNRUNNABLE, f"UNWITNESSED — could not read {where} ({exc})"
    body = definition(source, func)
    if body is None:
        return finding_kinds.UNRUNNABLE, (
            f"UNWITNESSED — {where} did not resolve to one definition; the finding may still "
            "hold but this reader cannot say so"
        )
    if needle in body:
        return finding_kinds.OPEN, f"{where} NOW REACHES {needle!r} — the exclusion is GONE"
    return finding_kinds.CLOSED, f"{where} does not reach {needle!r}"
