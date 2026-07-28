------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitfaces
--
-- Defines: coemit-faces
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitfaces where

open import Substrate.Foundation.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.List
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
open import Substrate.WitnessTower.SimplicialBoundary
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Op2
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Op2
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Algebra.F2
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere


------------------------------------------------------------------------
-- coemit-signed-boundary + coemit-s3-group-laws + coemit-mul-is-boundary (operator: the GRADED STENCIL sets up a
-- GROUPOID — StencilGroupoid: the μ-frame is the ≡-groupoid, the ν-frame is the ~-groupoid, connected by
-- CONTRACTIBILITY [unique up to unique iso]). So the two carriers' boundaries are identified UP TO the groupoid iso.
------------------------------------------------------------------------
-- (1) coemit-signed-boundary: the F₂ boundary ∂ = Σᵢ delAt i (signs vanish over F₂ — "each value occurs twice,
--     the face-pairing cancels", per SimplicialBoundary). ∂∘∂=0 is the simplicial pairing. Here: the list of all
--     faces of a coemit prefix (boundary via the face maps), whose double-application pairs off (∂²=0 shape).

-- all one-step faces of a prefix (the ∂-image, unsigned/F₂): delAt i for each position i < length.
coemit-faces : (r : RealTrace) (n : ℕ) → List (List ℕ)
coemit-faces r n = faces-go 0 (take n r)
  where faces-go : ℕ → List ℕ → List (List ℕ)
        faces-go i []       = []
        faces-go i (x ∷ xs) = delAt i (take n r) ∷ faces-go (suc i) xs
