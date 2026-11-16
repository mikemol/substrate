------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQHexagon.Op2
--
-- Defines: _
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQHexagon; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQHexagon.Op2 where

open import Substrate.Foundation.Product
open import Substrate.Foundation.Nat.Nat
open import Substrate.FUSep.FUSepQSKI    using (atom; app) renaming (Tm-QSKI to Tm-QSKI)
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQHexagon.Private
open import Substrate.FUSep.FUSepQHexagon.FunctorialDiamond
open import Substrate.FUSep.FUSepQHexagon.REdge
open import Substrate.FUSep.FUSepQHexagon.PEdge
open import Substrate.FUSep.FUSepQHexagon.Op
open import Substrate.FUSep.FUSepQSKI


_ : functorial-diamond (λ x → x) (λ x → x) (rEdge , pEdge) ≡ refl
_ = refl
