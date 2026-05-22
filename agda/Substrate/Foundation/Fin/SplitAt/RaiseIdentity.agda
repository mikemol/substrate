------------------------------------------------------------------------
-- Substrate.Foundation.Fin.SplitAt.RaiseIdentity
--
-- splitAt-raise : splitAt a (raise a i) ≡ inj₂ i.
-- Raising past a yields the "right" partition; splitting recovers it.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.SplitAt.RaiseIdentity where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Sum using (_⊎_; inj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Fin.Raise using (raise)
open import Substrate.Foundation.Fin.SplitAt using (splitAt)

splitAt-raise :
  ∀ a {b} (i : Fin b) → splitAt a {b} (raise a i) ≡ inj₂ i
splitAt-raise zero    i = refl
splitAt-raise (suc a) i with splitAt a (raise a i) | splitAt-raise a i
... | inj₂ _ | refl = refl
