------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQConfluence.Span0
--
-- Defines: span0
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQConfluence; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQConfluence.Span0 where

open import Substrate.Foundation.Product
import Substrate.Foundation.Product as FP   -- for the ⟡def-eq projection witnesses
open import Substrate.Foundation.Nat.Nat
open import Substrate.FUSep.FUSepQSKI    using (atom; app) renaming (Tm-QSKI to Tm-QSKI)
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQConfluence.Span
open import Substrate.FUSep.FUSepQConfluence.S0
open import Substrate.FUSep.FUSepQSKI


span0 : Span s0
span0 = record
  { viaR = atom zero ; viaP = atom zero
  ; rBack = s0 ; pBack = atom (suc zero)
  ; r-recon = refl ; p-recon = refl }

-- the braided pair reconstructs ONE shared node — confluence, machine-witnessed.
