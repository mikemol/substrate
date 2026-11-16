------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Raise
--
-- raise n : Fin k → Fin (n ℕ+ k).
-- Shift a Fin k up by n positions, embedding into Fin (n ℕ+ k).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Raise where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Fin.Fin

raise : ∀ n {k} → Fin k → Fin (n ℕ+ k)
raise zero    i = i
raise (suc n) i = suc (raise n i)
