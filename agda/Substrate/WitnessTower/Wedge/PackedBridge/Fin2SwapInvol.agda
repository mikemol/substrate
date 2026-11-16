------------------------------------------------------------------------
-- The seat-swap is an involution — the ℤ/2 group law.
-- Context: Substrate/WitnessTower/Wedge/PackedBridge/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.PackedBridge.Fin2SwapInvol where

open import Substrate.Foundation.Fin.Fin
open import Substrate.WitnessTower.Wedge.PackedBridge.Fin2Swap
open import Substrate.Foundation.Eq

fin2-swap-invol : (a : Fin 2) → fin2-swap (fin2-swap a) ≡ a
fin2-swap-invol fzero        = refl
fin2-swap-invol (fsuc fzero) = refl
