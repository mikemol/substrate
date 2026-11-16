# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""APSP COMMUNITY-CENTRIC reference -- the corpus data model, grounded from Drive (batch [AI-CORPUS-APSP]).

SOURCE (Drive, mikemol): "Implementation of APSP: A Community-Centric Approach" (1fEZnx7),
"Community-Centric APSP in PostgreSQL" (1iSNVUJ4), "Technical Discussion ... APSP" (1r9VyQ_J),
"Book III: Parallel Iterative APSP" folder (1z7Z6MO -> 1xd1kAF exploration, 1EMd5D4 annealing).
Every term below is WITNESSED in those docs (see .claude/cotype/chart/CHART.md), not reconstructed.

THIS IS A SEPARATE FACE OF APSP FROM apsp_ref.py:
  apsp_ref.py  = the DISTANCE-MATRIX face (min-plus segment-doubling + 2-hop). Computes d(i,j).
  apsp_community_ref.py = the corpus DATA-MODEL face (extent/path/community/dimension/ICAP). Computes the
    SAME shortest paths but via the community decomposition the corpus actually describes.
Conformance obligation (conform-don't-wrap): the community model's shortest paths MUST AGREE with apsp_ref's
distance matrix. The check cross-validates the two faces -- a genuine two-route witness (Rung 3): two
INDEPENDENT constructions of the same shortest-path object that CAN disagree if either is wrong.

GROUNDED VOCABULARY (source glosses):
  extent       = (start_node, end_node, path_length). The atomic unit; an edge is an extent of length 1.
  path         = a sequence of connected extents (a route).
  community    = THE fundamental unit: single edge | individual path | aggregation of interconnected paths.
                 Formed by MERGING smaller communities on a shared node. Hierarchical (parent1, parent2).
  dimension    = (community_id, extent): the longest NON-OVERLAPPING arterial paths covering all community
                 nodes without overlap -- the community's backbone. (canonical cover; subpaths referenced.)
  ICAP         = Inter-Community Arterial Path = transverse_path: an arterial path bridging DIFFERENT
                 communities; forms a higher-level community graph (communities=nodes, ICAPs=edges).
  two phases   = exploration (parallel discovery of paths from all nodes) + annealing (end-zone, geodesic-
                 preserving refinement: a shorter path between two end zones replaces the segment).

CONSERVATION (the witness this releases): the community MERGE TREE releases the trivial law "a shortest path
is found globally / atomically"; the carried witness is the MERGE LINEAGE (parent1,parent2 per community) --
which two sub-communities glued, on which shared node, to build each path. triviality-out (global-atomic) =
witness-in (the merge lineage). This is the SAME conservation as apsp_ref's segment split, in the data-model
face: community-merge-on-shared-node IS segment-gluing-at-shared-endpoint.

CANON+RESIDUE: the dimension cover is the CANONICAL form of a community (longest non-overlapping arterial
paths, no redundancy); it is LOSSY (drops which subpaths were merged). The residue is the merge lineage +
subpath index references. cover + residue = lossless (reconstruct any intra-community path).
"""
INF = float("inf")

# ─────────────────────────────────────────────────────────────────────────────
# extent: the atomic unit (start, end, length). An edge is an extent of length 1.
# ─────────────────────────────────────────────────────────────────────────────
def extent(start, end, length):
    return (start, end, length)

def extent_start(e): return e[0]
def extent_end(e):   return e[1]
def extent_len(e):   return e[2]

# ─────────────────────────────────────────────────────────────────────────────
# path: a sequence of connected extents. Connected = each extent's end is the next's start.
# ─────────────────────────────────────────────────────────────────────────────
def path_nodes(extents):
    """Reconstruct the node sequence of a path from its extent sequence."""
    if not extents:
        return []
    nodes = [extent_start(extents[0])]
    for e in extents:
        assert extent_start(e) == nodes[-1], "extents not connected (path invariant)"
        nodes.append(extent_end(e))
    return nodes

def path_length(extents):
    return sum(extent_len(e) for e in extents)

# ─────────────────────────────────────────────────────────────────────────────
# community: the fundamental unit. A community is built by MERGING on a shared node.
# We model a community as: id, the path it represents (extent seq), and parent lineage.
# An edge is a single-extent community with no parents. Merging two communities that
# share an endpoint node concatenates them into a longer community (the merge tree).
# ─────────────────────────────────────────────────────────────────────────────
class Community:
    _next_id = 0
    def __init__(self, extents, parent1=None, parent2=None):
        self.id = Community._next_id; Community._next_id += 1
        self.extents = tuple(extents)         # the path this community represents
        self.parent1 = parent1                # merge lineage (the conservation witness)
        self.parent2 = parent2
    def nodes(self):   return path_nodes(list(self.extents))
    def length(self):  return path_length(list(self.extents))
    def start(self):   return extent_start(self.extents[0])
    def end(self):     return extent_end(self.extents[-1])

def edge_community(u, v, w):
    """A single edge as a community of one extent (length 1 hop, weight w)."""
    return Community([extent(u, v, w)])

def apex_set(c):
    """The RECURSIVE apex set of a community = every interior (junction) vertex = the cone-apex hierarchy
    collected (cf. aspf_segment_ref.apex_set). Satisfies the inductive recurrence
        apex_set(merge(A,B)) = apex_set(A) ∪ {junction} ∪ apex_set(B).
    This recurrence IS the inductive step of the no-tangle construction (USER): a merge is a simple path iff
    its children are simple (IH) and their apex sets meet only at the junction. The interior-vertex reading."""
    ns = c.nodes()
    return frozenset(ns[1:-1])

def merge_communities(c1, c2):
    """Merge two communities that share a node (c1.end == c2.start): the gluing operation.

    HIERARCHICAL CONSTRUCTION (USER): a community is built ONLY from smaller communities that are adjacent
    subpaths of ONE simple host. The MIDPOINT<->ENDPOINT CHECK is the constructive operation that forecloses
    tangles: before abutting, the two pieces' RECURSIVE APEX SETS (= interior vertices, the cone-apex hierarchy)
    must meet only at the junction -- equivalently apex_set(c1) and apex_set(c2) are disjoint and neither free
    endpoint lands in the other. This is the inductive step: simplicity of the merge follows from simplicity of
    the children (IH) + apex-set disjointness, giving apex_set(merge) = apex_set(c1) ∪ {junction} ∪ apex_set(c2).

    THREE COUPLED FACTS (verified by construction, see register [AI-COMMUNITY-APEX-UNIFY]):
      (1) CHRONOLOGY: the check is well-defined only if the level below is already built (the children's apex
          sets must exist) -> shortest-to-longest construction order is load-bearing, not incidental.
      (2) SHARING: the apex set is memoized/shared on hash-consed communities (cf. aspf_ref intern); without
          maximal sharing, admitted tangles re-combine without bound (apex-only-without-sharing runs away).
      (3) INDUCTION: the recursive apex recurrence above IS the inductive hypothesis, not a bolted-on check.

    So the meet-condition is an INHERITED INVARIANT of one-hierarchy placement, not a runtime gate: on any
    community built by the hierarchy it always holds. It fires only on a hand-fed free-floating non-adjacent
    pair (e.g. 0-1-2 with 2-0-1), which is non-constructible. Junction-mismatch (different endpoints) is a
    usage error -> ValueError. Records parent lineage (parent1, parent2) = the conservation witness."""
    if c1.end() != c2.start():
        raise ValueError("merge requires a shared node (c1.end == c2.start)")
    # the midpoint<->endpoint check AS the recursive-apex comparison: the two pieces' apex sets (interior
    # vertices) plus free endpoints meet only at the junction. Equivalent to full node-disjointness-except-j.
    j = c1.end()
    if (set(c1.nodes()) & set(c2.nodes())) != {j}:
        shared = set(c1.nodes()) & set(c2.nodes())
        raise ValueError(
            f"non-constructible: recursive apex sets / endpoints of the two pieces share {shared}, not just "
            f"junction {j} -- they are not adjacent subpaths of one simple host (a tangle would result)")
    return Community(c1.extents + c2.extents, parent1=c1.id, parent2=c2.id)

def merge_lineage(c):
    """The residue: which sub-communities glued to build this one (the parent tree)."""
    return (c.parent1, c.parent2)

def build_from_host(host, weights=None):
    """The CONSTRUCTIVE source of communities (the hierarchy): recursively split a SIMPLE host path at
    an interior node into a binary merge-tree. Because subpaths of a simple path are simple and meet
    only at the split point, every community produced is simple and every merge satisfies the
    junction-only-meet invariant BY CONSTRUCTION -- simplicity is a theorem of this builder, not a check.
    host: a list of nodes forming a simple path; weights: optional dict (u,v)->w (default 1)."""
    assert len(host) == len(set(host)), "host must be a simple path (single-occurrence-in-one-tree)"
    assert len(host) >= 2, "host needs at least one edge"
    w = weights or {}
    def rec(seg):
        if len(seg) == 2:
            return edge_community(seg[0], seg[1], w.get((seg[0], seg[1]), 1))
        mid = len(seg) // 2
        return merge_communities(rec(seg[:mid+1]), rec(seg[mid:]))
    return rec(list(host))

# ─────────────────────────────────────────────────────────────────────────────
# The two-phase community-centric APSP. Builds shortest paths shortest-to-longest by
# merging communities on shared nodes (exploration), keeping only the geodesic per
# (start,end) pair (annealing = end-zone geodesic preservation). Returns, for each
# reachable (u,v), the shortest community (the path + its merge lineage).
# ─────────────────────────────────────────────────────────────────────────────
def community_apsp(n, edges):
    """edges: list of (u, v, w). Returns dict (u,v) -> Community (the shortest path), built by
    merge-on-shared-node, annealed to geodesics. Shortest-to-longest = single-shared-vertex keeps
    every compound a simple shortest path BY CONSTRUCTION (no shortcut exists before the two halves
    are themselves shortest)."""
    Community._next_id = 0
    # EXPLORATION: seed with edge-communities (paths of length 1), parallel over all nodes.
    best = {}   # (u,v) -> Community, the current shortest known
    for (u, v, w) in edges:
        c = edge_community(u, v, w)
        key = (u, v)
        if key not in best or c.length() < best[key].length():
            best[key] = c
    for u in range(n):                          # zero-length self community
        if (u, u) not in best:
            best[(u, u)] = Community([extent(u, u, 0)])
    # ANNEALING: repeatedly merge on shared nodes, keep geodesics (end-zone refinement).
    # A shorter path between two end zones (u..k and k..v) replaces the segment u..v.
    changed = True
    while changed:
        changed = False
        items = list(best.items())
        for (a, k1), ca in items:
            for (k2, b), cb in items:
                if k1 != k2:
                    continue
                if ca.length() + cb.length() == INF:
                    continue
                merged_len = ca.length() + cb.length()
                key = (a, b)
                if key not in best or merged_len < best[key].length():
                    # overlap avoidance (Book III §5.1): only glue if the two share just the junction;
                    # a merge that would revisit a node is not generated (prevents cycles).
                    if set(ca.nodes()) & set(cb.nodes()) != {k1}:
                        continue
                    best[key] = merge_communities(ca, cb)   # glue on shared node k1==k2
                    changed = True
    return best

# ─────────────────────────────────────────────────────────────────────────────
# dimension: the longest non-overlapping arterial cover of a community's nodes.
# Given a set of shortest paths (communities), the dimension cover is the minimal set
# of longest paths that touch every node without overlap. We compute it as a canonical
# greedy cover (longest-first), which is the corpus's "longest non-overlapping arterial paths".
# ─────────────────────────────────────────────────────────────────────────────
def dimension_cover(communities):
    """Canonical cover: pick longest arterial paths first, skip any whose nodes are already
    covered (non-overlapping). Returns the cover (canonical) -- subpaths are referenced, not stored."""
    ordered = sorted(communities, key=lambda c: -c.length())
    covered = set()
    cover = []
    for c in ordered:
        ns = set(c.nodes())
        if ns & covered:
            continue                  # overlaps an already-chosen arterial path -> skip (non-overlapping)
        cover.append(c)
        covered |= ns
    return cover

# ─────────────────────────────────────────────────────────────────────────────
# ICAP: an arterial path whose endpoints lie in DIFFERENT communities. Given a node->community
# assignment, an ICAP is a shortest path (u,v) with community(u) != community(v). The community
# graph has communities as nodes and ICAPs as edges.
# ─────────────────────────────────────────────────────────────────────────────
def icaps(best, node_community):
    """node_community: dict node -> community label. Returns the inter-community arterial paths."""
    out = []
    for (u, v), c in best.items():
        if u == v:
            continue
        if node_community.get(u) != node_community.get(v):
            out.append(((node_community.get(u), node_community.get(v)), c))
    return out

# ─────────────────────────────────────────────────────────────────────────────
# Conformance bridge: the community model's shortest-path distances MUST equal apsp_ref's.
# ─────────────────────────────────────────────────────────────────────────────
def distance_matrix(n, best):
    """Project the community model down to a distance matrix (for cross-validation with apsp_ref)."""
    D = [[INF]*n for _ in range(n)]
    for u in range(n):
        D[u][u] = 0
    for (u, v), c in best.items():
        if c.length() < D[u][v]:
            D[u][v] = c.length()
    return D
