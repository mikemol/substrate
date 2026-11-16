------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.ApproxRefl
--
-- Defines: ≈ᵉ-refl′
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.ApproxRefl where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Unfold
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad ℕ using (CoEmit; ret; emitᶜ; step; _≈ᵉ_; step≈; Step≈; ret≈; emit≈)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Nat.SucInjective
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.CoemitTrace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.ApproxTo
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.Approx



------------------------------------------------------------------------
-- THE FULL COMPOSE-FROM: with the iff (≈ᵉ→~ / ≈ᵉ←~), _≈ᵉ_'s WHOLE equivalence is INHERITED from the
-- universal carrier's — ≈ᵉ-refl/sym/trans are ~-refl/sym/trans transported through coemit-trace. The
-- bespoke step-refl/sym-step/trans-step in ExtrudeCoEmitMonad are now SUPERSEDED (retirable).
------------------------------------------------------------------------

≈ᵉ-refl′ : (c : CoEmit ℕ) → c ≈ᵉ c
≈ᵉ-refl′ c = ≈ᵉ←~ (~-refl (coemit-trace c))
