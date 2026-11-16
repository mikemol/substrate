------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Mul.SwapMul
--
-- Defines: swap-mul
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Mul; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Mul.SwapMul where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Mul.TimesComm
open import Substrate.Foundation.Nat.Properties.Mul.TimesAssoc
open import Substrate.Foundation.Nat.Properties.Mul.Quad
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans



-- Middle-swap of a right-nested triple product: a·(b·c) ≡ b·(a·c). The
-- three-factor analogue of *-comm — reassociate, swap the outer pair,
-- reassociate back. (quad is the four-factor interchange; this is three.)
swap-mul : (a b c : ℕ) → a * (b * c) ≡ b * (a * c)
swap-mul a b c =
  trans (sym (*-assoc a b c))
        (trans (cong₂ _*_ (*-comm a b) refl) (*-assoc b a c))
