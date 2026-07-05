------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Ops
--
-- Field operations on RealTrace — the CF-NATIVE, productive ones. A continued
-- fraction makes two operations trivial because they are just digit-position
-- bookkeeping, needing no Gosper search and no corecursion:
--
--   * RECIPROCATION  1/x  — the defining move of a CF. For x>1 (a₀≥1) prepend a
--     0; for x<1 (a₀=0) drop the leading 0. Involutive by construction.
--   * TRANSLATION    x+k  (k : ℕ) — touches only the leading digit a₀ ↦ a₀+k.
--
-- General `+` and `×` are NOT here yet: as unbounded Gosper bi-homographic STATE
-- machines their "ingest-until-emit" loop is not structurally guarded. But that is
-- a wall only for the state-machine framing — the bounded-OUTPUT / output-index
-- trick dissolves it the SAME way it did for the unary homographic (`Window`) and
-- exp/log (`Transcendental`): the n-digit window of x⊕y is a homographic on the
-- n-th convergents of x and y, structural on n ([[feedback_finite_window_constructive_lem]]).
-- So it is unbuilt engineering, not the "hard open problem" I once called it.
-- Meanwhile they live in the windowed ℚ view (compute with the convergents —
-- "reason about ℝ via ℚ"), which is also what B4's exp/log SERIES use. See
-- [[project_substrate_real_arc]] (B3-next / B4).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Ops where

open import Substrate.Foundation.Nat  using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Eq   using (_≡_; refl)

open import Substrate.Algebra.R.Trace using (RealTrace; head; tail; take; sqrt2; twos)
open import Substrate.Algebra.R.Trace.StreamMap using (onHead)

------------------------------------------------------------------------
-- Translation by a natural: x + k changes only the leading CF digit.
-- ⟡dedup.tree: an instance of the lifted `onHead` (modify the head digit only).
------------------------------------------------------------------------

addℕ : ℕ → RealTrace → RealTrace
addℕ k = onHead (k +_)

------------------------------------------------------------------------
-- Reciprocation 1/x — the CF "shift". `cons0` prepends a 0 digit.
------------------------------------------------------------------------

cons0 : RealTrace → RealTrace
head (cons0 x) = 0
tail (cons0 x) = x

recip-go : RealTrace → ℕ → RealTrace
recip-go x zero    = tail x      -- x = [0; a₁,…] (x<1) ⇒ 1/x = [a₁; …]
recip-go x (suc _) = cons0 x      -- x = [a₀; …] (x>1) ⇒ 1/x = [0; a₀, …]

recip : RealTrace → RealTrace
recip x = recip-go x (head x)

------------------------------------------------------------------------
-- Concrete: √2+3 = [4;2,2,…]; 1/√2 = [0;1,2,2,…]; recip is involutive on √2.
------------------------------------------------------------------------

_ : take 4 (addℕ 3 sqrt2) ≡ 4 ∷ 2 ∷ 2 ∷ 2 ∷ []
_ = refl

_ : take 5 (recip sqrt2) ≡ 0 ∷ 1 ∷ 2 ∷ 2 ∷ 2 ∷ []
_ = refl

_ : take 4 (recip (recip sqrt2)) ≡ 1 ∷ 2 ∷ 2 ∷ 2 ∷ []
_ = refl
