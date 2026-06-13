------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Log
--
-- B4-next: the natural logarithm on substrate-ℝ, fuel-free, on the bounded-output
-- rails. The naive series log(1+u) = u − u²/2 + … has alternating signs (wants ℤ)
-- and converges only for |u|<1 (wants range reduction). The atanh form avoids
-- BOTH:  log x = 2·atanh((x−1)/(x+1)) = 2·(s + s³/3 + s⁵/5 + …),  s = (x−1)/(x+1).
-- Every term is ≥ 0 (pure ℕ), and s ∈ [0,1) for every x ≥ 1 — no signs, no range
-- reduction. ([[project_substrate_real_arc]] B4; [[feedback_finite_window_constructive_lem]].)
--
-- Evaluated at x's n-th convergent p/q (p ≥ q ⟺ x ≥ 1): s = (p−q)/(p+q), the
-- `terms`-term series as a rational, then the result's CF via the EEA trace.
-- Bounded-output, structural on (terms, n), no fuel. log : ℝ≥1 → ℝ≥0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Log where

open import Substrate.Foundation.Nat     using (ℕ; zero; suc; _+_; _*_; _∸_)
open import Substrate.Foundation.List    using (List)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)

open import Substrate.Algebra.R.Trace          using (RealTrace)
open import Substrate.Algebra.R.Trace.Windowed using (windowed-cf)

------------------------------------------------------------------------
-- The atanh partial sum T = Σ_{k=0}^{terms−1} s²ᵏ/(2k+1) as a rational (Un,Ud),
-- s² = sn²/sd². Horner over the odd denominators od = 2·terms−1, …, 3, 1, each
-- U ↦ 1/od + s²·U = (sd²·Ud + od·sn²·Un)/(od·sd²·Ud). Structural on the term count.
------------------------------------------------------------------------

ath : ℕ → ℕ → ℕ → ℕ → ℕ → ℕ → ℕ × ℕ
ath zero    od sn² sd² Un Ud = (Un , Ud)
ath (suc t) od sn² sd² Un Ud =
  ath t (od ∸ 2) sn² sd² (sd² * Ud + od * sn² * Un) (od * sd² * Ud)

------------------------------------------------------------------------
-- log x = 2·atanh s, evaluated at x's n-th convergent (p ≥ q assumed, x ≥ 1).
------------------------------------------------------------------------

-- thin kernel over `Windowed.windowed-cf` (the apex): log's kernel is the atanh
-- series at s = (p−q)/(p+q), scaled by 2.
log-cf : ℕ → ℕ → RealTrace → List ℕ
log-cf terms = windowed-cf λ p q →
  let sn = p ∸ q
      sd = p + q
      U  = ath terms (2 * terms ∸ 1) (sn * sn) (sd * sd) 0 1
  in 2 * sn * proj₁ U , sd * proj₂ U

------------------------------------------------------------------------
-- Worked example (computed; left as a comment — the EEA-trace reduction on the
-- accumulated rational is heavy for the typechecker; the pieces refl-check in
-- B1 and the probes). At x ≈ 3/2 (√2's 2nd convergent), 1-term atanh:
--   s = (3−2)/(3+2) = 1/5,  log(3/2) ≈ 2·(1/5) = 2/5 = [0;2,2].
--   log-cf 1 2 sqrt2  ≡  0 ∷ 2 ∷ 2 ∷ []   (true 0.405; 1 term gives 0.4).
-- Larger (terms, n) ⟹ closer to log(√2) on a growing CF prefix.
------------------------------------------------------------------------
