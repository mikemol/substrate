------------------------------------------------------------------------
-- Substrate.Groups.Capabilities.PhaseProjection
--
-- Tier 2 capability record for the Zₙ × FreeCyclic phase projection
-- (Substrate.Groups.Zn-x-FreeCyclic-PhaseProjection's parameter list).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Capabilities.PhaseProjection where

------------------------------------------------------------------------
-- The capability record. Fields correspond to the Zₙ + F carrier
-- data that Zn-x-FreeCyclic-PhaseProjection asks for.
------------------------------------------------------------------------

record PhaseProjectionCapability : Set₁ where
  field
    Zn-Word      : Set
    Zn-ε         : Zn-Word
    _Zn-++_      : Zn-Word → Zn-Word → Zn-Word
    Zn-normalize : Zn-Word → Zn-Word
    F-Word       : Set
    F-ε          : F-Word
    _F-++_       : F-Word → F-Word → F-Word
    F-normalize  : F-Word → F-Word

------------------------------------------------------------------------
-- Z₃ witness.
------------------------------------------------------------------------

import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.FreeCyclic-Coxeter as F

cap-Z₃ : PhaseProjectionCapability
cap-Z₃ = record
  { Zn-Word      = Z₃.Word Z₃.Gen
  ; Zn-ε         = Z₃.ε
  ; _Zn-++_      = Z₃._++_
  ; Zn-normalize = Z₃.normalize
  ; F-Word       = F.Word F.Gen
  ; F-ε          = F.ε
  ; _F-++_       = F._++_
  ; F-normalize  = F.normalize
  }

------------------------------------------------------------------------
-- Z₄ witness.
------------------------------------------------------------------------

import Substrate.Groups.Z4-Coxeter as Z₄

cap-Z₄ : PhaseProjectionCapability
cap-Z₄ = record
  { Zn-Word      = Z₄.Word Z₄.Gen
  ; Zn-ε         = Z₄.ε
  ; _Zn-++_      = Z₄._++_
  ; Zn-normalize = Z₄.normalize
  ; F-Word       = F.Word F.Gen
  ; F-ε          = F.ε
  ; _F-++_       = F._++_
  ; F-normalize  = F.normalize
  }

------------------------------------------------------------------------
-- Z₅ witness.
------------------------------------------------------------------------

import Substrate.Groups.Z5-Coxeter as Z₅

cap-Z₅ : PhaseProjectionCapability
cap-Z₅ = record
  { Zn-Word      = Z₅.Word Z₅.Gen
  ; Zn-ε         = Z₅.ε
  ; _Zn-++_      = Z₅._++_
  ; Zn-normalize = Z₅.normalize
  ; F-Word       = F.Word F.Gen
  ; F-ε          = F.ε
  ; _F-++_       = F._++_
  ; F-normalize  = F.normalize
  }
