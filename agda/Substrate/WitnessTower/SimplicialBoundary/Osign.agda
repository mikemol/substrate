------------------------------------------------------------------------
-- Substrate.WitnessTower.SimplicialBoundary.Osign
--
-- Defines: osign
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SimplicialBoundary; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SimplicialBoundary.Osign where

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
open import Substrate.WitnessTower.SimplicialBoundary.DelAt
open import Substrate.WitnessTower.SimplicialBoundary.Simplicial
open import Substrate.WitnessTower.SimplicialBoundary.Boundary



------------------------------------------------------------------------
-- 4. THE ∂∘∂ CANCELLATION KERNEL. In the signed boundary ∂ = Σᵢ (−1)ⁱ delAt i,
--    the two routes to each codim-2 face are (drop suc j, then i) and (drop i,
--    then j) for i ≤ j. This is the per-generator fact the free-module UNIQUENESS
--    (the ∃!-extension: cata `eea-fold-unique` finite, `ana-unique` cofree — the
--    constructive coinduction that frees the basis from `Fin`) lifts to ∂∘∂ ≡ 0
--    on all chains: the two routes land on the SAME face (`simplicial`) with
--    OPPOSITE sign — so they cancel.
------------------------------------------------------------------------

-- the orientation sign (−1)ⁿ as a parity bit (false = +, true = −).
osign : ℕ → Bool
osign zero    = false
osign (suc n) = not (osign n)
