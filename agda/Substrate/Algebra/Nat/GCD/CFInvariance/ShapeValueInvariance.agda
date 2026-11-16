------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.CFInvariance.ShapeValueInvariance
--
-- Defines: shape-value-invariance
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.GCD.CFInvariance; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.CFInvariance.ShapeValueInvariance where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Mul
open import Substrate.Foundation.Nat.Properties.Order
open import Substrate.Foundation.Product
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.List
open import Substrate.Algebra.Nat.GCD.Wedge
open import Substrate.Algebra.Nat.GCD.EEATrace
open import Substrate.Algebra.Nat.DivMod.Unique.DivmodUnique
open import Substrate.Algebra.Nat.DivMod.Unique.Private
open import Substrate.Algebra.Wedge.Shape
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Nat.GCD.CFInvariance.Private
open import Substrate.Algebra.Nat.GCD.CFInvariance.PosTimesPos
open import Substrate.Algebra.Nat.GCD.CFInvariance.DivmodCross



------------------------------------------------------------------------
-- L4: continued-fraction value-invariance (KEYSTONE #1).
------------------------------------------------------------------------

shape-value-invariance :
  {a b c d g₁ g₂ : ℕ} (t₁ : EEATrace a b g₁) (t₂ : EEATrace c d g₂) →
  0 < g₁ → 0 < g₂ → a * d ≡ c * b → ℕ-shape t₁ ≡ ℕ-shape t₂
shape-value-invariance (base a)          (base c)          _    _    _   = refl
shape-value-invariance {c = c} (base a)  (step d' w₂ sub₂) pos₁ _    hyp =
  ⊥-elim (<-irrefl 0 (subst (0 <_) (trans hyp (*-zeroʳ c)) (pos-*-pos a d' pos₁)))
shape-value-invariance {a = a} (step b' w₁ sub₁) (base c)  _    pos₂ hyp =
  ⊥-elim (<-irrefl 0 (subst (0 <_) (trans (sym hyp) (*-zeroʳ a)) (pos-*-pos c b' pos₂)))
shape-value-invariance (step b' w₁ sub₁) (step d' w₂ sub₂) pos₁ pos₂ hyp =
  cong₂ _∷_ (proj₁ cross)
            (shape-value-invariance sub₁ sub₂ pos₁ pos₂ rec-hyp)
  where
    cross : (quotient w₁ ≡ quotient w₂)
          × (remainder w₁ * suc d' ≡ remainder w₂ * suc b')
    cross = divmod-cross (quotient w₁) (quotient w₂) (remainder w₁) (remainder w₂)
              b' d' (r<b w₁) (r<b w₂)
              (trans (cong (_* suc d') (sym (wedge-eq w₁)))
                     (trans hyp (cong (_* suc b') (wedge-eq w₂))))
    rec-hyp : suc b' * remainder w₂ ≡ suc d' * remainder w₁
    rec-hyp = trans (*-comm (suc b') (remainder w₂))
                    (trans (sym (proj₂ cross)) (*-comm (remainder w₁) (suc d')))
