------------------------------------------------------------------------
-- Substrate.Category.ReferenceOrbit.ChamberFreeQUOTRecent
--
-- Chamber-free variant of QUOTRecent. Reserved for future X-arc residue-runtime use.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ReferenceOrbit.ChamberFreeQUOTRecent where

open import Substrate.Category.ReferenceOrbit.SourceClass using (ArbitraryRecentSpan)
open import Substrate.Category.ReferenceOrbit.Permanence using (PermanentRule)
open import Substrate.Category.ReferenceOrbit.BindingClass using (ChamberFree)
open import Substrate.Category.ReferenceOrbit.Record using (ReferenceOrbit)

ChamberFreeQUOTRecent : ReferenceOrbit
ChamberFreeQUOTRecent = record
  { source = ArbitraryRecentSpan
  ; permanence = PermanentRule
  ; binding = ChamberFree
  }
