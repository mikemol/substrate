"""
kirchhoff_nedge.py — the nedge conductance model on its PROPER foundation: Kirchhoff nodal
analysis, with G_OR / G_AND as DERIVED special cases (candidate claim KIR).

The earlier pilots took G_OR = sum and G_AND = harmonic as primitive operations and then
*discovered* empirically that the parallel sum fails under a shared resource. That should have
been a given: evaluating a conductance network properly is Kirchhoff's laws (KCL current
conservation at nodes, KVL around loops), and

  * "two elements are in PARALLEL" MEANS they connect the SAME node pair -> only THEN do their
    conductances add (G_OR). A shared downstream element makes the branches NOT share a node pair,
    so KCL routes their merged current through that element -- the sum was never the right reduction.
  * series/parallel reduction (G_OR/G_AND) is exact ONLY on series-parallel-REDUCIBLE graphs.
    A shared resource or a bridge is NOT reducible; you must solve the nodal system. The contention
    cap and the Wheatstone bridge then fall out BY CONSTRUCTION, not by measurement.

The solve: build the graph Laplacian L (L[i,i]=sum of incident conductances, L[i,j]=-G_ij), ground
the sink, inject unit current at the source, solve L v = i. Effective conductance G_eff = 1/v_src.
This is the stationary point of the dissipated-power functional (Thomson's principle); KCL is its
stationarity condition -- the conserved current (Noether: conservation law <- the network's symmetry).

Witnesses (each [W]):
1. SERIES emerges: nodal(A-x-B) == G_AND(G1,G2) exactly (G_OR/G_AND are not primitive; they are
   reductions OF this solve).
2. PARALLEL emerges: nodal(A=B, two edges) == G_OR(G1,G2) exactly.
3. SHARED RESOURCE is DERIVED: k branches feeding one shared series element -> nodal == G_AND(k*g, c),
   saturating at c as k grows. The contention cap is a THEOREM of KCL, not an empirical finding.
4. WHEATSTONE / irreducible: nodal includes the coupling edge; series-parallel reduction (G_OR of
   G_AND paths) AGREES only when the bridge is BALANCED (no current through the coupling = the
   bridge null) and DIFFERS otherwise -- so the G_OR/G_AND algebra is valid iff Kirchhoff says the
   coupling carries no current.
5. KCL = NOETHER: at the solution, net current is 0 at every internal node (conservation); +1 at
   the source, -1 at the sink. The solver enforces the conserved current at every node.
Run output: tools/kirchhoff_nedge-out.txt.
"""
import numpy as np

G_OR  = lambda a, b: a + b
G_AND = lambda a, b: a * b / (a + b)


def solve(n, edges, src, sink):
    """Nodal analysis. edges: list of (u, v, G). Returns (G_eff, v) with unit current src->sink,
    sink grounded. G_eff = 1/v[src]; v is the full node-voltage vector (v[sink]=0)."""
    L = np.zeros((n, n))
    for u, v, g in edges:
        L[u, u] += g; L[v, v] += g; L[u, v] -= g; L[v, u] -= g
    idx = [i for i in range(n) if i != sink]
    Lr = L[np.ix_(idx, idx)]
    ir = np.zeros(len(idx)); ir[idx.index(src)] = 1.0
    vr = np.linalg.solve(Lr, ir)
    v = np.zeros(n)
    for i, node in enumerate(idx):
        v[node] = vr[i]
    return 1.0 / v[src], v, L


def w_series():
    G1, G2 = 2.0, 3.0
    geff, _, _ = solve(3, [(0, 1, G1), (1, 2, G2)], 0, 2)
    ok = abs(geff - G_AND(G1, G2)) < 1e-12
    print(f"1. series emerges: nodal(A-x-B) = {geff:.6f} == G_AND({G1},{G2}) = {G_AND(G1,G2):.6f}  {ok}")
    return ok


def w_parallel():
    G1, G2 = 2.0, 3.0
    geff, _, _ = solve(2, [(0, 1, G1), (0, 1, G2)], 0, 1)
    ok = abs(geff - G_OR(G1, G2)) < 1e-12
    print(f"2. parallel emerges: nodal(A=B, 2 edges) = {geff:.6f} == G_OR({G1},{G2}) = {G_OR(G1,G2):.6f}  {ok}")
    return ok


