------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQHexagon.Op
--
-- Defines: _
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQHexagon; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQHexagon.Op where

open import Substrate.Foundation.Product
open import Substrate.Foundation.Nat.Nat
open import Substrate.FUSep.FUSepQSKI    using (atom; app) renaming (Tm-QSKI to Tm-QSKI)
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQHexagon.Private
open import Substrate.FUSep.FUSepQHexagon.Hexagon
open import Substrate.FUSep.FUSepQHexagon.REdge
open import Substrate.FUSep.FUSepQHexagon.PEdge
open import Substrate.FUSep.FUSepQHexagon.QEdge
open import Substrate.FUSep.FUSepQSKI


_ : hexagon ((rEdge , pEdge) , qEdge) ≡ refl
_ = refl

-- and the functorial diamond fires for a concrete further-rewrite pair.
