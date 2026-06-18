#!/usr/bin/env python3
"""Ⓖ — collapse-check: a NON-BLOCKING pre-commit advisory (code-layer twin of
the `construct-dont-classify` skill).

It catches the code-shaped form of the either/or thrash the session kept hitting
(building a special case AND the generic that subsumes it, then orphaning the
special case — the `TrilinearUniversal` pattern; or proving one proposition in
two modules — the `Stab-normal-when-fixed` pattern).

For each newly-ADDED .agda module in the staged set it reports:

  • imported-by-0 — the module is imported by no other module. Confirm it is an
    intended capstone/leaf, NOT a built-then-orphaned rung. (Most leaves are
    legitimate terminal theorems/hubs; this just forces the conscious check
    that would have caught the dead rung.)

  • def-name overlap — a top-level definition whose NAME also exists in another
    module. The name-based gates (decl_shape_tag / import-shape) handle the
    same-name case for ambiguity tagging; here it is a *collapse* hint: if it is
    the SAME proposition, derive/import instead of re-proving.

It NEVER blocks (advisory only; exits 0). The deeper, same-content-different-NAME
duplicate check is `python jea/metalanguage/jea_pysim.py --cluster` (too heavy to
run every commit) — pointed at, not run, from here.
"""

from __future__ import annotations
import re
import subprocess
import sys
from pathlib import Path


def sh(*args: str) -> str:
    return subprocess.run(args, capture_output=True, text=True).stdout


def repo_root() -> Path:
    return Path(sh("git", "rev-parse", "--show-toplevel").strip())


def staged_added_agda(root: Path) -> list[Path]:
    out = sh("git", "diff", "--cached", "--name-only", "--diff-filter=A", "--", "*.agda")
    return [root / line for line in out.splitlines() if line.strip()]


# agda/Substrate/A/B.agda  ->  Substrate.A.B   (the module path importers use)
def module_path(root: Path, f: Path) -> str | None:
    try:
        rel = f.relative_to(root / "agda")
    except ValueError:
        return None
    return str(rel.with_suffix("")).replace("/", ".")


_DECL = re.compile(r"^([^\s:(){}@]+)\s*:")
_KEYWORDS = {"module", "open", "import", "record", "data", "infix", "infixl",
             "infixr", "private", "postulate", "variable", "syntax", "field",
             "mutual", "where", "renaming", "using", "hiding", "--", "{-#"}


def top_level_names(f: Path) -> list[str]:
    names = []
    for line in f.read_text(errors="replace").splitlines():
        if not line or line[0].isspace():
            continue           # indented => not a top-level decl
        m = _DECL.match(line)
        if m and m.group(1) not in _KEYWORDS and not m.group(1).startswith("-"):
            names.append(m.group(1))
    return names


def importers(root: Path, modpath: str, self_file: Path) -> int:
    # `import Substrate.A.B` (open import / import), with a path boundary so
    # Substrate.A.B does not match Substrate.A.BC.
    pat = re.compile(r"\bimport\s+" + re.escape(modpath) + r"(?:\s|$)")
    n = 0
    for g in (root / "agda").rglob("*.agda"):
        if g == self_file:
            continue
        try:
            if any(pat.search(l) for l in g.read_text(errors="replace").splitlines()):
                n += 1
        except OSError:
            pass
    return n


def name_overlaps(root: Path, names: list[str], self_file: Path) -> dict[str, list[str]]:
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
            if any(pat.match(l) for l in lines):
                hits[n].append(rel)
    return {n: ms for n, ms in hits.items() if ms}


def main() -> int:
    root = repo_root()
    added = staged_added_agda(root)
    if not added:
        return 0   # nothing new — silent no-op (the common case)

    findings: list[str] = []
    for f in added:
        if not f.exists():
            continue
        mp = module_path(root, f)
        if mp is None:
            continue
        imp = importers(root, mp, f)
        if imp > 0:
            continue   # consumed — not an orphan; no advisory
        names = top_level_names(f)
        overlaps = name_overlaps(root, names, f)
        note = [f"  • {mp} — imported-by-0 (a leaf)."]
        if overlaps:
            note.append("    def-name overlap (possible duplicate/parallel-rung — "
                         "collapse if it's the same proposition):")
            for n, ms in sorted(overlaps.items()):
                shown = ", ".join(sorted(set(ms))[:3])
                note.append(f"      {n}  also in: {shown}")
        else:
            note.append("    confirm it is an intended capstone/leaf, NOT a "
                        "built-then-orphaned rung (the TrilinearUniversal pattern).")
        findings.append("\n".join(note))

    if findings:
        print("collapse-check advisory (Ⓖ, non-blocking) — newly-added modules "
              "imported by nothing:")
        print("\n".join(findings))
        print("  → if any is subsumed by a more-general module, derive/collapse it; "
              "`python jea/metalanguage/jea_pysim.py --cluster` finds same-content "
              "duplicates under a different name.")
    return 0   # ADVISORY: never blocks


if __name__ == "__main__":
    sys.exit(main())
