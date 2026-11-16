------------------------------------------------------------------------
-- Substrate.Foundation.Fin.From2
--
-- Defines: fromℕ<
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Fin; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.From2 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Fin.Fin


fromℕ< : {m n : ℕ} → m < n → Fin n
fromℕ< {zero}  {suc _} _ = zero
fromℕ< {suc _} {suc _} (s≤s p) = suc (fromℕ< p)
