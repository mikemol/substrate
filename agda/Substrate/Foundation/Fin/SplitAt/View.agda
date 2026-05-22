------------------------------------------------------------------------
-- Substrate.Foundation.Fin.SplitAt.View
--
-- SplitAtView a k : structural witness that any k : Fin (a + b)
-- is either inject+ b j (for some j : Fin a) or raise a i (for some
-- i : Fin b). Lets the consumer destructure k by its partition.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.SplitAt.View where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Inject using (inject+)
open import Substrate.Foundation.Fin.Raise using (raise)

data SplitAtView (a : ℕ) {b : ℕ} : Fin (a + b) → Set where
  fromₗ : (j : Fin a) → SplitAtView a {b} (inject+ b j)
  fromᵣ : (i : Fin b) → SplitAtView a {b} (raise a i)

splitAt-view : ∀ a {b} (k : Fin (a + b)) → SplitAtView a {b} k
splitAt-view zero        k    = fromᵣ k
splitAt-view (suc a)    zero  = fromₗ zero
splitAt-view (suc a) (suc i) with splitAt-view a i
... | fromₗ j  = fromₗ (suc j)
... | fromᵣ i' = fromᵣ i'
