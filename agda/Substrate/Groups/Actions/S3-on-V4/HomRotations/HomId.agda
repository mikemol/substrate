------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.HomRotations.HomId
--
-- V₄-homomorphism witness for the canonical S₃-identity ([], []).
-- 16 refls collapse to one refl since act-on-canonical [] [] is id.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.HomRotations.HomId where

open import Substrate.Groups.Coxeter.Word using ([])
open import Substrate.Foundation.Eq using (refl)

open import Substrate.Groups.V4.IsHomomorphism using (IsHomomorphism)
open import Substrate.Groups.Actions.S3-on-V4.Dispatch using (act-on-canonical)

hom-id : IsHomomorphism (act-on-canonical [] [])
hom-id _ _ = refl
