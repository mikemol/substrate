------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPerm.HomEq
--
-- Defines: homEq
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatPerm; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPerm.HomEq where

open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Product
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.Wedge.OrientationRigCat
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Hom
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Hom2



-- morphism equality from its two honest components (non-dependent Σ ⇒ η-pair).
-- No object arguments: Homₚ discards them, so they would be phantom metas; the
-- morphism type is literally Σ (i ≡ j) (λ _ → Perm j).
homEq : {i j : ℕ} {p p' : i ≡ j} {σ σ' : Perm j} →
        p ≡ p' → σ ≡ σ' →
        _≡_ {A = Homᵣ i j} (p , σ) (p' , σ')
homEq refl refl = refl
