------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Window
--
-- General field operations on RealTrace — fuel-free, by bounding the OUTPUT.
--
-- The Gosper STATE MACHINE's ingest-loop has no state-based termination measure:
-- the denominators c, c+d grow without bound and the emit-timing depends on how
-- close the value sits to an integer — i.e. on the input's FUTURE digits. So its
-- termination is input-dependent (genuinely needs sized types or an input
-- hypothesis), and a fuel constant only papers over that.
--
-- But "bounded OUTPUT ⟹ a provable step bound" dissolves it
-- ([[feedback_finite_window_constructive_lem]]): to produce the result to a
-- window of `n` digits, the INPUT needed is bounded — the n-th convergent. So
-- recurse STRUCTURALLY on n (the output precision), no fuel, no Acc-on-state.
-- z evaluated at x's convergent pₙ/qₙ is the RATIONAL (a·pₙ+b·qₙ)/(c·pₙ+d·qₙ);
-- its continued fraction (the EEA trace, `digits-of-EEA`) is the result's CF,
-- valid on a prefix that grows with n. The window edge (the last digit or two)
-- is simply not yet COMMITTED — it may still change as the window grows. That is
-- observation DEPTH, not divergence from a separate "true value": the generator IS
-- the real, the prefix is an exact observation of it to depth n
-- ([[feedback_suspended_generators_not_approximations]]).
--
-- Reuses B1 wholesale: `convergent` (structural on n) + `digits-of-EEA` (the EEA
-- quotients ARE a CF) + `compute-trace`. The "reason about ℝ via ℚ in a window."
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Window where

open import Substrate.Foundation.Nat     using (ℕ; _+_; _*_)
open import Substrate.Foundation.List    using (List; []; _∷_)
open import Substrate.Foundation.Product using (_,_; proj₁; proj₂)
open import Substrate.Foundation.Eq      using (_≡_; refl)

open import Substrate.Algebra.Nat.GCD.ComputeTrace using (compute-trace)
open import Substrate.Algebra.R.Trace using (RealTrace; convergent; digits-of-EEA; sqrt2)

------------------------------------------------------------------------
-- The bounded-output homographic: the CF of (a·x+b)/(c·x+d) to the precision
-- of x's n-th convergent. Structural on n; no fuel.
------------------------------------------------------------------------

homographic-cf : ℕ → ℕ → ℕ → ℕ → ℕ → RealTrace → List ℕ
homographic-cf a b c d n x =
  let p = proj₁ (convergent n x)
      q = proj₂ (convergent n x)
  in digits-of-EEA (proj₂ (compute-trace (a * p + b * q) (c * p + d * q)))

scaleℕ-cf : ℕ → ℕ → RealTrace → List ℕ
scaleℕ-cf k n x = homographic-cf k 0 0 1 n x

------------------------------------------------------------------------
-- Worked example (computed, but left as a comment — the combined
-- convergent + EEA-trace reduction is heavy for the typechecker; the pieces
-- are checked by refl in B1 and the probes):
--   2·√2 = [2;1,4,1,4,…].  scaleℕ-cf 2 6 sqrt2  ≡  2 ∷ 1 ∷ 4 ∷ 1 ∷ 5 ∷ []
-- (2·99/70 = 99/35, CF [2;1,4,1,5]): the reliable prefix [2,1,4,1] matches; the
-- trailing 5 is the window edge — where the rational approximant diverges from
-- 2√2. Larger n ⟹ longer reliable prefix. No fuel; structural on n.
------------------------------------------------------------------------
