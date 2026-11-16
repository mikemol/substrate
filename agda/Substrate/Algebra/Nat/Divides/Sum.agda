------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Divides.Sum
--
-- ∣m∣n⇒∣m+n : c ∣ m → c ∣ n → c ∣ (m ℕ+ n).
-- Witnesses: m = q₁ * c, n = q₂ * c → m ℕ+ n = (q₁ ℕ+ q₂) * c.
-- Proven via *-distribʳ-+ : (q₁ ℕ+ q₂) * c = q₁ * c ℕ+ q₂ * c.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Divides.Sum where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Mul using (*-distribʳ-+)
open import Substrate.Algebra.Nat.Divides.Type using (_∣_; divides)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2

∣m∣n⇒∣m+n : ∀ {c m n} → c ∣ m → c ∣ n → c ∣ (m ℕ+ n)
∣m∣n⇒∣m+n {c} {m} {n} (divides q₁ m≡q₁*c) (divides q₂ n≡q₂*c) =
  divides (q₁ ℕ+ q₂)
    (trans (cong₂ _ℕ+_ m≡q₁*c n≡q₂*c)
           (sym (*-distribʳ-+ c q₁ q₂)))
