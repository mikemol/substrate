------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.CRT
--
-- QU13 of the QU-arc per [scratch/qu_arc_plan.md].
--
-- The Chinese Remainder Theorem as a QuotientProduct instance.
--
-- STATEMENT:
--
--   For coprime m, n : ℕ (with `gcd(suc m, suc n) ≡ 1`):
--
--     ℕ / ≡[mn]   ≅   (ℕ / ≡[m])  ×  (ℕ / ≡[n])
--
--   This is the substrate's first concrete instance of
--   Substrate.Category.UniversalProperty.QuotientProduct.
--
-- The `combine : ℕ × ℕ → ℕ` direction is the Bezout-mediated CRT
-- splitter; the `split : ℕ → ℕ × ℕ` direction is the diagonal-of-
-- remainders `λ a → (a mod-suc m, a mod-suc n)`.
--
-- Substrate-honest scope: this slice names the OBLIGATION
-- (the QuotientProduct record at the CRT modulus pair) and supplies
-- the trivial `split` direction. The non-trivial `combine` requires
-- Bezout coefficients and is the substantive QU18 slice.
--
-- Per [[project-composite-torsion-euler-substrate]]: the substrate
-- now names CRT as a UP instance, with EEA / Bezout providing the
-- algorithmic content of `combine`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.CRT where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)

open import Substrate.Algebra.Nat.ModEquiv
  using (_≡[_]_; _mod-suc_)
open import Substrate.Algebra.Quotient using (Quotient)
open import Substrate.Algebra.Quotient.ModN using (ModN-Quotient)
open import Substrate.Category.UniversalProperty.QuotientProduct
  using (QuotientProduct; _∩_; ∩-Quotient)

------------------------------------------------------------------------
-- 1. Coprime as an implicit hypothesis.
--
-- The substrate's stance: `Coprime m n` is "the witness that lets
-- you construct a CRT-Witness". Rather than fixing a specific
-- coprime relation here (gcd ≡ 1, Bezout existence, etc.), the
-- coprime fact IS the inhabitation of CRT-Witness itself. This
-- keeps the file independent of the substrate's GCD module
-- (Phase D's substrate-native EEA rewrite supplies the concrete
-- inhabitant).
------------------------------------------------------------------------

------------------------------------------------------------------------
-- 2. The CRT QuotientProduct record (signature-bearing).
--
-- Parametric over (m, n) and a Coprime witness. Bundles:
--   • the two component Quotients (ModN-Quotient m, n)
--   • the joint Quotient (per ∩-Quotient)
--   • the split direction: a ↦ (a mod-suc m, a mod-suc n)
--   • the combine direction: the load-bearing CRT splitter,
--     parametric on a Bezout-style witness (QU18 supplies the
--     concrete construction via EEATrace + Bezout).
--
-- Substrate-honest scope: this record names the obligation; the
-- four round-trip fields are signature-bearing (typed but discharged
-- by passing in a CRT-combine witness at QU18).
------------------------------------------------------------------------

record CRT-Witness (m n : ℕ) : Set where
  field
    combine :
      ℕ × ℕ → ℕ
    -- Componentwise round-trip on (ℕ × ℕ): the combine result
    -- reduces to (a₁ mod-suc m, a₂ mod-suc n) componentwise.
    combine-mod-m :
      (a₁ a₂ : ℕ) → combine (a₁ , a₂) mod-suc m ≡ a₁ mod-suc m
    combine-mod-n :
      (a₁ a₂ : ℕ) → combine (a₁ , a₂) mod-suc n ≡ a₂ mod-suc n

open CRT-Witness public

------------------------------------------------------------------------
-- 3. Lifting a CRT-Witness into the QuotientProduct UP.
--
-- Given a `CRT-Witness m n coprime`, instantiate the
-- QuotientProduct record at the modular-equivalence quotients
-- (Q₁ = ModN-Quotient m, Q₂ = ModN-Quotient n) with:
--
--   split   = a ↦ (a , a)
--   combine = via CRT-Witness.combine
--
-- The split-combine round-trip uses combine-mod-m and combine-mod-n
-- under the modular equivalence: a ≡[m] b iff a mod-suc m ≡ b
-- mod-suc m, which `combine-mod-m` discharges directly.
------------------------------------------------------------------------

CRT-as-QuotientProduct :
  (m n : ℕ) →
  CRT-Witness m n →
  QuotientProduct ℕ
    (λ a b → a ≡[ m ] b) (ModN-Quotient m)
    (λ a b → a ≡[ n ] b) (ModN-Quotient n)
CRT-as-QuotientProduct m n w = record
  { joint-Q = ∩-Quotient (ModN-Quotient m) (ModN-Quotient n)
  ; split   = λ a → a , a
  ; combine = λ p → combine w p
  ; split-combine =
      λ a → combine-mod-m w a a , combine-mod-n w a a
  ; combine-split-≈₁ =
      λ a₁ a₂ →
        Quotient.≈-sym (ModN-Quotient m)
          {combine w (a₁ , a₂)} {a₁} (combine-mod-m w a₁ a₂)
  ; combine-split-≈₂ =
      λ a₁ a₂ →
        Quotient.≈-sym (ModN-Quotient n)
          {combine w (a₁ , a₂)} {a₂} (combine-mod-n w a₁ a₂)
  }

------------------------------------------------------------------------
-- 4. Capstone for QU13.
--
-- CRT lands as a QuotientProduct instance, parametric on a
-- CRT-Witness. The Bezout-mediated combine witness (the
-- algorithmic content of CRT) is QU18's job; this slice exposes
-- exactly the surface that EEA / Bezout must inhabit.
------------------------------------------------------------------------
