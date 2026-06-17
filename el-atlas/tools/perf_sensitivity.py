"""
perf_sensitivity.py — the final view: edge SENSITIVITY from the same Kron solve (candidate KSN),
+ the tropical<->conductance semiring clarification (the min-vs-G_AND subtlety, done right).

Two things, both rigorous:

A. SENSITIVITY (the suggested next step, generalized correctly). From the nodal solve (node voltages
   v, unit current src->sink) the exact sensitivity of the effective conductance to each edge is
       dG_eff/dG_i = (dv_i / V_terminal)^2          (squared voltage drop, at unit terminal voltage)
   and the FRACTIONAL sensitivity (dln G_eff / dln G_i) = edge i's share of DISSIPATED POWER:
       s_i = G_i (dv_i)^2 / sum_j G_j (dv_j)^2 .
   For a series chain s_i = R_i / R_total (the resistance share = the spectrum view) -- but s_i is
   defined on ANY graph, where "resistance share" is undefined. It is exactly "how much does
   improving edge i help," and it ranks bottlenecks on bridges/meshes too. At the Wheatstone
   BALANCE, the bridge edge carries no current -> s = 0 (fixing it does nothing) -- a clean check.

B. THE SEMIRING SUBTLETY (min vs G_AND). They are NOT interchangeable: min = TROPICAL (the hard
   roofline bound), G_AND = CONDUCTANCE (the soft series knee). At a=b: min=a but G_AND=a/2. They
   are the endpoints of one p-norm family  G_p = (a^-p + b^-p)^(-1/p):  p=1 -> G_AND, p->inf -> min,
   related by Maslov/LogSumExp dequantization. So the uniform move is a PARAMETERIZED semiring, not
   collapsing min into G_AND (which would halve the roofline at the ridge).

Witnesses (each [W]):
1. series sensitivity == resistance share (the spectrum view) -- exact.
2. fractional sensitivities sum to 1 (Tellegen / power conservation) -- on a mesh, not just chains.
3. sensitivity == finite-difference dG_eff/dG_i, and the TOP-sensitivity edge gives the largest
   real G_eff gain when improved -- "how much fixing it helps," verified.
4. Wheatstone: unbalanced -> bridge edge sensitivity > 0; BALANCED -> ~0 (no current).
5. semiring bracket: G_AND <= min <= G_OR, and the p-norm family interpolates G_AND (p=1) to
   min (p large) -- the min-vs-G_AND "subtlety" is two endpoints of one family, not a bug to patch.
"""
import numpy as np
from kirchhoff_nedge import solve, G_AND, G_OR


def sensitivity(n, edges, src, sink):
    """Fractional sensitivity s_i = edge i's share of dissipated power, from one nodal solve.
    Returns [(edge_index, (u,v), s_i)] sorted desc; s_i sums to 1."""
    Geff, v, _ = solve(n, edges, src, sink)
    powers = [g * (v[u] - v[w]) ** 2 for (u, w, g) in edges]
    tot = sum(powers)
    rows = sorted(((i, (u, w), powers[i] / tot) for i, (u, w, g) in enumerate(edges)),
                  key=lambda r: -r[2])
    return Geff, rows


def dGeff_dGi(n, edges, src, sink):
    """Exact dG_eff/dG_i = (dv_i at unit terminal voltage)^2."""
    Geff, v, _ = solve(n, edges, src, sink)
    Vt = v[src]                                    # terminal voltage at unit injected current
    return Geff, [((v[u] - v[w]) / Vt) ** 2 for (u, w, g) in edges]


def Gp(a, b, p):                                   # p-norm conductance family: p=1 -> G_AND, inf -> min
    return (a ** (-p) + b ** (-p)) ** (-1.0 / p)


