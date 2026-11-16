------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQHexagon.QIdx
--
-- Defines: QIdx
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQHexagon; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQHexagon.QIdx where

open import Substrate.Foundation.Product
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
-- ⚑ Ⓑ11: `Tm⟦27e68fcc⟧` is a stripped dedup ALIAS for `FUSepQSKI.Tm`, not a
-- missing definition — see `FUSepQConfluence/PIdx.agda` for the archaeology.
open import Substrate.FUSep.FUSepQSKI


QIdx = Tm-QSKI × Tm-QSKI      -- a third index (for the hexagon's three-fold reorder)
