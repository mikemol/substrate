------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.SubMul.TimesSucR
--
-- Defines: *-sucʳ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.SubMul; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.SubMul.TimesSucR where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Mul.TimesComm
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans
*-sucʳ : (a b : ℕ) → a * suc b ≡ a ℕ+ a * b
*-sucʳ a b = trans (*-comm a (suc b)) (cong (a ℕ+_) (*-comm b a))
