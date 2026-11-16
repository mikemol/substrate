------------------------------------------------------------------------
-- Substrate.WitnessTower.Enumerate.LengthL
--
-- Defines: lengthL
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Enumerate; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Enumerate.LengthL where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.List



lengthL : ∀ {a} {A : Set a} → List A → ℕ
lengthL []       = zero
lengthL (x ∷ xs) = suc (lengthL xs)
