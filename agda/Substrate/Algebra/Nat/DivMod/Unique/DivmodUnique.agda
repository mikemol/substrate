------------------------------------------------------------------------
-- Substrate.Algebra.Nat.DivMod.Unique.DivmodUnique
--
-- Defines: divmod-unique
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.DivMod.Unique; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.DivMod.Unique.DivmodUnique where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityL
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Foundation.Nat.Properties.Cancel
open import Substrate.Foundation.Nat.Properties.Order
open import Substrate.Foundation.Product
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Nat.DivMod.Unique.Private
open import Substrate.Algebra.Nat.DivMod.Unique.NoWrap



divmod-unique :
  (q₁ q₂ r₁ r₂ b : ℕ) →
  r₁ < suc b → r₂ < suc b →
  q₁ * suc b ℕ+ r₁ ≡ q₂ * suc b ℕ+ r₂ →
  (q₁ ≡ q₂) × (r₁ ≡ r₂)
divmod-unique zero     zero     r₁ r₂ b _   _   eq = refl , eq
divmod-unique zero     (suc q₂) r₁ r₂ b lt₁ _   eq =
  ⊥-elim (no-wrap b (q₂ * suc b ℕ+ r₂) r₁
            (trans eq (+ℕ-assoc (suc b) (q₂ * suc b) r₂)) lt₁)
divmod-unique (suc q₁) zero     r₁ r₂ b _   lt₂ eq =
  ⊥-elim (no-wrap b (q₁ * suc b ℕ+ r₁) r₂
            (trans (sym eq) (+ℕ-assoc (suc b) (q₁ * suc b) r₁)) lt₂)
divmod-unique (suc q₁) (suc q₂) r₁ r₂ b lt₁ lt₂ eq =
  let eq' : q₁ * suc b ℕ+ r₁ ≡ q₂ * suc b ℕ+ r₂
      eq' = +-cancelˡ (suc b)
              (trans (sym (+ℕ-assoc (suc b) (q₁ * suc b) r₁))
                     (trans eq (+ℕ-assoc (suc b) (q₂ * suc b) r₂)))
      ih  = divmod-unique q₁ q₂ r₁ r₂ b lt₁ lt₂ eq'
  in cong suc (proj₁ ih) , proj₂ ih
