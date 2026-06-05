------------------------------------------------------------------------
-- Substrate.Algebra.Z.Properties.MulFull
--
-- The FULL ℤ multiplication ring laws (all sign cases) — the sign-grind the
-- back-substitution-only `Z.Properties.Mul` deliberately avoided. These gate
-- the ℚ field laws (Q.Properties.Field). Built by REDUCING every sign case to
-- the existing nonneg lemmas (`*ℤ-assoc-pos-pos`, `distribˡ-scalar`) via
-- `neg-*-left` / `neg-*-right`, `neg-+ℤ`, and `-ℤ-involutive`.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Properties.MulFull where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Nat.Properties.Add using (+-identityʳ; +-suc)
open import Substrate.Foundation.Nat.Properties.Mul using (*-zeroʳ)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; -ℤ_; -ℤ-involutive)
open import Substrate.Algebra.Z.Arithmetic using (_⊖_; _+ℤ_; _*ℤ_)
open import Substrate.Algebra.Z.Properties.Mul
  using (*ℤ-comm; neg-*-left; *ℤ-assoc-pos-pos; neg-pos-as-⊖; neg-add;
         distribˡ-scalar)
open import Substrate.Algebra.Z.Properties.Add using (⊖-+pos; +ℤ-comm)
open import Substrate.Foundation.Nat.Properties.Cancel using (+-cancelˡ; *-cancelʳ-suc)

------------------------------------------------------------------------
-- 1. Negation pulls out of the right factor too.
------------------------------------------------------------------------

neg-*-right : (x y : ℤ) → x *ℤ (-ℤ y) ≡ -ℤ (x *ℤ y)
neg-*-right x y =
  trans (*ℤ-comm x (-ℤ y))
        (trans (neg-*-left y x) (cong -ℤ_ (*ℤ-comm y x)))

------------------------------------------------------------------------
-- 2. Identity and zero.
------------------------------------------------------------------------

*ℤ-identityˡ : (x : ℤ) → (+ 1) *ℤ x ≡ x
*ℤ-identityˡ (+ n)    = cong +_ (+-identityʳ n)
*ℤ-identityˡ (-suc n) = cong (λ z → -ℤ (+ z)) (+-identityʳ (suc n))

*ℤ-identityʳ : (x : ℤ) → x *ℤ (+ 1) ≡ x
*ℤ-identityʳ x = trans (*ℤ-comm x (+ 1)) (*ℤ-identityˡ x)

*ℤ-zeroˡ : (x : ℤ) → (+ 0) *ℤ x ≡ + 0
*ℤ-zeroˡ (+ n)    = refl
*ℤ-zeroˡ (-suc n) = refl

*ℤ-zeroʳ : (x : ℤ) → x *ℤ (+ 0) ≡ + 0
*ℤ-zeroʳ (+ m)    = cong +_ (*-zeroʳ m)
*ℤ-zeroʳ (-suc m) = cong (λ z → -ℤ (+ z)) (*-zeroʳ (suc m))

------------------------------------------------------------------------
-- 3. Full associativity (all sign cases), reducing to *ℤ-assoc-pos-pos.
------------------------------------------------------------------------

*ℤ-assoc : (x y z : ℤ) → (x *ℤ y) *ℤ z ≡ x *ℤ (y *ℤ z)
*ℤ-assoc x (+ j) (+ k)       = *ℤ-assoc-pos-pos x j k
*ℤ-assoc x (+ j) (-suc k)    =
  trans (neg-*-right (x *ℤ (+ j)) (+ suc k))
        (trans (cong -ℤ_ (*ℤ-assoc-pos-pos x j (suc k)))
               (sym (neg-*-right x (+ (j * suc k)))))
*ℤ-assoc x (-suc j) (+ k)    =
  trans (cong (_*ℤ (+ k)) (neg-*-right x (+ suc j)))
        (trans (neg-*-left (x *ℤ (+ suc j)) (+ k))
               (trans (cong -ℤ_ (*ℤ-assoc-pos-pos x (suc j) k))
                      (sym (neg-*-right x (+ (suc j * k))))))
*ℤ-assoc x (-suc j) (-suc k) =
  trans (cong (_*ℤ (-suc k)) (neg-*-right x (+ suc j)))
        (trans (neg-*-right (-ℤ (x *ℤ (+ suc j))) (+ suc k))
               (trans (cong -ℤ_ (neg-*-left (x *ℤ (+ suc j)) (+ suc k)))
                      (trans (-ℤ-involutive ((x *ℤ (+ suc j)) *ℤ (+ suc k)))
                             (*ℤ-assoc-pos-pos x (suc j) (suc k)))))

