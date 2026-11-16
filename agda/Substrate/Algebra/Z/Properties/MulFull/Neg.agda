------------------------------------------------------------------------
-- Substrate.Algebra.Z.Properties.MulFull.Neg
--
-- Defines: neg-⊖
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.Properties.MulFull; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Properties.MulFull.Neg where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Z.Add.Op
open import Substrate.Algebra.Z.Sub
open import Substrate.Algebra.Z.Properties.Mul
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 4. Negation distributes over ℤ-addition (via ⊖).
------------------------------------------------------------------------

neg-⊖ : (m n : ℕ) → -ℤ (m ⊖ n) ≡ n ⊖ m
neg-⊖ m       zero    = neg-pos-as-⊖ m
neg-⊖ zero    (suc n) = refl
neg-⊖ (suc m) (suc n) = neg-⊖ m n
