------------------------------------------------------------------------
-- Substrate.Groups.Capabilities.Strict2Monoid
--
-- Tier 2 capability record for the Coxeter-as-Strict2Monoid lift
-- (Substrate.Groups.Zn-Coxeter-Strict2Monoid's parameter list).
--
-- Every Coxeter Word framework instance shares: _++_, [] (= ε),
-- ++-identity-left, ++-identity-right. Only Gen, ++-assoc, normalize,
-- normalize-distrib vary per Zₙ. `from-coxeter-data` packages the
-- shared shape; per-Zₙ witnesses are one-line applications.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Capabilities.Strict2Monoid where

open import Substrate.Foundation.Eq using (_≡_)

------------------------------------------------------------------------
-- The capability record. (Defined before opening Coxeter.Word to
-- avoid the `Word` field-vs-type-name clash.)
------------------------------------------------------------------------

record Strict2MonoidCapability : Set₁ where
  field
    Word              : Set
    _++_              : Word → Word → Word
    ε                 : Word
    ++-assoc          : (a b c : Word) → (a ++ b) ++ c ≡ a ++ (b ++ c)
    ++-identityˡ      : (a : Word) → ε ++ a ≡ a
    ++-identityʳ      : (a : Word) → a ++ ε ≡ a
    normalize         : Word → Word
    normalize-distrib : (a b : Word) →
                        normalize (a ++ b) ≡
                        normalize (normalize a ++ normalize b)

------------------------------------------------------------------------
-- from-coxeter-data: build a Strict2MonoidCapability from a Coxeter
-- instance's per-Zₙ data. Captures every shared field once.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.Word as CW
  using (_++_; ++-identity-left; ++-identity-right)

from-coxeter-data :
  (Gen : Set)
  (++-assoc : (a b c : CW.Word Gen) → (a ++ b) ++ c ≡ a ++ (b ++ c))
  (normalize : CW.Word Gen → CW.Word Gen)
  (normalize-distrib : (a b : CW.Word Gen) →
                       normalize (a ++ b) ≡
                       normalize (normalize a ++ normalize b)) →
  Strict2MonoidCapability
from-coxeter-data Gen assoc norm distrib = record
  { Word              = CW.Word Gen
  ; _++_              = _++_
  ; ε                 = CW.[]
  ; ++-assoc          = assoc
  ; ++-identityˡ      = ++-identity-left
  ; ++-identityʳ      = ++-identity-right
  ; normalize         = norm
  ; normalize-distrib = distrib
  }

------------------------------------------------------------------------
-- Per-Zₙ witnesses, one line each.
------------------------------------------------------------------------

import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.Z4-Coxeter as Z₄
import Substrate.Groups.Z5-Coxeter as Z₅
import Substrate.Groups.Z7-Coxeter as Z₇

cap-Z₂ = from-coxeter-data Z₂.Gen Z₂.++-assoc Z₂.normalize Z₂.normalize-distrib
cap-Z₃ = from-coxeter-data Z₃.Gen Z₃.++-assoc Z₃.normalize Z₃.normalize-distrib
cap-Z₄ = from-coxeter-data Z₄.Gen Z₄.++-assoc Z₄.normalize Z₄.normalize-distrib
cap-Z₅ = from-coxeter-data Z₅.Gen Z₅.++-assoc Z₅.normalize Z₅.normalize-distrib
cap-Z₇ = from-coxeter-data Z₇.Gen Z₇.++-assoc Z₇.normalize Z₇.normalize-distrib
