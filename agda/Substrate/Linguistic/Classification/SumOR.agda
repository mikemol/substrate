------------------------------------------------------------------------
-- Substrate.Linguistic.Classification.SumOR
--
-- Defines: _⊎-OR_, here, there
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Linguistic.Classification; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Classification.SumOR where

open import Substrate.Category.FreeOverBasis
open import Substrate.Linguistic.Roster.BasisOf
open import Substrate.Linguistic.Roster.FreeCarrierOf
open import Substrate.Linguistic.Roster.Lang
open import Substrate.Linguistic.Roster.WitnessOf
open import Substrate.Linguistic.Classification.WitnessByClass



------------------------------------------------------------------------
-- 5. Round-trip coherence: class → witness → class preserves.
--
-- For the six occupied cells, witness-by-class then class recovers
-- the original. Free-other is the documented placeholder.
------------------------------------------------------------------------

-- Substrate-native disjoint union for the round-trip statement
-- (avoids Data.Sum per [[feedback-minimize-stdlib-deps]]-strengthened).
data _⊎-OR_ (A B : Set) : Set where
  here  : A → A ⊎-OR B
  there : B → A ⊎-OR B
