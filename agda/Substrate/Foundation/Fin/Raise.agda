------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Raise
--
-- raise n : Fin k → Fin (n + k).
-- Shift a Fin k up by n positions, embedding into Fin (n + k).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Raise where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Fin using (Fin; suc)

raise : ∀ n {k} → Fin k → Fin (n + k)
raise zero    i = i
raise (suc n) i = suc (raise n i)
