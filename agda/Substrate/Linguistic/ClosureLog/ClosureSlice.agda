------------------------------------------------------------------------
-- Substrate.Linguistic.ClosureLog.ClosureSlice
--
-- Defines: ClosureSlice, D1, D10, D2, D3, D4, D5, D6, D7, D8, D9
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.ClosureLog; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.ClosureLog.ClosureSlice where




------------------------------------------------------------------------
-- 2. ClosureSlice enum.
--
-- The ten D-arc slices, each closing exactly one deferred item.
------------------------------------------------------------------------

data ClosureSlice : Set where
  D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 : ClosureSlice
