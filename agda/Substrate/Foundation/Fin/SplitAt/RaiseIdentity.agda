------------------------------------------------------------------------
-- Substrate.Foundation.Fin.SplitAt.RaiseIdentity
--
-- splitAt-raise : splitAt a (raise a i) ≡ inj₂ i.
-- Raising past a yields the "right" partition; splitting recovers it.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.SplitAt.RaiseIdentity where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Raise
open import Substrate.Foundation.Fin.SplitAt
open import Substrate.Foundation.Sum.Sum
open import Substrate.Foundation.Fin.Raise using (raise)
open import Substrate.Foundation.Fin.SplitAt using (splitAt)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong

splitAt-raise :
  ∀ a {b} (i : Fin b) → splitAt a {b} (raise a i) ≡ inj₂ i
splitAt-raise zero    i = refl
splitAt-raise (suc a) i with splitAt a (raise a i) | splitAt-raise a i
... | inj₂ _ | refl = refl
