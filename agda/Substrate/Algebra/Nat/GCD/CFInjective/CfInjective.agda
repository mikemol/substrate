------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.CFInjective.CfInjective
--
-- Defines: cf-injective
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.GCD.CFInjective; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.CFInjective.CfInjective where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.List
open import Substrate.Foundation.Product
open import Substrate.Algebra.Nat.GCD.Wedge
open import Substrate.Algebra.Nat.GCD.EEATrace
open import Substrate.Algebra.Wedge.Shape
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.Nat.GCD.CFInjective.ConsHead
open import Substrate.Algebra.Nat.GCD.CFInjective.ConsTail



cf-injective :
  {n₁ b₁ n₂ b₂ : ℕ}
  (t₁ : EEATrace n₁ b₁ 1) (t₂ : EEATrace n₂ b₂ 1) →
  ℕ-shape t₁ ≡ ℕ-shape t₂ → (n₁ ≡ n₂) × (b₁ ≡ b₂)
cf-injective (base _)          (base _)          _        = refl , refl
cf-injective (base _)          (step d' w₂ sub₂) ()
cf-injective (step b' w₁ sub₁) (base _)          ()
cf-injective (step b' w₁ sub₁) (step d' w₂ sub₂) shape-eq =
  n-eq , db-eq
  where
    ih      = cf-injective sub₁ sub₂ (∷-tail shape-eq)
    head-eq = ∷-head shape-eq                 -- quotient w₁ ≡ quotient w₂
    db-eq   = proj₁ ih                         -- suc b' ≡ suc d'
    rem-eq  = proj₂ ih                         -- remainder w₁ ≡ remainder w₂
    n-eq    = trans (wedge-eq w₁)
              (trans (cong₂ _ℕ+_ (cong₂ _*_ head-eq db-eq) rem-eq)
                     (sym (wedge-eq w₂)))
