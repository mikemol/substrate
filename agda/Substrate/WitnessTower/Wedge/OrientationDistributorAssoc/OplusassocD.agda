------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.OplusassocD
--
-- Defines: δ-⊕assoc-D
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationDistributorAssoc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.OplusassocD where

open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityL
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Raise
open import Substrate.Foundation.Fin.Combine
open import Substrate.Foundation.Fin.Combine.Assoc.ToNatRaise
open import Substrate.WitnessTower.Wedge.OrientationHexagon
open import Substrate.WitnessTower.Wedge.OrientationDistributor
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.P1
open import Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.P2



-- D-block: (b+c)+d = raise (b+c) m ;  b+(c+d) = raise b (raise c m).  (one +ℕ-assoc step)
δ-⊕assoc-D : ∀ a b c d (i : Fin a) (m : Fin d) →
             toℕ (p1 a b c d (combine i (raise (b ℕ+ c) m)))
               ≡ toℕ (p2 a b c d (combine i (raise b (raise c m))))
δ-⊕assoc-D a b c d i m =
  trans (trans (cong toℕ (trans (cong (δ a b c ⊕map (λ x → x)) (δ-raise a (b ℕ+ c) d i m))
                                (⊕map-raise (δ a b c) (λ x → x) (combine i m))))
               (toℕ-raise (a * b ℕ+ a * c) (combine i m)))
        (trans (+ℕ-assoc (a * b) (a * c) (toℕ (combine i m)))
        (sym (trans (cong toℕ (trans (cong ((λ x → x) ⊕map δ a c d) (δ-raise a b (c ℕ+ d) i (raise c m)))
                                     (trans (⊕map-raise (λ x → x) (δ a c d) (combine i (raise c m)))
                                            (cong (raise (a * b)) (δ-raise a c d i m)))))
                    (trans (toℕ-raise (a * b) (raise (a * c) (combine i m)))
                           (cong (a * b ℕ+_) (toℕ-raise (a * c) (combine i m)))))))
