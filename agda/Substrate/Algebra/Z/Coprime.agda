------------------------------------------------------------------------
-- Substrate.Algebra.Z.Coprime
--
-- Coprimality from Bézout (the ℤ side of the ℚ-Canonical shape route).
--
--   bezout-1→coprime : s·(+a) + t·(+b) ≡ +1 → gcd-ℕ a b ≡ 1
--   cofactor-coprime : na ≡ qn·g → suc d ≡ qd·g → gcd-ℕ qn qd ≡ 1
--                      (g = gcd-ℕ na (suc d); the cofactors are coprime)
--
-- Lives in the Z layer because it uses `bezout-ℤ` (Z.Bezout), which itself
-- imports Nat.GCD — so this cannot live under Nat.GCD without a cycle.
--
-- cofactor-coprime is the source of `reduce`-produces-reduced (Q layer):
-- dividing num/den by their gcd yields coprime cofactors, so `reduce q` is in
-- lowest terms — the coprimality KEYSTONE #2 consumes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Coprime where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂; subst)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; -ℤ_)
open import Substrate.Algebra.Z.Arithmetic using (_+ℤ_; _*ℤ_)
open import Substrate.Algebra.Z.Properties.MulFull
  using (*ℤ-assoc; *ℤ-distribʳ-+; *ℤ-identityˡ; +ℤ-injective; *ℤ-cancelʳ-pos)
open import Substrate.Algebra.Z.Bezout using (bezout-ℤ)
open import Substrate.Algebra.Nat.Divides using (_∣_; divides)
open import Substrate.Algebra.Nat.Divides.One using (∣-one)
open import Substrate.Algebra.Nat.GCD.GcdN using (gcd-ℕ)
open import Substrate.Algebra.Nat.GCD.GcdTrace using (gcd-trace)
open import Substrate.Algebra.Nat.GCD.GcdDividesLeft using (gcd-divides-left)
open import Substrate.Algebra.Nat.GCD.GcdDividesRight using (gcd-divides-right)
open import Substrate.Algebra.Nat.GCD.GcdPos using (gcd-pos)

private
  -- -ℤ (+ n) is never + 1: it is + 0 (n = 0) or -suc _ (n = suc _).
  neg-pos-not-one : (n : ℕ) → -ℤ (+ n) ≡ + 1 → ⊥
  neg-pos-not-one zero    eq with +ℤ-injective eq
  ... | ()
  neg-pos-not-one (suc j) ()

  -- A unit factor: z · (+ h) ≡ + 1 forces h ∣ 1 (so h ≡ 1).
  unit-z : (z : ℤ) (h : ℕ) → z *ℤ (+ h) ≡ + 1 → h ∣ 1
  unit-z (+ k)    h eq = divides k (sym (+ℤ-injective eq))
  unit-z (-suc k) h eq = ⊥-elim (neg-pos-not-one (suc k * h) eq)

-- Bézout-1 ⟹ coprime: a combination equal to 1 forces gcd 1.
bezout-1→coprime : (s t : ℤ) (a b : ℕ) →
  (s *ℤ (+ a)) +ℤ (t *ℤ (+ b)) ≡ + 1 → gcd-ℕ a b ≡ 1
bezout-1→coprime s t a b bz with gcd-divides-left a b | gcd-divides-right a b
... | divides qa a≡ | divides qb b≡ = ∣-one (unit-z z (gcd-ℕ a b) zg≡1)
  where
    z = (s *ℤ (+ qa)) +ℤ (t *ℤ (+ qb))
    zg≡1 : z *ℤ (+ gcd-ℕ a b) ≡ + 1
    zg≡1 = trans (*ℤ-distribʳ-+ (s *ℤ (+ qa)) (t *ℤ (+ qb)) (+ gcd-ℕ a b))
           (trans (cong₂ _+ℤ_
                     (trans (*ℤ-assoc s (+ qa) (+ gcd-ℕ a b)) (cong (λ x → s *ℤ (+ x)) (sym a≡)))
                     (trans (*ℤ-assoc t (+ qb) (+ gcd-ℕ a b)) (cong (λ x → t *ℤ (+ x)) (sym b≡))))
                  bz)

-- The cofactors of (na, suc d) by their gcd are coprime.
cofactor-coprime : (na d qn qd : ℕ) →
  na ≡ qn * gcd-ℕ na (suc d) → suc d ≡ qd * gcd-ℕ na (suc d) →
  gcd-ℕ qn qd ≡ 1
cofactor-coprime na d qn qd na≡ da≡ = bezout-1→coprime s t qn qd cofac-bz
  where
    g  = gcd-ℕ na (suc d)
    bw = bezout-ℤ (gcd-trace na (suc d))
    s  = proj₁ bw
    t  = proj₁ (proj₂ bw)
    bz : (s *ℤ (+ na)) +ℤ (t *ℤ (+ suc d)) ≡ + g
    bz = proj₂ (proj₂ bw)
    z  = (s *ℤ (+ qn)) +ℤ (t *ℤ (+ qd))
    gp = gcd-pos na d
    g′    = proj₁ gp
    g≡sg′ = proj₂ gp
    zg≡g : z *ℤ (+ g) ≡ + g
    zg≡g = trans (*ℤ-distribʳ-+ (s *ℤ (+ qn)) (t *ℤ (+ qd)) (+ g))
           (trans (cong₂ _+ℤ_
                     (trans (*ℤ-assoc s (+ qn) (+ g)) (cong (λ x → s *ℤ (+ x)) (sym na≡)))
                     (trans (*ℤ-assoc t (+ qd) (+ g)) (cong (λ x → t *ℤ (+ x)) (sym da≡))))
                  bz)
    cofac-bz : z ≡ + 1
    cofac-bz = *ℤ-cancelʳ-pos z (+ 1) g′
                 (subst (λ G → z *ℤ (+ G) ≡ (+ 1) *ℤ (+ G)) g≡sg′
                        (trans zg≡g (sym (*ℤ-identityˡ (+ g)))))
