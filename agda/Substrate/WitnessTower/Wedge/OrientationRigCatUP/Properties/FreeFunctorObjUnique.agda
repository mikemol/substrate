------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties.FreeFunctorObjUnique
--
-- Defines: freeFunctor-obj-unique
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties.FreeFunctorObjUnique where

open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal
open import Substrate.WitnessTower.Wedge.OrientationRigCat
open import Substrate.WitnessTower.Wedge.OrientationRigCat.Properties.OrientationRigCat
open import Substrate.WitnessTower.Wedge.OrientationRigCat.Properties.UipNat
open import Substrate.WitnessTower.Wedge.OrientationRigCatUP
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2
open import Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties.FreeObj
open import Substrate.Probability.MarkovCategory



------------------------------------------------------------------------
-- THE UNIQUENESS LEMMA (general target). Any RigFunctor out of the skeletal
-- orientationRigCatₛ has its object map FORCED to freeObj by preservation:
--   n = 0     : F-obj ⋆₀ ≡ ⊕-unit T                          (F-⊕obj-u)
--   n = suc m : F-obj ⋆_{suc m} = F-obj (⋆₁ ⊕ₛ ⋆ₘ)
--             ≡ (F-obj ⋆₁) ⊕_T (F-obj ⋆ₘ)                    (F-⊕obj-∧)
--             ≡ (⊗-unit T) ⊕_T freeObj m                    (F-⊗obj-u, IH)
-- (⋆₁ = the ⊗-unit object of the skeletal source; 1 + m ≡ suc m.) NO Σ.
------------------------------------------------------------------------

freeFunctor-obj-unique :
  {Obj : ℕ → Set} {Hom : {i j : ℕ} → Obj i → Obj j → Set}
  (T : GradedRigCat Obj Hom)
  (F : RigFunctor orientationRigCatₛ T) →
  (n : ℕ) → F-obj F (⋆ {n}) ≡ freeObj T n
freeFunctor-obj-unique T F zero    = F-⊕obj-u F
freeFunctor-obj-unique T F (suc n) =
  trans (F-⊕obj-∧ F (⋆ {1}) (⋆ {n}))
        (cong₂ (_∧_ (⊕obj T)) (F-⊗obj-u F) (freeFunctor-obj-unique T F n))
