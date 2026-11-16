#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Batched stdlib to Foundation migration: rewrite a batch, smoke-check, isolate failures.

The batched twin of `migrate_to_foundation.py`. That tool typechecks EVERY rewritten
file; agda's per-invocation overhead dominates, so this one rewrites a whole batch and
runs ONE smoke check over a few capstones that transitively cover most of the tree. When
the smoke check fails it reverts the batch and re-applies the rewrites one at a time to
find which file broke it.

Usage:

    scripts/migrate_to_foundation_v2.py [--batch N] [--limit M] [--dry-run]
                                        [--only PATTERN] [--smoke FILE ...]

⚑⚑ THE ISOLATION PASS IS WHY THIS IS NOT REDUNDANT WITH `make`. Batching trades away
per-file attribution, and the pass buys it back: the loop's product is *which rewrite
broke the tree*, plus that file reverted and the compiler's own text returned. A
tree-wide `make -C agda -j` answers "is the tree green" and can supply neither.

⚑ IT IS A LINEAR SCAN, NOT A BISECTION, AND THE OLD NAME SAID OTHERWISE. Re-applying
one file at a time costs N+1 smoke checks for a failing batch of N — the same order as
checking every file individually, so the batching wins only when batches PASS. A true
bisection would be log N and is not what this does; calling it `bisect` overstated it,
and a reader sizing a run off that word would size it wrong.

⚑⚑ THE SMOKE ROSTER IS VERIFIED BEFORE USE, BECAUSE TWO OF ITS FOUR DEFAULTS HAD
ALREADY BEEN DELETED. `Category/HC/InfCapstone.agda` and `Algebra/Module/Capstone.agda`
do not exist (the ⟡capstone-not-a-barrel arc removed them). `agda` on a missing file
exits nonzero, so `smoke_check` failed on its FIRST target no matter what the migration
did: every batch would report broken, every rewrite would be reverted, and the tool
would look like it was working. Nothing detected that — a stale path is invisible to
every linter, and the failure mode is a tool that runs and is uniformly wrong.

⚑ `absolute()`, NEVER `resolve()`: `PTH100` recommends `Path.resolve()` as
`os.path.abspath`'s replacement and it is NOT one — `resolve()` follows symlinks.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REWRITE_MAP = {
    # NOTE: longer keys must come first because the rewrite loop matches the FIRST key
    # that fits (e.g. Data.Nat.Properties before Data.Nat).
    "Data.Nat.Properties": "Substrate.Foundation.Nat.Properties",
    "Data.Fin.Properties": "Substrate.Foundation.Fin.Properties",
    "Data.Nat": "Substrate.Foundation.Nat",
    "Data.Fin": "Substrate.Foundation.Fin",
    "Data.Vec": "Substrate.Foundation.Vec",
    "Data.Product": "Substrate.Foundation.Product",
    "Data.Sum": "Substrate.Foundation.Sum",
    "Data.Unit": "Substrate.Foundation.Unit",
    "Data.Empty": "Substrate.Foundation.Empty",
    "Data.Bool": "Substrate.Foundation.Bool",
    "Function": "Substrate.Foundation.Function",
    "Relation.Binary.PropositionalEquality": "Substrate.Foundation.Eq",
    "Relation.Nullary": "Substrate.Foundation.Negation",
}

REPO_ROOT = Path(__file__).absolute().parent.parent
AGDA_ROOT = REPO_ROOT / "agda"
SUBSTRATE_ROOT = AGDA_ROOT / "Substrate"
FOUNDATION_ROOT = SUBSTRATE_ROOT / "Foundation"
MEMBUDGET = REPO_ROOT / "scripts" / "membudget"

# Default smoke targets — capstones that transitively import many modules. Override with
# --smoke. ⚑ VERIFIED AT STARTUP by `_present`, never assumed: a deleted target makes
# every batch read as broken.
DEFAULT_SMOKE = [
    "Substrate/Category/UniversalProperty/Capstone.agda",
    "Substrate/Conway/Capstone.agda",
]

_SMOKE_TIMEOUT_S = 600
_OUTPUT_TAIL = 1500
_OPEN_IMPORT = "open import "
_DEFAULT_BATCH = 5

# `auto` right-sizes the lease from peak-mem history — the shim's own default, and not a
# figure to restate here.
_LEASE_MB = "auto"


