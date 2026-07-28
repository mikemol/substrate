------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitdigitisv4morph
--
-- Defines: coemit-digit-is-v4-morph
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitdigitisv4morph where

open import Substrate.Foundation.Nat
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace using (coemit-trace) renaming (coalg to coemit-coalg)
open import Substrate.Foundation.Eq using () renaming (trans to ≡-trans)
open import Substrate.Category.Allegory.Refinement using (Refinement) renaming (iterate to Riterate)
open import Substrate.Category.Allegory.Refinement using () renaming (chain to Rchain; _⊑ᶠ_ to _R⊑ᶠ_)
open import Substrate.Algebra.R.Trace.Bisim using (~-trans) renaming (head~ to bhead~; tail~ to btail~)
open import Substrate.Foundation.Eq using (sym; cong) renaming (trans to ≡tr)
open import Substrate.Category.UniversalProperty.ExtrudeBisimUpTo
open import Substrate.Algebra.R.Trace.Bisim using (~-refl) renaming (_~_ to _~ᵗ_)
open import Substrate.Foundation.Empty using () renaming (⊥ to Bot)
open import Substrate.Algebra.R.Trace.Bisim using (~-sym) renaming (~-refl to ~-refl')
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflip
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflipflipsparity
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4flipmorph
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4flipobj
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Xor2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Digittov4
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflipfixesbit1


-- the two homomorphism laws: digit-to-v4 intertwines (pflip, xor2) with (v4-flip-morph, v4-flip-obj).
coemit-digit-is-v4-morph : (n : ℕ) → digit-to-v4 (pflip n) ≡ v4-flip-morph (digit-to-v4 n)
coemit-digit-is-v4-morph n = cong₂ V4.v4 (pflip-flips-parity n) (pflip-fixes-bit1 n)
