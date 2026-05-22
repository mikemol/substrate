------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.HomRotations.HomId
--
-- V₄-homomorphism witness for the canonical S₃-identity ([], []).
-- 16 refls collapse to one refl since act-on-canonical [] [] is id.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.HomRotations.HomId where

import Substrate.Groups.V4 as V4
open V4 using (V₄)
open import Substrate.Groups.Coxeter.Word using ([])
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch using (act-on-canonical)

hom-id : ∀ v₁ v₂ →
  act-on-canonical [] [] (v₁ V4.· v₂) ≡
  act-on-canonical [] [] v₁ V4.· act-on-canonical [] [] v₂
hom-id _ _ = refl
