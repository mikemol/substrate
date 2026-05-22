"""Percentile-depth clustering.

For each file, compute its sorted list of pairwise geometric-mean
similarities against every other file. Pick a per-file threshold at
the Nth percentile of THAT file's match scores: this gives every file
its own local "best neighbourhood" of size roughly (100-N)% of the
corpus. Build a graph where (a, b) is an edge iff each file ranks the
other inside its own best-Nth-percentile neighbourhood — mutual
nearest neighbours under a per-file rank cutoff. Connected components
of that graph are clusters.

Why per-file thresholds and not a single global threshold:
  Different files sit in regions of different density. A global cutoff
  at score s rewards files that have many easy neighbours (boilerplate
  shims) and starves files in genuinely sparse regions (single-purpose
  proofs whose only structural twins still sit only at moderate
  scores). The per-file percentile normalises for local density so a
  cluster shows up wherever a file's *best* neighbours mutually
  recognise each other, regardless of the absolute score level.

Mutual-NN is intentionally more conservative than directed-NN: it
filters out one-sided "this is the best I could find" matches between
otherwise-dissimilar files.
"""

from __future__ import annotations

import math
from collections import defaultdict
from itertools import combinations
from pathlib import Path

from .similarity import pair_similarity, profile
from .tokenize import read_anonymized


def _union_find_components(
    nodes: list[Path], edges: list[tuple[Path, Path]]
) -> list[list[Path]]:
    """Union-find over `nodes`, merging endpoints of every edge.
    Returns components sorted by size descending; ties by min path string.
    """
    parent: dict[Path, Path] = {n: n for n in nodes}

    def find(x: Path) -> Path:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: Path, y: Path) -> None:
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry

    for a, b in edges:
        union(a, b)

    groups: dict[Path, list[Path]] = defaultdict(list)
    for n in nodes:
        groups[find(n)].append(n)

    return sorted(
        (sorted(g) for g in groups.values()),
        key=lambda g: (-len(g), str(g[0])),
    )


def cluster_by_percentile(
    paths: list[Path],
    percentile: float,
    *,
    anonymize_patterns: list[tuple[str, str]] | None = None,
    min_score: float = 0.0,
    min_cluster_size: int = 2,
    min_cohesion: float = 0.0,
) -> None:
    """Cluster files by per-file Nth-percentile mutual-nearest-neighbour graph.

    percentile: e.g. 90 means "each file's top-10% match scores."
    min_score: also require the edge's pairwise score >= this floor.
    min_cluster_size: hide singleton (or smaller) components.
    min_cohesion: after components form via union-find, drop any whose
      MEDIAN intra-cluster pairwise score is below this. Defends against
      weak-chain smearing — when components form by union-find, the
      median intra-cluster score is the test that the cluster is really
      a clique-like region and not a chain of marginal pairs.
    """
    if not (0 < percentile < 100):
        raise ValueError(f"percentile must be in (0, 100); got {percentile}")

    n = len(paths)
    if n < 2:
        print("# Need at least two files for clustering.")
        return

    profiles = {
        p: profile(read_anonymized(p, anonymize_patterns)) for p in paths
    }

    # All pairwise scores; build per-file neighbour score lists too.
    pair_score: dict[frozenset[Path], float] = {}
    per_file_scores: dict[Path, list[float]] = {p: [] for p in paths}
    for a, b in combinations(paths, 2):
        geo, _ = pair_similarity(profiles[a], profiles[b])
        pair_score[frozenset({a, b})] = geo
        per_file_scores[a].append(geo)
        per_file_scores[b].append(geo)

    # Per-file Nth-percentile threshold. The Nth percentile of file F's
    # match scores admits roughly the top (100-N)% of F's neighbours.
    per_file_threshold: dict[Path, float] = {}
    for p, scores in per_file_scores.items():
        scores_sorted = sorted(scores)
        # ceil so percentile=90 over 100 scores admits exactly the top 10.
        idx = min(
            len(scores_sorted) - 1,
            max(0, math.ceil(percentile / 100.0 * len(scores_sorted)) - 1),
        )
        per_file_threshold[p] = scores_sorted[idx]

    # Edge iff mutual: both files rank the other in their best Nth-pct.
    edges: list[tuple[Path, Path]] = []
    for a, b in combinations(paths, 2):
        s = pair_score[frozenset({a, b})]
        if s < min_score:
            continue
        if s >= per_file_threshold[a] and s >= per_file_threshold[b]:
            edges.append((a, b))

    components = _union_find_components(paths, edges)

    # Compute intra-cluster stats once; filter on size + cohesion floor.
    annotated: list[tuple[list[Path], float, float]] = []
    for cluster in components:
        if len(cluster) < min_cluster_size:
            continue
        intra_scores = [
            pair_score[frozenset({a, b})] for a, b in combinations(cluster, 2)
        ]
        median = (
            sorted(intra_scores)[len(intra_scores) // 2] if intra_scores else 0.0
        )
        mean = sum(intra_scores) / len(intra_scores) if intra_scores else 0.0
        if median < min_cohesion:
            continue
        annotated.append((cluster, mean, median))

    print(
        f"# Clusters at percentile={percentile} "
        f"(per-file mutual-NN, min_score={min_score}, "
        f"min_cohesion={min_cohesion})"
    )
    print(
        f"#   {n} files; {len(edges)} mutual-NN edges; "
        f"{len(annotated)} clusters passing size/cohesion filter; "
        f"{sum(1 for c in components if len(c) == 1)} singletons."
    )
    print()

    for i, (cluster, mean, median) in enumerate(annotated):
        print(
            f"## Cluster {i+1}  size={len(cluster)}  "
            f"mean={mean:.4f}  median={median:.4f}"
        )
        for path in cluster:
            print(f"  {path}")
        print()
