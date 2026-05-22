------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.Projection
--
-- QU3 of the QU-arc per [scratch/qu_arc_plan.md].
--
-- The canonical projection q : A → A/~ in the substrate's HIT-free
-- encoding:
--
--   * Without a `Canonical Q` extension, "A/~" is just (A, _≈_),
--     and q is the identity. The structure is carried by demanding
--     downstream maps respect _≈_.
--
--   * With a `Canonical Q` extension, q : A → A is the canonical-
--     form function itself. This q satisfies:
--       q-respects-≈ : a ≈ b → q a ≡ q b      (canonical-respects-≈)
--       q-idempotent : q (q a) ≡ q a           (canonical-idempotent)
--       q-≈          : a ≈ q a                  (≈-canonical)
--
--   The second form is the computational projection — it picks a
--   distinguished representative per equivalence class.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.Projection where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Quotient
  using (Quotient; Canonical; canonical;
         canonical-idempotent; canonical-respects-≈; ≈-canonical)

------------------------------------------------------------------------
-- 1. Trivial projection: identity. Always available, regardless of
-- whether a Canonical extension exists.
--
-- This is the "name" the substrate gives to "the projection q : A → A/~"
-- when A/~ is encoded as (A, _≈_) with no canonical picker.
------------------------------------------------------------------------

trivial-projection : {A : Set} → A → A
trivial-projection a = a

trivial-projection-id :
  {A : Set} (a : A) → trivial-projection a ≡ a
trivial-projection-id _ = refl

------------------------------------------------------------------------
-- 2. Canonical projection: pick the canonical-form representative.
-- Requires a `Canonical Q` extension.
------------------------------------------------------------------------

canonical-projection :
  {A : Set} {_≈_ : A → A → Set} {Q : Quotient A _≈_}
  (C : Canonical Q) → A → A
canonical-projection C = canonical C

------------------------------------------------------------------------
-- 3. The three projection laws (re-export under projection-naming).
------------------------------------------------------------------------

q-respects-≈ :
  {A : Set} {_≈_ : A → A → Set} {Q : Quotient A _≈_}
  (C : Canonical Q) →
  {a b : A} → a ≈ b → canonical-projection C a ≡ canonical-projection C b
q-respects-≈ = canonical-respects-≈

q-idempotent :
  {A : Set} {_≈_ : A → A → Set} {Q : Quotient A _≈_}
  (C : Canonical Q) →
  (a : A) →
  canonical-projection C (canonical-projection C a)
    ≡ canonical-projection C a
q-idempotent = canonical-idempotent

q-≈ :
  {A : Set} {_≈_ : A → A → Set} {Q : Quotient A _≈_}
  (C : Canonical Q) →
  (a : A) → a ≈ canonical-projection C a
q-≈ = ≈-canonical

------------------------------------------------------------------------
-- 4. Capstone for QU3.
--
-- Two projection forms (trivial + canonical) with the three
-- substrate-native projection laws under the canonical form.
-- QU4 closes Phase A.
------------------------------------------------------------------------
