#!/usr/bin/env python3
"""agda_stdlib_migrator: mechanize routine stdlib → substrate migrations.

Operates per-file. For trivial single-symbol migrations (Data.List → Word,
Data.Maybe → Foundation.Maybe, Data.Empty → Foundation.Empty, Data.Unit →
Foundation.Unit), it performs sed-style import rewriting + identifier rename.

NOT a full Agda parser. Doesn't decompose multi-lemma files. Caller still
must verify (agda --safe) and decompose where required.
"""
from __future__ import annotations
import argparse
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
AGDA_DIR = REPO_ROOT / "agda"


# (regex_to_match, replacement) for the import line.
# Foundation.List is universe-polymorphic; preferred over Coxeter.Word
# for the generic List-of-A use (Coxeter.Word is mono-universe).
RULES = [
    (
        re.compile(r"^open import Data\.List using \(List; \[\]; _∷_; length\)$", re.MULTILINE),
        "open import Substrate.Foundation.List using (List; []; _∷_)\nopen import Substrate.Foundation.List.Length using (length)",
    ),
    (
        re.compile(r"^open import Data\.List using \(List; \[\]; _∷_; foldl\)$", re.MULTILINE),
        "open import Substrate.Foundation.List using (List; []; _∷_; foldl)",
    ),
    (
        re.compile(r"^open import Data\.List using \(List; \[\]; _∷_; foldr\)$", re.MULTILINE),
        "open import Substrate.Foundation.List using (List; []; _∷_; foldr)",
    ),
    (
        re.compile(r"^open import Data\.List using \(List; \[\]; _∷_\)$", re.MULTILINE),
        "open import Substrate.Foundation.List using (List; []; _∷_)",
    ),
    (
        re.compile(r"^open import Data\.List using \(List\)$", re.MULTILINE),
        "open import Substrate.Foundation.List using (List)",
    ),
    # Data.Maybe (mono).
    (
        re.compile(r"^open import Data\.Maybe using \((.*?)\)$", re.MULTILINE),
        r"open import Substrate.Foundation.Maybe using (\1)",
    ),
    # Inline Data.Empty / Data.Unit (used inside where-clauses).
    (
        re.compile(r"^(\s*)open import Data\.Empty using \(⊥\)$", re.MULTILINE),
        r"\1open import Substrate.Foundation.Empty using (⊥)",
    ),
    (
        re.compile(r"^(\s*)open import Data\.Unit using \(⊤(?:; tt)?\)$", re.MULTILINE),
        r"\1open import Substrate.Foundation.Unit using (⊤; tt)",
    ),
    # Polymorphic Unit / Empty (used in higher-universe code).
    (
        re.compile(r"^open import Data\.Unit\.Polymorphic using \((.*?)\)$", re.MULTILINE),
        r"open import Substrate.Foundation.Unit.Polymorphic using (\1)",
    ),
    (
        re.compile(r"^open import Data\.Empty\.Polymorphic using \((.*?)\)$", re.MULTILINE),
        r"open import Substrate.Foundation.Empty.Polymorphic using (\1)",
    ),
]

# No identifier renames needed: Foundation.List exposes the same names
# (List / [] / _∷_) as stdlib's Data.List.
ID_RENAMES: list = []


def migrate_text(text: str) -> tuple[str, list[str]]:
    """Apply RULES + ID_RENAMES. Returns (new_text, applied_descriptions)."""
    applied: list[str] = []
    new = text
    list_was_imported = "Data.List" in new
    for rx, repl in RULES:
        prev = new
        new = rx.sub(repl, new)
        if new != prev:
            applied.append(rx.pattern[:60])
    # Only rename `List` → `Word` if Data.List was the source.
    if list_was_imported:
        for rx, repl in ID_RENAMES:
            prev = new
            new = rx.sub(repl, new)
            if new != prev:
                applied.append(f"id-rename {rx.pattern}")
    return new, applied


def verify_agda(path: Path) -> tuple[bool, str]:
    """Run `agda --safe <path>`. Return (success, output)."""
    rel = path.resolve().relative_to(AGDA_DIR)
    try:
        proc = subprocess.run(
            ["agda", "--safe", str(rel)],
            cwd=AGDA_DIR,
            capture_output=True,
            text=True,
            timeout=120,
        )
        ok = proc.returncode == 0
        return ok, (proc.stdout + proc.stderr)
    except subprocess.TimeoutExpired as exc:
        return False, f"timeout: {exc}"


def process_file(path: Path, *, write: bool, verify: bool) -> dict:
    text = path.read_text()
    new, applied = migrate_text(text)
    result = {"path": str(path), "applied": applied, "changed": new != text}
    if not applied:
        return result
    if write:
        path.write_text(new)
        if verify:
            ok, output = verify_agda(path)
            result["agda_ok"] = ok
            if not ok:
                result["agda_output"] = output[-2000:]
    return result


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="Agda files to migrate.")
    ap.add_argument("--write", action="store_true", help="Write changes (default: dry-run).")
    ap.add_argument("--verify", action="store_true", help="Run agda --safe after writing.")
    ap.add_argument("--quiet", action="store_true", help="Only print files that changed.")
    args = ap.parse_args(argv)

    results = []
    for raw in args.paths:
        p = Path(raw)
        if not p.exists():
            print(f"WARN: missing {p}", file=sys.stderr)
            continue
        results.append(process_file(p, write=args.write, verify=args.verify))

    for r in results:
        if args.quiet and not r.get("changed"):
            continue
        applied = ", ".join(r["applied"]) if r["applied"] else "no-change"
        verify_marker = ""
        if "agda_ok" in r:
            verify_marker = " ✓" if r["agda_ok"] else " ✗"
        print(f"{r['path']}: {applied}{verify_marker}")
        if r.get("agda_output") and not r.get("agda_ok"):
            print(r["agda_output"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
