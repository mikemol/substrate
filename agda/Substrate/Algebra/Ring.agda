------------------------------------------------------------------------
-- Substrate.Algebra.Ring
--
-- M7 of the Algebra Ladder arc per [scratch/m_mod_arc_plan.md].
--
-- A Ring extends Semiring with additive AbelianGroup structure
-- (negation). The standard categorical name for the algebraic
-- structure of ℤ, ℚ, ℝ, F₂, F_p (for prime p), etc.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Ring where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup; magma)
open import Substrate.Algebra.Monoid using (Monoid; semigroup; ε)
open import Substrate.Algebra.Group using (Group; monoid)
open import Substrate.Algebra.AbelianGroup using (AbelianGroup; group)
open import Substrate.Algebra.Semiring using (Semiring; +-monoid; *-monoid)

------------------------------------------------------------------------
-- 1. The Ring record.
--
-- Strengthens Semiring's additive monoid to an additive AbelianGroup.
-- We supply the AbelianGroup structure + a coherence witness that
-- its underlying Monoid IS the Semiring's +-monoid.
------------------------------------------------------------------------

record Ring (A : Set) : Set where
  field
    semiring  : Semiring A
    +-abelian : AbelianGroup A
    +-coherent :
      monoid (group +-abelian) ≡ +-monoid semiring

open Ring public

------------------------------------------------------------------------
-- 2. Capstone for M7.
--
-- Ring landed. M8 strengthens to Field by adding multiplicative
-- inverse for nonzero elements.
------------------------------------------------------------------------
