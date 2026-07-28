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
--
-- ⟡set1-paydown: parameterize Word — the carrier `Word : Set` was a
-- record FIELD, forcing the whole record to Set₁. Taking it as the
-- module parameter drops the record to Set; the consumer names it
-- (`Strict2MonoidCapability W`).
------------------------------------------------------------------------

module _ (Word : Set) where

  record Strict2MonoidCapability : Set where
    field
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
  Strict2MonoidCapability (CW.Word Gen)
from-coxeter-data Gen assoc norm distrib = record
  { _++_              = _++_
  ; ε                 = CW.[]
  ; ++-assoc          = assoc
  ; ++-identityˡ      = ++-identity-left
  ; ++-identityʳ      = ++-identity-right
  ; normalize         = norm
  ; normalize-distrib = distrib
  }
