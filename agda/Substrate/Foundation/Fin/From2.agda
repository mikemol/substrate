------------------------------------------------------------------------
-- Substrate.Foundation.Fin.From2
--
-- Defines: fromℕ<
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Fin; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.From2 where

open import Substrate.Foundation.Nat
  renaming (_<_ to _<ℕ_; _≤_ to _≤ℕ_)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Empty
open import Substrate.Foundation.Negation
open import Substrate.Foundation.Fin.Fin


fromℕ< : {m n : ℕ} → m <ℕ n → Fin n
fromℕ< {zero}  {suc _} _ = zero
fromℕ< {suc _} {suc _} (Substrate.Foundation.Nat.s≤s p) = suc (fromℕ< p)
