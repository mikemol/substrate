------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.ApproxcanonicalEq
--
-- Defines: ≈⇒canonical-≡
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Quotient; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.ApproxcanonicalEq where

open import Agda.Primitive
open import Substrate.Algebra.Quotient.Quotient
open import Substrate.Algebra.Quotient.Canonical
open import Substrate.Foundation.Eq



≈⇒canonical-≡ :
  {ℓ r : Level} {A : Set ℓ} {_≈_ : A → A → Set r}
  {Q : Quotient A _≈_}
  (C : Canonical Q)
  {a b : A} →
  a ≈ b → canonical C a ≡ canonical C b
≈⇒canonical-≡ C = canonical-respects-≈ C
