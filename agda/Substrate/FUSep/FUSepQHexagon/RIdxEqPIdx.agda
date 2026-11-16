------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQHexagon.RIdxEqPIdx
--
-- Defines: RIdx≡PIdx
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQHexagon; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQHexagon.RIdxEqPIdx where

open import Substrate.Foundation.Iff
open import Substrate.Foundation.Product
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQHexagon.RIdx
open import Substrate.FUSep.FUSepQHexagon.PIdx



-- ⟡def-eq: the three index ROLES are ONE carrier (Tm × Tm) DEFINITIONALLY —
-- witnessed by refl, not merely asserted. The names carry intent; the equalities
-- carry the interchangeability the hexagon's three-fold reindexing rests on.
RIdx≡PIdx : RIdx ⇔ PIdx
RIdx≡PIdx = ⇔-refl
