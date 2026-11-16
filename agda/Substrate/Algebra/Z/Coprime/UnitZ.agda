------------------------------------------------------------------------
-- Substrate.Algebra.Z.Coprime.UnitZ
--
-- Defines: unit-z
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.Coprime; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Coprime.UnitZ where
open import Substrate.Algebra.Z.Mul

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Z.Arithmetic
open import Substrate.Algebra.Z.Properties.MulFull
open import Substrate.Algebra.Nat.Divides.Type
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Z.Coprime.Private
open import Substrate.Algebra.Z.Coprime.NegPosNotOne


unit-z : (z : ℤ) (h : ℕ) → z *ℤ (+ h) ≡ + 1 → h ∣ 1
unit-z (+ k)    h eq = divides k (sym (+ℤ-injective eq))
unit-z (-suc k) h eq = ⊥-elim (neg-pos-not-one (suc k * h) eq)
