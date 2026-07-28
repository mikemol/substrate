------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationProductUnit
--
-- ⟡rig-9 — the MULTIPLICATIVE UNITS of the graded rig: 1# = the one-element ordering is
-- a two-sided unit for ⊗ (up to the *-identity grade transports). The ⊗ analog of rig-5's
-- ⊕-units.
--
--   ⊗-unit-left  : subst Perm (*-identityˡ n) (1# ⊗ σ) ≡ σ
--   ⊗-unit-right : subst Perm (*-identityʳ n) (σ ⊗ 1#) ≡ σ
--
-- toℕ route (the alternate-encoding lesson): combine with a Fin-1 factor collapses to the
-- other factor's value (combine-unitₗ/ᵣ), so pointwise every lookup has the same toℕ as
-- lookup σ, and toℕ-injective closes it.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationProductUnit where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Nat.Properties.Add using (+-identityʳ)
open import Substrate.Foundation.Nat.Properties.Mul using (*-identityˡ; *-identityʳ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Properties using (toℕ-injective)
open import Substrate.Foundation.Fin.Combine using (combine)
open import Substrate.Foundation.Fin.RemQuot using (remQuot)
open import Substrate.Foundation.Fin.Combine.CombineRemQuotInverse using (combine-remQuot)
open import Substrate.Foundation.Fin.Combine.Assoc using (toℕ-subst; toℕ-combine)
open import Substrate.Foundation.Vec using (lookup)
open import Substrate.Foundation.Vec.Properties using (lookup∘tabulate)
open import Substrate.Foundation.Product using (proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; subst)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.Decompose using (lookup-ext)
open import Substrate.WitnessTower.Wedge.OrientationProduct using (_⊗_; 1#)
open import Substrate.WitnessTower.Wedge.OrientationProductLaws using (lookup-subst-Perm)

------------------------------------------------------------------------
-- 1. helpers: any Fin 1 has toℕ 0; combine with a Fin-1 factor collapses (toℕ).
------------------------------------------------------------------------

fin1-toℕ0 : (x : Fin 1) → toℕ x ≡ zero
fin1-toℕ0 zero = refl

combine-unitₗ : ∀ {n} (x : Fin 1) (y : Fin n) → toℕ (combine x y) ≡ toℕ y
combine-unitₗ {n} x y = trans (toℕ-combine x y) (cong (λ z → z * n + toℕ y) (fin1-toℕ0 x))

combine-unitᵣ : ∀ {m} (x : Fin m) (y : Fin 1) → toℕ (combine x y) ≡ toℕ x
combine-unitᵣ x y =
  trans (toℕ-combine x y)
        (trans (cong (toℕ x * 1 +_) (fin1-toℕ0 y))
               (trans (+-identityʳ (toℕ x * 1)) (*-identityʳ (toℕ x))))

-- toℕ of a lookup under a grade-subst.
toℕ-lookup-subst : ∀ {k k'} (eq : k ≡ k') (v : Perm k) (i : Fin k') →
                   toℕ (lookup (subst Perm eq v) i) ≡ toℕ (lookup v (subst Fin (sym eq) i))
toℕ-lookup-subst eq v i =
  trans (cong toℕ (lookup-subst-Perm eq v i)) (toℕ-subst eq (lookup v (subst Fin (sym eq) i)))

------------------------------------------------------------------------
-- 2. THE UNITS. lookup-ext + toℕ-injective; the collapsing factor is 1#'s Fin-1 slot.
------------------------------------------------------------------------

⊗-unit-left : ∀ {n} (σ : Perm n) → subst Perm (*-identityˡ n) (1# ⊗ σ) ≡ σ
⊗-unit-left {n} σ = lookup-ext _ _ pt
  where
  pt : (i : Fin n) → lookup (subst Perm (*-identityˡ n) (1# ⊗ σ)) i ≡ lookup σ i
  pt i = toℕ-injective
    (trans (toℕ-lookup-subst (*-identityˡ n) (1# ⊗ σ) i)
    (trans (cong toℕ (lookup∘tabulate _ i'))
    (trans (combine-unitₗ (lookup 1# a) (lookup σ b))
           (cong (λ z → toℕ (lookup σ z)) b≡i))))
    where
    i' = subst Fin (sym (*-identityˡ n)) i
    a  = proj₁ (remQuot {1} n i')
    b  = proj₂ (remQuot {1} n i')
    b≡i : b ≡ i
    b≡i = toℕ-injective (trans (sym t) (toℕ-subst (sym (*-identityˡ n)) i))
      where
      t : toℕ i' ≡ toℕ b
      t = trans (cong toℕ (sym (combine-remQuot 1 n i'))) (combine-unitₗ a b)

⊗-unit-right : ∀ {n} (σ : Perm n) → subst Perm (*-identityʳ n) (σ ⊗ 1#) ≡ σ
⊗-unit-right {n} σ = lookup-ext _ _ pt
  where
  pt : (i : Fin n) → lookup (subst Perm (*-identityʳ n) (σ ⊗ 1#)) i ≡ lookup σ i
  pt i = toℕ-injective
    (trans (toℕ-lookup-subst (*-identityʳ n) (σ ⊗ 1#) i)
    (trans (cong toℕ (lookup∘tabulate _ i'))
    (trans (combine-unitᵣ (lookup σ a) (lookup 1# b))
           (cong (λ z → toℕ (lookup σ z)) a≡i))))
    where
    i' = subst Fin (sym (*-identityʳ n)) i
    a  = proj₁ (remQuot {n} 1 i')
    b  = proj₂ (remQuot {n} 1 i')
    a≡i : a ≡ i
    a≡i = toℕ-injective (trans (sym t) (toℕ-subst (sym (*-identityʳ n)) i))
      where
      t : toℕ i' ≡ toℕ a
      t = trans (cong toℕ (sym (combine-remQuot n 1 i'))) (combine-unitᵣ a b)
