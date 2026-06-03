------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Generators.RotateIsHom
--
-- The Singer rotation generator `rotate` is a V₄-homomorphism. One of
-- the TWO irreducible base Cayley facts of the S3-on-V4 hom cluster
-- (the other is swap-αβ); every canonical action's homomorphism property
-- now derives from these two by composition + iter-pow induction, rather
-- than a per-canonical 16-refl table.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Generators.RotateIsHom where

open import Substrate.Axes using (v4×v4-cover)
open import Substrate.Foundation.Eq using (refl)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.V4.IsHomomorphism using (IsHomomorphism)
open import Substrate.Groups.Actions.S3-on-V4.Generators.Rotate using (rotate)

rotate-IsHom : IsHomomorphism rotate
rotate-IsHom = v4×v4-cover _
  ( (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  )