------------------------------------------------------------------------
-- 4. Negation distributes over ℤ-addition (via ⊖).
------------------------------------------------------------------------

neg-⊖ : (m n : ℕ) → -ℤ (m ⊖ n) ≡ n ⊖ m
neg-⊖ m       zero    = neg-pos-as-⊖ m
neg-⊖ zero    (suc n) = refl
neg-⊖ (suc m) (suc n) = neg-⊖ m n

neg-+ℤ : (a b : ℤ) → -ℤ (a +ℤ b) ≡ (-ℤ a) +ℤ (-ℤ b)
neg-+ℤ (+ m)    (+ n)    = sym (neg-add m n)
neg-+ℤ (+ m)    (-suc n) =
  trans (neg-⊖ m (suc n))
        (sym (trans (cong (_+ℤ (+ suc n)) (neg-pos-as-⊖ m))
                    (⊖-+pos 0 m (suc n))))
neg-+ℤ (-suc m) (+ n)    =
  trans (neg-⊖ n (suc m))
        (sym (trans (cong ((+ suc m) +ℤ_) (neg-pos-as-⊖ n))
                    (trans (+ℤ-comm (+ suc m) (0 ⊖ n)) (⊖-+pos 0 n (suc m)))))
neg-+ℤ (-suc m) (-suc n) = cong (λ z → + suc z) (sym (+-suc m n))

------------------------------------------------------------------------
-- 5. Full distributivity (all sign cases).
------------------------------------------------------------------------

*ℤ-distribˡ-+ : (x y z : ℤ) → x *ℤ (y +ℤ z) ≡ (x *ℤ y) +ℤ (x *ℤ z)
*ℤ-distribˡ-+ (+ k)    y z = distribˡ-scalar k y z
*ℤ-distribˡ-+ (-suc m) y z =
  trans (neg-*-left (+ suc m) (y +ℤ z))
        (trans (cong -ℤ_ (distribˡ-scalar (suc m) y z))
               (trans (neg-+ℤ ((+ suc m) *ℤ y) ((+ suc m) *ℤ z))
                      (cong₂ _+ℤ_ (sym (neg-*-left (+ suc m) y))
                                  (sym (neg-*-left (+ suc m) z)))))

*ℤ-distribʳ-+ : (x y z : ℤ) → (x +ℤ y) *ℤ z ≡ (x *ℤ z) +ℤ (y *ℤ z)
*ℤ-distribʳ-+ x y z =
  trans (*ℤ-comm (x +ℤ y) z)
        (trans (*ℤ-distribˡ-+ z x y)
               (cong₂ _+ℤ_ (*ℤ-comm z x) (*ℤ-comm z y)))

------------------------------------------------------------------------
-- 6. Cancellation by a positive factor, and a factor-swap helper —
--    the algebra cross-multiplication transitivity needs (for ℚ's _≈ℚ_).
------------------------------------------------------------------------

+ℤ-injective  : {j k : ℕ} → (+ j) ≡ (+ k) → j ≡ k
+ℤ-injective refl = refl

-suc-injectiveℤ : {j k : ℕ} → (-suc j) ≡ (-suc k) → j ≡ k
-suc-injectiveℤ refl = refl

*ℤ-cancelʳ-pos : (x y : ℤ) (d : ℕ) →
                 x *ℤ (+ suc d) ≡ y *ℤ (+ suc d) → x ≡ y
*ℤ-cancelʳ-pos (+ m)    (+ n)    d eq = cong +_ (*-cancelʳ-suc m n d (+ℤ-injective eq))
*ℤ-cancelʳ-pos (+ m)    (-suc n) d ()
*ℤ-cancelʳ-pos (-suc m) (+ n)    d ()
*ℤ-cancelʳ-pos (-suc m) (-suc n) d eq =
  cong -suc_ (*-cancelʳ-suc m n d (+-cancelˡ d (-suc-injectiveℤ eq)))

-- swap the last two factors: (x·y)·z ≡ (x·z)·y.
*ℤ-swap₂₃ : (x y z : ℤ) → (x *ℤ y) *ℤ z ≡ (x *ℤ z) *ℤ y
*ℤ-swap₂₃ x y z =
  trans (*ℤ-assoc x y z)
        (trans (cong (x *ℤ_) (*ℤ-comm y z)) (sym (*ℤ-assoc x z y)))
