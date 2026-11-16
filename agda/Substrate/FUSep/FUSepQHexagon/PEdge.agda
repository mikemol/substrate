------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQHexagon.PEdge
--
-- Defines: pEdge
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQHexagon; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQHexagon.PEdge where

open import Substrate.Foundation.Product
open import Substrate.Foundation.Nat.Nat
open import Substrate.FUSep.FUSepQSKI    using (atom; app) renaming (Tm-QSKI to Tm-QSKI)
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQHexagon.PIdx
open import Substrate.FUSep.FUSepQHexagon.Private
open import Substrate.FUSep.FUSepQSKI


pEdge : PIdx
pEdge = a1 , a0                 -- peel: arg a1, function a0
