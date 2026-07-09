------------------------------------------------------------------------
-- Substrate.Groups.Capabilities.PhaseProjection
--
-- Tier 2 capability record for the Zₙ × FreeCyclic phase projection
-- (Substrate.Groups.Zn-x-FreeCyclic-PhaseProjection's parameter list).
--
-- The F (FreeCyclic) side is identical across every Zₙ instance; only
-- the Zₙ-side carrier data varies. `from-coxeter-data` packages the
-- F side once and takes the Zₙ data as parameters.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Capabilities.PhaseProjection where

open import Substrate.Groups.Coxeter.Word using (Word; _++_)
import Substrate.Groups.FreeCyclic-Coxeter as F

------------------------------------------------------------------------
-- The capability record.
------------------------------------------------------------------------

-- ⟡set1-paydown: parameterize BOTH Set carriers (Zn-Word, F-Word) out of
-- the record — they were `field`s valued in Set, forcing the record to Set₁.
-- As module parameters the record lands in Set; consumers write
-- `PhaseProjectionCapability Zn-Word F-Word`.
module _ (Zn-Word F-Word : Set) where

  record PhaseProjectionCapability : Set where
    field
      Zn-ε         : Zn-Word
      _Zn-++_      : Zn-Word → Zn-Word → Zn-Word
      Zn-normalize : Zn-Word → Zn-Word
      F-ε          : F-Word
      _F-++_       : F-Word → F-Word → F-Word
      F-normalize  : F-Word → F-Word

------------------------------------------------------------------------
-- from-coxeter-data: build the capability from a Coxeter Word instance.
-- The Zₙ side uses Coxeter.Word's `_++_` (== Z_n._++_) and `[]` (==
-- Z_n.ε), so only Gen and normalize vary across instances.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.Word using ([])

from-coxeter-data :
  (Gen : Set)
  (normalize : Word Gen → Word Gen) →
  PhaseProjectionCapability (Word Gen) (F.Word F.Gen)
from-coxeter-data Gen norm = record
  { Zn-ε         = []
  ; _Zn-++_      = _++_
  ; Zn-normalize = norm
  ; F-ε          = F.ε
  ; _F-++_       = F._++_
  ; F-normalize  = F.normalize
  }

------------------------------------------------------------------------
-- Per-Zₙ witnesses, one line each.
------------------------------------------------------------------------

import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.Z4-Coxeter as Z₄
import Substrate.Groups.Z5-Coxeter as Z₅
import Substrate.Groups.Z7-Coxeter as Z₇

cap-Z₂ = from-coxeter-data Z₂.Gen Z₂.normalize
cap-Z₃ = from-coxeter-data Z₃.Gen Z₃.normalize
cap-Z₄ = from-coxeter-data Z₄.Gen Z₄.normalize
cap-Z₅ = from-coxeter-data Z₅.Gen Z₅.normalize
cap-Z₇ = from-coxeter-data Z₇.Gen Z₇.normalize
