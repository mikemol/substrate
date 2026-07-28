------------------------------------------------------------------------
-- Substrate.Groups.Actions.Z2-on-Z3.ActHom.LetterHom
--
-- act-letter distributes over Z/3's product (Z/3 is abelian, so inv is
-- a homomorphism). Relational; one definition.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.ActHom.LetterHom where

import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂E
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
import Substrate.Groups.Coxeter.Cyclic.Core 2 as Z₃C
import Substrate.Groups.Coxeter.Cyclic.Inverse 2 as Z₃I
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.Capabilities.CoxeterGroup.Witness as CoxeterGroupW
open import Substrate.Groups.Coxeter.Word using (_++_)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym)
open import Substrate.Foundation.Fin.Literals using (₁)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Groups.Actions.Z2-on-Z3.Act using (act-letter)
cap-Z₃ = CoxeterGroupW.cap 2



import Substrate.Groups.Coxeter.GroupFromCapability cap-Z₃ as Z₃G
act-letter-hom :
  ∀ {h} (c : Z₂E.Canonical-ex h)
    {n₁ n₂} (c-n₁ : Z₃E.Canonical-ex n₁) (c-n₂ : Z₃E.Canonical-ex n₂) →
  Z₃E.normalize (act-letter h (n₁ Z₃G.· n₂)) ≡
  Z₃E.normalize (act-letter h n₁ Z₃G.· act-letter h n₂)
act-letter-hom (Z₂E.c-pos zero) {n₁} {n₂} c-n₁ c-n₂ = refl
act-letter-hom (Z₂E.c-pos ₁) {n₁} {n₂} c-n₁ c-n₂ =
  trans (Z₃.inv-distrib-canonical c-n₁ c-n₂)
        (sym (Z₃C.normalize-idem (Z₃I.inv n₁ ++ Z₃I.inv n₂)))
