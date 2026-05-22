------------------------------------------------------------------------
-- Substrate.Foundation.Fin.RemQuot
--
-- remQuot : ∀ n → Fin (m * n) → Fin m × Fin n.
-- Unpack a flat Fin (m * n) into (quotient, remainder) — the inverse
-- of `combine`. Inducts on m: at each step, splitAt at n peels off
-- the first row.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.RemQuot where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Sum using (inj₁; inj₂)
open import Substrate.Foundation.Fin.SplitAt using (splitAt)

remQuot : ∀ {m} n → Fin (m * n) → Fin m × Fin n
remQuot {suc m} n i with splitAt n {m * n} i
... | inj₁ j  = zero , j
... | inj₂ i' with remQuot {m} n i'
... | (q , r) = suc q , r
