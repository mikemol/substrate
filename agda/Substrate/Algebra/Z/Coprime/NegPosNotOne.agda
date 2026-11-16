------------------------------------------------------------------------
-- Substrate.Algebra.Z.Coprime.NegPosNotOne
--
-- Defines: neg-pos-not-one
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.Coprime; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Coprime.NegPosNotOne where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Z.Properties.MulFull
open import Substrate.Algebra.Nat.Divides.Type
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Z.Coprime.Private


neg-pos-not-one : (n : ℕ) → -ℤ (+ n) ≡ + 1 → ⊥
neg-pos-not-one zero    eq with +ℤ-injective eq
... | ()
neg-pos-not-one (suc j) ()

-- A unit factor: z · (+ h) ≡ + 1 forces h ∣ 1 (so h ≡ 1).
