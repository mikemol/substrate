------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Exp
--
-- B4: the analytic exponential on substrate-ℝ, fuel-free, on B3's bounded-output
-- rails. exp(x) = Σ xᵏ/k! — a SERIES, so it lives naturally in the ℚ-approximation
-- view: evaluate the m-term Taylor partial sum at x's n-th convergent pₙ/qₙ (a
-- rational), and read off the result's continued fraction (the EEA trace). Two
-- windows — n (input precision) and m (series terms) — both STRUCTURAL, no fuel
-- ([[feedback_finite_window_constructive_lem]]; [[project_substrate_real_arc]] B4).
--
-- The partial sum is a Horner fold over ℕ — exp_m(x) = 1 + (x/1)(1 + (x/2)(1 +
-- … (x/m)·1 …)) — carried as a rational (N,D). exp of a non-negative real (CF
-- digits ℕ ⟹ x ≥ 0); exp : ℝ≥0 → ℝ≥1. (log, the inverse chart, + the exp⊣log
-- Atlas instance are B5.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Exp where

open import Substrate.Foundation.Nat     using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.List    using (List; []; _∷_)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq      using (_≡_; refl)

open import Substrate.Algebra.Nat.GCD.ComputeTrace using (compute-trace)
open import Substrate.Algebra.R.Trace using (RealTrace; convergent; digits-of-EEA; sqrt2)

------------------------------------------------------------------------
-- The m-term Taylor partial sum of exp at the rational p/q, as a rational (N,D).
-- Horner: process divisors j = m … 1, each B ↦ 1 + (p/(q·j))·B, i.e.
-- (Bn,Bd) ↦ (q·j·Bd + p·Bn , q·j·Bd). Structural recursion on the term count.
------------------------------------------------------------------------

horner : ℕ → ℕ → ℕ → ℕ → ℕ → ℕ × ℕ
horner zero    p q Bn Bd = (Bn , Bd)
horner (suc j) p q Bn Bd = horner j p q (q * suc j * Bd + p * Bn) (q * suc j * Bd)

------------------------------------------------------------------------
-- exp(x) to a window: x ≈ its n-th convergent p/q; exp via `terms`-term Taylor;
-- the result's CF via the EEA trace. Bounded-output, structural — no fuel.
------------------------------------------------------------------------

exp-cf : ℕ → ℕ → RealTrace → List ℕ
exp-cf terms n x =
  let p  = proj₁ (convergent n x)
      q  = proj₂ (convergent n x)
      ND = horner terms p q 1 1
  in digits-of-EEA (proj₂ (compute-trace (proj₁ ND) (proj₂ ND)))

------------------------------------------------------------------------
-- Worked (small window — a machinery check, not precision): at √2's 1st
-- convergent (= 1), 2-term Taylor gives exp_2(1) = 1 + 1 + 1/2 = 5/2 = [2;2].
-- Larger (terms, n) ⟹ closer to exp(√2) on a growing CF prefix.
------------------------------------------------------------------------

_ : exp-cf 2 1 sqrt2 ≡ 2 ∷ 2 ∷ []
_ = refl

------------------------------------------------------------------------
-- WALKING A TRANSCENDENTAL: e = exp(1) = Σ 1/k!. No input generator needed — the
-- Horner series AT 1 (horner m 1 1 1 1) is the rational partial sum Σ_{k≤m} 1/k!,
-- and its continued fraction is e's CF, read straight off the EEA trace. e is
-- transcendental (Hermite, 1873); its CF is [2;1,2,1,1,4,1,1,6,…]. Here the first
-- 3 digits, computed through the term window, by refl: exp_3(1) = 8/3 = [2;1,2].
--
-- (The continuous e^{iπ}=−1 is a further arc — signed reals + cos/sin + π + ℂ,
-- since cos π = −1 is negative. Its DISCRETE shadow, the antipode / order-2
-- half-turn e^{2iπ}=1, is already proved in Logic.Evidence.Verdict.Phase as
-- negBoth² = id.)
------------------------------------------------------------------------

e-cf : ℕ → List ℕ
e-cf m = digits-of-EEA (proj₂ (compute-trace (proj₁ (horner m 1 1 1 1))
                                             (proj₂ (horner m 1 1 1 1))))

_ : e-cf 3 ≡ 2 ∷ 1 ∷ 2 ∷ []
_ = refl
