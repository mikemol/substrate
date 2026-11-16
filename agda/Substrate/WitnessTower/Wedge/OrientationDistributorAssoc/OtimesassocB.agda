------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.OtimesassocB
--
-- Defines: δ-⊗assoc-B
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationDistributorAssoc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.OtimesassocB where

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
open import Substrate.Foundation.Fin.Inject
open import Substrate.Foundation.Fin.Combine
open import Substrate.Foundation.Fin.Combine.Assoc.ToNatCombine
open import Substrate.Foundation.Fin.Combine.Assoc.ToNatInjectPlus
open import Substrate.WitnessTower.Wedge.OrientationDistributorCoherence
open import Substrate.WitnessTower.Wedge.OrientationDistributor
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.P1x
open import Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.P2x
open import Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.ArithB
open import Substrate.FUSep.FUSepQHexagon.Private
open import Substrate.Algebra.Sporadic.HappyFamily.AsTree



-- B-block:
δ-⊗assoc-B : ∀ a a2 b c (i : Fin a) (i2 : Fin a2) (j : Fin b) →
             toℕ (p1x a a2 b c (combine (combine i i2) (inject+ c j)))
               ≡ toℕ (p2x a a2 b c (combine i (combine i2 (inject+ c j))))
δ-⊗assoc-B a a2 b c i i2 j =
  trans (trans (cong toℕ (δ-inject (a * a2) b c (combine i i2) j))
               (trans (toℕ-inject+ ((a * a2) * c) (combine (combine i i2) j))
                      (trans (toℕ-combine (combine i i2) j)
                             (cong (λ z → z * b ℕ+ toℕ j) (toℕ-combine i i2)))))
        (trans (arith-B (toℕ i) a2 (toℕ i2) b (toℕ j))
        (sym (trans (cong toℕ (trans (cong (δ a (a2 * b) (a2 * c))
                                           (trans (⊗map-combine {a} {a2 * (b ℕ+ c)} {a} {a2 * b ℕ+ a2 * c} (λ y → y) (δ a2 b c) i (combine i2 (inject+ c j)))
                                                  (cong (combine i) (δ-inject a2 b c i2 j))))
                                     (δ-inject a (a2 * b) (a2 * c) i (combine i2 j))))
                    (trans (toℕ-inject+ (a * (a2 * c)) (combine i (combine i2 j)))
                           (trans (toℕ-combine i (combine i2 j))
                                  (cong (toℕ i * (a2 * b) ℕ+_) (toℕ-combine i2 j)))))))
