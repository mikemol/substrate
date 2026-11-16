------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.P2
--
-- Defines: p2
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationDistributorAssoc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.P2 where

open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.WitnessTower.Wedge.OrientationHexagon
open import Substrate.WitnessTower.Wedge.OrientationDistributor
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong



p2 : ∀ a b c d → Fin (a * (b ℕ+ (c ℕ+ d))) → Fin (a * b ℕ+ (a * c ℕ+ a * d))
p2 a b c d x = ((λ y → y) ⊕map δ a c d) (δ a b (c ℕ+ d) x)
