------------------------------------------------------------------------
-- Ⓣ₂'s rung INDEX at level n: the basis-index type whose cardinality is the
-- sweep's 2ⁿ column — the tower-side reading of that column, as a TYPE.
-- Context: Substrate/WitnessTower/SnVersusTwoPowTowers/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SnVersusTwoPowTowers.T2RungIndex where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec

Ⓣ₂-rung-index : ℕ → Set
Ⓣ₂-rung-index n = Vec Bool n
