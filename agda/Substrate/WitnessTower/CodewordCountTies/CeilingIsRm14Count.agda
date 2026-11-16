------------------------------------------------------------------------
-- Substrate.WitnessTower.CodewordCountTies.CeilingIsRm14Count
--
-- Defines: ceiling-is-rm14-count
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.CodewordCountTies; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.CodewordCountTies.CeilingIsRm14Count where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Pow
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Category.ReedMullerHierarchy
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.Foundation.Nat.Plus
open import Substrate.WitnessTower.CodewordCountTies.RM14



-- and it equals the sweep's ceiling value directly:
ceiling-is-rm14-count : (2 ^ 5) ≡ pow2 (rm-dimension RM-1-4)
ceiling-is-rm14-count = refl
