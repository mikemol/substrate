------------------------------------------------------------------------
-- Substrate.Groups.Actions.Z2-on-Z3.ActHom.Hom
--
-- Each Z/2 element acts as a Z/3 group homomorphism. Relational; one
-- definition.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.ActHom.Hom where

-- ⚑ `normalize` / `normalize-canonical` ARE `ListPresentation`'s (Ⓐ¹³′).
import Substrate.Groups.Coxeter.Cyclic.Base 1 as Z₂B
import Substrate.Groups.Coxeter.Cyclic.Base 2 as Z₃B
import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂E
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
import Substrate.Groups.Coxeter.ListPresentation
  Z₂B.Gen Z₂E.Canonical-ex Z₂E.c-ε Z₂B.insert Z₂E.insert-canonical-ex as Z₂LP
import Substrate.Groups.Coxeter.ListPresentation
  Z₃B.Gen Z₃E.Canonical-ex Z₃E.c-ε Z₃B.insert Z₃E.insert-canonical-ex as Z₃LP
import Substrate.Groups.Capabilities.CoxeterGroup.Witness as CoxeterGroupW
open import Substrate.Groups.Coxeter.Word using (_++_)
open import Substrate.Groups.Actions.Z2-on-Z3.Act using (act; act-letter)
open import Substrate.Groups.Actions.Z2-on-Z3.ActHom.LetterHom using (act-letter-hom)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Generators
import Substrate.Groups.Coxeter.Cyclic.Core 2 as Z₃C
open import Substrate.Category.GaloisAdjunction
cap-Z₃ = CoxeterGroupW.cap 2



import Substrate.Groups.Coxeter.GroupFromCapability cap-Z₃ as Z₃G
act-hom : ∀ h n₁ n₂ → act h (n₁ Z₃G.· n₂) Z₃G.≈ (act h n₁ Z₃G.· act h n₂)
act-hom h n₁ n₂ =
  let
    c-h = Z₂LP.normalize-canonical h
    c-n₁ = Z₃LP.normalize-canonical n₁
    c-n₂ = Z₃LP.normalize-canonical n₂
    bridge-· : Z₃LP.normalize (n₁ Z₃G.· n₂) ≡ Z₃LP.normalize n₁ Z₃G.· Z₃LP.normalize n₂
    bridge-· = trans (Z₃C.normalize-idem (n₁ ++ n₂)) (Z₃C.normalize-distrib n₁ n₂)
  in
  trans (cong Z₃LP.normalize (cong (act-letter (Z₂LP.normalize h)) bridge-·))
        (act-letter-hom c-h c-n₁ c-n₂)
