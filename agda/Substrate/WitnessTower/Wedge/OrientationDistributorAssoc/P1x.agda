------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.P1x
--
-- Defines: p1x
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationDistributorAssoc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.P1x where

open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityL
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Foundation.Nat.Properties.Mul
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Combine
open import Substrate.WitnessTower.Wedge.OrientationDistributor
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.FUSep.FUSepQHexagon.Private



------------------------------------------------------------------------
-- δ vs ⊗-ASSOCIATIVITY (numpy-verified Laplaza-δ-⊗assoc), per-block. Distributing
-- (A⊗A')⊗(B⊕C) two ways: p1x = δ at the product grade a·a₂; p2x = (id_A ⊗ δ_{A',B,C})
-- then δ_{A, A'·B, A'·C}. Same per-block trick — the index in each association form
-- (combine (combine i i2) x  vs  combine i (combine i2 x)); both paths reduce via toℕ to
-- ℕ arithmetic (bridged by *-distribʳ / *-assoc / +ℕ-assoc). Completes 5/5.
------------------------------------------------------------------------

p1x : ∀ a a2 b c → Fin ((a * a2) * (b ℕ+ c)) → Fin ((a * a2) * b ℕ+ (a * a2) * c)
p1x a a2 b c x = δ (a * a2) b c x
