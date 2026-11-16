------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.Canonical
--
-- Defines: Canonical
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Quotient; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.Canonical where

open import Agda.Primitive
open import Substrate.Algebra.Quotient.Quotient
open import Substrate.Foundation.Eq




------------------------------------------------------------------------
-- 2. The Canonical extension.
--
-- Many substrate quotients additionally provide a canonical-form
-- function. This extension witnesses that data + its three laws
-- (idempotence, respect of _≈_, soundness).
--
-- When a `Canonical Q` is in scope, we additionally have:
--   canonical-≡⇒≈ : canonical a ≡ canonical b → a ≈ b
--   ≈⇒canonical-≡ : a ≈ b → canonical a ≡ canonical b
-- giving "represents the same class" via propositional equality on
-- canonical representatives.
------------------------------------------------------------------------

record Canonical      -- ⟦shape:de760d07 {a r,canonical,canonical-idempotent⟧
  {a r : Level} {A : Set a} {_≈_ : A → A → Set r} (Q : Quotient A _≈_) : Set (a ⊔ r) where
  field
    canonical            : A → A
    canonical-idempotent : (a : A) → canonical (canonical a) ≡ canonical a
    canonical-respects-≈ : {a b : A} → a ≈ b → canonical a ≡ canonical b
    ≈-canonical          : (a : A) → a ≈ canonical a

open Canonical public
