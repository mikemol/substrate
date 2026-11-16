------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQHexagon.Braid
--
-- Defines: braid
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQHexagon; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQHexagon.Braid where

open import Substrate.Foundation.Product
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQHexagon.P1
open import Substrate.FUSep.FUSepQHexagon.P2


------------------------------------------------------------------------
-- THE BRAIDING braid : (X ⊗ Y) → (Y ⊗ X) — the swap (Wedge/Monoidal.braid→).
------------------------------------------------------------------------
braid : {X Y : Set} → (X × Y) → (Y × X)
braid xy = p₂ xy , p₁ xy
