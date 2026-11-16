------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.ArithB
--
-- Defines: arith-B
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationDistributorAssoc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.ArithB where

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
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.FUSep.FUSepQHexagon.Private
open import Substrate.Algebra.Sporadic.HappyFamily.AsTree



-- arithmetic bridges (pure ℕ):
arith-B : ∀ i a2 i2 b j → (i * a2 ℕ+ i2) * b ℕ+ j ≡ i * (a2 * b) ℕ+ (i2 * b ℕ+ j)
arith-B i a2 i2 b j =
  trans (cong (_ℕ+ j) (*-distribʳ-+ b (i * a2) i2))
        (trans (+ℕ-assoc ((i * a2) * b) (i2 * b) j)
               (cong (_ℕ+ (i2 * b ℕ+ j)) (*-assoc i a2 b)))