def find_candidate_files() -> list[Path]:
    """Return every `.agda` under `agda/Substrate`, excluding `Foundation/`."""
    out = []
    for p in SUBSTRATE_ROOT.rglob("*.agda"):
        try:
            p.relative_to(FOUNDATION_ROOT)
            continue
        except ValueError:
            out.append(p)
    return sorted(out)


def _matches(rest: str, src: str) -> bool:
    """Report whether an import tail names module `src` exactly."""
    return rest == src or rest.startswith((src + " ", src + "\n"))


def rewrite_line(line: str) -> tuple[str, bool]:
    """Rewrite one import line, returning (new_line, changed)."""
    stripped = line.lstrip()
    if not stripped.startswith(_OPEN_IMPORT):
        return line, False
    rest = stripped[len(_OPEN_IMPORT) :]
    for src, dst in REWRITE_MAP.items():
        if _matches(rest, src):
            indent = line[: len(line) - len(stripped)]
            return f"{indent}{_OPEN_IMPORT}{dst}{rest[len(src) :]}", True
    return line, False


def file_needs_migration(path: Path) -> bool:
    """Report whether the file imports anything named by a REWRITE_MAP key."""
    text = path.read_text(encoding="utf-8")
    for src in REWRITE_MAP:
        marker = f"{_OPEN_IMPORT}{src}"
        if marker not in text:
            continue
        for raw in text.splitlines():
            if raw.lstrip().startswith(marker) and _matches(raw.lstrip()[len(_OPEN_IMPORT) :], src):
                return True
    return False


def rewrite_file(path: Path) -> bool:
    """Rewrite the file's imports in place; return whether any line changed."""
    text = path.read_text(encoding="utf-8")
    new_lines = []
    changed = False
    for line in text.splitlines(keepends=True):
        new_line, did = rewrite_line(line)
        new_lines.append(new_line)
        changed = changed or did
    if changed:
        path.write_text("".join(new_lines), encoding="utf-8")
    return changed


def missing_smoke(targets: list[str]) -> list[str]:
    """Return the smoke targets that do not exist on disk.

    ⚑ A DELETED TARGET IS INDISTINGUISHABLE FROM A BROKEN MIGRATION, which is what makes
    this check load-bearing rather than defensive. `agda` on a missing file exits
    nonzero exactly as it does on a type error, so `smoke_check` would report the batch
    broken, the isolation pass would revert every rewrite, and the run would look like a
    tree full of failures. Measured: two of four shipped defaults were already gone.
    """
    return [t for t in targets if not (AGDA_ROOT / t).exists()]


