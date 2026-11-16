------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Lh
--
-- Defines: lh
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Lh where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.List
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Chain
open import Substrate.Category.Allegory.Refinement.Iterate
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Allegory.Refinement.SqsubF
open import Substrate.Category.Allegory.Refinement.Chain
open import Substrate.Category.Allegory.Refinement.Iterate
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Allegory.Refinement.SqsubF
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Takevec
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitdescent
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- coemit-chain-limit: the finite-prefix chain's LIMIT is the trace. The graded prefixes (take n, forget of
-- take-vec n) approximate the flat trace; their limit (ALL n) DETERMINES it up to ~ — prefix-separates : if two
-- traces have equal prefixes at every grade, they are bisimilar. So the flat trace IS the limit of the graded
-- descent (⋂ₙ the prefixes = the trace up to ~), the ν-endpoint the graded chain approximates. (cf coemit-descent.)
------------------------------------------------------------------------

-- total List head/tail projections (default at []) — cong on these extracts ∷-injectivity without refl-pattern ambiguity.
lh : ℕ → List ℕ → ℕ
lh d []       = d
lh _ (x ∷ _)  = x
