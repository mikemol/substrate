------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Op2
--
-- Defines: _<_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Fin; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Op2 where

open import Substrate.Foundation.Nat using (ℕ; zero; suc) renaming (_<_ to _<ℕ_; _≤_ to _≤ℕ_)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Empty
open import Substrate.Foundation.Negation
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To


------------------------------------------------------------------------
-- Order on Fin: lift from ℕ via toℕ.
------------------------------------------------------------------------

_<_ : {n : ℕ} → Fin n → Fin n → Set
i < j = toℕ i <ℕ toℕ j
