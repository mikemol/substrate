------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Divides.Trans
--
-- ∣-trans : a ∣ b → b ∣ c → a ∣ c.
-- If b = q₁ * a and c = q₂ * b, then c = (q₂ * q₁) * a via *-assoc.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Divides.Trans where

open import Substrate.Foundation.Nat using (ℕ; _*_)
open import Substrate.Foundation.Nat.Properties.Mul using (*-assoc)
open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)
open import Substrate.Algebra.Nat.Divides.Type using (_∣_; divides)

∣-trans : ∀ {a b c} → a ∣ b → b ∣ c → a ∣ c
∣-trans {a} {b} {c} (divides q₁ b≡q₁*a) (divides q₂ c≡q₂*b) =
  divides (q₂ * q₁)
    (trans c≡q₂*b
    (trans (cong (q₂ *_) b≡q₁*a)
           (sym (*-assoc q₂ q₁ a))))
