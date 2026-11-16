------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQConfluence.Op2
--
-- Defines: _
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQConfluence; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQConfluence.Op2 where

open import Substrate.Foundation.Product
import Substrate.Foundation.Product as FP   -- for the ⟡def-eq projection witnesses
open import Substrate.Foundation.Nat.Nat
open import Substrate.FUSep.FUSepQSKI    using (atom; app) renaming (Tm-QSKI to Tm-QSKI)
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQConfluence.Packed
open import Substrate.FUSep.FUSepQConfluence.S0
open import Substrate.FUSep.FUSepQConfluence.Span0
open import Substrate.FUSep.FUSepQSKI


_ : packed s0 span0 ≡ refl
_ = refl
