------------------------------------------------------------------------
-- Substrate.Algebra.Nat.WellFounded
--
-- Well-foundedness of strict less-than on ℕ.
--
--   <-wellFounded : (n : ℕ) → Acc _<_ n
--
-- Standard proof: induct on n, peeling one suc per step. At each step
-- we use the helper `acc-suc` that extends an Acc-witness for n to
-- one for suc n by case-analysing the incoming `y < suc n` proof.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.WellFounded where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_; _≤_; s≤s; z≤n)
open import Substrate.Foundation.WellFounded using (Acc; acc; WellFounded)

private
  -- Helper: extend an Acc for n to an Acc for suc n by induction on
  -- the incoming y < suc n proof.
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

<-wellFounded : WellFounded _<_
<-wellFounded zero    = acc (λ _ ())
<-wellFounded (suc n) = acc-suc (<-wellFounded n)
