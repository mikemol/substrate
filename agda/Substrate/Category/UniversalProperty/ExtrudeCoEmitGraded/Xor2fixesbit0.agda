------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Xor2fixesbit0
--
-- Defines: xor2-fixes-bit0
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Xor2fixesbit0 where

open import Substrate.Foundation.Nat
open import Substrate.Foundation.Eq
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace using (coemit-trace) renaming (coalg to coemit-coalg)
open import Substrate.Foundation.Eq using () renaming (trans to ≡-trans)
open import Substrate.Category.Allegory.Refinement using (Refinement) renaming (iterate to Riterate)
open import Substrate.Category.Allegory.Refinement using () renaming (chain to Rchain; _⊑ᶠ_ to _R⊑ᶠ_)
open import Substrate.Algebra.R.Trace.Bisim using (~-trans) renaming (head~ to bhead~; tail~ to btail~)
open import Substrate.Foundation.Eq using (sym; cong) renaming (trans to ≡tr)
open import Substrate.Algebra.R.Trace.Bisim using (~-refl) renaming (_~_ to _~ᵗ_)
open import Substrate.Foundation.Empty using () renaming (⊥ to Bot)
open import Substrate.Algebra.R.Trace.Bisim using (~-sym) renaming (~-refl to ~-refl')
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.N-to-F2-Parity
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Xor2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Parity4periodic


xor2-fixes-bit0 : (n : ℕ) → parity (xor2 n) ≡ parity n
xor2-fixes-bit0 zero                        = refl
xor2-fixes-bit0 (suc zero)                  = refl
xor2-fixes-bit0 (suc (suc zero))            = refl
xor2-fixes-bit0 (suc (suc (suc zero)))      = refl
xor2-fixes-bit0 (suc (suc (suc (suc n))))   =
  -- LHS: parity (xor2 (n+4)) = parity ((xor2 n)+4) ≡ parity (xor2 n)   [4-periodic]
  -- RHS: parity (n+4) ≡ parity n                                        [4-periodic]
  trans (parity-4-periodic (xor2 n)) (trans (xor2-fixes-bit0 n) (sym (parity-4-periodic n)))
