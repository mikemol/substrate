------------------------------------------------------------------------
-- Substrate.Algebra.Z.Euclid
--
-- Euclid's lemma (coprime cancellation) via Bézout:
--   euclid : gcd-ℕ x (suc m′) ≡ 1 → suc m′ ∣ (x * y) → suc m′ ∣ y
--
-- The ℤ Bézout identity s·x + t·(suc m′) ≡ 1, multiplied by y and folded with
-- x·y = k·(suc m′), exhibits y = z·(suc m′) over ℤ; `ℤ-pos-divides` reads that
-- back to ℕ-divisibility (the negative-coefficient case is refuted by the
-- +/-suc constructor clash, since a positive divisor times -suc is -suc).
--
-- Z layer (uses bezout-ℤ, which imports Nat.GCD — so this can't live below it).
-- This is the second route to ℚ reduced-form uniqueness, alongside the CF-shape
-- keystones (Nat.GCD.CFInjective): coprime + cross-multiplication ⟹ equal.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Euclid where

open import Substrate.Foundation.Nat using (ℕ; suc; _*_)
open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong; cong₂)
open import Substrate.Foundation.Product using (proj₁; proj₂)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; -ℤ_)
open import Substrate.Algebra.Z.Arithmetic using (_+ℤ_; _*ℤ_)
open import Substrate.Algebra.Z.Properties.Mul using (*ℤ-comm)
open import Substrate.Algebra.Z.Properties.MulFull
  using (*ℤ-assoc; *ℤ-distribʳ-+; *ℤ-identityˡ; +ℤ-injective)
open import Substrate.Algebra.Z.Bezout using (bezout-ℤ)
open import Substrate.Algebra.Nat.Divides using (_∣_; divides)
open import Substrate.Algebra.Nat.GCD.GcdN using (gcd-ℕ)
open import Substrate.Algebra.Nat.GCD.GcdTrace using (gcd-trace)

-- ℤ→ℕ divisibility readback for a POSITIVE divisor.
ℤ-pos-divides : (z : ℤ) (m′ y : ℕ) → (+ y) ≡ z *ℤ (+ suc m′) → suc m′ ∣ y
ℤ-pos-divides (+ k)    m′ y eq = divides k (+ℤ-injective eq)
ℤ-pos-divides (-suc k) m′ y ()

euclid : (x m′ y : ℕ) → gcd-ℕ x (suc m′) ≡ 1 → suc m′ ∣ (x * y) → suc m′ ∣ y
euclid x m′ y cop (divides k xy≡k) = ℤ-pos-divides z m′ y y≡z·sm
  where
    bw = bezout-ℤ (gcd-trace x (suc m′))
    s  = proj₁ bw
    t  = proj₁ (proj₂ bw)
    bz : (s *ℤ (+ x)) +ℤ (t *ℤ (+ suc m′)) ≡ + 1
    bz = trans (proj₂ (proj₂ bw)) (cong +_ cop)
    z  = (s *ℤ (+ k)) +ℤ (t *ℤ (+ y))

    first-term : (s *ℤ (+ x)) *ℤ (+ y) ≡ (s *ℤ (+ k)) *ℤ (+ suc m′)
    first-term = trans (*ℤ-assoc s (+ x) (+ y))
                 (trans (cong (λ w → s *ℤ (+ w)) xy≡k)
                        (sym (*ℤ-assoc s (+ k) (+ suc m′))))

    second-term : (t *ℤ (+ suc m′)) *ℤ (+ y) ≡ (t *ℤ (+ y)) *ℤ (+ suc m′)
    second-term = trans (*ℤ-assoc t (+ suc m′) (+ y))
                  (trans (cong (t *ℤ_) (*ℤ-comm (+ suc m′) (+ y)))
                         (sym (*ℤ-assoc t (+ y) (+ suc m′))))

    y≡z·sm : (+ y) ≡ z *ℤ (+ suc m′)
    y≡z·sm = trans (sym (*ℤ-identityˡ (+ y)))
             (trans (cong (_*ℤ (+ y)) (sym bz))
             (trans (*ℤ-distribʳ-+ (s *ℤ (+ x)) (t *ℤ (+ suc m′)) (+ y))
             (trans (cong₂ _+ℤ_ first-term second-term)
                    (sym (*ℤ-distribʳ-+ (s *ℤ (+ k)) (t *ℤ (+ y)) (+ suc m′))))))
