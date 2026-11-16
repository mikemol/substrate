------------------------------------------------------------------------
-- …Recovery.Z3.EmbedEpsilon — embed preserves the identity.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z-x-FreeCyclic-Recovery.Z3.EmbedEpsilon where


import Substrate.Groups.Capabilities.xFreeCyclic.Witness as xFreeCyclicW
import Substrate.Groups.Coxeter.Cyclic.Core 2 as ZCore
open import Substrate.Groups.Z-x-FreeCyclic-Recovery.Z3.Embed using (embed-Z₃)
open import Substrate.Foundation.Eq
cap = xFreeCyclicW.cap 2



import Substrate.Groups.Coxeter.xFreeCyclicFromCapability cap as ZxF
embed-Z₃-ε : embed-Z₃ ZCore.ε ≡ ZxF.ε
embed-Z₃-ε = refl
