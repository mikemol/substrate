------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQHexagon.RIdx
--
-- Defines: RIdx
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQHexagon; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQHexagon.RIdx where

open import Substrate.Foundation.Product
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
-- ⚑ Ⓑ11: `Tm⟦27e68fcc⟧` is a stripped dedup ALIAS for `FUSepQSKI.Tm`, not a
-- missing definition — see `FUSepQConfluence/PIdx.agda` for the archaeology.
open import Substrate.FUSep.FUSepQSKI


RIdx = Tm-QSKI × Tm-QSKI      -- reduce edges (parent, reduct)
