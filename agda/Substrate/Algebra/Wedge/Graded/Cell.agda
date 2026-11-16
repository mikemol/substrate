------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Graded.Cell
--
-- The graded wedge's PRESENTED read: keep the remainder = the cell = the
-- grade-n digit. See dir README.
--
-- Defines: gcell
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Graded.Cell where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Wedge.Graded.DivStr
open import Substrate.Algebra.Wedge.Graded.Wedge

module _ {C : ℕ → Set} {R : ℕ → Set} where

  gcell : {G : GradedDivStr C R} {n : ℕ} {a : C (suc n)} {b : C n} →
          GradedWedge G n a b → R n
  gcell w = rem w
