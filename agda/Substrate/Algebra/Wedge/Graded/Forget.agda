------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Graded.Forget
--
-- The graded wedge's FORGETFUL read: evaluate the witness back to the
-- grade-(n+1) element. See dir README.
--
-- Defines: gforget
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Graded.Forget where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Wedge.Graded.DivStr
open import Substrate.Algebra.Wedge.Graded.Wedge

module _ {C : ℕ → Set} {R : ℕ → Set} where

  gforget : {G : GradedDivStr C R} {n : ℕ} {a : C (suc n)} {b : C n} →
            GradedWedge G n a b → C (suc n)
  gforget {G} {n} {b = b} w = recon G n b (rem w)
