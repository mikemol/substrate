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

open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup; magma; ·-assoc)
open import Substrate.Algebra.Monoid
  using (Monoid; semigroup; ε; ε-left; ε-right)
open import Substrate.Algebra.Group
  using (Group; monoid; inv; inv-left; inv-right)
open import Substrate.Algebra.SetoidGroup using (SetoidGroup)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2

------------------------------------------------------------------------
-- The coercion.
------------------------------------------------------------------------

to-setoid : {A : Set} → Group A → SetoidGroup A _≡_
to-setoid {A} G = record
  { _∙_       = Magma._·_ (magma (semigroup (monoid G)))
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
