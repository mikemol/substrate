------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQConfluence.RIdx
--
-- Defines: RIdx
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQConfluence; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQConfluence.RIdx where

open import Substrate.Foundation.Product
import Substrate.Foundation.Product as FP   -- for the ⟡def-eq projection witnesses
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
-- ⚑ Ⓑ11: `Tm⟦27e68fcc⟧` is a stripped dedup ALIAS for `FUSepQSKI.Tm`, not a
-- missing definition — see the sibling `PIdx.agda` for the full archaeology.
open import Substrate.FUSep.FUSepQSKI


RIdx = Tm-QSKI × Tm-QSKI    -- (parent, reduct)
