------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Le2
--
-- Defines: _≤?_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Le2 where

open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.DecNot
open import Substrate.Foundation.Negation.FromNotNot
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Negation.Preamble
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.SLesInjective



_≤?_ : (m n : ℕ) → Dec (m ≤ n)
zero  ≤? _     = yes z≤n
suc _ ≤? zero  = no λ ()
suc m ≤? suc n with m ≤? n
... | yes p = yes (s≤s p)
... | no  q = no λ le → q (s≤s-injective le)
