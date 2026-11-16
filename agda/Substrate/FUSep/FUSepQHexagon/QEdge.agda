------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQHexagon.QEdge
--
-- Defines: qEdge
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQHexagon; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQHexagon.QEdge where

open import Substrate.Foundation.Product
open import Substrate.Foundation.Nat.Nat
open import Substrate.FUSep.FUSepQSKI    using (atom; app) renaming (Tm-QSKI to Tm-QSKI)
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQHexagon.QIdx
open import Substrate.FUSep.FUSepQHexagon.Hexagon
open import Substrate.FUSep.FUSepQHexagon.Private
open import Substrate.FUSep.FUSepQSKI


qEdge : QIdx
qEdge = a2 , a1                 -- third edge

-- the three-fold reorder is coherent (hexagon fires): both paths land the same.
