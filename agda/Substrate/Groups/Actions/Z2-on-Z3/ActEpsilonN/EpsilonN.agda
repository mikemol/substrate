------------------------------------------------------------------------
-- Substrate.Groups.Actions.Z2-on-Z3.ActEpsilonN.EpsilonN
--
-- Every Z/2 element fixes Z/3's identity. Relational; one definition.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.ActEpsilonN.EpsilonN where

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
open import Substrate.Groups.Actions.Z2-on-Z3.Act using (act)
open import Substrate.Groups.Actions.Z2-on-Z3.ActEpsilonN.LetterEpsilon
  using (act-letter-ε)
open import Substrate.Foundation.Eq.Cong
cap-Z₃ = CoxeterGroupW.cap 2



import Substrate.Groups.Coxeter.GroupFromCapability cap-Z₃ as Z₃G
act-ε-N : ∀ h → act h Z₃G.ε Z₃G.≈ Z₃G.ε
act-ε-N h =
  cong Z₃LP.normalize (act-letter-ε (Z₂LP.normalize-canonical h))
