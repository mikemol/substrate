------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Mul
--
-- Multiplication properties on ℕ: zero/identity, suc-step,
-- commutativity, distributivity over addition.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Mul where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong₂; cong-trans; sym-trans)
open import Substrate.Foundation.Nat.Properties.Add
  using (+-identityʳ; +-suc; +-assoc; +-comm)

*-zeroˡ : (n : ℕ) → zero * n ≡ zero
*-zeroˡ _ = refl

*-zeroʳ : (n : ℕ) → n * zero ≡ zero
*-zeroʳ zero    = refl
*-zeroʳ (suc n) = *-zeroʳ n

*-identityˡ : (n : ℕ) → suc zero * n ≡ n
*-identityˡ n = +-identityʳ n

*-identityʳ : (n : ℕ) → n * suc zero ≡ n
*-identityʳ zero    = refl
*-identityʳ (suc n) = cong suc (*-identityʳ n)

*-suc : (m n : ℕ) → m * suc n ≡ m + m * n
*-suc zero    _ = refl
*-suc (suc m) n =
  cong suc
    (cong-trans (n +_) (*-suc m n)
       (sym-trans (+-assoc n m (m * n))
          (cong-trans (_+ (m * n)) (+-comm n m)
             (+-assoc m n (m * n)))))

*-comm : (m n : ℕ) → m * n ≡ n * m
*-comm zero    n = sym (*-zeroʳ n)
*-comm (suc m) n = cong-trans (n +_) (*-comm m n) (sym (*-suc n m))

*-distribˡ-+ : (a m n : ℕ) → a * (m + n) ≡ a * m + a * n
*-distribˡ-+ zero    _ _ = refl
*-distribˡ-+ (suc a) m n =
  let ih = *-distribˡ-+ a m n
      lemma : (m + n) + (a * (m + n)) ≡ (m + a * m) + (n + a * n)
      lemma = cong-trans ((m + n) +_) ih
              (trans (+-assoc m n (a * m + a * n))
                     (cong-trans (m +_)
                        (sym-trans (+-assoc n (a * m) (a * n))
                           (cong-trans (_+ (a * n)) (+-comm n (a * m))
                              (+-assoc (a * m) n (a * n))))
                        (sym (+-assoc m (a * m) (n + a * n)))))
  in lemma

*-distribʳ-+ : (a m n : ℕ) → (m + n) * a ≡ m * a + n * a
*-distribʳ-+ a m n =
  trans (*-comm (m + n) a)
  (trans (*-distribˡ-+ a m n)
         (cong₂ _+_ (*-comm a m) (*-comm a n)))

------------------------------------------------------------------------
-- Associativity. Reduce on the leftmost factor via *-distribʳ-+.
------------------------------------------------------------------------

*-assoc : (m n p : ℕ) → (m * n) * p ≡ m * (n * p)
*-assoc zero    _ _ = refl
*-assoc (suc m) n p =
  trans (*-distribʳ-+ p n (m * n))
        (cong (n * p +_) (*-assoc m n p))

------------------------------------------------------------------------
-- Middle-factor interchange of a product of two products (reusable for
-- multi-factor reassociations, e.g. ℚ distributivity denominators).
------------------------------------------------------------------------

quad : (w x y z : ℕ) → (w * x) * (y * z) ≡ (w * y) * (x * z)
quad w x y z =
  trans (*-assoc w x (y * z))
  (trans (cong (w *_) (sym (*-assoc x y z)))
  (trans (cong (λ t → w * (t * z)) (*-comm x y))
  (trans (cong (w *_) (*-assoc y x z))
         (sym (*-assoc w y (x * z))))))
