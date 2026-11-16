------------------------------------------------------------------------
-- Substrate.Foundation.Vec.Properties.TabulateCong
--
-- Defines: tabulate-cong
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Vec.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Vec.Properties.TabulateCong where

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
-- tabulate-cong + vec-ext: pointwise equality ⟹ vector equality.
--
-- The generic Vec extensionality, derived from the two round-trips
-- above (no funext, no K): if two vectors agree at every index they
-- are equal. Subsumes F₂'s ≡-from-lookup at any element type, so it
-- serves both the row level (Vec of rows) and the entry level.
------------------------------------------------------------------------

tabulate-cong :
  {A : Set ℓ} {n : ℕ}
  (f g : Fin n → A) → ((i : Fin n) → f i ≡ g i) → tabulate f ≡ tabulate g
tabulate-cong {n = zero}  f g p = refl
tabulate-cong {n = suc _} f g p =
  cong₂ _∷_ (p fzero) (tabulate-cong (λ i → f (fsuc i)) (λ i → g (fsuc i)) (λ i → p (fsuc i)))