if __name__ == "__main__":
    print("edge sensitivity from the Kron solve, + the tropical<->conductance semiring clarification.\n")

    # 1. series chain: sensitivity == resistance share
    Gs = [2.0, 5.0, 10.0, 3.0]
    chain = [(i, i + 1, g) for i, g in enumerate(Gs)]
    Geff, rows = sensitivity(len(Gs) + 1, chain, 0, len(Gs))
    Rtot = sum(1 / g for g in Gs)
    share = {i: (1 / Gs[i]) / Rtot for i in range(len(Gs))}
    w1 = all(abs(s - share[i]) < 1e-9 for i, _, s in rows)
    print(f"1. series sensitivity == resistance share: "
          f"{[(i, round(s,3)) for i,_,s in rows]} vs shares {[round(share[i],3) for i in range(len(Gs))]} {w1}")

    # 2. sums to 1 on a MESH (not just a chain): a random K6
    rng = np.random.default_rng(0); m = 6
    mesh = [(u, w, float(rng.uniform(0.3, 4))) for u in range(m) for w in range(u + 1, m)]
    _, mrows = sensitivity(m, mesh, 0, m - 1)
    w2 = abs(sum(s for _, _, s in mrows) - 1.0) < 1e-9
    print(f"2. fractional sensitivities sum to 1 on a K{m} mesh (Tellegen): {sum(s for _,_,s in mrows):.6f} {w2}")

    # 3. sensitivity == finite difference, and top edge = most leverage
    Geff0, dG = dGeff_dGi(m, mesh, 0, m - 1)
    eps = 1e-4
    fd = []
    for i, (u, w, g) in enumerate(mesh):
        bumped = [(u2, w2, g2 + (eps if j == i else 0)) for j, (u2, w2, g2) in enumerate(mesh)]
        Gb, _, _ = solve(m, bumped, 0, m - 1)
        fd.append((Gb - Geff0) / eps)
    w3a = all(abs(dG[i] - fd[i]) < 1e-3 for i in range(len(mesh)))
    top = max(range(len(mesh)), key=lambda i: dG[i])           # highest sensitivity edge
    w3b = top == max(range(len(mesh)), key=lambda i: fd[i])    # also the largest real gain
    print(f"3. analytic dG_eff/dG_i == finite-diff {w3a}; top-sensitivity edge = max real gain {w3b} "
          f"(edge {mesh[top][:2]}, dG_eff/dG={dG[top]:.4f})")

    # 4. Wheatstone: bridge-edge sensitivity > 0 unbalanced, ~0 balanced
    def bridge_sens(G1, G2, G3, G4, G5):
        edges = [(0, 1, G1), (1, 3, G2), (0, 2, G3), (2, 3, G4), (1, 2, G5)]   # edge 4 = the bridge
        _, rs = sensitivity(4, edges, 0, 3)
        return dict((i, s) for i, _, s in rs)[4]
    s_unbal = bridge_sens(1, 2, 3, 1, 0.5)
    s_bal = bridge_sens(2, 4, 3, 6, 0.5)        # G1/G2 = G3/G4 = 1/2  -> balanced
    w4 = s_unbal > 1e-3 and s_bal < 1e-9
    print(f"4. Wheatstone bridge-edge sensitivity: unbalanced {s_unbal:.4f} (>0) ; balanced {s_bal:.2e} "
          f"(~0, no current) {w4}")

    # 5. semiring: min vs G_AND are p-norm endpoints, NOT interchangeable
    a, b = 4.0, 4.0
    band = G_AND(a, b); bmin = min(a, b); bor = G_OR(a, b)
    bracket = band <= bmin <= bor and abs(band - a / 2) < 1e-9 and abs(bmin - a) < 1e-9
    interp = abs(Gp(a, b, 1) - band) < 1e-9 and abs(Gp(3.0, 7.0, 40) - min(3.0, 7.0)) < 1e-3
    w5 = bracket and interp
    print(f"5. semiring: at a=b={a}: G_AND={band} (p=1, soft knee) < min={bmin} (p->inf, hard bound) "
          f"< G_OR={bor}; p-norm interpolates {interp} -> NOT min:=G_AND (would halve the ridge) {w5}")

    ok = w1 and w2 and w3a and w3b and w4 and w5
    print(f"\nPERF SENSITIVITY: series==share {w1}; sums-to-1 {w2}; ==finite-diff {w3a and w3b}; "
          f"bridge-null {w4}; semiring-bracket {w5}")
    print(f"\n  {'PASS' if ok else 'FAIL'} — the bottleneck ranking is dG_eff/dG_i = each edge's share")
    print(f"  of dissipated power, exact from ONE nodal solve: = resistance share on a chain, but defined")
    print(f"  on ANY graph (it ranks bridge/mesh edges, and the bridge edge nulls at balance). 'How much")
    print(f"  fixing it helps' is the literal derivative. And min vs G_AND are the tropical/conductance")
    print(f"  endpoints of one p-norm family (dequantization) -- parameterize the semiring, don't collapse it.")
