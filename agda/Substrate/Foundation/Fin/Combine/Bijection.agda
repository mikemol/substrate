------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Combine.Bijection
--
-- *↔× : Fin (m * n) ↔ (Fin m × Fin n).
-- Substrate-native replacement for stdlib's Data.Fin.Properties.*↔×.
-- to    = remQuot
-- from  = uncurry combine
-- round-trips via Combine/CombineRemQuotInverse + Combine/RemQuotInverse.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Combine.Bijection where

open import Substrate.Foundation.Nat using (ℕ; _*_)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Algebra.Bijection using (_↔_; mk↔ₛ′)
open import Substrate.Foundation.Fin.Combine using (combine)
open import Substrate.Foundation.Fin.RemQuot using (remQuot)
open import Substrate.Foundation.Fin.Combine.RemQuotInverse using (remQuot-combine)
open import Substrate.Foundation.Fin.Combine.CombineRemQuotInverse using (combine-remQuot)

*↔× : ∀ {m n} → Fin (m * n) ↔ (Fin m × Fin n)
*↔× {m} {n} = mk↔ₛ′
  (remQuot n)
  (λ p → combine (proj₁ p) (proj₂ p))
  (λ p → remQuot-combine (proj₁ p) (proj₂ p))
  (combine-remQuot m n)
