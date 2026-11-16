------------------------------------------------------------------------
-- Substrate.WitnessTower.CodewordCountTies.Rm14CodewordCount32
--
-- Defines: rm14-codeword-count-32
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.CodewordCountTies; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.CodewordCountTies.Rm14CodewordCount32 where

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



-- THE TIE: AI-1's n=4 ceiling (2^ceil-exp 4 = 2⁵ = 32) is RM(1,4)'s codeword-count.
rm14-codeword-count-32 : pow2 (rm-dimension RM-1-4) ≡ 32
rm14-codeword-count-32 = refl
