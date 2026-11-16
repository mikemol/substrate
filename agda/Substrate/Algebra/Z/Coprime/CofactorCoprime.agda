------------------------------------------------------------------------
-- Substrate.Algebra.Z.Coprime.CofactorCoprime
--
-- Defines: cofactor-coprime
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.Coprime; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Coprime.CofactorCoprime where
open import Substrate.Algebra.Z.Add
open import Substrate.Algebra.Z.Mul

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Product
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Arithmetic
open import Substrate.Algebra.Z.Properties.MulFull
open import Substrate.Algebra.Z.Bezout
open import Substrate.Algebra.Nat.Divides.Type
open import Substrate.Algebra.Nat.Divides.One
open import Substrate.Algebra.Nat.GCD.GcdN
open import Substrate.Algebra.Nat.GCD.GcdTrace
open import Substrate.Algebra.Nat.GCD.GcdDividesLeft
open import Substrate.Algebra.Nat.GCD.GcdDividesRight
open import Substrate.Algebra.Nat.GCD.GcdPos.GcdPos
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Z.Coprime.Private
open import Substrate.Algebra.Z.Coprime.Bezout1Tocoprime



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
