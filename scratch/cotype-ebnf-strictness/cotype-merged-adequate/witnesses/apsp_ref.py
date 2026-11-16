# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""APSP reference: All-Pairs Shortest Paths via min-plus segment-doubling + 2-hop query.
The conformance checks f090_2_apsp_* pin THIS. STRUCTURE-PRIMARY (per the banked f090_2_apsp_sources
correction): APSP = ALL-PAIRS SHORTEST PATHS. One Drive doc (DIR/APSP/OCAL Isomorphisms) renders it
"Adaptive Processing/Search Protocol" with a community/annealing mechanism -- that is the OCAL APPLICATION
EMBEDDING (a contextual relabel by acronym-match), RETAINED as a reading but NOT the structural mechanism.
The structural mechanism (gated in f090_2_apsp_doubling_lit) is min-plus doubling / 2-hop, and THAT is what
this reference computes. (all-readings: both kept; structure-primary: the ref implements the structure.)

HOW IT WORKS (decomposed, the literature-grounded mechanism):
  min-plus (tropical) matrix product: (A *_minplus B)[i][j] = min_k (A[i][k] + B[k][j]). The shortest-path
  distance matrix is the min-plus CLOSURE of the weighted adjacency matrix.
  SEGMENT-DOUBLING (KMR 1972 prefix-doubling / min-plus repeated squaring, CLRS): D^(2^k) = D^(2^(k-1))
  *_minplus D^(2^(k-1)). Paths of length <= 2^k are built from two halves of length <= 2^(k-1). After
  ceil(log2(n)) doublings, all shortest paths (length <= n-1) are covered. This is the segment HIERARCHY:
  a length-2^k segment is the concatenation of two length-2^(k-1) segments (the doubling tree).
  2-HOP / hub labeling (Cohen-Halperin-Kaplan-Zwick 2003): each vertex stores a label L(v) of (hub,dist)
  pairs; dist(u,w) = min over shared hubs h of L(u)[h] + L(w)[h]. The query is a 2-hop join through a hub.

CONSERVATION (the APSP witness, per the register): segment-doubling RELEASES the trivial law "is-atomic /
locality holds unconditionally" (that a path is a single indivisible step), and the carried witness is the
SEGMENT DECOMPOSITION -- the (left-half, right-half, pivot) split that built each shortest path.
triviality-out (locality) = witness-in (the segment split).

CANON+RESIDUE (AI-CANON-RESIDUE, the per-ref obligation; APSP releases LOCALITY -- 6th carrier):
  the DISTANCE matrix D is the canonical form -- it is LOSSY (a distance d(i,j) collapses WHICH path
  achieved it; many segment decompositions give the same distance). The residue is the PIVOT/midpoint table
  (for each (i,j) at doubling level k, the k that split it) -- exactly what the distance discarded -- enough
  to reconstruct the shortest PATH. D + residue is LOSSLESS: recover_path(i,j) rebuilds the actual route.
"""
INF = float("inf")

# ---- min-plus (tropical) product ----
def minplus(A, B):
    n = len(A); m = len(B[0]); inner = len(B)
    C = [[INF]*m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            best = INF
            for k in range(inner):
                if A[i][k] + B[k][j] < best:
                    best = A[i][k] + B[k][j]
            C[i][j] = best
    return C

# ---- segment-doubling closure (with pivot/midpoint residue) ----
def apsp(weights):
    """All-pairs shortest paths by min-plus segment-doubling. weights[i][j] = edge cost (INF if no edge,
    0 on the diagonal). Returns (D, mid) where D is the distance matrix (canonical form) and mid is the
    pivot table: mid[i][j] = an intermediate vertex on a shortest i->j path, or None if the edge is direct
    (the residue that recovers the path)."""
    n = len(weights)
    D = [row[:] for row in weights]
    mid = [[None]*n for _ in range(n)]
    length = 1
    # doubling: ceil(log2(n)) rounds of D <- D *_minplus D, tracking the pivot that achieved each min
    while length < n - 1 or length == 1:
        newD = [[INF]*n for _ in range(n)]
        newMid = [[mid[i][j] for j in range(n)] for i in range(n)]
        for i in range(n):
            for j in range(n):
                best = D[i][j]; bestk = None
                for k in range(n):
                    if D[i][k] + D[k][j] < best:
                        best = D[i][k] + D[k][j]; bestk = k
                newD[i][j] = best
                if bestk is not None and bestk != i and bestk != j:
                    newMid[i][j] = bestk
        D, mid = newD, newMid
        if length >= n - 1: break
        length *= 2
    return D, mid

def recover_path(i, j, mid):
    """Reconstruct a shortest i->j path from the pivot residue (proves D+residue lossless: the route the
    distance discarded is recovered). Returns the vertex sequence."""
    k = mid[i][j]
    if k is None:
        return [i, j] if i != j else [i]
    left = recover_path(i, k, mid); right = recover_path(k, j, mid)
    return left[:-1] + right       # splice at the pivot

# ---- 2-hop / hub labeling query (directed: separate forward L_out and backward L_in) ----
def two_hop_labels(D):
    """Build a (correct, non-minimal) 2-hop labeling. For DIRECTED graphs each vertex needs a FORWARD
    label L_out[v] = {hub: dist(v->hub)} and a BACKWARD label L_in[v] = {hub: dist(hub->v)}. dist(u,w)
    joins through a shared hub: min_h L_out[u][h] + L_in[w][h]. (CHKZ picks a SMALL hub set; this reference
    uses the full set -- the QUERY structure, a 2-hop join through a shared hub, is the point.)"""
    n = len(D)
    L_out = [{h: D[v][h] for h in range(n) if D[v][h] < INF} for v in range(n)]   # v -> hub
    L_in  = [{h: D[h][v] for h in range(n) if D[h][v] < INF} for v in range(n)]   # hub -> v
    return (L_out, L_in)

def two_hop_query(u, w, labels):
    """dist(u,w) = min over shared hubs h of L_out[u][h] + L_in[w][h] -- the directed 2-hop join."""
    L_out, L_in = labels
    Lu, Lw = L_out[u], L_in[w]
    best = INF
    for h in Lu:
        if h in Lw and Lu[h] + Lw[h] < best:
            best = Lu[h] + Lw[h]
    return best

# ---- CANON + RESIDUE ----
def canonicalize(weights):
    """canonical = the distance matrix D (lossy: collapses which path); residue = the pivot table mid
    (recovers the path). D + mid is lossless via recover_path."""
    D, mid = apsp(weights)
    return D, mid

def recover(i, j, residue):
    return recover_path(i, j, residue)
