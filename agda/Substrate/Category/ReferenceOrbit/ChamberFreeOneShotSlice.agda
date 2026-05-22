------------------------------------------------------------------------
-- Substrate.Category.ReferenceOrbit.ChamberFreeOneShotSlice
--
-- Chamber-free variant of OneShotSlice. Reserved for future X-arc residue-runtime use.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ReferenceOrbit.ChamberFreeOneShotSlice where

open import Substrate.Category.ReferenceOrbit.SourceClass using (ExistingRuleSlice)
open import Substrate.Category.ReferenceOrbit.Permanence using (OneShot)
open import Substrate.Category.ReferenceOrbit.BindingClass using (ChamberFree)
open import Substrate.Category.ReferenceOrbit.Record using (ReferenceOrbit)

ChamberFreeOneShotSlice : ReferenceOrbit
ChamberFreeOneShotSlice = record
  { source = ExistingRuleSlice
  ; permanence = OneShot
  ; binding = ChamberFree
  }
