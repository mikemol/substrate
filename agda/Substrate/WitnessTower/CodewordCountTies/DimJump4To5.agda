------------------------------------------------------------------------
-- Substrate.WitnessTower.CodewordCountTies.DimJump4To5
--
-- Defines: dim-jump-4-to-5
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.CodewordCountTies; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.CodewordCountTies.DimJump4To5 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Pow
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Product
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Category.ReedMullerHierarchy
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.Foundation.Nat.Plus
open import Substrate.WitnessTower.CodewordCountTies.RM14
open import Substrate.WitnessTower.CodewordCountTies.RM16



-- the reappearance as a DIMENSION JUMP: n=4→n=5 ceiling exponents 5→7 are the
-- RM-dimensions of RM(1,4)→RM(1,6). The tie recurs at a HIGHER m (m=4→m=6),
-- the honest "different character" of the disappear/reappear.
dim-jump-4-to-5 : (rm-dimension RM-1-4 ≡ 5) × (rm-dimension RM-1-6 ≡ 7)
dim-jump-4-to-5 = refl , refl
