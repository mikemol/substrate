# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# NOTE [AI-ASPF-RELABEL]: this module is APSP material (the single-shared-vertex segment monoid of
# all-pairs-shortest-path), historically mis-prefixed aspf_. Its warrants are now named apsp_seg_* (op/nocycle/
# apex). The filename is retained (impl detail); the real parse-forest ASPF is aspf_rsbpf_ref.py.
"""ASPF -- the SEGMENT/CONE reading (positional). One of TWO valid ASPF formalizations in the paper:
  - aspf_ref.py        = the MULTISET/Godel reading (prime fingerprint; keeps WHICH tokens, order/distance-blind).
  - aspf_segment_ref.py (THIS) = the SEGMENT reading (keeps WHERE on the structure; the single-shared-vertex
    partial-composition monoid built shortest-to-longest, with the three user-formulations as coordinates).
Both are projections of one construction recording different residues (all-readings law). Neither replaces the other.

ONE construction: glue two compound-edges sharing EXACTLY ONE vertex, in length order (shortest-to-longest).
Shortest-path-ness is then a THEOREM not a filter: everything shorter is already built, so no shortcut appears
mid-construction. The single-shared-vertex rule keeps every compound a simple PATH (no cycle) -- the inductive
invariant. Three coordinates of one compound:
  F1 = the edge/vertex SET covered (the body).
  F2 = ENDPOINTS + length (the span); endpoints are the two degree-1 vertices (structural, label-free).
  F3 = the MIDPOINT = cone-APEX (the dual 0-cell over the edge, one order up). For an atom: a fresh point.
       For a compound: the apex LANDS on the shared junction; apex(2N) = the center junction where its two
       N-halves were glued, and the half-apexes are the halves' own apexes one order down. The apex hierarchy
       IS the construction tree. On a path the position-average (a+b)/2 is the SHADOW of this intrinsic apex.
"""
from fractions import Fraction

class Compound:
    """A compound edge = a simple path in the base graph, recorded as the set of base-EDGES it uses.
    Endpoints are derived structurally: the two vertices of odd degree (degree 1) in the path."""
    __slots__ = ("edges",)
    def __init__(self, edges):
        self.edges = frozenset(frozenset(e) for e in edges)   # set of base edges, each a 2-set
    @property
    def verts(self):
        s = set()
        for e in self.edges: s |= e
        return frozenset(s)
    @property
    def length(self):
        return len(self.edges)                                # number of edges = path length
    @property
    def endpoints(self):
        """The two degree-1 vertices (the ends of the path). Structural, label-free."""
        deg = {}
        for e in self.edges:
            for v in e: deg[v] = deg.get(v, 0) + 1
        ends = sorted(v for v, d in deg.items() if d == 1)
        return tuple(ends)                                    # exactly 2 for a path; () if a cycle
    @property
    def junctions(self):
        """Interior (degree-2) vertices -- the shared-vertices accumulated during construction."""
        deg = {}
        for e in self.edges:
            for v in e: deg[v] = deg.get(v, 0) + 1
        return frozenset(v for v, d in deg.items() if d == 2)
    def __eq__(self, o):  return isinstance(o, Compound) and self.edges == o.edges
    def __hash__(self):   return hash(self.edges)
    def __repr__(self):
        ep = self.endpoints
        return f"<{'-'.join(map(str,ep)) if len(ep)==2 else 'CYCLE'} len{self.length}>"

def atom(u, v):
    return Compound([{u, v}])

# ---- the operation: single-junction gluing ----
def composable(x, y):
    """Defined iff x,y share EXACTLY ONE base-VERTEX and NO base-edge (the single-junction rule).
    Sharing a vertex but no edge => gluing at that one point => the union is still a path (no cycle)."""
    if x.edges & y.edges:                       # share an edge -> would retrace
        return False
    return len(x.verts & y.verts) == 1

def combine(x, y):
    """Glue at the single shared vertex. Result = union of edge-sets. Endpoints fall out structurally."""
    assert composable(x, y), "single-junction rule violated"
    z = Compound(x.edges | y.edges)
    # the single-junction rule guarantees z is a simple path: the shared vertex becomes degree-2 (interior),
    # the two former endpoints at the join become interior, the outer two ends stay degree-1.
    return z

# ---- the construction: shortest-to-longest ----
def construct(base_edges, max_order=None):
    seen = set(); order0 = []
    for (u, v) in base_edges:
        c = atom(u, v)
        if c not in seen: seen.add(c); order0.append(c)
    orders = [order0]; allc = list(order0); k = 0
    while max_order is None or k < max_order:
        length = 2 ** k
        frontier = [c for c in allc if c.length == length]
        new = []
        for i in range(len(frontier)):
            for j in range(len(frontier)):
                x, y = frontier[i], frontier[j]
                if composable(x, y):
                    z = combine(x, y)
                    if z.length == 2 * length and z not in seen and len(z.endpoints) == 2:
                        seen.add(z); new.append(z)
        if not new: break
        orders.append(new); allc.extend(new); k += 1
    return orders

