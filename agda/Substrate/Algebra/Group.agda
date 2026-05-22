------------------------------------------------------------------------
-- Substrate.Algebra.Group
--
-- M4 of the Algebra Ladder arc per [scratch/m_mod_arc_plan.md].
--
-- A Group is a Monoid + inverse function + inverse laws. The
-- standard group structure.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Group where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup; magma)
open import Substrate.Algebra.Monoid using (Monoid; semigroup; ε)

------------------------------------------------------------------------
-- 1. The Group record.
------------------------------------------------------------------------

record Group (A : Set) : Set where
  field
    monoid   : Monoid A
    inv      : A → A
    inv-left :
      (a : A) →
      let _·_ = Magma._·_ (magma (semigroup monoid))
      in (inv a) · a ≡ ε monoid
    inv-right :
      (a : A) →
      let _·_ = Magma._·_ (magma (semigroup monoid))
      in a · (inv a) ≡ ε monoid

open Group public

------------------------------------------------------------------------
-- 2. Capstone for M4.
--
-- Group = Monoid + inverse. M5 extends with commutativity →
-- AbelianGroup.
------------------------------------------------------------------------
