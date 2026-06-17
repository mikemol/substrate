"""
kron_reduction.py — EVERY conductance graph reduces. Node elimination (Kron reduction = Schur
complement of the Laplacian) is the universal reduction; series / parallel / Y-Delta are its
low-degree special cases (candidate claim KRN).

The "series-parallel-reducible vs irreducible" split is not a wall -- it's just that series and
parallel are the two simplest node-eliminations. Eliminate an internal node x: fold its conductance
into fill-in edges between every pair of its neighbors,
    G_ij  +=  G_ix * G_xj / (sum_n G_xn)          (Schur complement on x)
and drop x. Special cases:
  * x has degree 2          -> ONE fill-in edge = SERIES (G_AND); x vanishes.
  * two edges on one pair    -> they merge by addition = PARALLEL (G_OR).
  * x has degree 3          -> THREE fill-in edges = the Y-Delta (star->triangle) transform.
  * x has degree k          -> star -> clique on k, k(k-1)/2 fill-in edges.
Eliminate all internal nodes (any order) -> a single src--sink edge = G_eff. So G_OR and G_AND are
not "the reducible case + a fallback"; they are the degree<=2 corner of ONE recursive operation
that reduces ANY graph.

Two substrate resonances: the fill-in is never-discard-residue (the eliminated node's structure is
FOLDED into the remaining edges, not dropped); and G_eff is ELIMINATION-ORDER-INVARIANT -- the order
is a gauge, the effective conductance is the invariant.

Witnesses (each [W], cross-checked against the nodal solve in kirchhoff_nedge):
1. degree-2 elimination == SERIES (G_AND).
2. parallel input/fill-in edges merge == G_OR.
3. degree-3 elimination == Y-Delta (matches the standard star->triangle formula).
4. the Wheatstone "irreducible" bridge FULLY reduces (eliminate P,Q) to G_eff == nodal solve.
5. order-invariance: reducing in different elimination orders gives the same G_eff (== nodal),
   on the bridge and on a random mesh -- the reduction is confluent.
Run output: tools/kron_reduction-out.txt.
"""
from itertools import combinations
import random, copy
from kirchhoff_nedge import solve, G_OR, G_AND


def _adj(edges):
    a = {}
    for u, v, g in edges:
        a.setdefault(u, {}); a.setdefault(v, {})
        a[u][v] = a[u].get(v, 0.0) + g       # parallel input edges merge here (G_OR)
        a[v][u] = a[v].get(u, 0.0) + g
    return a


def eliminate(a, x):
    """Kron-eliminate node x: Schur complement -> fill-in edges among x's neighbors, drop x."""
    nbrs = dict(a[x]); S = sum(nbrs.values())
    for i, j in combinations(nbrs, 2):
        add = nbrs[i] * nbrs[j] / S
        a[i][j] = a[i].get(j, 0.0) + add     # fill-in merges with any existing edge (parallel)
        a[j][i] = a[j].get(i, 0.0) + add
    for v in nbrs:
        del a[v][x]
    del a[x]


def g_eff(edges, src, sink, order=None):
    a = _adj(edges)
    internal = order if order is not None else [n for n in list(a) if n not in (src, sink)]
    for x in internal:
        eliminate(a, x)
    return a[src].get(sink, 0.0)


def eliminate_counted(a, x):
    """Eliminate x; return the number of NEW edges created (fill-in)."""
    nbrs = dict(a[x]); S = sum(nbrs.values()); fill = 0
    for i, j in combinations(nbrs, 2):
        if j not in a[i]:
            fill += 1
        add = nbrs[i] * nbrs[j] / S
        a[i][j] = a[i].get(j, 0.0) + add
        a[j][i] = a[j].get(i, 0.0) + add
    for v in nbrs:
        del a[v][x]
    del a[x]
    return fill


def g_eff_fill(edges, src, sink, order):
    a = _adj(edges); fill = 0
    for x in order:
        fill += eliminate_counted(a, x)
    return a[src].get(sink, 0.0), fill


def min_degree_order(edges, src, sink):
    """Greedy minimum-degree ordering: repeatedly eliminate the lowest-degree internal node
    (the classic sparse-elimination heuristic for minimizing fill-in)."""
    a = copy.deepcopy(_adj(edges)); order = []
    internal = lambda: [n for n in a if n not in (src, sink)]
    while internal():
        x = min(internal(), key=lambda n: len(a[n]))
        order.append(x); eliminate(a, x)
    return order


def w_series():
    G1, G2 = 2.0, 3.0
    g = g_eff([(0, 1, G1), (1, 2, G2)], 0, 2)       # eliminate node 1 (degree 2)
    ok = abs(g - G_AND(G1, G2)) < 1e-12
    print(f"1. degree-2 elimination == series G_AND: {g:.6f} == {G_AND(G1,G2):.6f}  {ok}")
    return ok


def w_parallel():
    G1, G2 = 2.0, 3.0
    # two series paths A-x-B and A-y-B: eliminate x,y -> fill-ins merge on (A,B) = G_OR of the paths
    g = g_eff([(0, 1, G1), (1, 2, G2), (0, 3, G1), (3, 2, G2)], 0, 2)
    ok = abs(g - G_OR(G_AND(G1, G2), G_AND(G1, G2))) < 1e-12
    print(f"2. fill-in edges merge == parallel G_OR: two G_AND({G1},{G2}) paths -> {g:.6f} == "
          f"{G_OR(G_AND(G1,G2),G_AND(G1,G2)):.6f}  {ok}")
    return ok


