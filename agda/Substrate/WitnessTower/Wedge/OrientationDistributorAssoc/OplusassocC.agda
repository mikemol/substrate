------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.OplusassocC
--
-- Defines: δ-⊕assoc-C
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationDistributorAssoc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.OplusassocC where

open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Inject
open import Substrate.Foundation.Fin.Raise
open import Substrate.Foundation.Fin.Combine
open import Substrate.Foundation.Fin.Combine.Assoc.ToNatInjectPlus
open import Substrate.Foundation.Fin.Combine.Assoc.ToNatRaise
open import Substrate.WitnessTower.Wedge.OrientationHexagon
open import Substrate.WitnessTower.Wedge.OrientationDistributor
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.P1
open import Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.P2



-- C-block: (b+c)+d = inject+ d (raise b l) ;  b+(c+d) = raise b (inject+ d l).
δ-⊕assoc-C : ∀ a b c d (i : Fin a) (l : Fin c) →
             toℕ (p1 a b c d (combine i (inject+ d (raise b l))))
               ≡ toℕ (p2 a b c d (combine i (raise b (inject+ d l))))
δ-⊕assoc-C a b c d i l =
  trans (trans (cong toℕ (trans (cong (δ a b c ⊕map (λ x → x)) (δ-inject a (b ℕ+ c) d i (raise b l)))
                                (trans (⊕map-inject (δ a b c) (λ x → x) (combine i (raise b l)))
                                       (cong (inject+ (a * d)) (δ-raise a b c i l)))))
               (trans (toℕ-inject+ (a * d) (raise (a * b) (combine i l)))
                      (toℕ-raise (a * b) (combine i l))))
        (sym (trans (cong toℕ (trans (cong ((λ x → x) ⊕map δ a c d) (δ-raise a b (c ℕ+ d) i (inject+ d l)))
                                     (trans (⊕map-raise (λ x → x) (δ a c d) (combine i (inject+ d l)))
                                            (cong (raise (a * b)) (δ-inject a c d i l)))))
                    (trans (toℕ-raise (a * b) (inject+ (a * d) (combine i l)))
                           (cong (a * b ℕ+_) (toℕ-inject+ (a * d) (combine i l))))))
