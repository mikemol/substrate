------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.TraceDescent  (ALG-CF closure)
--
-- PolyEEATrace termination AS the allegory Φ-chain descent — the concrete,
-- F₂[x] realization of `Category/Allegory/Refinement.chain` (ALG-7).  This
-- closes the CF↔allegory tie-in on the polynomial (B-EEA keystone) side.
--
--   * `qdim` — the dimension measure on the trace carrier `QPoly`
--     (a `Poly n` has degree < n, so dim bounds degree — cf. `DegreeBound.lp-bound`).
--   * `step-strict` — each EEA step STRICTLY decreases the measure: the
--     remainder `div-rem` (dim `suc d`) < the divisor `divisor-q` (dim `suc (suc d)`).
--     This is the per-step Φ-chain descent, concretely.
--   * `trace-len-bound` — TERMINATION: the trace length ≤ the divisor dimension.
--     The well-founded measure for B-EEA-COMPUTE, and the proof that the EEA
--     reaches its fixed point (the gcd / the map's singleton fiber) in bounded
--     steps — μΦ converges, for F₂[x].
--
-- NB the generic `Wedge.DivStr`/`CertifiedWedge` bridge does NOT fit here: its
-- `recon : ℕ → C → C → C` takes a ℕ quotient, but polynomial division's quotient
-- is a POLYNOMIAL — which is exactly why `PolyEEATrace` is a parallel construction
-- and the descent is stated directly on it.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.TraceDescent where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _≤_; _<_; z≤n; s≤s)
open import Substrate.Foundation.Product using (Σ; proj₁)
open import Substrate.Foundation.Vec using (Vec)
open import Substrate.Algebra.F2 using (F₂)
open import Substrate.Algebra.F2.Polynomial.Wedge.EEATrace
  using (QPoly; zero-q; divisor-q; div-rem; PolyEEATrace; base; step)

-- the dimension measure on the trace carrier (degree bound: a Poly n has degree < n).
qdim : QPoly → ℕ
qdim = proj₁

-- number of EEA steps in a trace.
trace-len : {a b g : QPoly} → PolyEEATrace a b g → ℕ
trace-len (base a)        = zero
trace-len (step d f-lo s) = suc (trace-len s)

private
  ≤-refl : (n : ℕ) → n ≤ n
  ≤-refl zero    = z≤n
  ≤-refl (suc n) = s≤s (≤-refl n)

-- per-step STRICT descent of the dimension measure (the Φ-chain descent,
-- concretely): the remainder's dimension < the divisor's dimension.
step-strict : (d : ℕ) (f-lo : Vec F₂ (suc d)) (a : QPoly)
            → qdim (div-rem d f-lo a) < qdim (divisor-q d f-lo)
step-strict d f-lo a = ≤-refl (suc (suc d))

-- TERMINATION: the EEA trace length is bounded by the divisor dimension — the
-- well-founded measure for B-EEA-COMPUTE, = the allegory Refinement chain (ALG-7)
-- descent realized for F₂[x].
trace-len-bound : {a b g : QPoly} (t : PolyEEATrace a b g) → trace-len t ≤ qdim b
trace-len-bound (base a)        = z≤n
trace-len-bound (step d f-lo s) = s≤s (trace-len-bound s)
