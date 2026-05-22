------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Inject
--
-- inject+ : ∀ {n} k → Fin n → Fin (n + k).
-- Embed a Fin n into Fin (n + k) by keeping the underlying numeric
-- value. The "extra" k slots at the high end are unreachable from
-- inject+'s image.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Inject where

open import Substrate.Foundation.Nat using (ℕ; _+_)
open import Substrate.Foundation.Fin using (Fin; zero; suc)

inject+ : ∀ {n} k → Fin n → Fin (n + k)
inject+ _ zero    = zero
inject+ k (suc i) = suc (inject+ k i)
