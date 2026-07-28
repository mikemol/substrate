------------------------------------------------------------------------
-- Substrate.Groups.Z3-x-FreeCyclic-Degree.DegreeDot
--
-- cycle-degree is a monoid homomorphism into (ℕ, +, 0).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-x-FreeCyclic-Degree.DegreeDot where

open import Substrate.Foundation.Nat using (_+_)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (_≡_; trans; cong)

import Substrate.Groups.Capabilities.xFreeCyclic.Witness as xFreeCyclicW
import Substrate.Groups.FreeCyclic-Coxeter as F
import Substrate.Groups.FreeCyclic-Coxeter-Length as F-Len
import Substrate.Groups.FreeCyclic-Coxeter-GradedMonoid as F-Grade
open import Substrate.Groups.Z3-x-FreeCyclic-Degree.CycleDegree using (cycle-degree)
cap-Z₃ = xFreeCyclicW.cap 2



import Substrate.Groups.Coxeter.xFreeCyclicFromCapability cap-Z₃ as Z₃×F
cycle-degree-· :
  (a b : Z₃×F.Word) →
  cycle-degree (a Z₃×F.· b) ≡ cycle-degree a + cycle-degree b
cycle-degree-· (_ , a₂) (_ , b₂) =
  trans
    (cong F-Len.length-of-word
          (F.canonical-is-fixed-Free (F.c-any _)))
    (F-Grade.length-distrib a₂ b₂)
