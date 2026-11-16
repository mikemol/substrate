------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQHexagon.FunctorialDiamond
--
-- Defines: functorial-diamond
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQHexagon; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQHexagon.FunctorialDiamond where

open import Substrate.Foundation.Product
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQHexagon.RIdx
open import Substrate.FUSep.FUSepQHexagon.PIdx
open import Substrate.FUSep.FUSepQHexagon.Braid
open import Substrate.FUSep.FUSepQHexagon.OtimesTo
open import Substrate.FUSep.FUSepQHexagon.BraidNat
open import Substrate.FUSep.FUSepQHexagon.Hexagon



------------------------------------------------------------------------
-- THE CONFLUENCE READING (why naturality/hexagon matter here). Naturality says:
-- reordering reduce/peel is COMPATIBLE with any further map on the indices — so
-- the ADD-107 diamond is not just LOCAL, it is FUNCTORIAL (survives further
-- rewriting). Concretely: apply a further rewrite `step` to the reduce-index; the
-- braided reorder still commutes.
------------------------------------------------------------------------
functorial-diamond :
  (step : RIdx → RIdx) (keep : PIdx → PIdx) (rp : RIdx × PIdx)
  → braid ((step ⊗→ keep) rp) ≡ (keep ⊗→ step) (braid rp)
functorial-diamond step keep rp = braid-nat step keep rp
