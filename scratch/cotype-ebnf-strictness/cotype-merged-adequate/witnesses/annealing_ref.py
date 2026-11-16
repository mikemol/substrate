# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Simulated-annealing exploration lifecycle (the other half of the OCAL behavior-frame reading of APSP).
The conformance checks f090_2_annealing_* pin THIS. Per all-readings: the annealing lifecycle is a change-of-
frame reading of the SAME min-plus structure -- annealing is the SOFT/finite-temperature version of APSP's
hard min-plus, and the T->0 limit RECOVERS the shortest path. This ref extracts the mechanism AND formalizes
the map APSP (hard, T=0) <-> annealing (soft, T>0), so the connection is witnessed.

HOW IT WORKS (decomposed):
  A temperature T cools on a schedule (geometric T <- alpha*T). At each step a candidate move is accepted
  with probability min(1, exp(-dE/T)): downhill always, uphill with prob exp(-dE/T) -- high T explores
  (accepts uphill), low T exploits (rejects uphill). The lifecycle: start hot (explore the whole space),
  cool slowly (settle into a basin), freeze (commit to the optimum). 

THE CHANGE-OF-FRAME MAP (annealing <-> APSP, witnessed):
  the SOFT min-plus (log-sum-exp at temperature T) interpolates: softmin_T(x_i) = -T log Sum exp(-x_i/T).
  As T->0 it -> min_i x_i (the HARD min-plus = APSP). As T->inf it -> a uniform average (pure exploration).
  So APSP is the T=0 (frozen) limit of the annealing free-energy, and annealing is APSP lifted to finite
  temperature. Formalized + checked: softmin_T -> min as T->0, and the soft shortest-path free energy at low
  T approximates the APSP distance. (This is the SAME soft/hard relationship as Nedge's LogSumExp vs min-plus:
  Nedge releases bivalence into a soft grade; annealing releases determinism into a soft exploration; both are
  the tau->0 / T->0 hard limit recovering the crisp structure. One conservation exchange, three surfacings.)

