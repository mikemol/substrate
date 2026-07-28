------------------------------------------------------------------------
-- …Recovery.Z4.Embed — the zero-cycle section w ↦ (w , ε).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z-x-FreeCyclic-Recovery.Z4.Embed where

open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.Coxeter.Word using (Word)

import Substrate.Groups.Capabilities.xFreeCyclic.Witness as xFreeCyclicW
import Substrate.Groups.Coxeter.Cyclic.Base 3 as Z₄B
import Substrate.Groups.FreeCyclic-Coxeter as F
cap-Z₄ = xFreeCyclicW.cap 3



import Substrate.Groups.Coxeter.xFreeCyclicFromCapability cap-Z₄ as Z₄×F
embed-Z₄ : Word Z₄B.Gen → Z₄×F.Word
embed-Z₄ w = (w , F.ε)
