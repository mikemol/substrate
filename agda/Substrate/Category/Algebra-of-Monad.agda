------------------------------------------------------------------------
-- Substrate.Category.Algebra-of-Monad
--
-- R3 of the R-arc. T-algebra: pair (A, α : T(A) → A) satisfying unit
-- + multiplication compatibility (= the Eilenberg-Moore object).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Algebra-of-Monad where

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)
open import Substrate.Category.Monad using (Monad)

record AlgebraOfMonad
  {ℓO ℓM : Level}
  {Obj : Set ℓO} {Mor : Obj → Obj → Set ℓM}
  (C : CategoryOf Obj Mor)
  (M : Monad C) : Set (ℓO ⊔ ℓM) where
  field
    A : Obj
    α : Mor (Functor.F-obj (Monad.T M) A) A
  -- Unit + multiplication compatibility: user obligations.
