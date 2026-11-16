------------------------------------------------------------------------
-- The ℤ/2 seat-swap (= the detector flip).
-- Context: Substrate/WitnessTower/Wedge/PackedBridge/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.PackedBridge.Fin2Swap where

open import Substrate.Foundation.Fin.Fin

fin2-swap : Fin 2 → Fin 2
fin2-swap fzero        = fsuc fzero
fin2-swap (fsuc fzero) = fzero
