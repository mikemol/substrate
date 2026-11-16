#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Ⓖ collapse-check — a NON-BLOCKING pre-commit advisory.

The code-layer twin of the `construct-dont-classify` skill. It catches the code-shaped
form of the either/or thrash the sessions kept hitting: building a special case AND the
generic that subsumes it, then orphaning the special case (the `TrilinearUniversal`
pattern), or proving one proposition in two modules (the `Stab-normal-when-fixed`
pattern).

For each newly-ADDED `.agda` module in the staged set it reports:

  · imported-by-0 — the module is imported by no other module. Confirm it is an
    intended capstone/leaf, NOT a built-then-orphaned rung. Most leaves are legitimate
    terminal theorems or hubs; this forces the conscious check that would have caught
    the dead rung.

  · def-name overlap — a top-level definition whose NAME also exists in another module.
    The name-based gates (decl_shape_tag / import-shape) handle the same-name case for
    ambiguity tagging; here it is a *collapse* hint: if it is the SAME proposition,
    derive or import instead of re-proving.

It NEVER blocks (advisory only; exits 0). The deeper same-content-different-NAME
duplicate check is `python jea/metalanguage/jea_pysim.py --cluster`, too heavy to run
every commit — pointed at from here, never run.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

_DECL = re.compile(r"^([^\s:(){}@]+)\s*:")
_KEYWORDS = {
    "module",
    "open",
    "import",
    "record",
    "data",
    "infix",
    "infixl",
    "infixr",
    "private",
    "postulate",
    "variable",
    "syntax",
    "field",
    "mutual",
    "where",
    "renaming",
    "using",
    "hiding",
    "--",
    "{-#",
}

# How many other homes a duplicated name lists before the report truncates.
_SHOWN_HOMES = 3


def sh(*args: str) -> str:
    """Return a git command's stdout, or `""` when it could not run.

    ⚑ THE EMPTY STRING IS AN HONEST FAILURE HERE, NOT A SWALLOWED ONE, BUT ONLY
    BECAUSE THE CALLER CHECKS. The previous shape read `.stdout` with no `check` and
    no returncode test, so `repo_root()` outside a git tree returned `Path("")` — an
    existing, wrong path that every later `rglob` silently walked. `PLW1510` was
    pointing at exactly that: an implicit `check` is where a reader cannot tell a
    deliberate choice from an oversight. `main` now refuses an empty root rather than
    proceeding against one.
    """
    proc = subprocess.run(args, capture_output=True, text=True, check=False)
    return proc.stdout if proc.returncode == 0 else ""


def repo_root() -> Path | None:
    """Return the repository root, or None when this is not a git worktree."""
    out = sh("git", "rev-parse", "--show-toplevel").strip()
    return Path(out) if out else None


def staged_added_agda(root: Path) -> list[Path]:
    """Return the newly-ADDED `.agda` paths in the staged set."""
    out = sh("git", "diff", "--cached", "--name-only", "--diff-filter=A", "--", "*.agda")
    return [root / line for line in out.splitlines() if line.strip()]


def module_path(root: Path, f: Path) -> str | None:
    """Map `agda/Substrate/A/B.agda` to `Substrate.A.B`, the name importers use."""
    try:
        rel = f.relative_to(root / "agda")
    except ValueError:
        return None
    return str(rel.with_suffix("")).replace("/", ".")


def top_level_names(f: Path) -> list[str]:
    """Return the file's top-level definition names (column-0 signatures only)."""
    names = []
    for line in f.read_text(errors="replace").splitlines():
        if not line or line[0].isspace():
            continue  # indented => not a top-level decl
        m = _DECL.match(line)
        if m is None:
            continue
        # ⚑ BOUND AND RE-TYPED AT THE BOUNDARY. `re.Match.group()` is annotated
        # `str | Any`, so every read through it is an unchecked expression under this
        # bar — the same `Any`-leak shape as `argparse.Namespace`. One `str()` here
        # narrows once; testing `m.group(1)` three times inline leaked it three times.
        head = str(m.group(1))
        if head not in _KEYWORDS and not head.startswith("-"):
            names.append(head)
    return names


