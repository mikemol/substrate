------------------------------------------------------------------------
-- Substrate.Algebra.Field
--
-- M8 of the Algebra Ladder arc per [scratch/m_mod_arc_plan.md].
--
-- A Field is a Ring + multiplicative inverse for non-zero elements
-- + non-triviality (0 ≠ 1). The leaf of the algebra ladder; F₂ and
-- ℚ both instantiate as Field at M9 and M10.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Field where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup; magma)
open import Substrate.Algebra.Monoid using (Monoid; semigroup; ε)
open import Substrate.Algebra.Semiring using (Semiring; +-monoid; *-monoid)
open import Substrate.Algebra.Ring using (Ring; semiring)

------------------------------------------------------------------------
-- 1. The Field record.
--
-- Ring + non-triviality + multiplicative inverse for non-zero.
------------------------------------------------------------------------

record Field (A : Set) : Set where
  field
    ring : Ring A
    -- 0 ≠ 1
    0≢1 :
      ¬ (ε (+-monoid (semiring ring)) ≡ ε (*-monoid (semiring ring)))
    -- Multiplicative inverse for non-zero elements.
    mul-inv :
      (a : A) → ¬ (a ≡ ε (+-monoid (semiring ring))) → A
    -- Inverse law: a * (a⁻¹) ≡ 1 (for a ≠ 0).
    mul-inv-law :
      (a : A) (a≢0 : ¬ (a ≡ ε (+-monoid (semiring ring)))) →
      let _*_ = Magma._·_ (magma (semigroup (*-monoid (semiring ring))))
      in a * (mul-inv a a≢0) ≡ ε (*-monoid (semiring ring))

open Field public

------------------------------------------------------------------------
-- 2. Capstone for M8.
--
-- Field landed; the leaf of the algebra ladder. M9 instantiates
-- F₂; M10 instantiates ℚ.
------------------------------------------------------------------------
