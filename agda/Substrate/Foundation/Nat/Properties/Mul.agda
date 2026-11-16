------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Mul
--
-- Multiplication properties on ℕ: zero/identity, suc-step,
-- commutativity, distributivity over addition.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Mul where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.CongTrans
open import Substrate.Foundation.Eq.SymTrans

*-zeroˡ : (n : ℕ) → zero * n ≡ zero
*-zeroˡ _ = refl

*-zeroʳ : (n : ℕ) → n * zero ≡ zero
*-zeroʳ zero    = refl
*-zeroʳ (suc n) = *-zeroʳ n

*-identityˡ : (n : ℕ) → suc zero * n ≡ n
*-identityˡ n = +ℕ-identityʳ n

*-identityʳ : (n : ℕ) → n * suc zero ≡ n
*-identityʳ zero    = refl
*-identityʳ (suc n) = cong suc (*-identityʳ n)

*-suc : (m n : ℕ) → m * suc n ≡ m ℕ+ m * n
*-suc zero    _ = refl
*-suc (suc m) n =
  cong suc
    (cong-trans (n ℕ+_) (*-suc m n)
       (sym-trans (+ℕ-assoc n m (m * n))
          (cong-trans (_ℕ+ (m * n)) (+ℕ-comm n m)
             (+ℕ-assoc m n (m * n)))))

*-comm : (m n : ℕ) → m * n ≡ n * m
*-comm zero    n = sym (*-zeroʳ n)
*-comm (suc m) n = cong-trans (n ℕ+_) (*-comm m n) (sym (*-suc n m))

*-distribˡ-+ : (a m n : ℕ) → a * (m ℕ+ n) ≡ a * m ℕ+ a * n
*-distribˡ-+ zero    _ _ = refl
*-distribˡ-+ (suc a) m n =
  let ih = *-distribˡ-+ a m n
      lemma : (m ℕ+ n) ℕ+ (a * (m ℕ+ n)) ≡ (m ℕ+ a * m) ℕ+ (n ℕ+ a * n)
      lemma = cong-trans ((m ℕ+ n) ℕ+_) ih
              (trans (+ℕ-assoc m n (a * m ℕ+ a * n))
                     (cong-trans (m ℕ+_)
                        (sym-trans (+ℕ-assoc n (a * m) (a * n))
                           (cong-trans (_ℕ+ (a * n)) (+ℕ-comm n (a * m))
                              (+ℕ-assoc (a * m) n (a * n))))
                        (sym (+ℕ-assoc m (a * m) (n ℕ+ a * n)))))
  in lemma

*-distribʳ-+ : (a m n : ℕ) → (m ℕ+ n) * a ≡ m * a ℕ+ n * a
*-distribʳ-+ a m n =
  trans (*-comm (m ℕ+ n) a)
  (trans (*-distribˡ-+ a m n)
         (cong₂ _ℕ+_ (*-comm a m) (*-comm a n)))

------------------------------------------------------------------------
-- Associativity. Reduce on the leftmost factor via *-distribʳ-+.
------------------------------------------------------------------------

*-assoc : (m n p : ℕ) → (m * n) * p ≡ m * (n * p)
*-assoc zero    _ _ = refl
*-assoc (suc m) n p =
  trans (*-distribʳ-+ p n (m * n))
        (cong (n * p ℕ+_) (*-assoc m n p))

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

-- Middle-swap of a right-nested triple product: a·(b·c) ≡ b·(a·c). The
-- three-factor analogue of *-comm — reassociate, swap the outer pair,
-- reassociate back. (quad is the four-factor interchange; this is three.)
swap-mul : (a b c : ℕ) → a * (b * c) ≡ b * (a * c)
swap-mul a b c =
  trans (sym (*-assoc a b c))
        (trans (cong₂ _*_ (*-comm a b) refl) (*-assoc b a c))
