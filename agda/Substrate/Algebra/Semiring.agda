------------------------------------------------------------------------
-- Substrate.Algebra.Semiring
--
-- M6 of the Algebra Ladder arc per [scratch/m_mod_arc_plan.md].
--
-- A Semiring is two compatible monoids (additive commutative,
-- multiplicative) joined by distributivity and zero-absorption.
-- Stands above M3 (Monoid) and below M7 (Ring, which strengthens
-- the additive monoid to AbelianGroup with negation).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Semiring where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup; magma)
open import Substrate.Algebra.Monoid using (Monoid; semigroup; ε)

------------------------------------------------------------------------
-- 1. The Semiring record.
--
-- Carries TWO monoid structures + distributivity + zero-absorbs
-- laws. Each monoid is named explicitly (`+-monoid`, `*-monoid`)
-- and the multiplicative monoid's identity is `1`.
------------------------------------------------------------------------

record Semiring (A : Set) : Set where
  field
    -- Additive structure (commutativity is a separate field, not
    -- here — full AbelianGroup is M7's job).
    +-monoid : Monoid A
    -- Multiplicative structure.
    *-monoid : Monoid A
    -- Distributivity:
    distrib-left :
      (a b c : A) →
      let _+_ = Magma._·_ (magma (semigroup +-monoid))
          _*_ = Magma._·_ (magma (semigroup *-monoid))
      in a * (b + c) ≡ (a * b) + (a * c)
    distrib-right :
      (a b c : A) →
      let _+_ = Magma._·_ (magma (semigroup +-monoid))
          _*_ = Magma._·_ (magma (semigroup *-monoid))
      in (a + b) * c ≡ (a * c) + (b * c)
    -- Zero absorbs multiplication:
    zero-absorb-left :
      (a : A) →
      let _*_ = Magma._·_ (magma (semigroup *-monoid))
      in (ε +-monoid) * a ≡ ε +-monoid
    zero-absorb-right :
      (a : A) →
      let _*_ = Magma._·_ (magma (semigroup *-monoid))
      in a * (ε +-monoid) ≡ ε +-monoid

open Semiring public

------------------------------------------------------------------------
-- 2. Capstone for M6.
--
-- Semiring landed. M7 strengthens to Ring by adding negation
-- (additive AbelianGroup).
------------------------------------------------------------------------