def w_ydelta():
    # Y: center 0, leaves 1,2,3 with conductances Ga,Gb,Gc. Eliminate 0 -> triangle.
    Ga, Gb, Gc = 1.0, 2.0, 3.0
    a = _adj([(0, 1, Ga), (0, 2, Gb), (0, 3, Gc)])
    eliminate(a, 0)
    S = Ga + Gb + Gc
    ok = (abs(a[1][2] - Ga * Gb / S) < 1e-12 and abs(a[1][3] - Ga * Gc / S) < 1e-12
          and abs(a[2][3] - Gb * Gc / S) < 1e-12)
    print(f"3. degree-3 elimination == Y-Delta: triangle G12={a[1][2]:.4f} G13={a[1][3]:.4f} "
          f"G23={a[2][3]:.4f} match star->mesh formula  {ok}")
    return ok


def w_wheatstone_reduces():
    edges = [(0, 1, 1.0), (1, 3, 2.0), (0, 2, 3.0), (2, 3, 1.0), (1, 2, 0.5)]  # unbalanced bridge
    g = g_eff(edges, 0, 3)                            # eliminate P=1, Q=2 -> single 0-3 edge
    ref, _, _ = solve(4, edges, 0, 3)
    ok = abs(g - ref) < 1e-9
    print(f"4. Wheatstone 'irreducible' bridge FULLY reduces: Kron {g:.6f} == nodal solve {ref:.6f}  {ok}")
    return ok


def w_order_invariance():
    edges = [(0, 1, 1.0), (1, 3, 2.0), (0, 2, 3.0), (2, 3, 1.0), (1, 2, 0.5)]
    g_a = g_eff(edges, 0, 3, order=[1, 2])
    g_b = g_eff(edges, 0, 3, order=[2, 1])
    ref, _, _ = solve(4, edges, 0, 3)
    bridge_ok = abs(g_a - g_b) < 1e-9 and abs(g_a - ref) < 1e-9
    # a random mesh: same G_eff under random elimination orders and vs the nodal solve
    rng = random.Random(0); n = 8
    medges = [(u, v, rng.uniform(0.2, 5.0)) for u in range(n) for v in range(u + 1, n)]
    src, sink = 0, n - 1
    internal = [x for x in range(n) if x not in (src, sink)]
    o1 = internal[:]; o2 = internal[::-1]; rng.shuffle(o3 := internal[:])
    gs = [g_eff(medges, src, sink, order=o) for o in (o1, o2, o3)]
    mref, _, _ = solve(n, medges, src, sink)
    mesh_ok = all(abs(x - mref) < 1e-9 for x in gs)
    print(f"5. order-invariance: bridge orders agree & == nodal {bridge_ok}; "
          f"K8 mesh under 3 orders all == nodal ({mref:.4f}) {mesh_ok}")
    return bridge_ok and mesh_ok


def w_order_cost():
    # double-star: a hub joined to k leaves; each leaf also joined to src and sink. Eliminating the
    # hub FIRST turns its k leaves into a clique (k(k-1)/2 fill); eliminating leaves first is cheap.
    # SAME G_eff either way -- the order is a COST gauge, not an answer gauge.
    k = 8; src = 0; hub = 1; sink = k + 2; leaves = list(range(2, k + 2))
    edges = ([(hub, l, 1.0) for l in leaves] + [(src, l, 1.0) for l in leaves]
             + [(l, sink, 1.0) for l in leaves] + [(src, hub, 1.0), (hub, sink, 1.0)])
    good = min_degree_order(edges, src, sink)         # the "right order" (min-degree heuristic)
    bad = [hub] + leaves                              # the worst: dense node first -> clique fill
    g_good, f_good = g_eff_fill(edges, src, sink, good)
    g_bad, f_bad = g_eff_fill(edges, src, sink, bad)
    same = abs(g_good - g_bad) < 1e-9
    cheaper = f_good < f_bad
    print(f"6. order is a COST gauge (answer invariant): G_eff {g_good:.5f} == {g_bad:.5f} {same}; "
          f"fill-in min-degree {f_good} << hub-first {f_bad} {cheaper}")
    print(f"   => 'the right order' = minimum-fill ordering = the sparse-elimination problem "
          f"(min-degree/nested-dissection; optimal NP-hard)")
    return same and cheaper


if __name__ == "__main__":
    print("Kron reduction: EVERY conductance graph reduces by node elimination (series/parallel/Y-Delta\n"
          "are its degree<=3 cases). Cross-checked against the nodal solve.\n")
    ws = [w_series(), w_parallel(), w_ydelta(), w_wheatstone_reduces(), w_order_invariance(), w_order_cost()]
    ok = all(ws)
    print(f"\nKRON REDUCTION: series {ws[0]}; parallel {ws[1]}; y-delta {ws[2]}; "
          f"bridge-reduces {ws[3]}; order-invariant {ws[4]}; order-is-cost-gauge {ws[5]}")
    print(f"\n  {'PASS' if ok else 'FAIL'} — ~all graphs reduce: node elimination (Schur complement) is the")
    print(f"  ONE recursive reduction, with series (degree-2) / parallel (edge-merge) / Y-Delta (degree-3)")
    print(f"  its low-degree cases. The bridge is not a wall -- one Y-Delta dissolves it. Fill-in is")
    print(f"  never-discard-residue (the node's conductance folds into its neighbors). The elimination")
    print(f"  ORDER is a gauge on the ANSWER (G_eff invariant) but a COST knob (fill-in): 'the right order'")
    print(f"  is the minimum-fill ordering -- the sparse-Gaussian-elimination problem. G_OR/G_AND were")
    print(f"  always this one operation, restricted to degree<=2.")
