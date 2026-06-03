------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Quotient
--
-- QU2 of the QU-arc per [scratch/qu_arc_plan.md].
--
-- Lifts `Substrate.Algebra.Quotient` into a universal-property
-- record `QuotientUP` and registers it as a `UPArrow` in the
-- UP-topos catalogue.
--
-- THE UNIVERSAL PROPERTY (statement-bearing):
--
--   Given a `Quotient A _≈_` Q and a function f : A → B that
--   respects _≈_  (i.e., ∀ {a b} → a ≈ b → f a ≡ f b), there
--   exists a unique f̃ : A → B such that f̃ a ≡ f a for every a,
--   AND f̃ depends only on the equivalence class of a (i.e., f̃
--   also respects _≈_).
--
-- Substrate-honest scope per [[project-agda-cubical-extraction-
-- discipline]]: A/~ is NOT introduced as a new HIT'd carrier; the
-- factorisation lives at the level of `respecting maps out of A`,
-- which is structurally equivalent in the absence of HITs. When a
-- `Canonical Q` extension is in scope (Coxeter, ℚ, V4-Cosets, F₂),
-- factorisation IS computational: f̃ a = f (canonical a). Without
-- canonical (surreals), the factorisation is the original f itself
-- viewed as a respecting map.
--
-- Per [[homology-cohomology-recursion]]: this slice lifts the
-- "quotient construction" pattern from instance-level data into
-- the internal-structure level (cohomology), making CRT and EEA
-- statable as UPArrow morphisms in subsequent QU-arc phases.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Quotient where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Unit using (⊤; tt)

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Algebra.Nat.Mod using (_mod-suc_)
open import Substrate.Algebra.Quotient using (Quotient; ≈-refl; ≈-sym; ≈-trans)
open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.UniversalProperty.Vacuity using (Contentful)

------------------------------------------------------------------------
-- 1. Respecting maps.
--
-- A function `f : A → B` *respects* `_≈_` when ≈-related inputs
-- produce equal outputs. This is the substrate's analogue of
-- "well-defined on equivalence classes".
------------------------------------------------------------------------

Respects :
  {A B : Set} (_≈_ : A → A → Set) (f : A → B) → Set
Respects {A} _≈_ f = {a b : A} → a ≈ b → f a ≡ f b

------------------------------------------------------------------------
-- 2. The QuotientUP record.
--
-- Bundles the universal-property data:
--   * the quotient (carrier A, equivalence _≈_, Q)
--   * for any (B, f : A → B, f-respects-≈):
--       a factor map  f̃ : A → B
--       the factor agrees with f on all inputs
--       the factor respects _≈_
--       uniqueness: any other respecting factor agrees with f̃
------------------------------------------------------------------------

record QuotientUP
  (A : Set) (_≈_ : A → A → Set) (Q : Quotient A _≈_) : Set₁ where
  field
    factor :
      (B : Set) (f : A → B) (f-resp : Respects _≈_ f) → A → B

    factor-≡-f :
      (B : Set) (f : A → B) (f-resp : Respects _≈_ f) →
      (a : A) → factor B f f-resp a ≡ f a

    factor-respects :
      (B : Set) (f : A → B) (f-resp : Respects _≈_ f) →
      Respects _≈_ (factor B f f-resp)

    factor-unique :
      (B : Set) (f : A → B) (f-resp : Respects _≈_ f) →
      (g : A → B) (g-resp : Respects _≈_ g) →
      ((a : A) → g a ≡ f a) →
      (a : A) → g a ≡ factor B f f-resp a

open QuotientUP public

------------------------------------------------------------------------
-- 3. The trivial witness.
--
-- For any quotient, the identity-factorisation IS the universal
-- factorisation: `factor f = f` whenever f respects _≈_. This
-- discharges the QuotientUP for any Quotient instance with no
-- additional structure required, and is the substrate's
-- HIT-free encoding of the UP.
------------------------------------------------------------------------

trivial-QuotientUP :
  {A : Set} {_≈_ : A → A → Set} (Q : Quotient A _≈_) →
  QuotientUP A _≈_ Q
trivial-QuotientUP {A} {_≈_} Q = record
  { factor           = λ _ f _ → f
  ; factor-≡-f       = λ _ _ _ _ → refl
  ; factor-respects  = λ _ _ f-resp → f-resp
  ; factor-unique    = λ _ _ _ _ _ g≡f a → g≡f a
  }

------------------------------------------------------------------------
-- 4. UPArrow registration.
--
-- Per the UP8 (Instances) pattern: register the quotient as a
-- catalogue entry under `Quotient-UPArrow`. The Spec / Inst / Witness
-- positions are signature-bearing (⊤-padded); the full structural
-- record is `QuotientUP` above, used directly by downstream slices.
------------------------------------------------------------------------

-- VACUITY-AUDIT REPAIR (2026-06-03): was a ⊤-collapse placeholder. Wired to
-- a real Contentful quotient — the quotient map ℕ ↠ ℤ/3: an element is
-- "solved" by any representative identified with it (≡ mod 3). The structural
-- QuotientUP record above is the general statement; this is its UPArrow-level
-- catalogue entry, now content-bearing (1 is not identified with 0).
Quotient-UPArrow : UPArrow
Quotient-UPArrow = record
  { Source  = ℕ   -- "an element to be classified"
  ; Target  = ℕ   -- "a representative of its class"
  ; Witness = λ a x → x mod-suc 2 ≡ a mod-suc 2   -- "x and a are identified by ℕ ↠ ℤ/3"
  }

Quotient-contentful : Contentful Quotient-UPArrow
Quotient-contentful = 1 , 0 , λ ()

------------------------------------------------------------------------
-- 5. Capstone for QU2.
--
-- QuotientUP record landed + trivial witness + UPArrow registration.
-- QU3 derives the canonical projection q : A → A/~ (the
-- factor-respecting form of `id` viewed through the quotient lens);
-- QU4 closes Phase A.
------------------------------------------------------------------------
