------------------------------------------------------------------------
-- Substrate.WitnessTower.SimplicialBoundary.NotXorL
--
-- Defines: not-xorˡ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SimplicialBoundary; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SimplicialBoundary.NotXorL where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Not
open import Substrate.Foundation.Bool.Xor
open import Substrate.Foundation.Bool.Properties.XorComm
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans
open import Substrate.WitnessTower.SimplicialBoundary.Private



-- sign of a composed pair of drops = parity of the position-sum = the xor.
not-xorˡ : (a b : Bool) → (not a) xor b ≡ not (a xor b)
not-xorˡ false b     = refl
not-xorˡ true  false = refl
not-xorˡ true  true  = refl
