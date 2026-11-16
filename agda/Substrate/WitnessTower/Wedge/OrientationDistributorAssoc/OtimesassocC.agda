------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.OtimesassocC
--
-- Defines: δ-⊗assoc-C
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationDistributorAssoc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.OtimesassocC where

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
open import Substrate.Foundation.Fin.Raise
open import Substrate.Foundation.Fin.Combine
open import Substrate.Foundation.Fin.Combine.Assoc.ToNatCombine
open import Substrate.Foundation.Fin.Combine.Assoc.ToNatRaise
open import Substrate.WitnessTower.Wedge.OrientationDistributorCoherence
open import Substrate.WitnessTower.Wedge.OrientationDistributor
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.P1x
open import Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.P2x
open import Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.ArithC
open import Substrate.FUSep.FUSepQHexagon.Private
open import Substrate.Algebra.Sporadic.HappyFamily.AsTree



-- C-block:
δ-⊗assoc-C : ∀ a a2 b c (i : Fin a) (i2 : Fin a2) (l : Fin c) →
             toℕ (p1x a a2 b c (combine (combine i i2) (raise b l)))
               ≡ toℕ (p2x a a2 b c (combine i (combine i2 (raise b l))))
δ-⊗assoc-C a a2 b c i i2 l =
  trans (trans (cong toℕ (δ-raise (a * a2) b c (combine i i2) l))
               (trans (toℕ-raise ((a * a2) * b) (combine (combine i i2) l))
                      (cong ((a * a2) * b ℕ+_)
                            (trans (toℕ-combine (combine i i2) l)
                                   (cong (λ z → z * c ℕ+ toℕ l) (toℕ-combine i i2))))))
        (trans (arith-C a a2 b (toℕ i) (toℕ i2) c (toℕ l))
        (sym (trans (cong toℕ (trans (cong (δ a (a2 * b) (a2 * c))
                                           (trans (⊗map-combine {a} {a2 * (b ℕ+ c)} {a} {a2 * b ℕ+ a2 * c} (λ y → y) (δ a2 b c) i (combine i2 (raise b l)))
                                                  (cong (combine i) (δ-raise a2 b c i2 l))))
                                     (δ-raise a (a2 * b) (a2 * c) i (combine i2 l))))
                    (trans (toℕ-raise (a * (a2 * b)) (combine i (combine i2 l)))
                           (cong (a * (a2 * b) ℕ+_)
                                 (trans (toℕ-combine i (combine i2 l))
                                        (cong (toℕ i * (a2 * c) ℕ+_) (toℕ-combine i2 l))))))))
