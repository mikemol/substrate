------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Windowed
--
-- THE APEX of the windowed-CF family — found by the similarity detector
-- (user, 2026-06-13: "Take a look at our similarity-detector script… enable
-- recursion with type holes"). `agda_similarity.py --recursive --typed-holes` over
-- Exp/Log/Window scored token-scale 0.99+ and extracted a shared skeleton whose
-- only per-file residue is the rational KERNEL (`horner` / `ath` / homographic):
--
--   <op>-cf … n x  =  digits-of-EEA (compute-trace (kernel (x's n-th convergent)))
--
-- i.e. "evaluate x's n-th convergent p/q through an op-specific rational kernel
-- K : (p q) ↦ (N , D), then read the result's continued fraction off the EEA
-- trace." Bounded-output, structural on n, fuel-free — uniformly, ONCE. Exp/Log/
-- Window become thin facades supplying only their kernel
-- ([[discipline/feedback_cluster_means_find_apex]]; [[feedback_fine_grained_over_coarse]]).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Windowed where

open import Substrate.Foundation.Nat     using (ℕ)
open import Substrate.Foundation.List    using (List)
open import Substrate.Foundation.Product using (_×_; proj₁; proj₂)

open import Substrate.Algebra.Nat.GCD.ComputeTrace using (compute-trace)
open import Substrate.Algebra.R.Trace using (RealTrace; convergent; digits-of-EEA)

------------------------------------------------------------------------
-- The wrapper: feed x's n-th convergent (p, q) to the kernel K, take the result's
-- continued fraction (the EEA trace's quotients). The kernel is the only hole.
------------------------------------------------------------------------

windowed-cf : (ℕ → ℕ → ℕ × ℕ) → ℕ → RealTrace → List ℕ
windowed-cf K n x =
  let p  = proj₁ (convergent n x)
      q  = proj₂ (convergent n x)
      ND = K p q
  in digits-of-EEA (proj₂ (compute-trace (proj₁ ND) (proj₂ ND)))
