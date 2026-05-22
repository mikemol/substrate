#!/usr/bin/env python3
"""
migrate_to_foundation.py — Phase 1 stdlib→Foundation migration tool.

For each Agda file under agda/Substrate (excluding agda/Substrate/Foundation
itself), rewrites `open import Data.Nat ...` style lines to
`open import Substrate.Foundation.Nat ...`, then typechecks the file. If
typecheck fails, the file is reverted.

Usage:
  scripts/migrate_to_foundation.py [--batch N] [--limit M] [--dry-run]
                                   [--only PATTERN]

The script processes files in batches of N (default 5); after each batch,
prints summary (passes / failures / total processed). Idempotent: files
already containing only Substrate.Foundation.* imports are skipped.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# Mapping: stdlib module name → Substrate.Foundation replacement
# Only the LEFT side of the "open import X using (...)" line changes.
REWRITE_MAP = {
    "Data.Nat":                                "Substrate.Foundation.Nat",
    "Data.Fin":                                "Substrate.Foundation.Fin",
    "Data.Vec":                                "Substrate.Foundation.Vec",
    "Data.Product":                            "Substrate.Foundation.Product",
    "Data.Sum":                                "Substrate.Foundation.Sum",
    "Data.Unit":                               "Substrate.Foundation.Unit",
    "Data.Empty":                              "Substrate.Foundation.Empty",
    "Data.Bool":                               "Substrate.Foundation.Bool",
    "Function":                                "Substrate.Foundation.Function",
    "Relation.Binary.PropositionalEquality":   "Substrate.Foundation.Eq",
    "Relation.Nullary":                        "Substrate.Foundation.Negation",
}

REPO_ROOT = Path(__file__).resolve().parent.parent
AGDA_ROOT = REPO_ROOT / "agda"
SUBSTRATE_ROOT = AGDA_ROOT / "Substrate"
FOUNDATION_ROOT = SUBSTRATE_ROOT / "Foundation"


def find_candidate_files() -> list[Path]:
    """All .agda files under agda/Substrate, excluding Foundation/."""
    out = []
    for p in SUBSTRATE_ROOT.rglob("*.agda"):
        try:
            p.relative_to(FOUNDATION_ROOT)
            continue  # skip Foundation itself
        except ValueError:
            pass
        out.append(p)
    return sorted(out)


def rewrite_line(line: str) -> tuple[str, bool]:
    """Rewrite one line; returns (new_line, changed?)."""
    stripped = line.lstrip()
    if not stripped.startswith("open import "):
        return line, False
    rest = stripped[len("open import "):]
    # First whitespace-delimited token is the module name (may include dots).
    # We compare against each REWRITE_MAP key as an exact module prefix.
    for src, dst in REWRITE_MAP.items():
        # match: "Data.Nat " (followed by space/newline) OR "Data.Nat$"
        if rest == src or rest.startswith(src + " ") or rest.startswith(src + "\n"):
            # Replace src with dst preserving leading whitespace + tail.
            indent = line[: len(line) - len(stripped)]
            new_rest = dst + rest[len(src):]
            return f"{indent}open import {new_rest}", True
    return line, False


def file_needs_migration(path: Path) -> bool:
    """Quick scan: does the file import anything from REWRITE_MAP keys?"""
    text = path.read_text()
    for src in REWRITE_MAP:
        marker = f"open import {src}"
        if marker in text:
            # match must be at the start of a stripped line
            for raw in text.splitlines():
                if raw.lstrip().startswith(marker):
                    rest = raw.lstrip()[len("open import "):]
                    if rest == src or rest.startswith(src + " ") or rest.startswith(src + "\n"):
                        return True
    return False


def rewrite_file(path: Path) -> bool:
    """Rewrite imports in-place; return True iff any line changed."""
    text = path.read_text()
    new_lines = []
    changed = False
    for line in text.splitlines(keepends=True):
        new_line, did = rewrite_line(line)
        new_lines.append(new_line)
        if did:
            changed = True
    if changed:
        path.write_text("".join(new_lines))
    return changed


def typecheck(path: Path) -> tuple[bool, str]:
    """Run agda on path; return (ok, last_lines_of_output)."""
    rel = path.relative_to(AGDA_ROOT)
    proc = subprocess.run(
        ["agda", "--safe", "--without-K", str(rel)],
        cwd=AGDA_ROOT,
        capture_output=True,
        text=True,
        timeout=180,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, out[-2000:]


def process_file(path: Path, dry_run: bool) -> tuple[str, str]:
    """
    Returns (status, detail):
      status ∈ {"skipped", "ok", "no-op", "failed"}
    """
    if not file_needs_migration(path):
        return "skipped", "no matching imports"
    if dry_run:
        return "ok", "(dry-run; not modified)"
    backup = path.read_text()
    changed = rewrite_file(path)
    if not changed:
        return "no-op", "matched but no rewrite applied"
    ok, out = typecheck(path)
    if not ok:
        path.write_text(backup)
        # capture trimmed failure
        snippet = "\n".join(out.strip().splitlines()[-6:])
        return "failed", snippet
    return "ok", "rewritten + typechecks"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=5,
                    help="files per batch (default 5)")
    ap.add_argument("--limit", type=int, default=None,
                    help="max files to process this run")
    ap.add_argument("--dry-run", action="store_true",
                    help="report-only; do not modify files")
    ap.add_argument("--only", default=None,
                    help="path substring filter (e.g. 'Algebra/')")
    args = ap.parse_args()

    files = find_candidate_files()
    if args.only:
        files = [p for p in files if args.only in str(p)]

    # Pre-filter to ones needing migration.
    pending = [p for p in files if file_needs_migration(p)]
    print(f"Candidate files needing migration: {len(pending)}")
    if args.limit:
        pending = pending[: args.limit]
        print(f"  (limiting to first {len(pending)})")

    counts = {"ok": 0, "skipped": 0, "no-op": 0, "failed": 0}
    failures = []

    for i in range(0, len(pending), args.batch):
        batch = pending[i : i + args.batch]
        print(f"\n--- Batch {i // args.batch + 1} ({len(batch)} files) ---")
        for p in batch:
            rel = p.relative_to(AGDA_ROOT)
            status, detail = process_file(p, args.dry_run)
            counts[status] += 1
            mark = {"ok": "✓", "skipped": "-", "no-op": "-",
                    "failed": "✗"}.get(status, "?")
            print(f"  {mark} {rel}  [{status}]  {detail.splitlines()[0] if detail else ''}")
            if status == "failed":
                failures.append((p, detail))

    print("\n=== Summary ===")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    if failures:
        print("\n=== Failure details ===")
        for p, det in failures:
            print(f"\n--- {p.relative_to(AGDA_ROOT)} ---")
            print(det)
        sys.exit(1)


if __name__ == "__main__":
    main()
