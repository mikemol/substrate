------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.ApproxIsEquivalence
--
-- Defines: ≈ᵉ-isEquivalence
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.ApproxIsEquivalence where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad ℕ using (CoEmit; ret; emitᶜ; step; _≈ᵉ_; step≈; Step≈; ret≈; emit≈)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Category.UniversalProperty.ExtrudeSetoidCategory
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.ApproxRefl
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.ApproxSym
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.ApproxTrans



------------------------------------------------------------------------
-- THE CANONICAL EQUIVALENCE OF _≈ᵉ_ — bundled from the INHERITED (universal-carrier) refl/sym/trans, NOT the
-- retired bespoke ones. Downstream gets _≈ᵉ_'s IsEquivalence from HERE (composed through RealTrace), the
-- single canonical home for the emit-bisimilarity equivalence.
------------------------------------------------------------------------

≈ᵉ-isEquivalence : IsEquivalence {CoEmit ℕ} _≈ᵉ_
≈ᵉ-isEquivalence = record { ≈-refl = ≈ᵉ-refl′ ; ≈-sym = ≈ᵉ-sym′ ; ≈-trans = ≈ᵉ-trans′ }
