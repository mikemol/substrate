------------------------------------------------------------------------
-- Substrate.Algebra.Quotient
--
-- QU1 of the QU-arc per [scratch/qu_arc_plan.md].
--
-- A `Quotient A _≈_` packages the bare equivalence-relation data on
-- a carrier A: refl, sym, trans. This is the substrate-native
-- presentation of A modulo _≈_ at its minimal commitment, suitable
-- for use as the base of QU2's UPArrow.
--
-- The substrate's quotient instances factor into two layers:
--
--   * `Quotient A _≈_`  — bare equivalence; the UP-arrow's input.
--     Surreals fit here (≈ⁿ on SurrealFinite n).
--
--   * `Canonical Q`      — extension witness when A has a
--     canonical-form function `canonical : A → A` (terminating,
--     idempotent, ≈-respecting). Coxeter Word `normalize`, ℚ gcd-
--     reduction, V4-Cosets `s-for-anchor X`, F₂ parity all live here.
--
-- The split is per [[feedback-use-vs-commit]]: the UP USES the
-- equivalence; specific instances may commit additionally to a
-- canonical-form picker, which gives decidability / normalisation
-- but is not necessary for the universal property. Per the
-- user's framing (2026-05-21): the term-algebra alignment with
-- surreals is preserved because Quotient's carrier is whatever
-- inductive type the instance provides; surreals' `⟨L ∣ R⟩` over
-- Coxeter Word IS that carrier.
--
-- Per [[project-agda-cubical-extraction-discipline]]: no HITs;
-- the quotient is encoded via (carrier, equivalence) rather than
-- a set-of-classes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient where

open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym)
open import Agda.Primitive using (Level; lzero; lsuc; _⊔_)

------------------------------------------------------------------------
-- 1. The base Quotient record: an equivalence relation, nothing more.
--
-- Surreals attach here directly via `_≈ⁿ_` from
-- Substrate.Conway.Equivalence.
------------------------------------------------------------------------

record Quotient {a r : Level} (A : Set a) (_≈_ : A → A → Set r) : Set (a ⊔ r) where
  field
    ≈-refl  : (a : A) → a ≈ a
    ≈-sym   : {a b : A} → a ≈ b → b ≈ a
    ≈-trans : {a b c : A} → a ≈ b → b ≈ c → a ≈ c

open Quotient public

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

≈⇒canonical-≡ :
  {ℓ r : Level} {A : Set ℓ} {_≈_ : A → A → Set r}
  {Q : Quotient A _≈_}
  (C : Canonical Q)
  {a b : A} →
  a ≈ b → canonical C a ≡ canonical C b
≈⇒canonical-≡ C = canonical-respects-≈ C

------------------------------------------------------------------------
-- 4. Capstone for QU1.
--
-- Quotient + Canonical landed. QU2 lifts the base Quotient into a
-- UPArrow; surreals attach (Canonical-free) at QU7, and the other
-- four substrate instances attach with a Canonical witness at QU5,
-- QU6, QU8, QU9.
------------------------------------------------------------------------
