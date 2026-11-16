------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQConfluence.S0
--
-- Defines: s0
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQConfluence; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQConfluence.S0 where

open import Substrate.Foundation.Product
import Substrate.Foundation.Product as FP   -- for the ⟡def-eq projection witnesses
open import Substrate.Foundation.Nat.Nat
open import Substrate.FUSep.FUSepQSKI    using (atom; app) renaming (Tm-QSKI to Tm-QSKI)
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQConfluence.Span
open import Substrate.FUSep.FUSepQConfluence.Diamond
open import Substrate.FUSep.FUSepQConfluence.Packed
open import Substrate.FUSep.FUSepQSKI



------------------------------------------------------------------------
-- CONCRETE WITNESS: a node s = app (atom 0) (atom 1) with BOTH a reduce-edge
-- (kept-parent backpointer = s) and a peel-edge (viaP = atom 0, arg = atom 1).
-- The two indexes converge on s — the diamond closes (packed … ≡ refl).
------------------------------------------------------------------------
s0 : Tm-QSKI
s0 = app (atom zero) (atom (suc zero))
