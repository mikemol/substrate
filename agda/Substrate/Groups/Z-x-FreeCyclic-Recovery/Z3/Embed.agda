------------------------------------------------------------------------
-- …Recovery.Z3.Embed — the zero-cycle section w ↦ (w , ε).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z-x-FreeCyclic-Recovery.Z3.Embed where

open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.Coxeter.Word using (Word)

import Substrate.Groups.Capabilities.xFreeCyclic.Witness as xFreeCyclicW
import Substrate.Groups.Coxeter.Cyclic.Base 2 as Z₃B
import Substrate.Groups.FreeCyclic-Coxeter as F
cap-Z₃ = xFreeCyclicW.cap 2



import Substrate.Groups.Coxeter.xFreeCyclicFromCapability cap-Z₃ as Z₃×F
embed-Z₃ : Word Z₃B.Gen → Z₃×F.Word
embed-Z₃ w = (w , F.ε)
