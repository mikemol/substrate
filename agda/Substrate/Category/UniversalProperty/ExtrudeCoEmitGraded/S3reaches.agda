------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3reaches
--
-- Defines: s3-reaches
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3reaches where

open import Substrate.Foundation.Nat
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace using (coemit-trace) renaming (coalg to coemit-coalg)
open import Substrate.Foundation.Product
open import Substrate.Foundation.Eq using () renaming (trans to ≡-trans)
open import Substrate.Category.Allegory.Refinement using (Refinement) renaming (iterate to Riterate)
open import Substrate.Category.Allegory.Refinement using () renaming (chain to Rchain; _⊑ᶠ_ to _R⊑ᶠ_)
open import Substrate.Algebra.R.Trace.Bisim using (~-trans) renaming (head~ to bhead~; tail~ to btail~)
open import Substrate.Foundation.Eq using (sym; cong) renaming (trans to ≡tr)
open import Substrate.Category.UniversalProperty.ExtrudeBisimUpTo
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
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3onaxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Swap01
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Swap12


-- TRANSITIVITY: from any axis, some S₃ permutation reaches any target axis (the single orbit = higher-order finite).
s3-reaches : (a b : GradingAxis) → Σ (Fin 3 → Fin 3) (λ σ → s3-on-axis σ a ≡ b)
s3-reaches μν-axis        μν-axis        = (λ x → x) , refl
s3-reaches μν-axis        head-tail-axis = swap01 , refl
s3-reaches μν-axis        cyc-aper-axis  = swap12 ∘f swap01 , refl
  where _∘f_ : (Fin 3 → Fin 3) → (Fin 3 → Fin 3) → (Fin 3 → Fin 3)
        (f ∘f g) x = f (g x)
s3-reaches head-tail-axis μν-axis        = swap01 , refl
s3-reaches head-tail-axis head-tail-axis = (λ x → x) , refl
s3-reaches head-tail-axis cyc-aper-axis  = swap12 , refl
s3-reaches cyc-aper-axis  μν-axis        = swap01 ∘f swap12 , refl
  where _∘f_ : (Fin 3 → Fin 3) → (Fin 3 → Fin 3) → (Fin 3 → Fin 3)
        (f ∘f g) x = f (g x)
s3-reaches cyc-aper-axis  head-tail-axis = swap12 , refl
s3-reaches cyc-aper-axis  cyc-aper-axis  = (λ x → x) , refl
