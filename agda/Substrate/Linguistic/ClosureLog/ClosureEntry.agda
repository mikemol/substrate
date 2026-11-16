------------------------------------------------------------------------
-- Substrate.Linguistic.ClosureLog.ClosureEntry
--
-- Defines: ClosureEntry, item, mkEntry, slice
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.ClosureLog; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.ClosureLog.ClosureEntry where

open import Substrate.Linguistic.ClosureLog.DeferredItem
open import Substrate.Linguistic.ClosureLog.ClosureSlice



------------------------------------------------------------------------
-- 3. The ClosureEntry record.
------------------------------------------------------------------------

record ClosureEntry : Set where
  constructor mkEntry
  field
    item  : DeferredItem
    slice : ClosureSlice

open ClosureEntry public
