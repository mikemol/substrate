------------------------------------------------------------------------
-- A binary digit picks a witness INSERTION SLOT (grade-aware).
-- Context: Substrate/WitnessTower/Wedge/PackedBridge/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.PackedBridge.Slot where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin

slot : {n : ℕ} → Fin 2 → Fin (suc n)
slot         fzero        = fzero
slot {zero}  (fsuc fzero) = fzero
slot {suc n} (fsuc fzero) = fsuc fzero
