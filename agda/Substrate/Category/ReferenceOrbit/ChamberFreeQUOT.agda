------------------------------------------------------------------------
-- Substrate.Category.ReferenceOrbit.ChamberFreeQUOT
--
-- Chamber-free variant of QUOT. Reserved for future X-arc residue-runtime use.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ReferenceOrbit.ChamberFreeQUOT where

open import Substrate.Category.ReferenceOrbit.SourceClass using (ExistingRuleSlice)
open import Substrate.Category.ReferenceOrbit.Permanence using (PermanentRule)
open import Substrate.Category.ReferenceOrbit.BindingClass using (ChamberFree)
open import Substrate.Category.ReferenceOrbit.Record using (ReferenceOrbit)

ChamberFreeQUOT : ReferenceOrbit
ChamberFreeQUOT = record
  { source = ExistingRuleSlice
  ; permanence = PermanentRule
  ; binding = ChamberFree
  }
