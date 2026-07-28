------------------------------------------------------------------------
-- …Recovery.Z3.EmbedDot — embed is a monoid homomorphism.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z-x-FreeCyclic-Recovery.Z3.EmbedDot where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Groups.Coxeter.Word using (Word)

import Substrate.Groups.Capabilities.xFreeCyclic.Witness as xFreeCyclicW
import Substrate.Groups.Coxeter.Cyclic.Base 2 as ZB
import Substrate.Groups.Coxeter.Cyclic.Core 2 as ZCore
open import Substrate.Groups.Z-x-FreeCyclic-Recovery.Z3.Embed using (embed-Z₃)
cap = xFreeCyclicW.cap 2



import Substrate.Groups.Coxeter.xFreeCyclicFromCapability cap as ZxF
embed-Z₃-· :
  (w₁ w₂ : Word ZB.Gen) →
  embed-Z₃ (w₁ ZCore.· w₂) ≡ (embed-Z₃ w₁ ZxF.· embed-Z₃ w₂)
embed-Z₃-· w₁ w₂ = refl
