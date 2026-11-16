------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQNf.Wit
--
-- Defines: Wit, peelW, redW
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQNf; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQNf.Wit where

open import Substrate.Foundation.Nat.Nat
open import Substrate.FUSep.FUSepQBridge.Anon
open import Substrate.FUSep.FUSepQBridge.Cong
open import Substrate.FUSep.FUSepQBridge.Cong2
open import Substrate.FUSep.FUSepQBridge.Eqtrans
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQSKI



------------------------------------------------------------------------
-- THE COMMON CARRIER (HetQ/CrossMul construction): the cospan into which both
-- witness-strands embed. redW = embA (reduction), peelW = embB (peel). Orthogonal
-- ⟹ clean cross (degree ≤ 1). This is the carrier the single recon requires.
------------------------------------------------------------------------
data Wit : Set where
  redW  : Tm-QSKI → Wit    -- reduction backpointer: the parent redex, KEPT (lossy step)
  peelW : Tm-QSKI → Wit    -- peel backpointer: the argument (structure, recomputable)
