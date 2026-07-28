------------------------------------------------------------------------
-- Substrate.Groups.Actions.Z2-on-Z3.ActHom.Hom
--
-- Each Z/2 element acts as a Z/3 group homomorphism. Relational; one
-- definition.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.ActHom.Hom where

import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂E
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
import Substrate.Groups.Coxeter.Cyclic.Core 2 as Z₃C
import Substrate.Groups.Capabilities.CoxeterGroup.Witness as CoxeterGroupW
open import Substrate.Groups.Coxeter.Word using (_++_)
open import Substrate.Foundation.Eq using (_≡_; trans; cong)
open import Substrate.Groups.Actions.Z2-on-Z3.Act using (act; act-letter)
open import Substrate.Groups.Actions.Z2-on-Z3.ActHom.LetterHom using (act-letter-hom)
cap-Z₃ = CoxeterGroupW.cap 2



import Substrate.Groups.Coxeter.GroupFromCapability cap-Z₃ as Z₃G
act-hom : ∀ h n₁ n₂ → act h (n₁ Z₃G.· n₂) Z₃G.≈ (act h n₁ Z₃G.· act h n₂)
act-hom h n₁ n₂ =
  let
    c-h = Z₂E.normalize-canonical h
    c-n₁ = Z₃E.normalize-canonical n₁
    c-n₂ = Z₃E.normalize-canonical n₂
    bridge-· : Z₃E.normalize (n₁ Z₃G.· n₂) ≡ Z₃E.normalize n₁ Z₃G.· Z₃E.normalize n₂
    bridge-· = trans (Z₃C.normalize-idem (n₁ ++ n₂)) (Z₃C.normalize-distrib n₁ n₂)
  in
  trans (cong Z₃E.normalize (cong (act-letter (Z₂E.normalize h)) bridge-·))
        (act-letter-hom c-h c-n₁ c-n₂)
