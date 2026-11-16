------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitfaces
--
-- Defines: coemit-faces
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitfaces where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.List
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.WitnessTower.SimplicialBoundary.DelAt
open import Substrate.WitnessTower.SimplicialBoundary.Len
open import Substrate.WitnessTower.SimplicialBoundary.Private
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


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
