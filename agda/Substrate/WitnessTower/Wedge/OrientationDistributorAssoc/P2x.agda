------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.P2x
--
-- Defines: p2x
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationDistributorAssoc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.P2x where

open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.WitnessTower.Wedge.OrientationDistributorCoherence
open import Substrate.WitnessTower.Wedge.OrientationDistributor
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.FUSep.FUSepQHexagon.Private



p2x : ∀ a a2 b c → Fin (a * (a2 * (b ℕ+ c))) → Fin (a * (a2 * b) ℕ+ a * (a2 * c))
p2x a a2 b c x =
  δ a (a2 * b) (a2 * c) ((_⊗map_ {a} {a2 * (b ℕ+ c)} {a} {a2 * b ℕ+ a2 * c} (λ y → y) (δ a2 b c)) x)