def importers(root: Path, modpath: str, self_file: Path) -> int:
    """Count modules importing `modpath`, excluding the module itself."""
    # `import Substrate.A.B` (open import / import), with a path boundary so
    # Substrate.A.B does not match Substrate.A.BC.
    pat = re.compile(r"\bimport\s+" + re.escape(modpath) + r"(?:\s|$)")
    n = 0
    for g in (root / "agda").rglob("*.agda"):
        if g == self_file:
            continue
        try:
            if any(pat.search(line) for line in g.read_text(errors="replace").splitlines()):
                n += 1
        except OSError:
            pass
    return n


def name_overlaps(root: Path, names: list[str], self_file: Path) -> dict[str, list[str]]:
    """Return each name that is also declared elsewhere, with those other homes."""
    if not names:
        return {}
    want = {n: re.compile(r"^" + re.escape(n) + r"\s*:") for n in names}
    hits: dict[str, list[str]] = {n: [] for n in names}
    for g in (root / "agda").rglob("*.agda"):
        if g == self_file:
            continue
        try:
            lines = g.read_text(errors="replace").splitlines()
        except OSError:
            continue
        rel = str(g)
        for n, pat in want.items():
            if any(pat.match(line) for line in lines):
                hits[n].append(rel)
    return {n: ms for n, ms in hits.items() if ms}


def _note_for(mp: str, overlaps: dict[str, list[str]]) -> str:
    """Render one module's advisory paragraph."""
    note = [f"  · {mp} — imported-by-0 (a leaf)."]
    if overlaps:
        note.append(
            "    def-name overlap (possible duplicate/parallel-rung — "
            "collapse if it's the same proposition):"
        )
        for n, ms in sorted(overlaps.items()):
            shown = ", ".join(sorted(set(ms))[:_SHOWN_HOMES])
            note.append(f"      {n}  also in: {shown}")
    else:
        note.append(
            "    confirm it is an intended capstone/leaf, NOT a "
            "built-then-orphaned rung (the TrilinearUniversal pattern)."
        )
    return "\n".join(note)


def main() -> int:
    """Report newly-added modules nothing imports. ADVISORY: always returns 0."""
    root = repo_root()
    if root is None:
        # ⚑ REFUSE AN ABSENT ROOT RATHER THAN WALK `Path("")`. The previous shape took
        # git's empty output as a path and rglob'd the CURRENT directory, so outside a
        # worktree the advisory reported on whatever happened to be there.
        return 0
    added = staged_added_agda(root)
    if not added:
        return 0  # nothing new — silent no-op (the common case)

    findings: list[str] = []
    for f in added:
        if not f.exists():
            continue
        mp = module_path(root, f)
        if mp is None:
            continue
        if importers(root, mp, f) > 0:
            continue  # consumed — not an orphan; no advisory
        overlaps = name_overlaps(root, top_level_names(f), f)
        findings.append(_note_for(mp, overlaps))

    if findings:
        # ⚑ ONE STREAM, ONE ORDERED NARRATIVE. Splitting a gate's header from its
        # findings across stdout/stderr lets the two flush independently and prints the
        # header AFTER the list — measured on `check_capstone_shape` today.
        head = (
            "collapse-check advisory (Ⓖ, non-blocking) — newly-added modules imported by nothing:"
        )
        tail = (
            "  -> if any is subsumed by a more-general module, derive/collapse it; "
            "`python jea/metalanguage/jea_pysim.py --cluster` finds same-content "
            "duplicates under a different name."
        )
        sys.stdout.write("\n".join([head, *findings, tail]) + "\n")
    return 0  # ADVISORY: never blocks


if __name__ == "__main__":
    sys.exit(main())
