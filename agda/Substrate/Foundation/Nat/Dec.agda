------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Dec
--
-- Defines: _≟_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Dec where

open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.DecNot
open import Substrate.Foundation.Negation.FromNotNot
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Negation.Preamble
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.SucInjective



_≟_ : (m n : ℕ) → Dec (m ≡ n)
zero  ≟ zero  = yes refl
zero  ≟ suc _ = no λ ()
suc _ ≟ zero  = no λ ()
suc m ≟ suc n with m ≟ n
... | yes p = yes (cong suc p)
... | no  q = no λ eq → q (suc-injective eq)
