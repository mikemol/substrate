------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQConfluence.RIdxEqPIdx
--
-- Defines: RIdx≡PIdx
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQConfluence; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQConfluence.RIdxEqPIdx where

open import Substrate.Foundation.Iff
open import Substrate.Foundation.Product
import Substrate.Foundation.Product as FP   -- for the ⟡def-eq projection witnesses
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQConfluence.RIdx
open import Substrate.FUSep.FUSepQConfluence.PIdx



-- ⟡def-eq: the reduce-index and peel-index share ONE carrier (Tm × Tm)
-- definitionally — witnessed, so the diamond's two edge-types are provably one.
RIdx≡PIdx : RIdx ⇔ PIdx
RIdx≡PIdx = ⇔-refl