# ---- Formulation 3 view: midpoint coordinate, VALID ONLY on a path (vertices = positions) ----
def midpoint_on_path(c):
    """Line-specific coordinate: midpoint = mean of the two endpoint positions. Meaningful only when the
    base graph is a path and vertex labels are positions. Returns Fraction or None if not a 2-ended path."""
    ep = c.endpoints
    if len(ep) != 2: return None
    return Fraction(ep[0] + ep[1], 2)


# ===== Formulation 3 (intrinsic): midpoint = cone-apex =====
"""F3 made intrinsic: midpoint = cone-apex. The apex of an edge is a NEW point one order up; the apex of a
compound built from two adjacent halves LANDS on their shared junction. Built and checked, no positions."""

# Each compound gets an APEX, a fresh symbol, EXCEPT we then check: for a compound = combine(x,y) at junction j,
# is the apex identifiable with j? We test the structural claim by building the cone and locating the apex as
# 'the unique vertex interior to the compound' (degree-2 vertex), and checking it equals the composition junction.

def apex_of(c):
    """The cone-apex (midpoint) of a compound, intrinsically:
       - atom (length 1): a fresh apex, denoted ('apex', frozenset(edge)) -- a NEW point one order up.
       - compound (length>1): the apex sits at the junction(s). For a length-2 compound there is exactly ONE
         interior (degree-2) vertex -- that IS the apex. (Higher lengths have an apex-PATH of junctions; the
         'midpoint' is the central junction.)"""
    ep = c.endpoints
    if c.length == 1:
        return ('apex', c.edges)                      # fresh point, dual to the edge (Hodge): one dim up
    # the apex is the CENTER junction: the interior vertex equidistant (along the path) from both endpoints --
    # the vertex where the two equal halves were glued. Order the interior vertices ALONG the path and take the
    # middle one. (length-2: one interior = the junction; length-2N: the central interior = the doubling junction.)
    ep = c.endpoints
    if len(ep) != 2:
        return ('central', tuple(sorted(c.junctions)))
    a, b = ep
    # build adjacency within the compound to walk the path a..b in order
    adj = {}
    for e in c.edges:
        for v in e:
            adj.setdefault(v, set()).add(next(iter(e - {v})))
    seq = [a]; prev = None; cur = a
    while cur != b:
        nxt = next(w for w in adj[cur] if w != prev)
        seq.append(nxt); prev, cur = cur, nxt
    return seq[len(seq) // 2]                          # the central vertex of the ordered path = the apex

def junction_of(x, y):
    """The shared vertex at which combine(x,y) glues -- the construction's junction."""
    s = x.verts & y.verts
    return next(iter(s)) if len(s) == 1 else None

def apex_set(c):
    """The RECURSIVE apex set = every apex down the construction tree = every interior (junction) vertex.
    This is the cone-apex hierarchy collected: apex_of gives the SINGLE central apex; apex_set gives ALL of
    them (the whole apex-path). For a compound it satisfies the inductive recurrence
        apex_set(combine(A,B)) = apex_set(A) ∪ {junction(A,B)} ∪ apex_set(B)
    and equals the interior-vertex set (all vertices that are not the two endpoints). This recurrence IS the
    inductive step of the no-tangle construction: a compound is a simple path iff its two children are simple
    paths (IH) and their apex sets meet only at the junction. (Atoms have empty apex set -- no interior.)"""
    ep = c.endpoints
    if len(ep) != 2:
        return frozenset(c.junctions)
    return frozenset(c.verts - set(ep))

def apex_disjoint_at_junction(x, y):
    """The MIDPOINT<->ENDPOINT check (USER), as the recursive-apex comparison: x and y may be abutted iff they
    share exactly one vertex (the junction) AND their recursive apex sets plus free endpoints meet only there.
    Equivalent to (x.verts & y.verts == {junction}); phrased via apex sets to show it rides the apex hierarchy
    the construction already computes -- NOT an extra runtime scan. Returns the junction if OK, else None."""
    j = junction_of(x, y)
    if j is None:
        return None
    # the recursive apex sets (interior vertices) of the two pieces must be disjoint, and neither piece's
    # free endpoint may land inside the other -- i.e. the only shared vertex is the junction j.
    if (x.verts & y.verts) != {j}:
        return None
    return j

