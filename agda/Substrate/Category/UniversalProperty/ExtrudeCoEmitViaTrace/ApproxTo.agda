------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.ApproxTo
--
-- Defines: ≈ᵉ→~
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.ApproxTo where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Unfold
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad ℕ using (CoEmit; ret; emitᶜ; step; _≈ᵉ_; step≈; Step≈; ret≈; emit≈)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Subst
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.Code
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.Next
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.CoemitTrace



------------------------------------------------------------------------
-- THE COMPATIBILITY: the coalgebra morphism PRESERVES bisimulation (≈ᵉ → ~). Arithmetic-free: matching
-- ret≈ a / emit≈ o gives the SAME head on both sides (refl); the tails recurse (guarded under tail~).
------------------------------------------------------------------------
-- head (coemit-trace c) = code (step c); tail (coemit-trace c) = coemit-trace (next c (step c)). Matching
-- step≈ p refines step c and step d to the SAME shape, so code/next reduce and the heads are refl-equal.
≈ᵉ→~ : {c d : CoEmit ℕ} → c ≈ᵉ d → coemit-trace c ~ coemit-trace d
head~ (≈ᵉ→~ {c} {d} p) with step c | step d | step≈ p
... | ret a     | ret .a      | ret≈ .a    = refl
... | emitᶜ o k  | emitᶜ .o k' | emit≈ .o q = refl
tail~ (≈ᵉ→~ {c} {d} p) with step c | step d | step≈ p
... | ret a     | ret .a      | ret≈ .a    = ≈ᵉ→~ p
... | emitᶜ o k  | emitᶜ .o k' | emit≈ .o q = ≈ᵉ→~ q
