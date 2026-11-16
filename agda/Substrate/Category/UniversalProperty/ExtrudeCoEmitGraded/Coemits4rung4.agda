------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits4rung4
--
-- Defines: coemit-s4-rung4
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits4rung4 where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.WitnessTower.Wedge.V4Seam
open import Substrate.WitnessTower.Wedge.Factoradic
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- (3) coemit-s4-rung4: the S₄=V₄⋊S₃ debuts at the rung-3→4 wedge (quot = 4 = |V₄|). Reuse V4Seam's seam-wedge-quot.

coemit-s4-rung4 : tower-quotient 3 ≡ 4     -- the rung-4 wedge quotient IS |V₄| = 4 (where S₄=V₄⋊S₃ debuts)
coemit-s4-rung4 = seam-quotient-is-4
