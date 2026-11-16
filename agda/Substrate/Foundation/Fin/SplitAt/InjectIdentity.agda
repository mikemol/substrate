------------------------------------------------------------------------
-- Substrate.Foundation.Fin.SplitAt.InjectIdentity
--
-- splitAt-inject : splitAt a (inject+ k j) ≡ inj₁ j.
-- Inject+ stays in the "left" partition; splitting recovers it.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.SplitAt.InjectIdentity where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Inject
open import Substrate.Foundation.Fin.SplitAt
open import Substrate.Foundation.Sum.Sum
open import Substrate.Foundation.Fin.Inject using (inject+)
open import Substrate.Foundation.Fin.SplitAt using (splitAt)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong

splitAt-inject :
  ∀ a {k} (j : Fin a) → splitAt a {k} (inject+ k j) ≡ inj₁ j
splitAt-inject (suc a) zero     = refl
splitAt-inject (suc a) {k} (suc j) with splitAt a {k} (inject+ k j)
                                      | splitAt-inject a {k} j
... | inj₁ _ | refl = refl
