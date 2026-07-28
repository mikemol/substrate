------------------------------------------------------------------------
-- …PhaseAdvance.Z4.Advance — advance the Z₄ phase, cycle axis fixed.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z-x-FreeCyclic-PhaseAdvance.Z4.Advance where

open import Substrate.Foundation.Product using (_,_)

import Substrate.Groups.Capabilities.xFreeCyclic.Witness as xFreeCyclicW
import Substrate.Groups.Coxeter.Cyclic.Base 3 as Z₄B
cap-Z₄ = xFreeCyclicW.cap 3



import Substrate.Groups.Coxeter.xFreeCyclicFromCapability cap-Z₄ as Z₄×F
phase-advance-Z₄ : Z₄×F.Word → Z₄×F.Word
phase-advance-Z₄ (w-p , w-c) = (Z₄B.insert Z₄B.a w-p , w-c)
