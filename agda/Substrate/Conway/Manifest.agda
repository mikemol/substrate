------------------------------------------------------------------------
-- Substrate.Conway.Manifest
--
-- Conway / surreal-numbers arc manifest. Mirrors
-- Substrate.Groups.Manifest in shape — every Conway module compiled
-- by the substrate is reachable through this import.
--
-- Per [[surreals-term-algebra-alignment]]: the surreal arc surfaces
-- {L | R} as a substrate term-algebra; downstream consumers can
-- reach the whole arc via this manifest.
--
-- Currently wired:
--   Add                — pointwise + on (left-set, right-set) surreals
--   AsCone             — SurrealFinite (suc n) as a Cone instance
--   AsField            — Surreal-as-Field obligation record
--   IntegerEmbedding   — ℕ-via-Conway integer embedding
--   Capstone           — arc closure documentation
--
-- (Pending in scope: Conway.Mul, Conway.Inverse — once their
-- substrate-native arithmetic prerequisites land.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.Manifest where

import Substrate.Conway.Add
import Substrate.Conway.AsCone
import Substrate.Conway.AsField
import Substrate.Conway.IntegerEmbedding
import Substrate.Conway.Capstone
