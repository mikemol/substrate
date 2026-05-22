------------------------------------------------------------------------
-- Substrate.Algebra.AbelianGroup
--
-- M5 of the Algebra Ladder arc per [scratch/m_mod_arc_plan.md].
--
-- An AbelianGroup is a Group + commutativity. The additive group
-- of a Ring is an AbelianGroup; F₂'s additive structure is one;
-- ℚ's additive structure is one.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.AbelianGroup where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup; magma)
open import Substrate.Algebra.Monoid using (Monoid; semigroup)
open import Substrate.Algebra.Group using (Group; monoid)

------------------------------------------------------------------------
-- 1. The AbelianGroup record.
------------------------------------------------------------------------

record AbelianGroup (A : Set) : Set where
  field
    group   : Group A
    ·-comm :
      (a b : A) →
      let _·_ = Magma._·_ (magma (semigroup (monoid group)))
      in a · b ≡ b · a

open AbelianGroup public

------------------------------------------------------------------------
-- 2. Capstone for M5.
--
-- AbelianGroup = Group + comm. M6 supplies Semiring (two
-- compatible monoids + distrib).
------------------------------------------------------------------------
