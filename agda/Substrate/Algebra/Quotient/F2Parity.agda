------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.F2Parity
--
-- QU6 of the QU-arc per [scratch/qu_arc_plan.md].
--
-- ℕ / parity ≅ F₂ as a Quotient + Canonical instance.
--
-- Equivalence: m ≈ n iff parity m ≡ parity n. Canonical-form:
-- pick 0 (if parity = 𝟘) or 1 (if parity = 𝟙). These are the
-- canonical representatives of the two equivalence classes.
--
-- Per the substrate's [[3+1-parity-universal]]: parity ℕ → F₂ is
-- a universal F₂-grading. This slice makes it a Quotient instance
-- so downstream code (e.g., F₂-graded structures) gets the UP for
-- free.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.F2Parity where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙)
open import Substrate.Algebra.N-to-F2-Parity using (parity)

open import Substrate.Algebra.Quotient using (Quotient; Canonical)

------------------------------------------------------------------------
-- 1. The parity equivalence on ℕ.
------------------------------------------------------------------------

infix 4 _≈ₚ_

_≈ₚ_ : ℕ → ℕ → Set
m ≈ₚ n = parity m ≡ parity n

------------------------------------------------------------------------
-- 2. Canonical representative.
--
-- Factor through F₂: `canonical-rep` maps each F₂ element to the
-- chosen ℕ representative (𝟘 ↦ 0, 𝟙 ↦ 1). The full canonical-form
-- function on ℕ is the composite `canonical-rep ∘ parity`.
-- Splitting via a helper keeps Agda's reduction transparent in the
-- idempotence and respect proofs below.
------------------------------------------------------------------------

canonical-rep : F₂ → ℕ
canonical-rep 𝟘 = 0
canonical-rep 𝟙 = 1

canonical-parity : ℕ → ℕ
canonical-parity n = canonical-rep (parity n)

------------------------------------------------------------------------
-- 3. Canonical-form laws.
------------------------------------------------------------------------

private
  -- The two named ℕ representatives have known parity.
  parity-0 : parity 0 ≡ 𝟘
  parity-0 = refl

  parity-1 : parity 1 ≡ 𝟙
  parity-1 = refl

  -- parity (canonical-rep x) ≡ x. Case split on x.
  parity-canonical-rep : (x : F₂) → parity (canonical-rep x) ≡ x
  parity-canonical-rep 𝟘 = parity-0
  parity-canonical-rep 𝟙 = parity-1

  -- canonical-parity is idempotent: parity (canonical-parity n)
  -- ≡ parity n, and applying canonical-rep to the same value
  -- twice gives the same result.
  canonical-parity-idem :
    (n : ℕ) → canonical-parity (canonical-parity n) ≡ canonical-parity n
  canonical-parity-idem n =
    cong canonical-rep (parity-canonical-rep (parity n))

  -- m ≈ₚ n means parity m ≡ parity n. Apply canonical-rep to both
  -- sides.
  canonical-parity-respects :
    {m n : ℕ} → m ≈ₚ n → canonical-parity m ≡ canonical-parity n
  canonical-parity-respects eq = cong canonical-rep eq

  -- parity n ≡ parity (canonical-parity n) by sym of
  -- parity-canonical-rep.
  ≈ₚ-canonical : (n : ℕ) → n ≈ₚ canonical-parity n
  ≈ₚ-canonical n = sym (parity-canonical-rep (parity n))

------------------------------------------------------------------------
-- 4. Quotient + Canonical instance.
------------------------------------------------------------------------

ℕ/parity-Quotient : Quotient ℕ _≈ₚ_
ℕ/parity-Quotient = record
  { ≈-refl  = λ _ → refl
  ; ≈-sym   = sym
  ; ≈-trans = trans
  }

ℕ/parity-Canonical : Canonical ℕ/parity-Quotient
ℕ/parity-Canonical = record
  { canonical            = canonical-parity
  ; canonical-idempotent = canonical-parity-idem
  ; canonical-respects-≈ = λ {m} {n} eq → canonical-parity-respects {m} {n} eq
  ; ≈-canonical          = ≈ₚ-canonical
  }

------------------------------------------------------------------------
-- 5. Capstone for QU6.
--
-- ℕ / ≈ₚ ≅ F₂ as a Quotient + Canonical instance. The canonical
-- form picks the 2-element {0, 1} ⊂ ℕ as class representatives,
-- matching the 3+1 parity universal at the ℕ-level.
------------------------------------------------------------------------
