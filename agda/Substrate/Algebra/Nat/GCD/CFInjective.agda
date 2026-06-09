------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.CFInjective
--
-- KEYSTONE #2 of the ℚ-Canonical shape route: the continued-fraction shape
-- is INJECTIVE on coprime fractions.
--
--   cf-injective :
--     (t₁ : EEATrace n₁ b₁ 1)(t₂ : EEATrace n₂ b₂ 1) →
--     ℕ-shape t₁ ≡ ℕ-shape t₂ → (n₁ ≡ n₂) × (b₁ ≡ b₂)
--
-- Coprimality is carried as the gcd index pinned to `1`. This is essential:
-- `ℕ-shape (base _) ≡ []` for EVERY first argument, so shape alone is NOT
-- injective (4/2 and 6/3 both have shape [2]). The `1` index forces a
-- terminating coprime fraction to be n/1 — when the trace bottoms out at
-- `base`, the index unifies its first argument with 1 — and threads through
-- `step` for free (the sub-trace keeps the same gcd index), so no separate
-- coprime-step lemma is needed. Mismatched base/step shapes are refuted by
-- the []-vs-∷ list-constructor clash.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.CFInjective where

open import Substrate.Foundation.Nat using (ℕ; suc; _+_; _*_)
open import Substrate.Foundation.List using (List; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong₂)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Algebra.Nat.GCD.Wedge using (quotient; remainder; wedge-eq)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace; base; step)
open import Substrate.Algebra.Wedge.Shape using (ℕ-shape)

private
  ∷-head : {x y : ℕ} {xs ys : List ℕ} → x ∷ xs ≡ y ∷ ys → x ≡ y
  ∷-head refl = refl
  ∷-tail : {x y : ℕ} {xs ys : List ℕ} → x ∷ xs ≡ y ∷ ys → xs ≡ ys
  ∷-tail refl = refl

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
              (trans (cong₂ _+_ (cong₂ _*_ head-eq db-eq) rem-eq)
                     (sym (wedge-eq w₂)))
