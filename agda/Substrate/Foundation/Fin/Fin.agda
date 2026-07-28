------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Fin
--
-- Defines: Fin
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Fin; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Fin where

open import Substrate.Foundation.Nat
  renaming (_<_ to _<ℕ_; _≤_ to _≤ℕ_)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Empty
open import Substrate.Foundation.Negation


------------------------------------------------------------------------
-- The Fin datatype.
------------------------------------------------------------------------

data Fin : ℕ → Set where
  zero : {n : ℕ} → Fin (suc n)
  suc  : {n : ℕ} → Fin n → Fin (suc n)

-- ⟡public-policy: unambiguous names provided AT SOURCE, so a consumer never
-- needs `renaming (zero to fzero)` to tell Fin's constructors from Nat's.
pattern fzero  = zero
pattern fsuc x = suc x
