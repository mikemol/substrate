------------------------------------------------------------------------
-- Substrate.Groups.Z3-x-FreeCyclic-Degree.DegreeEpsilon
--
-- The identity has cycle-degree 0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-x-FreeCyclic-Degree.DegreeEpsilon where

open import Substrate.Foundation.Eq using (_≡_; refl)

import Substrate.Groups.Capabilities.xFreeCyclic.Witness as xFreeCyclicW
open import Substrate.Groups.Z3-x-FreeCyclic-Degree.CycleDegree using (cycle-degree)
cap-Z₃ = xFreeCyclicW.cap 2



import Substrate.Groups.Coxeter.xFreeCyclicFromCapability cap-Z₃ as Z₃×F
cycle-degree-ε : cycle-degree Z₃×F.ε ≡ 0
cycle-degree-ε = refl
