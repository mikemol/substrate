------------------------------------------------------------------------
-- Substrate.Algebra.Q.Equiv.ApproxRatTrans
--
-- Defines: ≈ℚ-trans
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q.Equiv; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Equiv.ApproxRatTrans where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Mul
open import Substrate.Algebra.Z.Properties.MulFull
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Q.Equiv.ApproxRat
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans



≈ℚ-trans : {a b c : ℚ} → a ≈ℚ b → b ≈ℚ c → a ≈ℚ c
-- Projection form (no record-match on the implicits — that triggers an
-- eta coverage-stall). H1/H2 are ASCRIBED to their explicit `≡` types (a
-- definitional coercion, since `_≈ℚ_` unfolds to that `≡`) so `cong` can read
-- their endpoints.
≈ℚ-trans {a} {b} {c} H1 H2 = *ℤ-cancelʳ-pos _ _ (den-1 b) chain
  where
    h1 : (num a *ℤ (+ suc (den-1 b))) ≡ (num b *ℤ (+ suc (den-1 a)))
    h1 = H1
    h2 : (num b *ℤ (+ suc (den-1 c))) ≡ (num c *ℤ (+ suc (den-1 b)))
    h2 = H2
    chain : (num a *ℤ (+ suc (den-1 c))) *ℤ (+ suc (den-1 b))
          ≡ (num c *ℤ (+ suc (den-1 a))) *ℤ (+ suc (den-1 b))
    chain =
      trans (*ℤ-swap₂₃ (num a) (+ suc (den-1 c)) (+ suc (den-1 b)))
      (trans (cong (_*ℤ (+ suc (den-1 c))) h1)
      (trans (*ℤ-swap₂₃ (num b) (+ suc (den-1 a)) (+ suc (den-1 c)))
      (trans (cong (_*ℤ (+ suc (den-1 a))) h2)
             (*ℤ-swap₂₃ (num c) (+ suc (den-1 b)) (+ suc (den-1 a))))))
