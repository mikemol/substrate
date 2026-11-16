------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.HomSwaps.ActHom
--
-- act-hom: full S₃-on-V₄ homomorphism property, lifted from the
-- canonical dispatcher via Z₃/Z₂ normalization.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.HomSwaps.ActHom where

import Substrate.Groups.V4.Operations as V4
-- ⚑ `normalize-canonical` IS `ListPresentation`'s (Ⓐ¹⁶″); the `Cyclic.Base`
-- imports are NEW, since the application needs `Gen`/`insert`.
import Substrate.Groups.Coxeter.Cyclic.Base 1 as Z₂B
import Substrate.Groups.Coxeter.Cyclic.Base 2 as Z₃B
import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂E
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
import Substrate.Groups.Coxeter.ListPresentation
  Z₂B.Gen Z₂E.Canonical-ex Z₂E.c-ε Z₂B.insert Z₂E.insert-canonical-ex as Z₂LP
import Substrate.Groups.Coxeter.ListPresentation
  Z₃B.Gen Z₃E.Canonical-ex Z₃E.c-ε Z₃B.insert Z₃E.insert-canonical-ex as Z₃LP
import Substrate.Groups.S3 as S₃
open import Substrate.Foundation.Product using (_,_)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch.Act using (act)
open import Substrate.Groups.Actions.S3-on-V4.HomSwaps.ActHomOnCanonical
  using (act-hom-on-canonical)
open import Substrate.Foundation.Eq

act-hom : ∀ s v₁ v₂ → act s (v₁ V4.· v₂) ≡ act s v₁ V4.· act s v₂
act-hom (n , h) =
  act-hom-on-canonical (Z₃LP.normalize-canonical n) (Z₂LP.normalize-canonical h)
