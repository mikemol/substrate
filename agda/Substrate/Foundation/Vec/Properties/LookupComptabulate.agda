------------------------------------------------------------------------
-- Substrate.Foundation.Vec.Properties.LookupComptabulate
--
-- Defines: lookup∘tabulate
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Vec.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Vec.Properties.LookupComptabulate where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Vec.Properties.Private



------------------------------------------------------------------------
-- tabulate / lookup round-trip lemmas.
--
-- lookup∘tabulate : lookup (tabulate f) i ≡ f i
-- tabulate∘lookup : tabulate (lookup xs) ≡ xs
------------------------------------------------------------------------

lookup∘tabulate :
  {A : Set ℓ} {n : ℕ}
  (f : Fin n → A) (i : Fin n) →
  lookup (tabulate f) i ≡ f i
lookup∘tabulate {n = suc _} f zero    = refl
lookup∘tabulate {n = suc _} f (fsuc i) = lookup∘tabulate (λ j → f (fsuc j)) i
