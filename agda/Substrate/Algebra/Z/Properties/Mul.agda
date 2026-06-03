------------------------------------------------------------------------
-- Substrate.Algebra.Z.Properties.Mul
--
-- The ℤ multiplication laws the Bézout back-substitution needs (the `*`
-- half of the operand ring). We prove exactly the laws the Euclidean fold
-- uses — distribution where one side is a NONNEGATIVE coercion (which is
-- all the back-sub touches: a, b, q, r are ℕ) and a specialised
-- associativity with the two right factors positive — via a scalar-over-⊖
-- lemma (M1) + neg-*-left. This avoids the full general *-distrib/assoc
-- sign grind while giving the back-sub everything it needs.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Properties.Mul where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Nat.Properties.Add using (+-identityʳ; +-suc)
open import Substrate.Foundation.Nat.Properties.Mul
  using (*-zeroʳ; *-comm; *-assoc; *-distribˡ-+; *-suc)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; -ℤ_; -ℤ-involutive)
open import Substrate.Algebra.Z.Arithmetic using (_⊖_; _+ℤ_; _-ℤ_; _*ℤ_)
open import Substrate.Algebra.Z.Properties.Add using (⊖-merge)

------------------------------------------------------------------------
-- 1. Helpers.
------------------------------------------------------------------------

neg-pos-as-⊖ : (j : ℕ) → -ℤ (+ j) ≡ 0 ⊖ j
neg-pos-as-⊖ zero    = refl
neg-pos-as-⊖ (suc j) = refl

⊖-cancelˡ : (k a b : ℕ) → (k + a) ⊖ (k + b) ≡ a ⊖ b
⊖-cancelˡ zero    a b = refl
⊖-cancelˡ (suc k) a b = ⊖-cancelˡ k a b

-- scalar (nonneg) times a difference.
M1 : (k m n : ℕ) → (+ k) *ℤ (m ⊖ n) ≡ (k * m) ⊖ (k * n)
M1 k m zero =
  cong ((k * m) ⊖_) (sym (*-zeroʳ k))
M1 k zero (suc n) =
  trans (neg-pos-as-⊖ (k * suc n)) (cong (_⊖ (k * suc n)) (sym (*-zeroʳ k)))
M1 k (suc m) (suc n) =
  trans (M1 k m n)
        (sym (trans (cong₂ _⊖_ (*-suc k m) (*-suc k n))
                    (⊖-cancelˡ k (k * m) (k * n))))

-- sum of two negatives.
neg-add : (α β : ℕ) → (-ℤ (+ α)) +ℤ (-ℤ (+ β)) ≡ -ℤ (+ (α + β))
neg-add α β =
  trans (cong₂ _+ℤ_ (neg-pos-as-⊖ α) (neg-pos-as-⊖ β))
        (trans (⊖-merge 0 α 0 β) (sym (neg-pos-as-⊖ (α + β))))

------------------------------------------------------------------------
-- 2. Commutativity and negation-pull.
------------------------------------------------------------------------

*ℤ-comm : (x y : ℤ) → x *ℤ y ≡ y *ℤ x
*ℤ-comm (+ m)    (+ n)    = cong +_ (*-comm m n)
*ℤ-comm (+ m)    (-suc n) = cong (λ z → -ℤ (+ z)) (*-comm m (suc n))
*ℤ-comm (-suc m) (+ n)    = cong (λ z → -ℤ (+ z)) (*-comm (suc m) n)
*ℤ-comm (-suc m) (-suc n) = cong +_ (*-comm (suc m) (suc n))

neg-*-left : (x y : ℤ) → (-ℤ x) *ℤ y ≡ -ℤ (x *ℤ y)
neg-*-left (+ zero)  (+ n)    = refl
neg-*-left (+ zero)  (-suc n) = refl
neg-*-left (+ suc m) (+ n)    = refl
neg-*-left (+ suc m) (-suc n) = -ℤ-involutive (+ (suc m * suc n))
neg-*-left (-suc m)  (+ n)    = sym (-ℤ-involutive (+ (suc m * n)))
neg-*-left (-suc m)  (-suc n) = refl

------------------------------------------------------------------------
-- 3. Distribution by a nonnegative scalar / over a nonnegative factor.
------------------------------------------------------------------------

-- (+k)·(x + y) = (+k)·x + (+k)·y.
distribˡ-scalar : (k : ℕ) (x y : ℤ) →
                  (+ k) *ℤ (x +ℤ y) ≡ ((+ k) *ℤ x) +ℤ ((+ k) *ℤ y)
distribˡ-scalar k (+ a)    (+ b)    = cong +_ (*-distribˡ-+ k a b)
distribˡ-scalar k (+ a)    (-suc b) =
  trans (M1 k a (suc b))
        (sym (trans (cong ((+ (k * a)) +ℤ_) (neg-pos-as-⊖ (k * suc b)))
                    (trans (⊖-merge (k * a) 0 0 (k * suc b))
                           (cong (_⊖ (k * suc b)) (+-identityʳ (k * a))))))
distribˡ-scalar k (-suc a) (+ b)    =
  trans (M1 k b (suc a))
        (sym (trans (cong (_+ℤ (+ (k * b))) (neg-pos-as-⊖ (k * suc a)))
                    (trans (⊖-merge 0 (k * suc a) (k * b) 0)
                           (cong ((k * b) ⊖_) (+-identityʳ (k * suc a))))))
distribˡ-scalar k (-suc a) (-suc b) =
  trans (cong (λ z → -ℤ (+ z))
              (trans (cong (k *_) (sym (cong suc (+-suc a b))))
                     (*-distribˡ-+ k (suc a) (suc b))))
        (sym (neg-add (k * suc a) (k * suc b)))

-- x·(+j + +k) = x·(+j) + x·(+k).
distribˡ-pos : (x : ℤ) (j k : ℕ) →
               x *ℤ ((+ j) +ℤ (+ k)) ≡ (x *ℤ (+ j)) +ℤ (x *ℤ (+ k))
distribˡ-pos (+ m)    j k = cong +_ (*-distribˡ-+ m j k)
distribˡ-pos (-suc m) j k =
  trans (cong (λ z → -ℤ (+ z)) (*-distribˡ-+ (suc m) j k))
        (sym (neg-add (suc m * j) (suc m * k)))

-- (x + y)·(+k) = x·(+k) + y·(+k).  (via comm + scalar-distribution)
distribʳ-pos : (x y : ℤ) (k : ℕ) →
               (x +ℤ y) *ℤ (+ k) ≡ (x *ℤ (+ k)) +ℤ (y *ℤ (+ k))
distribʳ-pos x y k =
  trans (*ℤ-comm (x +ℤ y) (+ k))
        (trans (distribˡ-scalar k x y)
               (cong₂ _+ℤ_ (*ℤ-comm (+ k) x) (*ℤ-comm (+ k) y)))

------------------------------------------------------------------------
-- 4. Specialised associativity: the two right factors nonnegative.
--    (all the Euclidean back-substitution needs.)
------------------------------------------------------------------------

*ℤ-assoc-pos-pos : (x : ℤ) (j k : ℕ) →
                   (x *ℤ (+ j)) *ℤ (+ k) ≡ x *ℤ ((+ j) *ℤ (+ k))
*ℤ-assoc-pos-pos (+ m)    j k = cong +_ (*-assoc m j k)
*ℤ-assoc-pos-pos (-suc m) j k =
  trans (neg-*-left (+ (suc m * j)) (+ k))
        (cong (λ z → -ℤ (+ z)) (*-assoc (suc m) j k))
