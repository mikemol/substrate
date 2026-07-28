------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Op
--
-- Defines: _≟_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Fin; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Op where

open import Substrate.Foundation.Nat using (ℕ; zero; suc) renaming (_<_ to _<ℕ_; _≤_ to _≤ℕ_)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Empty
open import Substrate.Foundation.Negation
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Sucinjective


_≟_ : {n : ℕ} (i j : Fin n) → Dec (i ≡ j)
zero  ≟ zero  = yes refl
zero  ≟ suc _ = no λ ()
suc _ ≟ zero  = no λ ()
suc i ≟ suc j with i ≟ j
... | yes p = yes (cong suc p)
... | no  q = no λ eq → q (fin-suc-injective eq)
