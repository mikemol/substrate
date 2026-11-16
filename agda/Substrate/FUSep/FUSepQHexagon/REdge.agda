------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQHexagon.REdge
--
-- Defines: rEdge
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQHexagon; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQHexagon.REdge where

open import Substrate.Foundation.Product
open import Substrate.Foundation.Nat.Nat
open import Substrate.FUSep.FUSepQSKI    using (atom; app) renaming (Tm-QSKI to Tm-QSKI)
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQHexagon.RIdx
open import Substrate.FUSep.FUSepQHexagon.Private
open import Substrate.FUSep.FUSepQSKI


rEdge : RIdx
rEdge = (app a0 a1) , a0        -- reduce: parent (app a0 a1), reduct a0
