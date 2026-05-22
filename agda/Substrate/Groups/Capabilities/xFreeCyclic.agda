------------------------------------------------------------------------
-- Substrate.Groups.Capabilities.xFreeCyclic
--
-- Tier 2 capability record for the Zₙ × FreeCyclic 2-D word algebra
-- (Substrate.Groups.Zn-x-FreeCyclic's parameter list).
--
-- After the canonical-is-fixed rename pass, all Zₙ field names are
-- uniform; `from-coxeter-data` takes only the per-Zₙ data. Per-Zₙ
-- witnesses are one-line applications.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Capabilities.xFreeCyclic where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Groups.Coxeter.Word using (Word; _++_)

------------------------------------------------------------------------
-- The capability record.
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
-- from-coxeter-data: build the capability from a Coxeter instance.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.Word using ([])

from-coxeter-data :
  (Gen : Set)
  (++-assoc : (a b c : Word Gen) → (a ++ b) ++ c ≡ a ++ (b ++ c))
  (Canonical : Word Gen → Set)
  (normalize : Word Gen → Word Gen)
  (normalize-canonical : (w : Word Gen) → Canonical (normalize w))
  (canonical-is-fixed : {w : Word Gen} → Canonical w → normalize w ≡ w)
  (normalize-distrib : (a b : Word Gen) →
                       normalize (a ++ b) ≡
                       normalize (normalize a ++ normalize b)) →
  xFreeCyclicCapability
from-coxeter-data Gen assoc Can norm norm-can can-fix distrib = record
  { Zn-Word                = Word Gen
  ; _Zn-++_                = _++_
  ; Zn-ε                   = []
  ; Zn-++-assoc            = assoc
  ; Zn-Canonical           = Can
  ; Zn-normalize           = norm
  ; Zn-normalize-canonical = norm-can
  ; Zn-canonical-is-fixed  = can-fix
  ; Zn-normalize-distrib   = distrib
  }

------------------------------------------------------------------------
-- Per-Zₙ witnesses, one line each (now that canonical-is-fixed is
-- uniformly named).
------------------------------------------------------------------------

import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.Z4-Coxeter as Z₄
import Substrate.Groups.Z5-Coxeter as Z₅
import Substrate.Groups.Z7-Coxeter as Z₇

cap-Z₂ = from-coxeter-data Z₂.Gen Z₂.++-assoc Z₂.Canonical Z₂.normalize
                           Z₂.normalize-canonical Z₂.canonical-is-fixed
                           Z₂.normalize-distrib
cap-Z₃ = from-coxeter-data Z₃.Gen Z₃.++-assoc Z₃.Canonical Z₃.normalize
                           Z₃.normalize-canonical Z₃.canonical-is-fixed
                           Z₃.normalize-distrib
cap-Z₄ = from-coxeter-data Z₄.Gen Z₄.++-assoc Z₄.Canonical Z₄.normalize
                           Z₄.normalize-canonical Z₄.canonical-is-fixed
                           Z₄.normalize-distrib
cap-Z₅ = from-coxeter-data Z₅.Gen Z₅.++-assoc Z₅.Canonical Z₅.normalize
                           Z₅.normalize-canonical Z₅.canonical-is-fixed
                           Z₅.normalize-distrib
cap-Z₇ = from-coxeter-data Z₇.Gen Z₇.++-assoc Z₇.Canonical Z₇.normalize
                           Z₇.normalize-canonical Z₇.canonical-is-fixed
                           Z₇.normalize-distrib
