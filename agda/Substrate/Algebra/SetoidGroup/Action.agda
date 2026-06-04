------------------------------------------------------------------------
-- Substrate.Algebra.SetoidGroup.Action
--
-- A left action of a SetoidGroup on a set. Substrate-native; mirrors
-- Substrate.Algebra.GroupAction.Action but parametric over
-- SetoidGroup so files using setoid-style groups (Symmetric, SFin,
-- Coxeter Word-based groups) can describe actions.
--
-- The act axioms use propositional equality on the action carrier
-- (which is sufficient when the target's natural equality IS _≡_).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.SetoidGroup.Action where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Algebra.SetoidGroup using (SetoidGroup)

record Action (G : SetoidGroup) (B : Set) : Set where      -- ⟦shape:2f58ed86 act,act-id,(g h⟧
  open SetoidGroup G
  field
    act     : Carrier → B → B
    act-id  : (b : B) → act ε b ≡ b
    act-∙   :
      (g h : Carrier) (b : B) →
      act (g ∙ h) b ≡ act g (act h b)

open Action public
