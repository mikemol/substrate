------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Graded.Wedge
--
-- The graded wedge: a grade-(n+1) element a, decomposed against a base b
-- at grade n by a remainder rem, with witness a ≡ recon n b rem. (C R
-- inferred implicitly from the GradedDivStr argument.) See dir README.
--
-- Defines: GradedWedge
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Graded.Wedge where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Wedge.Graded.DivStr
open import Substrate.Foundation.Eq

module _ {C : ℕ → Set} {R : ℕ → Set} where

  record GradedWedge (G : GradedDivStr C R) (n : ℕ)
                     (a : C (suc n)) (b : C n) : Set where
    field
      rem      : R n
      wedge-eq : a ≡ recon G n b rem

  open GradedWedge public
