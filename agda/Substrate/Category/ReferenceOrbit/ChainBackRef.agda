------------------------------------------------------------------------
-- Substrate.Category.ReferenceOrbit.ChainBackRef
--
-- Z1: chain-symbol LZ77-style backref. Arbitrary recent span, one-shot, chamber-aligned.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ReferenceOrbit.ChainBackRef where

open import Substrate.Category.ReferenceOrbit.SourceClass using (ArbitraryRecentSpan)
open import Substrate.Category.ReferenceOrbit.Permanence using (OneShot)
open import Substrate.Category.ReferenceOrbit.BindingClass using (ChamberBound)
open import Substrate.Category.ReferenceOrbit.Record using (ReferenceOrbit)

ChainBackRef : ReferenceOrbit
ChainBackRef = record
  { source = ArbitraryRecentSpan
  ; permanence = OneShot
  ; binding = ChamberBound
  }
