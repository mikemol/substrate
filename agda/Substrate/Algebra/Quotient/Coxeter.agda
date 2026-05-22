------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.Coxeter
--
-- QU5 of the QU-arc per [scratch/qu_arc_plan.md].
--
-- Coxeter Word algebra → Quotient + Canonical instance.
--
-- The Coxeter Core's `_≈_` is defined as `w₁ ≈ w₂ = normalize w₁ ≡
-- normalize w₂`. This is exactly the "represents the same canonical
-- class" equivalence — a perfect fit for the substrate's Quotient
-- record. The Canonical extension's `canonical` is the Coxeter
-- Core's own `normalize`.
--
-- This module is parametric over the Coxeter Core's interface so
-- any concrete Coxeter instance (Z₃-Coxeter, V₄-Coxeter,
-- DirectProduct, ...) inherits a `Quotient + Canonical` witness
-- mechanically.
--
-- Per [[homology-cohomology-recursion]]: the Coxeter Word's
-- normalize IS the substrate's canonical-form-as-quotient instance
-- at the term-algebra level. QU2's UPArrow lifts it; this slice
-- attaches the witness.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)

module Substrate.Algebra.Quotient.Coxeter
  -- Coxeter Core's interface (same shape as ListPresentation's
  -- input to Core; see Substrate.Groups.Coxeter.Core).
  (Word : Set)
  (normalize : Word → Word)
  (normalize-idem :
    (w : Word) → normalize (normalize w) ≡ normalize w)
  where

open import Substrate.Algebra.Quotient using (Quotient; Canonical)

------------------------------------------------------------------------
-- 1. The Coxeter equivalence: w₁ ≈ w₂ iff normalize w₁ ≡ normalize w₂.
--
-- (Mirrors Substrate.Groups.Coxeter.Core._≈_'s definition.)
------------------------------------------------------------------------

_≈_ : Word → Word → Set
w₁ ≈ w₂ = normalize w₁ ≡ normalize w₂

------------------------------------------------------------------------
-- 2. Quotient instance.
------------------------------------------------------------------------

Coxeter-Quotient : Quotient Word _≈_
Coxeter-Quotient = record
  { ≈-refl  = λ _ → refl
  ; ≈-sym   = sym
  ; ≈-trans = trans
  }

------------------------------------------------------------------------
-- 3. Canonical extension via normalize.
------------------------------------------------------------------------

Coxeter-Canonical : Canonical Coxeter-Quotient
Coxeter-Canonical = record
  { canonical            = normalize
  ; canonical-idempotent = normalize-idem
  ; canonical-respects-≈ = λ ab → ab     -- _≈_ IS "normalize ≡ normalize"
  ; ≈-canonical          = λ a → sym (normalize-idem a)
  }

------------------------------------------------------------------------
-- 4. Capstone for QU5.
--
-- Coxeter Word's normalize lifted into the substrate's Quotient +
-- Canonical pair. Any Coxeter Core instance (Z₃, V₄, S₄, semidirect
-- products) now inherits a free Quotient witness.
------------------------------------------------------------------------
