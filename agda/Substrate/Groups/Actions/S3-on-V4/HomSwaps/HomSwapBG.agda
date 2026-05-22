------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.HomSwaps.HomSwapBG
--
-- V₄-homomorphism witness for swap βγ ([a,a], [a]). 16 refls via v4×v4-cover.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.HomSwaps.HomSwapBG where

import Substrate.Groups.V4 as V4
open V4 using (V₄)
import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Groups.Coxeter.Word using ([]; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Axes using (v4×v4-cover)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch using (act-on-canonical)

hom-swap-βγ : ∀ v₁ v₂ →
  act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) (Z₂.a ∷ []) (v₁ V4.· v₂) ≡
  act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) (Z₂.a ∷ []) v₁ V4.· act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) (Z₂.a ∷ []) v₂
hom-swap-βγ = v4×v4-cover _
  ( (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  )
