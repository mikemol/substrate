------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitrung4action
--
-- Defines: coemit-rung4-action
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitrung4action where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.WitnessTower.Wedge.Factoradic
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits4rung4
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- (3) coemit-rung4-action: the S₄=V₄⋊S₃ debuts at rung 4 (quot=4=|V₄|). The action's ARITY at rung 4 IS |V₄|=4.
--     Reuse coemit-s4-rung4 (tower-quotient 3 ≡ 4); the S₄ acts on the 4 cosets the wedge counts (the V₄ coset space).
coemit-rung4-action : tower-quotient 3 ≡ 4
coemit-rung4-action = coemit-s4-rung4
