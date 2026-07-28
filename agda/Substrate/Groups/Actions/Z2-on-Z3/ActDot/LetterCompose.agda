------------------------------------------------------------------------
-- act-letter composes over normalised Z/2 concatenation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.ActDot.LetterCompose where

import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂E
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
import Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv 2 as Z₃II
open import Substrate.Groups.Coxeter.Word using (_++_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym)
open import Substrate.Foundation.Fin.Literals using (₁)
open import Substrate.Foundation.Fin.Fin

open import Substrate.Groups.Actions.Z2-on-Z3.Act using (act-letter)

act-letter-compose :
  ∀ {h₁ h₂} (c₁ : Z₂E.Canonical-ex h₁) (c₂ : Z₂E.Canonical-ex h₂)
    {x} (c-x : Z₃E.Canonical-ex x) →
  act-letter (Z₂E.normalize (h₁ ++ h₂)) x ≡
  act-letter h₁ (act-letter h₂ x)
act-letter-compose (Z₂E.c-pos zero) (Z₂E.c-pos zero) c-x = refl
act-letter-compose (Z₂E.c-pos zero) (Z₂E.c-pos ₁) c-x = refl
act-letter-compose (Z₂E.c-pos ₁) (Z₂E.c-pos zero) {x} c-x = refl
act-letter-compose (Z₂E.c-pos ₁) (Z₂E.c-pos ₁) {x} c-x =
  sym (Z₃II.inv-inv-canonical-ex c-x)
