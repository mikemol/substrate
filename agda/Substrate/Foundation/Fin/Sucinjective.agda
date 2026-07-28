------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Sucinjective
--
-- Defines: fin-suc-injective
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Fin; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Sucinjective where

open import Substrate.Foundation.Nat
  renaming (_<_ to _<ℕ_; _≤_ to _≤ℕ_)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Empty
open import Substrate.Foundation.Negation
open import Substrate.Foundation.Fin.Fin


------------------------------------------------------------------------
-- Decidable equality on Fin.
------------------------------------------------------------------------

fin-suc-injective : {n : ℕ} {i j : Fin n} → (Fin.suc i) ≡ suc j → i ≡ j
fin-suc-injective refl = refl
