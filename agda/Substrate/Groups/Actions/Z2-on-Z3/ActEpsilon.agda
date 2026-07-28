------------------------------------------------------------------------
-- Substrate.Groups.Actions.Z2-on-Z3.ActEpsilon
--
-- act-ε: the Z/2 identity acts trivially.
--
-- Z₂.ε = []. act [] n = act-letter [] (Z₃-Existential.normalize n) = Z₃-Existential.normalize n.
-- Outer Z₃-Existential.normalize: Z₃-Existential.normalize (Z₃-Existential.normalize n) = Z₃-Existential.normalize n (idem).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.ActEpsilon where
open import Substrate.Groups.Coxeter.Cyclic.Core 2 using (_≈_)
import Substrate.Groups.Capabilities.CoxeterGroup.Witness as CoxeterGroupW
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃-Existential
import Substrate.Groups.Coxeter.Cyclic.Core 2 as Z₃-Core
import Substrate.Groups.Z3-Coxeter-Group as Z₃G
open import Substrate.Groups.Actions.Z2-on-Z3.Act using (act)
cap-Z₂ = CoxeterGroupW.cap 1




import Substrate.Groups.Coxeter.GroupFromCapability cap-Z₂ as Z₂G-GroupFromCapability
act-ε : ∀ n → act Z₂G-GroupFromCapability.ε n ≈ n
act-ε n = Z₃-Core.normalize-idem n
