#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Would promoting a directory out of scratch/ hold? The policy as a predicate, not a paragraph.

⚑⚑⚑ THE THIRD DRAIN OF THE ⟡drain-arc. `promotion_report` in the refused gate held the rule the
operator placed in tooling on purpose (2026-08-01: *"the place to put it is in tooling, which
will surface such rules when they're violated … CLAUDE.md is not tooling"*). A candidate is
promotable when it meets what the promoted corpus already meets:

  1. no live `scratch/` reference — the gate's own invariant, applied to the candidate;
  2. it ADDS NO CENSUS KEYS under the gates the promoted corpus is held to, the mypy ratchet
     first among them: the promoted profile is DEFECT-shaped with no annotation debt, because
     being annotated is part of what promotion already means.

⚑⚑ RULE 2 WAS THE ORIGIN'S OWN LIVE SCRATCH DEPENDENCY. It reached the type census through
`sys.path.insert(0, …/scratch)` + `import pycodemod` — a runtime coupling on `scratch/` INSIDE
the gate that forbids exactly that, invisible to the gate because the gate does not scan
`scripts/`. The reuse-search fired before this module was written and landed:
`substrate.mypy_census.type_errors` is the packaged reader, with the same `__unrunnable__`
sentinel, so rule 2 is asked of the package and the insert is not carried.

⚑ IDEMPOTENT — "already promoted" is a SATISFIED condition, not a refusal (operator: *"that
should just be idempotent"*). The origin's first cut returned False for a candidate already in
ROOTS, so `--promotable jea` printed BLOCK — a predicate reporting its own success as a failure
cannot be used to CONVERGE on the state it describes.

⚑ RULE 1's WALK SKIPS FEWER DIRECTORIES THAN THE `--scope` CENSUS DOES — no `.edit-snapshots`
here — and both skip lists are substring tests. Kept verbatim: the differential is against the
origin's output, and widening this walk's skip would silently change a verdict.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import corpus, mypy_census
from substrate import scratch_refs as sr
from substrate.promoted import ROOTS

if TYPE_CHECKING:
    from pathlib import Path

# Directory-path fragments rule 1's walk skips. ⚑ SUBSTRING semantics, and narrower than
# `scratch_scope.SKIP` — see the header.
SKIP = (".venv", "__pycache__", ".git")

# The origin's rule-2 wording, kept so the differential holds.
_UNAVAILABLE = (
    "type census UNAVAILABLE — cannot certify rule 2 (an unmeasured candidate is not a clean one)"
)


@dataclass(frozen=True, slots=True)
class Verdict:
    """Whether the candidate is promotable, and every reason either way."""

    ok: bool
    reasons: tuple[str, ...]


def _files(base: Path) -> list[Path]:
    """Return every `.py` under `base` outside a skipped directory, in a deterministic order."""
    return sorted(p for p in base.rglob("*.py") if not any(s in str(p.parent) for s in SKIP))


def _live(base: Path, root: Path) -> str | None:
    """Return rule 1's reason when the candidate carries a live reference, else None."""
    live = [(path, hit) for path in _files(base) for hit in sr.scan_file(path).hits]
    if not live:
        return None
    first_path, first_hit = live[0]
    return (
        f"{len(live)} live scratch/ reference(s); first: "
        f"{first_path.relative_to(root)}:{first_hit.lineno}"
    )


def _census(candidate: str, root: Path) -> str | None:
    """Return rule 2's reason when the candidate would add type-census keys, else None."""
    rows = mypy_census.type_errors(corpus.py_files(candidate, root=root), root=root)
    if rows is None or mypy_census.UNRUNNABLE in rows:
        return _UNAVAILABLE
    if rows:
        return f"{len(rows)} type-census key(s) would be ADDED; e.g. {min(rows)}"
    return None


def report(candidate: str, root: Path) -> Verdict:
    """Decide whether `candidate` (a path relative to the tree `root`) is promotable, with reasons.

    ⚑ `root` IS REQUIRED (2026-09-24, no-ROOT rule): the entry point (`scratch_cli`, via `--root`)
    chooses the tree; this used to default to `corpus.ROOT`.
    """
    base = root / candidate
    if not base.is_dir():
        return Verdict(ok=False, reasons=(f"{candidate}: not a directory under the repo root",))
    if candidate in ROOTS:
        return Verdict(
            ok=True, reasons=(f"{candidate}: already promoted (in ROOTS) — nothing to do",)
        )
    reasons = [r for r in (_live(base, root), _census(candidate, root)) if r is not None]
    if reasons:
        return Verdict(ok=False, reasons=tuple(reasons))
    return Verdict(ok=True, reasons=(f"{candidate}: promotable",))


def render(candidate: str, verdict: Verdict) -> list[str]:
    """Render the `--promotable` report in the origin's words."""
    mark = "ok  " if verdict.ok else "BLOCK"
    lines = [f"  {mark}  {r}" for r in verdict.reasons]
    state = "PROMOTABLE" if verdict.ok else "NOT promotable"
    lines.append(
        f"{candidate}: {state} — promotion means adding it to ROOTS, after which every "
        f"gate the promoted corpus is held to applies to it too"
    )
    return lines
