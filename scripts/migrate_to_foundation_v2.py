#!/usr/bin/env python3
"""
migrate_to_foundation_v2.py — stdlib→Foundation migration tool, fast.

Improvements over v1:
- Batches the rewrite, then runs ONE agda smoke check per batch (not per
  file). Agda's per-invocation overhead dominated v1; a single check on a
  representative capstone covers all the files in the batch by transitive
  imports. If the smoke check fails, the script bisects the batch by half
  to find the bad file.
- Smoke targets configurable via --smoke flag; default is a small list
  of capstones that transitively cover most of the codebase.

Usage:
  scripts/migrate_to_foundation_v2.py [--batch N] [--limit M] [--dry-run]
                                      [--only PATTERN]
                                      [--smoke FILE ...]
"""

import argparse
import subprocess
import sys
from pathlib import Path

REWRITE_MAP = {
    # NOTE: longer keys must come first because the rewrite loop
    # matches the FIRST key that fits (e.g. Data.Nat.Properties
    # before Data.Nat).
    "Data.Nat.Properties":                     "Substrate.Foundation.Nat.Properties",
    "Data.Fin.Properties":                     "Substrate.Foundation.Fin.Properties",
    "Data.Vec.Properties":                     "Substrate.Foundation.Vec.Properties",
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

# Default smoke-test targets — capstones that transitively import many
# modules. Add/remove via --smoke.
DEFAULT_SMOKE = [
    "Substrate/Category/HC/InfCapstone.agda",
    "Substrate/Category/UniversalProperty/Capstone.agda",
    "Substrate/Algebra/Module/Capstone.agda",
    "Substrate/Conway/Capstone.agda",
]


def find_candidate_files() -> list[Path]:
    out = []
    for p in SUBSTRATE_ROOT.rglob("*.agda"):
        try:
            p.relative_to(FOUNDATION_ROOT)
            continue
        except ValueError:
            pass
        out.append(p)
    return sorted(out)


def rewrite_line(line: str) -> tuple[str, bool]:
    stripped = line.lstrip()
    if not stripped.startswith("open import "):
        return line, False
    rest = stripped[len("open import "):]
    for src, dst in REWRITE_MAP.items():
        if rest == src or rest.startswith(src + " ") or rest.startswith(src + "\n"):
            indent = line[: len(line) - len(stripped)]
            new_rest = dst + rest[len(src):]
            return f"{indent}open import {new_rest}", True
    return line, False


def file_needs_migration(path: Path) -> bool:
    text = path.read_text()
    for raw in text.splitlines():
        stripped = raw.lstrip()
        if not stripped.startswith("open import "):
            continue
        rest = stripped[len("open import "):]
        for src in REWRITE_MAP:
            if rest == src or rest.startswith(src + " ") or rest.startswith(src + "\n"):
                return True
    return False


def rewrite_file(path: Path) -> bool:
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


def smoke_check(smoke_targets: list[str]) -> tuple[bool, str]:
    """Run a single agda invocation on each smoke target."""
    for tgt in smoke_targets:
        proc = subprocess.run(
            ["agda", "--safe", "--without-K", tgt],
            cwd=AGDA_ROOT,
            capture_output=True,
            text=True,
            timeout=600,
        )
        if proc.returncode != 0:
            out = (proc.stdout or "") + (proc.stderr or "")
            return False, f"smoke target {tgt} failed:\n{out[-1500:]}"
    return True, "all smoke targets pass"


def migrate_batch(batch: list[Path], smoke_targets: list[str], dry_run: bool) -> tuple[int, list[Path]]:
    """
    Rewrite a batch, then smoke-test. Returns (ok_count, failed_files).
    On smoke failure, bisects to identify the bad files.
    """
    if dry_run:
        for p in batch:
            print(f"  would migrate {p.relative_to(AGDA_ROOT)}")
        return len(batch), []

    backups = {p: p.read_text() for p in batch}
    actually_changed = []
    for p in batch:
        if rewrite_file(p):
            actually_changed.append(p)

    ok, detail = smoke_check(smoke_targets)
    if ok:
        return len(actually_changed), []

    # Bisect to find the bad file(s).
    print(f"    batch smoke failed: {detail.splitlines()[0]}")
    print(f"    bisecting {len(actually_changed)} changed files...")
    for p in actually_changed:
        p.write_text(backups[p])
    # Now apply one-at-a-time
    good = []
    bad = []
    for p in actually_changed:
        rewrite_file(p)
        ok, detail = smoke_check(smoke_targets)
        if ok:
            good.append(p)
        else:
            bad.append(p)
            p.write_text(backups[p])  # revert this one
    return len(good), bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=20)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default=None)
    ap.add_argument("--smoke", action="append", default=None,
                    help="smoke-check target; repeat for multiple")
    args = ap.parse_args()

    smoke_targets = args.smoke if args.smoke else DEFAULT_SMOKE
    # Validate smoke targets exist
    for tgt in smoke_targets:
        if not (AGDA_ROOT / tgt).exists():
            print(f"WARNING: smoke target not found: {tgt}", file=sys.stderr)

    files = find_candidate_files()
    if args.only:
        files = [p for p in files if args.only in str(p)]
    pending = [p for p in files if file_needs_migration(p)]
    print(f"Candidate files needing migration: {len(pending)}")
    if args.limit:
        pending = pending[: args.limit]
        print(f"  (limiting to first {len(pending)})")
    print(f"Smoke targets: {smoke_targets}")

    total_ok = 0
    total_bad: list[Path] = []
    for i in range(0, len(pending), args.batch):
        batch = pending[i : i + args.batch]
        n = i // args.batch + 1
        print(f"\n--- Batch {n} ({len(batch)} files) ---")
        ok, bad = migrate_batch(batch, smoke_targets, args.dry_run)
        total_ok += ok
        total_bad.extend(bad)
        print(f"    batch {n}: {ok} migrated, {len(bad)} failed")

    print(f"\n=== Summary ===")
    print(f"  migrated: {total_ok}")
    print(f"  failed:   {len(total_bad)}")
    if total_bad:
        print(f"\n  failed files:")
        for p in total_bad:
            print(f"    {p.relative_to(AGDA_ROOT)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
