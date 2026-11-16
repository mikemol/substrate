------------------------------------------------------------------------
-- Substrate.Foundation.Vec.Properties.TabulateComplookup
--
-- Defines: tabulate∘lookup
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Vec.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Vec.Properties.TabulateComplookup where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Vec.Properties.Private



tabulate∘lookup :
  {A : Set ℓ} {n : ℕ}
  (xs : Vec A n) → tabulate (lookup xs) ≡ xs
tabulate∘lookup []       = refl
tabulate∘lookup (x ∷ xs) = cong (x ∷_) (tabulate∘lookup xs)
