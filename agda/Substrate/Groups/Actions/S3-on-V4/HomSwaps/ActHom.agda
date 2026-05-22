------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.HomSwaps.ActHom
--
-- act-hom: full S₃-on-V₄ homomorphism property, lifted from the
-- canonical dispatcher via Z₃/Z₂ normalization.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.HomSwaps.ActHom where

import Substrate.Groups.V4 as V4
open V4 using (V₄)
import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.S3 as S₃
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Product using (_,_)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch using (act)
open import Substrate.Groups.Actions.S3-on-V4.HomSwaps.ActHomOnCanonical
  using (act-hom-on-canonical)

act-hom : ∀ s v₁ v₂ → act s (v₁ V4.· v₂) ≡ act s v₁ V4.· act s v₂
act-hom (n , h) =
  act-hom-on-canonical (Z₃.normalize-canonical n) (Z₂.normalize-canonical h)
