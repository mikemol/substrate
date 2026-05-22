------------------------------------------------------------------------
-- Substrate.Foundation.WellFounded
--
-- Substrate-native universe-polymorphic well-founded recursion via Acc.
--
-- A relation _<_ is well-founded if every element is accessible:
-- it has no infinite descending chains. Operationally: every
-- well-founded recursion can be unfolded structurally on Acc, which
-- terminates because Acc's constructor takes a function that
-- recursively produces Acc for strictly smaller elements.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.WellFounded where

open import Substrate.Foundation.Level using (Level; _⊔_)

private
  variable
    ℓ ℓ′ : Level

------------------------------------------------------------------------
-- Acc R x : x is accessible under R.
--
-- The single constructor `acc` takes a function: for every y with
-- y R x (strictly smaller), provide Acc R y. By induction on this
-- chain, any function recursing through Acc terminates.
------------------------------------------------------------------------

data Acc {A : Set ℓ} (R : A → A → Set ℓ′) (x : A) : Set (ℓ ⊔ ℓ′) where
  acc : (∀ y → R y x → Acc R y) → Acc R x

------------------------------------------------------------------------
-- WellFounded R : every element is accessible under R.
------------------------------------------------------------------------

WellFounded : {A : Set ℓ} → (A → A → Set ℓ′) → Set (ℓ ⊔ ℓ′)
WellFounded {A = A} R = (x : A) → Acc R x
