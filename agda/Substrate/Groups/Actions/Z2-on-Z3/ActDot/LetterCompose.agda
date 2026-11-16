------------------------------------------------------------------------
-- act-letter composes over normalised Z/2 concatenation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.ActDot.LetterCompose where

-- ⚑ `InvCanonical.InvInv` DISSOLVED (771283c8) — `inv-inv-canonical-ex` is
-- `InvInvCanonicalEx`'s; and `normalize` is `ListPresentation`'s, not
-- `Existential`'s, so the Z₂ instance is applied explicitly here (Ⓐ¹³).
import Substrate.Groups.Coxeter.Cyclic.Base 1 as Z₂B
import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂E
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
import Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv.InvInvCanonicalEx 2 as Z₃II
import Substrate.Groups.Coxeter.ListPresentation
  Z₂B.Gen Z₂E.Canonical-ex Z₂E.c-ε Z₂B.insert Z₂E.insert-canonical-ex as Z₂LP
open import Substrate.Groups.Coxeter.Word using (_++_)
open import Substrate.Foundation.Fin.Literals using (₁)
open import Substrate.Foundation.Fin.Fin

open import Substrate.Groups.Actions.Z2-on-Z3.Act using (act-letter)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym

act-letter-compose :
  ∀ {h₁ h₂} (c₁ : Z₂E.Canonical-ex h₁) (c₂ : Z₂E.Canonical-ex h₂)
    {x} (c-x : Z₃E.Canonical-ex x) →
  act-letter (Z₂LP.normalize (h₁ ++ h₂)) x ≡
  act-letter h₁ (act-letter h₂ x)
act-letter-compose (Z₂E.c-pos zero) (Z₂E.c-pos zero) c-x = refl
act-letter-compose (Z₂E.c-pos zero) (Z₂E.c-pos ₁) c-x = refl
act-letter-compose (Z₂E.c-pos ₁) (Z₂E.c-pos zero) {x} c-x = refl
act-letter-compose (Z₂E.c-pos ₁) (Z₂E.c-pos ₁) {x} c-x =
  sym (Z₃II.inv-inv-canonical-ex c-x)
