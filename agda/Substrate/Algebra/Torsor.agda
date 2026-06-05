------------------------------------------------------------------------
-- Substrate.Algebra.Torsor
--
-- A G-torsor: a set with a free, transitive G-action. Substrate-native
-- (built over Substrate.Algebra.Group + Substrate.Algebra.GroupAction).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Torsor where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Product using (∃; _,_)
open import Substrate.Algebra.Monoid using (ε)
open import Substrate.Algebra.Group using (Group; monoid)
open import Substrate.Algebra.GroupAction using (Actionᴳ; act)

------------------------------------------------------------------------
-- A G-torsor on a carrier T: an Actionᴳ that is free + transitive.
------------------------------------------------------------------------

record IsTorsorᴳ {A : Set} (G : Group A) (T : Set) : Set where      -- ⟦shape:70906623 action,(g,(t₁ t₂⟧
  field
    action     : Actionᴳ G T
    -- Free: only the identity fixes any point.
    free       :
      (g : A) (t : T) →
      act action g t ≡ t →
      g ≡ ε (monoid G)
    -- Transitive: any two points are connected by some group element.
    transitive :
      (t₁ t₂ : T) → ∃ λ g → act action g t₁ ≡ t₂

open IsTorsorᴳ public
