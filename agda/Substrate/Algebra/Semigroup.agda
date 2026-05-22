------------------------------------------------------------------------
-- Substrate.Algebra.Semigroup
--
-- M2 of the Algebra Ladder arc per [scratch/m_mod_arc_plan.md].
--
-- A Semigroup is a Magma + associativity. Extends the M1 record
-- with the single new axiom.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Semigroup where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Algebra.Magma using (Magma)

------------------------------------------------------------------------
-- 1. The Semigroup record.
------------------------------------------------------------------------

record Semigroup (A : Set) : Set where
  field
    magma  : Magma A
    ·-assoc :
      (a b c : A) →
      let _·_ = Magma._·_ magma
      in (a · b) · c ≡ a · (b · c)

open Semigroup public

------------------------------------------------------------------------
-- 2. Capstone for M2.
--
-- Semigroup = Magma + assoc. M3 extends with identity → Monoid.
------------------------------------------------------------------------
