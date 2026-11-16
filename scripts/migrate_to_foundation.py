#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Phase 1 stdlib to Foundation migration: rewrite, typecheck, revert on failure.

For each Agda file under `agda/Substrate` (excluding `agda/Substrate/Foundation`
itself) this rewrites `open import Data.Nat …` style lines to
`open import Substrate.Foundation.Nat …`, then typechecks the file. If the typecheck
fails, the file is REVERTED and the compiler's own error text is reported.

Usage:

    scripts/migrate_to_foundation.py [--batch N] [--limit M] [--dry-run]
                                     [--only PATTERN]

Files are processed in batches of N (default 5); after each batch it prints a summary.
Idempotent: files already importing only `Substrate.Foundation.*` are skipped.

⚑⚑ THE PER-FILE TYPECHECK IS THE POINT, AND IT IS NOT A SECOND BUILD SYSTEM. It looks
like one, and dispatching it to `make -C agda -j` — the right move for a whole-tree
verification — would DESTROY the capability. `make` answers *is the tree green*; this
loop answers *did THIS rewrite break THIS file*, and uses the answer to REVERT that one
file and hand back its error text. Attribution at the granularity of the edit, plus
rollback, is what the loop exists for; a tree-wide verdict cannot supply either. Same
reason `split_pipeline` keeps `isolate_check` alongside `make`.

⚑ WHAT WAS ACTUALLY WRONG WAS THE INVOCATION, NOT THE LOOP. The typecheck ran a bare
`agda` off PATH with a 180s timeout and NO memory cap — outside `membudget`, which is
the OOM-the-box path the repo's standing rule exists to prevent (a heavy compile can
take many GB; one took the machine down on 2026-06-19). Routing a single invocation
through `membudget run` preserves per-file attribution exactly, because membudget wraps
ONE command: the lease and the cgroup cap sit around the same process whose exit code
this function reads.

⚑ `absolute()`, NEVER `resolve()`. `PTH100` recommends `Path.resolve()` as
`os.path.abspath`'s replacement and it is NOT one — `resolve()` FOLLOWS SYMLINKS, so a
resolved `__file__` derives the symlink target's root rather than the invoking
checkout's. That substitution shipped to five repos on 2026-08-30.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