def w_shared_resource():
    # SRC(0) -- k parallel branches --> M(1) -- shared series c --> SINK(2)
    g, c = 10.0, 18.0
    rows = []
    for k in (1, 2, 4, 8, 64):
        edges = [(0, 1, g)] * k + [(1, 2, c)]
        geff, _, _ = solve(3, edges, 0, 2)
        rows.append((k, geff, G_AND(k * g, c)))
    # nodal == G_AND(k*g, c) exactly; saturates at c (the controller) as k grows
    exact = all(abs(ge - pred) < 1e-9 for _, ge, pred in rows)
    saturates = rows[-1][1] < c and rows[-1][1] > rows[0][1] and rows[-1][1] > 0.9 * c
    print("3. shared resource is DERIVED (contention cap is a KCL theorem, not measured):")
    for k, ge, pred in rows:
        print(f"     k={k:2d} branches: G_eff = {ge:6.3f} == G_AND(k*g, c) {pred:6.3f}  (cap c={c})")
    print(f"   nodal == G_AND(k*g, c) {exact}; saturates toward the shared element {saturates}")
    return exact and saturates


def w_wheatstone():
    # SRC(0) P(1) Q(2) SINK(3); bridge edge P-Q = G5. Series-parallel reduction IGNORES G5.
    def both(G1, G2, G3, G4, G5):
        geff, _, _ = solve(4, [(0, 1, G1), (1, 3, G2), (0, 2, G3), (2, 3, G4), (1, 2, G5)], 0, 3)
        sp = G_OR(G_AND(G1, G2), G_AND(G3, G4))          # naive series-parallel (ignores the bridge)
        return geff, sp
    # unbalanced: G1/G2 != G3/G4 -> current flows in the bridge -> reduction is WRONG
    ge_u, sp_u = both(1, 2, 3, 1, 0.5)
    # balanced: G1/G2 == G3/G4 -> no bridge current (the null) -> reduction is exact
    ge_b, sp_b = both(2, 4, 3, 6, 0.5)
    unbalanced_differs = abs(ge_u - sp_u) > 1e-6
    balanced_agrees = abs(ge_b - sp_b) < 1e-9
    print("4. Wheatstone / irreducible (G_OR/G_AND valid iff the coupling carries no current):")
    print(f"     unbalanced: nodal {ge_u:.6f} vs series-parallel {sp_u:.6f} -> differ {unbalanced_differs}")
    print(f"     balanced  : nodal {ge_b:.6f} vs series-parallel {sp_b:.6f} -> agree  {balanced_agrees}")
    return unbalanced_differs and balanced_agrees


def w_kcl_noether():
    # any network: at the solution, L @ v = injected current; internal nodes net 0 (KCL).
    G1, G2, G3, G4, G5 = 1.0, 2.0, 3.0, 1.0, 0.5
    geff, v, L = solve(4, [(0, 1, G1), (1, 3, G2), (0, 2, G3), (2, 3, G4), (1, 2, G5)], 0, 3)
    inj = L @ v                                           # net current out of each node
    internal_zero = abs(inj[1]) < 1e-9 and abs(inj[2]) < 1e-9   # KCL at internal nodes P,Q
    src_sink = abs(inj[0] - 1.0) < 1e-9 and abs(inj[3] + 1.0) < 1e-9
    conserved = abs(inj.sum()) < 1e-9                     # total current conserved (Noether current)
    print(f"5. KCL = Noether: internal nodes net-zero {internal_zero}; source +1 / sink -1 "
          f"{src_sink}; total conserved {conserved}")
    return internal_zero and src_sink and conserved


if __name__ == "__main__":
    print("nedge on its Kirchhoff foundation: G_OR/G_AND as DERIVED special cases of nodal analysis.\n")
    ws = [w_series(), w_parallel(), w_shared_resource(), w_wheatstone(), w_kcl_noether()]
    ok = all(ws)
    print(f"\nKIRCHHOFF NEDGE: series=G_AND {ws[0]}; parallel=G_OR {ws[1]}; shared-cap-derived {ws[2]}; "
          f"wheatstone-irreducible {ws[3]}; kcl=noether {ws[4]}")
    print(f"\n  {'PASS' if ok else 'FAIL'} — G_OR (sum) and G_AND (harmonic) are NOT primitive: they are the")
    print(f"  parallel and series REDUCTIONS of the Kirchhoff nodal solve, valid only on series-parallel-")
    print(f"  reducible graphs. 'The sum holds iff no shared downstream series resource' is the DEFINITION")
    print(f"  of parallel (same node pair) under KCL -- a given, not a discovery. The shared-resource cap")
    print(f"  and the Wheatstone bridge fall out by construction; KCL (current conservation = the Noether")
    print(f"  current of the dissipated-power stationarity) is enforced at every node. The earlier pilots'")
    print(f"  G_OR/G_AND are this solve restricted to reducible topologies; shared resources need the solve.")
