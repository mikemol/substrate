------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.HomRotations.HomRot
--
-- V₄-homomorphism witness for the rotation ([a], []): αβγ-cycle.
-- 16 refls via v4×v4-cover (4 inputs × 4 second-args).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.HomRotations.HomRot where

import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Groups.Coxeter.Word using ([]; _∷_)
open import Substrate.Foundation.Eq using (refl)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Axes using (v4×v4-cover)

open import Substrate.Groups.V4.IsHomomorphism using (IsHomomorphism)
open import Substrate.Groups.Actions.S3-on-V4.Dispatch using (act-on-canonical)

hom-rot : IsHomomorphism (act-on-canonical (Z₃.a ∷ []) [])
hom-rot = v4×v4-cover _
  ( (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  )
