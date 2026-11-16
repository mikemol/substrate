------------------------------------------------------------------------
-- …Recovery.Z4.EmbedEpsilon — embed preserves the identity.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z-x-FreeCyclic-Recovery.Z4.EmbedEpsilon where


import Substrate.Groups.Capabilities.xFreeCyclic.Witness as xFreeCyclicW
import Substrate.Groups.Coxeter.Cyclic.Core 3 as ZCore
open import Substrate.Groups.Z-x-FreeCyclic-Recovery.Z4.Embed using (embed-Z₄)
open import Substrate.Foundation.Eq
cap = xFreeCyclicW.cap 3



import Substrate.Groups.Coxeter.xFreeCyclicFromCapability cap as ZxF
embed-Z₄-ε : embed-Z₄ ZCore.ε ≡ ZxF.ε
embed-Z₄-ε = refl
