------------------------------------------------------------------------
-- Substrate.Algebra.CommutativeRing
--
-- A CommutativeRing is a Ring whose multiplication commutes. The one extra
-- law `*-comm` is exactly what the graded polynomial ring laws (`*P-comm`,
-- and hence `*P-assoc`) need from the coefficient ring — so `R[y]` and its
-- quotients are a free construction over any `CommutativeRing R`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CommutativeRing where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup; magma)
open import Substrate.Algebra.Monoid using (Monoid; semigroup)
open import Substrate.Algebra.Semiring using (Semiring; *-monoid)
open import Substrate.Algebra.Ring using (Ring; semiring)

record CommutativeRing (A : Set) : Set where
  field
    ring : Ring A
    *-comm :
      let _*_ = Magma._·_ (magma (semigroup (*-monoid (semiring ring))))
      in (a b : A) → a * b ≡ b * a

open CommutativeRing public
