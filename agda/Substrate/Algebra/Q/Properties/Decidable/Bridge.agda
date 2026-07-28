------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Decidable.Bridge
--
-- reduce a ≡ reduce b ⟹ a ≈ℚ b (the bridge to the canonical form).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Decidable.Bridge where

open import Substrate.Foundation.Eq using (_≡_; sym; subst)
open import Substrate.Algebra.Q using (ℚ)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_; ≈ℚ-sym; ≈ℚ-trans)
open import Substrate.Algebra.Q.Reduce using (reduce)
open import Substrate.Algebra.Q.Properties.Reduce using (≈-reduce)

re→≈ : {a b : ℚ} → reduce a ≡ reduce b → a ≈ℚ b
re→≈ {a} {b} re =
  ≈ℚ-trans {a} {reduce a} {b} (≈-reduce a)
    (subst (λ r → r ≈ℚ b) (sym re) (≈ℚ-sym {b} {reduce b} (≈-reduce b)))