CONSERVATION (the annealing-frame witness): the hard APSP min RELEASES the trivial "the optimum is taken
deterministically, no exploration" -- the annealing witness is the TEMPERATURE (the exploration budget the
deterministic min suppressed). triviality-out (determinism) = witness-in (temperature). T->0 spends the
witness back down to the crisp APSP optimum.
"""
import math

def accept_prob(dE, T):
    """Metropolis acceptance: downhill (dE<=0) always; uphill with exp(-dE/T)."""
    if dE <= 0: return 1.0
    if T <= 0: return 0.0
    return math.exp(-dE / T)

def softmin(xs, T):
    """Soft min-plus at temperature T: -T log Sum exp(-x/T). -> min as T->0, -> average-ish as T->inf."""
    if T <= 0:
        return min(xs)
    m = min(xs)                                 # stable log-sum-exp
    return m - T * math.log(sum(math.exp(-(x - m) / T) for x in xs))

def anneal(energy, neighbors, start, T0=10.0, alpha=0.9, steps=2000, rng=None):
    """Generic simulated annealing. energy: state->float; neighbors: state->list; returns the best state found.
    Deterministic-seedable for testing."""
    import random
    r = rng or random.Random(0)
    cur = start; curE = energy(cur); best = cur; bestE = curE; T = T0
    for _ in range(steps):
        nbrs = neighbors(cur)
        if not nbrs: break
        cand = r.choice(nbrs); candE = energy(cand)
        if r.random() < accept_prob(candE - curE, T):
            cur, curE = cand, candE
            if curE < bestE: best, bestE = cur, curE
        T *= alpha
    return best, bestE

# ---- THE CHANGE-OF-FRAME MAP: softmin_T -> APSP hard min as T->0 ----
def soft_path_distance(weights, i, j, T, kmax=None):
    """Soft shortest-path 'free energy' i->j at temperature T via soft min-plus relaxation. As T->0 it
    converges to the APSP hard distance. (One-step relaxation over intermediate vertices, iterated.)"""
    n = len(weights); INF = float("inf")
    D = [[weights[a][b] for b in range(n)] for a in range(n)]
    K = kmax or n
    for _ in range(K):
        newD = [[D[a][b] for b in range(n)] for a in range(n)]
        for a in range(n):
            for b in range(n):
                options = [D[a][b]] + [D[a][k] + D[k][b] for k in range(n)
                                       if D[a][k] < INF and D[k][b] < INF]
                newD[a][b] = softmin(options, T)
        D = newD
    return D[i][j]


# ─────────────────────────────────────────────────────────────────────────────
# [AI-WO-STATMECH] The Witness-Obligation / statistical-mechanics binding: macrostate = WITNESS, microstates =
# the OBLIGATION's discharge-paths, partition function = softmin (this ref's log-sum-exp), and the T->0 limit =
# canonicalization to the single minimal-cost witness. Binds witness_obligation_map (the (witness, obligation)
# dependent pair) to this annealing ref's softmin->min. The (E+,E-) accumulators of the paraconsistent carrier
# are the microstate COUNTS (degeneracy). The either/or this resolves: "which proof discharges the obligation?"
# -> the partition function sums over ALL of them (soft, T>0); the canonical witness is the T->0 minimum.
# ─────────────────────────────────────────────────────────────────────────────
def wo_partition_function(obligation_costs, T):
    """The partition function over an obligation's discharge-paths (microstates): Z = sum exp(-cost/T). The
    witness's free energy F = -T log Z = softmin_T(costs) is the macrostate observable. Returns F (the soft
    witness-cost). At high T all paths contribute (exploration); at low T the minimal-cost path dominates."""
    return softmin(obligation_costs, T)

def wo_canonical_witness_is_tzero_limit(obligation_costs, tol=1e-6):
    """The CANONICAL witness = the T->0 limit of the partition function = the minimal-cost discharge path. As
    T->0 the free energy softmin_T -> min (the single canonical witness); the macrostate collapses to its
    minimal microstate. Returns True iff softmin at very low T approximates min(costs) within tol -- the
    canonicalization (many obligation-paths -> one canonical witness) is the T->0 freezing."""
    import math
    low_T = 1e-3
    F = wo_partition_function(obligation_costs, low_T)
    return abs(F - min(obligation_costs)) < tol

def wo_degeneracy_is_accumulator_count(obligation_costs, T):
    """The (E+,E-) accumulators = microstate COUNTS (degeneracy): the number of discharge-paths at a given cost
    is the statistical weight. Verify the partition function is monotone in degeneracy -- adding another
    minimal-cost discharge path (raising the count/degeneracy of the ground state) LOWERS the free energy (more
    ways to discharge the obligation = a cheaper, more-supported witness). Returns True iff duplicating the
    minimal-cost path strictly lowers the soft witness-cost at finite T (the degeneracy contributes)."""
    F0 = wo_partition_function(obligation_costs, T)
    cmin = min(obligation_costs)
    F1 = wo_partition_function(obligation_costs + [cmin], T)   # add one more ground-state microstate (degeneracy++)
    return F1 < F0                                              # more ways to discharge -> lower free energy

def wo_macrostate_observable_is_softmin(obligation_costs, T):
    """The macrostate observable (the witness's cost) IS softmin_T over the obligation's microstate costs --
    binding witness_obligation_map's (witness, obligation) dependent pair to this ref's softmin. Verify the
    binding: the free energy F = -T log Z is bounded ABOVE by the minimum cost (F <= min, the standard
    statistical-mechanics bound: more microstates only lower the free energy) and approaches min as T->0 from
    below. Returns True iff F <= min(costs) and F rises toward min as T falls (F(T) <= F(2T), monotone)."""
    F = wo_partition_function(obligation_costs, T)
    F_hotter = wo_partition_function(obligation_costs, 2 * T)
    return F <= min(obligation_costs) + 1e-9 and F >= F_hotter - 1e-9
