------------------------------------------------------------------------
-- ◆AI-1d, discharged: the CARDINALITY of Ⓣ₂'s rung index IS 2ⁿ, as a proved term.
-- The sweep's right column is the enumerated count of the CD basis index, not a literal.
-- Context: Substrate/WitnessTower/SnVersusTwoPowTowers/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SnVersusTwoPowTowers.T2RungCount where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Pow
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.VecBoolCardinality
open import Substrate.Foundation.Eq

Ⓣ₂-rung-count : (n : ℕ) → lengthL (allVB n) ≡ 2 ^ n
Ⓣ₂-rung-count = card-VecBool
