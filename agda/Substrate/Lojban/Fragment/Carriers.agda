------------------------------------------------------------------------
-- Substrate.Lojban.Fragment.Carriers
--
-- The Sumti / Sem semantic carriers + denote / tense-sem / negate
-- shared by all worked examples. Includes the WithDenotation /
-- WithTense / WithNegation instantiations of the Gismu / Cmavo
-- submodules so example files can directly use gismu-to-selbri / PU /
-- NA.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.Fragment.Carriers where

open import Substrate.Foundation.Vec using (Vec)

open import Substrate.Lojban.Gismu using (Gismu; arity)
open import Substrate.Lojban.Cmavo using (TenseMarker; pu; ca; ba)

------------------------------------------------------------------------
-- 1. Sumti carrier — names + descriptors. Real Lojban has richer sumti
-- construction (le/lo/la articles, sub-bridi); the fragment uses
-- atomic descriptors as Sumti directly.

data Sumti : Set where
  mi       : Sumti
  do-pn    : Sumti  -- you (named with -pn suffix since `do` is reserved)
  ti       : Sumti
  ta       : Sumti
  zo-e     : Sumti  -- Lojban zo'e (unspecified)
  le-zarci : Sumti
  le-prenu : Sumti
  le-gerku : Sumti
  le-pendo : Sumti

------------------------------------------------------------------------
-- 2. Sem (semantic) carrier — records gismu + actual arguments,
-- plus tense/negation wrappers. Dependent Vec Sumti (arity g) gives
-- well-typedness: `fact` only constructs when the argument count
-- matches the gismu's arity.

data Sem : Set where
  fact   : (g : Gismu) → Vec Sumti (arity g) → Sem
  pu-of  : Sem → Sem
  ca-of  : Sem → Sem
  ba-of  : Sem → Sem
  na-of  : Sem → Sem

------------------------------------------------------------------------
-- 3. Canonical denotation: each gismu denotes its `fact` constructor.

denote : (g : Gismu) → Vec Sumti (arity g) → Sem
denote = fact

------------------------------------------------------------------------
-- 4. Tense / negation semantic operations for the cmavo wrappers.

tense-sem : TenseMarker → Sem → Sem
tense-sem pu = pu-of
tense-sem ca = ca-of
tense-sem ba = ba-of

negate : Sem → Sem
negate = na-of

------------------------------------------------------------------------
-- 5. Instantiate the WithDenotation / WithTense / WithNegation
-- submodules. Public so downstream example modules see PU / NA /
-- gismu-to-selbri directly.

open import Substrate.Lojban.Gismu
open Substrate.Lojban.Gismu.WithDenotation Sumti Sem denote public
  using (gismu-to-selbri)

open import Substrate.Lojban.Cmavo
open Substrate.Lojban.Cmavo.WithTense Sumti Sem tense-sem public
  using (PU)
open Substrate.Lojban.Cmavo.WithNegation Sumti Sem negate public
  using (NA)
