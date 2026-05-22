------------------------------------------------------------------------
-- Substrate.Category.ReferenceOrbit.QUOTRecent
--
-- QUOT-style permanent rule from an ARBITRARY recent span (not restricted to existing-rule slices). The U-arc's QUOT-stack design at full generality.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ReferenceOrbit.QUOTRecent where

open import Substrate.Category.ReferenceOrbit.SourceClass using (ArbitraryRecentSpan)
open import Substrate.Category.ReferenceOrbit.Permanence using (PermanentRule)
open import Substrate.Category.ReferenceOrbit.BindingClass using (ChamberBound)
open import Substrate.Category.ReferenceOrbit.Record using (ReferenceOrbit)

QUOTRecent : ReferenceOrbit
QUOTRecent = record
  { source = ArbitraryRecentSpan
  ; permanence = PermanentRule
  ; binding = ChamberBound
  }
