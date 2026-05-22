------------------------------------------------------------------------
-- Substrate.Category.ReferenceOrbit.ByteBackRef
--
-- Z2: byte-level LZ77-style backref. Operates on raw output bytes, bypassing chamber state.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ReferenceOrbit.ByteBackRef where

open import Substrate.Category.ReferenceOrbit.SourceClass using (ArbitraryRecentSpan)
open import Substrate.Category.ReferenceOrbit.Permanence using (OneShot)
open import Substrate.Category.ReferenceOrbit.BindingClass using (ChamberFree)
open import Substrate.Category.ReferenceOrbit.Record using (ReferenceOrbit)

ByteBackRef : ReferenceOrbit
ByteBackRef = record
  { source = ArbitraryRecentSpan
  ; permanence = OneShot
  ; binding = ChamberFree
  }
