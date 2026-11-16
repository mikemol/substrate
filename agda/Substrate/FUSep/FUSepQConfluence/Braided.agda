------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQConfluence.Braided
--
-- Defines: Braided
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQConfluence; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQConfluence.Braided where

open import Substrate.Foundation.Product
import Substrate.Foundation.Product as FP   -- for the ⟡def-eq projection witnesses
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQConfluence.RIdx
open import Substrate.FUSep.FUSepQConfluence.PIdx


-- THE BRAIDED PAIR: a node carrying BOTH a reduce-index and a peel-index. The
-- tensor RIdx ⊗ PIdx over the product carrier (Wedge/Monoidal: product carrier,
-- componentwise). The two hierarchical indexes, on one bucket.
Braided : Set
Braided = RIdx × PIdx
