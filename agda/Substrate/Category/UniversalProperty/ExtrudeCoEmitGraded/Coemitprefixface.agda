------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitprefixface
--
-- Defines: coemit-prefix-face
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitprefixface where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.WitnessTower.SimplicialBoundary.DelAt
open import Substrate.WitnessTower.SimplicialBoundary.Len
open import Substrate.WitnessTower.SimplicialBoundary.Private
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- coemit-delAt-literal + coemit-s3-permutation + coemit-hodge-axis: the FORMAL V₄/simplicial links.
-- (1) The coemit prefixes (take n r : List ℕ, the μ-carrier) carry SimplicialBoundary's delAt face maps and the
--     EXACT ∂²=0 law (simplicial i j i≤j). trace-mul (the ν-side ∂) squares to z; the μ-side prefixes obey the
--     literal simplicial identity. So the coemit grading's boundary IS SimplicialBoundary's ∂ on its prefixes.
------------------------------------------------------------------------

-- the coemit prefix face maps: delAt i on take n r (the μ-carrier List ℕ) — the i-th simplicial face of a prefix.
coemit-prefix-face : ℕ → RealTrace → ℕ → List ℕ
coemit-prefix-face i r n = delAt i (take n r)
