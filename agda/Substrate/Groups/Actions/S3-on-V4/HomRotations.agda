------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.HomRotations
--
-- V₄-homomorphism witnesses for the three rotation-type canonical S₃
-- elements: identity, rotation (αβγ), rotation² (αγβ). 16 refl cases
-- each.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.HomRotations where

import Substrate.Groups.V4 as V4
open V4 using (V₄; e; α; β; γ)
import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Groups.Coxeter.Word using ([]; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Axes using (v4×v4-cover)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch public

------------------------------------------------------------------------
-- ([], []) — identity.
------------------------------------------------------------------------

hom-id : ∀ v₁ v₂ →
  act-on-canonical [] [] (v₁ V4.· v₂) ≡
  act-on-canonical [] [] v₁ V4.· act-on-canonical [] [] v₂
hom-id _ _ = refl

------------------------------------------------------------------------
-- ([a], []) — rotation (αβγ).
------------------------------------------------------------------------

hom-rot : ∀ v₁ v₂ →
  act-on-canonical (Z₃.a ∷ []) [] (v₁ V4.· v₂) ≡
  act-on-canonical (Z₃.a ∷ []) [] v₁ V4.· act-on-canonical (Z₃.a ∷ []) [] v₂
hom-rot = v4×v4-cover _
  ( (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  )

------------------------------------------------------------------------
-- ([a,a], []) — rotation² (αγβ).
------------------------------------------------------------------------

hom-rot² : ∀ v₁ v₂ →
  act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) [] (v₁ V4.· v₂) ≡
  act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) [] v₁ V4.· act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) [] v₂
hom-rot² = v4×v4-cover _
  ( (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  )
