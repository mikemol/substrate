------------------------------------------------------------------------
-- Substrate.Algebra.Nat.WellFounded.AccSuc
--
-- Defines: acc-suc
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.WellFounded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.WellFounded.AccSuc where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.WellFounded
open import Substrate.Algebra.Nat.WellFounded.Private


acc-suc : ∀ {n} → Acc _<_ n → Acc _<_ (suc n)
acc-suc {n} acc-n = acc step
  where
    step : ∀ y → y < suc n → Acc _<_ y
    step y (s≤s y≤n) = down acc-n y≤n
      where
        down : ∀ {m} → Acc _<_ m → ∀ {k} → k ≤ m → Acc _<_ k
        down (acc rec) z≤n      = acc (λ _ ())
        down (acc rec) (s≤s p)  = acc (λ z z<sk → down (rec _ (s≤s p)) (≤-pred z<sk))
          where
            ≤-pred : ∀ {a b} → suc a ≤ suc b → a ≤ b
            ≤-pred (s≤s q) = q
