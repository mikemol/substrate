------------------------------------------------------------------------
-- …Recovery.Z4.EmbedDot — embed is a monoid homomorphism.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z-x-FreeCyclic-Recovery.Z4.EmbedDot where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Groups.Coxeter.Word using (Word)

import Substrate.Groups.Capabilities.xFreeCyclic.Witness as xFreeCyclicW
import Substrate.Groups.Coxeter.Cyclic.Base 3 as ZB
import Substrate.Groups.Coxeter.Cyclic.Core 3 as ZCore
open import Substrate.Groups.Z-x-FreeCyclic-Recovery.Z4.Embed using (embed-Z₄)
cap = xFreeCyclicW.cap 3



import Substrate.Groups.Coxeter.xFreeCyclicFromCapability cap as ZxF
embed-Z₄-· :
  (w₁ w₂ : Word ZB.Gen) →
  embed-Z₄ (w₁ ZCore.· w₂) ≡ (embed-Z₄ w₁ ZxF.· embed-Z₄ w₂)
embed-Z₄-· w₁ w₂ = refl
