------------------------------------------------------------------------
-- Substrate.Algebra.Nat.DivMod.Unique
--
-- Uniqueness of the Euclidean quotient/remainder:
--
--   divmod-unique : r₁ < suc b → r₂ < suc b →
--                   q₁ * suc b + r₁ ≡ q₂ * suc b + r₂ →
--                   (q₁ ≡ q₂) × (r₁ ≡ r₂)
--
-- Stated abstractly on the reconstruction equation (NOT by unfolding
-- `_div-suc_`/`_mod-suc_`), so it composes against any source of the
-- equation — in particular against a `Wedge`'s `wedge-eq`. This is the
-- arithmetic core of "same value ⟹ same first quotient", the head-step of
-- continued-fraction value-invariance.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.DivMod.Unique where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_; _≤_; _<_)
open import Substrate.Foundation.Nat.Properties.Add using (+-assoc)
open import Substrate.Foundation.Nat.Properties.Cancel using (+-cancelˡ)
open import Substrate.Foundation.Nat.Properties.Order using (<-irrefl; ≤-trans; m≤m+n)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; subst)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)

private
  -- A remainder r < suc b cannot equal `suc b + Y` — that exceeds the bound.
  no-wrap : (b Y r : ℕ) → r ≡ suc b + Y → r < suc b → ⊥
  no-wrap b Y r eq lt =
    <-irrefl (suc b + Y)
      (≤-trans (subst (λ z → suc z ≤ suc b) eq lt) (m≤m+n (suc b) Y))

divmod-unique :
  (q₁ q₂ r₁ r₂ b : ℕ) →
  r₁ < suc b → r₂ < suc b →
  q₁ * suc b + r₁ ≡ q₂ * suc b + r₂ →
  (q₁ ≡ q₂) × (r₁ ≡ r₂)
divmod-unique zero     zero     r₁ r₂ b _   _   eq = refl , eq
divmod-unique zero     (suc q₂) r₁ r₂ b lt₁ _   eq =
  ⊥-elim (no-wrap b (q₂ * suc b + r₂) r₁
            (trans eq (+-assoc (suc b) (q₂ * suc b) r₂)) lt₁)
divmod-unique (suc q₁) zero     r₁ r₂ b _   lt₂ eq =
  ⊥-elim (no-wrap b (q₁ * suc b + r₁) r₂
            (trans (sym eq) (+-assoc (suc b) (q₁ * suc b) r₁)) lt₂)
divmod-unique (suc q₁) (suc q₂) r₁ r₂ b lt₁ lt₂ eq =
  let eq' : q₁ * suc b + r₁ ≡ q₂ * suc b + r₂
      eq' = +-cancelˡ (suc b)
              (trans (sym (+-assoc (suc b) (q₁ * suc b) r₁))
                     (trans eq (+-assoc (suc b) (q₂ * suc b) r₂)))
      ih  = divmod-unique q₁ q₂ r₁ r₂ b lt₁ lt₂ eq'
  in cong suc (proj₁ ih) , proj₂ ih
