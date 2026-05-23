------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.HomRotations.HomRot2
--
-- V₄-homomorphism witness for the rotation² ([a,a], []): αγβ-cycle.
-- 16 refls via v4×v4-cover.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.HomRotations.HomRot2 where

import Substrate.Groups.V4 as V4
import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Groups.Coxeter.Word using ([]; _∷_)
open import Substrate.Foundation.Eq using (refl)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Axes using (v4×v4-cover)

open import Substrate.Groups.V4.IsHomomorphism using (IsHomomorphism)
open import Substrate.Groups.Actions.S3-on-V4.Dispatch using (act-on-canonical)

hom-rot² : IsHomomorphism (act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) [])
hom-rot² = v4×v4-cover _
  ( (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  )
