------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.HomSwaps.HomSwapAB
--
-- V₄-homomorphism witness for swap αβ ([], [a]). 16 refls via v4×v4-cover.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.HomSwaps.HomSwapAB where

import Substrate.Groups.V4 as V4
import Substrate.Groups.Z2-Coxeter as Z₂
open import Substrate.Groups.Coxeter.Word using ([]; _∷_)
open import Substrate.Foundation.Eq using (refl)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Axes using (v4×v4-cover)

open import Substrate.Groups.V4.IsHomomorphism using (IsHomomorphism)
open import Substrate.Groups.Actions.S3-on-V4.Dispatch using (act-on-canonical)

hom-swap-αβ : IsHomomorphism (act-on-canonical [] (Z₂.a ∷ []))
hom-swap-αβ = v4×v4-cover _
  ( (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  )
