------------------------------------------------------------------------
-- Substrate.Groups.Capabilities.CoxeterGroup
--
-- Tier 2 capability record for the Coxeter-as-Group lift
-- (Substrate.Groups.Coxeter.GroupAdapter's parameter list).
--
-- Every Coxeter Word instance shares the Word / _++_ / [] /
-- ++-identity-left / ++-identity-right machinery. Only Gen,
-- ++-assoc, Canonical, c-ε, normalize + normalize-canonical +
-- canonical-is-fixed + normalize-distrib, and the inv quartet
-- (inv, inv-canonical, inv-left-canonical, inv-right-canonical) vary
-- per Zₙ. `from-coxeter-data` packages the shape; per-Zₙ witnesses
-- are one-line applications.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Capabilities.CoxeterGroup where

open import Substrate.Foundation.Fin using (zero)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Groups.Coxeter.Word using (Word; _++_; [])

------------------------------------------------------------------------
-- The capability record.
------------------------------------------------------------------------

record CoxeterGroupCapability : Set₁ where
  field
    Gen                : Set
    Canonical          : Word Gen → Set
    c-ε                : Canonical []
    ++-assoc           : (a b c : Word Gen) → (a ++ b) ++ c ≡ a ++ (b ++ c)
    normalize          : Word Gen → Word Gen
    normalize-canonical : (w : Word Gen) → Canonical (normalize w)
    canonical-is-fixed : {w : Word Gen} → Canonical w → normalize w ≡ w
    normalize-distrib  : (a b : Word Gen) →
                         normalize (a ++ b) ≡
                         normalize (normalize a ++ normalize b)
    inv                : Word Gen → Word Gen
    inv-canonical      : {w : Word Gen} → Canonical w → Canonical (inv w)
    inv-left-canonical : {w : Word Gen} → Canonical w → normalize (inv w ++ w) ≡ []
    inv-right-canonical : {w : Word Gen} → Canonical w → normalize (w ++ inv w) ≡ []

------------------------------------------------------------------------
-- Per-Zₙ witnesses.
------------------------------------------------------------------------

import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.Z4-Coxeter as Z₄
import Substrate.Groups.Z5-Coxeter as Z₅
import Substrate.Groups.Z7-Coxeter as Z₇

cap-Z₂ : CoxeterGroupCapability
cap-Z₂ = record
  { Gen                = Z₂.Gen
  ; Canonical          = Z₂.Canonical
  ; c-ε                = Z₂.c-pos zero
  ; ++-assoc           = Z₂.++-assoc
  ; normalize          = Z₂.normalize
  ; normalize-canonical = Z₂.normalize-canonical
  ; canonical-is-fixed = Z₂.canonical-is-fixed
  ; normalize-distrib  = Z₂.normalize-distrib
  ; inv                = Z₂.inv
  ; inv-canonical      = Z₂.inv-canonical
  ; inv-left-canonical = Z₂.inv-left-canonical
  ; inv-right-canonical = Z₂.inv-right-canonical
  }

cap-Z₃ : CoxeterGroupCapability
cap-Z₃ = record
  { Gen                = Z₃.Gen
  ; Canonical          = Z₃.Canonical
  ; c-ε                = Z₃.c-pos zero
  ; ++-assoc           = Z₃.++-assoc
  ; normalize          = Z₃.normalize
  ; normalize-canonical = Z₃.normalize-canonical
  ; canonical-is-fixed = Z₃.canonical-is-fixed
  ; normalize-distrib  = Z₃.normalize-distrib
  ; inv                = Z₃.inv
  ; inv-canonical      = Z₃.inv-canonical
  ; inv-left-canonical = Z₃.inv-left-canonical
  ; inv-right-canonical = Z₃.inv-right-canonical
  }

cap-Z₄ : CoxeterGroupCapability
cap-Z₄ = record
  { Gen                = Z₄.Gen
  ; Canonical          = Z₄.Canonical
  ; c-ε                = Z₄.c-pos zero
  ; ++-assoc           = Z₄.++-assoc
  ; normalize          = Z₄.normalize
  ; normalize-canonical = Z₄.normalize-canonical
  ; canonical-is-fixed = Z₄.canonical-is-fixed
  ; normalize-distrib  = Z₄.normalize-distrib
  ; inv                = Z₄.inv
  ; inv-canonical      = Z₄.inv-canonical
  ; inv-left-canonical = Z₄.inv-left-canonical
  ; inv-right-canonical = Z₄.inv-right-canonical
  }

cap-Z₅ : CoxeterGroupCapability
cap-Z₅ = record
  { Gen                = Z₅.Gen
  ; Canonical          = Z₅.Canonical
  ; c-ε                = Z₅.c-pos zero
  ; ++-assoc           = Z₅.++-assoc
  ; normalize          = Z₅.normalize
  ; normalize-canonical = Z₅.normalize-canonical
  ; canonical-is-fixed = Z₅.canonical-is-fixed
  ; normalize-distrib  = Z₅.normalize-distrib
  ; inv                = Z₅.inv
  ; inv-canonical      = Z₅.inv-canonical
  ; inv-left-canonical = Z₅.inv-left-canonical
  ; inv-right-canonical = Z₅.inv-right-canonical
  }

cap-Z₇ : CoxeterGroupCapability
cap-Z₇ = record
  { Gen                = Z₇.Gen
  ; Canonical          = Z₇.Canonical
  ; c-ε                = Z₇.c-pos zero
  ; ++-assoc           = Z₇.++-assoc
  ; normalize          = Z₇.normalize
  ; normalize-canonical = Z₇.normalize-canonical
  ; canonical-is-fixed = Z₇.canonical-is-fixed
  ; normalize-distrib  = Z₇.normalize-distrib
  ; inv                = Z₇.inv
  ; inv-canonical      = Z₇.inv-canonical
  ; inv-left-canonical = Z₇.inv-left-canonical
  ; inv-right-canonical = Z₇.inv-right-canonical
  }
