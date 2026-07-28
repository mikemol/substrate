------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.HomSwaps.ActHom
--
-- act-hom: full S₃-on-V₄ homomorphism property, lifted from the
-- canonical dispatcher via Z₃/Z₂ normalization.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.HomSwaps.ActHom where

import Substrate.Groups.V4.Operations as V4
import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂E
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
import Substrate.Groups.S3 as S₃
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Product using (_,_)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch.Act using (act)
open import Substrate.Groups.Actions.S3-on-V4.HomSwaps.ActHomOnCanonical
  using (act-hom-on-canonical)

act-hom : ∀ s v₁ v₂ → act s (v₁ V4.· v₂) ≡ act s v₁ V4.· act s v₂
act-hom (n , h) =
  act-hom-on-canonical (Z₃E.normalize-canonical n) (Z₂E.normalize-canonical h)
