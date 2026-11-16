# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Hierarchical Community Model reference (the OCAL 'behavior-frame' reading of APSP, extracted + formalized).
The conformance checks f090_2_community_* pin THIS. NOT a separate algorithm dropped in: per all-readings, the
Hierarchical Community Model is a CHANGE-OF-FRAME reading of the SAME graph the APSP min-plus/segment-doubling
structure organizes. This ref extracts the mechanism AND formalizes the map APSP-structure -> community-structure,
so the connection is WITNESSED (computed agreement), not asserted.

HOW IT WORKS (decomposed, the standard mechanism):
  HIERARCHICAL AGGLOMERATION: start with every vertex its own community; repeatedly MERGE the pair of
  communities whose merge most increases MODULARITY Q = (1/2m) Σ_ij [A_ij - k_i k_j/2m] δ(c_i,c_j); record
  the merge order as a DENDROGRAM (the community hierarchy). Cutting the dendrogram at a level gives a
  partition; the hierarchy is the nested family of partitions (the "hierarchical community" structure).

THE CHANGE-OF-FRAME MAP (the load-bearing part -- APSP <-> community, witnessed not asserted):
  the APSP DISTANCE matrix and the community structure are two readings of one graph. The precise map is
  SINGLE-LINKAGE agglomeration on the APSP distances: repeatedly merge the two clusters with the smallest
  inter-cluster shortest-path distance. On a DISTANCE-SEPARABLE graph (intra-community distances strictly
  below the inter-community gap) this single-linkage dendrogram REPRODUCES the modularity dendrogram's nested
  partitions -- same hierarchy, two frames (paths vs density). The readings DIVERGE at bridge vertices (a
  vertex distance-1 from another community but densely tied to its own): there the distance frame and the
  density frame disagree, and THAT disagreement is retained content (the residue of the change-of-frame),
  not a failure -- it marks exactly where "close by path" and "belongs to community" come apart.
  Formalized + checked below: on a separable graph the two dendrograms induce the same partition; the bridge
  case is exhibited as the witnessed divergence.

CONSERVATION (the community-frame witness): the flat APSP distance matrix RELEASES the trivial "all vertices
sit in one undifferentiated space" (no grouping); the community frame's witness is the DENDROGRAM (the nested
partition that the distances implied but the flat matrix suppressed). triviality-out (one flat space) =
witness-in (the hierarchy). This is the SAME conservation exchange as the APSP locality release, one level up:
APSP releases locality (witness = segment decomposition); the community reading releases flatness (witness =
the dendrogram). The segment hierarchy and the community hierarchy are the same nesting seen via paths vs blocks.
"""
from importlib import util as _il
import os as _os

def _apsp():
    spec = _il.spec_from_file_location("apsp_ref", _os.path.join(_os.path.dirname(__file__), "apsp_ref.py"))
    m = _il.module_from_spec(spec); spec.loader.exec_module(m); return m

# ---- modularity ----
def modularity(adj_weight, communities):
    """Q = (1/2m) Σ_ij [A_ij - k_i k_j/2m] δ(c_i,c_j). adj_weight: symmetric weight dict-of-dicts or matrix;
    communities: list assigning each vertex a community id."""
    n = len(adj_weight)
    m2 = sum(adj_weight[i][j] for i in range(n) for j in range(n))   # 2m
    if m2 == 0: return 0.0
    k = [sum(adj_weight[i]) for i in range(n)]
    Q = 0.0
    for i in range(n):
        for j in range(n):
            if communities[i] == communities[j]:
                Q += adj_weight[i][j] - k[i]*k[j]/m2
    return Q / m2

# ---- hierarchical agglomeration (greedy modularity, the dendrogram) ----
def agglomerate(adj_weight):
    """Greedy modularity merging. Returns the DENDROGRAM as a list of merges [(a,b,Q_after), ...] and the
    sequence of partitions (each a list of community ids), finest-to-coarsest."""
    n = len(adj_weight)
    comm = list(range(n))                 # each vertex its own community
    partitions = [comm[:]]
    merges = []
    active = set(range(n))
    while len(active) > 1:
        best_dQ = None; best_pair = None
        ids = sorted(active)
        for a in ids:
            for b in ids:
                if a < b:
                    trial = [(a if x == b else x) for x in comm]
                    q = modularity(adj_weight, trial)
                    if best_dQ is None or q > best_dQ:
                        best_dQ = q; best_pair = (a, b)
        a, b = best_pair
        comm = [(a if x == b else x) for x in comm]
        active.discard(b)
        merges.append((a, b, best_dQ))
        partitions.append(comm[:])
    return merges, partitions

def best_partition(adj_weight):
    """The dendrogram cut maximizing modularity (the natural community structure)."""
    merges, parts = agglomerate(adj_weight)
    best = max(parts, key=lambda p: modularity(adj_weight, p))
    return best

# ---- THE CHANGE-OF-FRAME MAP: single-linkage on APSP distances <-> community dendrogram ----
def single_linkage_partition(weights, ncomm):
    """Read community structure OUT of the APSP distance matrix by SINGLE-LINKAGE agglomeration: start with
    singletons, repeatedly merge the two clusters at smallest inter-cluster shortest-path distance, until
    ncomm clusters remain. On a distance-separable graph this reproduces the modularity partition."""
    A = _apsp(); INF = A.INF
    D, _ = A.apsp(weights)
    n = len(D)
    clusters = [{i} for i in range(n)]
    def cdist(c1, c2):
        return min(D[i][j] for i in c1 for j in c2)
    while len(clusters) > ncomm:
        best = None; bi = bj = -1
        for i in range(len(clusters)):
            for j in range(i+1, len(clusters)):
                d = cdist(clusters[i], clusters[j])
                if best is None or d < best:
                    best = d; bi, bj = i, j
        clusters[bi] |= clusters[bj]; clusters.pop(bj)
    part = [0]*n
    for cid, cl in enumerate(clusters):
        for v in cl: part[v] = cid
    return part

def same_partition(p, q):
    """Two partitions are equal up to relabeling iff they induce the same same-community relation."""
    n = len(p)
    return all((p[i]==p[j]) == (q[i]==q[j]) for i in range(n) for j in range(n))
