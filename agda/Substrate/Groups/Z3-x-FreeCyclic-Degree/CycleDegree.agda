------------------------------------------------------------------------
-- Substrate.Groups.Z3-x-FreeCyclic-Degree.CycleDegree
--
-- The ℕ-grading on the cycle axis of Z₃ × FreeCyclic: read the length
-- of the second (free) component. See the folder for the laws.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-x-FreeCyclic-Degree.CycleDegree where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (_,_)

import Substrate.Groups.Capabilities.xFreeCyclic.Witness as xFreeCyclicW
import Substrate.Groups.FreeCyclic-Coxeter-Length as F-Len
cap-Z₃ = xFreeCyclicW.cap 2



import Substrate.Groups.Coxeter.xFreeCyclicFromCapability cap-Z₃ as Z₃×F
cycle-degree : Z₃×F.Word → ℕ
cycle-degree (_ , w-c) = F-Len.length-of-word w-c
