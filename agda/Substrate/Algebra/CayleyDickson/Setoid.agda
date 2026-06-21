------------------------------------------------------------------------
-- Substrate.Algebra.CayleyDickson.Setoid
--
-- The `≈#` equivalence on the Cayley-Dickson tower, plus the `neg`/`conj`
-- behaviour on `zero#` — the setoid infrastructure that CD reasoning (and in
-- particular the ⊙.morton cocycle: conj-on-basis, the recursive product law)
-- needs but `Algebra.CayleyDickson` did not yet have (it carried only the bare
-- `i²≈−1` and the zero-divisor projections). Everything is structural induction
-- on the level `n`, bottoming out in ℚ's setoid (`≈# 0 = ≈ℚ`).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Setoid where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (refl)
open import Substrate.Foundation.Product using (_,_; _×_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_; ≈ℚ-refl; ≈ℚ-sym; ≈ℚ-trans)
open import Substrate.Algebra.Q.Properties.Congruence using (+ℚ-cong; *ℚ-cong)
open import Substrate.Algebra.Q.Properties.Field
  using (zero-absorbˡ; zero-absorbʳ; +ℚ-identityˡ; +ℚ-identityʳ; *ℚ-identityˡ; *ℚ-identityʳ)
open import Substrate.Algebra.CayleyDickson.CommuteEdge using (-ℚ-cong)
open import Substrate.Algebra.CayleyDickson
  using (Carrier; ≈#; add; sub; mul; neg; conj; zero#; one#)

------------------------------------------------------------------------
-- 1. ≈# is an equivalence (componentwise lift of ℚ's setoid).
------------------------------------------------------------------------

≈#-refl : (n : ℕ) (x : Carrier n) → ≈# n x x
≈#-refl zero    x       = ≈ℚ-refl x
≈#-refl (suc n) (a , b) = ≈#-refl n a , ≈#-refl n b

≈#-sym : (n : ℕ) {x y : Carrier n} → ≈# n x y → ≈# n y x
≈#-sym zero    {x} {y} p       = ≈ℚ-sym {x} {y} p
≈#-sym (suc n) (p , q)         = ≈#-sym n p , ≈#-sym n q

≈#-trans : (n : ℕ) {x y z : Carrier n} → ≈# n x y → ≈# n y z → ≈# n x z
≈#-trans zero    {x} {y} {z} p r = ≈ℚ-trans {x} {y} {z} p r
≈#-trans (suc n) (p , q) (p′ , q′) = ≈#-trans n p p′ , ≈#-trans n q q′

------------------------------------------------------------------------
-- 2. neg and conj fix zero# (the doubling's empty residue).
------------------------------------------------------------------------

-- neg n (zero# n) ≈# zero# n.  (At ℚ, −0 = 0 — by the ℤ zero self-negation.)
neg-zero# : (n : ℕ) → ≈# n (neg n (zero# n)) (zero# n)
neg-zero# zero    = refl
neg-zero# (suc n) = neg-zero# n , neg-zero# n

-- conj n (zero# n) ≈# zero# n.  (conj fixes the all-zero vector.)
conj-zero# : (n : ℕ) → ≈# n (conj n (zero# n)) (zero# n)
conj-zero# zero    = refl
conj-zero# (suc n) = conj-zero# n , neg-zero# n

------------------------------------------------------------------------
-- 3. ≈# is a CONGRUENCE for every CD operation (add / neg / conj / sub / mul).
-- Each is structural induction on n: the base is ℚ's congruence (+ℚ-cong /
-- -ℚ-cong / *ℚ-cong), the step is componentwise. `mul-cong` is the substantive
-- one (the doubling formula's congruence) and is the gating prerequisite for the
-- recursive product law eᵢ·eⱼ ≈# ε(i,j)·e_{i⊕j}, since that induction must rewrite
-- under mul. Reuses CommuteEdge.-ℚ-cong (negation respects ≈ℚ).
------------------------------------------------------------------------

add-cong : (n : ℕ) {x x′ y y′ : Carrier n} →
           ≈# n x x′ → ≈# n y y′ → ≈# n (add n x y) (add n x′ y′)
add-cong zero    {x} {x′} {y} {y′} px py = +ℚ-cong {x} {x′} {y} {y′} px py
add-cong (suc n) (pa , pb) (pc , pd)     = add-cong n pa pc , add-cong n pb pd

neg-cong : (n : ℕ) {x y : Carrier n} → ≈# n x y → ≈# n (neg n x) (neg n y)
neg-cong zero    {x} {y} p = -ℚ-cong {x} {y} p
neg-cong (suc n) (pa , pb) = neg-cong n pa , neg-cong n pb

conj-cong : (n : ℕ) {x y : Carrier n} → ≈# n x y → ≈# n (conj n x) (conj n y)
conj-cong zero    p        = p                       -- conj at level 0 is the identity
conj-cong (suc n) (pa , pb) = conj-cong n pa , neg-cong n pb

sub-cong : (n : ℕ) {x x′ y y′ : Carrier n} →
           ≈# n x x′ → ≈# n y y′ → ≈# n (sub n x y) (sub n x′ y′)
sub-cong n px py = add-cong n px (neg-cong n py)

mul-cong : (n : ℕ) {x x′ y y′ : Carrier n} →
           ≈# n x x′ → ≈# n y y′ → ≈# n (mul n x y) (mul n x′ y′)
mul-cong zero    {x} {x′} {y} {y′} px py = *ℚ-cong {x} {x′} {y} {y′} px py
mul-cong (suc n) (pa , pb) (pc , pd) =
    sub-cong n (mul-cong n pa pc) (mul-cong n (conj-cong n pd) pb)
  , add-cong n (mul-cong n pd pa) (mul-cong n pb (conj-cong n pc))

------------------------------------------------------------------------
-- 4. ZERO and ONE laws. The doubling product's off-diagonal halves vanish
-- (mul-zero), so the empty residue is killed (add/sub-zero); together these give
-- 1 as a two-sided multiplicative identity (mul-one). All clean — NO negation
-- distribution (the cocycle's deeper layer). These are the laws the recursive
-- product law's 4-case induction needs to discharge its zero/identity corners.
------------------------------------------------------------------------

add-zeroˡ : (n : ℕ) (x : Carrier n) → ≈# n (add n (zero# n) x) x
add-zeroˡ zero    x       = +ℚ-identityˡ x
add-zeroˡ (suc n) (a , b) = add-zeroˡ n a , add-zeroˡ n b

add-zeroʳ : (n : ℕ) (x : Carrier n) → ≈# n (add n x (zero# n)) x
add-zeroʳ zero    x       = +ℚ-identityʳ x
add-zeroʳ (suc n) (a , b) = add-zeroʳ n a , add-zeroʳ n b

-- sub x 0 ≈# x   (sub x y = add x (neg y); neg 0 ≈# 0)
sub-zeroʳ : (n : ℕ) (x : Carrier n) → ≈# n (sub n x (zero# n)) x
sub-zeroʳ n x = ≈#-trans n (add-cong n (≈#-refl n x) (neg-zero# n)) (add-zeroʳ n x)

-- mul absorbs zero on both sides (mutually: the doubling formula crosses them).
mul-zeroˡ : (n : ℕ) (x : Carrier n) → ≈# n (mul n (zero# n) x) (zero# n)
mul-zeroʳ : (n : ℕ) (x : Carrier n) → ≈# n (mul n x (zero# n)) (zero# n)
mul-zeroˡ zero    x       = zero-absorbˡ x
mul-zeroˡ (suc n) (c , d) =
    ≈#-trans n (sub-cong n (mul-zeroˡ n c) (mul-zeroʳ n (conj n d))) (sub-zeroʳ n (zero# n))
  , ≈#-trans n (add-cong n (mul-zeroʳ n d) (mul-zeroˡ n (conj n c))) (add-zeroʳ n (zero# n))
mul-zeroʳ zero    x       = zero-absorbʳ x
mul-zeroʳ (suc n) (a , b) =
    ≈#-trans n (sub-cong n (mul-zeroʳ n a)
                           (≈#-trans n (mul-cong n (conj-zero# n) (≈#-refl n b)) (mul-zeroˡ n b)))
               (sub-zeroʳ n (zero# n))
  , ≈#-trans n (add-cong n (mul-zeroˡ n a)
                           (≈#-trans n (mul-cong n (≈#-refl n b) (conj-zero# n)) (mul-zeroʳ n b)))
               (add-zeroʳ n (zero# n))

-- conj fixes the unit 1 (its imaginary half is 0).
conj-one# : (n : ℕ) → ≈# n (conj n (one# n)) (one# n)
conj-one# zero    = ≈#-refl 0 (one# 0)
conj-one# (suc n) = conj-one# n , neg-zero# n

-- 1 is a two-sided multiplicative identity (mutually: the doubling crosses sides).
mul-oneˡ : (n : ℕ) (x : Carrier n) → ≈# n (mul n (one# n) x) x
mul-oneʳ : (n : ℕ) (x : Carrier n) → ≈# n (mul n x (one# n)) x
mul-oneˡ zero    x       = *ℚ-identityˡ x
mul-oneˡ (suc n) (c , d) =
    ≈#-trans n (sub-cong n (mul-oneˡ n c) (mul-zeroʳ n (conj n d))) (sub-zeroʳ n c)
  , ≈#-trans n (add-cong n (mul-oneʳ n d) (mul-zeroˡ n (conj n c))) (add-zeroʳ n d)
mul-oneʳ zero    x       = *ℚ-identityʳ x
mul-oneʳ (suc n) (a , b) =
    ≈#-trans n (sub-cong n (mul-oneʳ n a)
                           (≈#-trans n (mul-cong n (conj-zero# n) (≈#-refl n b)) (mul-zeroˡ n b)))
               (sub-zeroʳ n a)
  , ≈#-trans n (add-cong n (mul-zeroˡ n a)
                           (≈#-trans n (mul-cong n (≈#-refl n b) (conj-one# n)) (mul-oneʳ n b)))
               (add-zeroˡ n b)
