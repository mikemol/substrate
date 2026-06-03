------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Generators.SwapABIsHom
--
-- The swap generator `swap-αβ` is a V₄-homomorphism. The second of the
-- two irreducible base Cayley facts of the S3-on-V4 hom cluster (with
-- rotate-IsHom). See RotateIsHom for the structural-collapse rationale.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Generators.SwapABIsHom where

open import Substrate.Axes using (v4×v4-cover)
open import Substrate.Foundation.Eq using (refl)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.V4.IsHomomorphism using (IsHomomorphism)
open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapAB using (swap-αβ)

swap-αβ-IsHom : IsHomomorphism swap-αβ
swap-αβ-IsHom = v4×v4-cover _
  ( (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  )
