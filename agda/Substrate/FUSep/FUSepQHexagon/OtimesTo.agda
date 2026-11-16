------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQHexagon.OtimesTo
--
-- Defines: _⊗→_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQHexagon; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQHexagon.OtimesTo where

open import Substrate.Foundation.Product
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQHexagon.P1
open import Substrate.FUSep.FUSepQHexagon.P2



-- functorial action of ⊗ on index MAPS (Wedge/Monoidal._⊗ᵇ_): componentwise.
_⊗→_ : {X X' Y Y' : Set} → (X → X') → (Y → Y') → (X × Y) → (X' × Y')
(f ⊗→ g) xy = f (p₁ xy) , g (p₂ xy)
