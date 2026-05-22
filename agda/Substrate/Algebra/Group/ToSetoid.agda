------------------------------------------------------------------------
-- Substrate.Algebra.Group.ToSetoid
--
-- Coercion: every `Substrate.Algebra.Group A` lifts to a
-- `Substrate.Algebra.SetoidGroup` using propositional `_≡_` as the
-- setoid relation.
--
-- This bridges the propositional-equality group ladder
-- (Substrate.Algebra.{Magma,Semigroup,Monoid,Group}) into the
-- setoid-equality bundle (Substrate.Algebra.SetoidGroup) used by
-- the substrate's Coxeter-framework consumers (SemidirectProductGroup,
-- GroupAdapter, S4-Composed).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Group.ToSetoid where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup; magma; ·-assoc)
open import Substrate.Algebra.Monoid
  using (Monoid; semigroup; ε; ε-left; ε-right)
open import Substrate.Algebra.Group
  using (Group; monoid; inv; inv-left; inv-right)
open import Substrate.Algebra.SetoidGroup using (SetoidGroup)

------------------------------------------------------------------------
-- The coercion.
------------------------------------------------------------------------

to-setoid : {A : Set} → Group A → SetoidGroup
to-setoid {A} G = record
  { Carrier   = A
  ; _≈_       = _≡_
  ; _∙_       = Magma._·_ (magma (semigroup (monoid G)))
  ; ε         = ε (monoid G)
  ; _⁻¹       = inv G
  ; ≈-refl    = λ _ → refl
  ; ≈-sym     = sym
  ; ≈-trans   = trans
  ; ∙-assoc   = ·-assoc (semigroup (monoid G))
  ; ε-left    = ε-left (monoid G)
  ; ε-right   = ε-right (monoid G)
  ; inv-left  = inv-left G
  ; inv-right = inv-right G
  ; ∙-cong    = cong₂ (Magma._·_ (magma (semigroup (monoid G))))
  ; ⁻¹-cong   = cong (inv G)
  }
