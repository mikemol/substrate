------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties
--
-- Substrate-native properties of ℕ (associativity / commutativity /
-- identity / suc-* lemmas). Mirrors stdlib's Data.Nat.Properties
-- but built on Foundation.Nat / Foundation.Eq.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)

------------------------------------------------------------------------
-- Addition.
------------------------------------------------------------------------

+-identityˡ : (n : ℕ) → zero + n ≡ n
+-identityˡ _ = refl

+-identityʳ : (n : ℕ) → n + zero ≡ n
+-identityʳ zero    = refl
+-identityʳ (suc n) = cong suc (+-identityʳ n)

+-suc : (m n : ℕ) → m + suc n ≡ suc (m + n)
+-suc zero    _ = refl
+-suc (suc m) n = cong suc (+-suc m n)

+-assoc : (m n k : ℕ) → (m + n) + k ≡ m + (n + k)
+-assoc zero    _ _ = refl
+-assoc (suc m) n k = cong suc (+-assoc m n k)

+-comm : (m n : ℕ) → m + n ≡ n + m
+-comm zero    n = sym (+-identityʳ n)
+-comm (suc m) n = trans (cong suc (+-comm m n)) (sym (+-suc n m))

------------------------------------------------------------------------
-- Multiplication.
------------------------------------------------------------------------

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
    (trans (cong (n +_) (*-suc m n))
           (trans (sym (+-assoc n m (m * n)))
                  (trans (cong (_+ (m * n)) (+-comm n m))
                         (+-assoc m n (m * n)))))

*-comm : (m n : ℕ) → m * n ≡ n * m
*-comm zero    n = sym (*-zeroʳ n)
*-comm (suc m) n = trans (cong (n +_) (*-comm m n)) (sym (*-suc n m))

------------------------------------------------------------------------
-- Distributivity.
------------------------------------------------------------------------

*-distribˡ-+ : (a m n : ℕ) → a * (m + n) ≡ a * m + a * n
*-distribˡ-+ zero    _ _ = refl
*-distribˡ-+ (suc a) m n =
  let ih = *-distribˡ-+ a m n
      -- (m + n) + a*(m+n) ≡ (m + n) + (a*m + a*n)
      --                   ≡ m + (n + (a*m + a*n))
      --                   ≡ m + ((n + a*m) + a*n)
      --                   ≡ m + ((a*m + n) + a*n)
      --                   ≡ m + (a*m + (n + a*n))
      --                   ≡ (m + a*m) + (n + a*n)
      lemma : (m + n) + (a * (m + n)) ≡ (m + a * m) + (n + a * n)
      lemma = trans (cong ((m + n) +_) ih)
              (trans (+-assoc m n (a * m + a * n))
              (trans (cong (m +_)
                       (trans (sym (+-assoc n (a * m) (a * n)))
                       (trans (cong (_+ (a * n)) (+-comm n (a * m)))
                              (+-assoc (a * m) n (a * n)))))
                     (sym (+-assoc m (a * m) (n + a * n)))))
  in lemma

*-distribʳ-+ : (a m n : ℕ) → (m + n) * a ≡ m * a + n * a
*-distribʳ-+ a m n =
  trans (*-comm (m + n) a)
  (trans (*-distribˡ-+ a m n)
         (cong₂-+-* a m n))
  where
    open Substrate.Foundation.Eq using (cong₂)
    cong₂-+-* : (a m n : ℕ) → a * m + a * n ≡ m * a + n * a
    cong₂-+-* a m n = cong₂ _+_ (*-comm a m) (*-comm a n)
