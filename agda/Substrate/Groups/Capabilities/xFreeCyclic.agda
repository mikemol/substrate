------------------------------------------------------------------------
-- Substrate.Groups.Capabilities.xFreeCyclic
--
-- Tier 2 capability record for the Zₙ × FreeCyclic 2-D word algebra
-- (Substrate.Groups.Zn-x-FreeCyclic's parameter list).
--
-- Each Zₙ with the capability supplies the record. Missing fields →
-- typecheck errors.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Capabilities.xFreeCyclic where

open import Substrate.Foundation.Eq using (_≡_)

------------------------------------------------------------------------
-- The capability record. Fields correspond to the Zₙ-Coxeter Core
-- inputs that Zn-x-FreeCyclic asks for.
------------------------------------------------------------------------

record xFreeCyclicCapability : Set₁ where
  field
    Zn-Word              : Set
    _Zn-++_              : Zn-Word → Zn-Word → Zn-Word
    Zn-ε                 : Zn-Word
    Zn-++-assoc          : (a b c : Zn-Word) →
                           (a Zn-++ b) Zn-++ c ≡ a Zn-++ (b Zn-++ c)
    Zn-Canonical         : Zn-Word → Set
    Zn-normalize         : Zn-Word → Zn-Word
    Zn-normalize-canonical : (w : Zn-Word) → Zn-Canonical (Zn-normalize w)
    Zn-canonical-is-fixed  : {w : Zn-Word} → Zn-Canonical w → Zn-normalize w ≡ w
    Zn-normalize-distrib   : (a b : Zn-Word) →
                             Zn-normalize (a Zn-++ b) ≡
                             Zn-normalize (Zn-normalize a Zn-++ Zn-normalize b)

------------------------------------------------------------------------
-- Z₃ witness.
------------------------------------------------------------------------

import Substrate.Groups.Z3-Coxeter as Z₃

cap-Z₃ : xFreeCyclicCapability
cap-Z₃ = record
  { Zn-Word                = Z₃.Word Z₃.Gen
  ; _Zn-++_                = Z₃._++_
  ; Zn-ε                   = Z₃.ε
  ; Zn-++-assoc            = Z₃.++-assoc
  ; Zn-Canonical           = Z₃.Canonical
  ; Zn-normalize           = Z₃.normalize
  ; Zn-normalize-canonical = Z₃.normalize-canonical
  ; Zn-canonical-is-fixed  = Z₃.canonical-is-fixed-Z3
  ; Zn-normalize-distrib   = Z₃.normalize-distrib
  }

------------------------------------------------------------------------
-- Z₄ witness.
------------------------------------------------------------------------

import Substrate.Groups.Z4-Coxeter as Z₄

cap-Z₄ : xFreeCyclicCapability
cap-Z₄ = record
  { Zn-Word                = Z₄.Word Z₄.Gen
  ; _Zn-++_                = Z₄._++_
  ; Zn-ε                   = Z₄.ε
  ; Zn-++-assoc            = Z₄.++-assoc
  ; Zn-Canonical           = Z₄.Canonical
  ; Zn-normalize           = Z₄.normalize
  ; Zn-normalize-canonical = Z₄.normalize-canonical
  ; Zn-canonical-is-fixed  = Z₄.canonical-is-fixed-Z4
  ; Zn-normalize-distrib   = Z₄.normalize-distrib
  }

------------------------------------------------------------------------
-- Z₅ witness.
------------------------------------------------------------------------

import Substrate.Groups.Z5-Coxeter as Z₅

cap-Z₅ : xFreeCyclicCapability
cap-Z₅ = record
  { Zn-Word                = Z₅.Word Z₅.Gen
  ; _Zn-++_                = Z₅._++_
  ; Zn-ε                   = Z₅.ε
  ; Zn-++-assoc            = Z₅.++-assoc
  ; Zn-Canonical           = Z₅.Canonical
  ; Zn-normalize           = Z₅.normalize
  ; Zn-normalize-canonical = Z₅.normalize-canonical
  ; Zn-canonical-is-fixed  = Z₅.canonical-is-fixed-Z5
  ; Zn-normalize-distrib   = Z₅.normalize-distrib
  }
