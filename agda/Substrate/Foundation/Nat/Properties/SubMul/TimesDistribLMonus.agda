------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.SubMul.TimesDistribLMonus
--
-- Defines: *-distribˡ-∸
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.SubMul; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.SubMul.TimesDistribLMonus where

open import Substrate.Foundation.Nat.Monus
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Mul.TimesZeroR
open import Substrate.Foundation.Nat.Properties.SubMul.ZeroMonusn
open import Substrate.Foundation.Nat.Properties.SubMul.PlusMonusCancelL
open import Substrate.Foundation.Nat.Properties.SubMul.TimesSucR
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans



-- Multiplication distributes (on the left) over truncated subtraction.
*-distribˡ-∸ : (a b c : ℕ) → a * (b ∸ c) ≡ a * b ∸ a * c
*-distribˡ-∸ a b       zero    = sym (cong (λ z → a * b ∸ z) (*-zeroʳ a))
*-distribˡ-∸ a zero    (suc c) =
  trans (*-zeroʳ a) (sym (trans (cong (_∸ a * suc c) (*-zeroʳ a)) (0∸n (a * suc c))))
*-distribˡ-∸ a (suc b) (suc c) =
  trans (*-distribˡ-∸ a b c)
        (sym (trans (cong₂ _∸_ (*-sucʳ a b) (*-sucʳ a c))
                    (+-∸-cancelˡ a (a * b) (a * c))))
