------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQConfluence.CompEqid
--
-- Defines: σ∘σ≡id
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQConfluence; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQConfluence.CompEqid where

open import Substrate.Foundation.Product
import Substrate.Foundation.Product as FP   -- for the ⟡def-eq projection witnesses
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQConfluence.Iso
open import Substrate.FUSep.FUSepQConfluence.RIdx
open import Substrate.FUSep.FUSepQConfluence.PIdx
open import Substrate.FUSep.FUSepQConfluence.Op



σ∘σ≡id : (b : RIdx × PIdx) → fwd σ (fwd σ b) ≡ b
σ∘σ≡id b = refl
