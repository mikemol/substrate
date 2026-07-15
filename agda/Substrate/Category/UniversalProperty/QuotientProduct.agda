------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.QuotientProduct
--
-- QU10 of the QU-arc per [scratch/qu_arc_plan.md].
--
-- The universal property of QUOTIENT-OF-PRODUCT, aka the CRT
-- pattern at its abstract level.
--
-- STATEMENT:
--
-- Given a carrier A and two equivalence relations _≈₁_, _≈₂_ on A
-- such that the joint equivalence `_≈₁∩₂_ a b = a ≈₁ b × a ≈₂ b`
-- holds with no additional constraint, the quotient by the joint
-- equivalence is the product of the individual quotients:
--
--   A / _≈₁∩₂_  ≅  (A / _≈₁_) × (A / _≈₂_)
--
-- This is the CRT universal property in disguise: when ~ₘ and ~ₙ
-- are coprime modular equivalences on ℕ, ~ₘₙ ⊆ ~ₘ × ~ₙ (and the
-- reverse inclusion holds by Bezout), making ℕ/(mn) the joint
-- quotient and ≅ to ℕ/m × ℕ/n. QU13 instantiates exactly this.
--
-- Per [[project-composite-torsion-euler-substrate]]: this is the
-- abstract universal property the substrate is naming; CRT instances
-- (cyclic, abelian, multi-factor) become trivial witnesses once the
-- UP is in scope.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.QuotientProduct where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Unit using (⊤; tt)

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Algebra.Nat.Mod using (_mod-suc_)
open import Substrate.Algebra.Quotient using (Quotient)
open import Substrate.Category.UniversalProperty using (UPArrowP; mkUP)
open import Substrate.Category.UniversalProperty.Vacuity using (Contentful)
open import Substrate.Category.UniversalProperty.Quotient
  using (QuotientUP; Respects)

------------------------------------------------------------------------
-- 1. The joint equivalence.
--
-- Given two equivalences on the same carrier, their conjunction is
-- itself an equivalence. This is the equivalence that the
-- "quotient by both" UP is about.
------------------------------------------------------------------------

_∩_ :
  {A : Set} (_≈₁_ _≈₂_ : A → A → Set) → A → A → Set
(_≈₁_ ∩ _≈₂_) a b = (a ≈₁ b) × (a ≈₂ b)

-- The joint equivalence-relation witnesses.
∩-refl :
  {A : Set} {_≈₁_ _≈₂_ : A → A → Set}
  (Q₁ : Quotient A _≈₁_) (Q₂ : Quotient A _≈₂_)
  (a : A) → (_≈₁_ ∩ _≈₂_) a a
∩-refl Q₁ Q₂ a = Quotient.≈-refl Q₁ a , Quotient.≈-refl Q₂ a

∩-sym :
  {A : Set} {_≈₁_ _≈₂_ : A → A → Set}
  (Q₁ : Quotient A _≈₁_) (Q₂ : Quotient A _≈₂_)
  {a b : A} → (_≈₁_ ∩ _≈₂_) a b → (_≈₁_ ∩ _≈₂_) b a
∩-sym Q₁ Q₂ (p , q) = Quotient.≈-sym Q₁ p , Quotient.≈-sym Q₂ q

∩-trans :
  {A : Set} {_≈₁_ _≈₂_ : A → A → Set}
  (Q₁ : Quotient A _≈₁_) (Q₂ : Quotient A _≈₂_)
  {a b c : A} →
  (_≈₁_ ∩ _≈₂_) a b → (_≈₁_ ∩ _≈₂_) b c → (_≈₁_ ∩ _≈₂_) a c
∩-trans Q₁ Q₂ (p₁ , q₁) (p₂ , q₂) =
  Quotient.≈-trans Q₁ p₁ p₂ , Quotient.≈-trans Q₂ q₁ q₂

-- Joint quotient.
∩-Quotient :
  {A : Set} {_≈₁_ _≈₂_ : A → A → Set}
  (Q₁ : Quotient A _≈₁_) (Q₂ : Quotient A _≈₂_) →
  Quotient A (_≈₁_ ∩ _≈₂_)
