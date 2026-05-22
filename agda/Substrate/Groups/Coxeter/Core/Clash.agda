------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.Clash
--
-- Section 7 of Coxeter.Core. The clash macro: lift Canonical-level
-- equality back to Word-level via canonical-is-fixed, then combine
-- with ≉ for ⊥-elim. Used by per-instance enumeration proofs.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Eq    using (_≡_; _≢_; cong)

module Substrate.Groups.Coxeter.Core.Clash
  (Word : Set)
  (Canonical : Word → Set)
  (normalize : Word → Word)
  where

private
  _≉_ : Word → Word → Set
  w₁ ≉ w₂ = normalize w₁ ≢ normalize w₂

clash : {w₁ w₂ : Word} → Canonical w₁ → Canonical w₂ →
        w₁ ≉ w₂ → w₁ ≡ w₂ → ∀ {A : Set} → A
clash _ _ neq eq = ⊥-elim (neq (cong normalize eq))