# Mapping: stdlib module name -> Substrate.Foundation replacement.
# Only the LEFT side of the "open import X using (...)" line changes.
REWRITE_MAP = {
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

_TYPECHECK_TIMEOUT_S = 180
_OUTPUT_TAIL = 2000
_SNIPPET_LINES = 6
_OPEN_IMPORT = "open import "

# ⚑ `auto` RIGHT-SIZES THE LEASE FROM PEAK-MEM HISTORY, which is the shim's own default
# and the reason not to pin a number here. A fixed lease would be a second authority for
# a figure `membudget` already derives per module, and this repo has measured that shape
# going stale by a factor of two.
_LEASE_MB = "auto"


def find_candidate_files() -> list[Path]:
    """Return every `.agda` under `agda/Substrate`, excluding `Foundation/`."""
    out = []
    for p in SUBSTRATE_ROOT.rglob("*.agda"):
        try:
            p.relative_to(FOUNDATION_ROOT)
            continue  # skip Foundation itself
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
    # The first whitespace-delimited token is the module name (dots included); each
    # REWRITE_MAP key is compared as an exact module prefix.
    for src, dst in REWRITE_MAP.items():
        if _matches(rest, src):
            indent = line[: len(line) - len(stripped)]
            new_rest = dst + rest[len(src) :]
            return f"{indent}{_OPEN_IMPORT}{new_rest}", True
    return line, False


def file_needs_migration(path: Path) -> bool:
    """Report whether the file imports anything named by a REWRITE_MAP key."""
    text = path.read_text(encoding="utf-8")
    for src in REWRITE_MAP:
        marker = f"{_OPEN_IMPORT}{src}"
        if marker not in text:
            continue
        # The match must begin a stripped line, not merely appear in the text.
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


def typecheck(path: Path) -> tuple[bool, str]:
    """Typecheck one file under a memory lease; return (ok, output tail).

    ⚑ ONE FILE, ONE INVOCATION, ONE LEASE - and that is deliberate. The caller reverts
    on failure and reports the compiler's text, so the verdict must belong to THIS file
    and no other. `membudget run` wraps exactly one command, so routing through it adds
    a cgroup `MemoryMax` and a budget lease WITHOUT changing whose exit code is read.

    ⚑ `check=False` IS EXPLICIT: a nonzero exit is the ANSWER this function returns, not
    an error to raise on. An implicit default is where a reader cannot tell a deliberate
    choice from an oversight (`PLW1510`).
    """
    rel = path.relative_to(AGDA_ROOT)
    argv = [
        str(MEMBUDGET),
        "run",
        _LEASE_MB,
        str(rel),
        "--",
        "agda",
        "--safe",
        "--without-K",
        str(rel),
    ]
    try:
        proc = subprocess.run(
            argv,
            cwd=AGDA_ROOT,
            capture_output=True,
            text=True,
            timeout=_TYPECHECK_TIMEOUT_S,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return False, f"timeout after {_TYPECHECK_TIMEOUT_S}s: {exc}"
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, out[-_OUTPUT_TAIL:]


def process_file(path: Path, *, dry_run: bool) -> tuple[str, str]:
    """Migrate one file and report (status, detail).

    Status is one of `skipped` / `ok` / `no-op` / `failed`.

    ⚑ THE REVERT IS THE LOOP'S REASON FOR EXISTING. A failed typecheck restores the
    file's exact prior bytes and returns the compiler's last lines, so a batch leaves
    the tree in the state it started in for every file that did not migrate cleanly -
    and the operator gets an error attributed to ONE rewrite rather than a red tree.
    """
    if not file_needs_migration(path):
        return "skipped", "no matching imports"
    if dry_run:
        return "ok", "(dry-run; not modified)"
    backup = path.read_text(encoding="utf-8")
    if not rewrite_file(path):
        return "no-op", "matched but no rewrite applied"
    ok, out = typecheck(path)
    if not ok:
        path.write_text(backup, encoding="utf-8")
        snippet = "\n".join(out.strip().splitlines()[-_SNIPPET_LINES:])
        return "failed", snippet
    return "ok", "rewritten + typechecks"


def _run_batches(
    pending: list[Path], *, batch: int, dry_run: bool
) -> tuple[dict[str, int], list[tuple[Path, str]]]:
    """Process every file in batches, returning the tally and the failures."""
    counts = {"ok": 0, "skipped": 0, "no-op": 0, "failed": 0}
    failures: list[tuple[Path, str]] = []
    marks = {"ok": "ok", "skipped": "-", "no-op": "-", "failed": "FAIL"}
    for i in range(0, len(pending), batch):
        chunk = pending[i : i + batch]
        sys.stdout.write(f"\n--- Batch {i // batch + 1} ({len(chunk)} files) ---\n")
        for p in chunk:
            rel = p.relative_to(AGDA_ROOT)
            status, detail = process_file(p, dry_run=dry_run)
            counts[status] += 1
            head = detail.splitlines()[0] if detail else ""
            sys.stdout.write(f"  {marks.get(status, '?')} {rel}  [{status}]  {head}\n")
            if status == "failed":
                failures.append((p, detail))
    return counts, failures


def main() -> int:
    """Rewrite, typecheck and report; exit 1 if any file failed and was reverted."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--batch", type=int, default=5, help="files per batch (default 5)")
    ap.add_argument("--limit", type=int, default=None, help="max files to process this run")
    ap.add_argument("--dry-run", action="store_true", help="report-only; do not modify files")
    ap.add_argument("--only", default=None, help="path substring filter (e.g. 'Algebra/')")
    args = ap.parse_args()

    # ⚑ NARROWED AT THE BOUNDARY. `argparse.Namespace` attributes are `Any`, so every
    # read through `args.` is an unchecked expression under this bar.
    opts: dict[str, object] = vars(args)
    raw_batch = opts.get("batch")
    batch = raw_batch if isinstance(raw_batch, int) and raw_batch > 0 else 5
    raw_limit = opts.get("limit")
    limit = raw_limit if isinstance(raw_limit, int) else None
    dry_run = opts.get("dry_run") is True
    raw_only = opts.get("only")
    only = raw_only if isinstance(raw_only, str) else None

    files = find_candidate_files()
    if only:
        files = [p for p in files if only in str(p)]

    pending = [p for p in files if file_needs_migration(p)]
    sys.stdout.write(f"Candidate files needing migration: {len(pending)}\n")
    if limit:
        pending = pending[:limit]
        sys.stdout.write(f"  (limiting to first {len(pending)})\n")

    counts, failures = _run_batches(pending, batch=batch, dry_run=dry_run)

    sys.stdout.write("\n=== Summary ===\n")
    for k, v in counts.items():
        sys.stdout.write(f"  {k}: {v}\n")
    if failures:
        sys.stdout.write("\n=== Failure details ===\n")
        for p, det in failures:
            sys.stdout.write(f"\n--- {p.relative_to(AGDA_ROOT)} ---\n{det}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
