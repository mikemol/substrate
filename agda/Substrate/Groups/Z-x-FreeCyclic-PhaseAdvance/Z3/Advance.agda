------------------------------------------------------------------------
-- …PhaseAdvance.Z3.Advance — advance the Z₃ phase, cycle axis fixed.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z-x-FreeCyclic-PhaseAdvance.Z3.Advance where

open import Substrate.Foundation.Product using (_,_)

import Substrate.Groups.Capabilities.xFreeCyclic.Witness as xFreeCyclicW
import Substrate.Groups.Coxeter.Cyclic.Base 2 as Z₃B
cap-Z₃ = xFreeCyclicW.cap 2



import Substrate.Groups.Coxeter.xFreeCyclicFromCapability cap-Z₃ as Z₃×F
phase-advance-Z₃ : Z₃×F.Word → Z₃×F.Word
phase-advance-Z₃ (w-p , w-c) = (Z₃B.insert Z₃B.a w-p , w-c)
