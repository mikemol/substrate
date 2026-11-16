------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.ArithC
--
-- Defines: arith-C
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationDistributorAssoc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.ArithC where

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


arith-C : ∀ a a2 b i i2 c l →
          (a * a2) * b ℕ+ ((i * a2 ℕ+ i2) * c ℕ+ l) ≡ a * (a2 * b) ℕ+ (i * (a2 * c) ℕ+ (i2 * c ℕ+ l))
arith-C a a2 b i i2 c l =
  trans (cong (_ℕ+ ((i * a2 ℕ+ i2) * c ℕ+ l)) (*-assoc a a2 b))
        (cong (a * (a2 * b) ℕ+_)
              (trans (cong (_ℕ+ l) (*-distribʳ-+ c (i * a2) i2))
                     (trans (cong (λ z → (z ℕ+ i2 * c) ℕ+ l) (*-assoc i a2 c))
                            (+ℕ-assoc (i * (a2 * c)) (i2 * c) l))))
