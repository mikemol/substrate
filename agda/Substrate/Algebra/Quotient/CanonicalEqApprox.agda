------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.CanonicalEqApprox
--
-- Defines: canonical-≡⇒≈
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Quotient; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.CanonicalEqApprox where

open import Agda.Primitive
open import Substrate.Algebra.Quotient.Quotient
open import Substrate.Algebra.Quotient.Canonical
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym




------------------------------------------------------------------------
-- 3. Derived characterisations under a Canonical extension.
------------------------------------------------------------------------

canonical-≡⇒≈ :
  {ℓ r : Level} {A : Set ℓ} {_≈_ : A → A → Set r}
  {Q : Quotient A _≈_}
  (C : Canonical Q)
  (a b : A) →
  canonical C a ≡ canonical C b → a ≈ b
canonical-≡⇒≈ {_≈_ = _≈_} {Q = Q} C a b eq = ≈-trans Q step₁ step₂
  where
    step₁ : a ≈ canonical C b
    step₁ rewrite sym eq = ≈-canonical C a

    step₂ : canonical C b ≈ b
    step₂ = ≈-sym Q (≈-canonical C b)
