------------------------------------------------------------------------
-- Substrate.WitnessTower.SimplicialBoundary.OppSign
--
-- Defines: ∂∂-opp-sign
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SimplicialBoundary; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SimplicialBoundary.OppSign where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Not
open import Substrate.Foundation.Bool.Xor
open import Substrate.Foundation.Bool.Properties.XorComm
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans
open import Substrate.WitnessTower.SimplicialBoundary.Private
open import Substrate.WitnessTower.SimplicialBoundary.Osign
open import Substrate.WitnessTower.SimplicialBoundary.NotXorL



-- the two routes carry opposite signs (the suc on the first-dropped position
-- flips the parity; xor-commutativity aligns the two orders).
∂∂-opp-sign : (i j : ℕ) → (osign (suc j)) xor (osign i) ≡ not ((osign i) xor (osign j))
∂∂-opp-sign i j =
  trans (not-xorˡ (osign j) (osign i)) (cong not (xor-comm (osign j) (osign i)))
