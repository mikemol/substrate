------------------------------------------------------------------------
-- Substrate.Groups.Actions.Z2-on-Z3.ActEpsilonN.EpsilonN
--
-- Every Z/2 element fixes Z/3's identity. Relational; one definition.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.ActEpsilonN.EpsilonN where

import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂E
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
import Substrate.Groups.Capabilities.CoxeterGroup.Witness as CoxeterGroupW
open import Substrate.Foundation.Eq using (cong)
open import Substrate.Groups.Actions.Z2-on-Z3.Act using (act)
open import Substrate.Groups.Actions.Z2-on-Z3.ActEpsilonN.LetterEpsilon
  using (act-letter-ε)
cap-Z₃ = CoxeterGroupW.cap 2



import Substrate.Groups.Coxeter.GroupFromCapability cap-Z₃ as Z₃G
act-ε-N : ∀ h → act h Z₃G.ε Z₃G.≈ Z₃G.ε
act-ε-N h =
  cong Z₃E.normalize (act-letter-ε (Z₂E.normalize-canonical h))
