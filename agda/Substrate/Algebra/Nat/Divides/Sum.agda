------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Divides.Sum
--
-- ∣m∣n⇒∣m+n : c ∣ m → c ∣ n → c ∣ (m + n).
-- Witnesses: m = q₁ * c, n = q₂ * c → m + n = (q₁ + q₂) * c.
-- Proven via *-distribʳ-+ : (q₁ + q₂) * c = q₁ * c + q₂ * c.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Divides.Sum where

open import Substrate.Foundation.Nat using (ℕ; _+_; _*_)
open import Substrate.Foundation.Nat.Properties.Mul using (*-distribʳ-+)
open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong; cong₂)
open import Substrate.Algebra.Nat.Divides.Type using (_∣_; divides)

∣m∣n⇒∣m+n : ∀ {c m n} → c ∣ m → c ∣ n → c ∣ (m + n)
∣m∣n⇒∣m+n {c} {m} {n} (divides q₁ m≡q₁*c) (divides q₂ n≡q₂*c) =
  divides (q₁ + q₂)
    (trans (cong₂ _+_ m≡q₁*c n≡q₂*c)
           (sym (*-distribʳ-+ c q₁ q₂)))
