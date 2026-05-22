"""Genericization score: per-scale shared/total ratio + orbit verdict.

A summary view that converts the multi-scale similarity-cluster
analysis into a single actionable verdict: STRONG / PARTIAL / WEAK
orbit candidate. Strong-orbit clusters are ready for parametric
consolidation; weak-orbit clusters are structurally divergent.

The verdict uses the MAXIMUM shared-ratio across scales rather than
their geometric mean: a single high scale (e.g., 90% block-shared)
is enough to indicate "consolidate me" even if char3 noise pulls
the geometric mean down.
"""

from __future__ import annotations

from pathlib import Path

from .similarity import SCALE_NAMES
from .template import template_at_scale


STRONG_ORBIT_THRESHOLD = 0.80
PARTIAL_ORBIT_THRESHOLD = 0.50


def genericization_score(
    paths: list[Path],
) -> dict[str, tuple[int, int, float]]:
    """Per scale, return (shared_count, total_count, ratio).

    shared_count = units appearing in EVERY file
    total_count  = distinct units across all files
    ratio        = shared / total ∈ [0, 1]
    """
    n = len(paths)
    out: dict[str, tuple[int, int, float]] = {}
    for scale in SCALE_NAMES:
        unit_files = template_at_scale(paths, scale)
        total = len(unit_files)
        shared = sum(1 for fs in unit_files.values() if len(fs) == n)
        ratio = (shared / total) if total else 0.0
        out[scale] = (shared, total, ratio)
    return out


def verdict(scores: dict[str, tuple[int, int, float]]) -> str:
    """Classify the file-set's orbit-readiness based on max scale-ratio."""
    if not scores:
        return "NO DATA"
    max_ratio = max(r for _, _, r in scores.values())
    if max_ratio >= STRONG_ORBIT_THRESHOLD:
        return f"STRONG orbit candidate ({max_ratio*100:.1f}% max shared)"
    if max_ratio >= PARTIAL_ORBIT_THRESHOLD:
        return f"PARTIAL orbit ({max_ratio*100:.1f}% max shared)"
    return f"WEAK orbit ({max_ratio*100:.1f}% max shared)"


def print_score(paths: list[Path]) -> None:
    """Print genericization score with per-scale bars + verdict line."""
    n = len(paths)
    print(f"Genericization score over {n} files:")
    for p in paths:
        print(f"  {p}")
    print()
    scores = genericization_score(paths)
    print(f"  {'scale':6}  {'shared':>6}/{'total':<6}  {'ratio':>5}    bar")
    for scale, (shared, total, ratio) in scores.items():
        bar = "█" * int(ratio * 20)
        print(f"  {scale:6}  {shared:>6}/{total:<6}  {ratio*100:5.1f}%  {bar}")
    print()
    print(f"  → {verdict(scores)}")
