------------------------------------------------------------------------
-- At grade 1 the binary digit IS the witness slot — so the cell's ℤ/2 swap is
-- exactly the tower's S₂ slot-transposition there.
-- Context: Substrate/WitnessTower/Wedge/PackedBridge/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.PackedBridge.SlotGrade1Id where

open import Substrate.Foundation.Fin.Fin
open import Substrate.WitnessTower.Wedge.PackedBridge.Slot
open import Substrate.Foundation.Eq

slot-grade1-id : (a : Fin 2) → slot {1} a ≡ a
slot-grade1-id fzero        = refl
slot-grade1-id (fsuc fzero) = refl
