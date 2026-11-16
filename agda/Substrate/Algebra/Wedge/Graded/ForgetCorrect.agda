------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Graded.ForgetCorrect
--
-- gforget recovers the original grade-(n+1) element. See dir README.
--
-- Defines: gforget-correct
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Graded.ForgetCorrect where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Wedge.Graded.DivStr
open import Substrate.Algebra.Wedge.Graded.Wedge
open import Substrate.Algebra.Wedge.Graded.Forget
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym

module _ {C : ℕ → Set} {R : ℕ → Set} where

  gforget-correct : {G : GradedDivStr C R} {n : ℕ} {a : C (suc n)} {b : C n}
                    (w : GradedWedge G n a b) → gforget w ≡ a
  gforget-correct w = sym (wedge-eq w)
