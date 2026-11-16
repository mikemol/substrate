------------------------------------------------------------------------
-- Decode a binary digit-sequence into a permutation (fold insert-at ∘ slot).
-- Context: Substrate/WitnessTower/Wedge/PackedBridge/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.PackedBridge.Decode where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.Wedge.PackedBridge.Slot

decode : {n : ℕ} → Vec (Fin 2) n → Perm n
decode []      = []
decode (a ∷ v) = insert-at (slot a) (decode v)
