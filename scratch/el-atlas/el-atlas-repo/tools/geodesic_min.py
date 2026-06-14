"""
geodesic_min.py — min() is not an operator; it EMERGES from the circuit settling (candidate GEO).

Correction (deeper than "parameterize the semiring"): I had framed min (tropical) and G_AND
(conductance) as two endpoints you SELECT. You don't select. A real network RELAXES to the
minimum-dissipation configuration -- Thomson's principle: the node voltages minimize total
dissipated power subject to the boundary, which IS the Kirchhoff solution (= a geodesic in the
resistance-distance metric). That settled G_eff is the truth. min() is merely what you READ OFF the
settled state when one constraint clearly dominates -- its asymptote, not an input.

The tell: G_AND(a,b) -> min(a,b) automatically as the conductances SEPARATE (a << b), with no min
ever computed. Only near the ridge (a ~ b) do they differ, and there min STRICTLY OVER-PREDICTS:
min(a,a)=a but the settle gives a/2 (the rounded roofline knee, which is the physical reality). So
the conductance solve (p=1, the physics) already gives min-behavior in the bottleneck regime and the
true knee generically; min (p->inf) is its shadow, not a co-equal semiring to pick.

Witnesses (each [W]):
1. min EMERGES: G_AND(a,b)/min(a,b) -> 1 as the conductances separate; you never impose min.
2. min STRICTLY OVER-PREDICTS at the ridge: at a=b the settle is a/2 < min=a -- imposing min here is
   wrong (it would put the roofline knee a factor 2 too high).
3. THE SETTLE IS ENERGY-MINIMIZATION (Thomson): the nodal solution minimizes dissipated power --
   every random perturbation of the interior voltages INCREASES P. So the operator is "relax to the
   minimum," and min is its read-off, not its definition.
4. GEODESIC / resistance-distance: G_eff^-1 = R_eff is a metric; when one edge's resistance
   dominates, R_eff -> that edge (the geodesic runs through the bottleneck) = min(conductances) FOR
   FREE from the solve.
"""
import numpy as np
from kirchhoff_nedge import solve, G_AND


def dissipated_power(edges, v):
    return sum(g * (v[u] - v[w]) ** 2 for (u, w, g) in edges)


if __name__ == "__main__":
    print("min() is the read-off of the settled (minimum-dissipation) state, not an operator.\n")

    # 1. min EMERGES from G_AND as conductances separate (no min ever computed)
    print("1. min EMERGES: G_AND(a,b) vs min(a,b) as they separate:")
    ratios = [(1.0, 1.0), (1.0, 2.0), (1.0, 10.0), (1.0, 100.0), (1.0, 1e4)]
    w1 = True
    for a, b in ratios:
        gand, mn = G_AND(a, b), min(a, b)
        print(f"     a={a:<6g} b={b:<8g}: G_AND={gand:.4f}  min={mn:.4f}  ratio G_AND/min={gand/mn:.4f}")
        if b / a >= 100:
            w1 &= abs(gand / mn - 1) < 0.02            # converges to min when separated
    print(f"   G_AND -> min as conductances separate (settle gives min FOR FREE) {w1}")

    # 2. min STRICTLY OVER-PREDICTS at the ridge (a=b): settle = a/2, min = a
    a = 5.0
    w2 = abs(G_AND(a, a) - a / 2) < 1e-12 and min(a, a) == a and G_AND(a, a) < min(a, a)
    print(f"\n2. at the ridge a=b={a}: settle G_AND = {G_AND(a,a)} (= a/2), min = {min(a,a)} (= a) -> "
          f"min over-predicts by 2x; imposing min puts the knee too high {w2}")

    # 3. THE SETTLE IS ENERGY-MINIMIZATION (Thomson): solved voltages minimize dissipated power
    rng = np.random.default_rng(0); n = 6
    edges = [(u, w, float(rng.uniform(0.3, 4))) for u in range(n) for w in range(u + 1, n)]
    src, sink = 0, n - 1
    _, v, _ = solve(n, edges, src, sink)
    P0 = dissipated_power(edges, v)
    interior = [i for i in range(n) if i not in (src, sink)]
    worse = 0
    for _ in range(2000):
        vp = v.copy()
        for i in interior:
            vp[i] += rng.normal(0, 0.01)               # perturb interior voltages only
        if dissipated_power(edges, vp) >= P0 - 1e-12:
            worse += 1
    w3 = worse == 2000
    print(f"\n3. Thomson: the solved interior voltages MINIMIZE dissipated power -- {worse}/2000 random "
          f"perturbations increase P (settle = the energy minimum) {w3}")

    # 4. GEODESIC: R_eff -> the dominant edge's resistance when one edge dominates the path
    #    series chain with one huge resistor: G_eff^-1 -> R_big (geodesic through the bottleneck)
    Gs = [100.0, 100.0, 0.5, 100.0]                    # edge 2 is the bottleneck (R=2)
    chain = [(i, i + 1, g) for i, g in enumerate(Gs)]
    Geff, _, _ = solve(len(Gs) + 1, chain, 0, len(Gs))
    R_eff = 1 / Geff; R_big = 1 / min(Gs)
    w4 = abs(R_eff - R_big) / R_big < 0.05             # R_eff ~ the bottleneck resistance
    print(f"\n4. geodesic / resistance-distance: chain R_eff = {R_eff:.3f} ~ bottleneck R = {R_big:.3f} "
          f"-> G_eff ~ min(conductances) emerges from the settle, not imposed {w4}")

    ok = w1 and w2 and w3 and w4
    print(f"\nGEODESIC MIN: min-emerges {w1}; min-over-predicts-at-ridge {w2}; settle=energy-min {w3}; "
          f"geodesic=bottleneck {w4}")
    print(f"\n  {'PASS' if ok else 'FAIL'} — min() is STRICTLY not the operator: the network settles to the")
    print(f"  minimum-dissipation state (Thomson = Kirchhoff = a resistance-metric geodesic), and that")
    print(f"  settled G_eff IS the answer. min is its asymptote where one constraint dominates (emerges")
    print(f"  for free); at the ridge min over-predicts and the settle gives the true rounded knee. Don't")
    print(f"  impose min, don't even pick a semiring p -- solve, and read min off the dominated regime.")
