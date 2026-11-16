------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCat.Properties.OrientationRigCat
--
-- Defines: orientationRigCatₛ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCat.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCat.Properties.OrientationRigCat where

open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityL
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Foundation.Nat.Properties.Mul
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal
open import Substrate.WitnessTower.Wedge.OrientationRigCat
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.WitnessTower.Wedge.OrientationRigCat.Properties.Hom
open import Substrate.WitnessTower.Wedge.OrientationRigCat.Properties.UipNat



orientationRigCatₛ : GradedRigCat Objₛ Homₛ
orientationRigCatₛ = record
  { idHom        = λ _ → refl
  ; _∘_          = λ g f → trans f g
  ; left-id      = λ { refl → refl }
  ; right-id     = λ _ → refl
  ; assoc        = λ { refl _ _ → refl }
  ; ⊕obj         = record { u = ⋆ ; _∧_ = λ _ _ → ⋆ }
  ; ⊗obj         = record { u = ⋆ ; _∧_ = λ _ _ → ⋆ }
  ; braid⊕       = λ {i} {j} _ _ → +ℕ-comm i j
  ; braid⊗       = λ {i} {j} _ _ → *-comm i j
  ; braid⊕-invol = λ {i} {j} _ _ → uipℕ (trans (+ℕ-comm i j) (+ℕ-comm j i)) refl
  ; braid⊗-invol = λ {i} {j} _ _ → uipℕ (trans (*-comm i j) (*-comm j i)) refl
  }
