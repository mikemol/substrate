------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQHexagon.AssocTo
--
-- Defines: assoc→
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQHexagon; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQHexagon.AssocTo where

open import Substrate.Foundation.Product
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQHexagon.P1
open import Substrate.FUSep.FUSepQHexagon.P2



------------------------------------------------------------------------
-- THE ASSOCIATOR (product reassociation, Wedge/Monoidal.assoc→): ((a,b),c) ↦
-- (a,(b,c)) — the hierarchical re-nesting of three indexes over one bucket.
------------------------------------------------------------------------
assoc→ : {X Y Z : Set} → ((X × Y) × Z) → (X × (Y × Z))
assoc→ xyz = p₁ (p₁ xyz) , (p₂ (p₁ xyz) , p₂ xyz)
