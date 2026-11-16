------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.CFInvariance.DivmodCross
--
-- Defines: divmod-cross
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.GCD.CFInvariance; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.CFInvariance.DivmodCross where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Mul
open import Substrate.Foundation.Nat.Properties.Order
open import Substrate.Foundation.Product
open import Substrate.Algebra.Nat.DivMod.Unique.DivmodUnique
open import Substrate.Algebra.Nat.DivMod.Unique.Private
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Nat.GCD.CFInvariance.Private
open import Substrate.Algebra.Nat.GCD.CFInvariance.MulMonoStrict



------------------------------------------------------------------------
-- L3: the head step. Same value ⟹ same leading quotient ℕ+ tail cross-eq.
------------------------------------------------------------------------

divmod-cross :
  (q₁ q₂ r₁ r₂ b' d' : ℕ) →
  r₁ < suc b' → r₂ < suc d' →
  (q₁ * suc b' ℕ+ r₁) * suc d' ≡ (q₂ * suc d' ℕ+ r₂) * suc b' →
  (q₁ ≡ q₂) × (r₁ * suc d' ≡ r₂ * suc b')
divmod-cross q₁ q₂ r₁ r₂ b' d' lt₁ lt₂ eq =
  divmod-unique q₁ q₂ (r₁ * suc d') (r₂ * suc b') (d' ℕ+ b' * suc d')
    (mul-mono-strict r₁ b' d' lt₁)
    (subst (r₂ * suc b' <_) (*-comm (suc d') (suc b')) (mul-mono-strict r₂ d' b' lt₂))
    eq'
  where
    lhs : (q₁ * suc b' ℕ+ r₁) * suc d' ≡ q₁ * (suc b' * suc d') ℕ+ r₁ * suc d'
    lhs = trans (*-distribʳ-+ (suc d') (q₁ * suc b') r₁)
                (cong (_ℕ+ r₁ * suc d') (*-assoc q₁ (suc b') (suc d')))
    rhs : (q₂ * suc d' ℕ+ r₂) * suc b' ≡ q₂ * (suc b' * suc d') ℕ+ r₂ * suc b'
    rhs = trans (*-distribʳ-+ (suc b') (q₂ * suc d') r₂)
                (cong (_ℕ+ r₂ * suc b')
                      (trans (*-assoc q₂ (suc d') (suc b'))
                             (cong (q₂ *_) (*-comm (suc d') (suc b')))))
    eq' : q₁ * (suc b' * suc d') ℕ+ r₁ * suc d' ≡ q₂ * (suc b' * suc d') ℕ+ r₂ * suc b'
    eq' = trans (sym lhs) (trans eq rhs)
