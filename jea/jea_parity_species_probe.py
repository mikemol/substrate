#!/usr/bin/env python3
# =============================================================================
# jea_parity_species_probe.py   (Ⓟ — the orbit-cloud parity-species probe)
#
# Δ-G2-wired (jea_regression_gate SYMPY subset): pure sympy, no GPU. DEFAULT runs
# rung 3 only (~0.2s, the load-bearing idempotent-species claim); --full adds
# rung 4 (~8s, faithfulness); --deep adds rung 5 (~minutes, manual only).
#
# (a) THE §0 FINDING (literate). POINT_CLOUD_HODGE_FORMALIZATION.md §0's earlier
#     "rung 3 -> 22-not-24 by a generic-vector near-degeneracy" was WRONG on
#     mechanism. The exact, corpus-and-compile-verified statement:
#
#     The rung-3 orbit cloud is EXACTLY 22 under exact rational arithmetic --
#     NOT a float near-degeneracy (exact sympy dedup gives 22), and NOT an
#     orbit-size claim (22 does not divide 24, correctly: the acting object is
#     the REPRESENTATION'S IMAGE, not S4). Mechanism: the cycle-space rep
#     S4 -> GL(3,Q) is NOT FAITHFUL. It identifies exactly two pairs of
#     permutations, each pair related by the V2 double-transposition
#     tau = (0 1)(2 3). On cycle space tau acts as a REFLECTION T:
#         T^2 = I,  eigenvalues {-1 (once), +1 (twice)}.
#     So 24 frames -> 22 distinct cycle-space maps -> 22 distinct image points.
#     The 22 is the SUCCESS CONDITION of the experiment, not an artifact: V2
#     rerouted exactly 2 points at the rung-3 grade transition -- caught in the act.
#
#     *** CORRECTION (Ⓟ.3″ / Ⓖ★, verify-by-compile) ***  An earlier draft said T
#     "negates the 1-dim WITNESS line ... the static kernel and the dynamic
#     reflection are ONE line." That collapses a WEDGE. In a CONSISTENT cycle
#     basis (CenterWitness's), the static antisymmetric-form kernel w=(1,-1,1)
#     and the dynamic reflection's -1 axis d=(1,-1,0) are DISTINCT lines (w is
#     not even a T-eigenvector: T*w=(0,0,1)); they are glued by d = (I - T)*w.
#     So rung 3 carries TWO parity-distinguished lines (static kernel + dynamic
#     axis), not one. Mechanized in Substrate.Logic.Evidence.ElAtlas.
#     OrbitCloudRung3Wedge (Ⓟ.3″) and unified with the genus in GenusSpecies (Ⓖ★).
#
#     IDENTITY WITH ZERO-DIVISORS (the genus). The reroute is a zero-divisor:
#     (T - I)(T + I) = T^2 - I = 0 with both factors nonzero. The analysis-grade
#     FAILURE (rep not faithful; the collapsed direction is non-invertible) IS
#     the structural-grade WITNESS (the retained parity line / fiber).
#
#     TWO SPECIES within that genus (the load-bearing refinement):
#       * IDEMPOTENT/involution species:  T^2 = I, e=(I+T)/2, e(1-e)=0. The V2
#         reflection. The clean / orthogonal-idempotent extreme, mechanized in
#         CenterIsStarCRT (Xi-star.c^n) and unified in GenusSpecies (Ⓖ★).
#       * NILPOTENT species:  N^n = 0 (d^n = 0). The cross_term degree>1 graded
#         residue (NComplex / CenterIsStarLocal). The retained COST.
#     The rung-3 V2 reroute is the IDEMPOTENT species (T^2=I; N=T-I is NOT
#     nilpotent) -- the clean extreme.
#
# (b) THE PROBE. Does the NILPOTENT species also appear in this orbit-cloud
#     experiment at higher rungs (a reroute with N^k=0 rather than T^2=I)? The
#     verdict below: rungs >= 4 are FAITHFUL (no reroute at all), so the cloud
#     shows ONLY the idempotent species, ONLY at rung 3 -- the nilpotent species
#     lives only in cross_term / the carried residue, invisible to orbit geometry.
# =============================================================================
import sys
import sympy as sp
from itertools import combinations, permutations
from math import comb


