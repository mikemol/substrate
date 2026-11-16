------------------------------------------------------------------------
-- Substrate.Algebra.Z.Properties.MulFull.NegPlusInt
--
-- Defines: neg-+ℤ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.Properties.MulFull; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Properties.MulFull.NegPlusInt where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Z.Add.Op
open import Substrate.Algebra.Z.Add.PlusInt
open import Substrate.Algebra.Z.Sub
open import Substrate.Algebra.Z.Properties.Mul
open import Substrate.Algebra.Z.Properties.Add
open import Substrate.Algebra.Z.Properties.MulFull.Neg
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans



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
neg-+ℤ (-suc m) (-suc n) = cong (λ z → ℕ+ suc z) (sym (+ℕ-suc m n))