∩-Quotient Q₁ Q₂ = record
  { ≈-refl  = ∩-refl Q₁ Q₂
  ; ≈-sym   = ∩-sym Q₁ Q₂
  ; ≈-trans = ∩-trans Q₁ Q₂
  }

------------------------------------------------------------------------
-- 2. The QuotientProduct record.
--
-- Bundles a pair of quotients (Q₁, Q₂) on the same carrier with the
-- joint quotient and the splitting witness. The splitting is the
-- substrate's substantive load:
--
--   • forward  : A → (A × A)  given by (a, a) — diagonal
--   • backward : (A × A) → A  is the load-bearing CRT splitter;
--                              for cyclic-prime ≡ₘ, ≡ₙ this is the
--                              ts + um Bezout combination.
--   • round-trips up to ≈₁∩₂ on the A-side, and componentwise up to
--     ≈₁ / ≈₂ on the (A × A)-side.
--
-- Substrate-honest signature scope: this slice provides the record
-- and the trivial diagonal-only witness. The CRT-specific splitter
-- lands at QU13 once the modular-equivalence instance exists.
------------------------------------------------------------------------

record QuotientProduct
  (A : Set)
  (_≈₁_ : A → A → Set) (Q₁ : Quotient A _≈₁_)
  (_≈₂_ : A → A → Set) (Q₂ : Quotient A _≈₂_)
  : Set₁ where
  field
    -- The joint quotient (= the equalised quotient).
    joint-Q : Quotient A (_≈₁_ ∩ _≈₂_)
    -- The splitting map (typically `a ↦ (a , a)` for the trivial
    -- case; CRT instantiates this with the Bezout-mediated split).
    split   : A → A × A
    -- The combining map (the load-bearing CRT direction).
    combine : A × A → A
    -- Round-trip: combining a split returns an equivalent element.
    split-combine :
      (a : A) → (_≈₁_ ∩ _≈₂_) (combine (split a)) a
    -- Componentwise round-trip on the product side.
    combine-split-≈₁ :
      (a₁ a₂ : A) → a₁ ≈₁ proj₁ (split (combine (a₁ , a₂)))
    combine-split-≈₂ :
      (a₁ a₂ : A) → a₂ ≈₂ proj₂ (split (combine (a₁ , a₂)))

open QuotientProduct public

------------------------------------------------------------------------
-- 3. No trivial witness.
--
-- The diagonal `a ↦ (a, a)` does NOT satisfy QuotientProduct: the
-- componentwise round-trip on the product side asks that the second
-- coordinate is recoverable, which the diagonal collapses. This is
-- the substantive content of CRT — `combine` is a non-trivial
-- splitter whose existence requires extra structure (coprimality,
-- for the modular instance at QU12-13).
--
-- The record is therefore left with no default witness; instances
-- discharge it under their specific hypotheses.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- 4. UPArrow registration.
------------------------------------------------------------------------

-- VACUITY-AUDIT REPAIR (2026-06-03): was a ⊤-collapse placeholder. Wired to
-- the real Contentful quotient-PRODUCT — CRT: a residue pair (mod 3, mod 5)
-- is jointly solved by any x agreeing with both. This IS the joint quotient
-- ℕ ↠ ℤ/3 × ℤ/5 ≅ ℤ/15. Content-bearing: (1,2) is not solved by 0.
QuotientProduct-W : (ℕ × ℕ) → ℕ → Set   -- "two residues (mod 3, mod 5)" ↦ "a joint representative (mod 15)"
QuotientProduct-W p x = (x mod-suc 2 ≡ proj₁ p mod-suc 2)
                      × (x mod-suc 4 ≡ proj₂ p mod-suc 4)

QuotientProduct-UPArrow : UPArrowP (ℕ × ℕ) ℕ QuotientProduct-W
QuotientProduct-UPArrow = mkUP

QuotientProduct-contentful : Contentful QuotientProduct-UPArrow
QuotientProduct-contentful = (1 , 2) , 0 , λ { (() , _) }

------------------------------------------------------------------------
-- 5. Capstone for QU10.
--
-- QuotientProduct record + diagonal witness + UPArrow registration.
-- CRT (QU12-QU14) refines `split` / `combine` to the Bezout-mediated
-- splitter for coprime-modulus quotients.
------------------------------------------------------------------------
