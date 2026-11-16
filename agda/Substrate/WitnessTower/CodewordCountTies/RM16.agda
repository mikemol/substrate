------------------------------------------------------------------------
-- Substrate.WitnessTower.CodewordCountTies.RM16
--
-- Defines: RM-1-6
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.CodewordCountTies; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.CodewordCountTies.RM16 where

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



------------------------------------------------------------------------
-- ◆AI-1c' : the REAPPEARANCE tie. The disappear/reappear (complement-8 recurs
--   at n=5) applies to the RM tie too. n=5 ceiling 2⁷ = 128 = RM(1,6)'s
--   codeword-count (dimension 7). The ceil-exp jump 5→7 IS the RM-dimension
--   jump, and the "different character" is m=4→m=6 — a DIFFERENT code, not the
--   same construction recurring. So the RM tie exhibits the same split the
--   sweep's complement does: same arithmetic (a power of 2 as codeword-count),
--   different structural home (RM(1,4) vs RM(1,6)).
------------------------------------------------------------------------

RM-1-6 : RMParams
RM-1-6 = record { m = 6 ; r = 1 }
