------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQHexagon.Hexagon
--
-- Defines: hexagon
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQHexagon; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQHexagon.Hexagon where

open import Substrate.Foundation.Product
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQHexagon.RIdx
open import Substrate.FUSep.FUSepQHexagon.PIdx
open import Substrate.FUSep.FUSepQHexagon.QIdx
open import Substrate.FUSep.FUSepQHexagon.Braid
open import Substrate.FUSep.FUSepQHexagon.OtimesTo
open import Substrate.FUSep.FUSepQHexagon.AssocTo
open import Substrate.FUSep.FUSepQHexagon.IdP
open import Substrate.FUSep.FUSepQHexagon.IdQ



hexagon : (rpq : (RIdx × PIdx) × QIdx)
        → assoc→ (braid (assoc→ rpq))
          ≡ (idP ⊗→ braid) (assoc→ ((braid ⊗→ idQ) rpq))
hexagon rpq = refl
