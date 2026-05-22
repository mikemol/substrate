------------------------------------------------------------------------
-- Substrate.Groups.Capabilities.Strict2Monoid
--
-- Tier 2 capability record for the Coxeter-as-Strict2Monoid lift
-- (Substrate.Groups.Zn-Coxeter-Strict2Monoid's parameter list).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Capabilities.Strict2Monoid where

open import Substrate.Foundation.Eq using (_≡_)

------------------------------------------------------------------------
-- The capability record.
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
-- Z₃ / Z₄ / Z₅ witnesses.
------------------------------------------------------------------------

import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.Z4-Coxeter as Z₄
import Substrate.Groups.Z5-Coxeter as Z₅
import Substrate.Groups.Z7-Coxeter as Z₇
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _++_; ++-identity-left; ++-identity-right)

cap-Z₂ : Strict2MonoidCapability
cap-Z₂ = record
  { Word              = Word Z₂.Gen
  ; _++_              = _++_
  ; ε                 = []
  ; ++-assoc          = Z₂.++-assoc
  ; ++-identityˡ      = ++-identity-left
  ; ++-identityʳ      = ++-identity-right
  ; normalize         = Z₂.normalize
  ; normalize-distrib = Z₂.normalize-distrib
  }

cap-Z₃ : Strict2MonoidCapability
cap-Z₃ = record
  { Word              = Word Z₃.Gen
  ; _++_              = _++_
  ; ε                 = []
  ; ++-assoc          = Z₃.++-assoc
  ; ++-identityˡ      = ++-identity-left
  ; ++-identityʳ      = ++-identity-right
  ; normalize         = Z₃.normalize
  ; normalize-distrib = Z₃.normalize-distrib
  }

cap-Z₄ : Strict2MonoidCapability
cap-Z₄ = record
  { Word              = Word Z₄.Gen
  ; _++_              = _++_
  ; ε                 = []
  ; ++-assoc          = Z₄.++-assoc
  ; ++-identityˡ      = ++-identity-left
  ; ++-identityʳ      = ++-identity-right
  ; normalize         = Z₄.normalize
  ; normalize-distrib = Z₄.normalize-distrib
  }

cap-Z₅ : Strict2MonoidCapability
cap-Z₅ = record
  { Word              = Word Z₅.Gen
  ; _++_              = _++_
  ; ε                 = []
  ; ++-assoc          = Z₅.++-assoc
  ; ++-identityˡ      = ++-identity-left
  ; ++-identityʳ      = ++-identity-right
  ; normalize         = Z₅.normalize
  ; normalize-distrib = Z₅.normalize-distrib
  }

cap-Z₇ : Strict2MonoidCapability
cap-Z₇ = record
  { Word              = Word Z₇.Gen
  ; _++_              = _++_
  ; ε                 = []
  ; ++-assoc          = Z₇.++-assoc
  ; ++-identityˡ      = ++-identity-left
  ; ++-identityʳ      = ++-identity-right
  ; normalize         = Z₇.normalize
  ; normalize-distrib = Z₇.normalize-distrib
  }
