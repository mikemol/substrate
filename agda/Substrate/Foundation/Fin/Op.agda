------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Op
--
-- Defines: _≟ᶠ_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Fin; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Op where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.DecNot
open import Substrate.Foundation.Negation.FromNotNot
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Negation.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Sucinjective
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong


_≟ᶠ_ : {n : ℕ} (i j : Fin n) → Dec (i ≡ j)
zero  ≟ᶠ zero  = yes refl
zero  ≟ᶠ suc _ = no λ ()
suc _ ≟ᶠ zero  = no λ ()
suc i ≟ᶠ suc j with i ≟ᶠ j
... | yes p = yes (cong suc p)
... | no  q = no λ eq → q (fin-suc-injective eq)
