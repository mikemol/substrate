------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Combine
--
-- combine : Fin m → Fin n → Fin (m * n).
-- Packs a pair of Fins into a single flat index (row-major).
-- The natural-number interpretation is `toℕ i * n + toℕ j`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Combine where

open import Substrate.Foundation.Nat using (ℕ; suc; _*_)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Inject using (inject+)
open import Substrate.Foundation.Fin.Raise using (raise)

combine : ∀ {m n} → Fin m → Fin n → Fin (m * n)
combine {suc m} {n} zero    j = inject+ (m * n) j
combine {suc m} {n} (suc i) j = raise n (combine i j)
