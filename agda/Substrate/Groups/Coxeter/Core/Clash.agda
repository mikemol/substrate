------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.Clash
--
-- Section 7 of Coxeter.Core. The clash macro: lift Canonical-level
-- equality back to Word-level via canonical-is-fixed, then combine
-- with ≉ for ⊥-elim. Used by per-instance enumeration proofs.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ `Substrate.Foundation.Empty` and `.Eq` are CONSUMED PARENTS — both were split into
-- leaves, so the pre-split spelling of these imports is a `[FileNotFound]`. Restored from
-- HEAD, this file named the retired parents; the leaves are the live homes.
open import Substrate.Foundation.Empty.BotElim using (⊥-elim)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Eq.Neq using (_≢_)
open import Substrate.Foundation.Eq.Cong using (cong)
open import Substrate.Algebra.Quotient.Canonical

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