def cyc_maps(nv):
    """The (nv)! frame actions on the cycle space of K_nv (exact rational)."""
    edges = list(combinations(range(nv), 2)); eidx = {e: i for i, e in enumerate(edges)}
    tree = set((0, j) for j in range(1, nv)); rows = []
    for e in edges:
        if e in tree:
            continue
        a, b = e; v = [0] * len(edges); v[eidx[e]] += 1
        if a != 0:
            v[eidx[(0, a)]] -= 1
        if b != 0:
            v[eidx[(0, b)]] += 1
        rows.append(v)
    C = sp.Matrix(rows); Cpinv = C.T * (C * C.T).inv()

    def edge_perm(p):
        m = len(edges); P = sp.zeros(m, m)
        for j, (a, b) in enumerate(edges):
            pa, pb = p[a], p[b]; e2 = (pa, pb) if pa < pb else (pb, pa); P[eidx[e2], j] = 1
        return P
    return [(p, C * edge_perm(p) * Cpinv) for p in permutations(range(nv))], C.shape[0]


def nilpotent_index(M, cap=8):
    Mk = M
    for k in range(1, cap + 1):
        if sp.simplify(Mk) == sp.zeros(*M.shape):
            return k
        Mk = sp.simplify(Mk * M)
    return None


results = []


def check(name, cond):
    ok = bool(cond); results.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    return ok


def probe_rung(n):
    """Returns (n_distinct, species-dict) for rung n (K_{n+1}, cycle-dim C(n,2))."""
    nv = n + 1; cyc_dim = comb(n, 2)
    print(f"\n=== rung {n}: K{nv}, cycle-dim {cyc_dim} ===")
    maps, dim = cyc_maps(nv); I = sp.eye(dim)
    classes = []
    for (p, M) in maps:
        hit = None
        for k, (rep, idx) in enumerate(classes):
            if sp.simplify(M - rep) == sp.zeros(dim, dim):
                hit = k; break
        if hit is None:
            classes.append((M, [p]))
        else:
            classes[hit][1].append(p)
    n_distinct = len(classes); n_collisions = sum(len(idx) - 1 for _, idx in classes)
    print(f"  frames {len(maps)} -> distinct maps {n_distinct}  (collisions: {n_collisions})")
    # for each COLLIDING pair, the 'invisible' g = p1 . p0^-1, its action T_g, and species
    species = {}
    for (M, ps) in classes:
        if len(ps) < 2:
            continue
        p0 = ps[0]
        for p1 in ps[1:]:
            inv0 = [0] * nv
            for i, x in enumerate(p0):
                inv0[x] = i
            g = tuple(p1[inv0[i]] for i in range(nv))     # p1 ∘ p0^-1
            _, Tg = next((pp, MM) for pp, MM in maps if pp == g)
            isI = sp.simplify(Tg - I) == sp.zeros(dim, dim)
            invol = sp.simplify(Tg * Tg - I) == sp.zeros(dim, dim)
            N = sp.simplify(Tg - I); nidx = nilpotent_index(N)
            kind = ("trivial" if isI else
                    "IDEMPOTENT/involution (T^2=I)" if invol else
                    f"NILPOTENT (N^{nidx}=0)" if nidx else "OTHER")
            species.setdefault(kind, 0); species[kind] += 1
    if species:
        print(f"  reroute species: {dict(species)}")
    else:
        print(f"  reroute species: NONE (faithful at this rung -- no collisions)")
    return n_distinct, species


def main():
    rungs = [3]
    if "--full" in sys.argv:
        rungs = [3, 4]
    if "--deep" in sys.argv:
        rungs = [3, 4, 5]
    saw_nilpotent = False
    for n in rungs:
        n_distinct, species = probe_rung(n)
        if any("NILPOTENT" in k for k in species):
            saw_nilpotent = True
        if n == 3:
            check("rung 3: cloud is exactly 22 (idempotent V2 reroute, not 24, not float)", n_distinct == 22)
            check("rung 3: the reroute is IDEMPOTENT species (T^2=I), NOT nilpotent",
                  any("IDEMPOTENT" in k for k in species))
            check("rung 3: NO nilpotent reroute (clean extreme only)",
                  not any("NILPOTENT" in k for k in species))
        else:  # rungs >= 4 are faithful: distinct == (n+1)!, no reroute
            from math import factorial
            check(f"rung {n}: FAITHFUL (distinct == {n + 1}! = {factorial(n + 1)}, no reroute)",
                  n_distinct == factorial(n + 1) and not species)

    print("\n=== VERDICT ===")
    check("no NILPOTENT reroute appears in the orbit cloud at any tested rung "
          "(the nilpotent species lives only in cross_term, invisible to orbit geometry)",
          not saw_nilpotent)

    npass = sum(ok for _, ok in results)
    print(f"\n=== TALLY: {npass}/{len(results)} exact checks pass ===")
    return 0 if npass == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
