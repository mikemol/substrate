------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.P1
--
-- Defines: p1
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationDistributorAssoc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.P1 where

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



-- the two distribution paths, on a·((b+c)+d) [p1] and a·(b+(c+d)) [p2]:
p1 : ∀ a b c d → Fin (a * ((b ℕ+ c) ℕ+ d)) → Fin ((a * b ℕ+ a * c) ℕ+ a * d)
p1 a b c d x = (δ a b c ⊕map (λ y → y)) (δ a (b ℕ+ c) d x)
