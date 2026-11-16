# The prime-indexed coboundary obstruction tower (witnesses)

Re-runnable witnesses for the finding that the cycle-space rep of `S_{n+1}` on
`K_{n+1}` hosts a tower of **zero-divisor species**, one per coboundary degree,
indexed by the primes, living on roots of unity, igniting where the prime divides
the vertex count. Pure sympy, no GPU. Each script self-checks against the recorded
numbers below; if a number drifts, the grade drifts — re-run before trusting.

## What each script establishes (exact rational arithmetic)

- `probe_faithful_generators.py LO HI` — faithfulness on GENERATORS (a 3-cycle tests
  A_{n+1}, a transposition tests parity), O(n) matrices/rung not (n+1)!. Result:
  **no kernel collapse, rungs 3–12** (no 3-cycle, no transposition in the kernel).
  Corrects the old probe's "rungs ≥ 4 FAITHFUL" overclaim: faithful-so-far is right,
  the ∀-quantifier was not earned. Reuses S_n ⊂ S_{n+1} (kernel is detected on
  generators, the user's "reuse n! for (n+1)!" insight applied to the right question).

- `probe_orbit_cloud.py LO HI` — the CORRECT recurrence test (generic-vector orbit
  stabilizer), the actual rung-3 mechanism. Result: rung 3 cloud **22** with 2
  `(2,2)` idempotent fixers; rungs 4,5,6,7 **clean** (full cloud, zero fixers). The
  rung-3 degeneracy does NOT recur as a same-orbit collision through rung 7.

- `probe_v2_study.py` — how the V₂ (double-transposition) class manifests in cycle
  space at rungs 2,3,4. Result (non-obvious): the single conjugacy class SPLITS into
  distinct cycle-space actions — rung 3: one reflection `{−1,1,1}` + one singular
  projection `{1,0,0}`; rung 4: 15 distinct actions, **irrational spectra** (`√5/5`),
  **102 of 105 pairs NON-commuting**. The V₂'s are a twisted non-commuting weave by S₅.

- `probe_zerodiv_span.py LO HI` — reframes the reflection "die-out" as a ZERO-DIVISOR
  event (the user's key move). Tracks SINGULAR V₂ actions (det 0, a 0-eigenvalue =
  the annihilated direction) and the span vs intersection of their kernels. Result:

  | rung | S    | singular V₂ | annihilation span | common (centralized?) |
  |------|------|-------------|-------------------|-----------------------|
  | 3    | S₄   | 1           | 2/3               | dim 2 — CENTRALIZED    |
  | 4    | S₅   | **0**       | —                 | (species absent)       |
  | 5    | S₆   | 10          | 9/10              | dim 0 — DISTRIBUTED    |
  | 6    | S₇   | **0**       | —                 | (species absent)       |
  | 7    | S₈   | 101         | 21/21 (saturated) | dim 0 — DISTRIBUTED    |

  The zero-divisor (order-2) species lives on **even-vertex** K (nv = 4,6,8 ⟺ odd
  rung), absent on odd-vertex (nv = 5,7). Centralized at rung 3 (clean idempotent,
  one shared null plane), DISTRIBUTED at rungs 5,7 (the twist — no shared null
  vector, the annihilation fragmented and growing toward saturation).

- `probe_sign_link.py` — the −1 / fixed-point-free link, AND the correction. Result:
  the SINGULAR species is the V₂ that is NOT fixed-point-free (the one with leftover
  fixed points — the residual fixed point is the `x = −x` / characteristic-2 collapse,
  and the collapse-point IS the 0-eigenvalue). The genuinely fixed-point-free perfect
  matching is NON-singular (det ≠ 0). At rung 5 the matching involution carries a
  **`−1/3` eigenspace** — the 2-structure already coupled to 3-torsion.

- `probe_order3.py LO HI` — the order-3 analogue (the user's real conjecture). Result:
  the order-3 zero-divisor species **ignites at nv = 6** (rung 5, first nv divisible
  by 3 and > 3): `(3)`-class 28 singular, `(3,3)`-class 26 singular. ABSENT at
  nv = 4,5,7 (nv ≢ 0 mod 3). Spectrum is the **primitive cube roots of unity**
  `ω = −1/2 ± √3·i/2`, with a `0` eigenvalue at ignition. Where order-2 gave `−1`
  (2nd root), order-3 gives `ω` (3rd roots), igniting where 3 | nv.

## The tower (degrees 1–2 confirmed; prime-indexed conjecture)

- **Degree 1 — the sign ε:** root of unity `−1` (order 2); zero-divisor species on
  even nv ⟺ "every prime but 2" ⟺ `−1 ≠ 1` realizable. The commutativity grade.
- **Degree 2 — the coboundary dε:** root of unity `ω` (order 3); zero-divisor species
  on nv ÷ 3 ⟺ "not coprime to 3". The associator grade.
- These are the SAME ε / dε proven --safe in
  `agda/Substrate/Algebra/CayleyDickson/Cocycle.agda` (ε the 2-cochain sign, dε its
  coboundary 3-cochain). The rep's two zero-divisor species ARE the two cochain
  degrees, seen as roots of unity.

**Conjecture (grade-2, confirmed at two degrees):** degree k ↔ prime p_{k+1} ↔
primitive p-th roots of unity ↔ zero-divisor ignition at p | nv. "Coprime to 6"
(= odd and not multiple of 3) = degrees 1 and 2 jointly nontrivial.

**Falsifiable next step:** order-5 species at nv = 10 (rung 9), primitive 5th-root
spectrum (√5-flavored), AND **no independent order-4** (4 = 2² should be order-2
composed, not a new primitive degree). Order-4-vs-order-5 is THE discriminating
experiment: if order-4 ignites independently at nv ÷ 4 the index is "all integers";
if it does not and order-5 ignites at nv ÷ 5, the index is genuinely PRIME. nv = 8
(rung 7) already affords nv ÷ 4 — probe the (4)/(4,4) class there for independent
ignition; nv = 10 (rung 9) is the order-5 test (needs conjugacy-class-targeted
search, not 10! enumeration).

## Run

    python3 probe_faithful_generators.py 3 12
    python3 probe_orbit_cloud.py 3 7
    python3 probe_v2_study.py
    python3 probe_zerodiv_span.py 3 7
    python3 probe_sign_link.py
    python3 probe_order3.py 2 6