def smoke_check(smoke_targets: list[str]) -> tuple[bool, str]:
    """Typecheck each smoke target under a memory lease; return (ok, detail).

    ⚑ ROUTED THROUGH `membudget run`, which wraps ONE command — so the cgroup cap and
    the budget lease sit around the same process whose exit code is read, and a capstone
    that transitively pulls in most of the tree cannot take the machine down. A bare
    `agda` here was the OOM path the repo's standing rule exists to prevent.
    """
    for tgt in smoke_targets:
        argv = [
            str(MEMBUDGET),
            "run",
            _LEASE_MB,
            tgt,
            "--",
            "agda",
            "--safe",
            "--without-K",
            tgt,
        ]
        try:
            proc = subprocess.run(
                argv,
                cwd=AGDA_ROOT,
                capture_output=True,
                text=True,
                timeout=_SMOKE_TIMEOUT_S,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return False, f"smoke target {tgt} timed out: {exc}"
        if proc.returncode != 0:
            out = (proc.stdout or "") + (proc.stderr or "")
            return False, f"smoke target {tgt} failed:\n{out[-_OUTPUT_TAIL:]}"
    return True, "all smoke targets pass"


def _isolate(
    changed: list[Path], backups: dict[Path, str], smoke_targets: list[str]
) -> tuple[int, list[Path]]:
    """Re-apply rewrites one at a time to find which file broke the smoke check.

    ⚑ LINEAR, NOT LOGARITHMIC. Every file gets its own smoke check, so this costs N
    checks for a batch of N — the batching only pays when batches PASS. Stated plainly
    because the previous name (`bisect`) implied log N and would mis-size a run.
    """
    for p in changed:
        p.write_text(backups[p], encoding="utf-8")
    good: list[Path] = []
    bad: list[Path] = []
    for p in changed:
        rewrite_file(p)
        ok, _detail = smoke_check(smoke_targets)
        if ok:
            good.append(p)
        else:
            bad.append(p)
            p.write_text(backups[p], encoding="utf-8")  # revert this one
    return len(good), bad


def migrate_batch(
    batch: list[Path], smoke_targets: list[str], *, dry_run: bool
) -> tuple[int, list[Path]]:
    """Rewrite a batch and smoke-test it; isolate the failures. Returns (ok, bad)."""
    if dry_run:
        for p in batch:
            sys.stdout.write(f"  would migrate {p.relative_to(AGDA_ROOT)}\n")
        return len(batch), []

    backups = {p: p.read_text(encoding="utf-8") for p in batch}
    changed = [p for p in batch if rewrite_file(p)]

    ok, detail = smoke_check(smoke_targets)
    if ok:
        return len(changed), []

    sys.stdout.write(f"    batch smoke failed: {detail.splitlines()[0]}\n")
    sys.stdout.write(f"    isolating {len(changed)} changed file(s), one at a time...\n")
    return _isolate(changed, backups, smoke_targets)


def main() -> int:
    """Migrate in batches, smoke-checking each; exit 1 if any file was reverted."""
    ap = argparse.ArgumentParser(description="Batched stdlib->Foundation migration.")
    ap.add_argument(
        "--batch",
        type=int,
        default=_DEFAULT_BATCH,
        help=f"files per batch (default {_DEFAULT_BATCH})",
    )
    ap.add_argument("--limit", type=int, default=None, help="max files to process this run")
    ap.add_argument("--dry-run", action="store_true", help="report-only; do not modify files")
    ap.add_argument("--only", default=None, help="path substring filter")
    ap.add_argument(
        "--smoke", nargs="*", default=None, help="smoke targets, repo-relative under agda/"
    )
    args = ap.parse_args()

    # ⚑ NARROWED AT THE BOUNDARY: `argparse.Namespace` attributes are `Any`.
    opts: dict[str, object] = vars(args)
    raw_batch = opts.get("batch")
    batch_n = raw_batch if isinstance(raw_batch, int) and raw_batch > 0 else _DEFAULT_BATCH
    raw_limit = opts.get("limit")
    limit = raw_limit if isinstance(raw_limit, int) else None
    dry_run = opts.get("dry_run") is True
    raw_only = opts.get("only")
    only = raw_only if isinstance(raw_only, str) else None
    raw_smoke = opts.get("smoke")
    smoke = (
        [str(x) for x in raw_smoke]
        if isinstance(raw_smoke, list) and raw_smoke
        else list(DEFAULT_SMOKE)
    )

    # ⚑ REFUSE A STALE ROSTER RATHER THAN RUN AGAINST IT. Proceeding would revert every
    # rewrite and report a tree-wide failure that the migration did not cause.
    gone = missing_smoke(smoke)
    if gone:
        sys.stderr.write(
            "migrate-v2: REFUSING — smoke target(s) do not exist, so every batch would "
            "read as broken:\n"
        )
        for t in gone:
            sys.stderr.write(f"    missing {t}\n")
        sys.stderr.write("  Pass live targets with --smoke, or update DEFAULT_SMOKE.\n")
        return 2

    files = find_candidate_files()
    if only:
        files = [p for p in files if only in str(p)]
    pending = [p for p in files if file_needs_migration(p)]
    sys.stdout.write(f"Candidate files needing migration: {len(pending)}\n")
    if limit:
        pending = pending[:limit]
        sys.stdout.write(f"  (limiting to first {len(pending)})\n")

    total_ok = 0
    all_bad: list[Path] = []
    for i in range(0, len(pending), batch_n):
        chunk = pending[i : i + batch_n]
        sys.stdout.write(f"\n--- Batch {i // batch_n + 1} ({len(chunk)} files) ---\n")
        ok_n, bad = migrate_batch(chunk, smoke, dry_run=dry_run)
        total_ok += ok_n
        all_bad.extend(bad)

    sys.stdout.write("\n=== Summary ===\n")
    sys.stdout.write(f"  migrated: {total_ok}\n")
    sys.stdout.write(f"  reverted: {len(all_bad)}\n")
    if all_bad:
        sys.stdout.write("\n=== Reverted (smoke check failed) ===\n")
        for p in all_bad:
            sys.stdout.write(f"  {p.relative_to(AGDA_ROOT)}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
